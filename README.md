# **ReVocalize: Text Processing Pipeline**

## Overview

The **Text Processing Pipeline** branch of ReVocalize focuses on robust text analysis and transformation, leveraging NLP tools to process transcriptions, apply custom word replacements, and compute semantic similarities. This module integrates spaCy for language processing and provides utilities to streamline text-based operations in the ReVocalize workflow.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Code Explanation](#code-explanation)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Language Support**: Dynamically load and manage spaCy language models.
- **Text Processing**: Extract nouns, pronouns, and other tokens for analysis.
- **Word Replacement**: Apply custom replacement rules to transform transcriptions.
- **Text Similarity**: Compute semantic similarity between text pairs using spaCy.

## Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher installed.
- `pip` and `virtualenv` installed for managing dependencies.

## Installation

Follow these steps to set up the text processing pipeline:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/himanshumahajan138/ReVocalize.git
   cd ReVocalize
   git checkout text-processing-pipeline
   ```

2. **Set up the environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Install spaCy models**:
   SpaCy models for required languages will be downloaded dynamically during execution.

## Usage

This branch includes utilities for text processing. Here's how you can use the provided functionality:

### Sample Code

```python
from code.text_processing import process_text, apply_replacements_to_transcription, compute_similarity

# Process text to extract nouns and other tokens
nouns, others = process_text("Hello world, this is an NLP demo.", "English")
print("Nouns/Pronouns:", nouns)
print("Other Tokens:", others)

# Apply replacements to a transcription
replacements = [{'world': ['earth'], 'NLP': ['Natural Language Processing']}]
result = apply_replacements_to_transcription("Hello world, this is an NLP demo.", replacements)
print("Replaced Texts:", result)

# Compute similarity between two texts
similarity_score = compute_similarity("Hello world", "Hi Earth", "English")
print("Similarity Score:", similarity_score)
```

### Example Output

```plaintext
Nouns/Pronouns: ['world', 'NLP']
Other Tokens: ['demo', 'this', 'an']
Replaced Texts: ['Hello earth, this is an Natural Language Processing demo.']
Similarity Score: 0.85
```

## Code Explanation

### Functions

1. **`load_spacy_model(lang_code)`**  
   Dynamically downloads and loads the appropriate spaCy model for the specified language.
2. **`process_text(text, language)`**  
   Processes text to extract nouns, pronouns, and other tokens based on part-of-speech tagging.

3. **`apply_replacements_to_transcription(text, replacements_list)`**  
   Applies a sequence of word replacements to a given transcription.

4. **`compute_similarity(text1, text2, language)`**  
   Computes semantic similarity between two text inputs using spaCy.

### Configuration

The language mappings are defined in `code.options.whisper_languages`, providing support for multiple languages.

### Logging

Detailed logs are displayed during model downloads and replacements for better monitoring.

## Contributing

We welcome contributions to improve the text processing pipeline. Fork the repository, create a new branch, and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
