import json
import logging
import os
import requests
import boto3
from transcription_pipeline import TranscriptionPipeline

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize boto3 client
s3 = boto3.client("s3")

def download_file_from_s3(bucket_name, object_key, local_file_path):
    """
    Downloads a file from S3 to the local path.
    """
    try:
        logging.info(f"Downloading file from S3 bucket: {bucket_name}, key: {object_key}")
        s3.download_file(bucket_name, object_key, local_file_path)
        logging.info(f"File downloaded to {local_file_path}")
    except Exception as e:
        logging.error(f"Error downloading file from S3: {str(e)}")
        raise

def upload_file_to_s3(local_file_path, bucket_name, object_key):
    """
    Uploads a file to S3.
    """
    try:
        logging.info(f"Uploading file to S3 bucket: {bucket_name}, key: {object_key}")
        s3.upload_file(local_file_path, bucket_name, object_key)
        logging.info(f"File uploaded successfully to {bucket_name}/{object_key}")
    except Exception as e:
        logging.error(f"Error uploading file to S3: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    Lambda handler to process transcription requests.

    Args:
        event (dict): The event data passed by Lambda (e.g., file URL or S3 details).
        context (LambdaContext): The runtime information passed by AWS Lambda.

    Returns:
        dict: The transcription result or error message.
    """
    try:
        logging.info("Lambda handler invoked.")

        # Extract S3 bucket and key from the event
        bucket_name = event.get("bucket_name")
        object_key = event.get("object_key")

        if not bucket_name or not object_key:
            raise ValueError("S3 bucket name and object key must be provided in the event.")

        # Define the local file path for Lambda's /tmp directory
        local_file_path = f"/tmp/{os.path.basename(object_key)}"

        # Download the file from S3
        download_file_from_s3(bucket_name, object_key, local_file_path)

        # Initialize and run the transcription pipeline
        pipeline = TranscriptionPipeline()
        pipeline.load_model()

        # Perform transcription
        result = pipeline.transcribe_audio(local_file_path)

        # Save transcription result to S3
        transcription_result = {"transcription": result.get("text")}
        result_file_path = f"/tmp/result.json"
        with open(result_file_path, "w") as file:
            json.dump(transcription_result, file)

        result_object_key = f"results/{os.path.basename(object_key)}.json"
        upload_file_to_s3(result_file_path, bucket_name, result_object_key)

        # Return the transcription result
        return {
            "statusCode": 200,
            "body": json.dumps({"transcription": transcription_result}),
        }

    except Exception as e:
        logging.error(f"Error processing the transcription: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
