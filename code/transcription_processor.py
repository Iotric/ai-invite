import re
import logging
import torch
from fuzzywuzzy import process
from typing import List, Dict
from deepmultilingualpunctuation import PunctuationModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def restore_punctuation(transcription: str) -> str:
    """
    Restores punctuation and capitalization in the given transcription using a pre-trained BERT model.
    
    Args:
        transcription (str): The original unpunctuated transcription.
        
    Returns:
        str: Transcription with punctuation and capitalization restored.
    """
    # Load the pre-trained punctuation model
    model = PunctuationModel()
    
    # Restore punctuation and capitalization
    punctuated_text = model.restore_punctuation(transcription)
    
    return punctuated_text

def replace_key_with_replacements(transcription: str, key: str, replacements: List[str], threshold: int) -> List[str]:
    """
    Replaces occurrences of a key in the transcription with each of the provided replacements.

    Args:
        transcription (str): Original transcription string.
        key (str): The key to be replaced.
        replacements (List[str]): List of replacement words for the key.
        threshold (int): The minimum fuzzy matching threshold.

    Returns:
        List[str]: List of new transcriptions with the key replaced by each replacement.
    """
    result = []
    words = transcription.split()
    
    # Find the closest match for the key in the transcription
    matched_word, match_score = process.extractOne(key, words)
    
    if match_score >= threshold:
        for replacement in replacements:
            # Replace occurrences of the matched word with each replacement
            new_transcription = transcription.replace(matched_word, replacement)
            if torch.cuda.is_available():
                new_transcription = restore_punctuation(new_transcription)
            result.append(new_transcription)
            logging.debug(f"Replaced '{matched_word}' with '{replacement}' in transcription: {new_transcription}")

    return result

def generate_transcription_combinations(
        transcriptions: List[str], input_dict: Dict[str, List[str]], threshold: int) -> List[str]:
    """
    Generates combinations of transcriptions by processing multiple keys from the input dictionary.

    Args:
        transcriptions (List[str]): List of transcriptions to process.
        input_dict (Dict[str, List[str]]): Dictionary containing keys and their corresponding replacements.
        threshold (int): The minimum fuzzy matching threshold.

    Returns:
        List[str]: List of final transcriptions with all keys replaced by their respective replacements.
    """
    final_results = []

    for transcription in transcriptions:
        for key, replacements in input_dict.items():
            result = replace_key_with_replacements(transcription, key, replacements, threshold)
            final_results.extend(result)

    return final_results

def process_transcription(transcription: str, input_dict: Dict[str, List[str]], threshold: int = 85) -> List[str]:
    """
    Processes a transcription to replace keys from the input dictionary with their corresponding replacements.

    Args:
        transcription (str): Original transcription string.
        input_dict (Dict[str, List[str]]): Dictionary containing keys and their corresponding replacements.
        threshold (int, optional): The minimum fuzzy matching threshold. Defaults to 80.

    Returns:
        List[str]: List of transcriptions with keys replaced by corresponding replacement words.
    """
    # Validate inputs
    if not transcription or not isinstance(transcription, str):
        logging.error("Invalid transcription input.")
        return []
    if not input_dict or not isinstance(input_dict, dict):
        logging.error("Invalid input dictionary.")
        return []

    logging.info(f"Processing transcription: '{transcription}' with input dictionary keys: {list(input_dict.keys())}")

    initial_results = []
    if torch.cuda.is_available():
        transcription = re.sub(r'[^\w\s]', '', transcription)
    # Process each key separately to create initial variations
    for key, replacements in input_dict.items():
        result = replace_key_with_replacements(transcription, key, replacements, threshold)
        initial_results.extend(result)

    # Generate combinations if multiple keys are present
    if len(input_dict) > 1:
        final_results = generate_transcription_combinations(initial_results, input_dict, threshold)
        return final_results

    return initial_results

# example usage
# if __name__ == "__main__":
#     transcription = "hey nick, how are you doing brother ?"
#     input_dict = {
#         "nick": ["dana forba", "ben", "alex", "monica", "camila"],
#         "brother": ["sister", "mother", "father"]
#     }

#     result = process_transcription(transcription, input_dict)
#     print(result)
