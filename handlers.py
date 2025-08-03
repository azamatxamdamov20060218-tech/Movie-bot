"""
Main bot handlers
"""

import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.config import Config
from bot.database import Database
from bot.language import language_manager
from bot.subscription import SubscriptionChecker
from bot.admin import admin_manager

class BotHandlers:
    def __init__(self):
        self.db = Database()
        self.subscription_checker = None
        self.pending_movies = {}  # Store pending movie uploads for admins
    
    def get_subscription_checker(self, context):
        """Get or create subscription checker"""
        if self.subscription_checker is None:
            self.subscription_checker = SubscriptionChecker(context.bot.token)
        return self.subscription_checker
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        self.db.add_user(user.id, user.username, user.first_name, user.last_name)
        
        # Get user's language preference
        user_data = self.db.get_user(user.id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        # Welcome message with subscription request
        welcome_text = language_manager.get_text('welcome_message_with_subscription', language_code, 
                                                  first_name=user.first_name or 'User')
        
        # Language selection keyboard
        keyboard = language_manager.get_language_keyboard()
        
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
    
    async def language_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show language selection menu"""
        user_data = self.db.get_user(update.effective_user.id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        text = language_manager.get_text('select_language', language_code)
        keyboard = language_manager.get_language_keyboard()
        
        await update.message.reply_text(text, reply_markup=keyboard)
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if not admin_manager.is_admin(user_id):
            return
        
        user_data = self.db.get_user(user_id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        text = language_manager.get_text('admin_panel', language_code)
        keyboard = admin_manager.get_admin_keyboard(language_code)
        
        await update.message.reply_text(text, reply_markup=keyboard)
    
    async def add_movie(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /add_movie command"""
        user_id = update.effective_user.id
        
        if not admin_manager.is_admin(user_id):
            return
        
        user_data = self.db.get_user(user_id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        if len(context.args) < 2:
            text = language_manager.get_text('add_movie_usage', language_code)
            await update.message.reply_text(text)
            return
        
        code = context.args[0]
        title = " ".join(context.args[1:])
        
        # Store pending movie info
        self.pending_movies[user_id] = {'code': code, 'title': title}
        
        text = language_manager.get_text('send_movie_file', language_code, code=code, title=title)
        await update.message.reply_text(text)
    
    async def remove_movie(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remove_movie command"""
        user_id = update.effective_user.id
        
        if not admin_manager.is_admin(user_id):
            return
        
        user_data = self.db.get_user(user_id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        if not context.args:
            text = language_manager.get_text('remove_movie_usage', language_code)
            await update.message.reply_text(text)
            return
        
        code = context.args[0]
        movie = self.db.get_movie(code)
        
        if not movie:
            text = language_manager.get_text('movie_not_found', language_code, code=code)
            await update.message.reply_text(text)
            return
        
        # Remove from database and delete file
        if self.db.remove_movie(code):
            admin_manager.delete_movie_file(movie[4])  # file_path is at index 4
            text = language_manager.get_text('movie_removed', language_code, code=code)
        else:
            text = language_manager.get_text('movie_remove_error', language_code)
        
        await update.message.reply_text(text)
    
    async def list_movies(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list_movies command"""
        user_id = update.effective_user.id
        
        if not admin_manager.is_admin(user_id):
            return
        
        user_data = self.db.get_user(user_id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        message = admin_manager.format_movies_list(language_code)
        await update.message.reply_text(message)
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        
        if not admin_manager.is_admin(user_id):
            return
        
        user_data = self.db.get_user(user_id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        message = admin_manager.format_stats(language_code)
        await update.message.reply_text(message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (movie codes)"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        # Get user data
        user_data = self.db.get_user(user_id)
        if not user_data:
            await self.start(update, context)
            return
        
        language_code = user_data[4]
        
        # No subscription check - bot works for everyone
        
        # Try to find movie by code
        movie = self.db.get_movie(message_text)
        
        if movie:
            # Send movie file
            try:
                file_path = movie[4]  # file_path is at index 4
                
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as movie_file:
                        await update.message.reply_document(
                            document=movie_file,
                            filename=movie[3],  # filename is at index 3
                            caption=language_manager.get_text('movie_sent', language_code, title=movie[2])
                        )
                    
                    # Update download count and add record
                    self.db.increment_download_count(message_text)
                    self.db.add_download_record(user_id, message_text)
                else:
                    text = language_manager.get_text('movie_file_not_found', language_code)
                    await update.message.reply_text(text)
                    
            except Exception as e:
                print(f"Error sending movie: {e}")
                text = language_manager.get_text('movie_send_error', language_code)
                await update.message.reply_text(text)
        else:
            text = language_manager.get_text('invalid_code', language_code, code=message_text)
            await update.message.reply_text(text)
    
    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle file uploads from admins"""
        user_id = update.effective_user.id
        
        if not admin_manager.is_admin(user_id):
            return
        
        user_data = self.db.get_user(user_id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        # Check if admin has pending movie
        if user_id not in self.pending_movies:
            text = language_manager.get_text('no_pending_movie', language_code)
            await update.message.reply_text(text)
            return
        
        pending_movie = self.pending_movies[user_id]
        
        try:
            # Download file
            file = update.message.document or update.message.video
            file_obj = await context.bot.get_file(file.file_id)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                await file_obj.download_to_drive(temp_file.name)
                temp_path = temp_file.name
            
            # Save movie file
            file_path, filename = admin_manager.save_movie_file(
                temp_path, pending_movie['code'], file.file_name
            )
            
            if file_path:
                # Add to database
                success = self.db.add_movie(
                    pending_movie['code'],
                    pending_movie['title'],
                    filename,
                    file_path,
                    file.file_size,
                    user_id
                )
                
                if success:
                    text = language_manager.get_text('movie_added', language_code,
                                                     code=pending_movie['code'],
                                                     title=pending_movie['title'])
                    del self.pending_movies[user_id]
                else:
                    text = language_manager.get_text('movie_code_exists', language_code)
                    admin_manager.delete_movie_file(file_path)
            else:
                text = language_manager.get_text('movie_save_error', language_code)
            
            await update.message.reply_text(text)
            
        except Exception as e:
            print(f"Error handling file upload: {e}")
            text = language_manager.get_text('file_upload_error', language_code)
            await update.message.reply_text(text)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Get user data
        user_data = self.db.get_user(user_id)
        language_code = user_data[4] if user_data else Config.DEFAULT_LANGUAGE
        
        # Language selection
        if data.startswith('lang_'):
            new_language = data.split('_')[1]
            if new_language in Config.SUPPORTED_LANGUAGES:
                self.db.update_user_language(user_id, new_language)
                
                text = language_manager.get_text('language_changed_with_subscription', new_language)
                keyboard = self.get_subscription_checker(context).get_subscription_keyboard(new_language)
                
                await query.edit_message_text(text, reply_markup=keyboard)
        
        # Subscription check
        elif data == 'check_subscription':
            checker = self.get_subscription_checker(context)
            is_subscribed = await checker.check_channel_subscription(user_id)
            
            if is_subscribed:
                self.db.update_subscription_status(user_id, True)
                
                # Show Instagram follow request
                text = language_manager.get_text('instagram_follow_request', language_code,
                                                 instagram=Config.INSTAGRAM_ACCOUNT)
                keyboard = checker.get_instagram_confirmation_keyboard(language_code)
                
                try:
                    await query.edit_message_text(text, reply_markup=keyboard)
                except Exception as e:
                    print(f"Error editing message: {e}")
                    await query.message.reply_text(text, reply_markup=keyboard)
            else:
                text = language_manager.get_text('not_subscribed_soft', language_code)
                keyboard = checker.get_subscription_keyboard(language_code)
                
                try:
                    await query.edit_message_text(text, reply_markup=keyboard)
                except Exception as e:
                    print(f"Error editing message: {e}")
                    await query.message.reply_text(text, reply_markup=keyboard)
        
        # Instagram follow confirmation
        elif data == 'instagram_followed':
            self.db.update_subscription_status(user_id, True, True)
            
            text = language_manager.get_text('setup_complete_soft', language_code)
            try:
                await query.edit_message_text(text)
            except Exception as e:
                print(f"Error editing message: {e}")
                await query.message.reply_text(text)
        
        # Skip subscription - allow bot usage
        elif data == 'skip_subscription':
            text = language_manager.get_text('skip_subscription_message', language_code)
            try:
                await query.edit_message_text(text)
            except Exception as e:
                print(f"Error editing message: {e}")
                await query.message.reply_text(text)
        
        # Back to subscription
        elif data == 'back_to_subscription':
            checker = self.get_subscription_checker(context)
            text = language_manager.get_text('subscription_request_soft', language_code)
            keyboard = checker.get_subscription_keyboard(language_code)
            
            await query.edit_message_text(text, reply_markup=keyboard)

        # Admin panel actions
        elif data.startswith('admin_'):
            if not admin_manager.is_admin(user_id):
                return
            
            if data == 'admin_add_movie':
                text = language_manager.get_text('add_movie_instructions', language_code)
                await query.edit_message_text(text)
            
            elif data == 'admin_list_movies':
                message = admin_manager.format_movies_list(language_code)
                await query.edit_message_text(message)
            
            elif data == 'admin_stats':
                message = admin_manager.format_stats(language_code)
                await query.edit_message_text(message)
            
            elif data == 'admin_close':
                await query.edit_message_text(
                    language_manager.get_text('admin_panel_closed', language_code)
                )
