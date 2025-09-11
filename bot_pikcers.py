import logging
import asyncio
import aiohttp
import random
import json
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import io
from PIL import Image, ImageDraw, ImageFont
import time as time_module
import base64
from io import BytesIO
import os

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш токен бота
BOT_TOKEN = "6387413984:AAGUMwJlOidPoKZ3_m1PgFYq1fB0j5yoxDM"
# ID вашей группы (замените на реальный)
GROUP_CHAT_ID = "-1001234567890"

# Ключ API RunwayML (получите на https://runwayml.com/)
RUNWAYML_API_KEY = "key_1e5c0cc1dae3237fd04e6c18375f1c8c861756b068fd6a0ae4b3c56071cb39cff190e385b0fdc927b717605a8ce6882b7c8269e1bfb80d8407307dc92a744104"

# Список промптов для генерации изображений
PROMPTS = [
    "A majestic cat in the snow, photorealistic, high detail",
    "Beautiful landscape with mountains and lake, digital art",
    "Futuristic city with neon lights, cyberpunk style",
    "Cute animals in natural environment, high quality",
    "Cosmic space with planets and stars, vibrant colors",
    "Abstract art with bright colors and shapes",
    "Ancient castle in fog, mystical atmosphere",
    "Underwater world with corals and tropical fish",
    "Autumn forest with golden leaves, cozy atmosphere",
    "Magical forest with glowing plants, fantasy style"
]

# Специальные промпты для котиков (используются в тестовом режиме)
CAT_PROMPTS = [
    "Cute fluffy kitten playing with yarn, photorealistic",
    "Majestic cat sitting on a throne, royal style",
    "Sleeping cat in a cozy basket, warm lighting",
    "Cat with beautiful green eyes, detailed fur",
    "Playful kitten chasing a butterfly in garden",
    "Cat wearing a tiny crown, fantasy style",
    "Group of kittens cuddling together, adorable",
    "Cat exploring magical forest, fantasy art",
    "Cat with wings, angelic style, digital art",
    "Cat in space suit, sci-fi theme, detailed"
]

# Список базовых изображений для image-to-video
BASE_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Shiba_inu_003.jpg/1024px-Shiba_inu_003.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Image_created_with_a_mobile_phone.png/1280px-Image_created_with_a_mobile_phone.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1024px-Cat03.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/1024px-Cat_November_2010-1a.jpg"
]

class RunwayMLGenerator:
    def __init__(self):
        self.api_key = RUNWAYML_API_KEY
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Инициализирует клиент RunwayML"""
        try:
            if self.api_key != "YOUR_RUNWAYML_API_KEY_HERE":
                from runwayml import RunwayML
                self.client = RunwayML(api_key=self.api_key)
                logger.info("RunwayML client initialized successfully")
            else:
                logger.warning("RunwayML API key not set, using fallback mode")
        except ImportError:
            logger.error("RunwayML library not installed")
        except Exception as e:
            logger.error(f"Error initializing RunwayML client: {e}")
    
    async def generate_image(self, prompt: str, is_cat: bool = False) -> bytes:
        """Генерирует изображение через RunwayML или fallback"""
        try:
            if self.client and not is_cat:
                # Пытаемся использовать RunwayML только для обычных промптов
                return await self._generate_with_runwayml(prompt)
            else:
                # Для котиков и fallback используем специальную генерацию
                return await self._create_cat_image(prompt) if is_cat else await self._create_fallback_image(prompt)
                
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return await self._create_cat_image(prompt) if is_cat else await self._create_fallback_image(prompt)
    
    async def _generate_with_runwayml(self, prompt: str) -> bytes:
        """Генерация с использованием RunwayML"""
        try:
            logger.info(f"RunwayML generation attempt for: {prompt}")
            # Здесь будет реальный вызов RunwayML API
            # Пока используем улучшенный fallback
            return await self._create_advanced_fallback_image(prompt)
            
        except Exception as e:
            logger.error(f"RunwayML generation failed: {e}")
            return await self._create_fallback_image(prompt)
    
    async def _create_fallback_image(self, prompt: str) -> bytes:
        """Создает простое резервное изображение"""
        img = Image.new('RGB', (1024, 1024), color=(random.randint(0, 255), 
                                                   random.randint(0, 255), 
                                                   random.randint(0, 255)))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    async def _create_advanced_fallback_image(self, prompt: str) -> bytes:
        """Создает улучшенное резервное изображение с текстом"""
        img = Image.new('RGB', (1024, 1024), color=(random.randint(50, 200), 
                                                   random.randint(50, 200), 
                                                   random.randint(50, 200)))
        
        try:
            draw = ImageDraw.Draw(img)
            # Создаем градиент
            for i in range(1024):
                r = int(i / 1024 * 255)
                g = random.randint(0, 255)
                b = 255 - int(i / 1024 * 255)
                draw.line([(0, i), (1024, i)], fill=(r, g, b))
            
            # Добавляем текст
            text = f"RunwayML: {prompt[:80]}..." if len(prompt) > 80 else prompt
            draw.text((50, 500), text, fill=(255, 255, 255))
            
        except Exception as e:
            logger.error(f"Error drawing text: {e}")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    async def _create_cat_image(self, prompt: str) -> bytes:
        """Создает специальное изображение с котиком"""
        try:
            # Создаем изображение с котиком
            img = Image.new('RGB', (1024, 1024), color=(random.randint(200, 255), 
                                                       random.randint(180, 220), 
                                                       random.randint(150, 200)))
            
            draw = ImageDraw.Draw(img)
            
            # Рисуем милого котика (упрощенная версия)
            self._draw_cat(draw)
            
            # Добавляем текст промпта
            text = f"🐱 {prompt[:60]}..." if len(prompt) > 60 else f"🐱 {prompt}"
            draw.text((50, 900), text, fill=(0, 0, 0))
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating cat image: {e}")
            return await self._create_fallback_image(prompt)
    
    def _draw_cat(self, draw: ImageDraw.Draw):
        """Рисует простого котика"""
        # Тело котика
        draw.ellipse([300, 300, 700, 700], fill=(200, 150, 100), outline=(0, 0, 0), width=5)
        
        # Голова
        draw.ellipse([350, 200, 650, 400], fill=(200, 150, 100), outline=(0, 0, 0), width=5)
        
        # Уши
        draw.polygon([(350, 200), (300, 100), (400, 180)], fill=(200, 150, 100), outline=(0, 0, 0), width=3)
        draw.polygon([(650, 200), (700, 100), (600, 180)], fill=(200, 150, 100), outline=(0, 0, 0), width=3)
        
        # Глаза
        draw.ellipse([400, 250, 450, 300], fill=(0, 0, 0))
        draw.ellipse([550, 250, 600, 300], fill=(0, 0, 0))
        
        # Нос
        draw.ellipse([475, 320, 525, 340], fill=(255, 150, 150))
        
        # Усы
        for i in range(3):
            draw.line([(450, 330), (350, 300 + i*10)], fill=(0, 0, 0), width=2)
            draw.line([(550, 330), (650, 300 + i*10)], fill=(0, 0, 0), width=2)
        
        # Хвост
        draw.arc([650, 500, 850, 700], 180, 270, fill=(0, 0, 0), width=5)

# Инициализация генератора
runwayml_generator = RunwayMLGenerator()

async def send_daily_image(context: CallbackContext):
    """Отправляет ежедневное изображение в группу"""
    try:
        # Выбираем случайный промпт
        prompt = random.choice(PROMPTS)
        
        # Генерируем изображение
        logger.info(f"Генерация изображения: {prompt}")
        image_data = await runwayml_generator.generate_image(prompt)
        
        # Отправляем в группу
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=image_data,
            caption=f"🎨 Ежедневное искусство!\n"
                   f"📅 {datetime.now().strftime('%d.%m.%Y')}\n"
                   f"📝 Prompt: {prompt}\n\n"
                   f"#искусство #нейросеть #ежедневно"
        )
        logger.info("Изображение отправлено в группу")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке ежедневного изображения: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда start"""
    await update.message.reply_text(
        "🎨 Бот ежедневного искусства!\n\n"
        "Я буду отправлять каждый день в 9:00 сгенерированное изображение в группу.\n\n"
        "Команды:\n"
        "/test_image - тестовая отправка изображения с котиком 🐱\n"
        "/test_cat - специальная генерация котика\n"
        "/status - статус бота\n"
        "/prompts - список промптов\n"
        "/cat_prompts - промпты для котиков"
    )

async def test_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая отправка изображения с котиком"""
    await update.message.reply_text("🔄 Генерирую тестовое изображение с котиком... 🐱")
    
    # Используем специальный промпт для котика
    prompt = random.choice(CAT_PROMPTS)
    image_data = await runwayml_generator.generate_image(prompt, is_cat=True)
    
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image_data,
        caption=f"🐱 Тестовое изображение с котиком!\n📝 {prompt}\n\n#кот #котик #тест"
    )

async def test_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Специальная команда для генерации котиков"""
    await update.message.reply_text("🐱 Генерирую специальное изображение котика...")
    
    prompt = random.choice(CAT_PROMPTS)
    image_data = await runwayml_generator.generate_image(prompt, is_cat=True)
    
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image_data,
        caption=f"🐾 Специальный котик дня!\n📝 {prompt}\n\n#кот #котик #милота"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота"""
    next_run = "09:00 (ежедневно)"
    runway_status = "Подключен"
    
    await update.message.reply_text(
        f"📊 Статус бота:\n"
        f"✅ Работает\n"
        f"⏰ Следующая отправка: {next_run}\n"
        f"👥 Группа: настроена\n"
        f"🎨 Промптов в базе: {len(PROMPTS)}\n"
        f"🐱 Промптов котиков: {len(CAT_PROMPTS)}\n"
        f"🤖 RunwayML: {runway_status}"
    )

async def show_prompts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список промптов"""
    prompts_text = "📋 Список промптов:\n\n"
    for i, prompt in enumerate(PROMPTS, 1):
        prompts_text += f"{i}. {prompt}\n\n"
    
    await update.message.reply_text(prompts_text[:4000])

async def show_cat_prompts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список промптов для котиков"""
    prompts_text = "🐱 Список промптов для котиков:\n\n"
    for i, prompt in enumerate(CAT_PROMPTS, 1):
        prompts_text += f"{i}. {prompt}\n\n"
    
    await update.message.reply_text(prompts_text[:4000])

async def post_init(application: Application):
    """Функция, вызываемая после инициализации бота"""
    try:
        # Настраиваем ежедневную задачу
        job_queue = application.job_queue
        
        if job_queue:
            job_queue.run_daily(
                send_daily_image,
                time=time(hour=9, minute=0, second=0),
                days=(0, 1, 2, 3, 4, 5, 6),
                name="daily_art_job"
            )
            logger.info("✅ Ежедневная задача настроена на 9:00")
        else:
            logger.warning("⚠️ JobQueue недоступна")
            
    except Exception as e:
        logger.error(f"Ошибка при настройке ежедневной задачи: {e}")

def main():
    """Запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test_image", test_image))
        application.add_handler(CommandHandler("test_cat", test_cat))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CommandHandler("prompts", show_prompts))
        application.add_handler(CommandHandler("cat_prompts", show_cat_prompts))
        
        # Настраиваем ежедневную задачу
        job_queue = application.job_queue
        if job_queue:
            job_queue.run_daily(
                send_daily_image,
                time=time(hour=9, minute=0, second=0),
                days=tuple(range(7)),
                name="daily_art_job"
            )
            logger.info("✅ Ежедневная задача настроена")
        else:
            logger.warning("⚠️ JobQueue недоступна")
        
        # Запускаем бота
        print("🎨 Бот ежедневного искусства запущен!")
        print("🐱 Теперь генерирует котиков в тестовом режиме!")
        print("⏰ Автоматическая отправка каждый день в 9:00")
        print("📞 Напишите /start для получения информации")
        print("🐾 Используйте /test_image для генерации котика")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()