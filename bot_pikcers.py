import logging
import asyncio
import aiohttp
import random
import json
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import io
from PIL import Image, ImageDraw
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
# ID вашей группы (ЗАМЕНИТЕ НА РЕАЛЬНЫЙ! Используйте /chat_id в группе чтобы получить)
GROUP_CHAT_ID = "-1001234567890"  # ЗАМЕНИТЕ ЭТОТ ID!

# Список промптов для генерации изображений
PROMPTS = [
    "A majestic cat in the snow, photorealistic, high detail",
    "Beautiful landscape with mountains and lake, digital art",
    "Futuristic city with neon lights, cyberpunk style",
    "Cute animals in natural environment, high quality",
    "Cosmic space with planets and stars, vibrant colors",
]

# Специальные промпты для котиков
CAT_PROMPTS = [
    "Cute fluffy kitten playing with yarn, photorealistic",
    "Majestic cat sitting on a throne, royal style",
    "Sleeping cat in a cozy basket, warm lighting",
    "Cat with beautiful green eyes, detailed fur",
    "Playful kitten chasing a butterfly in garden",
]

class ImageGenerator:
    def __init__(self):
        pass
    
    async def generate_image(self, prompt: str, is_cat: bool = False) -> bytes:
        """Генерирует изображение"""
        try:
            return await self._create_cat_image(prompt) if is_cat else await self._create_fallback_image(prompt)
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return await self._create_fallback_image(prompt)
    
    async def _create_fallback_image(self, prompt: str) -> bytes:
        """Создает простое резервное изображение"""
        img = Image.new('RGB', (512, 512), color=(random.randint(0, 255), 
                                                   random.randint(0, 255), 
                                                   random.randint(0, 255)))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    async def _create_cat_image(self, prompt: str) -> bytes:
        """Создает специальное изображение с котиком"""
        try:
            img = Image.new('RGB', (512, 512), color=(random.randint(200, 255), 
                                                       random.randint(180, 220), 
                                                       random.randint(150, 200)))
            
            draw = ImageDraw.Draw(img)
            self._draw_cat(draw)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating cat image: {e}")
            return await self._create_fallback_image(prompt)
    
    def _draw_cat(self, draw: ImageDraw.Draw):
        """Рисует простого котика"""
        # Тело котика
        draw.ellipse([150, 150, 350, 350], fill=(200, 150, 100), outline=(0, 0, 0), width=3)
        # Голова
        draw.ellipse([175, 100, 325, 200], fill=(200, 150, 100), outline=(0, 0, 0), width=3)
        # Глаза
        draw.ellipse([200, 125, 225, 150], fill=(0, 0, 0))
        draw.ellipse([275, 125, 300, 150], fill=(0, 0, 0))
        # Нос
        draw.ellipse([237, 160, 263, 170], fill=(255, 150, 150))
        # Усы
        for i in range(3):
            draw.line([(225, 165), (175, 155 + i*10)], fill=(0, 0, 0), width=1)
            draw.line([(275, 165), (325, 155 + i*10)], fill=(0, 0, 0), width=1)

# Инициализация генератора
image_generator = ImageGenerator()

async def send_daily_image(context: CallbackContext):
    """Отправляет ежедневное изображение в группу"""
    try:
        # Проверяем, установлен ли ID группы
        if GROUP_CHAT_ID == "-1001234567890":
            logger.error("❌ ID группы не настроен! Используйте /chat_id в группе чтобы получить ID")
            return
        
        # Выбираем случайный промпт
        prompt = random.choice(PROMPTS)
        
        # Генерируем изображение
        logger.info(f"Генерация изображения для группы: {prompt}")
        image_data = await image_generator.generate_image(prompt)
        
        # Отправляем в группу
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=image_data,
            caption=f"🎨 Ежедневное искусство!\n"
                   f"📅 {datetime.now().strftime('%d.%m.%Y')}\n"
                   f"📝 {prompt}\n\n"
                   f"#искусство #нейросеть #ежедневно"
        )
        logger.info(f"✅ Изображение отправлено в группу {GROUP_CHAT_ID}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке в группу: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда start"""
    await update.message.reply_text(
        "🎨 Бот ежедневного искусства!\n\n"
        "Я буду отправлять каждый день в 9:00 сгенерированное изображение в группу.\n\n"
        "Команды:\n"
        "/test_image - тестовая отправка изображения с котиком 🐱\n"
        "/test_group - тест отправки в группу\n"
        "/chat_id - показать ID текущего чата\n"
        "/status - статус бота\n"
        "/set_group - установить ID группы"
    )

async def test_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая отправка изображения с котиком"""
    await update.message.reply_text("🔄 Генерирую тестовое изображение с котиком... 🐱")
    
    prompt = random.choice(CAT_PROMPTS)
    image_data = await image_generator.generate_image(prompt, is_cat=True)
    
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image_data,
        caption=f"🐱 Тестовое изображение с котиком!\n📝 {prompt}"
    )

async def test_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тест отправки в группу"""
    try:
        if GROUP_CHAT_ID == "-1001234567890":
            await update.message.reply_text("❌ ID группы не настроен! Используйте /chat_id в группе")
            return
        
        await update.message.reply_text("🔄 Тестирую отправку в группу...")
        
        prompt = "Тестовое изображение для группы"
        image_data = await image_generator.generate_image(prompt)
        
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=image_data,
            caption=f"🧪 Тестовое сообщение от бота\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        
        await update.message.reply_text("✅ Тестовое сообщение отправлено в группу!")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка отправки в группу: {e}")

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает ID текущего чата"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    chat_title = update.message.chat.title or "Личный чат"
    
    message = (
        f"📋 Информация о чате:\n"
        f"ID: `{chat_id}`\n"
        f"Тип: {chat_type}\n"
        f"Название: {chat_title}\n\n"
        f"💡 Скопируйте ID и установите в коде как GROUP_CHAT_ID"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def set_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка ID группы через команду"""
    try:
        if context.args:
            global GROUP_CHAT_ID
            GROUP_CHAT_ID = context.args[0]
            await update.message.reply_text(f"✅ ID группы установлен: {GROUP_CHAT_ID}")
        else:
            await update.message.reply_text("❌ Укажите ID группы: /set_group <group_id>")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота"""
    group_status = "✅ Настроен" if GROUP_CHAT_ID != "-1001234567890" else "❌ Не настроен"
    
    await update.message.reply_text(
        f"📊 Статус бота:\n"
        f"✅ Работает\n"
        f"⏰ Отправка в 9:00\n"
        f"👥 Группа: {group_status}\n"
        f"🎨 Промптов: {len(PROMPTS)}\n"
        f"🐱 Котиков: {len(CAT_PROMPTS)}\n"
        f"📋 ID группы: {GROUP_CHAT_ID}"
    )

def main():
    """Запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test_image", test_image))
        application.add_handler(CommandHandler("test_group", test_group))
        application.add_handler(CommandHandler("chat_id", get_chat_id))
        application.add_handler(CommandHandler("set_group", set_group_id))
        application.add_handler(CommandHandler("status", status))
        
        # Настраиваем ежедневную задачу
        job_queue = application.job_queue
        if job_queue:
            job_queue.run_daily(
                send_daily_image,
                time=time(hour=9, minute=0, second=0),
                days=tuple(range(7)),
                name="daily_art_job"
            )
            logger.info("✅ Ежедневная задача настроена на 9:00")
        else:
            logger.warning("⚠️ JobQueue недоступна")
        
        # Запускаем бота
        print("🎨 Бот ежедневного искусства запущен!")
        print("⚠️  ВАЖНО: Настройте ID группы!")
        print("📋 Используйте в группе команду /chat_id чтобы получить ID группы")
        print("💻 Затем установите GROUP_CHAT_ID в коде или используйте /set_group")
        print("🐱 Используйте /test_image для генерации котика")
        print("🧪 Используйте /test_group для теста отправки в группу")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()
