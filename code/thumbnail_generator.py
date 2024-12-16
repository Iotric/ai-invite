from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg as ffmpeg
import shutil
import os
import logging
import subprocess
import warnings

# Configure logging to a suitable level for monitoring and debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Suppress warnings
warnings.filterwarnings("ignore")

ffmpeg_path = ffmpeg.get_ffmpeg_exe()

def generate_thumbnail(output_image: str, text: str, base_image: str):
    """
    Generates a thumbnail image with text centered and font size adjusted dynamically.

    Parameters:
    -----------
    base_image : str
        Path to the base image to use as a thumbnail.
    output_image : str
        Path to save the generated thumbnail image.
    text : str
        Text to overlay on the thumbnail.
    """
    try:
        # Load the base image
        img = Image.open(base_image).convert("RGB")
        img_size = img.size

        # Prepare to draw text
        draw = ImageDraw.Draw(img)

        # Dynamically adjust font size based on image size
        base_font_size = img_size[0] // 20  # Adjust this ratio for your needs
        try:
            font = ImageFont.truetype("arial.ttf", base_font_size)
        except IOError:
            font = ImageFont.load_default()

        # Get text size and calculate position for centering
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_position = (
            (img_size[0] - text_width) // 2,
            (img_size[1] - text_height) // 2,
        )

        # Draw text on the image
        draw.text(text_position, text, fill="black",stroke_width=2, stroke_fill="white" , font=font)

        # Save the modified image
        img.save(output_image)
        logging.info(f"Thumbnail image generated: {output_image}")
    except Exception as e:
        logging.error(f"Error generating thumbnail: {e}")
        raise


def add_thumbnail_to_video(text: str, output_video: str, base_image: str = "data/inputs/background.png"):
    """
    Embeds the generated thumbnail into the video.

    Parameters:
    -----------
    thumbnail_image : str
        Path to the thumbnail image.
    output_video : str
        Path to save the video with the embedded thumbnail.
    """
    thumbnail_image = output_video + ".png"
    generate_thumbnail(thumbnail_image, text, base_image)
    temp_input_video = shutil.copy(output_video, output_video + "_temp.mp4")

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        temp_input_video,
        "-i",
        thumbnail_image,
        "-map",
        "0",
        "-map",
        "1",
        "-c",
        "copy",
        "-disposition:v:1",
        "attached_pic",
        output_video
    ]
    try:
        logging.info(f"Embedding thumbnail into video: {output_video}")
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logging.info(f"Thumbnail added successfully to {output_video}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error adding thumbnail to video: {e}")
        raise RuntimeError("Thumbnail embedding failed") from e
    
    os.remove(temp_input_video)
    os.remove(thumbnail_image)