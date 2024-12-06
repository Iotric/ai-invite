import re
import logging
import torch
from itertools import product
from fuzzywuzzy import fuzz
from typing import List, Dict
from deepmultilingualpunctuation import PunctuationModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


class TranscriptionProcessor:
    def __init__(
        self, model: PunctuationModel, transcription: str, input_dict: Dict[str, List[str]], threshold: int = 90
    ):
        """
        Initializes the generator with the given transcription, dictionary of substitutions, and similarity threshold.

        Args:
            transcription (str): The original sentence to generate combinations from.
            input_dict (Dict[str, List[str]]): Dictionary with words to replace and their possible substitutes.
            threshold (int): Minimum similarity percentage for fuzzy matching. Default is 90.
        """
        self.transcription = transcription
        self.input_dict = input_dict
        self.threshold = threshold
        self.model = model

    def _get_replacement_options(self, word: str) -> List[str]:
        """
        Finds replacement options for a word based on fuzzy matching with the threshold.

        Args:
            word (str): The word to search replacements for.

        Returns:
            List[str]: Replacement options for the word, or the original word if no replacements found.
        """
        for key in self.input_dict:
            # Check if word matches any key in input_dict within the threshold
            if fuzz.ratio(word.lower(), key.lower()) >= self.threshold:
                return self.input_dict[key]
        # If no match, return the word itself
        return [word]

    def _restore_punctuation(self, transcription_list: List) -> List:
        """
        Restores punctuation and capitalization in the given transcription using a pre-trained BERT model.

        Args:
            transcription_list (List): The original unpunctuated transcription List.

        Returns:
            List: Transcription List with punctuation and capitalization restored.
        """

        for id, transcription in enumerate(transcription_list):
            # Restore punctuation and capitalization
            transcription_list[id] = self.model.restore_punctuation(transcription)

        return transcription_list

    def process_transcription(self) -> List[str]:
        """
        Generates all possible sentence combinations based on the replacement options.

        Returns:
            List[str]: List of all possible sentence combinations.
        """
        clean_sentence = lambda s: re.sub(r"[^\w\s]", "", s).split()
        tokens = clean_sentence(self.transcription)
        replaceable_words = []

        # Determine replacement options for each token in the transcription
        for token in tokens:
            replacements = self._get_replacement_options(token)

            # Ensure replacements are non-empty; if empty, add the original word
            if replacements:
                replaceable_words.append(replacements)
            else:
                replaceable_words.append(
                    [token]
                )  # Default to original word if no replacements found

        # Use Cartesian product to create all possible combinations
        all_combinations = list(product(*replaceable_words))
        result = [" ".join(words) for words in all_combinations]

        # apply punctuation
        result = self._restore_punctuation(result)

        return result

    def display_combinations(self) -> None:
        """
        Prints all possible sentence combinations to the console.
        """
        sentences = self.process_transcription()
        for sentence in sentences:
            print(sentence)


# Example usage
# if __name__ == "__main__":
# Load the pre-trained punctuation model
#     model = PunctuationModel(model="kredor/punctuate-all")
#     transcription = "hey nick, how are you doing brother ?"
#     input_dict = {
#         "nick": ["dana farbo", "ben", "alex"],
#         "brother": [],
#         "how": ["what", "why"],
#     }

#     generator = TranscriptionProcessor(model, transcription, input_dict, threshold=90)
#     generator.display_combinations()
