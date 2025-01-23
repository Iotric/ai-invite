import whisper
import os
import torch
import logging


class TranscriptionPipeline:
    def __init__(
        self,
        model_path: str = os.environ.get("WHISPER_MODEL"),
        device: str = None,
    ):
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model_path = model_path
        self.model = None

    def load_model(self):
        try:
            self.model = whisper.load_model(
                name=self.model_path, in_memory=True
            )
            logging.info(f"Whisper model loaded successfully on {self.device}.")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {str(e)}")
            raise

    def transcribe_audio(self, audio_path: str) -> dict:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call `load_model` first.")

        try:
            result = self.model.transcribe(audio=audio_path)
            logging.info(f"Transcription completed for file: {audio_path}")
            return result
        except Exception as e:
            logging.error(f"Error during transcription: {str(e)}")
            raise

# testing
# if __name__ == "__main__":
#     pipeline = TranscriptionPipeline()
#     pipeline.load_model()
#     print(pipeline.transcribe_audio("test.wav"))