import os
import json
import logging
import tempfile
from urllib.parse import urlparse
import boto3
from cloner import Cloner

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


def parse_s3_url(s3_url: str) -> tuple:
    """
    Parses an S3 URL into bucket name and object key.
    """
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc.split(".")[0]
    object_key = parsed_url.path.lstrip("/")
    return bucket_name, object_key


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda handler for cloning tasks.
    """
    try:
        logger.info("Lambda function invoked.")

        # Extract task and file URL from the event
        ref_audio_url = event.get("ref_audio_url")
        ref_transcription_url = event.get("ref_transcription_url")
        gen_transcription_list = event.get("gen_transcription_list")
        upload_bucket_url = event.get("upload_bucket_url")

        if (
            not ref_audio_url
            or not ref_transcription_url
            or not gen_transcription_list
            or not upload_bucket_url
        ):
            raise ValueError(
                "The 'ref_audio_url', 'ref_transcription_url', 'gen_transcription_list' and 'upload_bucket_url' fields are required in the event payload."
            )

        ref_audio_bucket_name, ref_audio_object_key = parse_s3_url(ref_audio_url)
        ref_transcription_bucket_name, ref_transcription_object_key = parse_s3_url(
            ref_transcription_url
        )
        upload_bucket_name, upload_object_key = parse_s3_url(upload_bucket_url)

        # Local file paths
        temp_dir = tempfile.gettempdir()
        
        local_audio_path = os.path.join(temp_dir, os.path.basename(ref_audio_object_key))
        download_file_from_s3(ref_audio_bucket_name, ref_audio_object_key, local_audio_path)
        
        local_transcription_path = os.path.join(
            temp_dir, os.path.basename(ref_transcription_object_key)
        )
        download_file_from_s3(
            ref_transcription_bucket_name, ref_transcription_object_key, local_transcription_path
        )
        
        
        cloner = Cloner(
            model_type="F5-TTS",
            ckpt_file=os.environ.get("CLONER_CKPT", ""),
            vocab_file=os.environ.get("CLONER_VOCAB", ""),
            local_path=os.environ.get("VOCOS_FOLDER", None),
        )
        
        uploaded_files_url_list = []
        
        for gen_transcription_url in gen_transcription_list:
            gen_transcription_bucket_name, gen_transcription_object_key = parse_s3_url(gen_transcription_url)
            local_gen_transcription_path = os.path.join(
                temp_dir, os.path.basename(gen_transcription_object_key)
            )
            download_file_from_s3(
                gen_transcription_bucket_name, gen_transcription_object_key, local_gen_transcription_path
            )
            gen_transcription = json.load(open(local_gen_transcription_path))
            gen_transcription = gen_transcription["transcription"]
            
            file_wav = os.path.join(temp_dir, f"{os.path.basename(ref_audio_object_key)}_{os.path.basename(gen_transcription_object_key)}.wav")
            
            _, _, _ = cloner.infer(
                ref_file=local_audio_path,
                ref_text=local_transcription_path,
                gen_text=gen_transcription,
                file_wave=file_wav
            )
            
            upload_object_key += f"/{os.path.basename(ref_audio_object_key)}_{os.path.basename(gen_transcription_object_key)}.wav"
            upload_file_to_s3(file_wav, upload_bucket_name, upload_object_key)

            uploaded_files_url_list.append(f"s3://{upload_bucket_name}/{upload_object_key}")
            
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Completed successfully.",
                    "uploaded_files_": uploaded_files_url_list,
                }
            ),
        }

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# if __name__ == "__main__":
#     # Test the Lambda handler locally
#     event = {
#         "ref_audio_url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
#         "ref_transcription_url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
#         "gen_transcription_list": [
#             "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
#             "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}"
#         ],
#         "upload_bucket_url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}"
#     }
#     lambda_handler(event, None)