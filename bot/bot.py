import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import httpx
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set in env")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class AddHabit(StatesGroup):
    waiting_name = State()


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
    await message.reply("Привет! Я буду помогать отслеживать привычки. Используй /addhabit, /done и /stats")


@dp.message_handler(commands=["addhabit"])
async def cmd_addhabit(message: types.Message):
    await message.reply("Напиши название привычки (например: Читать 20 минут)")
    await AddHabit.waiting_name.set()


@dp.message_handler(state=AddHabit.waiting_name)
async def process_habit_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    async with httpx.AsyncClient() as client:
        # register ensures user exists and returns internal user id
        reg = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
        reg_json = reg.json() if reg.status_code == 200 else {}
        user_id = reg_json.get("id")
        if not user_id:
            await message.reply("Не удалось зарегистрировать пользователя. Попробуйте позже.")
            await state.finish()
            return
        res = await client.post(f"{BACKEND}/bot/add_habit", params={"user_id": user_id, "name": name})
    await message.reply(f"Добавлена привычка: {name}")
    await state.finish()


@dp.message_handler(commands=["done"])
async def cmd_done(message: types.Message):
    # get habits for user
    async with httpx.AsyncClient() as client:
        # Lookup user by telegram_id (fast)
        res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
        if res.status_code == 404:
            await message.reply("Вы не зарегистрированы. Отправьте /start")
            return
        my = res.json()
        user_id = my.get("id")
        habits_resp = await client.get(f"{BACKEND}/users/{user_id}/habits")
        if habits_resp.status_code != 200:
            await message.reply("Ошибка при получении списка привычек. Попробуйте позже.")
            return
        habits = habits_resp.json()
    if not habits:
        await message.reply("У вас нет привычек. Добавьте через /addhabit")
        return
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for h in habits:
        kb.add(KeyboardButton(str(h["id"]) + ": " + h["name"]))
    await message.reply("Выберите привычку (нажмите кнопку):", reply_markup=kb)


@dp.message_handler(lambda m: ": " in m.text)
async def choose_habit(message: types.Message):
    try:
        hid = int(message.text.split(": ", 1)[0])
    except Exception:
        await message.reply("Не понял выбор.")
        return
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
        if res.status_code == 404:
            await message.reply("Не зарегистрированы. Отправьте /start")
            return
        my = res.json()
        user_id = my.get("id")
        await client.post(f"{BACKEND}/bot/done", params={"user_id": user_id, "habit_id": hid})
    await message.reply("Отмечено как сделанное сегодня!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=["stats"])
async def cmd_stats(message: types.Message):
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
        if res.status_code == 404:
            await message.reply("Вы не зарегистрированы. Отправьте /start")
            return
        my = res.json()
        user_id = my.get("id")
        stats_resp = await client.get(f"{BACKEND}/users/{user_id}/stats")
        if stats_resp.status_code != 200:
            await message.reply("Ошибка при получении статистики. Попробуйте позже.")
            return
        stats = stats_resp.json()
    await message.reply(f"У вас привычек: {stats.get('habits')}\nЗа последние 7 дней отмечено: {stats.get('done_last_7_days')}")


def main():
    from aiogram import executor
    # Ensure there's an event loop set for the main thread (fixes RuntimeError on some envs)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
