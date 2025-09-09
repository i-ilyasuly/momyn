import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')
    VECTOR_STORE_ID = os.getenv('VECTOR_STORE_ID')
    
    # Сессия уақыты (секундпен)
    SESSION_TIMEOUT = 24 * 60 * 60  # 24 сағат
    
    # Сурет параметрлері
    MAX_IMAGE_SIZE = (1024, 1024)
    ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']
    
    @classmethod
    def validate_config(cls):
        """Конфигурацияны тексеру"""
        missing_vars = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            missing_vars.append('TELEGRAM_BOT_TOKEN')
        
        if not cls.OPENAI_API_KEY:
            missing_vars.append('OPENAI_API_KEY')
        
        if not cls.OPENAI_ASSISTANT_ID:
            missing_vars.append('OPENAI_ASSISTANT_ID')
        
        if missing_vars:
            print(f"❌ Келесі environment variable-дар жоқ: {', '.join(missing_vars)}")
            print("📝 .env файлында орнатыңыз:")
            for var in missing_vars:
                print(f"   {var}=your_value_here")
            return False
        
        print("✅ Конфигурация дұрыс орнатылған")
        return True
