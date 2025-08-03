"""
Configuration settings for the bot
"""

import os

class Config:
    # Telegram channel and Instagram account settings
    TELEGRAM_CHANNEL = "kinolar_olammim"
    TELEGRAM_CHANNEL_URL = "https://t.me/kinolar_olammim"
    INSTAGRAM_ACCOUNT = "@19_xamdamov"
    
    # Admin user IDs (comma-separated in environment variable)
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    
    # Database settings
    DATABASE_PATH = "bot_database.db"
    
    # File storage settings
    MOVIES_DIR = "movies"
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
    
    # Language settings
    DEFAULT_LANGUAGE = "uz"
    SUPPORTED_LANGUAGES = ["uz", "ru", "en"]
    
    @classmethod
    def is_admin(cls, user_id):
        """Check if user is admin"""
        return user_id in cls.ADMIN_IDS
    
    @classmethod
    def ensure_movies_dir(cls):
        """Ensure movies directory exists"""
        os.makedirs(cls.MOVIES_DIR, exist_ok=True)
