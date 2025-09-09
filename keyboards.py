from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    @staticmethod
    def main_menu(language='kk'):
        """Басты меню"""
        buttons = {
            'kk': {
                'company': '🏢 Мекеме іздеу',
                'additive': '🧪 Е қоспасы туралы',
                'image': '📷 Сурет бойынша талдау',
                'help': 'ℹ️ Көмек',
                'language': '🌐 Тіл ауыстыру'
            },
            'ru': {
                'company': '🏢 Поиск организации',
                'additive': '🧪 О пищевых добавках',
                'image': '📷 Анализ по фото',
                'help': 'ℹ️ Помощь',
                'language': '🌐 Сменить язык'
            },
            'en': {
                'company': '🏢 Search Company',
                'additive': '🧪 About E-additives',
                'image': '📷 Image Analysis',
                'help': 'ℹ️ Help',
                'language': '🌐 Change Language'
            }
        }
        
        lang_buttons = buttons.get(language, buttons['kk'])
        
        keyboard = [
            [InlineKeyboardButton(lang_buttons['company'], callback_data='search_company')],
            [InlineKeyboardButton(lang_buttons['additive'], callback_data='search_additive')],
            [InlineKeyboardButton(lang_buttons['image'], callback_data='analyze_image')],
            [InlineKeyboardButton(lang_buttons['help'], callback_data='help'),
             InlineKeyboardButton(lang_buttons['language'], callback_data='change_language')]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def language_menu():
        """Тіл таңдау мәзірі"""
        keyboard = [
            [InlineKeyboardButton('🇰🇿 Қазақша', callback_data='lang_kk')],
            [InlineKeyboardButton('🇷🇺 Русский', callback_data='lang_ru')],
            [InlineKeyboardButton('🇺🇸 English', callback_data='lang_en')],
            [InlineKeyboardButton('⬅️ Артқа', callback_data='back_to_main')]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main(language='kk'):
        """Басты мәзірге оралу"""
        text = {
            'kk': '⬅️ Басты мәзірге',
            'ru': '⬅️ Главное меню',
            'en': '⬅️ Main Menu'
        }
        
        keyboard = [[InlineKeyboardButton(
            text.get(language, text['kk']), 
            callback_data='back_to_main'
        )]]
        
        return InlineKeyboardMarkup(keyboard)
