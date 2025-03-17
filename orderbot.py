import telebot
from telebot import types
import sqlite3
import logging
import threading

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

admin_id = 1205843084  # ID администратора (должен быть integer)
bot = telebot.TeleBot("7725640690:AAEOP6dDRw2IxIB7XAeALgtHO5vTT2FSaL8")

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("orders.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT DEFAULT 'В процессе приготовления'
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Команда /start
@bot.message_handler(commands=["start"])
def main_order(message):
    if message.chat.id == admin_id:
        # Клавиатура для администратора
        markup = types.InlineKeyboardMarkup()
        but1 = types.InlineKeyboardButton("Сообщить пользователю о готовности заказа", callback_data="notify_user")
        markup.add(but1)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        # Клавиатура для пользователя
        markup = types.InlineKeyboardMarkup()

        but = types.InlineKeyboardButton(
            text="Открыть меню",
            web_app=types.WebAppInfo(url="https://py-tenz.github.io/bot_order/")
        )
        but1 = types.InlineKeyboardButton(
            "Хочу получить уведомление по готовности заказа!",
            callback_data="check_status"
        )
        markup.add(but, but1)
        bot.send_message(
            message.chat.id,
            "Здравствуйте! Вас приветствует бот ресторана. Через него Вы сможете сделать заказ и забрать его:",
            reply_markup=markup
        )

# Команда /help
@bot.message_handler(commands=["help"])
def help_command(message):
    help_text = """
Доступные команды:
/start - Начать работу с ботом
/help - Получить справку по командам
"""
    bot.send_message(message.chat.id, help_text)

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "notify_user":
        # Логика для администратора
        bot.send_message(call.message.chat.id, "Введите номер заказа, который готов:")
        bot.register_next_step_handler(call.message, notify_user)
    elif call.data == "check_status":
        # Логика для пользователя
        bot.send_message(call.message.chat.id, "Введите номер вашего заказа:")
        bot.register_next_step_handler(call.message, save_order_and_check_status)

# Функция для сохранения заказа и проверки статуса
def save_order_and_check_status(message):
    order_number = message.text.strip()
    user_id = message.chat.id

    # Сохраняем заказ в базу данных
    conn = sqlite3.connect("orders.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO orders (order_number, user_id)
            VALUES (?, ?)
        """, (order_number, user_id))
        conn.commit()

        # Получаем статус заказа
        cursor.execute("SELECT status FROM orders WHERE order_number = ?", (order_number,))
        status = cursor.fetchone()[0]
        bot.send_message(user_id, f"Статус вашего заказа: {status}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении заказа: {e}")
        bot.send_message(user_id, f"Произошла ошибка: {e}")
    finally:
        conn.close()

# Функция для уведомления пользователя
def notify_user(message):
    order_number = message.text.strip()

    # Получаем данные о заказе из базы данных
    conn = sqlite3.connect("orders.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM orders WHERE order_number = ?", (order_number,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            # Обновляем статус заказа
            cursor.execute("UPDATE orders SET status = 'Готов' WHERE order_number = ?", (order_number,))
            conn.commit()

            # Отправляем уведомление пользователю
            bot.send_message(user_id, "Ваш заказ готов!")
            bot.send_message(message.chat.id, f"Пользователь с ID {user_id} уведомлен о готовности заказа.")

            # Удаляем заказ из базы данных после уведомления
            cursor.execute("DELETE FROM orders WHERE order_number = ?", (order_number,))
            conn.commit()
            bot.send_message(message.chat.id, f"Заказ {order_number} удален из базы данных.")
        else:
            bot.send_message(message.chat.id, "Заказ с таким номером не найден или пользователь не желает получать уведомление о готовности.")
    except Exception as e:
        logger.error(f"Ошибка при уведомлении пользователя: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
    finally:
        conn.close()

# Запуск бота с использованием многопоточности
def polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")

polling_thread = threading.Thread(target=polling)
polling_thread.start()