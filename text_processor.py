from options import whisper_languages
import spacy
import subprocess
import sys
import re


# Function to download and load the appropriate spaCy language model for a given language code
def load_spacy_model(lang_code="en") -> spacy.language.Language:
    lang_model = f"{lang_code}_core_web_sm"

    try:
        # Attempt to load the spaCy model
        return spacy.load(lang_model)
    except OSError:
        # If the model is not found, download and install it
        print(f"Model '{lang_model}' not found. Downloading now...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", lang_model])
        # Load the model after installation
        return spacy.load(lang_model)


# Function to process text and extract nouns, pronouns, and other tokens
def process_text(text, language="English") -> {list, list}:
    # Load the appropriate spaCy model for the specified language
    nlp = load_spacy_model(whisper_languages[language])

    # Remove punctuation and special characters from the text
    text = re.sub(r"[^\w\s]", "", text)

    # Parse the cleaned text using spaCy
    doc = nlp(text)

    # Define the parts of speech to categorize as nouns, proper nouns, and pronouns
    nouns_prons = {"NOUN", "PROPN", "PRON"}

    # Return lists of noun-related tokens and other tokens
    return (
        list(set(token.text for token in doc if token.pos_ in nouns_prons)),
        list(set(token.text for token in doc if token.pos_ not in nouns_prons)),
    )


# Function to apply word replacements to a transcription based on replacement rules
def apply_replacements_to_transcription(text, replacements_list) -> list:
    # Clean the input text by removing punctuation and special characters
    clean_text = re.sub(r"[^\w\s]", "", text)
    result = []

    # Iterate through the list of replacement dictionaries
    for replacements in replacements_list:
        temp_text = clean_text
        # Apply each replacement (replace one occurrence per key)
        for key, values in replacements.items():
            if values:
                temp_text = temp_text.replace(key, values[0], 1)
        result.append(temp_text)

    # Return the list of modified texts after applying replacements
    return result


# Function to compute similarity between two texts using spaCy's similarity feature
def compute_similarity(text1, text2, language="English") -> float:
    # Load the spaCy model for the specified language
    nlp = load_spacy_model(whisper_languages[language])
    # Parse both input texts
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    # Return the similarity score between the two texts
    return doc1.similarity(doc2)


# Test the functions with sample inputs
# Uncomment the lines below for testing:
# print(apply_replacements_to_transcription("Hey Nick, how you doing brother? It's Dean Norris here, aka ASAC Schrader. you were right. Hey, thanks for being a fan", [{'brother': ['Buddy'], 'Nick': ['Himanshu'], 'you': ["we"]}, {'brother': ['Sir'], 'Nick': ['akash'], 'you': ["i"]}]))
# print(process_text("Hey Nick, how you doing brother? It's Dean Norris here, aka ASAC Schrader. Rip Hank is right. Hey, thanks for being a fan", "English"))
