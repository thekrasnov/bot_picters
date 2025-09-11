import logging
import random
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import io
import math

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш токен бота
BOT_TOKEN = "6387413984:AAGUMwJlOidPoKZ3_m1PgFYq1fB0j5yoxDM"
# ID вашей группы (ЗАМЕНИТЕ НА РЕАЛЬНЫЙ!)
GROUP_CHAT_ID = "-1002592721236"

# Списки промптов для котиков
CAT_PROMPTS = [
    "Милый пушистый котенок играет с клубком",
    "Величественный кот на троне в королевском стиле",
    "Спящий кот в уютной корзине",
    "Кот с красивыми зелеными глазами",
    "Игривый котенок гоняется за бабочкой в саду",
    "Кот в крошечной короне в фэнтези стиле",
    "Группа котят прижимается друг к другу",
    "Кот исследует магический лес",
    "Кот с крыльями в ангельском стиле",
    "Кот в скафандре в научно-фантастической тематике"
]

class BeautifulCatGenerator:
    def __init__(self):
        self.has_pillow = self._check_pillow()
        
    def _check_pillow(self):
        """Проверяет наличие библиотеки Pillow"""
        try:
            from PIL import Image, ImageDraw
            return True
        except ImportError:
            logger.warning("Pillow не установлен. Установите: pip install pillow")
            return False
    
    async def generate_cat_image(self, prompt: str) -> bytes:
        """Генерирует красивого котика"""
        try:
            if self.has_pillow:
                return await self._create_beautiful_cat(prompt)
            else:
                return await self._create_simple_cat()
                
        except Exception as e:
            logger.error(f"Ошибка генерации котика: {e}")
            return await self._create_simple_cat()
    
    async def _create_beautiful_cat(self, prompt: str) -> bytes:
        """Создает красивого котика с помощью Pillow"""
        from PIL import Image, ImageDraw
        
        # Создаем изображение с милым фоном
        width, height = 600, 600
        
        # Милые пастельные цвета для фона
        bg_colors = [
            (255, 228, 225),  # лавандовый
            (255, 250, 205),  # лимонный
            (230, 255, 253),  # голубой
            (255, 235, 205),  # персиковый
            (230, 255, 230),  # мятный
        ]
        
        img = Image.new('RGB', (width, height), color=random.choice(bg_colors))
        draw = ImageDraw.Draw(img)
        
        # Рисуем милого котика
        self._draw_cute_cat(draw, width, height)
        
        # Добавляем декоративные элементы
        self._add_decorations(draw, width, height)
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=95)
        return img_byte_arr.getvalue()
    
    def _draw_cute_cat(self, draw: ImageDraw.Draw, width: int, height: int):
        """Рисует милого котика"""
        center_x, center_y = width // 2, height // 2
        
        # Тело котика (пушистое и круглое)
        body_color = self._get_cat_color()
        draw.ellipse([center_x - 100, center_y - 50, center_x + 100, center_y + 150], 
                    fill=body_color, outline=(100, 100, 100), width=2)
        
        # Голова
        head_color = body_color
        draw.ellipse([center_x - 80, center_y - 120, center_x + 80, center_y + 30], 
                    fill=head_color, outline=(100, 100, 100), width=2)
        
        # Уши
        ear_color = body_color
        # Левое ухо
        draw.polygon([
            (center_x - 70, center_y - 110),
            (center_x - 120, center_y - 160),
            (center_x - 50, center_y - 90)
        ], fill=ear_color, outline=(100, 100, 100), width=2)
        
        # Правое ухо
        draw.polygon([
            (center_x + 70, center_y - 110),
            (center_x + 120, center_y - 160),
            (center_x + 50, center_y - 90)
        ], fill=ear_color, outline=(100, 100, 100), width=2)
        
        # Внутренняя часть ушей
        draw.polygon([
            (center_x - 75, center_y - 105),
            (center_x - 100, center_y - 140),
            (center_x - 55, center_y - 95)
        ], fill=(255, 200, 200))
        
        draw.polygon([
            (center_x + 75, center_y - 105),
            (center_x + 100, center_y - 140),
            (center_x + 55, center_y - 95)
        ], fill=(255, 200, 200))
        
        # Глаза (большие и выразительные)
        eye_color = random.choice([(0, 191, 255), (50, 205, 50), (255, 165, 0)])  # голубые, зеленые, оранжевые
        draw.ellipse([center_x - 50, center_y - 50, center_x - 20, center_y - 20], 
                    fill=(255, 255, 255))  # белок
        draw.ellipse([center_x + 20, center_y - 50, center_x + 50, center_y - 20], 
                    fill=(255, 255, 255))  # белок
        
        draw.ellipse([center_x - 40, center_y - 40, center_x - 30, center_y - 30], 
                    fill=eye_color)  # радужка
        draw.ellipse([center_x + 30, center_y - 40, center_x + 40, center_y - 30], 
                    fill=eye_color)  # радужка
        
        draw.ellipse([center_x - 35, center_y - 35, center_x - 33, center_y - 33], 
                    fill=(0, 0, 0))  # зрачок
        draw.ellipse([center_x + 33, center_y - 35, center_x + 35, center_y - 33], 
                    fill=(0, 0, 0))  # зрачок
        
        # Носик (маленький розовый треугольник)
        draw.polygon([
            (center_x - 10, center_y - 5),
            (center_x + 10, center_y - 5),
            (center_x, center_y + 5)
        ], fill=(255, 150, 150))
        
        # Ротик (улыбка)
        draw.arc([center_x - 15, center_y + 5, center_x + 15, center_y + 15], 
                180, 0, fill=(0, 0, 0), width=2)
        
        # Усы
        for i in range(3):
            # Левые усы
            draw.line([(center_x - 20, center_y), (center_x - 60, center_y - 20 + i*10)], 
                     fill=(100, 100, 100), width=1)
            draw.line([(center_x - 20, center_y + 5), (center_x - 60, center_y + i*10)], 
                     fill=(100, 100, 100), width=1)
            # Правые усы
            draw.line([(center_x + 20, center_y), (center_x + 60, center_y - 20 + i*10)], 
                     fill=(100, 100, 100), width=1)
            draw.line([(center_x + 20, center_y + 5), (center_x + 60, center_y + i*10)], 
                     fill=(100, 100, 100), width=1)
        
        # Лапки
        paw_color = body_color
        draw.ellipse([center_x - 70, center_y + 120, center_x - 40, center_y + 140], 
                    fill=paw_color, outline=(100, 100, 100), width=2)
        draw.ellipse([center_x + 40, center_y + 120, center_x + 70, center_y + 140], 
                    fill=paw_color, outline=(100, 100, 100), width=2)
    
    def _get_cat_color(self):
        """Возвращает милый цвет для котика"""
        colors = [
            (200, 170, 150),  # бежевый
            (180, 160, 140),  # серо-бежевый
            (220, 180, 160),  # персиковый
            (170, 150, 130),  # коричневатый
            (190, 170, 150),  # кремовый
        ]
        return random.choice(colors)
    
    def _add_decorations(self, draw: ImageDraw.Draw, width: int, height: int):
        """Добавляет декоративные элементы"""
        # Сердечки вокруг котика
        for _ in range(8):
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            size = random.randint(10, 20)
            self._draw_heart(draw, x, y, size, (255, 150, 150))
        
        # Звездочки
        for _ in range(5):
            x = random.randint(30, width - 30)
            y = random.randint(30, height - 30)
            self._draw_star(draw, x, y, 8, (255, 255, 100))
    
    def _draw_heart(self, draw: ImageDraw.Draw, x: int, y: int, size: int, color: tuple):
        """Рисует сердечко"""
        # Левая половина сердца
        draw.ellipse([x, y, x + size, y + size], fill=color)
        # Правая половина сердца
        draw.ellipse([x + size, y, x + 2*size, y + size], fill=color)
        # Нижняя часть сердца
        draw.polygon([
            (x, y + size//2),
            (x + size, y + 2*size),
            (x + 2*size, y + size//2)
        ], fill=color)
    
    def _draw_star(self, draw: ImageDraw.Draw, x: int, y: int, size: int, color: tuple):
        """Рисует звездочку"""
        points = []
        for i in range(5):
            # Внешние точки
            angle = math.pi/2 + i * 2*math.pi/5
            points.append((x + size * math.cos(angle), y + size * math.sin(angle)))
            # Внутренние точки
            angle += math.pi/5
            points.append((x + size/2 * math.cos(angle), y + size/2 * math.sin(angle)))
        
        draw.polygon(points, fill=color)
    
    async def _create_simple_cat(self) -> bytes:
        """Простая заглушка если Pillow не установлен"""
        # Можно вернуть пустое изображение или сообщение об ошибке
        return b''

# Инициализация генератора
cat_generator = BeautifulCatGenerator()

# ========== КОМАНДЫ БОТА ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда"""
    welcome_text = """
🐱 *Добро пожаловать в Бот Красивых Котиков!*

Я создаю милых и красивых котиков!

✨ *Команды:*
/cat - Сгенерировать котика
/cute - Милый котик
/fluffy - Пушистый котик
/sleepy - Сонный котик
/playful - Игривый котик

🎨 *Дополнительно:*
/status - Статус бота
/help - Помощь по командам

Просто напишите /cat чтобы получить котика!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def generate_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация котика"""
    await update.message.reply_text("🐱 Генерирую красивого котика...")
    
    prompt = random.choice(CAT_PROMPTS)
    image_data = await cat_generator.generate_cat_image(prompt)
    
    if image_data:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"✨ {prompt}\n\n#кот #котик #милота 🐾"
        )
    else:
        await update.message.reply_text(
            "❌ Не удалось сгенерировать котика.\n"
            "📦 Установите Pillow: pip install pillow"
        )

async def generate_cute_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Милый котик"""
    await update.message.reply_text("💖 Генерирую особенно милого котика...")
    await generate_cat(update, context)

async def generate_fluffy_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пушистый котик"""
    await update.message.reply_text("🦁 Генерирую пушистого котика...")
    await generate_cat(update, context)

async def generate_sleepy_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сонный котик"""
    await update.message.reply_text("😴 Генерирую сонного котика...")
    await generate_cat(update, context)

async def generate_playful_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Игривый котик"""
    await update.message.reply_text("🎾 Генерирую игривого котика...")
    await generate_cat(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь по командам"""
    help_text = """
🐾 *Помощь по командам котиков:*

/cat - Случайный котик
/cute - Особенно милый котик
/fluffy - Пушистый котик
/sleepy - Сонный котик
/playful - Игривый котик

📊 *Информация:*
/status - Статус бота
/start - Главное меню

💡 *Для лучшего качества:*
Установите Pillow: pip install pillow
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота"""
    status_text = f"""
📊 *Статус Бота Котиков:*

• 🟢 Онлайн и работает
• 🐱 Сгенерировано котиков: 0
• 🎨 Pillow: {'✅ Установлен' if cat_generator.has_pillow else '❌ Не установлен'}
• 💫 Режим: Красивые котики

✨ *Особенности:*
- Большие выразительные глаза
- Пушистая шерстка
- Милые позы
- Декоративные элементы
- Пастельные цвета

Версия: 2.0 🐾
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

# ========== ЗАПУСК БОТА ==========

def main():
    """Запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("cat", generate_cat))
        application.add_handler(CommandHandler("cute", generate_cute_cat))
        application.add_handler(CommandHandler("fluffy", generate_fluffy_cat))
        application.add_handler(CommandHandler("sleepy", generate_sleepy_cat))
        application.add_handler(CommandHandler("playful", generate_playful_cat))
        application.add_handler(CommandHandler("status", bot_status))
        
        # Запускаем бота
        print("🐱 Бот Красивых Котиков запущен!")
        print("✨ Команды:")
        print("   /cat - Сгенерировать котика")
        print("   /cute -
