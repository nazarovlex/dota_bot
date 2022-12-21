import conf
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils import executor
import requests
import re

my_bot = Bot(token=conf.telegram_token)
dp = Dispatcher(my_bot)

account_info = KeyboardButton("Статистика аккаунта")
heroes_info = KeyboardButton("Лучшие 20 героев")

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
menu_keyboard.add(account_info)
menu_keyboard.add(heroes_info)

player_info = []
heroes_stat = []


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await my_bot.send_message(message["from"]["id"], "Введите ID аккаунта в доте", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands="stop")
async def cmd_stop(message: types.Message):
    await my_bot.send_message(message["from"]["id"], "Bye", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == "Статистика аккаунта")
async def acc_info(message: types.Message):
    await my_bot.send_message(message["from"]["id"], str(player_info))


@dp.message_handler(lambda message: message.text == "Лучшие 20 героев")
async def acc_info(message: types.Message):
    await my_bot.send_message(message["from"]["id"], str(heroes_stat))


@dp.message_handler()
async def process_id(message: types.Message):
    msg = message["text"]
    if msg == "master":
        msg = str(conf.master_id)

    global player_info, heroes_stat
    if re.search(r'^[0-9]+$', msg):
        player_info, error = await win_lose(msg)
        if not error:
            heroes_stat, error = await top_heroes(msg)
        if error:
            await my_bot.send_message(message["from"]["id"], "Ошибка сервера Dota (возможно некорректный ID)")
        else:
            await my_bot.send_message(message["from"]["id"], "Какую статистику показать?", reply_markup=menu_keyboard)
    else:
        await my_bot.send_message(message["from"]["id"], "Введите корректный ID аккаунта")


async def win_lose(account_id):
    params = {
        "api_key": conf.dota_token
    }
    name_response = requests.get(f"https://api.opendota.com/api/players/{account_id}", params=params)
    if name_response.status_code != 200:
        return None, True

    player_profile = name_response.json().get("profile", None)
    if player_profile is None:
        return None, True
    player_name = player_profile["personaname"]

    wl_response = requests.get(f"https://api.opendota.com/api/players/{account_id}/wl", params=params)
    if wl_response.status_code != 200:
        return None, True

    normal_wins = wl_response.json()["win"]
    normal_lose = wl_response.json()["lose"]

    turbo_params = {
        "api_key": conf.dota_token,
        "significant": 0,
        "game_mode": 23
    }

    turbo_wl_response = requests.get(
        f"https://api.opendota.com/api/players/{account_id}/wl", params=turbo_params)
    if turbo_wl_response.status_code != 200:
        return None, True

    turbo_wins = turbo_wl_response.json()["win"]
    turbo_lose = turbo_wl_response.json()["lose"]
    turbo_wr = round(turbo_wins / (turbo_lose + turbo_wins) * 100, 2)
    normal_wr = round(normal_wins / (normal_wins + normal_lose) * 100, 2)

    info = [player_name, normal_wins, normal_lose, normal_wr, turbo_wins, turbo_lose, turbo_wr]
    info.insert(0, "Никнейм игрока: ")
    info.insert(2, "\nПобед в нормальной игре: ")
    info.insert(4, "\nПоражений в нормальной игре: ")
    info.insert(6, "\nПроцент побед в нормальной игре: ")
    info.insert(8, "\nПобед в турбо: ")
    info.insert(10, "\nПоражений в турбо: ")
    info.insert(12, "\nПроцент побед в турбо: ")
    info = ' '.join(map(str, info))

    return info, False


async def top_heroes(account_id):
    params = {
        "api_key": conf.dota_token
    }

    all_heroes_response = requests.get("https://api.opendota.com/api/heroes", params=params)
    if all_heroes_response.status_code != 200:
        return None, True

    id_name_heroes_data = {}

    for hero in all_heroes_response.json():
        id_name_heroes_data[str(hero["id"])] = hero["localized_name"]

    response_heroes = requests.get(f"https://api.opendota.com/api/players/{account_id}/heroes", params=params)
    if response_heroes.status_code != 200:
        return None, True

    best_twenty_heroes = response_heroes.json()[:20]
    info = []
    for hero in best_twenty_heroes:
        info += [
            "Название героя: ", id_name_heroes_data[hero["hero_id"]] + "\n",
            "Матчей: ", hero["games"], "\n",
            "Побед: ", hero["win"], "\n",
            "Поражений: ", hero["games"] - hero["win"], "\n",
            "Процент побед: ", round(hero["win"] / hero["games"] * 100, 2), "\n\n"]
    info = ''.join(map(str, info))
    return info, False


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
