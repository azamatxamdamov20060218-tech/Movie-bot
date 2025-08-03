"""
Database operations for the bot
"""

import sqlite3
import os
from datetime import datetime
from bot.config import Config

class Database:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT DEFAULT 'uz',
                    is_subscribed BOOLEAN DEFAULT FALSE,
                    instagram_followed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Movies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    uploaded_by INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    download_count INTEGER DEFAULT 0
                )
            ''')
            
            # Download history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    movie_code TEXT,
                    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (movie_code) REFERENCES movies (code)
                )
            ''')
            
            conn.commit()
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Add or update user in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, last_activity)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
    
    def get_user(self, user_id):
        """Get user from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()
    
    def update_user_language(self, user_id, language_code):
        """Update user's language preference"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET language_code = ? WHERE user_id = ?',
                (language_code, user_id)
            )
            conn.commit()
    
    def update_subscription_status(self, user_id, is_subscribed, instagram_followed=None):
        """Update user's subscription status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if instagram_followed is not None:
                cursor.execute(
                    'UPDATE users SET is_subscribed = ?, instagram_followed = ? WHERE user_id = ?',
                    (is_subscribed, instagram_followed, user_id)
                )
            else:
                cursor.execute(
                    'UPDATE users SET is_subscribed = ? WHERE user_id = ?',
                    (is_subscribed, user_id)
                )
            conn.commit()
    
    def add_movie(self, code, title, filename, file_path, file_size, uploaded_by):
        """Add movie to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO movies (code, title, filename, file_path, file_size, uploaded_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (code, title, filename, file_path, file_size, uploaded_by))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Code already exists
    
    def get_movie(self, code):
        """Get movie by code"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE code = ?', (code,))
            return cursor.fetchone()
    
    def remove_movie(self, code):
        """Remove movie from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM movies WHERE code = ?', (code,))
            conn.commit()
            return cursor.rowcount > 0
    
    def list_movies(self):
        """List all movies"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT code, title, download_count FROM movies ORDER BY code')
            return cursor.fetchall()
    
    def increment_download_count(self, code):
        """Increment download count for a movie"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE movies SET download_count = download_count + 1 WHERE code = ?',
                (code,)
            )
            conn.commit()
    
    def add_download_record(self, user_id, movie_code):
        """Add download record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO downloads (user_id, movie_code) VALUES (?, ?)',
                (user_id, movie_code)
            )
            conn.commit()
    
    def get_stats(self):
        """Get bot statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Subscribed users
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1')
            subscribed_users = cursor.fetchone()[0]
            
            # Total movies
            cursor.execute('SELECT COUNT(*) FROM movies')
            total_movies = cursor.fetchone()[0]
            
            # Total downloads
            cursor.execute('SELECT COUNT(*) FROM downloads')
            total_downloads = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'subscribed_users': subscribed_users,
                'total_movies': total_movies,
                'total_downloads': total_downloads
            }
