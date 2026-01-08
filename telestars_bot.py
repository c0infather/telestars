import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_reply_keyboard():
    """Создает reply keyboard с основными кнопками"""
    keyboard = [
        ['⭐ Купить звезды', '💎 Купить Premium'],
        ['👤 Профиль', '🆘 Поддержка']
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    welcome_message = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Добро пожаловать в бот для покупки звезд Telegram! ⭐\n\n"
        "Выберите действие из меню ниже:"
    )
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_reply_keyboard()
    )


async def handle_buy_stars(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки '⭐ Купить звезды'"""
    message = (
        "⭐ Купить звезды\n\n"
        "Здесь будет функционал для покупки звезд Telegram.\n"
        "Функция в разработке..."
    )
    await update.message.reply_text(message)


async def handle_buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки '💎 Купить Premium'"""
    message = (
        "💎 Купить Premium\n\n"
        "Здесь будет функционал для покупки Telegram Premium.\n"
        "Функция в разработке..."
    )
    await update.message.reply_text(message)


async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки '👤 Профиль'"""
    user = update.effective_user
    message = (
        f"👤 Профиль\n\n"
        f"ID: {user.id}\n"
        f"Имя: {user.first_name or 'Не указано'}\n"
        f"Username: @{user.username if user.username else 'не указан'}\n\n"
        "Здесь будет отображаться статистика и баланс."
    )
    await update.message.reply_text(message)


async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик кнопки '🆘 Поддержка'"""
    message = (
        "🆘 Поддержка\n\n"
        "Если у вас возникли вопросы или проблемы, "
        "свяжитесь с нашей службой поддержки.\n\n"
        "Функция в разработке..."
    )
    await update.message.reply_text(message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if text == "⭐ Купить звезды":
        await handle_buy_stars(update, context)
    elif text == "💎 Купить Premium":
        await handle_buy_premium(update, context)
    elif text == "👤 Профиль":
        await handle_profile(update, context)
    elif text == "🆘 Поддержка":
        await handle_support(update, context)
    else:
        # Неизвестное сообщение
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню для навигации.",
            reply_markup=get_reply_keyboard()
        )


def main() -> None:
    """Запуск бота"""
    # Создаем приложение с токеном из конфигурации
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
