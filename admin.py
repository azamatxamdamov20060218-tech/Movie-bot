"""
Admin functionality for the bot
"""

import os
import shutil
from bot.config import Config
from bot.database import Database
from bot.language import language_manager

class AdminManager:
    def __init__(self):
        self.db = Database()
        Config.ensure_movies_dir()
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        return Config.is_admin(user_id)
    
    def save_movie_file(self, file_path, code, original_filename):
        """Save movie file to movies directory"""
        try:
            # Create filename with code
            file_extension = os.path.splitext(original_filename)[1]
            new_filename = f"{code}{file_extension}"
            destination = os.path.join(Config.MOVIES_DIR, new_filename)
            
            # Copy file to movies directory
            shutil.move(file_path, destination)
            
            return destination, new_filename
        except Exception as e:
            print(f"Error saving movie file: {e}")
            return None, None
    
    def delete_movie_file(self, file_path):
        """Delete movie file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting movie file: {e}")
        return False
    
    def get_admin_keyboard(self, language_code):
        """Get admin panel keyboard"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton(
                language_manager.get_text('add_movie_btn', language_code),
                callback_data='admin_add_movie'
            )],
            [InlineKeyboardButton(
                language_manager.get_text('list_movies_btn', language_code),
                callback_data='admin_list_movies'
            )],
            [InlineKeyboardButton(
                language_manager.get_text('stats_btn', language_code),
                callback_data='admin_stats'
            )],
            [InlineKeyboardButton(
                language_manager.get_text('close', language_code),
                callback_data='admin_close'
            )]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def format_stats(self, language_code):
        """Format bot statistics"""
        stats = self.db.get_stats()
        
        return language_manager.get_text('stats_message', language_code,
            total_users=stats['total_users'],
            subscribed_users=stats['subscribed_users'],
            total_movies=stats['total_movies'],
            total_downloads=stats['total_downloads']
        )
    
    def format_movies_list(self, language_code):
        """Format movies list for admin"""
        movies = self.db.list_movies()
        
        if not movies:
            return language_manager.get_text('no_movies', language_code)
        
        message = language_manager.get_text('movies_list_header', language_code) + "\n\n"
        
        for code, title, download_count in movies:
            message += f"🎬 {code}: {title}\n"
            message += f"📥 {language_manager.get_text('downloads', language_code)}: {download_count}\n\n"
        
        return message

# Global admin manager instance
admin_manager = AdminManager()
