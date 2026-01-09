"""
Модуль для работы с базой данных
"""
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL
from urllib.parse import urlparse, uses_netloc

logger = logging.getLogger(__name__)

# Поддержка postgres:// в urlparse (для Python 3.6+)
if 'postgres' not in uses_netloc:
    uses_netloc.append('postgres')
if 'postgresql' not in uses_netloc:
    uses_netloc.append('postgresql')


def get_connection():
    """Получить соединение с базой данных"""
    try:
        # Парсим DATABASE_URL
        parsed = urlparse(DATABASE_URL)
        
        # Получаем имя базы данных (убираем первый слэш)
        database = parsed.path[1:] if parsed.path and parsed.path.startswith('/') else parsed.path
        
        # Создаем соединение
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=database or 'postgres',
        )
        return conn
    except Exception as e:
        logger.error(f"Ошибка при подключении к базе данных: {e}")
        raise


def init_db():
    """Инициализация базы данных - создание таблиц"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Создаем таблицу и все необходимые объекты напрямую
        # Это более надежно, чем выполнение SQL файла
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255),
                language_code VARCHAR(10),
                is_premium BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                stars_balance INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username 
            ON users(username) WHERE username IS NOT NULL
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_created_at 
            ON users(created_at)
        """)
        
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_users_updated_at ON users
        """)
        
        cursor.execute("""
            CREATE TRIGGER update_users_updated_at 
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()
        """)
        
        conn.commit()
        logger.info("Таблицы базы данных созданы/проверены")
        
    except Exception as e:
        if conn:
            conn.rollback()
        error_msg = str(e)
        # Игнорируем ошибки о существующих объектах
        if 'already exists' not in error_msg.lower():
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise
        else:
            logger.info("Таблицы базы данных уже существуют")
    finally:
        if conn:
            conn.close()


def add_user(user):
    """
    Добавить нового пользователя или обновить существующего
    
    Args:
        user: объект User из telegram
        
    Returns:
        bool: True если пользователь был добавлен, False если обновлен
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM users WHERE id = %s", (user.id,))
        exists = cursor.fetchone()
        
        if exists:
            # Обновляем данные пользователя
            cursor.execute("""
                UPDATE users 
                SET username = %s,
                    first_name = %s,
                    last_name = %s,
                    language_code = %s,
                    is_premium = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                user.username,
                user.first_name,
                user.last_name,
                user.language_code,
                getattr(user, 'is_premium', False),
                user.id
            ))
            conn.commit()
            logger.info(f"Пользователь {user.id} обновлен в базе данных")
            return False
        else:
            # Добавляем нового пользователя
            cursor.execute("""
                INSERT INTO users (id, username, first_name, last_name, language_code, is_premium)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user.id,
                user.username,
                user.first_name,
                user.last_name,
                user.language_code,
                getattr(user, 'is_premium', False)
            ))
            conn.commit()
            logger.info(f"Новый пользователь {user.id} добавлен в базу данных")
            return True
            
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Ошибка при добавлении/обновлении пользователя: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_user(user_id):
    """
    Получить информацию о пользователе по ID
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        dict: информация о пользователе или None
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        return None
    finally:
        if conn:
            conn.close()
