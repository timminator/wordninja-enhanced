import re
import os
import glob
import gzip
import shutil
import importlib


def process_language_files(
    language_code,
    input_filepaths,
    output_filepath,
    allowed_chars_pattern,
    strip_s_apostrophe=False,
    blacklist=None,
    additional_words_to_append=None
):
    """
    Reads multiple input files for a language, processes the words, and writes
    a sorted dictionary file.

    Args:
        language_code (str): The language code (e.g., 'en', 'fr').
        input_filepaths (list): A list of paths to the input corpus files.
        output_filepath (str): The path to the output dictionary file.
        allowed_chars_pattern (re.Pattern): A compiled regex pattern for valid characters.
        strip_s_apostrophe (bool, optional): If True, removes "'s" from word endings.
                                             Defaults to False.
        blacklist (list, optional): A list of lowercase words to exclude.
                                    Defaults to None.
        additional_words_to_append (list, optional): A list of words to append
                                                       at the end of the file.
                                                       Defaults to None.
    """
    word_occurrences_map = {}
    blacklist_set = set(word.lower() for word in blacklist) if blacklist else set()

    print(f"--- Processing language: {language_code.upper()} ---")
    print(f"Found {len(input_filepaths)} file(s) to process.")

    for filepath in input_filepaths:
        try:
            with open(filepath, 'r', encoding='utf-8') as infile:
                for line in infile:
                    parts = line.strip().split('\t')
                    if len(parts) != 3:
                        continue

                    original_word = parts[1]
                    try:
                        occurrence = int(parts[2])

                        # Step 1: Normalize curly apostrophes
                        processed_word = original_word.replace('’', "'")

                        # Step 2: Filter out multi-word entries (containing spaces)
                        if ' ' in processed_word:
                            continue

                        # Step 3: Strictly filter for allowed characters
                        if not allowed_chars_pattern.match(processed_word):
                            continue

                        # Step 4: Lowercase for consistent processing
                        processed_word = processed_word.lower()

                        # Step 5: Filter out standalone '-' and '''
                        if processed_word in ("-", "'"):
                            continue

                        # Step 6: Filter out words starting with '-' or "'"
                        if processed_word.startswith(("-", "'")):
                            continue

                        # Step 7: Filter out words ending with '-' or "'"
                        if processed_word.endswith(("-", "'")):
                            continue

                        # Step 8: Filter out words with two or more consecutive '-' or "'"
                        if "--" in processed_word or "''" in processed_word:
                            continue

                        # Step 9: Language-specific processing (e.g., for English 's)
                        base_word = processed_word
                        if strip_s_apostrophe and base_word.endswith("'s"):
                            base_word = base_word[:-2]

                        # If the word becomes empty after processing, skip it
                        if not base_word:
                            continue

                        # Step 10: Consolidate occurrences
                        word_occurrences_map[base_word] = word_occurrences_map.get(base_word, 0) + occurrence

                    except ValueError:
                        continue
        except FileNotFoundError:
            print(f"  [Warning] Input file not found: '{filepath}'")
        except Exception as e:
            print(f"  [Error] An unexpected error occurred while processing '{filepath}': {e}")

    # Step 11: Apply blacklist
    if blacklist_set:
        word_occurrences_map = {word: count for word, count in word_occurrences_map.items() if word not in blacklist_set}

    # Step 12: Sort by occurrence (high to low)
    sorted_words = sorted(word_occurrences_map.keys(), key=lambda word: word_occurrences_map[word], reverse=True)

    # Step 13: Deduplicate additional words
    final_words_to_append = []
    if additional_words_to_append:
        existing_words_set = set(sorted_words)
        for word in additional_words_to_append:
            word_lower = word.lower()
            if word_lower not in existing_words_set:
                final_words_to_append.append(word_lower)
                existing_words_set.add(word_lower)

    try:
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            for word in sorted_words:
                outfile.write(word + '\n')

            for word in final_words_to_append:
                outfile.write(word + '\n')

            if strip_s_apostrophe: # Special case for English
                 outfile.write("'s\n")

        print(f"Successfully created dictionary at '{output_filepath}'.")
        total_words = len(sorted_words) + len(final_words_to_append) + (1 if strip_s_apostrophe else 0)
        print(f"Total unique words: {total_words}")

        # Gzip the file with max compression
        gzip_filepath = output_filepath + '.gz'
        with open(output_filepath, 'rb') as f_in:
            with gzip.open(gzip_filepath, 'wb', compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"Compressed file created at '{gzip_filepath}'.")

    except Exception as e:
        print(f"  [Error] An unexpected error occurred while writing to '{output_filepath}': {e}")


def load_language_lists(lang_code, list_type):
    """Load a list like 'blacklist' or 'additional_words' from a module."""
    module_name = f"vocab_blacklists_and_additions.{lang_code}_{list_type}"
    try:
        module = importlib.import_module(module_name)
        return getattr(module, list_type)
    except (ModuleNotFoundError, AttributeError):
        print("Blacklist or additional words list could not be loaded!")
        return []


if __name__ == "__main__":
    LANGUAGE_CONFIGS = {
        'en': {
            'folder_name': 'English Corpus Data',
            'allowed_chars': "a-zA-Z",
            'strip_s_apostrophe': True,
            'blacklist': load_language_lists('en', 'blacklist'),
            'additional_words': load_language_lists('en', 'additional_words'),
        },
        'de': {
            'folder_name': 'German Corpus Data',
            'allowed_chars': "a-zA-ZäöüßÄÖÜẞ",
            'blacklist': load_language_lists('de', 'blacklist'),
            'additional_words': load_language_lists('de', 'additional_words'),
        },
        'fr': {
            'folder_name': 'French Corpus Data',
            'allowed_chars': "a-zA-ZàâæéèêëîïôœùûüÿçÀÂÆÉÈÊËÎÏÔŒÙÛÜŸÇ",
            'blacklist': load_language_lists('fr', 'blacklist'),
            'additional_words': load_language_lists('fr', 'additional_words'),
        },
        'it': {
            'folder_name': 'Italian Corpus Data',
            'allowed_chars': "a-zA-ZàèéìíîòóùúÀÈÉÌÍÎÒÓÙÚ",
            'blacklist': load_language_lists('it', 'blacklist'),
            'additional_words': load_language_lists('it', 'additional_words'),
        },
        'es': {
            'folder_name': 'Spanish Corpus Data',
            'allowed_chars': "a-zA-ZáéíóúüñÁÉÍÓÚÜÑ",
            'blacklist': load_language_lists('es', 'blacklist'),
            'additional_words': load_language_lists('es', 'additional_words'),
        },
        'pt': {
            'folder_name': 'Portuguese Corpus Data',
            'allowed_chars': "a-zA-ZáâãàçéêíóôõúÀÁÂÃÇÉÊÍÓÔÕÚ",
            'blacklist': load_language_lists('pt', 'blacklist'),
            'additional_words': load_language_lists('pt', 'additional_words'),
        },
    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "Dictionaries")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Output directory is: {output_dir}\n")

    for code, config in LANGUAGE_CONFIGS.items():
        input_folder_path = os.path.join(base_dir, config['folder_name'])
        
        if not os.path.isdir(input_folder_path):
            print(f"--- Skipping language: {code.upper()} ---")
            print(f"Directory not found: '{input_folder_path}'\n")
            continue
            
        # Find all .txt files in the language-specific corpus folder
        input_files = glob.glob(os.path.join(input_folder_path, '*.txt'))
        
        if not input_files:
            print(f"--- Skipping language: {code.upper()} ---")
            print(f"No .txt files found in '{input_folder_path}'\n")
            continue

        # Compile the regex pattern for allowed characters for the current language
        pattern = re.compile(rf"^[-'{config['allowed_chars']}]+$")

        process_language_files(
            language_code=code,
            input_filepaths=input_files,
            output_filepath=os.path.join(output_dir, f"{code}_dict.txt"),
            allowed_chars_pattern=pattern,
            strip_s_apostrophe=config.get('strip_s_apostrophe', False),
            blacklist=config['blacklist'],
            additional_words_to_append=config['additional_words']
        )
        print("-" * 30 + "\n")

    print("All language processing complete.")