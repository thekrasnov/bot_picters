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
# ID вашей группы (ЗАМЕНИТЕ НА РЕАЛЬНЫЙ!)
GROUP_CHAT_ID = "-1001234567890"

# Списки промптов
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

ANIME_PROMPTS = [
    "Anime girl with colorful hair, detailed eyes, kawaii style",
    "Anime boy in school uniform, manga art style",
    "Anime character in fantasy world, digital painting",
    "Cute anime animal character, chibi style",
    "Anime mecha robot, detailed mechanical design",
    "Anime landscape with cherry blossoms, serene atmosphere",
    "Anime warrior with sword, action pose",
    "Anime magical girl transformation sequence",
    "Anime food illustration, delicious and cute",
    "Anime cityscape at night, neon lights"
]

# Настройки бота
BOT_SETTINGS = {
    "auto_post": True,
    "post_time": "09:00",
    "image_quality": "high",
    "theme": "random"
}

class ImageGenerator:
    def __init__(self):
        pass
    
    async def generate_image(self, prompt: str, style: str = "default") -> bytes:
        """Генерирует изображение в указанном стиле"""
        try:
            if style == "cat":
                return await self._create_cat_image(prompt)
            elif style == "anime":
                return await self._create_anime_image(prompt)
            elif style == "abstract":
                return await self._create_abstract_image(prompt)
            else:
                return await self._create_default_image(prompt)
                
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return await self._create_default_image(prompt)
    
    async def _create_default_image(self, prompt: str) -> bytes:
        """Создает стандартное изображение"""
        colors = [
            (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
            (random.randint(0, 100), random.randint(100, 200), random.randint(200, 255)),
            (random.randint(200, 255), random.randint(0, 100), random.randint(100, 200))
        ]
        
        img = Image.new('RGB', (512, 512), color=random.choice(colors))
        draw = ImageDraw.Draw(img)
        
        # Добавляем градиент
        for i in range(512):
            r = int(i / 512 * random.randint(0, 255))
            g = int(i / 512 * random.randint(0, 255))
            b = int(i / 512 * random.randint(0, 255))
            draw.line([(0, i), (512, i)], fill=(r, g, b), width=1)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    async def _create_cat_image(self, prompt: str) -> bytes:
        """Создает изображение с котиком"""
        img = Image.new('RGB', (512, 512), color=(random.randint(200, 255), 
                                                 random.randint(180, 220), 
                                                 random.randint(150, 200)))
        
        draw = ImageDraw.Draw(img)
        self._draw_cat(draw)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    async def _create_anime_image(self, prompt: str) -> bytes:
        """Создает аниме-стилизованное изображение"""
        # Яркие пастельные цвета для аниме
        colors = [
            (255, 200, 200),  # розовый
            (200, 255, 200),  # зеленый
            (200, 200, 255),  # голубой
            (255, 255, 200),  # желтый
            (255, 200, 255),  # фиолетовый
        ]
        
        img = Image.new('RGB', (512, 512), color=random.choice(colors))
        draw = ImageDraw.Draw(img)
        
        # Рисуем простой аниме-элемент (сердечки)
        for _ in range(10):
            x, y = random.randint(50, 450), random.randint(50, 450)
            size = random.randint(20, 50)
            self._draw_heart(draw, x, y, size, (255, 100, 100))
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    async def _create_abstract_image(self, prompt: str) -> bytes:
        """Создает абстрактное изображение"""
        img = Image.new('RGB', (512, 512), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Создаем абстрактные узоры
        for _ in range(50):
            x1, y1 = random.randint(0, 512), random.randint(0, 512)
            x2, y2 = random.randint(0, 512), random.randint(0, 512)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(1, 5))
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    def _draw_cat(self, draw: ImageDraw.Draw):
        """Рисует котика"""
        # Тело
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
    
    def _draw_heart(self, draw: ImageDraw.Draw, x: int, y: int, size: int, color: tuple):
        """Рисует сердечко"""
        draw.ellipse([x, y, x + size, y + size], fill=color)
        draw.ellipse([x + size, y, x + 2*size, y + size], fill=color)
        draw.polygon([(x, y + size//2), (x + size, y + 2*size), (x + 2*size, y + size//2)], fill=color)

# Инициализация генератора
image_generator = ImageGenerator()

# ========== КОМАНДЫ БОТА ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда start"""
    welcome_text = """
🎨 *Добро пожаловать в Арт-Бот!*

Я генерирую изображения и отправляю их в группу каждый день в 9:00.

*📋 Основные команды:*
/help - Показать все команды
/test - Тестовая генерация изображения
/cat - Сгенерировать котика
/anime - Аниме-стиль изображения
/abstract - Абстрактное искусство

*⚙️ Настройки:*
/settings - Настройки бота
/status - Статус и информация
/chat_id - Получить ID чата
/set_group - Установить ID группы

*🎭 Специальные команды:*
/daily - Принудительная ежедневная отправка
/theme - Выбрать тему генерации
/add_prompt - Добавить свой промпт
/list_prompts - Список промптов

Напишите /help для подробной информации!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь по командам"""
    help_text = """
*📖 Помощь по командам:*

*🎨 Генерация изображений:*
/test - Случайное изображение
/cat - Милые котики 🐱
/anime - Аниме-стиль
/abstract - Абстрактное искусство
/theme <название> - Выбрать тему

*⚙️ Управление ботом:*
/start - Главное меню
/settings - Настройки бота
/status - Статус системы
/chat_id - ID текущего чата
/set_group <id> - Установить ID группы

*📊 Информация:*
/list_prompts - Все промпты
/list_themes - Доступные темы
/stats - Статистика бота
/version - Версия бота

*🔧 Администрирование:*
/daily - Принудительная отправка
/auto_post <on/off> - Автопостинг
/add_prompt <текст> - Добавить промпт
/clear_prompts - Очистить промпты

*❓ Примеры:*
/test
/cat
/set_group -1001234567890
/add_prompt Beautiful sunset
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def test_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая генерация"""
    await update.message.reply_text("🎨 Генерирую тестовое изображение...")
    
    prompt = random.choice(PROMPTS)
    image_data = await image_generator.generate_image(prompt)
    
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image_data,
        caption=f"🖼 Тестовое изображение\n📝 *{prompt}*",
        parse_mode='Markdown'
    )

async def generate_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация котика"""
    await update.message.reply_text("🐱 Генерирую милого котика...")
    
    prompt = random.choice(CAT_PROMPTS)
    image_data = await image_generator.generate_image(prompt, "cat")
    
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image_data,
        caption=f"🐾 Мур-мяу!\n📝 *{prompt}*",
        parse_mode='Markdown'
    )

async def generate_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация в аниме-стиле"""
    await update.message.reply_text("🎎 Генерирую аниме-изображение...")
    
    prompt = random.choice(ANIME_PROMPTS)
    image_data = await image_generator.generate_image(prompt, "anime")
    
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image_data,
        caption=f"🌸 Аниме-стиль!\n📝 *{prompt}*",
        parse_mode='Markdown'
    )

async def generate_abstract(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Абстрактное искусство"""
    await update.message.reply_text("🔄 Генерирую абстрактное искусство...")
    
    prompt = "Abstract art with " + random.choice(["colorful patterns", "geometric shapes", "fluid forms"])
    image_data = await image_generator.generate_image(prompt, "abstract")
    
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=image_data,
        caption=f"🎭 Абстрактное искусство\n📝 *{prompt}*",
        parse_mode='Markdown'
    )

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройки бота"""
    settings_text = f"""
*⚙️ Настройки бота:*

• Автопостинг: `{'✅ Вкл' if BOT_SETTINGS['auto_post'] else '❌ Выкл'}`
• Время отправки: `{BOT_SETTINGS['post_time']}`
• Качество: `{BOT_SETTINGS['image_quality']}`
• Тема: `{BOT_SETTINGS['theme']}`
• ID группы: `{GROUP_CHAT_ID if GROUP_CHAT_ID != '-1001234567890' else 'Не настроен'}`

*Команды настроек:*
/auto_post <on/off> - Автопостинг
/set_time <ЧЧ:ММ> - Время отправки
/set_theme <тема> - Тема генерации
    """
    await update.message.reply_text(settings_text, parse_mode='Markdown')

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота"""
    status_text = f"""
*📊 Статус бота:*

• 🟢 Онлайн и работает
• ⏰ Следующая отправка: {BOT_SETTINGS['post_time']}
• 📝 Промптов: {len(PROMPTS)}
• 🐱 Котиков: {len(CAT_PROMPTS)}
• 🎎 Аниме: {len(ANIME_PROMPTS)}
• 👥 Группа: {'✅ Настроена' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроена'}

*🖼 Сгенерировано сегодня:* 0 изображений
*📈 Всего сгенерировано:* 0 изображений

Версия: 2.0
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получить ID чата"""
    chat_info = f"""
*📋 Информация о чате:*

• ID: `{update.message.chat_id}`
• Тип: `{update.message.chat.type}`
• Название: `{update.message.chat.title or 'Личный чат'}`

*💡 Для установки группы:*
1. Добавьте бота в группу
2. Напишите `/chat_id` в группе
3. Скопируйте ID группы
4. Используйте `/set_group <ID_группы>`
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

async def list_prompts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список промптов"""
   
