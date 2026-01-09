-- Создание таблицы users для хранения информации о пользователях Telegram бота
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,  -- Telegram user ID
    username VARCHAR(255),  -- Telegram username (может быть NULL)
    first_name VARCHAR(255) NOT NULL,  -- Имя пользователя
    last_name VARCHAR(255),  -- Фамилия (может быть NULL)
    language_code VARCHAR(10),  -- Код языка пользователя
    is_premium BOOLEAN DEFAULT FALSE,  -- Имеет ли пользователь Telegram Premium
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата регистрации
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Дата последнего обновления
    stars_balance INTEGER DEFAULT 0,  -- Баланс звезд (для будущего функционала)
    total_spent INTEGER DEFAULT 0  -- Всего потрачено (для будущего функционала)
);

-- Создание индекса для быстрого поиска по username (если он есть)
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username) WHERE username IS NOT NULL;

-- Создание индекса для сортировки по дате регистрации
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at при изменении записи
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
