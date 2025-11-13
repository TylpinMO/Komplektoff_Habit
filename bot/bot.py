import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


class AddHabit(StatesGroup):
    waiting_name = State()


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
    await message.reply(
        "Привет! 👋 Я помогу отслеживать привычки и прогресс.\n\n"
        "<b>Команды:</b>\n"
        "/addhabit — добавить новую привычку\n"
        "/done — отметить выполненную привычку за сегодня\n"
        "/stats — показать простую статистику\n"
        "/help — краткая подсказка\n\n"
        "Чтобы начать, добавьте первую привычку через /addhabit"
    )



# simple logging to bot.log/stdout
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dp.message_handler(commands=["addhabit"])
async def cmd_addhabit(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Отмена"))
    await message.reply("Напиши название привычки (например: Читать 20 минут)", reply_markup=kb)
    await AddHabit.waiting_name.set()


@dp.message_handler(state=AddHabit.waiting_name)
async def process_addhabit(message: types.Message, state: FSMContext):
    # allow user to cancel
    if message.text and message.text.lower() == 'отмена':
        await state.finish()
        await message.reply('Отменено ✅', reply_markup=ReplyKeyboardRemove())
        return

    name = message.text.strip()
    async with httpx.AsyncClient() as client:
        # register ensures user exists and returns internal user id
        try:
            reg = await client.post(f"{BACKEND}/bot/register_user", params={"telegram_id": message.from_user.id, "username": message.from_user.username})
            reg_json = reg.json() if reg.status_code == 200 else {}
            user_id = reg_json.get("id")
        except Exception:
            logger.exception("Error registering user")
            await state.finish()
            await message.reply("Ошибка сервера. Попробуйте позже.")
            return

        if not user_id:
            await state.finish()
            await message.reply("Не удалось получить id пользователя.")
            return

        try:
            res = await client.post(f"{BACKEND}/bot/add_habit", params={"user_id": user_id, "name": name})
            if res.status_code == 200:
                logger.info(f"Added habit for user {user_id}: {name}")
            else:
                logger.error(f"add_habit returned {res.status_code}: {res.text}")
                await message.reply("Не удалось добавить привычку. Попробуйте позже.")
                await state.finish()
                return
        except Exception:
            logger.exception("Error adding habit")
            await message.reply("Ошибка сервера при добавлении привычки.")
            await state.finish()
            return

    await message.reply(f"✅ <b>Добавлена привычка:</b> {name}", reply_markup=ReplyKeyboardRemove())
    await state.finish()

@dp.message_handler(commands=["done"])
async def cmd_done(message: types.Message):
    # get habits for user
    async with httpx.AsyncClient() as client:
        try:
            # Lookup user by telegram_id (fast)
            res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
        except Exception:
            logger.exception("Error calling /users/by_telegram")
            await message.reply("Ошибка сервера. Попробуйте позже.")
            return

        if res.status_code == 404:
            await message.reply("Вы не зарегистрированы. Отправьте /start")
            return

        my = res.json()
        user_id = my.get("id")
        try:
            habits_resp = await client.get(f"{BACKEND}/users/{user_id}/habits")
        except Exception:
            logger.exception("Error getting habits")
            await message.reply("Ошибка при получении списка привычек. Попробуйте позже.")
            return

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
    kb.add(KeyboardButton("Отмена"))
    await message.reply("Выберите привычку (нажмите кнопку):", reply_markup=kb)


@dp.message_handler(lambda m: m.text and ": " in m.text)
async def choose_habit(message: types.Message):
    try:
        hid = int(message.text.split(": ", 1)[0])
    except Exception:
        await message.reply("Не понял выбор.")
        return

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
            if res.status_code == 404:
                await message.reply("Не зарегистрированы. Отправьте /start")
                return
            my = res.json()
            user_id = my.get("id")
        except Exception:
            logger.exception("Error calling /users/by_telegram")
            await message.reply("Ошибка сервера. Попробуйте позже.", reply_markup=ReplyKeyboardRemove())
            return

        # allow cancel
        if message.text and message.text.lower() == 'отмена':
            await message.reply('Отменено ✅', reply_markup=ReplyKeyboardRemove())
            return

        try:
            done_res = await client.post(f"{BACKEND}/bot/done", params={"user_id": user_id, "habit_id": hid})
        except Exception:
            logger.exception("Error calling /bot/done")
            await message.reply("Ошибка при отметке привычки. Попробуйте позже.", reply_markup=ReplyKeyboardRemove())
            return

        if done_res.status_code == 200:
            jr = done_res.json()
            if jr.get("ok"):
                await message.reply("✅ Отмечено как сделанное сегодня!", reply_markup=ReplyKeyboardRemove())
            else:
                await message.reply(jr.get("message", "Уже отмечено сегодня"), reply_markup=ReplyKeyboardRemove())
        else:
            # log server response body for debugging
            try:
                text = done_res.text
            except Exception:
                text = '<no-body>'
            logger.error(f"/bot/done returned status {done_res.status_code}: {text}")
            await message.reply("Ошибка при отметке привычки. Попробуйте позже.", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=["stats"])
async def cmd_stats(message: types.Message):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{BACKEND}/users/by_telegram/{message.from_user.id}")
        except Exception:
            logger.exception("Error calling /users/by_telegram")
            await message.reply("Ошибка сервера. Попробуйте позже.")
            return

        if res.status_code == 404:
            await message.reply("Вы не зарегистрированы. Отправьте /start")
            return
        my = res.json()
        user_id = my.get("id")
        try:
            stats_resp = await client.get(f"{BACKEND}/users/{user_id}/stats")
        except Exception:
            logger.exception("Error getting stats")
            await message.reply("Ошибка при получении статистики. Попробуйте позже.")
            return

        if stats_resp.status_code != 200:
            await message.reply("Ошибка при получении статистики. Попробуйте позже.")
            return
        stats = stats_resp.json()
    # nicer formatting
    await message.reply(
        f"<b>Статистика</b>\n"
        f"Привычек: <b>{stats.get('habits')}</b>\n"
        f"Отмечено за 7 дней: <b>{stats.get('done_last_7_days')}</b>\n",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.reply(
        "<b>Краткая справка</b>\n"
        "• /addhabit — добавить новую привычку\n"
        "• /done — отметить привычку за сегодня (выберите из списка)\n"
        "• /stats — посмотреть простую статистику\n"
        "• Отправьте 'Отмена' при вводе, чтобы прервать операцию"
    )


@dp.message_handler(commands=['cancel'])
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply('Операция отменена ✅', reply_markup=ReplyKeyboardRemove())


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
