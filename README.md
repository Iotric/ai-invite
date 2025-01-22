# **ReVocalize: Transcription Pipeline**

## Overview

The **Transcription Pipeline** provides serverless audio-to-text transcription using OpenAI's Whisper model, packaged within a Lambda-compatible Docker container. This pipeline processes audio files stored in AWS S3, performs transcription, and stores the resulting text back in S3. The setup integrates AWS Lambda, S3, and Whisper, with additional dependencies like `ffmpeg` for audio file manipulation.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Docker Setup](#docker-setup)
- [Code Explanation](#code-explanation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Whisper Integration**: Uses OpenAI's Whisper for transcription.
- **FFmpeg Support**: Includes FFmpeg for handling audio files.
- **S3 Integration**: Downloads and uploads audio/transcription to/from AWS S3.
- **Serverless Deployment**: Fully compatible with AWS Lambda for scalable and efficient deployment.
- **Model Management**: Automatically downloads and caches Whisper models.
- **Logging**: Logs transcription progress for easy monitoring.

## Prerequisites

Before using this pipeline, ensure you have the following:

- Python 3.10 or later installed (inside Docker container).
- AWS credentials configured for accessing S3.
- Docker installed for building the container.

## Installation

### Docker Build and Deployment

1. **Clone the repository**:

   ```bash
   git clone https://github.com/himanshumahajan138/ReVocalize.git
   cd ReVocalize
   git checkout transcription-pipeline
   ```

2. **Create a Docker image**:

   Build the Docker image that packages the transcription pipeline with all necessary dependencies:

   ```bash
   docker build -t transcription-pipeline .
   ```

3. **Push the Docker image to Amazon ECR** (if deploying on AWS Lambda):

   - Tag the Docker image for ECR:
     ```bash
     docker tag transcription-pipeline:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/transcription-pipeline:latest
     ```

   - Push the image to ECR:
     ```bash
     docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/transcription-pipeline:latest
     ```

4. **Deploy the container to AWS Lambda**:

   Create a Lambda function and select the ECR image as the deployment package.

## Usage

### Lambda Handler

Once deployed, you can invoke the transcription Lambda function, passing the S3 bucket and object key as part of the event.

#### Example Event

```json
{
  "bucket_name": "your-s3-bucket",
  "object_key": "path/to/audio/file.mp3"
}
```

#### Example Lambda Invocation

You can use the following Python script to invoke the Lambda handler:

```python
from transcription_pipeline import lambda_handler

event = {
    "bucket_name": "your-s3-bucket",
    "object_key": "path/to/audio/file.mp3"
}
context = {}  # AWS Lambda context (mocked for local testing)

response = lambda_handler(event, context)
print(response)
```

### Example Output

```json
{
  "statusCode": 200,
  "body": "{\"transcription\": \"Hello world.\"}"
}
```

## Docker Setup

This project uses Docker to create a container that runs the transcription pipeline as an AWS Lambda function. The Dockerfile builds the environment with the following components:

- **FFmpeg**: Installed for audio processing.
- **Python dependencies**: `ffmpeg-python`, `whisper`, and other requirements.
- **Whisper model**: Automatically downloads the specified Whisper model.

### Dockerfile Breakdown

1. **Base Image**: Uses `public.ecr.aws/lambda/python:3.10` for a Lambda-compatible environment.
2. **FFmpeg Installation**: Downloads and extracts FFmpeg binaries, adding them to the Lambda environment.
3. **Python Dependencies**: Installs Python libraries as specified in `requirements.txt` and additional libraries like `ffmpeg-python`.
4. **Whisper Model**: Downloads and caches the specified Whisper model (`small`) using the `whisper_manager.py` script.
5. **Lambda Handler**: Specifies `lambda_function.lambda_handler` as the entry point for Lambda invocations.

```Dockerfile
FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y tar xz wget

RUN mkdir -p /var/task/ffmpeg && \
    cd /var/task/ffmpeg && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xvf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/* . && \
    rm -rf ffmpeg-*-amd64-static && \
    rm ffmpeg-release-amd64-static.tar.xz

ENV PATH="/var/task/ffmpeg:${PATH}"

RUN chmod -R +x /var/task/ffmpeg

RUN pip install ffmpeg-python -t /var/task

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY /** ${LAMBDA_TASK_ROOT}

RUN python ${LAMBDA_TASK_ROOT}/whisper_manager.py --model_name small --root ${LAMBDA_TASK_ROOT}/.cache

ENV WHISPER_MODEL=${LAMBDA_TASK_ROOT}/.cache/small.pt

CMD [ "lambda_function.lambda_handler" ]
```

## Code Explanation

### Key Components

1. **Lambda Handler**: 
   - `lambda_handler(event, context)`: Entry point for Lambda function that processes the transcription request.
   - Downloads the audio file from S3, processes it using Whisper, and uploads the transcription result back to S3.

2. **Transcription Pipeline**:
   - `TranscriptionPipeline`: Contains logic to load the Whisper model and transcribe audio files.
   - `load_model()`: Loads the Whisper model for transcription.
   - `transcribe_audio(audio_path)`: Transcribes the given audio file to text.

3. **Whisper Manager**:
   - Handles downloading and caching Whisper models to avoid repeated downloads during Lambda invocations.

### Environment Variables

- `WHISPER_MODEL`: Path to the Whisper model on the container's file system.

### Dependencies

- `ffmpeg-python`: For audio processing.
- `whisper`: OpenAI's Whisper for transcription.
- Additional Python packages specified in `requirements.txt`.

## Contributing

We welcome contributions to improve the transcription pipeline. Please fork the repository, create a new branch, and submit a pull request with your improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
