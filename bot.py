import os
import logging
import asyncio
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from aiohttp import web
import asyncio
import os
import logging

# Импортируем наши функции конвертации
from colors import *

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("❌ Не найден BOT_TOKEN в файле .env!")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временная папка для картинок
TEMP_DIR = "temp_colors"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


def create_color_preview(hex_color, filename):
    """Создает картинку с образцом цвета"""
    # Создаем изображение 300x300
    img = Image.new('RGB', (300, 300), color=hex_color)

    # Создаем кисть для рисования
    draw = ImageDraw.Draw(img)

    # Рисуем рамку
    draw.rectangle([0, 0, 299, 299], outline='black', width=2)

    # Пробуем добавить текст с HEX-кодом
    try:
        # Пытаемся загрузить шрифт (если есть)
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Добавляем белый фон для текста
    text = hex_color.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Определяем цвет текста (белый для темных цветов, черный для светлых)
    r, g, b = hex_to_rgb(hex_color)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    text_color = 'white' if brightness < 128 else 'black'

    # Рисуем полупрозрачный фон для текста
    draw.rectangle(
        [150 - text_width // 2 - 5, 150 - text_height // 2 - 5,
         150 + text_width // 2 + 5, 150 + text_height // 2 + 5],
        fill=(0, 0, 0, 128) if text_color == 'white' else (255, 255, 255, 128)
    )

    # Рисуем текст
    draw.text((150 - text_width // 2, 150 - text_height // 2), text,
              fill=text_color, font=font)

    # Сохраняем
    img.save(filename)
    return filename


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = """
🎨 Привет! Я бот-конвертер цветов!

Я помогу тебе конвертировать цвета между разными форматами:

🔹 HEX → RGB
🔹 RGB → HEX
🔹 HEX → HSL
🔹 HEX → CMYK

📝 Как пользоваться:
• Просто отправь HEX-код (например, #FF5733 или FF5733)
• Или отправь RGB (например, 255, 87, 51 или 255 87 51)

🌈 Я покажу образец цвета и все конвертации!
"""
    await message.answer(welcome_text)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🔍 Подробная инструкция:

📤 Отправь HEX-код:
• #FF5733
• FF5733
• #f5a (краткая форма)

📤 Отправь RGB:
• 255, 87, 51
• 255 87 51
• rgb(255, 87, 51)

📤 Отправь название цвета (англ.):
• red
• blue
• green

🎯 Что получу:
✅ Образец цвета
✅ HEX код
✅ RGB значения
✅ HSL значения
✅ CMYK для печати
"""
    await message.answer(help_text)


@dp.message()
async def handle_color(message: types.Message):
    """Обработчик текстовых сообщений"""
    text = message.text.strip()

    # Отправляем сообщение о начале обработки
    status_msg = await message.answer("🔄 Обрабатываю цвет...")

    try:
        rgb = None
        hex_color = None
        input_format = None

        # Проверяем, это HEX?
        if text.startswith('#') or is_valid_hex(text):
            hex_color = text if text.startswith('#') else f'#{text}'
            rgb = hex_to_rgb(hex_color)
            input_format = 'HEX'

        # Проверяем, это RGB?
        if not rgb:
            rgb = parse_rgb(text)
            if rgb:
                hex_color = rgb_to_hex(*rgb)
                input_format = 'RGB'

        # Проверяем, это название цвета на английском?
        if not rgb:
            # Словарь базовых цветов
            named_colors = {
                'red': '#FF0000',
                'green': '#00FF00',
                'blue': '#0000FF',
                'yellow': '#FFFF00',
                'cyan': '#00FFFF',
                'magenta': '#FF00FF',
                'black': '#000000',
                'white': '#FFFFFF',
                'orange': '#FFA500',
                'purple': '#800080',
                'pink': '#FFC0CB',
                'brown': '#A52A2A',
                'gray': '#808080',
                'grey': '#808080'
            }

            if text.lower() in named_colors:
                hex_color = named_colors[text.lower()]
                rgb = hex_to_rgb(hex_color)
                input_format = 'NAME'

        if rgb and hex_color:
            # Конвертируем во все форматы
            r, g, b = rgb
            hsl = rgb_to_hsl(r, g, b)
            cmyk = rgb_to_cmyk(r, g, b)

            # Создаем картинку с образцом цвета
            img_filename = os.path.join(TEMP_DIR, f"{message.from_user.id}.png")
            create_color_preview(hex_color, img_filename)

            # Формируем ответ
            response = f"""
🎨 **Результат конвертации:**

**Образец цвета:** (смотри ниже)

📌 **HEX:** `{hex_color.upper()}`
🎯 **RGB:** `{r}, {g}, {b}`
🌈 **HSL:** `{hsl[0]}°, {hsl[1]}%, {hsl[2]}%`
🖨️ **CMYK:** `{cmyk[0]}%, {cmyk[1]}%, {cmyk[2]}%, {cmyk[3]}%`

**Ближайшие цвета:**
⚫️ Черный: `rgb(0, 0, 0)`
⚪️ Белый: `rgb(255, 255, 255)`
🔴 Красный: `rgb(255, 0, 0)`
🟢 Зеленый: `rgb(0, 255, 0)`
🔵 Синий: `rgb(0, 0, 255)`

_Отправь другой HEX или RGB для новой конвертации!_
"""

            # Удаляем статус
            await status_msg.delete()

            # Отправляем картинку с цветом
            photo = FSInputFile(img_filename)
            await message.answer_photo(
                photo=photo,
                caption=response,
                parse_mode='Markdown'
            )

            # Удаляем временный файл
            os.remove(img_filename)

        else:
            await status_msg.edit_text(
                "❌ Не удалось распознать цвет.\n\n"
                "Попробуй:\n"
                "• HEX: #FF5733 или FF5733\n"
                "• RGB: 255, 87, 51 или 255 87 51\n"
                "• Или /help для помощи"
            )

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await status_msg.edit_text(
            "❌ Произошла ошибка. Проверь формат цвета и попробуй снова."
        )


# ============= НОВАЯ ЧАСТЬ: ВЕБ-СЕРВЕР ДЛЯ RENDER =============

async def health_check(request):
    """Эндпоинт для проверки здоровья (Render его пингует)"""
    return web.Response(text="OK")


async def on_startup(app):
    """Действия при запуске приложения"""
    logging.info("Бот запускается...")
    # Удаляем вебхук на всякий случай и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))
    logging.info("Polling запущен в фоне")


async def on_shutdown(app):
    """Действия при остановке приложения"""
    logging.info("Бот останавливается...")
    await bot.session.close()


def setup_app():
    """Настройка веб-приложения"""
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)  # корневой маршрут тоже
    return app


# ============= ЗАПУСК =============

if __name__ == "__main__":
    print("=" * 50)
    print("🎨 БОТ-КОНВЕРТЕР ЦВЕТОВ ЗАПУЩЕН!")
    print("=" * 50)
    print("📝 Режим: Polling + Веб-сервер для Render")

    # Получаем порт из переменной окружения (обязательно для Render)
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Веб-сервер запускается на порту: {port}")
    print("=" * 50)

    # Запускаем веб-сервер
    app = setup_app()
    web.run_app(app, host='0.0.0.0', port=port)