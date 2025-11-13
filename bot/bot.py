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
import logging
    waiting_name = State()


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
    await message.reply("Привет! Я буду помогать отслеживать привычки. Используй /addhabit, /done и /stats")



# simple logging to bot.log/stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@dp.message_handler(commands=["addhabit"])
async def cmd_addhabit(message: types.Message):
    await message.reply("Напиши название привычки (например: Читать 20 минут)")
    await AddHabit.waiting_name.set()


@dp.message_handler(state=AddHabit.waiting_name)
        try:
            res = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
            if res.status_code == 200:
                logger.info(f"Registered user {message.from_user.id}")
        except Exception as e:
            logger.exception("Error registering user on /start")
    name = message.text.strip()
    async with httpx.AsyncClient() as client:
        # register ensures user exists and returns internal user id
        reg = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
        reg_json = reg.json() if reg.status_code == 200 else {}
        user_id = reg_json.get("id")
        if not user_id:
        try:
            reg = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
            reg_json = reg.json() if reg.status_code == 200 else {}
        except Exception:
            reg_json = {}
            await state.finish()
            return
        res = await client.post(f"{BACKEND}/bot/add_habit", params={"user_id": user_id, "name": name})
    await message.reply(f"Добавлена привычка: {name}")
    await state.finish()
        try:
            res = await client.post(f"{BACKEND}/bot/add_habit", params={"user_id": user_id, "name": name})
            if res.status_code == 200:
                logger.info(f"Added habit for user {user_id}: {name}")
        except Exception:
            logger.exception("Error adding habit")

@dp.message_handler(commands=["done"])
async def cmd_done(message: types.Message):
    # get habits for user
    async with httpx.AsyncClient() as client:
        # Lookup user by telegram_id (fast)
        res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
        if res.status_code == 404:
        try:
            res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
        except Exception:
            logger.exception("Error calling /users/by_telegram")
            await message.reply("Ошибка сервера. Попробуйте позже.")
            return
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
        try:
            done_res = await client.post(f"{BACKEND}/bot/done", params={"user_id": user_id, "habit_id": hid})
        except Exception:
            logger.exception("Error calling /bot/done")
            await message.reply("Ошибка при отметке привычки. Попробуйте позже.", reply_markup=types.ReplyKeyboardRemove())
            return

        if done_res.status_code == 200:
            jr = done_res.json()
            if jr.get("ok"):
                await message.reply("✅ Отмечено как сделанное сегодня!", reply_markup=types.ReplyKeyboardRemove())
            else:
                await message.reply(jr.get("message", "Уже отмечено сегодня"), reply_markup=types.ReplyKeyboardRemove())
        else:
            # log server response body for debugging
            try:
                text = done_res.text
            except Exception:
                text = '<no-body>'
            logger.error(f"/bot/done returned status {done_res.status_code}: {text}")
            await message.reply("Ошибка при отметке привычки. Попробуйте позже.", reply_markup=types.ReplyKeyboardRemove())
        if res.status_code == 404:
            await message.reply("Не зарегистрированы. Отправьте /start")
            return
        my = res.json()
        user_id = my.get("id")
        done_res = await client.post(f"{BACKEND}/bot/done", params={"user_id": user_id, "habit_id": hid})
    if done_res.status_code == 200:
        jr = done_res.json()
        if jr.get("ok"):
            await message.reply("Отмечено как сделанное сегодня!", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.reply(jr.get("message", "Уже отмечено сегодня"), reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.reply("Ошибка при отметке привычки. Попробуйте позже.", reply_markup=types.ReplyKeyboardRemove())


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
