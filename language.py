"""
Language management for the bot
"""

import json
import os
from bot.config import Config

class LanguageManager:
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        for lang in Config.SUPPORTED_LANGUAGES:
            try:
                with open(f'languages/{lang}.json', 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Translation file for {lang} not found")
                self.translations[lang] = {}
    
    def get_text(self, key, language_code=None, **kwargs):
        """Get translated text"""
        if language_code is None:
            language_code = Config.DEFAULT_LANGUAGE
        
        if language_code not in self.translations:
            language_code = Config.DEFAULT_LANGUAGE
        
        text = self.translations.get(language_code, {}).get(key, key)
        
        # Format text with provided arguments
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return text
    
    def get_language_keyboard(self):
        """Get language selection keyboard"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = []
        for lang in Config.SUPPORTED_LANGUAGES:
            lang_name = self.get_text('language_name', lang)
            keyboard.append([InlineKeyboardButton(lang_name, callback_data=f'lang_{lang}')])
        
        return InlineKeyboardMarkup(keyboard)

# Global language manager instance
language_manager = LanguageManager()
