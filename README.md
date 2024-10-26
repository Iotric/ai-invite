# **ReVocalize**: Your Voice, Reimagined.

## Overview
The ReVocalize Project is designed to extract audio from video files, transcribe the audio, replacing the required words from the audio and use voice cloning techniques to generate new audio outputs. This project integrates various components such as audio extraction, transcription, replacing words and voice synthesis, providing a seamless workflow for audio processing.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Audio Extraction**: Extract audio from various video formats.
- **Audio Transcription**: Transcribe the extracted audio using advanced models.
- **Replacing Words**: Replace the Required words from the audio and then regenerate audio.
- **Voice Cloning**: Clone voices based on transcriptions to generate new audio outputs.
- **Logging**: Monitor the process with detailed logging.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.10 or higher installed on your machine.
- `virtualenv` package for creating virtual environments.

## Installation
Follow the steps below to set up the project:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Iotric/ai-invite.git
   cd ai-invite
   ```

2. **Run the setup script**:
   - For macOS/Linux:
     ```bash
     chmod +x setup.sh
     ./setup.sh
     ```

   - For Windows:
     ```batch
     setup.bat
     ```

3. **Activate the virtual environment**:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   The setup script will automatically install the required dependencies.

## Usage
To run the project, ensure that your virtual environment is activated and execute the following command:

```bash
python main.py
```

### Parameters
- **input_video**: Path to the input video file.
- **output_audio**: Path to save the extracted audio file.
- **input_dict**: A dictionary mapping words to their replacements for processing transcriptions.
  
### Example
The default parameters in `main.py` are set as follows:
```python
input_video = r"data\inputs\test.mp4"
output_audio = r"data\outputs\output_audio.wav"
input_dict = {"nick": ["Dana Farbo","Monica","camila"]} # More the inputs more will be complexity
```

## Code Structure
The main functionality of the project is implemented in `main.py`. Here's a brief overview of the main components:

- **AudioExtractor**: A class responsible for extracting audio from video files.
- **AudioTranscriber**: A class used for transcribing audio files.
- **F5TTS**: A voice cloner that generates audio based on input text with natural tone.
- **process_transcription**: A function that processes the transcribed text and applies necessary word transformations.

### Main Function Workflow
The workflow consists of the following steps:
1. **Extract Audio**: The audio is extracted from the provided video file.
2. **Transcribe Audio**: The extracted audio is transcribed into text.
3. **Process Transcription**: The transcribed text is processed to apply replacements based on the `input_dict`.
4. **Voice Cloning**: The processed transcriptions are cloned into new audio outputs.

## Contributing
We welcome contributions to enhance the project. If you have suggestions or improvements, feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
