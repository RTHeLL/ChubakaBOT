import configparser
import logging
import random
import time

import math
import requests
from typing import Optional, Any, List

# Import VKBottle
from vkbottle import GroupEventType, GroupTypes, Keyboard, ABCHandler, ABCView, \
    BaseMiddleware, \
    CtxStorage, Text
from vkbottle.bot import Bot, Message
from vkbottle_types.objects import UsersUserXtrCounters

# Import classes
import classes.mysql
import classes.timer

# Import data
import data.general
import data.timers

# Define
MySQL = classes.mysql.MySQL()
UserAction = classes.mysql.UserAction()
MainData = classes.mysql.MainData()
dummy_db = CtxStorage()
config = configparser.ConfigParser()
config.read("config/vk.ini")
timer = classes.timer
general = data.general.General()

# Logs settings
logging.basicConfig(filename="logs/logs.log")
logging.basicConfig(level=logging.INFO)

# VK ConnectionTypeError: __init__() takes 1 positional argument but 5 were given

bot = Bot(config["VK_DATA"]["GROUP_TOKEN"])

# Keyboards
START_KEYBOARD = (
    Keyboard(one_time=False).add(Text("❓ Помощь", payload={"cmd": "cmd_help"})).get_json()
)

MAIN_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "📒 Профиль", "type": "text", "payload": {"cmd": "cmd_profile"}, "color": "primary"},
            {"label": "💲 Баланс", "type": "text", "payload": {"cmd": "cmd_balance"}, "color": "secondary"},
            {"label": "👑 Рейтинг", "type": "text", "payload": {"cmd": "cmd_rating"}, "color": "secondary"}
        ],
        [
            {"label": "🛍 Магазин", "type": "text", "payload": {"cmd": "cmd_shop"}, "color": "secondary"},
            {"label": "💰 Банк", "type": "text", "payload": {"cmd": "cmd_bank"}, "color": "secondary"}
        ],
        [
            {"label": "❓ Помощь", "type": "text", "payload": {"cmd": "cmd_help"}, "color": "secondary"},
            {"label": "💡 Разное", "type": "text", "payload": {"cmd": "cmd_other"}, "color": "secondary"}
        ],
        [
            {"label": "🎁 Получить бонус", "type": "text", "payload": {"cmd": "cmd_bonus"}, "color": "positive"}
        ]
    ]
).get_json()

SHOP_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "🚗 Машины", "type": "text", "payload": {"cmd": "cmd_shop_transport_cars"}, "color": "secondary"},
            {"label": "🏍 Мотоциклы", "type": "text", "payload": {"cmd": "cmd_shop_transport_motorcycles"},
             "color": "secondary"},
            {"label": "🛥 Яхты", "type": "text", "payload": {"cmd": "cmd_shop_transport_yachts"}, "color": "secondary"},
            {"label": "🛩 Самолеты", "type": "text", "payload": {"cmd": "cmd_shop_transport_airplanes"},
             "color": "secondary"},
            {"label": "🚁 Вертолеты", "type": "text", "payload": {"cmd": "cmd_shop_transport_helicopters"},
             "color": "secondary"}
        ],
        [
            {"label": "🏠 Дома", "type": "text", "payload": {"cmd": "cmd_shop_estate_houses"}, "color": "secondary"},
            {"label": "🌇 Квартиры", "type": "text", "payload": {"cmd": "cmd_shop_estate_apartments"},
             "color": "secondary"}
        ],
        [
            {"label": "📱 Телефоны", "type": "text", "payload": {"cmd": "cmd_shop_other_phones"}, "color": "secondary"},
            {"label": "🔋 Фермы", "type": "text", "payload": {"cmd": "cmd_shop_other_farms"}, "color": "secondary"},
            {"label": "💼 Бизнесы", "type": "text", "payload": {"cmd": "cmd_shop_other_businesses"},
             "color": "secondary"},
            {"label": "🐸 Питомцы", "type": "text", "payload": {"cmd": "cmd_shop_other_pets"}, "color": "secondary"}
        ],
        [
            {"label": "📦 Кейсы", "type": "text", "payload": {"cmd": "cmd_shop_other_cases"}, "color": "secondary"}
        ],
        [
            {"label": "◀ В главное меню", "type": "text", "payload": {"cmd": "cmd_mainmenu"}, "color": "positive"}
        ]
    ]
).get_json()

OTHER_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "🚀 Игры", "type": "text", "payload": {"cmd": "cmd_games"}, "color": "secondary"},
            {"label": "🖨 Реши", "type": "text", "payload": {"cmd": "cmd_equation"}, "color": "secondary"},
            {"label": "📊 Курс", "type": "text", "payload": {"cmd": "cmd_course"}, "color": "secondary"}
        ],
        [
            {"label": "🏆 Топ", "type": "text", "payload": {"cmd": "cmd_top"}, "color": "secondary"},
            {"label": "🤝 Передать", "type": "text", "payload": {"cmd": "cmd_transfer"}, "color": "secondary"}
        ],
        [
            {"label": "⚙ Настройки", "type": "text", "payload": {"cmd": "cmd_settings"}, "color": "primary"},
            {"label": "◀ В главное меню", "type": "text", "payload": {"cmd": "cmd_mainmenu"}, "color": "positive"}
        ]
    ]
).get_json()

GAMES_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "🔫 Рулетка", "type": "text", "payload": {"cmd": "game_roulette"}, "color": "secondary"},
            {"label": "🎲 Кубик", "type": "text", "payload": {"cmd": "game_cube"}, "color": "secondary"},
            {"label": "🎰 Казино", "type": "text", "payload": {"cmd": "game_casino"}, "color": "secondary"}
        ],
        [
            {"label": "📈 Трейд", "type": "text", "payload": {"cmd": "game_trade"}, "color": "secondary"},
            {"label": "🥛 Стаканчик", "type": "text", "payload": {"cmd": "game_cup"}, "color": "secondary"},
            {"label": "🦅 Монетка", "type": "text", "payload": {"cmd": "game_coin"}, "color": "secondary"}
        ],
        [
            {"label": "◀ В раздел \"разное\"", "type": "text", "payload": {"cmd": "cmd_other"}, "color": "positive"}
        ]
    ]
).get_json()

GAME_ROULETTE_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "🔫 Выстрелить", "type": "text", "payload": {"cmd": "game_roulette_shot"}, "color": "secondary"},
            {"label": "💵 Остановиться", "type": "text", "payload": {"cmd": "game_roulette_stop"},
             "color": "secondary"},
        ],
        [
            {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"}, "color": "positive"}
        ]
    ]
).get_json()

GAME_CUBE_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "🎲 1", "type": "text", "payload": {"cmd": "game_cube_1"}, "color": "secondary"},
            {"label": "🎲 2", "type": "text", "payload": {"cmd": "game_cube_2"}, "color": "secondary"},
            {"label": "🎲 3", "type": "text", "payload": {"cmd": "game_cube_3"}, "color": "secondary"}
        ],
        [
            {"label": "🎲 4", "type": "text", "payload": {"cmd": "game_cube_4"}, "color": "secondary"},
            {"label": "🎲 5", "type": "text", "payload": {"cmd": "game_cube_5"}, "color": "secondary"},
            {"label": "🎲 6", "type": "text", "payload": {"cmd": "game_cube_6"}, "color": "secondary"}
        ],
        [
            {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"}, "color": "positive"}
        ]
    ]
).get_json()

GAME_COIN_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "🦅 Орел", "type": "text", "payload": {"cmd": "game_coin_1"}, "color": "secondary"},
            {"label": "🗂 Решка", "type": "text", "payload": {"cmd": "game_coin_2"}, "color": "secondary"},
        ],
        [
            {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"}, "color": "positive"}
        ]
    ]
).get_json()


# Subs classes
class NoBotMiddleware(BaseMiddleware):
    async def pre(self, message: Message):
        return message.from_id > 0  # True / False


# noinspection PyTypeChecker
class RegistrationMiddleware(BaseMiddleware):
    async def pre(self, message: Message):
        user = dummy_db.get(message.from_id)
        if user is None:
            user = (await bot.api.users.get(message.from_id))[0]
            dummy_db.set(message.from_id, user)
        return {"info": user}


class InfoMiddleware(BaseMiddleware):
    async def post(
            self,
            message: Message,
            view: "ABCView",
            handle_responses: List[Any],
            handlers: List["ABCHandler"],
    ):
        if not handlers:
            return


fliptext_dict = {'q': 'q', 'w': 'ʍ', 'e': 'ǝ', 'r': 'ɹ', 't': 'ʇ', 'y': 'ʎ', 'u': 'u', 'i': 'ᴉ', 'o': 'o', 'p': 'p',
                 'a': 'ɐ', 's': 's', 'd': 'd', 'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ', 'j': 'ɾ', 'k': 'ʞ', 'l': 'l', 'z': 'z',
                 'x': 'x', 'c': 'ɔ', 'v': 'ʌ', 'b': 'b', 'n': 'n', 'm': 'ɯ',
                 'й': 'ņ', 'ц': 'ǹ', 'у': 'ʎ', 'к': 'ʞ', 'е': 'ǝ', 'н': 'н', 'г': 'ɹ', 'ш': 'm', 'щ': 'm', 'з': 'ε',
                 'х': 'х', 'ъ': 'q', 'ф': 'ф', 'ы': 'ıq', 'в': 'ʚ', 'а': 'ɐ', 'п': 'u', 'р': 'd', 'о': 'о', 'л': 'v',
                 'д': 'ɓ', 'ж': 'ж', 'э': 'є', 'я': 'ʁ', 'ч': 'һ', 'с': 'ɔ', 'м': 'w', 'и': 'и', 'т': 'ɯ', 'ь': 'q',
                 'б': 'ƍ', 'ю': 'oı'}

# Timers
timer.RepeatedTimer(3600, data.timers.Timers.hour_timer).start()
timer.RepeatedTimer(60, data.timers.Timers.minute_timer).start()


# User commands
@bot.on.message(text=["Начать", "Старт", "начать", "старт"])
@bot.on.message(payload={"cmd": "cmd_start"})
async def start_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(f"Вы уже зарегистрированы в боте!\nИспользуйте команду \"Помощь\", для получения списка "
                             f"команд")


@bot.on.message(text=["Помощь", "помощь"])
@bot.on.message(payload={"cmd": "cmd_help"})
async def help_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:"
                             f"\n🎉 Развлекательные:\n"
                             f"⠀⠀↪ Переверни [фраза]\n"
                             f"⠀⠀🔮 Шар [фраза]\n"
                             f"⠀⠀📊 Инфа [фраза]\n"
                             f"⠀⠀⚖ Выбери [фраза] или [фраза2]\n"
                             f"⠀⠀📊 Курс\n"
                             f"⠀⠀💖 Брак\n"
                             f"⠀⠀💔 Развод\n\n"
                             f"💼 Бизнес:\n"
                             f"⠀⠀📈 Бизнес\n"
                             f"⠀⠀💵 Бизнес снять [сумма]\n"
                             f"⠀⠀👷 Бизнес нанять [кол-во]\n"
                             f"⠀⠀✅ Бизнес улучшить\n\n"
                             f"🌽 Питомцы:\n"
                             f"⠀⠀🐒 Питомец\n"
                             f"⠀⠀🐪 Питомец поход\n"
                             f"⠀⠀🌟 Питомец улучшить\n\n"
                             f"🚀 Игры:\n"
                             f"⠀⠀🎲 Кубик\n"
                             f"⠀⠀🎰 Казино [ставка]\n"
                             f"⠀⠀📈 Трейд [вверх/вниз] [ставка]\n"
                             f"⠀⠀🥛 Стаканчик [1-3] [ставка]\n"
                             f"⠀⠀🦅 Монетка\n\n"
                             f"🔥 Полезное:\n"
                             f"⠀⠀📒 Профиль\n"
                             f"⠀⠀🛍 Магазин\n"
                             f"⠀⠀💲 Баланс\n"
                             f"⠀⠀💰 Банк\n"
                             f"⠀⠀📦 Кейсы\n"
                             f"⠀⠀🔋 Ферма\n"
                             f"⠀⠀💎 Бонус\n\n"
                             f"💡 Разное:\n"
                             f"⠀⠀⚔ Клан\n"
                             f"⠀⠀🍹 Зелья\n"
                             f"⠀⠀👑 Рейтинг - ваш рейтинг\n"
                             f"⠀⠀🏆 Топ\n"
                             f"⠀⠀📠 Реши [пример]\n"
                             f"⠀⠀✒ Ник [имя]\n"
                             f"⠀⠀💸 Продать [предмет]\n"
                             f"⠀⠀🤝 Передать [ID] [сумма]\n"
                             f"⠀⠀👥 Реф\n"
                             f"⠀⠀🏆 Реф топ\n"
                             f"⠀⠀🎁 Донат\n\n"
                             f"🆘 Репорт [фраза] - ошибки или пожелания", keyboard=MAIN_KEYBOARD)


@bot.on.message(text=["Профиль", "профиль"])
@bot.on.message(payload={"cmd": "cmd_profile"})
async def profile_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)

        temp_message = f'@id{message.from_id} ({user[0]["Name"]}), Ваш профиль:\n'
        temp_message += f'🔎 ID: {user[0]["ID"]}\n'
        # Check RankLevel
        if user[0]["RankLevel"] == 2:
            temp_message += f'🔥 VIP игрок\n'
        elif user[0]["RankLevel"] == 3:
            temp_message += f'🔮 Premium игрок\n'
        elif user[0]["RankLevel"] == 4:
            temp_message += f'🌀 Модератор\n'
        elif user[0]["RankLevel"] >= 5:
            temp_message += f'👑 Администратор\n'
        # Basic check
        if user[0]["EXP"] > 0:
            temp_message += f'⭐ Опыта: {general.change_number(user[0]["EXP"])}\n'
        if user[0]["Money"] > 0:
            temp_message += f'💰 Денег: {general.change_number(user[0]["Money"])}$\n'
        if user[0]["BTC"] > 0:
            temp_message += f'🌐 Биткоинов: {general.change_number(user[0]["BTC"])}₿\n'
        if user[0]["Rating"] > 0:
            temp_message += f'👑 Рейтинг: {general.change_number(user[0]["Rating"])}\n'
        if user[0]["Marriage_Partner"] > 0:
            temp_message += f'💖 Партнер: @id{UserAction.get_user_by_gameid(user[0]["Marriage_Partner"])[0]["VK_ID"]}' \
                            f' ({UserAction.get_user_by_gameid(user[0]["Marriage_Partner"])[0]["Name"]})\n'
        # Property
        temp_message += f'\n🔑 Имущество:\n'
        if user[1]["Car"] > 0:
            temp_message += f'⠀🚗 Машина: {MainData.get_data("cars")[user[1]["Car"] - 1]["CarName"]}\n'
        if user[1]["Motorcycle"] > 0:
            temp_message += f'⠀🏍 Мотоцикл: {MainData.get_data("motorcycles")[user[1]["Motorcycle"] - 1]["MotoName"]}\n'
        if user[1]["Yacht"] > 0:
            temp_message += f'⠀🛥 Яхта: {MainData.get_data("yachts")[user[1]["Yacht"] - 1]["YachtName"]}\n'
        if user[1]["Airplane"] > 0:
            temp_message += f'⠀✈ Самолет: ' \
                            f'{MainData.get_data("airplanes")[user[1]["Airplane"] - 1]["AirplaneName"]}\n'
        if user[1]["Helicopter"] > 0:
            temp_message += f'⠀🚁 Вертолет: ' \
                            f'{MainData.get_data("helicopters")[user[1]["Helicopter"] - 1]["HelicopterName"]}\n'
        if user[1]["House"] > 0:
            temp_message += f'⠀🏠 Дом: {MainData.get_data("houses")[user[1]["House"] - 1]["HouseName"]}\n'
        if user[1]["Apartment"] > 0:
            temp_message += f'⠀🌇 Квартира: ' \
                            f'{MainData.get_data("apartments")[user[1]["Apartment"] - 1]["ApartmentName"]}\n'
        if user[1]["Business"] > 0:
            temp_message += f'⠀💼 Бизнес: ' \
                            f'{MainData.get_data("businesses")[user[1]["Business"] - 1]["BusinessName"]}\n'
        if user[1]["Pet"] > 0:
            temp_message += f'⠀{MainData.get_data("pets")[user[1]["Pet"] - 1]["PetIcon"]} Питомец: ' \
                            f'{MainData.get_data("pets")[user[1]["Pet"] - 1]["PetName"]}\n'
        if user[1]["Farms"] > 0:
            temp_message += f'⠀🔋 Фермы: {MainData.get_data("farms")[user[1]["FarmsType"] - 1]["FarmName"]} ' \
                            f'({general.change_number(user[1]["Farms"])} шт.)\n'
        if user[1]["Phone"] > 0:
            temp_message += f'⠀📱 Телефон: {MainData.get_data("phones")[user[1]["Phone"] - 1]["PhoneName"]}\n'

        temp_message += f'\n📗 Дата регистрации: {user[0]["Register_Data"].strftime("%d.%m.%Y, %H:%M:%S")}\n'
        await message.answer(temp_message)


@bot.on.message(text=["Банк", "банк"])
@bot.on.message(text=["Банк <item1>", "банк <item1>"])
@bot.on.message(text=["Банк <item1> <item2:int>", "банк <item1> <item2:int>"])
@bot.on.message(payload={"cmd": "cmd_bank"})
async def bank_handler(message: Message, info: UsersUserXtrCounters, item1: Optional[str] = None,
                       item2: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if item1 is None and item2 is None:
            await message.answer(
                f'@id{message.from_id} ({user[0]["Name"]}), на Вашем банковском счете: {general.change_number(user[0]["Bank_Money"])}$')
        elif item1 == "положить":
            if item2 is None or not general.isint(item2):
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте "банк положить [сумма], '
                                     f'чтобы положить деньги на счет')
            else:
                if user[0]["Money"] < item2:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                else:
                    user[0]["Bank_Money"] += item2
                    user[0]["Money"] -= item2
                    UserAction.save_user(message.from_id, user)
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), Вы пополнили свой банковский счет на '
                        f'{general.change_number(item2)}$')
        elif item1 == "снять":
            if item2 is None or not general.isint(item2):
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте "банк снять [сумма], '
                                     f'чтобы снять деньги со счета')
            else:
                if user[0]["Bank_Money"] < item2:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), на Вашем банковском счете нет '
                                         f'столько денег!')
                else:
                    user[0]["Bank_Money"] -= item2
                    user[0]["Money"] += item2
                    UserAction.save_user(message.from_id, user)
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), Вы сняли со своего банковского счета '
                        f'{general.change_number(item2)}$')
        else:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте "банк [положить/снять] [сумма]'
                                 f'"')


@bot.on.message(text=["Магазин", "магазин"])
@bot.on.message(text=["Магазин <category>", "магазин <category>"])
@bot.on.message(text=["Магазин <category> купить <product>", "магазин <category> купить <product>"])
@bot.on.message(
    text=["Магазин <category> купить <product> <count:int>", "магазин <category> купить <product> <count:int>"])
@bot.on.message(payload={"cmd": "cmd_shop"})
async def shop_handler(message: Message, info: UsersUserXtrCounters, category: Optional[str] = None,
                       product: Optional[str] = None, count: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        shop_data = MainData.get_shop_data()
        shop_data_sorted = MainData.get_shop_data(1)
        temp_text = ''
        if category is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), разделы магазина:\n'
                                 f'🚙 Транспорт:\n'
                                 f'⠀🚗 Машины\n'
                                 f'⠀🏍 Мотоциклы\n'
                                 f'⠀🛥 Яхты\n'
                                 f'⠀🛩 Самолеты\n'
                                 f'⠀🚁 Вертолеты\n'
                                 f'\n🏘 Недвижимость:\n'
                                 f'⠀🏠 Дома\n'
                                 f'⠀🌇 Квартиры\n'
                                 f'\n📌 Остальное:\n'
                                 f'⠀📱 Телефоны\n'
                                 f'⠀🔋 Фермы\n'
                                 f'⠀👑 Рейтинг [кол-во]⠀⠀{general.change_number(1000000)}$/ед.\n'
                                 f'⠀💼 Бизнесы\n'
                                 f'⠀🌐 Биткоин [кол-во]⠀⠀{general.change_number(MainData.get_settings()[0]["BTC_USD_Curse"])}$/ед.\n'
                                 f'⠀🐸 Питомцы\n'
                                 f'⠀📦 Кейсы'
                                 f'\n🔎 Для просмотра категории используйте "магазин [категория]".\n'
                                 f'🔎 Для покупки используйте "магазин [категория] купить [номер товара]".\n',
                                 keyboard=SHOP_KEYBOARD)
        elif category.lower() == 'машины':
            if product is None:
                for car in shop_data_sorted[0]:
                    temp_text += f'\n🔸 {car["ID"]}. {car["CarName"]} [{general.change_number(car["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), машины: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин машины купить [номер]"')
            else:
                if user[1]["Car"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть машина! Для покупки'
                                         f', продайте старую: продать машина!')
                else:
                    if user[0]["Money"] < shop_data[0][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[0][int(product) - 1]["Price"]
                        user[1]["Car"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[0][int(product) - 1]["CarName"]} за '
                                             f'{general.change_number(shop_data[0][int(product) - 1]["Price"])}$')
        elif category.lower() == 'яхты':
            if product is None:
                for yacht in shop_data_sorted[1]:
                    temp_text += f'\n🔸 {yacht["ID"]}. {yacht["YachtName"]} [{general.change_number(yacht["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), яхты: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин яхты купить [номер]"')
            else:
                if user[1]["Yacht"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть яхта! Для покупки'
                                         f', продайте старую: продать яхта!')
                else:
                    if user[0]["Money"] < shop_data[1][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[1][int(product) - 1]["Price"]
                        user[1]["Yacht"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[1][int(product) - 1]["YachtName"]} за '
                                             f'{general.change_number(shop_data[1][int(product) - 1]["Price"])}$')
        elif category.lower() == 'самолеты':
            if product is None:
                for airplane in shop_data_sorted[2]:
                    temp_text += f'\n🔸 {airplane["ID"]}. {airplane["AirplaneName"]} ' \
                                 f'[{general.change_number(airplane["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), самолеты: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин самолеты купить [номер]"')
            else:
                if user[1]["Airplane"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть самолет! Для '
                                         f'покупки, продайте старый: продать самолет!')
                else:
                    if user[0]["Money"] < shop_data[2][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[2][int(product) - 1]["Price"]
                        user[1]["Airplane"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[2][int(product) - 1]["AirplaneName"]} за '
                                             f'{general.change_number(shop_data[2][int(product) - 1]["Price"])}$')
        elif category.lower() == 'вертолеты' or category.lower() == 'вертолёты':
            if product is None:
                for helicopters in shop_data_sorted[3]:
                    temp_text += f'\n🔸 {helicopters["ID"]}. {helicopters["HelicopterName"]} ' \
                                 f'[{general.change_number(helicopters["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), вертолеты: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин вертолеты купить [номер]"')
            else:
                if user[1]["Helicopter"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть вертолет! Для '
                                         f'покупки, продайте старый: продать вертолет!')
                else:
                    if user[0]["Money"] < shop_data[3][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[3][int(product) - 1]["Price"]
                        user[1]["Helicopter"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[3][int(product) - 1]["HelicopterName"]} за '
                                             f'{general.change_number(shop_data[3][int(product) - 1]["Price"])}$')
        elif category.lower() == 'дома':
            if product is None:
                for houses in shop_data_sorted[4]:
                    temp_text += f'\n🔸 {houses["ID"]}. {houses["HouseName"]} ' \
                                 f'[{general.change_number(houses["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), дома: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин дома купить [номер]"')
            else:
                if user[1]["House"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть дом! Для покупки'
                                         f', продайте старый: продать дом!')
                else:
                    if user[0]["Money"] < shop_data[4][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[4][int(product) - 1]["Price"]
                        user[1]["House"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[4][int(product) - 1]["HouseName"]} за '
                                             f'{general.change_number(shop_data[4][int(product) - 1]["Price"])}$')
        elif category.lower() == 'квартиры':
            if product is None:
                for apartments in shop_data_sorted[5]:
                    temp_text += f'\n🔸 {apartments["ID"]}. {apartments["ApartmentName"]} ' \
                                 f'[{general.change_number(apartments["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), квартиры: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин квартиры купить [номер]"')
            else:
                if user[1]["Apartment"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть квартира! Для '
                                         f'покупки, продайте старую: продать квартира!')
                else:
                    if user[0]["Money"] < shop_data[5][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[5][int(product) - 1]["Price"]
                        user[1]["Apartment"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[5][int(product) - 1]["ApartmentName"]} за '
                                             f'{general.change_number(shop_data[5][int(product) - 1]["Price"])}$')
        elif category.lower() == 'телефоны':
            if product is None:
                for phones in shop_data_sorted[6]:
                    temp_text += f'\n🔸 {phones["ID"]}. {phones["PhoneName"]} ' \
                                 f'[{general.change_number(phones["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), телефоны: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин телефоны купить [номер]"')
            else:
                if user[1]["Phone"] > 0:
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть телефон! Для покупки'
                        f', продайте старый: продать телефон!')
                else:
                    if user[0]["Money"] < shop_data[6][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[6][int(product) - 1]["Price"]
                        user[1]["Phone"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[6][int(product) - 1]["PhoneName"]} за '
                                             f'{general.change_number(shop_data[6][int(product) - 1]["Price"])}$')
        elif category.lower() == 'фермы':
            if product is None:
                for farms in MainData.get_data("farms"):
                    temp_text += f'\n🔸 {farms["ID"]}. {farms["FarmName"]} - {farms["FarmBTCPerHour"]} ₿/час ' \
                                 f'[{general.change_number(farms["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), фермы: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин фермы купить [номер]"')
            else:
                if count is None:
                    if user[0]["Money"] < shop_data[7][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[7][int(product) - 1]["Price"]
                        user[1]["Farms"] += 1
                        user[1]["FarmsType"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[7][int(product) - 1]["FarmName"]} за '
                                             f'{general.change_number(shop_data[7][int(product) - 1]["Price"])}$')
                else:
                    if user[0]["Money"] < shop_data[7][int(product) - 1]["Price"] * count:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[7][int(product) - 1]["Price"] * count
                        user[1]["Farms"] += count
                        user[1]["FarmsType"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{general.change_number(count)} ферм(ы) '
                                             f'{shop_data[7][int(product) - 1]["FarmName"]} за '
                                             f'{general.change_number(shop_data[7][int(product) - 1]["Price"] * count)}$')
        elif category.lower() == 'рейтинг':
            if product is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), ❓ Для покупки введите "магазин рейтинг'
                                     f' купить [кол-во]"')
            else:
                if user[0]["Money"] < int(product) * 1000000:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= int(product) * 1000000
                    user[0]["Rating"] += int(product)
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                         f'{product} рейтинга за {general.change_number(int(product) * 1000000)}$\n'
                                         f'Ваш рейтинг: {general.change_number(user[0]["Rating"])} 👑')
        elif category.lower() == 'бизнесы':
            if product is None:
                for businesses in shop_data_sorted[8]:
                    temp_text += f'\n🔸 {businesses["ID"]}. {businesses["BusinessName"]} ' \
                                 f'[{general.change_number(businesses["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), бизнесы: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин бизнесы купить [номер]"')
            else:
                if user[1]["Business"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть бизнес! Для покупки'
                                         f', продайте старый: продать бизнес!')
                else:
                    if user[0]["Money"] < shop_data[8][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[8][int(product) - 1]["Price"]
                        user[0]["Money_In_Business"] = 0
                        user[0]["Workers_In_Business"] = 0
                        user[1]["Business"] = product
                        user[1]["BusinessLevel"] = 1
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[8][int(product) - 1]["BusinessName"]} за '
                                             f'{general.change_number(shop_data[8][int(product) - 1]["Price"])}$')
        elif category.lower() == 'биткоин':
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), ❓ Для покупки введите "биткоин [кол-во]"')
        elif category.lower() == 'питомцы':
            if product is None:
                for pets in shop_data_sorted[9]:
                    temp_text += f'\n🔸 {pets["ID"]}. {pets["PetIcon"]} {pets["PetName"]} ' \
                                 f'[{general.change_number(pets["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), питомцы: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин питомцы купить [номер]"')
            else:
                if user[1]["Pet"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть питомец! Для '
                                         f'покупки, продайте старого: продать питомец!')
                else:
                    if user[0]["Money"] < shop_data[9][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[9][int(product) - 1]["Price"]
                        user[0]["Pet_Hunger"] = 100
                        user[0]["Pet_Joy"] = 100
                        user[1]["Pet"] = product
                        user[1]["PetLevel"] = 1
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[9][int(product) - 1]["PetIcon"]} '
                                             f'{shop_data[9][int(product) - 1]["PetName"]} за '
                                             f'{general.change_number(shop_data[9][int(product) - 1]["Price"])}$')
        elif category.lower() == 'мотоциклы':
            if product is None:
                for motorcycle in shop_data_sorted[10]:
                    temp_text += f'\n🔸 {motorcycle["ID"]}. {motorcycle["MotoName"]} [{general.change_number(motorcycle["Price"])}$]'
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), мотоциклы: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин мотоциклы купить [номер]"')
            else:
                if user[1]["Motorcycle"] > 0:
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть мотоцикл! Для покупки'
                        f', продайте старый: продать мотоцикл!')
                else:
                    if user[0]["Money"] < shop_data[10][int(product) - 1]["Price"]:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= shop_data[10][int(product) - 1]["Price"]
                        user[1]["Motorcycle"] = product
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{shop_data[10][int(product) - 1]["MotoName"]} за '
                                             f'{general.change_number(shop_data[10][int(product) - 1]["Price"])}$')
        elif category.lower() == 'кейсы':
            if product is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), кейсы: {temp_text}'
                                     f'🔸 1. Bronze Case [10.000$]\n'
                                     f'🔸 2. Silver Case [60.000$]\n'
                                     f'🔸 3. Gold Case [150.000$]\n'
                                     f'🔸 4. Premium Case [10 руб.]\n\n'
                                     f'❓ Для покупки введите "магазин кейсы купить [номер] ([кол-во])"')
            elif product == '1':
                if count is None:
                    if user[0]["Money"] < 10000:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= 10000
                        user[0]["Bronze_Case"] += 1
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'Bronze Case за 10.000$')
                else:
                    if user[0]["Money"] < 10000 * count:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= 10000 * count
                        user[0]["Bronze_Case"] += count
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{general.change_number(count)} Bronze Case за '
                                             f'{general.change_number(10000 * count)}$')
            elif product == '2':
                if count is None:
                    if user[0]["Money"] < 60000:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= 60000
                        user[0]["Silver_Case"] += 1
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'Silver Case за 60.000$')
                else:
                    if user[0]["Money"] < 60000 * count:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= 60000 * count
                        user[0]["Silver_Case"] += count
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{general.change_number(count)} Silver Case за '
                                             f'{general.change_number(60000 * count)}$')
            elif product == '3':
                if count is None:
                    if user[0]["Money"] < 150000:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= 150000
                        user[0]["Gold_Case"] += 1
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'Gold Case за 150.000$')
                else:
                    if user[0]["Money"] < 150000 * count:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
                    else:
                        user[0]["Money"] -= 150000 * count
                        user[0]["Gold_Case"] += count
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                             f'{general.change_number(count)} Gold Case за '
                                             f'{general.change_number(150000 * count)}$')
            elif product == '4':
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), данный кейс можно купить только '
                                     f'через донат\n'
                                     f'Используйте: донат')
        else:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), проверьте правильность введенных данных!")


# Shop transport
@bot.on.message(payload={"cmd": "cmd_shop_transport_cars"})
@bot.on.message(payload={"cmd": "cmd_shop_transport_motorcycles"})
@bot.on.message(payload={"cmd": "cmd_shop_transport_yachts"})
@bot.on.message(payload={"cmd": "cmd_shop_transport_airplanes"})
@bot.on.message(payload={"cmd": "cmd_shop_transport_helicopters"})
# Shop estate
@bot.on.message(payload={"cmd": "cmd_shop_estate_houses"})
@bot.on.message(payload={"cmd": "cmd_shop_estate_apartments"})
# Shop other
@bot.on.message(payload={"cmd": "cmd_shop_other_phones"})
@bot.on.message(payload={"cmd": "cmd_shop_other_farms"})
@bot.on.message(payload={"cmd": "cmd_shop_other_businesses"})
@bot.on.message(payload={"cmd": "cmd_shop_other_pets"})
@bot.on.message(payload={"cmd": "cmd_shop_other_cases"})
async def shop_products_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        shop_data = MainData.get_shop_data()
        shop_data_sorted = MainData.get_shop_data(1)
        temp_text = ''
        products_category = message.payload.split('{"cmd":"cmd_shop_')[1].split('"}')[0]
        if products_category == 'transport_cars':
            for car in shop_data_sorted[0]:
                temp_text += f'\n🔸 {car["ID"]}. {car["CarName"]} [{general.change_number(car["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), машины: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин машины купить [номер]"')
        if products_category == 'transport_yachts':
            for yacht in shop_data_sorted[1]:
                temp_text += f'\n🔸 {yacht["ID"]}. {yacht["YachtName"]} [{general.change_number(yacht["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), яхты: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин яхты купить [номер]"')
        if products_category == 'transport_airplanes':
            for airplane in shop_data_sorted[2]:
                temp_text += f'\n🔸 {airplane["ID"]}. {airplane["AirplaneName"]} ' \
                             f'[{general.change_number(airplane["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), самолеты: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин самолеты купить [номер]"')
        if products_category == 'transport_helicopters':
            for helicopters in shop_data_sorted[3]:
                temp_text += f'\n🔸 {helicopters["ID"]}. {helicopters["HelicopterName"]} ' \
                             f'[{general.change_number(helicopters["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), вертолеты: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин вертолеты купить [номер]"')
        if products_category == 'estate_houses':
            for houses in shop_data_sorted[4]:
                temp_text += f'\n🔸 {houses["ID"]}. {houses["HouseName"]} ' \
                             f'[{general.change_number(houses["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), дома: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин дома купить [номер]"')
        if products_category == 'estate_apartments':
            for apartments in shop_data_sorted[5]:
                temp_text += f'\n🔸 {apartments["ID"]}. {apartments["ApartmentName"]} ' \
                             f'[{general.change_number(apartments["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), квартиры: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин квартиры купить [номер]"')
        if products_category == 'other_phones':
            for phones in shop_data_sorted[6]:
                temp_text += f'\n🔸 {phones["ID"]}. {phones["PhoneName"]} ' \
                             f'[{general.change_number(phones["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), телефоны: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин телефоны купить [номер]"')
        if products_category == 'other_farms':
            for farms in shop_data_sorted[7]:
                temp_text += f'\n🔸 {farms["ID"]}. {farms["FarmName"]} - {farms["FarmBTCPerHour"]} ₿/час ' \
                             f'[{general.change_number(farms["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), фермы: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин фермы купить [номер]"')
        if products_category == 'other_businesses':
            for businesses in shop_data_sorted[8]:
                temp_text += f'\n🔸 {businesses["ID"]}. {businesses["BusinessName"]} ' \
                             f'[{general.change_number(businesses["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), бизнесы: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин бизнесы купить [номер]"')
        if products_category == 'other_pets':
            for pets in shop_data_sorted[9]:
                temp_text += f'\n🔸 {pets["ID"]}. {pets["PetIcon"]} {pets["PetName"]} ' \
                             f'[{general.change_number(pets["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), питомцы: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин питомцы купить [номер]"')
        if products_category == 'transport_motorcycles':
            for motorcycle in shop_data_sorted[10]:
                temp_text += f'\n🔸 {motorcycle["ID"]}. {motorcycle["MotoName"]} [{general.change_number(motorcycle["Price"])}$]'
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), мотоциклы: {temp_text}\n\n '
                                 f'❓ Для покупки введите "магазин мотоциклы купить [номер]"')
        if products_category == 'other_cases':
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), кейсы: {temp_text}\n'
                                 f'🔸 1. Bronze Case [10.000$]\n'
                                 f'🔸 2. Silver Case [60.000$]\n'
                                 f'🔸 3. Gold Case [150.000$]\n'
                                 f'🔸 4. Premium Case [10 руб.]\n\n'
                                 f'❓ Для покупки введите "магазин кейсы купить [номер] ([кол-во])"')


@bot.on.message(text=["Бонус", "бонус"])
@bot.on.message(payload={"cmd": "cmd_bonus"})
async def bonus_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: "
                             f"{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if user[0]["Bonus"] == 0:
            temp_money = random.randint(50, 500)
            temp_btc = random.randint(1, 50)
            if user[0]["RankLevel"] == 1:
                user[0]["Money"] += temp_money
                user[0]["Bonus"] = 24*60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money)} $. '
                                     f'Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"]*60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"]*60))}.')
            elif user[0]["RankLevel"] == 2:
                user[0]["Money"] += temp_money * 2
                user[0]["BTC"] += temp_btc
                user[0]["Bonus"] = 12*60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 2)} $ '
                                     f'и {general.change_number(temp_btc)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"]*60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"]*60))}')
            elif user[0]["RankLevel"] == 3:
                user[0]["Money"] += temp_money * 3
                user[0]["BTC"] += temp_btc * 2
                user[0]["Bonus"] = 6*60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 3)} $ '
                                     f'и {general.change_number(temp_btc * 2)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"]*60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"]*60))}')
            elif user[0]["RankLevel"] == 4:
                user[0]["Money"] += temp_money * 4
                user[0]["BTC"] += temp_btc * 3
                user[0]["Bonus"] = 3*60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 4)} $ '
                                     f'и {general.change_number(temp_btc * 3)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"]*60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"]*60))}')
            elif user[0]["RankLevel"] >= 5:
                user[0]["Money"] += temp_money * 5
                user[0]["BTC"] += temp_btc * 4
                user[0]["Bonus"] = 1*60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 5)} $ '
                                     f'и {general.change_number(temp_btc * 4)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"]*60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"]*60))}')
            UserAction.save_user(message.from_id, user)
        else:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам еще недоступен бонус! Возвращайтесь '
                                 f'через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"]*60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"]*60))}')


@bot.on.message(text=["Баланс", "баланс"])
@bot.on.message(payload={"cmd": "cmd_balance"})
async def balance_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: "
                             f"{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас на руках '
                             f'{general.change_number(user[0]["Money"])}$\n'
                             f'💳 В банке: {general.change_number(user[0]["Bank_Money"])}$\n'
                             f'🌐 Биткоинов: {general.change_number(user[0]["BTC"])}₿')


@bot.on.message(text=["Рейтинг", "рейтинг"])
@bot.on.message(payload={"cmd": "cmd_rating"})
async def rating_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: "
                             f"{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш рейтинг: '
                             f'{general.change_number(user[0]["Rating"])} 👑')


@bot.on.message(text=["Передать", "передать"])
@bot.on.message(text=["Передать <gameid:int>", "передать <gameid:int>"])
@bot.on.message(text=["Передать <gameid:int> <money:int>", "передать <gameid:int> <money:int>"])
@bot.on.message(payload={"cmd": "cmd_transfer"})
async def transfer_handler(message: Message, info: UsersUserXtrCounters, gameid: Optional[int] = None,
                           money: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: "
                             f"{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if gameid is None or money is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте "передать [игровой ID] '
                                 f'[сумма]", чтобы передать деньги')
        else:
            if user[0]["Money"] < money:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько денег!')
            elif not UserAction.get_user_by_gameid(gameid):
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), такого пользователя не существует!')
            elif gameid == user[0]["ID"]:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                     f'нельзя передать деньги самому себе!')
            else:
                transfer_user = UserAction.get_user_by_gameid(gameid)
                user[0]["Money"] -= money
                transfer_user[0]["Money"] += money
                UserAction.save_user(message.from_id, user)
                UserAction.save_user(transfer_user[0]["VK_ID"], transfer_user)
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы успешно перевели '
                                     f'{general.change_number(money)}$ игроку @id{transfer_user[0]["VK_ID"]} '
                                     f'({transfer_user[0]["Name"]})')
                await message.answer(f'@id{transfer_user[0]["VK_ID"]} ({transfer_user[0]["Name"]}), пользователь '
                                     f'@id{message.from_id} '
                                     f'({user[0]["Name"]}) перевел Вам {general.change_number(money)}$',
                                     user_id=transfer_user[0]["VK_ID"])


@bot.on.message(text=["Выбери <item1> <item2>", "выбери <item1> <item2>"])
@bot.on.message(payload={"cmd": "cmd_selecttext"})
async def selecttext_handler(message: Message, info: UsersUserXtrCounters, item1: Optional[str] = None,
                             item2: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if item1 is None or item2 is None:
            await message.answer(
                f"@id{message.from_id} ({user[0]['Name']}), Используйте: выбери \"фраза 1\" \"фраза 2\"")
        else:
            temp_var = random.randint(0, 1)
            if temp_var == 0:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), мне кажется лучше \"{item1}\", чем \"{item2}\"")
            elif temp_var == 1:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), мне кажется лучше \"{item2}\", чем \"{item1}\"")


@bot.on.message(text=["Переверни", "переверни"])
@bot.on.message(text=["Переверни <item>", "переверни <item>"])
async def fliptext_handler(message: Message, info: UsersUserXtrCounters, item: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if item is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Используйте: переверни \"текст\"")
        else:
            await message.answer(
                f"@id{message.from_id} ({user[0]['Name']}), держи \"{''.join(list(map(lambda x, y: x.replace(x, fliptext_dict.get(x)), ''.join(item.replace(' ', '').lower()), fliptext_dict)))}\"")


@bot.on.message(text=["Шар", "шар"])
@bot.on.message(text=["Шар <item>", "шар <item>"])
async def magicball_handler(message: Message, info: UsersUserXtrCounters, item: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        if item is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), Используйте: шар \"текст\"")
        else:
            ball_text = ('перспективы не очень хорошие', 'предрешено', 'мой ответ - «нет»', 'хорошие перспективы',
                         'пока не ясно', 'сконцентрируйся и спроси опять', 'знаки говорят - «Да»', 'определённо да',
                         'вероятнее всего', 'весьма сомнительно', 'спроси позже', 'по моим данным - «Нет»')
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), {random.choice(ball_text)}")


@bot.on.message(text=["Инфа", "инфа"])
@bot.on.message(text=["Инфа <item>", "инфа <item>"])
async def infa_handler(message: Message, info: UsersUserXtrCounters, item: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if item is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Используйте: инфа \"текст\"")
        else:
            infa_text = ('вероятность -', 'шанс этого', 'мне кажется около')
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), {random.choice(infa_text)} "
                                 f"{random.randint(0, 100)}%")


@bot.on.message(text=["Реши", "реши"])
@bot.on.message(text=["Реши <equation>", "реши <equation>"])
@bot.on.message(payload={"cmd": "cmd_equation"})
async def equation_handler(message: Message, info: UsersUserXtrCounters, equation: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if equation is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Используйте: реши [уравнение]")
        else:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), {eval(equation)}")


@bot.on.message(text=["Курс", "курс"])
@bot.on.message(payload={"cmd": "cmd_course"})
async def course_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        bit = requests.get('https://api.cryptonator.com/api/ticker/btc-usd',
                           headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) '
                                                  'Gecko/20030624 Netscape/7.1 (ax)'}).json()
        await message.answer(
            f'@id{message.from_id} ({UserAction.get_user(message.from_id)[0]["Name"]}), курс валют на данный момент:\n'
            f'💸 Биткоин: {general.change_number(math.trunc(float(bit["ticker"]["price"])))}$')


@bot.on.message(text=["Продать", "продать"])
@bot.on.message(text=["Продать <property_name>", "продать <property_name>"])
@bot.on.message(text=["Продать <property_name> <count:int>", "продать <property_name> <count:int>"])
async def sellproperty_handler(message: Message, info: UsersUserXtrCounters, property_name: Optional[str] = None,
                               count: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        shop_data = MainData.get_shop_data()
        if property_name is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), чтобы что-то продать, используйте: "
                                 f"продать [категория]\n\n"
                                 f"Категории:\n"
                                 f"⠀🚗 машина\n"
                                 f"⠀🏍 мотоцикл"
                                 f"⠀🛥 яхта\n"
                                 f"⠀🛩 самолет\n"
                                 f"⠀🚁 вертолет\n"
                                 f"⠀🏠 дом\n"
                                 f"⠀🌇 квартира\n"
                                 f"⠀📱 телефон\n"
                                 f"⠀👑 рейтинг [кол-во]⠀⠀{general.change_number(math.trunc(MainData.get_settings()[0]['Rating_Price'] / 2))}$/ед.\n"
                                 f"⠀💼 бизнес\n"
                                 f"⠀🌐 биткоин [кол-во]⠀⠀{general.change_number(math.trunc(MainData.get_settings()[0]['BTC_USD_Curse'] / 2))}$/ед.\n"
                                 f"⠀🐸 питомец")
        elif property_name == 'машина':
            if user[1]["Car"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет машины! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[0][user[1]["Car"] - 1]["CarName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[0][user[1]["Car"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[0][user[1]["Car"] - 1]["Price"] / 2)
                user[1]["Car"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'яхта':
            if user[1]["Yacht"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет яхты! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[1][user[1]["Yacht"] - 1]["YachtName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[1][user[1]["Yacht"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[1][user[1]["Yacht"] - 1]["Price"] / 2)
                user[1]["Yacht"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'самолет':
            if user[1]["Airplane"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет самолета! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[2][user[1]["Airplane"] - 1]["AirplaneName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[2][user[1]["Airplane"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[2][user[1]["Airplane"] - 1]["Price"] / 2)
                user[1]["Airplane"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'вертолет':
            if user[1]["Helicopter"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет вертолета! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[3][user[1]["Helicopter"] - 1]["HelicopterName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[3][user[1]["Helicopter"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[3][user[1]["Helicopter"] - 1]["Price"] / 2)
                user[1]["Helicopter"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'дом':
            if user[1]["House"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет дома! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[4][user[1]["House"] - 1]["HouseName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[4][user[1]["House"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[4][user[1]["House"] - 1]["Price"] / 2)
                user[1]["House"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'квартира':
            if user[1]["Apartment"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет квартиры! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[5][user[1]["Apartment"] - 1]["ApartmentName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[5][user[1]["Apartment"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[5][user[1]["Apartment"] - 1]["Price"] / 2)
                user[1]["Apartment"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'телефон':
            if user[1]["Phone"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет телефона! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[6][user[1]["Phone"] - 1]["PhoneName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[6][user[1]["Phone"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[6][user[1]["Phone"] - 1]["Price"] / 2)
                user[1]["Phone"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'ферма':
            if count is None or count == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для продажи ферм используйте: '
                                     f'продать ферма [кол-во]')
            else:
                if user[1]["Farms"] < count:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько ферм! Для '
                                         f'покупки используйте магазин.')
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                         f'{general.change_number(count)} ферм {shop_data[7][user[1]["FarmsType"] - 1]["FarmName"]} за '
                                         f'{general.change_number(math.trunc(shop_data[7][user[1]["FarmsType"] - 1]["Price"] / 2) * count)}$')
                    user[0]["Money"] += math.trunc(shop_data[7][user[1]["FarmsType"] - 1]["Price"] / 2) * count
                    user[1]["Farms"] -= count
                    UserAction.save_user(message.from_id, user)
        elif property_name == 'рейтинг':
            if count is None or count == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для продажи рейтинга используйте: '
                                     f'продать рейтинг [кол-во]')
            else:
                if user[0]["Rating"] < count:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько рейтинга! Для '
                                         f'покупки используйте магазин.')
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                         f'{general.change_number(count)} рейтинга за '
                                         f'{general.change_number(math.trunc(MainData.get_settings()[0]["Rating_Price"] / 2) * count)}$')
                    user[0]["Money"] += math.trunc(MainData.get_settings()[0]["Rating_Price"] / 2) * count
                    user[0]["Rating"] -= count
                    UserAction.save_user(message.from_id, user)
        elif property_name == 'бизнес':
            if user[1]["Business"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет бизнеса! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[8][user[1]["Business"] - 1]["BusinessName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[8][user[1]["Business"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[8][user[1]["Business"] - 1]["Price"] / 2)
                user[0]["Money_In_Business"] = 0
                user[0]["Workers_In_Business"] = 0
                user[1]["Business"] = 0
                user[1]["BusinessLevel"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'биткоин':
            if count is None or count == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для продажи биткоина используйте: '
                                     f'продать биткоин [кол-во]')
            else:
                if user[0]["BTC"] < count:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько биткоинов! Для '
                                         f'покупки используйте магазин, или используйте фермы')
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                         f'{general.change_number(count)} биткоина(-ов) за '
                                         f'{general.change_number(math.trunc(MainData.get_settings()[0]["BTC_USD_Curse"] / 2) * count)}$')
                    user[0]["Money"] += math.trunc(MainData.get_settings()[0]["BTC_USD_Curse"] / 2) * count
                    user[0]["BTC"] -= count
                    UserAction.save_user(message.from_id, user)
        elif property_name == 'питомец':
            if user[1]["Pet"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет питомца! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[9][user[1]["Pet"] - 1]["PetName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[9][user[1]["Pet"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[9][user[1]["Pet"] - 1]["Price"] / 2)
                user[0]["Pet_Hunger"] = 0
                user[0]["Pet_Joy"] = 0
                user[1]["Pet"] = 0
                user[1]["PetLevel"] = 0
                UserAction.save_user(message.from_id, user)
        elif property_name == 'мотоцикл':
            if user[1]["Motorcycle"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет мотоцикла! Для покупки '
                                     f'используйте магазин.')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                     f'{shop_data[10][user[1]["Motorcycle"] - 1]["MotoName"]} за '
                                     f'{general.change_number(math.trunc(shop_data[10][user[1]["Motorcycle"] - 1]["Price"] / 2))}$')
                user[0]["Money"] += math.trunc(shop_data[10][user[1]["Motorcycle"] - 1]["Price"] / 2)
                user[1]["Motorcycle"] = 0
                UserAction.save_user(message.from_id, user)
        else:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), проверьте правильность введенных данных!')


@bot.on.message(text=["Репорт", "репорт"])
@bot.on.message(text=["Репорт <question>", "репорт <question>"])
async def report_handler(message: Message, info: UsersUserXtrCounters, question: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if question is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), чтобы задать вопрос, используйте: репорт '
                                 f'[вопрос]')
        else:
            MainData.add_and_update_report(Question=question, AskingID=user[0]["ID"])
            for admin in UserAction.get_admins():
                await message.answer(f'@id{admin["VK_ID"]} ({admin["Name"]}), игрок '
                                     f'@id{message.from_id}({user[0]["Name"]}) прислал репорт:\n\n'
                                     f'{question}\n\nИспользуйте: репорты', user_id=admin["VK_ID"])
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш репорт отправлен администрации.\n'
                                 f'Ожидайте ответа.')


@bot.on.message(text=["Ник", "ник"])
@bot.on.message(text=["Ник <nick>", "ник <nick>"])
async def nick_handler(message: Message, info: UsersUserXtrCounters, nick: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if nick is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: ник [никнейм]')
        else:
            if user[0]["RankLevel"] < 2:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), смена имени доступна только игрокам с '
                                     f'VIP статусом.\nИспользуйте: донат')
            else:
                user[0]["Name"] = nick
                UserAction.save_user(message.from_id, user)
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы изменили свое имя на {nick}')


@bot.on.message(text=["Брак", "брак"])
@bot.on.message(text=["Брак <partner_id>", "брак <partner_id>"])
@bot.on.message(text=["Брак <partner_id> <action>", "брак <partner_id> <action>"])
async def marriage_handler(message: Message, info: UsersUserXtrCounters, partner_id: Optional[str] = None,
                           action: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if partner_id is None or not general.isint(partner_id):
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: брак [игровой ID]')
        else:
            partner_user = UserAction.get_user_by_gameid(int(partner_id))
            if action is None:
                if partner_user is False:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), такого пользователя не существует')
                else:
                    if user[0]["Marriage_Partner"] != 0:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы уже состоите в браке')
                    elif partner_user[0]["Marriage_Partner"] != 0:
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), данный игрок уже состоит в браке')
                    else:
                        partner_user[0]["Marriage_Request"] = user[0]["ID"]
                        user[0]["Marriage_Request"] = int(partner_id)
                        UserAction.save_user(message.from_id, user)
                        UserAction.save_user(partner_user[0]["VK_ID"], partner_user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы сделали предложение игроку '
                                             f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}) 💍')
                        await message.answer(f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}), '
                                             f'игрок @id{message.from_id} ({user[0]["Name"]}) ({user[0]["ID"]}) '
                                             f'сделал Вам предложение 💍\n'
                                             f'🔎 Для принятия предложения используйте "брак [игровой ID] принять"\n'
                                             f'🔎 Для отклонения предложения используйте "брак [игровой ID] отказать"',
                                             user_id=partner_user[0]["VK_ID"])
            elif action == 'принять':
                if user[0]["Marriage_Request"] == 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет предложений брака')
                else:
                    user[0]["Marriage_Partner"] = user[0]["Marriage_Request"]
                    partner_user[0]["Marriage_Partner"] = partner_user[0]["Marriage_Request"]
                    user[0]["Marriage_Request"] = 0
                    partner_user[0]["Marriage_Request"] = 0
                    UserAction.save_user(message.from_id, user)
                    UserAction.save_user(partner_user[0]["VK_ID"], partner_user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы вступили в брак с '
                                         f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}) 💍')
                    await message.answer(f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}), игрок '
                                         f'@id{message.from_id} ({user[0]["Name"]}) принял Ваше предложение брака 💍',
                                         user_id=partner_user[0]["VK_ID"])
            elif action == "отказать":
                if user[0]["Marriage_Request"] == 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет предложений брака')
                else:
                    user[0]["Marriage_Request"] = 0
                    partner_user[0]["Marriage_Request"] = 0
                    UserAction.save_user(message.from_id, user)
                    UserAction.save_user(partner_user[0]["VK_ID"], partner_user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы отказались от брак с '
                                         f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}) 😔')
                    await message.answer(f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}), игрок '
                                         f'@id{message.from_id} ({user[0]["Name"]}) '
                                         f'отказался от Вашего предложения брака 😔',
                                         user_id=partner_user[0]["VK_ID"])


@bot.on.message(text=["Развод", "развод"])
@bot.on.message(text=["Развод <partner_id>", "развод <partner_id>"])
async def divorce_handler(message: Message, info: UsersUserXtrCounters, partner_id: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if partner_id is None or not general.isint(partner_id):
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: развод [игровой ID]')
        else:
            partner_user = UserAction.get_user_by_gameid(int(partner_id))
            if partner_user is False:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), такого пользователя не существует')
            elif user[0]["Marriage_Partner"] is not partner_user[0]["Marriage_Partner"]:
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), данный игрок не является Вашим партнером')
            elif user[0]["Marriage_Partner"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не состоите в браке')
            else:
                partner_user[0]["Marriage_Partner"] = 0
                user[0]["Marriage_Partner"] = 0
                UserAction.save_user(message.from_id, user)
                UserAction.save_user(partner_user[0]["VK_ID"], partner_user)
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы развелись с игроком '
                                     f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}) 💔')
                await message.answer(f'@id{partner_user[0]["VK_ID"]} ({partner_user[0]["Name"]}), '
                                     f'игрок @id{message.from_id} ({user[0]["Name"]}) ({user[0]["ID"]}) '
                                     f'развелся с Вами 💔\n', user_id=partner_user[0]["VK_ID"])


# Business
@bot.on.message(text=["Бизнес", "бизнес"])
@bot.on.message(text=["Бизнес <action>", "бизнес <action>"])
@bot.on.message(text=["Бизнес <action> <count>", "бизнес <action> <count>"])
async def business_handler(message: Message, info: UsersUserXtrCounters, action: Optional[str] = None,
                           count: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        businesses = MainData.get_data('businesses')
        if user[1]["Business"] == 0:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет бизнеса.\n'
                                 f'Используйте магазин для покупки')
        elif action is None:
            if user[1]["BusinessLevel"] == 1:
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), статистика вашего бизнеса «{businesses[user[1]["Business"] - 1]["BusinessName"]}»:\n'
                    f'💸 Прибыль: {general.change_number(businesses[user[1]["Business"] - 1]["MoneyPerHouse"])}$\n'
                    f'💼 Рабочих: {user[0]["Workers_In_Business"]}/{businesses[user[1]["Business"] - 1]["BusinessWorkers"]}\n'
                    f'💰 На счёте: {general.change_number(user[0]["Money_In_Business"])}$\n'
                    f'{"❌ У Вас работает мало людей. Прибыль уменьшена в 2 раза." if user[0]["Workers_In_Business"] < businesses[user[1]["Business"] - 1]["BusinessWorkers"] else ""}'
                    f'\n✅ Вы можете купить следующее улучшение за {general.change_number(math.trunc(businesses[user[1]["Business"] - 1]["Price"] * 1.75))}$')
            elif user[1]["BusinessLevel"] == 2:
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), статистика вашего бизнеса «{businesses[user[1]["Business"] - 1]["BusinessName"]}»:\n'
                    f'💸 Прибыль: {general.change_number(businesses[user[1]["Business"] - 1]["MoneyPerHouse"] * 2)}$\n'
                    f'💼 Рабочих: {user[0]["Workers_In_Business"]}/{businesses[user[1]["Business"] - 1]["BusinessWorkers"] * 2}\n'
                    f'💰 На счёте: {general.change_number(user[0]["Money_In_Business"])}$\n'
                    f'{"❌ У Вас работает мало людей. Прибыль уменьшена в 2 раза." if user[0]["Workers_In_Business"] < businesses[user[1]["Business"] - 1]["BusinessWorkers"] * 2 else ""}')
            await message.answer(f'Команды доступные для бизнеса:\n'
                                 f'бизнес улучшить\n'
                                 f'бизнес нанять [кол-во]\n'
                                 f'бизнес снять [сумма]')
        elif action == 'улучшить':
            if user[0]["Money"] < math.trunc(businesses[user[1]["Business"] - 1]["Price"] * 1.75):
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас недостаточно денег для улучшения'
                                     f' бизнеса')
            elif user[1]["BusinessLevel"] == 2:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже улучшенный бизнес')
            else:
                user[0]["Money"] -= math.trunc(businesses[user[1]["Business"] - 1]["Price"] * 1.75)
                user[1]["BusinessLevel"] = 2
                UserAction.save_user(message.from_id, user)
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы улучшили свой бизнес ⬆')
        elif action == 'нанять':
            if count is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: бизнес нанять [кол-во]')
            else:
                if user[1]["BusinessLevel"] == 1 and (
                        user[0]["Workers_In_Business"] + int(count) > businesses[user[1]["Business"] - 1][
                    "BusinessWorkers"]):
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), лимит работников бизнеса')
                elif user[1]["BusinessLevel"] == 2 and (
                        user[0]["Workers_In_Business"] + int(count) > businesses[user[1]["Business"] - 1][
                    "BusinessWorkers"] * 2):
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), лимит работников бизнеса')
                else:
                    user[0]["Workers_In_Business"] += int(count)
                    user[0]["Money"] -= math.trunc((businesses[user[1]["Business"] - 1]["Price"] * 0.0001) * int(count))
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы наняли '
                                         f'{general.change_number(int(count))} рабочих за '
                                         f'{general.change_number(math.trunc((businesses[user[1]["Business"] - 1]["Price"] * 0.0001) * int(count)))}$ ☺')
        elif action == 'снять':
            if count is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: бизнес снять [сумма]')
            else:
                if user[0]["Money_In_Business"] < int(count):
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), на счету Вашего бизнеса нет '
                                         f'столько денег')
                else:
                    user[0]["Money_In_Business"] -= int(count)
                    user[0]["Money"] += int(count)
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы сняли со счета своего бизнеса '
                                         f'{general.change_number(int(count))}$ 🤑\n')


@bot.on.message(text=["Питомец", "питомец"])
@bot.on.message(text=["Питомец <action>", "питомец <action>"])
async def pet_handler(message: Message, info: UsersUserXtrCounters, action: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        pets = MainData.get_data('pets')
        if action is None and user[1]["Pet"] == 0:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет питомца.\n'
                                 f'Вы можете найти питомца. Используйте: питомец найти\n'
                                 f'или используйте магазин для покупки')
        elif action is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), информация о Вашем питомце:\n'
                                 f'{pets[user[1]["Pet"] - 1]["PetIcon"]} Питомец: «{pets[user[1]["Pet"] - 1]["PetName"]}»\n'
                                 f'💳 Стоимость улучшения: {general.change_number(pets[user[1]["Pet"] - 1]["Price"] * (user[1]["PetLevel"] + 1))}$\n'
                                 f'💖 Радость: {user[0]["Pet_Joy"]}%\n'
                                 f'🍗 Сытость: {user[0]["Pet_Hunger"]}%\n'
                                 f'🌟 Уровень: {user[1]["PetLevel"]}\n\n'
                                 f'Команды доступные для питомца:\n'
                                 f'питомец улучшить\n'
                                 f'питомец поход')
        elif action == 'улучшить':
            if user[1]["Pet"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет питомца.\n'
                                     f'Вы можете найти питомца. Используйте: питомец найти\n'
                                     f'или используйте магазин для покупки')
            else:
                if user[0]["Money"] < pets[user[1]["Pet"] - 1]["Price"] * (user[1]["PetLevel"] + 1):
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), у Вас недостаточно денег для улучшения')
                else:
                    user[0]["Money"] -= pets[user[1]["Pet"] - 1]["Price"] * (user[1]["PetLevel"] + 1)
                    user[1]["PetLevel"] += 1
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы улучшили своего питомца ⬆')
        elif action == 'поход':
            if user[1]["Pet"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет питомца.\n'
                                     f'Вы можете найти питомца. Используйте: питомец найти\n'
                                     f'или используйте магазин для покупки')
            else:
                if user[0]["Pet_Fatigue"] > 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец устал. \n'
                                         f'Вы сможете отправить его в поход через {user[0]["Pet_Fatigue"]} минут')
                elif user[0]["Pet_Joy"] < 5:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вашего питомца нет настроения.\n'
                                         f'Поиграйте с ними, чтобы поднять ему настроение')
                elif user[0]["Pet_Hunger"] < 5:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец слишком голоден.\n'
                                         f'Вам стоит покормить его')
                else:
                    found_money = random.randint(pets[user[1]["Pet"] - 1]["PetMinMoney"],
                                                 pets[user[1]["Pet"] - 1]["PetMaxMoney"])
                    chance_loss = random.randint(1, 5)
                    if chance_loss == 1:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец потерялся в походе 😔')
                        user[0]["Pet_Fatigue"] = 0
                        user[0]["Pet_Hunger"] = 0
                        user[0]["Pet_Joy"] = 0
                        user[1]["Pet"] = 0
                        user[1]["PetLevel"] = 0
                        UserAction.save_user(message.from_id, user)
                    else:
                        user[0]["Money"] += found_money
                        user[0]["Pet_Fatigue"] = 60
                        user[0]["Pet_Joy"] -= random.randint(1, 15)
                        user[0]["Pet_Hunger"] -= random.randint(1, 15)
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец нашел в походе {general.change_number(found_money)}$')
        elif action == 'найти':
            if user[1]["Pet"] != 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть питомец')
            else:
                if user[0]["Energy"] <= 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас недостаточно энергии 😔')
                else:
                    chance_found = random.randint(0, 70)
                    if chance_found == 1:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы нашли питомца «{pets[0]["PetName"]}»')
                        user[0]["Energy"] -= 1
                        user[0]["Pet_Fatigue"] = 0
                        user[0]["Pet_Hunger"] = 0
                        user[0]["Pet_Joy"] = 0
                        user[1]["Pet"] = 1
                        user[1]["PetLevel"] = 1
                        UserAction.save_user(message.from_id, user)
                    else:
                        user[0]["Energy"] -= 1
                        UserAction.save_user(message.from_id, user)
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не смогли найти питомца 😔\n'
                                             f'💡 Ваша энергия: {user[0]["Energy"]}\n'
                                             f'Попробуйте еще раз')
        elif action == 'поиграть':
            if user[1]["Pet"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет питомца.\n'
                                     f'Вы можете найти питомца. Используйте: питомец найти\n'
                                     f'или используйте магазин для покупки')
            else:
                if user[0]["Pet_Joy"] == 100:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец и так в хорошем настроении')
                elif user[0]["Energy"] <= 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас недостаточно энергии 😔')
                else:
                    user[0]["Energy"] -= 1
                    user[0]["Pet_Joy"] = 100
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы поиграли со своим питомцем.\n'
                                         f'Теперь он в хорошем настроении и может отправляться в поход 🎉')
        elif action == 'покормить':
            if user[1]["Pet"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет питомца.\n'
                                     f'Вы можете найти питомца. Используйте: питомец найти\n'
                                     f'или используйте магазин для покупки')
            else:
                if user[0]["Pet_Hunger"] == 100:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец и так сыт')
                elif user[0]["Money"] < user[1]["PetLevel"]*3:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас недостаточно денег, чтобы '
                                         f'покормить питомца 😔')
                else:
                    user[0]["Money"] -= user[1]["PetLevel"]*3
                    user[0]["Pet_Hunger"] = 100
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы покормили своего питомца за '
                                         f'{general.change_number(user[1]["PetLevel"]*3)}$\n'
                                         f'Теперь он сыт и может отправляться в поход 🎉')


# Games
@bot.on.message(text=["Игры", "игры"])
@bot.on.message(payload={"cmd": "cmd_games"})
async def games_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои игры: \n"
                             f"🔫 Рулетка - русская рулетка\n"
                             f"🎲 Кубик [1-6]\n"
                             f"🎰 Казино [сумма]\n"
                             f"📈 Трейд [вверх/вниз] [сумма]\n"
                             f"🥛 Стаканчик [1-3] [сумма]\n"
                             f"🦅 Монетка [орёл/решка] [сумма]", keyboard=GAMES_KEYBOARD)


# Game roulette
@bot.on.message(text=["Рулетка", "рулетка"])
@bot.on.message(payload={"cmd": "game_roulette"})
async def game_roulette_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        user[0]["Roulette_Shots"] = 1
        UserAction.save_user(message.from_id, user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы начали игру в \"Русскую рулетку\" 👍\n"
                             f"🔫 Для игры введите \"выстрелить\"\n"
                             f"❌ Чтобы выйти из игры, напишет \"остановиться\"", keyboard=GAME_ROULETTE_KEYBOARD)


@bot.on.message(text=["Выстрелить", "выстрелить"])
@bot.on.message(payload={"cmd": "game_roulette_shot"})
async def game_roulette_shot_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        shot = random.randint(1, 6)
        if user[0]["Roulette_Shots"] <= 0:
            user[0]["Roulette_Shots"] = 1
            UserAction.save_user(message.from_id, user)
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы начали игру в \"Русскую рулетку\" 👍\n'
                                 f'🔫 Для игры введите \"выстрелить\"\n'
                                 f'❌ Чтобы выйти из игры, напишет \"остановиться\"', keyboard=GAME_ROULETTE_KEYBOARD)
        else:
            if shot == 1 and user[0]["Roulette_Shots"] > 0:
                if user[0]["Money"] >= 800:
                    heal_money = random.randint(1, 8) * 100
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы выстрелили на '
                                         f'{user[0]["Roulette_Shots"]}-й попытке ☹\n'
                                         f'💸 Ваш выигрыш: {general.change_number(user[0]["Roulette_Shots"] * 100)}$\n'
                                         f'❤ На лечение потрачено: {general.change_number(heal_money)}$',
                                         keyboard=GAME_ROULETTE_KEYBOARD)
                    user[0]["Money"] -= heal_money
                    user[0]["Money"] += user[0]["Roulette_Shots"] * 100
                    user[0]["Roulette_Shots"] = 0
                    UserAction.save_user(message.from_id, user)
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы выстрелили на '
                                         f'{user[0]["Roulette_Shots"]}-й попытке ☹\n'
                                         f'💸 Ваш выигрыш: {general.change_number(user[0]["Roulette_Shots"] * 100)}$',
                                         keyboard=GAME_ROULETTE_KEYBOARD)
                    user[0]["Money"] += user[0]["Roulette_Shots"] * 100
                    user[0]["Roulette_Shots"] = 0
                    UserAction.save_user(message.from_id, user)
            else:
                user[0]["Roulette_Shots"] += 1
                UserAction.save_user(message.from_id, user)
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы сделали '
                                     f'{user[0]["Roulette_Shots"] - 1}-ю осечку', keyboard=GAME_ROULETTE_KEYBOARD)


@bot.on.message(text=["Остановиться", "остановиться"])
@bot.on.message(payload={"cmd": "game_roulette_stop"})
async def game_roulette_shot_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if user[0]["Roulette_Shots"] - 1 <= 0:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не играли в \"Русскую рулетку\"\n'
                                 f'🔫 Для начала игры введите \"рулетка\"\n', keyboard=GAMES_KEYBOARD)
        else:
            if user[0]["Roulette_Shots"] - 1 > 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы остановилсь на '
                                     f'{user[0]["Roulette_Shots"]}-й попытке 👍\n'
                                     f'💸 Ваш выигрыш: {general.change_number(user[0]["Roulette_Shots"] * 100)}$',
                                     keyboard=GAMES_KEYBOARD)
                user[0]["Money"] += user[0]["Roulette_Shots"] * 100
                user[0]["Roulette_Shots"] = 0
                UserAction.save_user(message.from_id, user)


# Game cube
@bot.on.message(text=["Кубик", "кубик"])
@bot.on.message(payload={"cmd": "game_cube"})
async def game_cube_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), Вы начали игру в \"Кубик\" 👍\n"
            f"🎲 Для игры в кубик выбирайте числа от 1 до 6\n", keyboard=GAME_CUBE_KEYBOARD)


@bot.on.message(payload={"cmd": "game_cube_1"})
@bot.on.message(payload={"cmd": "game_cube_2"})
@bot.on.message(payload={"cmd": "game_cube_3"})
@bot.on.message(payload={"cmd": "game_cube_4"})
@bot.on.message(payload={"cmd": "game_cube_5"})
@bot.on.message(payload={"cmd": "game_cube_6"})
async def game_cube_number_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        temp_number = message.payload.split('{"cmd":"game_cube_')[1].split('"}')[0]
        cube_temp = random.randint(1, 6)
        cube_prize = random.randint(2, 50) * 50
        if cube_temp == int(temp_number):
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы угадали 🎉\n'
                                 f'🎲 Выпало число: {cube_temp}\n'
                                 f'💸 Ваш выигрыш: {general.change_number(cube_prize)}$', keyboard=GAME_CUBE_KEYBOARD)
            user[0]["Money"] += cube_prize
            UserAction.save_user(message.from_id, user)
        else:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не угадали 😟\n'
                                 f'🎲 Выпало число: {cube_temp}', keyboard=GAME_CUBE_KEYBOARD)


# Game coin
@bot.on.message(text=["Монетка", "монетка"])
@bot.on.message(payload={"cmd": "game_coin"})
async def game_cube_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), Вы начали игру в \"Монетка\" 👍\n"
            f"🦅 Для игры в кубик выбирайте \"Орел\" или \"Решка\"\n", keyboard=GAME_COIN_KEYBOARD)


@bot.on.message(payload={"cmd": "game_coin_1"})
@bot.on.message(payload={"cmd": "game_coin_2"})
async def game_cube_number_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        temp_number = message.payload.split('{"cmd":"game_coin_')[1].split('"}')[0]
        coin_temp = random.randint(1, 2)
        coin_prize = random.randint(2, 25) * 50
        if coin_temp == int(temp_number):
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы угадали 🎉\n'
                                 f'🦅 Выпало: {"орел" if coin_temp == 1 else "решка"}\n'
                                 f'💸 Ваш выигрыш: {general.change_number(coin_prize)}$', keyboard=GAME_COIN_KEYBOARD)
            user[0]["Money"] += coin_prize
            UserAction.save_user(message.from_id, user)
        else:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не угадали 😟\n'
                                 f'🦅 Выпало: {"орел" if coin_temp == 1 else "решка"}', keyboard=GAME_COIN_KEYBOARD)


# Game cup
@bot.on.message(text=["Стаканчик <cupnumber:int> <money:int>", "стаканчик <cupnumber:int> <money:int>"])
@bot.on.message(payload={"cmd": "game_cup"})
async def game_cup_handler(message: Message, info: UsersUserXtrCounters, cupnumber: Optional[int] = None,
                           money: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if cupnumber is None or money is None or cupnumber > 3:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), для игры в \"Стаканчик\"\n"
                                 f"Используйте: стаканчик [1-3] [ставка]")
        else:
            user = UserAction.get_user(message.from_id)
            cup_temp = random.randint(1, 3)
            if cup_temp == cupnumber:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы угадали 🎉\n'
                                     f'💸 Ваш выигрыш: {general.change_number(math.trunc(money / 2))}$')
                user[0]["Money"] += math.trunc(money / 2)
                UserAction.save_user(message.from_id, user)
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не угадали 😟\n'
                                     f'🥛 это был {cup_temp}-й стаканчик')
                user[0]["Money"] -= money
                UserAction.save_user(message.from_id, user)


# Game trade
@bot.on.message(text=["Трейд <change> <money:int>", "трейд <change> <money:int>"])
@bot.on.message(payload={"cmd": "game_trade"})
async def game_trade_handler(message: Message, info: UsersUserXtrCounters, change: Optional[str] = None,
                             money: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if change is None or money is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), для игры в \"Трейд\"\n"
                                 f"Используйте: трейд [вверх/вниз] [ставка]")
        else:
            trade_temp = random.randint(1, 5)
            trade_course = random.randint(1, 1000)
            if change == 'вверх':
                if trade_temp == 1:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), курс подорожал ⤴ на '
                                         f'{general.change_number(trade_course)}$\n'
                                         f'💸 Вы заработали: {general.change_number(money)}$ 😎')
                    user[0]["Money"] += money
                    UserAction.save_user(message.from_id, user)
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), курс подешевел ⤵ на '
                                         f'{general.change_number(trade_course)}$\n'
                                         f'💸 Вы потеряли: {general.change_number(money)}$ 😔')
                    user[0]["Money"] -= money
                    UserAction.save_user(message.from_id, user)
            elif change == 'вниз':
                if trade_temp == 1:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), курс подешевел ⤵ на '
                                         f'{general.change_number(trade_course)}$\n'
                                         f'💸 Вы заработали: {general.change_number(money)}$ 😎')
                    user[0]["Money"] += money
                    UserAction.save_user(message.from_id, user)
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), курс подорожал ⤴ на '
                                         f'{general.change_number(trade_course)}$\n'
                                         f'💸 Вы потеряли: {general.change_number(money)}$ 😔')
                    user[0]["Money"] -= money
                    UserAction.save_user(message.from_id, user)
            else:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), для игры в \"Трейд\"\n"
                                     f"Используйте: трейд [вверх/вниз] [ставка]")


# Game trade
@bot.on.message(text=["Казино <money:int>", "казино <money:int>"])
@bot.on.message(payload={"cmd": "game_casino"})
async def game_casino_handler(message: Message, info: UsersUserXtrCounters, money: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if money is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), для игры в \"Казино\"\n"
                                 f"Используйте: казино [ставка]")
        else:
            casino_temp = random.choice([0, 0.5, 2, 5, 10])
            if casino_temp == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам выпал коэффициент {casino_temp}\n'
                                     f'💸 Вы потеряли {general.change_number(money * casino_temp)}$')
                user[0]["Money"] += money * casino_temp
                UserAction.save_user(message.from_id, user)
            elif casino_temp == 0.5:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам выпал коэффициент {casino_temp}\n'
                                     f'💸 Вы заработали: {general.change_number(math.trunc(money * casino_temp))}$')
                user[0]["Money"] += money * casino_temp
                UserAction.save_user(message.from_id, user)
            elif casino_temp == 2:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам выпал коэффициент {casino_temp}\n'
                                     f'💸 Вы заработали: {general.change_number(money * casino_temp)}$')
                user[0]["Money"] += money * casino_temp
                UserAction.save_user(message.from_id, user)
            elif casino_temp == 5:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам выпал коэффициент {casino_temp}\n'
                                     f'💸 Вы заработали: {general.change_number(money * casino_temp)}$')
                user[0]["Money"] += money * casino_temp
                UserAction.save_user(message.from_id, user)
            elif casino_temp == 10:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам выпал коэффициент {casino_temp}\n'
                                     f'💸 Вы заработали: {general.change_number(money * casino_temp)}$')
                user[0]["Money"] += money * casino_temp
                UserAction.save_user(message.from_id, user)
            else:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), для игры в \"Казино\"\n"
                                     f"Используйте: казино [ставка]")


# Menu commands
@bot.on.message(text=["Разное", "разное"])
@bot.on.message(payload={"cmd": "cmd_other"})
async def other_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), раздел \"Разное\" 💡",
            keyboard=OTHER_KEYBOARD)


@bot.on.message(payload={"cmd": "cmd_mainmenu"})
async def other_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), раздел \"Главное меню\" 💡",
            keyboard=MAIN_KEYBOARD)


# Farms commands
@bot.on.message(text=["Ферма", "ферма"])
@bot.on.message(text=["Ферма <action>", "ферма <action>"])
@bot.on.message(payload={"cmd": "cmd_farm"})
async def farm_handler(message: Message, info: UsersUserXtrCounters, action: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if action is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), на Ваших фермах '
                                 f'{general.change_number(user[0]["BTC_In_Farms"])}₿\n'
                                 f'🔎 Для сбора биткоинов используйте: "ферма собрать"')
        elif action == 'собрать':
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы собрали '
                                 f'{general.change_number(user[0]["BTC_In_Farms"])}₿ с ваших ферм\n'
                                 f'🔎 Для продажи биткоинов используйте: "продать биткоин [кол-во]"')
            user[0]["BTC"] += user[0]["BTC_In_Farms"]
            user[0]["BTC_In_Farms"] = 0
            UserAction.save_user(message.from_id, user)
        else:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), проверьте правильность введенных данных!')


# Case commands
@bot.on.message(text=["Кейсы", "кейсы"])
@bot.on.message(text=["Кейсы <case_type>", "кейсы <case_type>"])
@bot.on.message(text=["Кейсы <case_type> <action>", "кейсы <case_type> <action>"])
async def cases_handler(message: Message, info: UsersUserXtrCounters, case_type: Optional[int] = None,
                        action: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if case_type is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваши кейсы:\n'
                                 f'🥉 Bronze Case {general.change_number(user[0]["Bronze_Case"])} шт.\n'
                                 f'🥈 Silver Case {general.change_number(user[0]["Silver_Case"])} шт.\n'
                                 f'🥇 Gold Case {general.change_number(user[0]["Gold_Case"])} шт.\n'
                                 f'🥇 Premium Case {general.change_number(user[0]["Premium_Case"])} шт.\n\n'
                                 f'Команды доступные для кейсов:\n'
                                 f'кейсы [тип кейса (bronze, silver, gold, premium)] открыть')
        elif case_type == 'bronze':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '
                                     f'{general.change_number(user[0]["Bronze_Case"])} 🥉 Bronze Case\n\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы bronze открыть')
            elif action == 'открыть':
                if user[0]["Bronze_Case"] < 1:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Bronze Case 😔\n'
                                         f'Для покупки, используйте: магазин кейсы')
                else:
                    user[0]["Bronze_Case"] -= 1
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Bronze Case 🎉\n'
                                         f'Ваш приз: ')
        elif case_type == 'silver':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '
                                     f'{general.change_number(user[0]["Silver_Case"])} 🥈 Silver Case\n\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы silver открыть')
            elif action == 'открыть':
                if user[0]["Silver_Case"] < 1:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Silver Case 😔\n'
                                         f'Для покупки, используйте: магазин кейсы')
                else:
                    user[0]["Silver_Case"] -= 1
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Silver Case 🎉\n'
                                         f'Ваш приз: ')
        elif case_type == 'gold':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '
                                     f'{general.change_number(user[0]["Gold_Case"])} 🥇 Gold Case\n\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы gold открыть')
            elif action == 'открыть':
                if user[0]["Gold_Case"] < 1:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Gold Case 😔\n'
                                         f'Для покупки, используйте: магазин кейсы')
                else:
                    user[0]["Gold_Case"] -= 1
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Gold Case 🎉\n'
                                         f'Ваш приз: ')
        elif case_type == 'premium':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '                                     
                                     f'{general.change_number(user[0]["Premium_Case"])} 🥇 Premium Case\n\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы premium открыть')
            elif action == 'открыть':
                if user[0]["Premium_Case"] < 1:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Premium Case 😔\n'
                                         f'Для покупки, используйте: донат')
                else:
                    user[0]["Premium_Case"] -= 1
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Premium Case 🎉\n'
                                         f'Ваш приз: ')


# Admin commands
@bot.on.message(text=["Админпомощь", "админпомощь", "ahelp"])
@bot.on.message(payload={"cmd": "cmd_ahelp"})
async def admin_ahelp_handler(message: Message, info: UsersUserXtrCounters):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    elif user[0]["RankLevel"] == 4:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), команды модератора:\n"
            f"⠀1. отв [ID репорта] [ответ] - ответить на жалобу\n"
            f"⠀2. setnick [ID] [ник] - изменить игроку ник\n"
            f"⠀3. лник [ID] - включить/выключить игроку длинный ник\n"
            f"⠀4. log [ID] - скачать лог игрока\n"
            f"⠀5. getbaninfo [ID] - узнать информацию о бане игрока\n"
            f"⠀6. get [ID] - узнать информацию об игроке\n"
            f"⠀7. банреп [ID] - запретить/разрешить игроку писать в репорт\n"
            f"⠀8. тбан [ID] - заблокировать/разблокировать игроку топ\n"
            f"⠀9. пбан [ID] - запретить/разрешить игроку передавать деньги\n"
            f"⠀10. разбан [ID] - разблокировать игрока\n"
            f"⠀11. бан [ID] [время]с/м/ч/д [причина] - заблокировать игрока\n"
            f"⠀12. статистика - общая статистика бота\n"
            f"⠀13. getid [ссылка] - узнать игровой ID игрока")
    elif user[0]["RankLevel"] == 5:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), команды модератора:\n"
            f"⠀1. отв [ID репорта] [ответ] - ответить на жалобу\n"
            f"⠀2. setnick [ID] [ник] - изменить игроку ник\n"
            f"⠀3. лник [ID] - включить/выключить игроку длинный ник\n"
            f"⠀4. log [ID] - скачать лог игрока\n"
            f"⠀5. getbaninfo [ID] - узнать информацию о бане игрока\n"
            f"⠀6. get [ID] - узнать информацию об игроке\n"
            f"⠀7. банреп [ID] - запретить/разрешить игроку писать в репорт\n"
            f"⠀8. тбан [ID] - заблокировать/разблокировать игроку топ\n"
            f"⠀9. пбан [ID] - запретить/разрешить игроку передавать деньги\n"
            f"⠀10. разбан [ID] - разблокировать игрока\n"
            f"⠀11. бан [ID] [время]с/м/ч/д [причина] - заблокировать игрока\n"
            f"⠀12. статистика - общая статистика бота\n"
            f"⠀13. getid [ссылка] - узнать игровой ID игрока\n"
            f"⠀\nКоманды администратора:\n"
            f"⠀1. выдать [ID] деньги/рейтинг/биткоины/опыт [кол-во]\n"
            f"⠀2. измимущество [ID] "
            f"бизнес/питомец/телефон/квартира/дом/вертолёт/самолёт/машина/ферма/яхта [название]\n "
            f"⠀3. replace [ID] переменная [значение]\n"
            f"⠀Основные значения для replace:\n"
            f"⠀- balance - деньги на руках\n"
            f"⠀- bank - деньги в банке\n"
            f"⠀- rating - рейтинг\n"
            f"⠀- farms - количество ферм")
    elif user[0]["RankLevel"] > 5:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), команды модератора:\n"
            f"⠀1. отв [ID репорта] [ответ] - ответить на жалобу\n"
            f"⠀2. setnick [ID] [ник] - изменить игроку ник\n"
            f"⠀3. лник [ID] - включить/выключить игроку длинный ник\n"
            f"⠀4. log [ID] - скачать лог игрока\n"
            f"⠀5. getbaninfo [ID] - узнать информацию о бане игрока\n"
            f"⠀6. get [ID] - узнать информацию об игроке\n"
            f"⠀7. банреп [ID] - запретить/разрешить игроку писать в репорт\n"
            f"⠀8. тбан [ID] - заблокировать/разблокировать игроку топ\n"
            f"⠀9. пбан [ID] - запретить/разрешить игроку передавать деньги\n"
            f"⠀10. разбан [ID] - разблокировать игрока\n"
            f"⠀11. бан [ID] [время]с/м/ч/д [причина] - заблокировать игрока\n"
            f"⠀12. статистика - общая статистика бота\n"
            f"⠀13. getid [ссылка] - узнать игровой ID игрока\n"
            f"\nКоманды администратора:\n"
            f"⠀1. выдать [ID] деньги/рейтинг/биткоины/опыт [кол-во]\n"
            f"⠀2. измимущество [ID] "
            f"бизнес/питомец/телефон/квартира/дом/вертолёт/самолёт/машина/ферма/яхта [название]\n "
            f"⠀3. replace [ID] переменная [значение]\n"
            f"⠀4. @sendtext [сообщение] - рассылка текстового сообщения\n"
            f"⠀5. @sendwall [ID поста] - рыссылка поста\n"
            f"\nКоманды основателя:\n"
            f"⠀1. add_property [тип] - добавить имущество в бота\n"
            f"⠀2. измранг [ID] [значение] - именить статус игрока\n"
            f"\nПараметры для add_property:\n"
            f"⠀машина - [название] [цена]\n"
            f"⠀яхта - [название] [цена]\n"
            f"⠀самолет - [название] [цена]\n"
            f"⠀вертолет - [название] [цена]\n"
            f"⠀дом - [название] [цена]\n"
            f"⠀квартира - [название] [цена]\n"
            f"⠀бизнес - [название] [цена] [кол-во рабочих]\n"
            f"⠀питомец - [название] [цена] [мин кол-во добычи] [макс кол-во добычи] [иконка]\n"
            f"⠀ферма - [название] [цена] [кол-во биткоинов в час]\n"
            f"⠀телефон - [название] [цена]\n"
            f"\nОсновные значения для replace:\n"
            f"⠀- balance - деньги на руках\n"
            f"⠀- bank - деньги в банке\n"
            f"⠀- rating - рейтинг\n"
            f"⠀- farms - количество ферм\n"
            f"\nСтатусы:\n"
            f"⠀1 - обычный игрок\n"
            f"⠀2 - VIP\n"
            f"⠀3 - Premium\n"
            f"⠀4 - Модератор\n"
            f"⠀5 - Администратор")


@bot.on.message(text=["add_property"])
@bot.on.message(text=["add_property <property_type>"])
@bot.on.message(text=["add_property <property_type> \"<name>\""])
@bot.on.message(text=["add_property <property_type> \"<name>\" <price:int>"])
@bot.on.message(text=["add_property <property_type> \"<name>\" <price:int> <param1:int>"])
@bot.on.message(text=["add_property <property_type> \"<name>\" <price:int> <param1:int> <param2:int> <param3>"])
@bot.on.message(payload={"cmd": "cmd_add_property"})
async def admin_add_property_handler(message: Message, info: UsersUserXtrCounters, property_type: Optional[str] = None,
                                     name: Optional[str] = None, price: Optional[int] = None,
                                     param1: Optional[int] = None,
                                     param2: Optional[int] = None, param3: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 6:
        return True
    elif property_type is None:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property [тип]'")
    elif property_type == "машина":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property машина ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("cars", CarName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новый автомобиль "
                                 f"{name} с ценой {general.change_number(price)}$")
    elif property_type == "мотоцикл":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property мотоцикл ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("motorcycles", MotoName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новый мотоцикл "
                                 f"{name} с ценой {general.change_number(price)}$")
    elif property_type == "яхта":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property яхта ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("yachts", YachtName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новую яхту "
                                 f"{name} с ценой {general.change_number(price)}$")
    elif property_type == "самолет":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property самолет ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("airplanes", AirplaneName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новый самолет "
                                 f"{name} с ценой {general.change_number(price)}$")
    elif property_type == "вертолет":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property вертолет ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("helicopters", HelicopterName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новый вертолет "
                                 f"{name} с ценой {general.change_number(price)}$")
    elif property_type == "дом":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property дом ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("houses", HouseName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новый дом "
                                 f"{name} с ценой {general.change_number(price)}$")
    elif property_type == "квартира":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property квартира ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("apartments", ApartmentName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новую квартиру "
                                 f"{name} с ценой {general.change_number(price)}$")
    elif property_type == "бизнес":
        if name is None or price is None or param1 is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property бизнес ["
                                 f"название] [цена] [кол-во рабочих]'")
        else:
            MainData.add_business(BusinessName=name, Price=price, BusinessWorkers=param1)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новый бизнес "
                                 f"{name} с ценой {general.change_number(price)}$ и максимальным количеством рабочих "
                                 f"{param1}")
    elif property_type == "питомец":
        if name is None or price is None or param1 is None or param2 is None or param3 is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property питомец ["
                                 f"название] [цена] [мин кол-во добычи] [макс кол-во добычи] [иконка]'")
        else:
            MainData.add_pet(PetName=name, Price=price, PetMinMoney=param1, PetMaxMoney=param2, PetIcon=param3)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили нового питомца "
                                 f"{name} с ценой {general.change_number(price)}$, минимальной добычей {param1}, "
                                 f"максимальной добычей {param2}"
                                 f" и иконкой {param3}")
    elif property_type == "ферма":
        if name is None or price is None or param1 is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property ферма ["
                                 f"название] [цена] [кол-во биткоинов в час]'")
        else:
            MainData.add_farm(FarmName=name, Price=price, FarmBTCPerHour=param1)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новую ферму "
                                 f"{name} с ценой {general.change_number(price)}$ и количеством биткоинов в час "
                                 f"{param1}")
    elif property_type == "телефон":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property телефон ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("phones", PhoneName=name, Price=price)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы успешно добавили новый телефон "
                                 f"{name} с ценой {general.change_number(price)}$")
    else:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), проверьте правильность введенных данных!")


@bot.on.message(text=["Репорты", "репорты"])
@bot.on.message(text=["Репорты <action> <report_id> <answer>", "репорты <action> <report_id> <answer>"])
async def admin_report_handler(message: Message, info: UsersUserXtrCounters, action: Optional[str] = None,
                               report_id: Optional[int] = None, answer: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    else:
        reports = MainData.get_reports()
        if reports is False:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), репрортов пока что нет')
        else:
            if action is None:
                temp_message = ''
                for report in reports:
                    if report["Answer"] is not None:
                        continue
                    else:
                        temp_message += f'\n✉ {report["ID"]}. {report["Question"]} ' \
                                        f'[{UserAction.get_user_by_gameid(report["AskingID"])[0]["Name"]} ({report["AskingID"]})]'
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), неотвеченные репорты: {temp_message}\n\n '
                    f'❓ Для ответа введите "репорты ответить [ID репорта] [ответ]"')
            elif action == "ответить":
                if report_id is None or answer is None:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: '
                                         f'"репорты ответить [ID репорта] [ответ]"')
                else:
                    answering_user = UserAction.get_user_by_gameid(reports[int(report_id) - 1]["AskingID"])
                    MainData.add_and_update_report(Answer=answer, AnsweringID=user[0]["ID"], ReportID=int(report_id))
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш ответ отправлен игроку')
                    await message.answer(
                        f'@id{answering_user[0]["VK_ID"]} ({answering_user[0]["Name"]}), администратор '
                        f'{user[0]["ID"]} ответил Вам:\n\n'
                        f'{answer}\n\nБлагодарим за ожидание!', user_id=answering_user[0]["VK_ID"])
            else:
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), проверьте правильность введенных данных!')


# noinspection PyTypeChecker
@bot.on.raw_event(GroupEventType.GROUP_JOIN, dataclass=GroupTypes.GroupJoin)
async def group_join_handler(event: GroupTypes.GroupJoin):
    await bot.api.messages.send(peer_id=event.object.user_id, message="Спасибо за подписку!", random_id=0,
                                keyboard=START_KEYBOARD)


bot.labeler.message_view.register_middleware(NoBotMiddleware())
bot.labeler.message_view.register_middleware(RegistrationMiddleware())
bot.labeler.message_view.register_middleware(InfoMiddleware())
bot.run_forever()
