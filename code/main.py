import re
import logging
from audio_extractor import AudioExtractor
from audio_transcriber import AudioTranscriber
from audio_cloner.src.f5_tts.api import F5TTS
from transcription_processor import TranscriptionProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def run(
    input_video: str,
    output_audio: str,
    input_dict: dict,
    transcriber: AudioTranscriber,
    cloner: F5TTS,
) -> None:
    """
    Main function to extract audio from a video file and transcribe it.

    Args:
        input_video (str): Path to the input video file.
        output_audio (str): Path to save the extracted audio file.
        transcriber (AudioTranscriber): An instance of the AudioTranscriber class for transcription.
    """
    try:
        # Step 1: Extract audio from the video
        extractor = AudioExtractor(input_video, output_audio)
        output_audio = extractor.extract_audio()

        if output_audio:
            logging.info(f"Audio extraction complete -----> Transcription Starting...")
            # Step 2: Transcribe the extracted audio
            transcription = transcriber.transcribe_file(output_audio)
            print(transcription)
            clean_sentence = lambda s: re.sub(r"[^\w\s]", "", s).lower().split()
            original_words = clean_sentence(transcription)
            logging.info(f"Audio Transcription complete -----> Cloning Starting...")

            transcription_processor = TranscriptionProcessor(
                transcription, input_dict, threshold=90
            )
            processed_transcription_list = (
                transcription_processor.process_transcription()
            )

            for processed_transcription in processed_transcription_list:
                changed_words = clean_sentence(processed_transcription)
                different_words = [w for w in changed_words if w not in original_words]
                final_name = "_".join(different_words)

                wav, sr, spect = cloner.infer(
                    ref_file=output_audio,
                    ref_text=transcription,
                    gen_text=processed_transcription,
                    file_wave=f"data/outputs/{final_name}.wav",
                )
                extractor.replace_audio(
                    f"data/outputs/{final_name}.wav", f"data/outputs/{final_name}.mp4"
                )
            logging.info(f"Finally Done output Folder: data/outputs")
        else:
            logging.error("Audio extraction failed. Skipping transcription.")

    except Exception as e:
        logging.error(f"Error in main workflow: {str(e)}")


if __name__ == "__main__":
    input_video = r"data/inputs/english_test.mp4"
    output_audio = r"data/outputs/output_audio.wav"
    input_dict = {
        "nick": ["Dana Farbo", "camila", "monica"],
        "brother": ["sister", "mother", "father"],
        "how": ["what", "why"],
        "man": ["Women", "Mix"],  # just an example (^_~)
    }

    # now it supports translation also means,
    # if the given video is in hindi it can be translated to another languages(supported)

    # language means it will translate the final transcription to provided language,
    # default is "english"(language="en") user can provide others as their short name eg. "en" for "english"
    # user can skip this using language=""
    transcriber = AudioTranscriber(
        language="en", model_name="openai/whisper-small", device="cpu"
    )
    cloner = F5TTS()

    run(input_video, output_audio, input_dict, transcriber, cloner)
