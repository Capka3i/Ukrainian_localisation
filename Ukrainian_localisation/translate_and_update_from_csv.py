import os
import csv
import re
from googletrans import Translator
from tqdm import tqdm  # For progress bar

# Initialize the Google Translator
translator = Translator()

# Function to remove HTML tags from the text
def remove_html_tags(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)

# Function to restore HTML tags in translated text
def restore_html_tags(original_text, translated_text):
    html_tags = re.findall(r"<.*?>", original_text)
    for tag in html_tags:
        translated_text = translated_text.replace(" ", "", 1)
        translated_text = translated_text.replace(" ", tag, 1)
    return translated_text

# Function to handle placeholders like {0}, {1}, etc.
def handle_placeholders(text):
    placeholders = re.findall(r"{\d+}", text)
    for placeholder in placeholders:
        text = text.replace(placeholder, f"__{placeholder}__")
    return text, placeholders

def restore_placeholders(translated_text, placeholders):
    for placeholder in placeholders:
        translated_text = translated_text.replace(f"__{placeholder}__", placeholder)
    return translated_text

# Function to check if text is already translated
def is_already_translated(original_text, translated_text, dest_lang='uk'):
    try:
        # Use Google Translator to detect the language of the translated text
        detected_lang = translator.detect(translated_text).lang
        return detected_lang == dest_lang
    except Exception as e:
        print(f"Error detecting language for text: {translated_text}\nError: {e}")
        return False

# Function to translate text with placeholder and HTML tag handling
def translate_text(original_text, translated_text, dest_lang='uk'):
    if translated_text and is_already_translated(original_text, translated_text, dest_lang):
        return translated_text  # Skip if already translated
    try:
        cleaned_text, placeholders = handle_placeholders(original_text)  # Handle placeholders
        clean_text = remove_html_tags(cleaned_text)  # Remove HTML tags
        translated_text = translator.translate(clean_text, dest=dest_lang).text
        translated_text = restore_placeholders(translated_text, placeholders)  # Restore placeholders
        translated_text = restore_html_tags(original_text, translated_text)  # Restore HTML tags
        return translated_text
    except Exception as e:
        print(f"Translation error for text: {original_text}\nError: {e}")
        return original_text

# Function to translate CSV files in a directory
def translate_csv_files_in_directory(directory, dest_lang='uk'):
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            print(f"Processing file: {file_path}")

            # Read the CSV file
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                fieldnames = reader.fieldnames

            # Translate the text and comments columns with progress bar
            with tqdm(total=len(rows), desc=f"Translating {filename}", ncols=80) as pbar:
                for row in rows:
                    if 'Text' in row and row['Text']:
                        row['Text'] = translate_text(row['Text'], row.get('TranslatedText', ''), dest_lang)
                    if 'Comments' in row and row['Comments']:
                        row['Comments'] = translate_text(row['Comments'], row.get('TranslatedComments', ''), dest_lang)
                    pbar.update(1)

            # Write the translated content back to the CSV file
            with open(file_path, mode='w', encoding='utf-8', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"Translated file saved: {file_path}")

# Directory containing the CSV files
directory = './'

# Translate all CSV files in the directory
translate_csv_files_in_directory(directory, dest_lang='uk')
