import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import Config
from openai_client import OpenAIClient
from utils import SessionManager, resize_image

# Логтау орнату
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global объекттер
session_manager = SessionManager()
openai_client = OpenAIClient()

class HalalBot:
    def __init__(self):
        self.application = None
    
    def get_welcome_message(self, language='kk'):
        """Қош келу хабарламасы"""
        messages = {
            'kk': """🌟 Халал Сертификат AI Боты-на қош келдіңіз!

Мен сізге мынадай мәселелерде көмектесе аламын:
• ҚМДБ халал сертификатын алған мекемелер туралы ақпарат
• Е қоспаларының халал/харам мәртебесі туралы
• Өнім құрамын сурет бойынша талдау

**Пайдалану:**
• Мекеме атын жазыңыз - сертификат бар-жоғын тексеремін
• Е қоспасының кодын немесе атауын жазыңыз - мәртебесін айтамын
• Өнім суретін жіберіңіз - құрамын талдап берем

**Тіл ауыстыру:** /language
**Көмек:** /help

Сұрағыңызды жазыңыз немесе сурет жіберіңіз!""",
            
            'ru': """🌟 Добро пожаловать в Халял Сертификат AI Бот!

Я могу помочь вам в следующих вопросах:
• Информация об организациях с халяль сертификатом ҚМДБ
• Статус халяль/харам пищевых добавок
• Анализ состава продукта по фотографии

**Использование:**
• Напишите название организации - проверю наличие сертификата
• Напишите код или название добавки - расскажу о статусе
• Отправьте фото продукта - проанализирую состав

**Смена языка:** /language
**Помощь:** /help

Напишите ваш вопрос или отправьте фото!""",
            
            'en': """🌟 Welcome to Halal Certificate AI Bot!

I can help you with the following issues:
• Information about organizations with ҚМДБ halal certificate
• Halal/haram status of food additives
• Product composition analysis by photo

**Usage:**
• Write organization name - I'll check certificate status
• Write additive code or name - I'll tell about status
• Send product photo - I'll analyze composition

**Language change:** /language
**Help:** /help

Write your question or send a photo!"""
        }
        return messages.get(language, messages['kk'])
    
    def get_language_selection(self):
        """Тіл таңдау хабарламасы"""
        return """🌐 Тілді таңдаңыз / Выберите язык / Choose language:

/kk - Қазақша 🇰🇿
/ru - Русский 🇷🇺  
/en - English 🇺🇸

Тілді таңдағаннан кейін қалыпты режимде жұмыс жасай аласыз."""
    
    def get_help_message(self, language='kk'):
        """Көмек хабарламасы"""
        messages = {
            'kk': """ℹ️ **Бот туралы ақпарат**

**Мүмкіндіктері:**
• Мекемелердің ҚМДБ халал сертификаты бар-жоғын тексеру
• Е қоспаларының халал/харам мәртебесін білу
• Өнім суретін жүктеп, құрамын талдау
• Үш тілде жұмыс жасау

**Команданамлар:**
/start - Ботты қайта іске қосу
/language - Тіл ауыстыру
/help - Көмек

**Мысалдар:**
"Рахат компаниясы халал сертификаты бар ма?"
"E621 қоспасы халал ма?"
[Өнім суретін жіберу]

Кез келген сұрақ қойыңыз!""",
            
            'ru': """ℹ️ **Информация о боте**

**Возможности:**
• Проверка наличия халяль сертификата ҚМДБ у организаций
• Определение статуса халяль/харам пищевых добавок
• Загрузка фото продукта и анализ состава
• Работа на трех языках

**Команды:**
/start - Перезапустить бота
/language - Сменить язык
/help - Помощь

**Примеры:**
"Есть ли у компании Рахат халяль сертификат?"
"Является ли добавка E621 халяль?"
[Отправить фото продукта]

Задавайте любые вопросы!""",
            
            'en': """ℹ️ **Bot Information**

**Features:**
• Check if organizations have ҚМДБ halal certificate
• Determine halal/haram status of food additives
• Upload product photos and analyze composition
• Work in three languages

**Commands:**
/start - Restart bot
/language - Change language
/help - Help

**Examples:**
"Does Rakhat company have halal certificate?"
"Is E621 additive halal?"
[Send product photo]

Ask any questions!"""
        }
        return messages.get(language, messages['kk'])
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Бот іске қосылу"""
        user_id = update.effective_user.id
        user_info = {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username,
            'language': 'kk'  # Әдепкі тіл
        }
        
        # Сессия жасау
        session = session_manager.get_session(user_id)
        session['user_info'] = user_info
        
        # OpenAI байланысын тексеру
        connection_test = await openai_client.test_connection()
        if not connection_test:
            await update.message.reply_text(
                "❌ OpenAI байланысы жоқ. Админстраторға хабарласыңыз.\n\n"
                "Тексеру керек:\n"
                "• OPENAI_API_KEY\n"
                "• OPENAI_ASSISTANT_ID\n"
                "• Интернет байланысы"
            )
            return
        
        # OpenAI thread жасау
        if not session.get('thread_id'):
            thread_id = await openai_client.create_thread()
            if thread_id:
                session['thread_id'] = thread_id
        
        welcome_text = self.get_welcome_message(user_info['language'])
        await update.message.reply_text(welcome_text)
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Тіл таңдау команда"""
        language_text = self.get_language_selection()
        await update.message.reply_text(language_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Көмек команда"""
        user_id = update.effective_user.id
        session = session_manager.get_session(user_id)
        language = session['user_info'].get('language', 'kk')
        
        help_text = self.get_help_message(language)
        await update.message.reply_text(help_text)
    
    async def set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lang_code):
        """Тіл орнату"""
        user_id = update.effective_user.id
        session = session_manager.get_session(user_id)
        session['user_info']['language'] = lang_code
        session_manager.update_session(user_id, user_info=session['user_info'])
        
        success_messages = {
            'kk': '✅ Тіл қазақша орнатылды',
            'ru': '✅ Язык установлен на русский',
            'en': '✅ Language set to English'
        }
        
        await update.message.reply_text(success_messages.get(lang_code, success_messages['kk']))
        
        # Жаңа тілде қош келу хабарламасын көрсету
        welcome_text = self.get_welcome_message(lang_code)
        await update.message.reply_text(welcome_text)
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Мәтін хабарламаларын өңдеу"""
        user_id = update.effective_user.id
        session = session_manager.get_session(user_id)
        language = session['user_info'].get('language', 'kk')
        
        # Thread болмаса жасау
        if not session.get('thread_id'):
            thread_id = await openai_client.create_thread()
            if thread_id:
                session['thread_id'] = thread_id
            else:
                await update.message.reply_text("Техникалық қате орын алды. Кейінірек қайталап көріңіз.")
                return
        
        user_message = update.message.text
        
        # Жауапты күту хабарламасы
        waiting_messages = {
            'kk': '⏳',
            'ru': '⏳',
            'en': '⏳'
        }
        
        waiting_msg = await update.message.reply_text(waiting_messages.get(language, waiting_messages['kk']))
        
        # OpenAI-дан жауап алу
        response = await openai_client.send_message(session['thread_id'], user_message)
        
        # Күту хабарламасын жою
        await waiting_msg.delete()
        
        # Жауапты жіберу
        await update.message.reply_text(response)
        
        # Сессияны жаңарту
        session['conversation_history'].append({
            'timestamp': datetime.now(),
            'user_message': user_message,
            'bot_response': response
        })
    
    async def photo_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сурет хабарламаларын өңдеу"""
        user_id = update.effective_user.id
        session = session_manager.get_session(user_id)
        language = session['user_info'].get('language', 'kk')
        
        # Thread болмаса жасау
        if not session.get('thread_id'):
            thread_id = await openai_client.create_thread()
            if thread_id:
                session['thread_id'] = thread_id
            else:
                error_messages = {
                    'kk': 'Техникалық қате орын алды. Кейінірек қайталап көріңіз.',
                    'ru': 'Произошла техническая ошибка. Попробуйте позже.',
                    'en': 'A technical error occurred. Please try again later.'
                }
                await update.message.reply_text(error_messages.get(language, error_messages['kk']))
                return
        
        try:
            # Суретті жүктеу
            photo = update.message.photo[-1]  # Ең үлкен көлемді алу
            file = await context.bot.get_file(photo.file_id)
            file_bytes = await file.download_as_bytearray()
            
            # Суретті өңдеу
            image_base64 = resize_image(file_bytes)
            if not image_base64:
                error_messages = {
                    'kk': 'Сурет форматы қолдаумен емес. JPG, PNG немесе WEBP форматында жіберіңіз.',
                    'ru': 'Неподдерживаемый формат изображения. Отправьте в формате JPG, PNG или WEBP.',
                    'en': 'Unsupported image format. Send in JPG, PNG or WEBP format.'
                }
                await update.message.reply_text(error_messages.get(language, error_messages['kk']))
                return
            
            # Хабарлама дайындау
            caption = update.message.caption or ""
            formatted_message = f"Сурет бойынша өнім құрамын талдау: {caption}".strip()
            
            # Жауапты күту хабарламасы
            waiting_messages = {
                'kk': '📸 Суретті талдап жатырмын...',
                'ru': '📸 Анализирую изображение...',
                'en': '📸 Analyzing image...'
            }
            
            waiting_msg = await update.message.reply_text(waiting_messages.get(language, waiting_messages['kk']))
            
            # OpenAI-дан жауап алу
            response = await openai_client.send_message(
                session['thread_id'], 
                formatted_message, 
                image_base64=image_base64
            )
            
            # Күту хабарламасын жою
            await waiting_msg.delete()
            
            # Жауапты жіберу
            await update.message.reply_text(response)
            
            # Сессияны жаңарту
            session['conversation_history'].append({
                'timestamp': datetime.now(),
                'user_message': f"[Сурет] {caption}",
                'bot_response': response
            })
            
        except Exception as e:
            logger.error(f"Сурет өңдеу қатесі: {e}")
            error_messages = {
                'kk': 'Суретті өңдеуде қате орын алды. Қайталап көріңіз.',
                'ru': 'Ошибка при обработке изображения. Попробуйте еще раз.',
                'en': 'Error processing image. Please try again.'
            }
            await update.message.reply_text(error_messages.get(language, error_messages['kk']))
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Қателерді өңдеу"""
        logger.error(f"Update {update} қатеге себеп болды: {context.error}")
    
    def run(self):
        """Ботты іске қосу"""
        # Application жасау
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Handler-лерді қосу
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Тіл орнату команданамары
        self.application.add_handler(CommandHandler("kk", lambda u, c: self.set_language(u, c, 'kk')))
        self.application.add_handler(CommandHandler("ru", lambda u, c: self.set_language(u, c, 'ru')))
        self.application.add_handler(CommandHandler("en", lambda u, c: self.set_language(u, c, 'en')))
        
        # Хабарлама handler-лері
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.photo_handler))
        self.application.add_error_handler(self.error_handler)
        
        # Ботты іске қосу
        print("🚀 Халал Сертификат AI Боты іске қосылды!")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    # Конфигурацияны тексеру
    if not Config.validate_config():
        print("❌ Бот іске қосылмады. Конфигурацияны дұрыстаңыз.")
        exit(1)
    
    bot = HalalBot()
    bot.run()
