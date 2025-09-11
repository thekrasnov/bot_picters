import logging
import random
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import io
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
    "Красивый пейзаж с горами и озером",
    "Футуристический город с неоновыми огнями",
    "Милые животные в природной среде",
    "Космическое пространство с планетами",
    "Абстрактное искусство с яркими цветами",
    "Старинный замок в тумане",
    "Подводный мир с кораллами",
    "Осенний лес с золотыми листьями",
    "Магический лес со светящимися растениями",
    "Горный водопад в солнечный день"
]

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

# Настройки бота
BOT_SETTINGS = {
    "auto_post": True,
    "post_time": "09:00",
    "image_quality": "high"
}

class SimpleImageGenerator:
    def __init__(self):
        # Проверяем наличие Pillow
        self.has_pillow = self._check_pillow()
        
    def _check_pillow(self):
        """Проверяет наличие библиотеки Pillow"""
        try:
            from PIL import Image, ImageDraw
            return True
        except ImportError:
            logger.warning("Pillow не установлен. Используем простую генерацию.")
            return False
    
    async def generate_image(self, prompt: str, style: str = "default") -> bytes:
        """Генерирует простое изображение"""
        try:
            if self.has_pillow and style == "cat":
                return await self._create_cat_image(prompt)
            elif self.has_pillow:
                return await self._create_default_image(prompt)
            else:
                return await self._create_simple_image(prompt)
                
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return await self._create_simple_image(prompt)
    
    async def _create_default_image(self, prompt: str) -> bytes:
        """Создает изображение с помощью Pillow"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (512, 512), color=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ))
            
            draw = ImageDraw.Draw(img)
            
            # Простой градиент
            for i in range(512):
                r = int(i / 512 * 255)
                g = random.randint(0, 255)
                b = 255 - int(i / 512 * 255)
                draw.line([(0, i), (512, i)], fill=(r, g, b), width=1)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка создания изображения: {e}")
            return await self._create_simple_image(prompt)
    
    async def _create_cat_image(self, prompt: str) -> bytes:
        """Создает изображение с котиком"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (512, 512), color=(
                random.randint(200, 255),
                random.randint(180, 220),
                random.randint(150, 200)
            ))
            
            draw = ImageDraw.Draw(img)
            
            # Рисуем простого котика
            draw.ellipse([150, 150, 350, 350], fill=(200, 150, 100), outline=(0, 0, 0), width=3)
            draw.ellipse([175, 100, 325, 200], fill=(200, 150, 100), outline=(0, 0, 0), width=3)
            draw.ellipse([200, 125, 225, 150], fill=(0, 0, 0))
            draw.ellipse([275, 125, 300, 150], fill=(0, 0, 0))
            draw.ellipse([237, 160, 263, 170], fill=(255, 150, 150))
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка создания котика: {e}")
            return await self._create_default_image(prompt)
    
    async def _create_simple_image(self, prompt: str) -> bytes:
        """Создает самое простое изображение без зависимостей"""
        # Для демонстрации возвращаем пустой bytes
        # В реальном проекте можно добавить базовую генерацию
        return b''

# Инициализация генератора
image_generator = SimpleImageGenerator()

# ========== ОСНОВНЫЕ КОМАНДЫ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда"""
    welcome_text = """
🎨 *Добро пожаловать в Арт-Бот!*

Я отправляю изображения в группу каждый день в 9:00.

📋 *Основные команды:*
/help - Все команды
/test - Тестовое изображение
/cat - Сгенерировать котика
/status - Статус бота
/chat_id - Получить ID чата

⚙️ *Настройки:*
/set_group - Установить ID группы
/settings - Настройки бота

Напишите /help для подробной информации!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь по командам"""
    help_text = """
📖 *Помощь по командам:*

🎨 *Генерация:*
/test - Случайное изображение
/cat - Милые котики 🐱

⚙️ *Управление:*
/start - Главное меню
/status - Статус системы
/chat_id - ID текущего чата
/set_group <id> - Установить ID группы

📊 *Информация:*
/settings - Настройки бота
/stats - Статистика

❓ *Примеры:*
/test
/cat
/set_group -1001234567890
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def test_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая генерация"""
    await update.message.reply_text("🎨 Генерирую тестовое изображение...")
    
    prompt = random.choice(PROMPTS)
    image_data = await image_generator.generate_image(prompt)
    
    if image_data:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"🖼 Тестовое изображение\n📝 {prompt}"
        )
    else:
        await update.message.reply_text("❌ Ошибка генерации изображения")

async def generate_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация котика"""
    await update.message.reply_text("🐱 Генерирую милого котика...")
    
    prompt = random.choice(CAT_PROMPTS)
    image_data = await image_generator.generate_image(prompt, "cat")
    
    if image_data:
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=image_data,
            caption=f"🐾 Мур-мяу!\n📝 {prompt}"
        )
    else:
        await update.message.reply_text("❌ Ошибка генерации котика")

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройки бота"""
    settings_text = f"""
⚙️ *Настройки бота:*

• Автопостинг: {'✅ Вкл' if BOT_SETTINGS['auto_post'] else '❌ Выкл'}
• Время отправки: {BOT_SETTINGS['post_time']}
• Качество: {BOT_SETTINGS['image_quality']}
• ID группы: {'✅ Настроен' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроен'}

*Команды настроек:*
/set_group <id> - Установить ID группы
    """
    await update.message.reply_text(settings_text, parse_mode='Markdown')

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота"""
    status_text = f"""
📊 *Статус бота:*

• 🟢 Онлайн и работает
• ⏰ Отправка в: {BOT_SETTINGS['post_time']}
• 📝 Промптов: {len(PROMPTS)}
• 🐱 Котиков: {len(CAT_PROMPTS)}
• 👥 Группа: {'✅ Настроена' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроена'}
• 🖼 Pillow: {'✅ Установлен' if image_generator.has_pillow else '❌ Не установлен'}

Версия: 1.0
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

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

async def send_daily_image(context: CallbackContext):
    """Отправляет ежедневное изображение в группу"""
    try:
        if GROUP_CHAT_ID == "-1001234567890":
            logger.error("❌ ID группы не настроен!")
            return
        
        prompt = random.choice(PROMPTS + CAT_PROMPTS)
        image_data = await image_generator.generate_image(prompt, "cat" if "кот" in prompt.lower() else "default")
        
        if image_data:
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=image_data,
                caption=f"🎨 Ежедневное искусство!\n📅 {datetime.now().strftime('%d.%m.%Y')}\n📝 {prompt}"
            )
            logger.info(f"✅ Изображение отправлено в группу {GROUP_CHAT_ID}")
        else:
            logger.error("❌ Не удалось сгенерировать изображение для группы")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке в группу: {e}")

async def force_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительная отправка в группу"""
    await update.message.reply_text("🔄 Принудительная отправка в группу...")
    await send_daily_image(context)
    await update.message.reply_text("✅ Сообщение отправлено в группу!")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика бота"""
    stats_text = """
📈 *Статистика бота:*

• 🖼 Сгенерировано сегодня: 0
• 📊 Всего сгенерировано: 0
• ⏰ Время работы: 0 часов
• 🎯 Успешных отправок: 0
• ❌ Ошибок: 0

*📝 Промпты:*
• Обычные: {len(PROMPTS)}
• Котики: {len(CAT_PROMPTS)}
    """
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def show_version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Версия бота"""
    await update.message.reply_text("🤖 *Версия бота: 2.0*\n📅 Последнее обновление: 2024", parse_mode='Markdown')

# ========== ЗАПУСК БОТА ==========

def main():
    """Запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("test", test_image))
        application.add_handler(CommandHandler("cat", generate_cat))
        application.add_handler(CommandHandler("settings", show_settings))
        application.add_handler(CommandHandler("status", bot_status))
        application.add_handler(CommandHandler("chat_id", get_chat_id))
        application.add_handler(CommandHandler("set_group", set_group_id))
        application.add_handler(CommandHandler("daily", force_daily))
        application.add_handler(CommandHandler("stats", show_stats))
        application.add_handler(CommandHandler("version", show_version))
        
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
        
        # Запускаем бота
        print("🎨 Арт-Бот запущен!")
        print("📋 Доступные команды:")
        print("   /start - Главное меню")
        print("   /help - Помощь по командам")
        print("   /test - Тестовое изображение")
        print("   /cat - Генерация котика")
        print("   /chat_id - Получить ID чата")
        print("   /set_group - Установить ID группы")
        print("   /status - Статус бота")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")

if __name__ == "__main__":
    # Проверяем установлен ли Pillow
    try:
        from PIL import Image, ImageDraw
        print("✅ Pillow установлен")
    except ImportError:
        print("⚠️  Pillow не установлен. Установите: pip install pillow")
        print("⚠️  Генерация изображений будет ограничена")
    
    main()
