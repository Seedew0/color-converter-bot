# Цвет-конвертер-бот

Telegram-бот на Python для конвертации цветов между популярными форматами.

Бот принимает HEX-код или RGB-значение, показывает образец цвета и выводит значения в других форматах.

## Возможности

- HEX → RGB
- RGB → HEX
- HEX → HSL
- HEX → CMYK
- Генерация изображения с образцом цвета
- Команды `/start` и `/help`

Примеры ввода:

- `#FF5733`
- `FF5733`
- `#f5a`
- `255, 87, 51`
- `255 87 51`
- `rgb(255, 87, 51)`

## Технологии

- Python
- aiogram
- Pillow
- aiohttp
- Docker

## Запуск локально

1. Склонируй репозиторий:

   ```bash
   git clone https://github.com/Seedew0/color-converter-bot.git
   cd color-converter-bot
