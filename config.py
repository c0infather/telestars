# config.py
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Читаем токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    # Если токен не найден, вызываем исключение с понятным сообщением
    raise ValueError("Ошибка: не найден токен бота (BOT_TOKEN) в .env файле.")
    
# Читаем строку подключения к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Если URL не найден, также вызываем исключение
    raise ValueError("Ошибка: не найдена строка подключения (DATABASE_URL) в .env файле.")
