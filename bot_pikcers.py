import logging
import random
import asyncio
import aiohttp
import re
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import io
from urllib.parse import quote
import json

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурационные переменные
BOT_TOKEN = "6387413984:AAGUMwJlOidPoKZ3_m1PgFYq1fB0j5yoxDM"

# ID группы (замените на реальный!)
GROUP_CHAT_ID = "-1002592721236"

# Время отправки по умолчанию
POST_TIME = time(hour=9, minute=0)  # 09:00 по умолчанию

# Списки промптов для поиска
PROMPTS = [
    "красивый пейзаж с горами",
    "футуристический город ночью",
    "милые животные в природе", 
    "космос планеты звезды",
    "абстрактное искусство",
    "старинный замок",
    "подводный мир кораллы",
    "осенний лес золотые листья",
    "магический лес",
    "горный водопад"
]

CAT_PROMPTS = [
    "милый пушистый котенок",
    "красивый кот глаза",
    "кот спит корзине",
    "игривый котенок играет",
    "кот в короне",
    "группа котят",
    "кот в лесу",
    "кот с крыльями",
    "котик в космосе",
    "смешной кот"
]

# User-Agent для имитации браузера
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class YandexImageSearcher:
    def __init__(self):
        self.session = None
        
    async def init_session(self):
        """Инициализация сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=HEADERS)
    
    async def close_session(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search_image(self, query: str) -> bytes:
        """Ищет изображение через Яндекс Картинки"""
        try:
            await self.init_session()
            
            # Кодируем запрос для URL
            encoded_query = quote(query)
            
            # URL для поиска в Яндекс Картинках
            search_url = f"https://yandex.ru/images/search?text={encoded_query}&itype=jpg"
            
            logger.info(f"🔍 Поиск изображения: {query}")
            
            async with self.session.get(search_url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Ищем URL изображений в HTML
                    image_urls = self._extract_image_urls(html)
                    
                    if image_urls:
                        # Выбираем случайное изображение
                        image_url = random.choice(image_urls)
                        logger.info(f"📷 Найдено изображение: {image_url}")
                        
                        # Скачиваем изображение
                        return await self._download_image(image_url)
                    else:
                        logger.warning("❌ Изображения не найдены в HTML")
                        return await self._get_fallback_image(query)
                else:
                    logger.error(f"❌ Ошибка HTTP: {response.status}")
                    return await self._get_fallback_image(query)
                    
        except Exception as e:
            logger.error(f"❌ Ошибка поиска: {e}")
            return await self._get_fallback_image(query)
    
    def _extract_image_urls(self, html: str) -> list:
        """Извлекает URL изображений из HTML"""
        try:
            # Паттерны для поиска URL изображений
            patterns = [
                r'"img_href":"(https?://[^"]+\.(?:jpg|jpeg|png|webp))"',
                r'src="(https?://[^"]+\.(?:jpg|jpeg|png|webp))"',
                r'url\(\'(https?://[^"]+\.(?:jpg|jpeg|png|webp))\'\)',
            ]
            
            image_urls = []
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                # Фильтруем только валидные URL
                valid_urls = [url for url in matches if self._is_valid_image_url(url)]
                image_urls.extend(valid_urls)
            
            # Убираем дубликаты
            return list(set(image_urls))[:20]  # Берем первые 20 уникальных
            
        except Exception as e:
            logger.error(f"❌ Ошибка извлечения URL: {e}")
            return []
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Проверяет валидность URL изображения"""
        # Исключаем логотипы, иконки и маленькие изображения
        exclude_keywords = [
            'logo', 'icon', 'avatar', 'thumb', 'small', 
            'pixel', 'placeholder', 'yandex', 'google'
        ]
        
        url_lower = url.lower()
        return (
            any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']) and
            not any(keyword in url_lower for keyword in exclude_keywords) and
            'http' in url_lower
        )
    
    async def _download_image(self, image_url: str) -> bytes:
        """Скачивает изображение по URL"""
        try:
            async with self.session.get(image_url, timeout=20) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    # Проверяем, что это действительно изображение
                    if len(image_data) > 1024:  # Минимум 1KB
                        logger.info(f"✅ Изображение скачано: {len(image_data)} bytes")
                        return image_data
                    else:
                        logger.warning("❌ Слишком маленькое изображение")
                        return b''
                else:
                    logger.error(f"❌ Ошибка загрузки: {response.status}")
                    return b''
                    
        except Exception as e:
            logger.error(f"❌ Ошибка скачивания: {e}")
            return b''
    
    async def _get_fallback_image(self, query: str) -> bytes:
        """Создает fallback изображение"""
        try:
            # Пробуем альтернативный поиск через быстрый API
            return await self._search_alternative(query)
        except:
            return b''
    
    async def _search_alternative(self, query: str) -> bytes:
        """Альтернативный поиск через другие методы"""
        try:
            # Пробуем поиск через Google Images (альтернативный метод)
            google_url = f"https://www.google.com/search?q={quote(query)}&tbm=isch"
            
            async with self.session.get(google_url, timeout=20) as response:
                if response.status == 200:
                    html = await response.text()
                    # Упрощенный парсинг Google Images
                    image_pattern = r'"(https?://[^"]+\.(?:jpg|jpeg|png|webp))"'
                    image_urls = re.findall(image_pattern, html, re.IGNORECASE)
                    
                    if image_urls:
                        image_url = random.choice(image_urls)
                        return await self._download_image(image_url)
            
            return b''
        except:
            return b''

# Инициализация поисковика
image_searcher = YandexImageSearcher()

# Переменные состояния
last_sent_time = None
sent_count = 0
current_job = None

async def send_daily_image(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневное изображение в группу"""
    global last_sent_time, sent_count
    
    try:
        if GROUP_CHAT_ID == "-1002592721236":
            logger.error("❌ ID группы не настроен!")
            return
        
        logger.info(f"🕒 Поиск изображения для группы {GROUP_CHAT_ID}")
        
        # Выбираем случайный промпт
        prompt = random.choice(PROMPTS + CAT_PROMPTS)
        
        # Ищем изображение
        image_data = await image_searcher.search_image(prompt)
        
        if image_data and len(image_data) > 1024:
            # Отправляем в группу
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=image_data,
                caption=f"🎨 Ежедневная картинка!\n"
                       f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                       f"🔍 По запросу: {prompt}\n\n"
                       f"#яндекс #картинки #ежедневно"
            )
            
            # Обновляем статистику
            last_sent_time = datetime.now()
            sent_count += 1
            
            logger.info(f"✅ Изображение отправлено в группу")
        else:
            logger.error("❌ Не удалось найти подходящее изображение")
            # Отправляем сообщение об ошибке
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"❌ Сегодня не удалось найти картинку по запросу: {prompt}\n"
                     f"Попробуем завтра! 🌅"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда"""
    welcome_text = f"""
🎨 *Добро пожаловать в Картинки Бот!*

Я ищу красивые изображения и отправляю их в группу.

*📊 Статистика:*
• Отправок: {sent_count}
• Последняя: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}
• Время отправки: {POST_TIME.strftime('%H:%M')}

*📋 Команды:*
/search - Найти картинку
/cat - Найти котика
/status - Статус бота
/settings - Настройки
/set_time - Изменить время отправки
/chat_id - Получить ID чата
/set_group - Установить ID группы
/daily - Принудительная отправка
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def search_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск изображения"""
    query = ' '.join(context.args) if context.args else random.choice(PROMPTS)
    
    await update.message.reply_text(f"🔍 Ищу картинку: {query}")
    
    image_data = await image_searcher.search_image(query)
    
    if image_data and len(image_data) > 1024:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"📷 Найдено по запросу: {query}"
        )
    else:
        await update.message.reply_text(f"❌ Не удалось найти картинку по запросу: {query}")

async def search_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск котика"""
    query = random.choice(CAT_PROMPTS)
    
    await update.message.reply_text(f"🐱 Ищу котика: {query}")
    
    image_data = await image_searcher.search_image(query)
    
    if image_data and len(image_data) > 1024:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"🐾 Найден котик: {query}"
        )
    else:
        await update.message.reply_text(f"❌ Не удалось найти котика :(")

async def force_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительная отправка"""
    try:
        if GROUP_CHAT_ID == "-1001234567890":
            await update.message.reply_text("❌ ID группы не настроен!")
            return
        
        await update.message.reply_text("🔄 Принудительный поиск и отправка...")
        await send_daily_image(context)
        await update.message.reply_text("✅ Сообщение отправлено в группу!")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def set_post_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка времени отправки"""
    global POST_TIME, current_job
    
    if not context.args:
        await update.message.reply_text("❌ Укажите время: /set_time ЧЧ:ММ\nПример: /set_time 09:30")
        return
    
    try:
        time_str = context.args[0]
        hours, minutes = map(int, time_str.split(':'))
        
        if not (0 <= hours < 24 and 0 <= minutes < 60):
            raise ValueError("Некорректное время")
        
        # Обновляем время
        POST_TIME = time(hour=hours, minute=minutes)
        
        # Перезапускаем job с новым временем
        job_queue = context.application.job_queue
        if job_queue and current_job:
            current_job.schedule_removal()
        
        current_job = job_queue.run_daily(
            send_daily_image,
            time=POST_TIME,
            days=tuple(range(7)),
            name="daily_art_job"
        )
        
        await update.message.reply_text(f"✅ Время отправки установлено: {time_str}")
        logger.info(f"Время отправки изменено на: {time_str}")
        
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Неверный формат времени. Используйте: ЧЧ:ММ\nПример: /set_time 09:30")

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать настройки"""
    settings_text = f"""
⚙️ *Настройки бота:*

• Время отправки: `{POST_TIME.strftime('%H:%M')}`
• ID группы: `{'✅ Настроен' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроен'}`
• Поисковик: `Яндекс Картинки`
• Промптов: `{len(PROMPTS + CAT_PROMPTS)}`

*Команды настроек:*
/set_time ЧЧ:ММ - Изменить время отправки
/set_group ID - Установить ID группы
    """
    await update.message.reply_text(settings_text, parse_mode='Markdown')

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить ID чата"""
    chat_info = f"""
📋 *Информация о чате:*

• ID: `{update.message.chat_id}`
• Тип: `{update.message.chat.type}`
• Название: `{update.message.chat.title or 'Личный чат'}`

💡 *Для установки группы:*
1. Добавьте бота в группу
2. Напишите `/chat_id` в группе
3. Скопируйте ID группы
4. Используйте `/set_group ID_группы`
    """
    await update.message.reply_text(chat_info, parse_mode='Markdown')

async def set_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить ID группы"""
    if not context.args:
        await update.message.reply_text("❌ Укажите ID группы: /set_group <group_id>")
        return
    
    global GROUP_CHAT_ID
    GROUP_CHAT_ID = context.args[0]
    await update.message.reply_text(f"✅ ID группы установлен: `{GROUP_CHAT_ID}`", parse_mode='Markdown')

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота"""
    status_text = f"""
📊 *Статус Яндекс Картинки Бота:*

• 🟢 Онлайн и работает
• ⏰ Время отправки: {POST_TIME.strftime('%H:%M')}
• 📝 Промптов: {len(PROMPTS + CAT_PROMPTS)}
• 👥 Группа: {'✅ Настроена' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроена'}
• 🖼 Всего отправок: {sent_count}
• 🕒 Последняя отправка: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}

*🔧 Техническая информация:*
• Поисковик: Яндекс Картинки
• ID группы: `{GROUP_CHAT_ID}`
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def post_init(application: Application):
    """Инициализация после запуска бота"""
    global current_job
    
    try:
        job_queue = application.job_queue
        if job_queue:
            # Создаем ежедневную задачу
            current_job
