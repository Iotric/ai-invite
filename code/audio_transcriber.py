import os
import torch
import librosa
import logging
from transformers import AutoProcessor, WhisperForConditionalGeneration
from typing import List, Dict
import torch.nn.functional as F

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


class AudioTranscriber:
    def __init__(
        self,
        language: str = "en",
        model_name: str = "openai/whisper-small",
        device: str = "cpu",
    ):
        """Initialize the transcriber with the model and processor."""
        self.language = language
        self.device = device
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name).to(
            device
        )
        logging.info(
            f"Initialized AudioTranscriber with model: {model_name} on device: {device}"
        )

    def load_audio(self, file_path: str, sample_rate: int = 16000) -> torch.Tensor:
        """Load and resample the audio file to the specified sample rate."""
        try:
            audio, _ = librosa.load(file_path, sr=sample_rate)
            logging.info(
                f"Loaded audio file: {file_path} with sample rate: {sample_rate}"
            )
            return torch.tensor(audio)
        except Exception as e:
            logging.error(f"Error loading audio file {file_path}: {str(e)}")
            raise

    def preprocess_audio(
        self, audio: torch.Tensor, sample_rate: int = 16000
    ) -> Dict[str, torch.Tensor]:
        """Preprocess the audio for input to the Whisper model."""
        try:
            inputs = self.processor(
                audio,
                return_tensors="pt",
                truncation=False,
                padding="longest",
                return_attention_mask=True,
                sampling_rate=sample_rate,
            ).to(self.device)

            # Ensure the mel spectrogram has 3000 frames (pad or trim if necessary)
            mel_length = inputs["input_features"].shape[-1]
            if mel_length < 3000:
                inputs["input_features"] = F.pad(
                    inputs["input_features"], (0, 3000 - mel_length)
                )
            elif mel_length > 3000:
                inputs["input_features"] = inputs["input_features"][:, :, :3000]

            logging.info("Audio preprocessing completed.")
            return inputs
        except Exception as e:
            logging.error("Error during audio preprocessing: %s", str(e))
            raise

    def transcribe_audio(self, inputs: Dict[str, torch.Tensor]) -> List[Dict[str, str]]:
        """Generate transcription with word-level timestamps."""
        try:
            if self.language == "":
                generated_ids = self.model.generate(**inputs, return_timestamps=True)
            else:
                generated_ids = self.model.generate(
                    **inputs, language=self.language, return_timestamps=True
                )

            logging.info("Transcription generated successfully.")
            return self.processor.batch_decode(
                generated_ids, output_word_offsets=True, skip_special_tokens=True
            )
        except Exception as e:
            logging.error("Error during transcription: %s", str(e))
            raise

    def transcribe_file(self, file_path: str) -> str:
        """Load, preprocess, and transcribe a single audio file."""
        try:
            audio = self.load_audio(file_path)
            inputs = self.preprocess_audio(audio)
            transcription = self.transcribe_audio(inputs)
            logging.info(f"Transcription for file {file_path} completed successfully.")
            return transcription[0]
        except Exception as e:
            logging.error(f"Failed to transcribe file {file_path}: {str(e)}")
            raise


def transcribe_directory(audio_directory: str, transcriber: AudioTranscriber) -> str:
    """Process all audio files in a directory and print transcriptions."""
    for audio_file in os.listdir(audio_directory):
        audio_path = os.path.join(audio_directory, audio_file)
        if not audio_file.lower().endswith((".wav", ".mp3", ".flac", ".ogg")):
            logging.warning(f"Skipping unsupported file: {audio_file}")
            continue
        transcription = ""
        try:
            transcription = transcriber.transcribe_file(audio_path)
        except Exception as e:
            logging.error(f"Failed to process {audio_file}: {str(e)}")

        return transcription


def transcribe_single_file(audio_file: str, transcriber: AudioTranscriber) -> str:
    """
    Transcribe a specific audio file and print the transcription.

    Args:
        audio_file (str): Path to the audio file to be transcribed.
        transcriber (AudioTranscriber): An instance of the AudioTranscriber class.
    """
    transcription = ""
    try:
        transcription = transcriber.transcribe_file(audio_file)
    except Exception as e:
        logging.error(f"Failed to transcribe {audio_file}: {str(e)}")

    return transcription


# # Usage example
# if __name__ == "__main__":
#     audio_directory = r"data/inputs"
#     transcriber = AudioTranscriber(language="en",device="cpu")
#     print(transcribe_directory(audio_directory, transcriber))
