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
        # register ensures user exists
        await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
        res = await client.post(f"{BACKEND}/bot/add_habit", params={"user_id": message.from_user.id, "name": name})
    await message.reply(f"Добавлена привычка: {name}")
    await state.finish()


@dp.message_handler(commands=["done"])
async def cmd_done(message: types.Message):
    # get habits for user
    async with httpx.AsyncClient() as client:
        # Try to find user id in backend by telegram_id via /users list
        users = await client.get(f"{BACKEND}/users")
        users = users.json()
        my = next((u for u in users if u.get("telegram_id") == message.from_user.id), None)
        if not my:
            await message.reply("Вы не зарегистрированы. Отправьте /start")
            return
        user_id = my["id"]
        habits = await client.get(f"{BACKEND}/users/{user_id}/habits")
        habits = habits.json()
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
        # find user id
        users = await client.get(f"{BACKEND}/users")
        users = users.json()
        my = next((u for u in users if u.get("telegram_id") == message.from_user.id), None)
        if not my:
            await message.reply("Не зарегистрированы. Отправьте /start")
            return
        user_id = my["id"]
        await client.post(f"{BACKEND}/bot/done", params={"user_id": user_id, "habit_id": hid})
    await message.reply("Отмечено как сделанное сегодня!", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=["stats"])
async def cmd_stats(message: types.Message):
    async with httpx.AsyncClient() as client:
        users = await client.get(f"{BACKEND}/users")
        users = users.json()
        my = next((u for u in users if u.get("telegram_id") == message.from_user.id), None)
        if not my:
            await message.reply("Вы не зарегистрированы. Отправьте /start")
            return
        user_id = my["id"]
        stats = await client.get(f"{BACKEND}/users/{user_id}/stats")
        stats = stats.json()
    await message.reply(f"У вас привычек: {stats.get('habits')}\nЗа последние 7 дней отмечено: {stats.get('done_last_7_days')}")


def main():
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
