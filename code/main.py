import os
import logging
from audio_extractor import AudioExtractor
from audio_transcriber import AudioTranscriber
from audio_cloner.src.f5_tts.api import F5TTS
from transcription_processor import process_transcription

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def run(input_video: str, output_audio: str, input_dict: dict, transcriber: AudioTranscriber, cloner: F5TTS) -> None:
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
            logging.info(f"Audio Transcription complete -----> Cloning Starting...")
            
            processed_transcription_list = process_transcription(transcription,input_dict,90)
            
            for processed_transcription in processed_transcription_list:
                wav, sr, spect = cloner.infer(
                    ref_file=output_audio,
                    ref_text=transcription,
                    gen_text=processed_transcription,
                    file_wave="data/outputs/final.wav"
                )
            
            logging.info("Clonning Done, Output Folder: data/outputs/")
        else:
            logging.error("Audio extraction failed. Skipping transcription.")

    except Exception as e:
        logging.error(f"Error in main workflow: {str(e)}")

if __name__ == "__main__":
    input_video = r"D:\project\data\inputs\test.mp4"
    output_audio = r"D:\project\data\outputs\output_audio.wav"
    input_dict = {"nick":["himanshu"]}

    transcriber = AudioTranscriber(device="cpu")
    cloner = F5TTS()

    run(input_video, output_audio,input_dict, transcriber, cloner)
