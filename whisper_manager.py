import whisper
import logging
import os
import argparse


class WhisperManager:
    def __init__(self, model_name: str, root: str):
        self.model_name = model_name
        self.root = root

    def download_model(self):
        """
        Downloads the Whisper model to the cache directory without loading it into memory.
        """
        try:
            whisper._download(
                whisper._MODELS[self.model_name], root=self.root, in_memory=False
            )
            logging.info(f"Whisper model '{self.model_name}' downloaded successfully.")
            logging.info(
                f"Saved Path as WHISPER_MODEL='{self.root}' in environment variables"
            )

        except Exception as e:
            logging.error(f"Error downloading Whisper model: {str(e)}")
            raise

# main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whisper Manager")
    parser.add_argument(
        "--model_name",
        type=str,
        default="small",
        required=False,
        help="Name of the Whisper model to download",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=os.path.join(os.path.expanduser("~"), ".cache"),
        required=False,
        help="Root directory for model download",
    )
    args = parser.parse_args()
    manager = WhisperManager(args.model_name, args.root)
    manager.download_model()
