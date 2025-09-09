import asyncio
import base64
import io
from datetime import datetime, timedelta
from PIL import Image
from config import Config

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, user_id):
        """Пайдаланушының сессиясын алу"""
        current_time = datetime.now()
        
        if user_id in self.sessions:
            session = self.sessions[user_id]
            # Сессия уақыты өткен жоқ па тексеру
            if current_time - session['last_activity'] < timedelta(seconds=Config.SESSION_TIMEOUT):
                session['last_activity'] = current_time
                return session
            else:
                # Сессия уақыты өткен, жаңасын жасау
                del self.sessions[user_id]
        
        # Жаңа сессия жасау
        self.sessions[user_id] = {
            'thread_id': None,
            'conversation_history': [],
            'last_activity': current_time,
            'user_info': {}
        }
        return self.sessions[user_id]
    
    def update_session(self, user_id, **kwargs):
        """Сессия мәліметтерін жаңарту"""
        session = self.get_session(user_id)
        session.update(kwargs)
        session['last_activity'] = datetime.now()
    
    def clear_old_sessions(self):
        """Ескі сессияларды тазарту"""
        current_time = datetime.now()
        expired_sessions = []
        
        for user_id, session in self.sessions.items():
            if current_time - session['last_activity'] > timedelta(seconds=Config.SESSION_TIMEOUT):
                expired_sessions.append(user_id)
        
        for user_id in expired_sessions:
            del self.sessions[user_id]

def resize_image(image_bytes):
    """Суретті кішірейту"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Форматты тексеру
        if image.format not in Config.ALLOWED_IMAGE_FORMATS:
            return None
        
        # Өлшемін кішірейту
        if image.size[0] > Config.MAX_IMAGE_SIZE[0] or image.size[1] > Config.MAX_IMAGE_SIZE[1]:
            image.thumbnail(Config.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Base64 форматына түрлендіру
        output = io.BytesIO()
        image_format = 'JPEG' if image.format == 'JPEG' else 'PNG'
        image.save(output, format=image_format, quality=85 if image_format == 'JPEG' else None)
        
        return base64.b64encode(output.getvalue()).decode()
    except Exception as e:
        print(f"Сурет өңдеу қатесі: {e}")
        return None
