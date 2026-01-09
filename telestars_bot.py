import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from config import BOT_TOKEN
from database import init_db, add_user

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


def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Добавляем пользователя в базу данных
    try:
        is_new_user = add_user(user)
        if is_new_user:
            logger.info(f"Новый пользователь зарегистрирован: {user.id} (@{user.username or 'без username'})")
        else:
            logger.info(f"Пользователь обновлен: {user.id} (@{user.username or 'без username'})")
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя в БД: {e}")
    
    welcome_message = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Добро пожаловать в бот для покупки звезд Telegram! ⭐\n\n"
        "Выберите действие из меню ниже:"
    )
    update.message.reply_text(
        welcome_message,
        reply_markup=get_reply_keyboard()
    )


def handle_buy_stars(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки '⭐ Купить звезды'"""
    message = (
        "⭐ Купить звезды\n\n"
        "Здесь будет функционал для покупки звезд Telegram.\n"
        "Функция в разработке..."
    )
    update.message.reply_text(message)


def handle_buy_premium(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки '💎 Купить Premium'"""
    message = (
        "💎 Купить Premium\n\n"
        "Здесь будет функционал для покупки Telegram Premium.\n"
        "Функция в разработке..."
    )
    update.message.reply_text(message)


def handle_profile(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки '👤 Профиль'"""
    user = update.effective_user
    message = (
        f"👤 Профиль\n\n"
        f"ID: {user.id}\n"
        f"Имя: {user.first_name or 'Не указано'}\n"
        f"Username: @{user.username if user.username else 'не указан'}\n\n"
        "Здесь будет отображаться статистика и баланс."
    )
    update.message.reply_text(message)


def handle_support(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки '🆘 Поддержка'"""
    message = (
        "🆘 Поддержка\n\n"
        "Если у вас возникли вопросы или проблемы, "
        "свяжитесь с нашей службой поддержки.\n\n"
        "Функция в разработке..."
    )
    update.message.reply_text(message)


def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    if text == "⭐ Купить звезды":
        handle_buy_stars(update, context)
    elif text == "💎 Купить Premium":
        handle_buy_premium(update, context)
    elif text == "👤 Профиль":
        handle_profile(update, context)
    elif text == "🆘 Поддержка":
        handle_support(update, context)
    else:
        # Неизвестное сообщение
        update.message.reply_text(
            "Пожалуйста, используйте кнопки меню для навигации.",
            reply_markup=get_reply_keyboard()
        )


def main() -> None:
    """Запуск бота"""
    # Инициализируем базу данных
    try:
        logger.info("Инициализация базы данных...")
        init_db()
        logger.info("База данных готова")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        logger.warning("Бот будет запущен без базы данных")
    
    # Создаем Updater и передаем ему токен бота
    updater = Updater(token=BOT_TOKEN, use_context=True)
    
    # Получаем dispatcher для регистрации обработчиков
    dispatcher = updater.dispatcher
    
    # Регистрируем обработчики
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    updater.start_polling()
    
    # Запускаем бота до тех пор, пока не будет нажато Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
