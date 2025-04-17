from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from config import ADMIN_ID
import app.keyboards as kb
import dbconnection as db
import aiosqlite



router = Router()

class SetNum(StatesGroup):
    user_id = State()
    order_number = State()


class SendData(StatesGroup):
    order_ready_number = State()


@router.message(Command("help"))
async def send_help(message: Message):
    await message.answer(text=f"Ваше ID: {message.from_user.id}")

@router.message(CommandStart())
async def start_scenary(message: Message):
        await message.answer(text=f"Вас приветствует бот для онлайн-заказа блюд из ресторанов. Если Вы хотите получить уведомление "
                         f" по готовности заказа, нажмите кнопку 'Уведомление'.\n"
                         f"Если Вы хотите сделать заказ, нажмите на кнопку 'Сделать заказ'\n"
                         f" Выберите действие ниже: ", reply_markup=kb.main)



@router.callback_query(F.data == "notification")
async def notification(query: CallbackQuery, state: FSMContext):
    await state.update_data(user_id = query.from_user.id)
    await state.set_state(SetNum.order_number)
    await query.message.answer("Пожалуйста, введите номер Вашего заказа: ")


@router.message(SetNum.order_number)
async def set_order(message: Message, state: FSMContext):
    # Проверяем, что введённый номер заказа — число
    if not message.text.isdigit():
        await message.answer(text="❌ Номер заказа должен состоять только из цифр. Попробуйте ещё раз.", reply_markup=kb.main)
        return

    order_num = int(message.text)
    data = await state.get_data()
    user_id = data.get('user_id')

    if not user_id:
        await message.answer("⚠️ Произошла ошибка. Попробуйте снова: /start")
        await state.clear()
        return

    is_success = await db.add_notification_request(user_id=user_id, order_num=order_num)

    if is_success:
        await message.answer(
            f"✅ Уведомление по заказу №{order_num} активировано!\n"
            "Вы получите сообщение, когда заказ будет готов.",
            reply_markup=kb.main
        )
    else:
        await message.answer(
            "❌ Не удалось сохранить запрос. Попробуйте позже.",
            reply_markup=kb.main
        )

    await state.clear()




@router.message(Command("admin_panel"))
async def admin_panel(message: Message):
    if message.chat.id != ADMIN_ID:
        pass
    elif message.chat.id == ADMIN_ID:
        await message.answer(text="Выберите действие ниже: ", reply_markup=kb.admin_kb)


@router.callback_query(F.data == "admin")
async def send_notification_to_user(query: CallbackQuery, state: FSMContext):
    await state.set_state(SendData.order_ready_number)
    await query.message.answer("Введите номер готового заказа: ")

@router.message(SendData.order_ready_number)
async def send_order_to_user(message: Message, state: FSMContext):
    # Проверяем, что сообщение содержит номер заказа
    if not message.text.isdigit():
        await message.answer("❌ Пожалуйста, укажите корректный номер заказа.")
        return

    order_num = int(message.text)  # Получаем номер заказа из сообщения
    await state.update_data(order_ready_number=order_num)

    try:
        async with aiosqlite.connect('database.db') as db:
            # Выполняем запрос к базе данных
            cursor = await db.execute(
                "SELECT USER_ID FROM notify_users WHERE ORDER_NUM = ?",
                (order_num,)
            )
            result = await cursor.fetchone()  # Получаем первую строку результата

            if result:
                user_ready_id = result[0]  # Извлекаем USER_ID из результата
                # Отправляем сообщение пользователю
                await message.bot.send_message(chat_id=user_ready_id, text=f"✅ Ваш заказ №{order_num} готов!")
                await message.answer(f"✅ Уведомление отправлено пользователю с ID {user_ready_id}.")
            else:
                await message.answer(f"❌ Заказ №{order_num} не найден.")

    except Exception as e:
        print(f"Ошибка при поиске user_id: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса. Попробуйте позже.")





