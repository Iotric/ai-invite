# Revocalize: Video Processing Pipeline

Revocalize Video Processing Pipeline provides a serverless solution for video-to-audio extraction and audio replacement tasks using AWS Lambda and S3. Packaged in a Lambda-compatible Docker container, this pipeline seamlessly handles video files stored in AWS S3, extracts audio, and optionally replaces it with new audio files. It leverages FFmpeg for efficient video and audio processing, ensuring high-quality outputs. The results are stored back in S3, structured for easy access and management.

---

## Features

1. **Extract Audio**: Extracts audio from a video file and stores the result in an S3 bucket.
2. **Replace Audio**: Replaces the audio in a video with a new audio file and uploads the updated video to an S3 bucket.

---

## Project Structure

```
.
├── lambda_function.py        # Lambda function code
├── video_processor.py        # Video/audio processing utilities
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration for AWS Lambda
```

---

## Environment Variables

| Variable Name       | Default Value      | Description                                      |
|---------------------|--------------------|--------------------------------------------------|
| `RESULT_BUCKET_NAME`| `revocalize-files` | Name of the S3 bucket to store processed files. |
| `RESULT_OBJECT_KEY` | `results`          | Base path in the bucket for result files.       |

The S3 result directory must follow this structure:
```
{RESULT_OBJECT_KEY}/
└── video_processing_results/
    ├── extracted_audios/
    └── updated_videos/
```

---

## Prerequisites

1. **AWS Lambda**:
   - Use the AWS Lambda base image: `public.ecr.aws/lambda/python:3.10`.
   - Set up IAM roles with access to the necessary S3 buckets.
2. **AWS S3**:
   - Input and output files are stored in S3.
   - The function supports parsing S3 URLs.

---

## Installation

### 1. Build the Docker Image
```bash
docker build -t revocalize-lambda .
```

### 2. Push to AWS ECR
```bash
# Tag the image
docker tag revocalize-lambda:latest <your-ecr-repo-uri>:latest

# Push the image
docker push <your-ecr-repo-uri>:latest
```

### 3. Deploy the Lambda
1. Create an AWS Lambda function.
2. Use the ECR image as the deployment package.

---

## Input Event Structure

### Example for Audio Extraction
```json
{
  "task": "separate",
  "url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}"
}
```

### Example for Audio Replacement
```json
{
  "task": "replace",
  "url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
  "new_audio": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}"
}
```

---

## Running Locally

To test the function locally, uncomment the `__main__` section in `lambda_function.py` and update the event payload.

```bash
python lambda_function.py
```

---

## Usage

1. **Extract Audio**:
   - The Lambda downloads the video file from S3, extracts the audio using FFmpeg, and uploads the result to the `extracted_audios/` directory in the specified bucket.
2. **Replace Audio**:
   - The Lambda downloads the video and audio files from S3, replaces the video’s audio, and uploads the result to the `updated_videos/` directory in the specified bucket.

---

## Dependencies

- **Python 3.10**
- **Libraries**:
  - `boto3`: AWS SDK for Python.
  - `moviepy`: Video and audio editing.
  - `imageio-ffmpeg`: FFmpeg wrapper for video/audio processing.

---

## Deployment Instructions

1. **Prepare Requirements**:
   Add the following to `requirements.txt`:
   ```
   boto3
   moviepy
   imageio-ffmpeg
   ```
2. **Build Docker**:
   Use the `Dockerfile` to create the container image.
3. **Upload to ECR**:
   Push the image to an AWS Elastic Container Registry.
4. **Configure Lambda**:
   - Set environment variables `RESULT_BUCKET_NAME` and `RESULT_OBJECT_KEY`.
   - Assign an IAM role with S3 permissions to the Lambda function.

---

## Limitations

1. Assumes FFmpeg is correctly installed and available through `imageio-ffmpeg`.
2. Requires proper IAM permissions for S3 operations.

---

## Contributing

We welcome contributions to improve the transcription pipeline. Please fork the repository, create a new branch, and submit a pull request with your improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

--- 