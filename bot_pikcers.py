import logging
import random
import asyncio
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import io

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ваш токен бота
BOT_TOKEN = "6387413984:AAGUMwJlOidPoKZ3_m1PgFYq1fB0j5yoxDM"
# ID вашей группы (ЗАМЕНИТЕ НА РЕАЛЬНЫЙ!)
GROUP_CHAT_ID = "-1001234567890"  # ЗАМЕНИТЕ ЭТОТ ID!

# Списки промптов
PROMPTS = [
    "Красивый пейзаж с горами и озером",
    "Футуристический город с неоновыми огнями",
    "Милые животные в природной среде",
    "Космическое пространство с планетами",
    "Абстрактное искусство с яркими цветами"
]

class SimpleImageGenerator:
    def __init__(self):
        self.has_pillow = self._check_pillow()
        
    def _check_pillow(self):
        """Проверяет наличие библиотеки Pillow"""
        try:
            from PIL import Image, ImageDraw
            return True
        except ImportError:
            logger.warning("Pillow не установлен. Используем простую генерацию.")
            return False
    
    async def generate_image(self, prompt: str) -> bytes:
        """Генерирует простое изображение"""
        try:
            if self.has_pillow:
                return await self._create_image_with_pillow(prompt)
            else:
                return await self._create_simple_image(prompt)
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return await self._create_simple_image(prompt)
    
    async def _create_image_with_pillow(self, prompt: str) -> bytes:
        """Создает изображение с помощью Pillow"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Создаем изображение
        img = Image.new('RGB', (512, 512), color=(
            random.randint(50, 200),
            random.randint(50, 200), 
            random.randint(50, 200)
        ))
        
        draw = ImageDraw.Draw(img)
        
        # Добавляем градиент
        for i in range(512):
            r = int(i / 512 * random.randint(0, 255))
            g = int(i / 512 * random.randint(0, 255))
            b = int(i / 512 * random.randint(0, 255))
            draw.line([(0, i), (512, i)], fill=(r, g, b), width=1)
        
        # Добавляем текст
        try:
            font = ImageFont.load_default()
            draw.text((50, 250), f"🎨 {prompt}", fill=(255, 255, 255), font=font)
            draw.text((150, 300), "Ежедневное искусство", fill=(255, 255, 255), font=font)
        except:
            pass
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    async def _create_simple_image(self, prompt: str) -> bytes:
        """Создает самое простое изображение"""
        # Для демонстрации возвращаем пустой bytes
        return b''

# Инициализация генератора
image_generator = SimpleImageGenerator()

# Переменная для отслеживания отправок
last_sent_time = None
sent_count = 0

async def send_daily_image(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневное изображение в группу"""
    global last_sent_time, sent_count
    
    try:
        # Проверяем, установлен ли ID группы
        if GROUP_CHAT_ID == "-1001234567890":
            logger.error("❌ ID группы не настроен! Используйте /chat_id в группе")
            return
        
        logger.info(f"🕒 Попытка отправки в группу {GROUP_CHAT_ID}")
        
        # Выбираем случайный промпт
        prompt = random.choice(PROMPTS)
        
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
                       f"#искусство #нейросеть #ежедневно"
            )
            
            # Обновляем статистику
            last_sent_time = datetime.now()
            sent_count += 1
            
            logger.info(f"✅ Изображение отправлено в группу {GROUP_CHAT_ID}")
            logger.info(f"📊 Всего отправлено: {sent_count}")
        else:
            logger.error("❌ Не удалось сгенерировать изображение")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке в группу: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная команда"""
    welcome_text = f"""
🎨 *Добро пожаловать в Арт-Бот!*

Я отправляю изображения в группу каждый день в 9:00.

*📊 Статистика:*
• Всего отправок: {sent_count}
• Последняя отправка: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}

*📋 Команды:*
/test - Тестовое изображение
/status - Статус бота
/chat_id - Получить ID чата
/set_group - Установить ID группы
/daily - Принудительная отправка

*⚠️ Важно:*
Убедитесь что ID группы настроен!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

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

async def force_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принудительная отправка в группу"""
    try:
        if GROUP_CHAT_ID == "-1001234567890":
            await update.message.reply_text("❌ ID группы не настроен! Используйте /chat_id в группе")
            return
        
        await update.message.reply_text("🔄 Принудительная отправка в группу...")
        await send_daily_image(context)
        await update.message.reply_text("✅ Сообщение отправлено в группу!")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

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

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота"""
    status_text = f"""
*📊 Статус бота:*

• 🟢 Онлайн и работает
• ⏰ Следующая отправка: 09:00
• 📝 Промптов: {len(PROMPTS)}
• 👥 Группа: {'✅ Настроена' if GROUP_CHAT_ID != '-1001234567890' else '❌ Не настроена'}
• 🖼 Всего отправок: {sent_count}
• 🕒 Последняя отправка: {last_sent_time.strftime('%d.%m.%Y %H:%M') if last_sent_time else 'Никогда'}

*🔧 Техническая информация:*
• Pillow: {'✅ Установлен' if image_generator.has_pillow else '❌ Не установлен'}
• ID группы: `{GROUP_CHAT_ID}`
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def simulate_daily_job(context: ContextTypes.DEFAULT_TYPE):
    """Симуляция ежедневной job для тестирования"""
    logger.info("🔧 Симуляция ежедневной отправки...")
    await send_daily_image(context)

async def post_init(application: Application):
    """Инициализация после запуска бота"""
    try:
        # Проверяем доступность JobQueue
        if hasattr(application, 'job_queue') and application.job_queue:
            job_queue = application.job_queue
            
            # Добавляем ежедневную задачу в 9:00
            job_queue.run_daily(
                send_daily_image,
                time=time(hour=9, minute=0, second=0),
                days=tuple(range(7)),
                name="daily_art_job"
            )
            
            # Добавляем тестовую задачу каждые 5 минут для отладки
            job_queue.run_repeating(
                simulate_daily_job,
                interval=300,  # 5 минут
                first=10,      # начать через 10 секунд
                name="test_job"
            )
            
            logger.info("✅ JobQueue настроена")
            logger.info("✅ Ежедневная задача на 9:00")
            logger.info("✅ Тестовая задача каждые 5 минут")
        else:
            logger.warning("⚠️ JobQueue недоступна")
            
    except Exception as e:
        logger.error(f"❌ Ошибка настройки JobQueue: {e}")

def main():
    """Запуск бота"""
    try:
        print("🎨 Запуск Арт-Бота...")
        print("⚠️  Убедитесь что установлен python-telegram-bot с JobQueue:")
        print("    pip install \"python-telegram-bot[job-queue]\"")
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test_image))
        application.add_handler(CommandHandler("daily", force_daily))
        application.add_handler(CommandHandler("chat_id", get_chat_id))
        application.add_handler(CommandHandler("set_group", set_group_id))
        application.add_handler(CommandHandler("status", bot_status))
        
        # Настраиваем JobQueue
        job_queue = application.job_queue
        if job_queue:
            print("✅ JobQueue доступна")
            
            # Основная задача в 9:00
            job_queue.run_daily(
                send_daily_image,
                time=time(hour=9, minute=0, second=0),
                days=tuple(range(7)),
                name="daily_art_job"
            )
            
            # Тестовая задача каждые 2 минуты для отладки
            job_queue.run_repeating(
                simulate_daily_job,
                interval=120,  # 2 минуты
                first=5,       # начать через 5 секунд
                name="debug_job"
            )
            
            print("✅ Задачи настроены:")
            print("   - Ежедневно в 09:00")
            print("   - Тест каждые 2 минуты")
        else:
            print("❌ JobQueue недоступна!")
            print("📦 Установите: pip install \"python-telegram-bot[job-queue]\"")
        
        # Запускаем бота
        print("\n🤖 Бот запущен! Команды:")
        print("   /start - Главное меню")
        print("   /test - Тест изображения")
        print("   /daily - Принудительная отправка")
        print("   /chat_id - Получить ID группы")
        print("   /set_group - Установить ID группы")
        print("   /status - Статус бота")
        print("\n⏰ Автоматическая отправка в 9:00 и каждые 2 мин для теста")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    # Проверяем установку библиотек
    try:
        import telegram
        print("✅ python-telegram-bot установлен")
    except ImportError:
        print("❌ python-telegram-bot не установлен!")
        print("📦 Установите: pip install python-telegram-bot")
    
    try:
        from PIL import Image
        print("✅ Pillow установлен")
    except ImportError:
        print("⚠️  Pillow не установлен. Установите: pip install pillow")
    
    main()
