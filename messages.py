class Messages:
    @staticmethod
    def get_welcome_message(language='kk'):
        messages = {
            'kk': """🌟 Халал Сертификат Боты-на қош келдіңіз!

Мен сізге мынадай мәселелерде көмектесе аламын:

🏢 **Мекеме іздеу** - ҚМДБ халал сертификатын алған мекемелер туралы ақпарат
🧪 **Е қоспалары** - Е қоспаларының халал/харам мәртебесі туралы
📷 **Сурет талдау** - Өнім құрамын сурет бойынша талдау

Қажетті опцияны таңдаңыз:""",
            
            'ru': """🌟 Добро пожаловать в Халял Сертификат Бот!

Я могу помочь вам в следующих вопросах:

🏢 **Поиск организации** - Информация об организациях с халяль сертификатом ҚМДБ
🧪 **Пищевые добавки** - Статус халяль/харам пищевых добавок
📷 **Анализ фото** - Анализ состава продукта по фотографии

Выберите нужную опцию:""",
            
'en': """🌟 Welcome to Halal Certificate Bot!

I can help you with the following issues:

🏢 **Company Search** - Information about organizations with ҚМДБ halal certificate
🧪 **E-additives** - Halal/haram status of food additives
📷 **Image Analysis** - Product composition analysis by photo

Select the desired option:"""
        }
        
        return messages.get(language, messages['kk'])
    
    @staticmethod
    def get_help_message(language='kk'):
        messages = {
            'kk': """ℹ️ **Бот туралы ақпарат**

**Мүмкіндіктері:**
• Мекемелердің ҚМДБ халал сертификаты бар-жоғын тексеру
• Е қоспаларының халал/харам мәртебесін білу
• Өнім суретін жүктеп, құрамын талдау
• Үш тілде жұмыс жасау (қазақша, орысша, ағылшынша)

**Пайдалану:**
1. Керекті опцияны таңдаңыз
2. Сұрағыңызды жазыңыз немесе сурет жіберіңіз
3. Нақты жауап алыңыз

Сұрақтарыңыз болса, жай ғана жазыңыз!""",
            
            'ru': """ℹ️ **Информация о боте**

**Возможности:**
• Проверка наличия халяль сертификата ҚМДБ у организаций
• Определение статуса халяль/харам пищевых добавок
• Загрузка фото продукта и анализ состава
• Работа на трех языках (казахский, русский, английский)

**Использование:**
1. Выберите нужную опцию
2. Напишите ваш вопрос или отправьте фото
3. Получите точный ответ

Если есть вопросы, просто напишите!""",
            
'en': """ℹ️ **Bot Information**

**Features:**
• Check if organizations have ҚМДБ halal certificate
• Determine halal/haram status of food additives
• Upload product photos and analyze composition
• Work in three languages (Kazakh, Russian, English)

**Usage:**
1. Select the desired option
2. Write your question or send a photo
3. Get an accurate answer

If you have questions, just write!"""
        }
        
        return messages.get(language, messages['kk'])
    
    @staticmethod
    def get_search_prompt(search_type, language='kk'):
        prompts = {
            'search_company': {
                'kk': '🏢 Мекеме атын жазыңыз (толық немесе қысқартылған):',
                'ru': '🏢 Напишите название организации (полное или сокращенное):',
                'en': '🏢 Write the name of the organization (full or abbreviated):'
            },
            'search_additive': {
                'kk': '🧪 Е қоспасының кодын немесе атауын жазыңыз (мысалы: E100 немесе Куркумин):',
                'ru': '🧪 Напишите код или название пищевой добавки (например: E100 или Куркумин):',
                'en': '🧪 Write the code or name of the food additive (example: E100 or Curcumin):'
            },
            'analyze_image': {
                'kk': '📷 Өнімнің суретін жіберіңіз (этикетка немесе құрам тізімі көрінетіндей):',
                'ru': '📷 Отправьте фото продукта (чтобы была видна этикетка или состав):',
                'en': '📷 Send a photo of the product (so that the label or composition is visible):'
            }
        }
        
        return prompts.get(search_type, {}).get(language, prompts.get(search_type, {}).get('kk', ''))
