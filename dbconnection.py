import aiosqlite


async def connect():
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            '''
            CREATE TABLE IF NOT EXISTS notify_users (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USER_ID INTEGER NOT NULL,
                ORDER_NUM INTEGER NOT NULL
            )
            '''
        )
        await db.commit()


async def add_notification_request(user_id: int, order_num: int) -> bool:
    try:
        async with aiosqlite.connect('database.db') as db:
            # Проверяем, существует ли уже запись
            cursor = await db.execute(
                "SELECT COUNT(*) FROM notify_users WHERE USER_ID = ? AND ORDER_NUM = ?",
                (user_id, order_num)
            )
            count = await cursor.fetchone()
            if count[0] > 0:
                return False  # Запись уже существует

            # Добавляем новую запись
            await db.execute(
                "INSERT INTO notify_users (USER_ID, ORDER_NUM) VALUES (?, ?)",
                (user_id, order_num)
            )
            await db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при сохранении уведомления: {e}")
        return False


