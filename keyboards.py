from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сделать заказ", web_app=WebAppInfo(url="https://py-tenz.github.io/bot_order/"))],
        [InlineKeyboardButton(text="Уведомление", callback_data="notification")]
    ]
)

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Уведомить пользователя о готовности", callback_data="admin")],
    ]
)