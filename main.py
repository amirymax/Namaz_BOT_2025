from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
from datetime import datetime, timedelta
import logging
import asyncio
from api_token import TOKEN

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Загружаем данные о временах намаза
with open("prayer_times.json", "r", encoding="utf-8") as f:
    prayer_times = json.load(f)

# Главное меню (выбор страны)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(*[KeyboardButton(country) for country in prayer_times.keys()])

steps = {
    "country": None
    }
# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    with open("users.txt", "a") as f:
        f.write(f"{message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} {message.from_user.username}\n")
    await message.answer("🌟 Добро пожаловать! Этот бот показывает времена намаза в разных городах мира.  Выберите страну, чтобы продолжить. 🇹🇯🇷🇺\n\Автор бота: @Amirilifee", reply_markup=main_menu)

# Обработчик выбора страны
@dp.message_handler(lambda message: steps["country"] == None)
async def choose_country(message: types.Message):
    country = message.text
    try:
        cities = list(prayer_times[country].keys())
        steps["country"] = country
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(*[KeyboardButton(city) for city in cities])
        markup.add(KeyboardButton("🔙 Назад"))
        await message.answer("Выберите город:", reply_markup=markup)
    except KeyError:
        steps["country"] = None
        await message.answer("❌ Страна не найдена. Пожалуйста, выберите другую страну.", reply_markup=main_menu)
    

# Обработчик выбора города 
@dp.message_handler(lambda message: steps["country"] != None and message.text != "🔙 Назад")
async def get_prayer_times(message: types.Message):
    try:
        country = steps["country"]
        cities = prayer_times[country]
        if message.text in cities:
            city = message.text
            today = datetime.today().strftime("%Y-%m-%d")
            tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
            times_today = cities.get(city, {}).get(today)
            times_tomorrow = cities.get(city, {}).get(tomorrow)

            text = f"📍 <b>{city}, {country}</b>\n"
            
            if times_today:
                text += f"📅 {today}\n"
                text += "\n".join(
                    [f"🕌 <b>{key.capitalize()}</b>: {value}" for key, value in times_today.items()]
                )
            
            if times_tomorrow:
                text += f"\n\n📅 {tomorrow}\n"
                text += "\n".join(
                    [f"🕌 <b>{key.capitalize()}</b>: {value}" for key, value in times_tomorrow.items()]
                )
            
            if not times_today and not times_tomorrow:
                text = "⚠️ Пока для этого города точный источник не найден.\nЕсли у вас есть источник, напишите @Amiri_Talks"
            
            await message.answer(text, parse_mode="HTML")
        

        else:
            await message.answer("⚠️ Пока для этого города точный источник не найден.\nЕсли у вас есть источник, напишите @Amiri_Talks")

    except KeyError:
        steps["country"] = None
        await message.answer("❌ Пожалуйста, выберите страну.", reply_markup=main_menu)
# Обработчик кнопки "Назад"
@dp.message_handler(lambda message: message.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Выберите страну:", reply_markup=main_menu)
    steps["country"] = None


# Запуск бота
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
