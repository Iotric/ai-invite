import subprocess
import os
import imageio_ffmpeg as ffmpeg
from moviepy import *
import logging
import warnings

# Configure logging to a suitable level for monitoring and debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Suppress warnings
warnings.filterwarnings("ignore")


class AudioExtractor:
    """
    A class to handle the extraction of audio from a video file using FFmpeg.
    """

    def __init__(self, input_video: str, output_audio: str):
        self.input_video = input_video
        self.output_audio = self._validate_audio_extension(output_audio)
        self.ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    def _validate_audio_extension(self, output_audio: str) -> str:
        if not output_audio.endswith(".wav"):
            output_audio += ".wav"
            logging.warning(
                f"Output file extension missing or incorrect. Updated to: {output_audio}"
            )
        return output_audio

    def _create_output_directory(self):
        output_dir = os.path.dirname(self.output_audio)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")

    def extract_audio(self) -> str:
        self._create_output_directory()
        command = [
            self.ffmpeg_path,
            "-y",
            "-i",
            self.input_video,
            "-ac",
            "2",
            "-ar",
            "44100",
            "-vn",
            self.output_audio,
        ]
        try:
            logging.info(f"Extracting audio from video: {self.input_video}")
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logging.info(f"Audio extracted successfully to {self.output_audio}")
            return self.output_audio
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during audio extraction: {e}")
            raise RuntimeError("Audio extraction failed") from e


    def replace_audio(self, new_audio: str, output_video: str):
        """
        Replaces the audio in a video file and adds a thumbnail.

        Parameters:
        -----------
        new_audio : str
            Path to the new audio file.
        output_video : str
            Path to the output video file.
        thumbnail_text : str
            Text to include in the thumbnail.
        """
        if not os.path.exists(self.input_video) or not os.path.exists(new_audio):
            logging.error("Input video or new audio file does not exist.")
            return

        # Replace audio
        video = VideoFileClip(self.input_video)
        audio = AudioFileClip(new_audio)
        video = video.with_audio(audio)
        video.write_videofile(output_video)
        logging.info(f"Audio replaced successfully in {output_video}")
        


# # Example usage
# if __name__ == "__main__":
#     input_video = r"data/inputs/test.mp4"
#     output_audio = r"data/output_audio.wav"
#     edited_audio = r"data/outputs/final.wav"
#     output_video = r"data/final.mp4"
#     thumbnail_text = "My Custom Thumbnail"

#     extractor = AudioExtractor(input_video, output_audio)
#     output_audio = extractor.extract_audio()
#     extractor.replace_audio(output_audio, output_video, thumbnail_text)
