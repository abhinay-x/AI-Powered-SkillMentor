"""
Text processing utilities for SkillMentor
"""
import nltk
from nltk.tokenize import word_tokenize
from googletrans import Translator
import logging

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextProcessor:
    """
    Class for processing and normalizing text input
    including multilingual support
    """
    
    def __init__(self):
        """Initialize the text processor with translator"""
        self.translator = Translator()
        logging.info("TextProcessor initialized")
    
    def process_input(self, text, source_lang='en'):
        """
        Process input text:
        1. Translate non-English text to English if needed
        2. Tokenize and normalize the text
        
        Args:
            text (str): The input text query
            source_lang (str): The source language code (default: 'en')
            
        Returns:
            dict: Processed text information
                - original_text: The original input text
                - processed_text: The processed text (translated if needed)
                - tokens: List of tokens
                - source_lang: The detected or provided source language
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        original_text = text
        processed_text = text
        
        # Translate text if not in English
        if source_lang != 'en':
            try:
                translation = self.translator.translate(text, dest='en')
                processed_text = translation.text
                # Update source language in case it was auto-detected
                source_lang = translation.src
                logging.info(f"Translated text from {source_lang} to English")
            except Exception as e:
                logging.error(f"Translation error: {str(e)}")
                # Continue with original text if translation fails
                processed_text = text
        
        # Tokenize the text
        tokens = word_tokenize(processed_text.lower())
        
        return {
            "original_text": original_text,
            "processed_text": processed_text,
            "tokens": tokens,
            "source_lang": source_lang
        }
    
    def translate_to_source(self, text, target_lang):
        """
        Translate text back to the source language if needed
        
        Args:
            text (str): The text to translate
            target_lang (str): The target language code
            
        Returns:
            str: Translated text
        """
        if target_lang == 'en':
            return text
        
        try:
            translation = self.translator.translate(text, dest=target_lang)
            return translation.text
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            return text 