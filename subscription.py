"""
Subscription verification functionality
"""

import asyncio
from telegram import Bot
from telegram.error import TelegramError
from bot.config import Config

class SubscriptionChecker:
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
    
    async def check_channel_subscription(self, user_id):
        """Check if user is subscribed to the Telegram channel"""
        try:
            # Get chat member status
            member = await self.bot.get_chat_member(
                chat_id=f"@{Config.TELEGRAM_CHANNEL}",
                user_id=user_id
            )
            
            # Check if user is a member (not left or kicked)
            return member.status in ['member', 'administrator', 'creator']
            
        except TelegramError as e:
            print(f"Error checking subscription: {e}")
            return False
    
    def get_subscription_keyboard(self, language_code):
        """Get subscription verification keyboard with skip option"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        from bot.language import language_manager
        
        keyboard = [
            [InlineKeyboardButton(
                language_manager.get_text('join_channel', language_code),
                url=Config.TELEGRAM_CHANNEL_URL
            )],
            [InlineKeyboardButton(
                language_manager.get_text('follow_instagram', language_code),
                url=f"https://instagram.com/{Config.INSTAGRAM_ACCOUNT.replace('@', '')}"
            )],
            [InlineKeyboardButton(
                language_manager.get_text('check_subscription', language_code),
                callback_data='check_subscription'
            )],
            [InlineKeyboardButton(
                language_manager.get_text('skip_subscription', language_code),
                callback_data='skip_subscription'
            )]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_instagram_confirmation_keyboard(self, language_code):
        """Get Instagram follow confirmation keyboard"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        from bot.language import language_manager
        
        keyboard = [
            [InlineKeyboardButton(
                language_manager.get_text('instagram_followed', language_code),
                callback_data='instagram_followed'
            )],
            [InlineKeyboardButton(
                language_manager.get_text('back', language_code),
                callback_data='back_to_subscription'
            )]
        ]
        
        return InlineKeyboardMarkup(keyboard)
