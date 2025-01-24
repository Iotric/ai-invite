import os
import json
import logging
import tempfile
from urllib.parse import urlparse
import boto3
from video_processor import VideoProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize S3 client
s3_client = boto3.client("s3")


def download_file_from_s3(
    bucket_name: str, object_key: str, local_file_path: str
) -> None:
    """
    Downloads a file from S3 to a local path.
    """
    try:
        logger.info(
            f"Downloading file from S3 bucket: {bucket_name}, key: {object_key}"
        )
        s3_client.download_file(bucket_name, object_key, local_file_path)
        logger.info(f"File successfully downloaded to: {local_file_path}")
    except Exception as e:
        logger.error(f"Failed to download file from S3: {e}")
        raise


def upload_file_to_s3(local_file_path: str, bucket_name: str, object_key: str) -> None:
    """
    Uploads a file to S3.
    """
    try:
        logger.info(f"Uploading file to S3 bucket: {bucket_name}, key: {object_key}")
        s3_client.upload_file(local_file_path, bucket_name, object_key)
        logger.info(f"File successfully uploaded to S3: {bucket_name}/{object_key}")
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for audio processing tasks.
    """
    try:
        logger.info("Lambda function invoked.")

        # Extract task and file URL from the event
        task = event.get("task")
        file_url = event.get("url")
        new_audio_url = event.get("new_audio") if task == "replace" else None

        if not task or not file_url:
            raise ValueError(
                "The 'task' and 'url' fields are required in the event payload."
            )
        if task not in ["separate", "replace"]:
            raise ValueError("Invalid 'task' value. Expected 'separate' or 'replace'.")

        # Parse the S3 URL
        parsed_url = urlparse(file_url)
        bucket_name = parsed_url.netloc.split(".")[0]
        object_key = parsed_url.path.lstrip("/")

        # Local file paths
        temp_dir = tempfile.gettempdir()
        local_video_path = os.path.join(temp_dir, os.path.basename(object_key))
        download_file_from_s3(bucket_name, object_key, local_video_path)

        if task == "separate":
            # Extract audio from the video
            audio_extractor = VideoProcessor(input_video=local_video_path)
            output_audio_path = audio_extractor.extract_audio()

            # Upload the extracted audio back to S3
            result_bucket_name = os.environ.get(
                "RESULT_BUCKET_NAME", "revocalize-files"
            )
            result_object_key = os.environ.get(
                "RESULT_OBJECT_KEY", "results"
            )
            
            result_object_key += f"/video_processing_results/extracted_audios/{os.path.basename(output_audio_path)}"
            
            upload_file_to_s3(output_audio_path, result_bucket_name, result_object_key)

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "message": "Audio extracted successfully.",
                        "audio_url": f"s3://{result_bucket_name}/{result_object_key}",
                    }
                ),
            }

        elif task == "replace":
            # Validate new audio URL
            if not new_audio_url:
                raise ValueError(
                    "The 'new_audio' field is required for the 'replace' task."
                )

            # Parse new audio S3 URL and download it
            parsed_audio_url = urlparse(new_audio_url)
            audio_bucket_name = parsed_audio_url.netloc.split(".")[0]
            audio_object_key = parsed_audio_url.path.lstrip("/")
            local_audio_path = os.path.join(
                temp_dir, os.path.basename(audio_object_key)
            )
            download_file_from_s3(audio_bucket_name, audio_object_key, local_audio_path)

            # Replace audio in the video
            output_video_path = os.path.join(
                temp_dir, f"replaced_{os.path.basename(local_video_path)}"
            )
            audio_extractor = VideoProcessor(input_video=local_video_path)
            audio_extractor.replace_audio(
                new_audio=local_audio_path, output_video=output_video_path
            )

            # Upload the updated video back to S3
            result_bucket_name = os.environ.get(
                "RESULT_BUCKET_NAME", "revocalize-files"
            )
            result_object_key = os.environ.get(
                "RESULT_OBJECT_KEY", "results"
            )
            result_object_key += f"/video_processing_results/updated_videos/{os.path.basename(output_video_path)}"
            upload_file_to_s3(output_video_path, result_bucket_name, result_object_key)

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "message": "Audio replaced successfully.",
                        "video_url": f"s3://{result_bucket_name}/{result_object_key}",
                    }
                ),
            }

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# if __name__ == "__main__":
#     # Test the Lambda handler locally
#     event1 = {
#         "task": "separate",
#         "url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
#     }
#     event2 = {
#         "task": "replace",
#         "url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
#         "new_audio": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
#     }
#     lambda_handler(event1, None)
#     lambda_handler(event2, None)
