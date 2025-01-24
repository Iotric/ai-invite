import subprocess
import os
import imageio_ffmpeg as ffmpeg
from moviepy import VideoFileClip, AudioFileClip
import logging
import warnings

# Configure logging to a suitable level for monitoring and debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Suppress warnings
warnings.filterwarnings("ignore")

class VideoProcessor:
    """
    A class to handle video and audio processing tasks, including:
    
    1. Extracting audio from a video file.
    2. Replacing the audio in a video file with a new audio file.

    Attributes:
    -----------
    input_video : str
        Path to the input video file.
    output_audio : str
        Path to the output audio file (in WAV format).
    ffmpeg_path : str
        Path to the FFmpeg executable.

    Methods:
    --------
    extract_audio():
        Extracts audio from the input video file and saves it as a WAV file.
    
    replace_audio(new_audio: str, output_video: str):
        Replaces the audio in the input video file with a specified audio file
        and generates a new video file.
    """

    def __init__(self, input_video: str, output_audio: str = None):
        """
        Initializes the VideoProcessor class.

        Parameters:
        -----------
        input_video : str
            Path to the input video file.
        output_audio : str, optional
            Path to the output audio file. If not provided, the output audio
            file will have the same name as the input video, but with a .wav extension.
        """
        self.input_video = input_video
        self.output_audio = output_audio or self._default_audio_name(input_video)
        self.ffmpeg_path = ffmpeg.get_ffmpeg_exe()

    def _default_audio_name(self, input_video: str) -> str:
        """
        Generates a default audio file name based on the input video file name.

        Parameters:
        -----------
        input_video : str
            Path to the input video file.

        Returns:
        --------
        str
            Default output audio file name with a .wav extension.
        """
        base_name = os.path.splitext(input_video)[0]
        return f"{base_name}.wav"

    def _create_output_directory(self):
        """
        Creates the directory for the output audio file if it does not exist.
        """
        output_dir = os.path.dirname(self.output_audio)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")

    def extract_audio(self) -> str:
        """
        Extracts audio from the input video file.

        Returns:
        --------
        str
            Path to the extracted audio file.

        Raises:
        -------
        RuntimeError
            If audio extraction fails.
        """
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
        Replaces the audio in a video file.

        Parameters:
        -----------
        new_audio : str
            Path to the new audio file.
        output_video : str
            Path to the output video file.
        """
        if not os.path.exists(self.input_video) or not os.path.exists(new_audio):
            logging.error("Input video or new audio file does not exist.")
            return

        try:
            logging.info(f"Replacing audio in video: {self.input_video}")
            video = VideoFileClip(self.input_video)
            audio = AudioFileClip(new_audio)
            video = video.set_audio(audio)
            video.write_videofile(output_video, codec="libx264", audio_codec="aac")
            logging.info(f"Audio replaced successfully in {output_video}")
        except Exception as e:
            logging.error(f"Error during audio replacement: {e}")
            raise RuntimeError("Audio replacement failed") from e
