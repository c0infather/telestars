import logging
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
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


def get_stars_selection_keyboard():
    """Создает inline keyboard для выбора количества звезд"""
    keyboard = [
        [
            InlineKeyboardButton("⭐ 50", callback_data="stars_50"),
            InlineKeyboardButton("⭐ 100", callback_data="stars_100")
        ],
        [
            InlineKeyboardButton("⭐ 200", callback_data="stars_200"),
            InlineKeyboardButton("⭐ 500", callback_data="stars_500")
        ],
        [
            InlineKeyboardButton("⭐ 1000", callback_data="stars_1000"),
            InlineKeyboardButton("⭐ 5000", callback_data="stars_5000")
        ],
        [
            InlineKeyboardButton("🎁 В подарок", callback_data="stars_gift")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_purchase_keyboard():
    """Создает reply keyboard после выбора количества звезд"""
    keyboard = [
        ['🎁 В подарок'],
        ['🔙 Назад']
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
    # Сбрасываем состояние покупки
    context.user_data.pop('buying_stars', None)
    context.user_data.pop('stars_amount', None)
    
    message = (
        "⭐ Покупка звёзд\n\n"
        "Выберите количество звёзд ниже\n"
        "или введите число от 50 до 10 000\n\n"
        "Хотите отправить звёзды другу?\n"
        "Нажмите «🎁 В подарок»"
    )
    update.message.reply_text(
        message,
        reply_markup=get_stars_selection_keyboard()
    )


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


def handle_callback_query(update: Update, context: CallbackContext) -> None:
    """Обработчик inline кнопок"""
    query = update.callback_query
    query.answer()
    
    callback_data = query.data
    
    if callback_data.startswith("stars_"):
        if callback_data == "stars_gift":
            # Логика подарка (будет реализована позже)
            query.edit_message_text(
                "🎁 Отправка звёзд в подарок\n\n"
                "Функция в разработке..."
            )
            # Устанавливаем состояние для подарка
            context.user_data['buying_stars'] = True
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Выберите действие:",
                reply_markup=get_purchase_keyboard()
            )
        else:
            # Извлекаем количество звезд из callback_data
            amount = int(callback_data.split("_")[1])
            context.user_data['buying_stars'] = True
            context.user_data['stars_amount'] = amount
            
            # Обновляем сообщение и показываем новое меню
            query.edit_message_text(
                f"✅ Выбрано: {amount} звёзд"
            )
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Выберите действие:",
                reply_markup=get_purchase_keyboard()
            )


def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    # Проверяем, находится ли пользователь в процессе покупки звезд
    if context.user_data.get('buying_stars'):
        # Пользователь вводит количество звезд или использует меню
        if text == "🎁 В подарок":
            # Логика подарка (будет реализована позже)
            update.message.reply_text(
                "🎁 Отправка звёзд в подарок\n\n"
                "Функция в разработке...",
                reply_markup=get_purchase_keyboard()
            )
            return
        elif text == "🔙 Назад":
            # Возвращаемся к выбору количества
            context.user_data.pop('buying_stars', None)
            context.user_data.pop('stars_amount', None)
            handle_buy_stars(update, context)
            return
        else:
            # Проверяем, является ли введенный текст числом
            try:
                amount = int(text)
                
                if amount < 50:
                    update.message.reply_text(
                        "❌ Минимум — 50 звёзд",
                        reply_markup=get_purchase_keyboard()
                    )
                    return
                elif amount > 10000:
                    update.message.reply_text(
                        "❌ Максимум — 10 000 звёзд",
                        reply_markup=get_purchase_keyboard()
                    )
                    return
                else:
                    # Корректное число
                    context.user_data['stars_amount'] = amount
                    update.message.reply_text(
                        f"✅ Выбрано: {amount} звёзд\n\n"
                        "Выберите действие:",
                        reply_markup=get_purchase_keyboard()
                    )
                    return
                    
            except ValueError:
                # Не число
                update.message.reply_text(
                    "❌ Введите число от 50 до 10 000",
                    reply_markup=get_purchase_keyboard()
                )
                return
    
    # Обработка основных команд меню
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
    dispatcher.add_handler(CallbackQueryHandler(handle_callback_query))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    updater.start_polling()
    
    # Запускаем бота до тех пор, пока не будет нажато Ctrl-C
    updater.idle()


if __name__ == '__main__':
    main()
