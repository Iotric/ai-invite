# **ReVocalize: Cloning Pipeline**

## Overview

The **Cloning Pipeline** branch of ReVocalize is designed to automate the process of cloning voices by using reference audio and transcription files. It leverages AWS Lambda for serverless execution, S3 for file management, and integrates the **Cloner** model (F5-TTS) to generate cloned audio files based on given transcriptions. This pipeline is part of the larger ReVocalize system that facilitates advanced speech synthesis tasks.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Code Explanation](#code-explanation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Voice Cloning**: Clone voices using reference audio and transcription, generating new speech.
- **AWS Lambda Integration**: Serverless architecture to handle the cloning process on-demand.
- **S3 Integration**: Seamlessly download and upload files from/to AWS S3 buckets.
- **FFmpeg & Hugging Face Models**: Utilizes FFmpeg for audio processing and Hugging Face models for voice cloning.

## Prerequisites

Before you begin, ensure you have the following:

- **AWS Account** with access to Lambda, S3, and required IAM roles.
- **Docker** for building and deploying the Lambda function.
- **Python 3.10** or higher.
- **Boto3** for interacting with AWS services.

## Installation

Follow these steps to set up the cloning pipeline:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repository/ReVocalize.git
   cd ReVocalize
   git checkout cloning-pipeline
   ```

2. **Set up the environment**:

   Ensure you have the necessary dependencies installed via a `requirements.txt` file.

   ```bash
   pip install -r requirements.txt
   ```

3. **Docker Setup**:

   The pipeline is packaged for AWS Lambda and tested using Docker. Build the Docker image as follows:

   ```bash
   docker build -t revocalize-cloning-pipeline .
   ```

   Push the image to AWS ECR (Elastic Container Registry) if needed for Lambda deployment.

## Usage

### Lambda Handler

The main entry point for the Lambda function is `lambda_handler`. This function orchestrates the cloning pipeline by performing the following steps:

1. Download reference audio, transcription, and generated transcriptions from specified S3 URLs.
2. Initialize the Cloner model (F5-TTS).
3. Process each generated transcription to produce cloned audio files.
4. Upload the resulting audio files back to the specified S3 bucket.

### Sample Event

The Lambda function expects the following event format:

```json
{
  "ref_audio_url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
  "ref_transcription_url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
  "gen_transcription_list": [
    "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}",
    "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}"
  ],
  "upload_bucket_url": "https://{bucket-name}.s3.{region}.amazonaws.com/{object-key}"
}
```

### Example Output

Upon successful execution, the Lambda function returns:

```json
{
  "statusCode": 200,
  "body": {
    "message": "Completed successfully.",
    "uploaded_files_": [
      "s3://your-upload-bucket/path/to/output/clone1.wav",
      "s3://your-upload-bucket/path/to/output/clone2.wav"
    ]
  }
}
```

## Code Explanation

### Functions

1. **`download_file_from_s3(bucket_name, object_key, local_file_path)`**  
   Downloads a file from S3 to a local path.

2. **`upload_file_to_s3(local_file_path, bucket_name, object_key)`**  
   Uploads a local file to S3.

3. **`parse_s3_url(s3_url)`**  
   Parses an S3 URL to extract the bucket name and object key.

4. **`lambda_handler(event, context)`**  
   The Lambda function handler, which processes the cloning tasks. It orchestrates downloading files from S3, running the Cloner model, and uploading the cloned audio back to S3.

### Dockerfile

The Dockerfile configures the environment to run the Lambda function with the necessary dependencies:

- **FFmpeg**: For processing audio files.
- **Hugging Face models**: For voice cloning (vocos and F5-TTS).
- **AWS CLI**: For interacting with AWS services from within the container.

### Environment Variables

- **VOCOS_FOLDER**: Path to the vocos model folder.
- **CLONER_VOCAB**: Path to the Cloner model vocabulary file.
- **CLONER_CKPT**: Path to the Cloner model checkpoint file.

### Logging

The Lambda function uses the `logging` module to capture detailed logs during execution, which is helpful for debugging and monitoring.

## Contributing

We welcome contributions to improve the cloning pipeline. Fork the repository, create a new branch, and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
