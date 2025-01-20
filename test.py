############################################ This is Just a Test File (for development purposes) ############################################


# import spacy
# import subprocess
# import sys


# # Function to download and load spaCy language model
# def load_spacy_model(lang_model):
#     try:
#         # Try loading the model
#         return spacy.load(lang_model)
#     except OSError:
#         print(f"Model '{lang_model}' not found. Downloading now...")
#         # Download the model if not already installed
#         subprocess.check_call([sys.executable, "-m", "spacy", "download", lang_model])
#         # Load the model after downloading
#         return spacy.load(lang_model)


# # Define the language model (e.g., 'en_core_web_sm' for English)
# lang_model = "en_core_web_sm"

# # Load the spaCy model (with automated downloading)
# nlp = load_spacy_model(lang_model)

# # Input text
# text = "Hey Nick, how you doing brother? It's Dean Norris here, aka ASAC Schrader. Rip Hank is right. Hey, thanks for being a fan man, we appreciate that very much. But more importantly, happy birthday man! 31st, yeah!"

# # Process the text
# doc = nlp(text)

# for token in doc:
#     print(token.text + " - " + token.pos_)
#     # print(token.text, token.pos_)
# # # Identify nouns and other parts of speech
# # nouns = [token.text for token in doc if token.pos_ == "NOUN"]
# # pronouns = [token.text for token in doc if token.pos_ == "PRON"]
# # verbs = [token.text for token in doc if token.pos_ == "VERB"]
# # adjectives = [token.text for token in doc if token.pos_ == "ADJ"]

# # print("Nouns:", nouns)
# # print("Pronouns:", pronouns)
# # print("Verbs:", verbs)
# # print("Adjectives:", adjectives)
