import logging
import random
import asyncio
import aiohttp
import json
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import io
import base64

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурационные переменные
BOT_TOKEN = "6387413984:AAGUMwJlOidPoKZ3_m1PgFYq1fB0j5yoxDM"
NEUROIMG_API_KEY = "3747955d-f4e0-4dc4-b11a-941c6e08bb5d"
NEUROIMG_API_URL = "https://api.neuroimg.art/v1/generate"

# ID группы (замените на реальный!)
GROUP_CHAT_ID = "-1002592721236"

# Время отправки по умолчанию
POST_TIME = time(hour=9, minute=0)  # 09:00 по умолчанию

# Списки промптов
PROMPTS = [
    "Beautiful landscape with mountains and lake, 4k, photorealistic",
    "Futuristic city with neon lights, cyberpunk style, detailed",
    "Cute animals in natural environment, high quality, vibrant colors",
    "Cosmic space with planets and stars, nebula, vibrant colors",
    "Abstract art with bright colors and shapes, digital painting",
    "Ancient castle in fog, mystical atmosphere, fantasy art",
    "Underwater world with corals and tropical fish, clear water",
    "Autumn forest with golden leaves, cozy atmosphere, sunlight",
    "Magical forest with glowing plants, fantasy style, enchanting",
    "Mountain waterfall in sunny day, nature, peaceful"
]

CAT_PROMPTS = [
    "Cute fluffy kitten playing with yarn, photorealistic, detailed fur",
    "Majestic cat sitting on a throne, royal style, beautiful eyes",
    "Sleeping cat in a cozy basket, warm lighting, peaceful",
    "Cat with beautiful green eyes, detailed fur, high quality",
    "Playful kitten chasing a butterfly in garden, happy, vibrant colors"
]

# Переменные состояния
last_sent_time = None
sent_count = 0
current_job = None

class NeuroImageGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_image(self, prompt: str) -> bytes:
        """Генерирует изображение через NeuroImg API"""
        try:
            logger.info(f"Генерация изображения: {prompt}")
            
            payload = {
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "steps": 20,
                "cfg_scale": 7.5,
                "sampler": "Euler",
                "seed": random.randint(0, 999999999),
                "model": "stable-diffusion-xl",
                "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    NEUROIMG_API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if result.get("status") == "success" and result.get("data"):
                            image_data = result["data"].get("image")
                            if image_data:
                                # Декодируем base64 изображение
                                if image_data.startswith('data:image'):
                                    image_data = image_data.split(',')[1]
                                return base64.b64decode(image_data)
                    
                    logger.error(f"Ошибка API: {response.status}")
                    return await self._create_fallback_image(prompt)
                    
        except Exception as e:
            logger.error(f"Ошибка генерации NeuroImg: {e}")
            return await self._create_fallback_image(prompt)
    
    async def _create_fallback_image(self, prompt: str) -> bytes:
        """Создает fallback изображение"""
        # Простое изображение с градиентом
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (512, 512), color=(
                random.randint(50, 200),
                random.randint(50, 200), 
                random.randint(50, 200)
            ))
            draw = ImageDraw.Draw(img)
            for i in range(512):
                r = int(i / 512 * 255)
                g = random.randint(0, 255)
                b = 255 - int(i / 512 * 255)
                draw.line([(0, i), (512, i)], fill=(r, g, b), width=1)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
        except ImportError:
            return b''

# Инициализация генератора
image_generator = NeuroImageGenerator(NEUROIMG_API_KEY)

async def send_daily_image(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневное изображение в группу"""
    global last_sent_time, sent_count
    
    try:
        if GROUP_CHAT_ID == "-1001234567890":
            logger.error("❌ ID группы не настроен!")
            return
        
        logger.info(f"🕒 Отправка в группу {GROUP_CHAT_ID}")
        
        # Выбираем случайный промпт
        prompt = random.choice(PROMPTS + CAT_PROMPTS)
        
        # Генерируем изображение
        image_data = await image_generator.generate_image(prompt)
        
        if image_data:
            # Отправляем в группу
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=image_data,
                caption=f"🎨 Ежедневное искусство!\n"
                       f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                       f"📝 {prompt}\n\n"
                       f"#нейросеть #искусство #ежедневно"
            )
            
            # Обновляем статистику
            last_sent_time = datetime.now()
            sent_count += 1
            
            logger.info(f"✅ Изображение отправлено в группу")
        else:
            logger.error("❌ Не удалось сгенерировать изображение")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда"""
    welcome_text = f"""
🎨 *Добро пожаловать в NeuroArt Бот!*

Использует нейросеть NeuroImg.art для генерации изображений.

*📊 Статистика:*
• Отправок: {sent_count}
• Последняя: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}
• Время отправки: {POST_TIME.strftime('%H:%M')}

*📋 Команды:*
/test - Тестовое изображение
/cat - Сгенерировать котика
/status - Статус бота
/settings - Настройки
/set_time - Изменить время отправки
/chat_id - Получить ID чата
/set_group - Установить ID группы
/daily - Принудительная отправка
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def test_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая генерация"""
    await update.message.reply_text("🎨 Генерирую тестовое изображение через NeuroImg...")
    
    prompt = random.choice(PROMPTS)
    image_data = await image_generator.generate_image(prompt)
    
    if image_data:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"🖼 NeuroImg тест\n📝 {prompt}"
        )
    else:
        await update.message.reply_text("❌ Ошибка генерации изображения")

async def generate_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация котика"""
    await update.message.reply_text("🐱 Генерирую котика через NeuroImg...")
    
    prompt = random.choice(CAT_PROMPTS)
    image_data = await image_generator.generate_image(prompt)
    
    if image_data:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"🐾 NeuroImg котик\n📝 {prompt}"
        )
    else:
        await update.message.reply_text("❌ Ошибка генерации котика")

async def force_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительная отправка"""
    try:
        if GROUP_CHAT_ID == "-1001234567890":
            await update.message.reply_text("❌ ID группы не настроен!")
            return
        
        await update.message.reply_text("🔄 Принудительная отправка...")
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
• Нейросеть: `NeuroImg.art`
• API ключ: `{'✅ Активен' if NEUROIMG_API_KEY else '❌ Не настроен'}`

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
📊 *Статус NeuroArt Бота:*

• 🟢 Онлайн и работает
• ⏰ Время отправки: {POST_TIME.strftime('%H:%M')}
• 📝 Промптов: {len(PROMPTS + CAT_PROMPTS)}
• 👥 Группа: {'✅ Настроена' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроена'}
• 🖼 Всего отправок: {sent_count}
• 🕒 Последняя отправка: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}

*🔧 Техническая информация:*
• Нейросеть: NeuroImg.art
• API: {'✅ Активен' if NEUROIMG_API_KEY else '❌ Не настроен'}
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
            
            # Тестовая задача для отладки
            job_queue.run_once(
                lambda ctx: asyncio.create_task(send_daily_image(ctx)),
                when=5,  # через 5 секунд
                name="test_job"
            )
            
            logger.info(f"✅ Задача настроена на время: {POST_TIME.strftime('%H:%M')}")
        else:
            logger.warning("⚠️ JobQueue недоступна")
            
    except Exception as e:
        logger.error(f"❌ Ошибка настройки задач: {e}")

def main():
    """Запуск бота"""
    try:
        print("🎨 Запуск NeuroArt Бота...")
        print(f"⏰ Время отправки: {POST_TIME.strftime('%H:%M')}")
        print("🤖 Нейросеть: NeuroImg.art")
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test_image))
        application.add_handler(CommandHandler("cat", generate_cat))
        application.add_handler(CommandHandler("daily", force_daily))
        application.add_handler(CommandHandler("set_time", set_post_time))
        application.add_handler(CommandHandler("settings", show_settings))
        application.add_handler(CommandHandler("chat_id", get_chat_id))
        application.add_handler(CommandHandler("set_group", set_group_id))
        application.add_handler(CommandHandler("status", bot_status))
        
        # Запускаем бота
        print("\n🤖 Бот запущен! Команды:")
        print("   /start - Главное меню")
        print("   /test - Тест NeuroImg")
        print("   /cat - Сгенерировать котика")
        print("   /set_time ЧЧ:ММ - Изменить время отправки")
        print("   /settings - Настройки")
        print("   /chat_id - Получить ID группы")
        print("   /set_group - Установить ID группы")
        print("   /daily - Принудительная отправка")
        print(f"\n⏰ Автоматическая отправка в {POST_TIME.strftime('%H:%M')}")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    # Проверяем необходимые библиотеки
    try:
        import aiohttp
        print("✅ aiohttp установлен")
    except ImportError:
        print("❌ aiohttp не установлен! pip install aiohttp")
    
    main()
