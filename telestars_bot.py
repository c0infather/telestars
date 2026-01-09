import logging
import math
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


def show_order_message(update: Update, context: CallbackContext, amount: int, is_gift: bool = False, chat_id: int = None) -> None:
    """Показывает сообщение с информацией о заказе"""
    # Получаем chat_id из обновления или переданного параметра
    if chat_id is None:
        if update.callback_query:
            chat_id = update.callback_query.message.chat_id
            user = update.callback_query.from_user
        else:
            chat_id = update.message.chat_id
            user = update.effective_user
    else:
        user = update.effective_user if not update.callback_query else update.callback_query.from_user
    
    username = user.username if user.username else "username"
    
    # Цена за одну звезду
    price_per_star = 1.47
    
    # Рассчитываем стоимость
    total_cost = amount * price_per_star
    # Округляем в большую сторону
    final_cost = math.ceil(total_cost)
    
    # Определяем получателя
    if is_gift:
        recipient_text = f"⭐ Звёзды для аккаунта @{username} (в подарок)"
    else:
        recipient_text = f"⭐ Звёзды для аккаунта @{username}"
    
    message = (
        "⏳ Счёт активен 30 минут\n\n"
        "🧾 Ваш заказ:\n"
        f"{recipient_text}\n\n"
        "💰 Стоимость:\n"
        f" ⭐ Количество звезд = {final_cost} ₽ (исходя из цены {price_per_star} за звезду)\n"
        "Итоговая сумма округлена в большую сторону\n\n"
        "👇 Ссылка на оплату ниже"
    )
    
    # Сохраняем информацию о заказе
    context.user_data['current_order'] = {
        'amount': amount,
        'cost': final_cost,
        'is_gift': is_gift
    }
    
    # Отправляем сообщение
    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=get_reply_keyboard()
    )
    
    # Сбрасываем состояние покупки
    context.user_data.pop('buying_stars', None)
    context.user_data.pop('stars_amount', None)


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
    # Устанавливаем состояние выбора количества звезд
    context.user_data['buying_stars'] = True
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
            # Устанавливаем флаг подарка и возвращаем к выбору количества
            context.user_data['buying_stars'] = True
            context.user_data['is_gift'] = True
            query.edit_message_text(
                "🎁 Отправка звёзд в подарок\n\n"
                "Выберите количество звёзд ниже\n"
                "или введите число от 50 до 10 000",
                reply_markup=get_stars_selection_keyboard()
            )
        else:
            # Извлекаем количество звезд из callback_data
            amount = int(callback_data.split("_")[1])
            
            # Проверяем валидность количества
            if amount < 50:
                query.answer("❌ Минимум — 50 звёзд", show_alert=True)
                return
            elif amount > 10000:
                query.answer("❌ Максимум — 10 000 звёзд", show_alert=True)
                return
            
            # Проверяем, является ли это подарком
            is_gift = context.user_data.get('is_gift', False)
            
            # Закрываем inline сообщение и показываем заказ
            query.edit_message_text("✅ Обработка заказа...")
            show_order_message(update, context, amount, is_gift, chat_id=query.message.chat_id)
            
            # Сбрасываем флаг подарка
            context.user_data.pop('is_gift', None)


def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    text = update.message.text
    
    # Проверяем, находится ли пользователь в процессе покупки звезд (выбор количества)
    if context.user_data.get('buying_stars'):
        # Проверяем, является ли введенный текст числом
        try:
            amount = int(text)
            
            # Проверка валидности количества
            if amount < 50:
                update.message.reply_text(
                    "❌ Минимум — 50 звёзд\n\n"
                    "Попробуйте еще раз или выберите из предложенных вариантов:",
                    reply_markup=get_stars_selection_keyboard()
                )
                return
            elif amount > 10000:
                update.message.reply_text(
                    "❌ Максимум — 10 000 звёзд\n\n"
                    "Попробуйте еще раз или выберите из предложенных вариантов:",
                    reply_markup=get_stars_selection_keyboard()
                )
                return
            else:
                # Корректное число - показываем заказ
                is_gift = context.user_data.get('is_gift', False)
                show_order_message(update, context, amount, is_gift)
                
                # Сбрасываем флаг подарка
                context.user_data.pop('is_gift', None)
                return
                
        except ValueError:
            # Не число - показываем ошибку и возвращаем к выбору
            update.message.reply_text(
                "❌ Введите число от 50 до 10 000\n\n"
                "Или выберите из предложенных вариантов:",
                reply_markup=get_stars_selection_keyboard()
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
