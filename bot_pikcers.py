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
import base64

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурационные переменные
BOT_TOKEN = "6387413984:AAGUMwJlOidPoKZ3_m1PgFYq1fB0j5yoxDM"
YANDEXART_API_KEY = "ajeimg918cd8u005nb5c"  # Замените на ваш API ключ

# ID группы (замените на реальный!)
GROUP_CHAT_ID = "-1002689149167"

# Время отправки по умолчанию
POST_TIME = time(hour=9, minute=0)  # 09:00 по умолчанию

# Списки промптов для генерации
PROMPTS = [
    "красивый пейзаж с горами в стиле цифрового искусства",
    "футуристический город ночью с неоновыми огнями",
    "милые животные в природе, высокое качество", 
    "космос с планетами и звездами, фантастический стиль",
    "абстрактное искусство с яркими цветами",
    "старинный замок в тумане, мистическая атмосфера",
    "подводный мир с кораллами и тропическими рыбами",
    "осенний лес с золотыми листьями, фотография",
    "магический лес с светящимися растениями",
    "горный водопад в солнечный день"
]

CAT_PROMPTS = [
    "милый пушистый котенок в корзинке, фотореалистично",
    "красивый кот с большими глазами, портрет",
    "кот спит уютно в комнате, мягкое освещение",
    "игривый котенок играет с клубком ниток",
    "кот в короне как король, фэнтези стиль",
    "группа котят вместе, милая сцена",
    "кот в лесу среди природы, натуралистично",
    "кот с магическими крыльями, фантастика",
    "котик в космическом скафандре, научная фантастика",
    "смешной кот в забавной позе, мультяшный стиль"
]

# Настройки для YandexART API
YANDEXART_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGeneration"
YANDEXART_HEADERS = {
    "Authorization": f"Api-Key {YANDEXART_API_KEY}",
    "Content-Type": "application/json"
}

class YandexArtImageGenerator:
    def __init__(self):
        self.session = None
        
    async def init_session(self):
        """Инициализация сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=YANDEXART_HEADERS)
    
    async def close_session(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate_image(self, prompt: str) -> bytes:
        """Генерирует изображение через YandexART API"""
        try:
            await self.init_session()
            
            logger.info(f"🎨 Генерация изображения: {prompt}")
            
            # Параметры для генерации
            payload = {
                "model": "art",  # Модель для генерации изображений
                "generationOptions": {
                    "seed": random.randint(0, 1000000),  # Случайный seed для разнообразия
                    "temperature": 0.7,  # Креативность (0-1)
                    "numImages": 1  # Количество изображений
                },
                "messages": [
                    {
                        "role": "user",
                        "text": f"Сгенерируй изображение: {prompt}. Высокое качество, детализированное, художественное."
                    }
                ]
            }
            
            async with self.session.post(YANDEXART_API_URL, json=payload, timeout=60) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Извлекаем base64 изображение из ответа
                    if 'images' in result and result['images']:
                        image_base64 = result['images'][0]
                        image_data = base64.b64decode(image_base64)
                        
                        logger.info(f"✅ Изображение сгенерировано: {len(image_data)} bytes")
                        return image_data
                    else:
                        logger.warning("❌ Изображение не сгенерировано в ответе API")
                        return await self._get_fallback_image(prompt)
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка API YandexART: {response.status} - {error_text}")
                    return await self._get_fallback_image(prompt)
                    
        except asyncio.TimeoutError:
            logger.error("❌ Таймаут при генерации изображения")
            return await self._get_fallback_image(prompt)
        except Exception as e:
            logger.error(f"❌ Ошибка генерации: {e}")
            return await self._get_fallback_image(prompt)
    
    async def _get_fallback_image(self, prompt: str) -> bytes:
        """Fallback на случай ошибки генерации"""
        try:
            # Пробуем альтернативный метод через поиск (как было раньше)
            return await self._search_backup_image(prompt)
        except:
            return b''
    
    async def _search_backup_image(self, query: str) -> bytes:
        """Резервный поиск через Яндекс.Картинки"""
        try:
            search_url = f"https://yandex.ru/images/search?text={quote(query)}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Упрощенный парсинг для fallback
                        pattern = r'"img_href":"(https?://[^"]+\.(?:jpg|jpeg|png|webp))"'
                        image_urls = re.findall(pattern, html)
                        
                        if image_urls:
                            image_url = random.choice(image_urls)
                            async with session.get(image_url, timeout=20) as img_response:
                                if img_response.status == 200:
                                    return await img_response.read()
            
            return b''
        except:
            return b''

# Инициализация генератора
image_generator = YandexArtImageGenerator()

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
        
        logger.info(f"🎨 Генерация ежедневного изображения для группы {GROUP_CHAT_ID}")
        
        # Выбираем случайный промпт
        prompt = random.choice(PROMPTS + CAT_PROMPTS)
        
        # Генерируем изображение
        image_data = await image_generator.generate_image(prompt)
        
        if image_data and len(image_data) > 1024:
            # Отправляем в группу
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=image_data,
                caption=f"🎨 Ежедневная AI-картинка!\n"
                       f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                       f"🤖 Сгенерировано по запросу: {prompt}\n\n"
                       f"#yandexart #ai #генерация #ежедневно"
            )
            
            # Обновляем статистику
            last_sent_time = datetime.now()
            sent_count += 1
            
            logger.info(f"✅ AI-изображение отправлено в группу")
        else:
            logger.error("❌ Не удалось сгенерировать изображение")
            # Отправляем сообщение об ошибке
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"❌ Сегодня не удалось сгенерировать картинку по запросу: {prompt}\n"
                     f"Попробуем завтра! 🌅"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда"""
    welcome_text = f"""
🎨 *Добро пожаловать в YandexART Бот!*

Я генерирую уникальные изображения с помощью AI и отправляю их в группу.

*📊 Статистика:*
• Отправок: {sent_count}
• Последняя: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}
• Время отправки: {POST_TIME.strftime('%H:%M')}

*📋 Команды:*
/generate - Сгенерировать картинку
/cat - Сгенерировать котика
/status - Статус бота
/settings - Настройки
/set_time - Изменить время отправки
/chat_id - Получить ID чата
/set_group - Установить ID группы
/daily - Принудительная отправка
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация изображения"""
    query = ' '.join(context.args) if context.args else random.choice(PROMPTS)
    
    await update.message.reply_text(f"🎨 Генерирую картинку: {query}")
    
    image_data = await image_generator.generate_image(query)
    
    if image_data and len(image_data) > 1024:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"🤖 Сгенерировано по запросу: {query}"
        )
    else:
        await update.message.reply_text(f"❌ Не удалось сгенерировать картинку по запросу: {query}")

async def generate_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация котика"""
    query = random.choice(CAT_PROMPTS)
    
    await update.message.reply_text(f"🐱 Генерирую котика: {query}")
    
    image_data = await image_generator.generate_image(query)
    
    if image_data and len(image_data) > 1024:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"🐾 Сгенерирован котик: {query}"
        )
    else:
        await update.message.reply_text(f"❌ Не удалось сгенерировать котика :(")

# Остальные функции остаются без изменений (force_daily, set_post_time, show_settings, get_chat_id, set_group_id, bot_status)

async def force_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительная отправка"""
    try:
        if GROUP_CHAT_ID == "-1001234567890":
            await update.message.reply_text("❌ ID группы не настроен!")
            return
        
        await update.message.reply_text("🔄 Принудительная генерация и отправка...")
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
• Генератор: `YandexART API`
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
📊 *Статус YandexART Бота:*

• 🟢 Онлайн и работает
• ⏰ Время отправки: {POST_TIME.strftime('%H:%M')}
• 📝 Промптов: {len(PROMPTS + CAT_PROMPTS)}
• 👥 Группа: {'✅ Настроена' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроена'}
• 🖼 Всего отправок: {sent_count}
• 🕒 Последняя отправка: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}

*🔧 Техническая информация:*
• Генератор: YandexART API
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
            current_job = job_queue.run_daily(
                send_daily_image,
                time=POST_TIME,
                days=tuple(range(7)),
                name="daily_art_job"
            )
            logger.info(f"✅ Ежедневная задача настроена на {POST_TIME.strftime('%H:%M')}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации: {e}")

async def post_stop(application: Application):
    """Очистка при остановке бота"""
    await image_generator.close_session()
    logger.info("✅ Сессия генератора закрыта")

def main():
    """Основная функция"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).post_stop(post_stop).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate_image))
    application.add_handler(CommandHandler("cat", generate_cat))
    application.add_handler(CommandHandler("daily", force_daily))
    application.add_handler(CommandHandler("set_time", set_post_time))
    application.add_handler(CommandHandler("settings", show_settings))
    application.add_handler(CommandHandler("chat_id", get_chat_id))
    application.add_handler(CommandHandler("set_group", set_group_id))
    application.add_handler(CommandHandler("status", bot_status))
    
    # Запускаем бота
    logger.info("🤖 YandexART Бот запускается...")
    application.run_polling()

if __name__ == "__main__":
    main()
