import json
import logging
import os
import tempfile
from urllib.parse import urlparse
import boto3
from transcription_pipeline import TranscriptionPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize boto3 S3 client
s3_client = boto3.client("s3")


def download_file_from_s3(
    bucket_name: str, object_key: str, local_file_path: str
) -> None:
    """
    Downloads a file from S3 to a local path.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The object key in the S3 bucket.
        local_file_path (str): The local path to save the downloaded file.
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

    Args:
        local_file_path (str): The local file path to upload.
        bucket_name (str): The target S3 bucket name.
        object_key (str): The target object key in the bucket.
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
    AWS Lambda handler to process transcription tasks.

    Args:
        event (dict): Lambda event data containing the file URL.
        context (object): AWS Lambda runtime context.

    Returns:
        dict: Response with transcription or error details.
    """
    try:
        logger.info("Lambda function invoked.")

        # Validate and parse the input URL
        file_url = event.get("url")
        if not file_url:
            raise ValueError("The 'url' field is required in the event payload.")

        parsed_url = urlparse(file_url)
        bucket_name = parsed_url.netloc.split(".")[0]
        object_key = parsed_url.path.lstrip("/")

        # Define local file paths using tempfile
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio_file:
            local_audio_path = temp_audio_file.name
            logger.info(f"Temporary audio file created at {local_audio_path}")

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".json"
        ) as temp_transcription_file:
            local_transcription_path = temp_transcription_file.name
            logger.info(
                f"Temporary transcription file created at {local_transcription_path}"
            )

        # Step 1: Download the audio file from S3
        download_file_from_s3(bucket_name, object_key, local_audio_path)

        # Step 2: Initialize transcription pipeline
        pipeline = TranscriptionPipeline()
        pipeline.load_model()
        logger.info("Transcription pipeline initialized.")

        # Step 3: Perform transcription
        transcription_result = pipeline.transcribe_audio(local_audio_path)
        transcription_text = transcription_result.get("text", "")
        if not transcription_text:
            raise RuntimeError("Transcription result is empty.")

        # Save transcription result to a JSON file
        with open(local_transcription_path, "w") as result_file:
            json.dump({"transcription": transcription_text}, result_file)

        # Step 4: Upload the transcription result back to S3
        result_bucket_name = os.environ.get("RESULT_BUCKET_NAME", "revocalize-files")
        result_object_key = os.environ.get("RESULT_OBJECT_KEY", "results")
        result_object_key += (
            f"/transcription_results/{str(os.path.basename(object_key)).split('.')[0]}_transcription.json"
        )
        upload_file_to_s3(
            local_transcription_path, result_bucket_name, result_object_key
        )

        # Step 5: Return success response
        response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Transcription completed successfully.",
                    "transcription_url": f"s3://{result_bucket_name}/{result_object_key}",
                }
            ),
        }
        logger.info(f"Transcription process completed: {response}")
        return response

    except Exception as e:
        logger.error(f"Error occurred during transcription: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# Example test event
# if __name__ == "__main__":
#     # event = {
#     #     "url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}"
#     # }
#     lambda_handler(event, None)
