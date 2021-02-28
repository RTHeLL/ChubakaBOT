import asyncio
import configparser
import logging
import random
from threading import Thread

import time
from datetime import date

import math
import requests
from typing import Optional, Any, List

# Import VKBottle
from vkbottle import GroupEventType, GroupTypes, Keyboard, ABCHandler, ABCView, \
    BaseMiddleware, VKAPIError, \
    CtxStorage, Text, EMPTY_KEYBOARD
from vkbottle.bot import Bot, Message, rules
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
CodeError = VKAPIError

# Logs settings
logging.basicConfig(filename="logs/logs.log")
logging.basicConfig(level=logging.INFO)

# Tokens
bot = Bot(config["VK_DATA"]["GROUP_TOKEN"])
widget = Bot(config["VK_DATA"]["WIDGET_TOKEN"])

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
            {"label": "📦 Кейсы", "type": "text", "payload": {"cmd": "cmd_shop_other_cases"}, "color": "secondary"},
            {"label": "🍹 Зелья", "type": "text", "payload": {"cmd": "cmd_shop_other_potion"}, "color": "secondary"}
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

HELP_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "🎉 Развлекательные", "type": "text", "payload": {"cmd": "cmd_help_category_funny"},
             "color": "secondary"},
            {"label": "💼 Бизнес", "type": "text", "payload": {"cmd": "cmd_help_category_business"},
             "color": "secondary"},
            {"label": "🌽 Питомцы", "type": "text", "payload": {"cmd": "cmd_help_category_pet"}, "color": "secondary"}
        ],
        [
            {"label": "🚀 Игры", "type": "text", "payload": {"cmd": "cmd_help_category_games"}, "color": "secondary"},
            {"label": "🔥 Полезное", "type": "text", "payload": {"cmd": "cmd_help_category_useful"},
             "color": "secondary"},
            {"label": "🔦 Добыча", "type": "text", "payload": {"cmd": "cmd_help_category_mining"}, "color": "secondary"}
        ],
        [
            {"label": "💡 Разное", "type": "text", "payload": {"cmd": "cmd_help_category_other"}, "color": "secondary"},
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


@bot.on.chat_message(rules.ChatActionRule("chat_invite_user"))
async def test_invite_handler(message: Message, info: UsersUserXtrCounters):
    chats = {ID["ChatID"] for ID in MainData.get_chats()}
    if message.chat_id not in chats:
        MainData.add_chat(ChatID=message.chat_id)
        await message.answer(f'Всем привет, я Чубака!\n'
                             f'Напишите "помощь", чтобы узнать мои команды', keyboard=EMPTY_KEYBOARD)
    else:
        await message.answer(f'Всем привет, я Чубака!\n'
                             f'Напишите "помощь", чтобы узнать мои команды', keyboard=EMPTY_KEYBOARD)


# User commandsMessageEvent
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
@bot.on.message(text=["Помощь <param>", "помощь <param>"])
@bot.on.message(payload={"cmd": "cmd_help"})
async def help_handler(message: Message, info: UsersUserXtrCounters, param: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if param is None:
            if message.chat_id in chats:
                await message.answer(
                    f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), разделы:\n"
                    f"🎉 Развлекательные\n"
                    f"💼 Бизнес\n"
                    f"🌽 Питомцы\n"
                    f"🚀 Игры\n"
                    f"🔥 Полезное\n"
                    f"🔦 Добыча\n"
                    f"💡 Разное\n"
                    f"🆘 Репорт [фраза] - ошибки или пожелания\n\n"
                    f"🔎 Для просмотра команд в разделе используйте \"помощь [раздел]\"",
                    keyboard=Keyboard(one_time=False, inline=True).schema(
                        [
                            [
                                {"label": "🎉 Развлекательные", "type": "text",
                                 "payload": {"cmd": "cmd_help_category_funny"}, "color": "secondary"},
                                {"label": "💼 Бизнес", "type": "text", "payload": {"cmd": "cmd_help_category_business"},
                                 "color": "secondary"},
                                {"label": "🌽 Питомцы", "type": "text", "payload": {"cmd": "cmd_help_category_pet"},
                                 "color": "secondary"}
                            ],
                            [
                                {"label": "🚀 Игры", "type": "text", "payload": {"cmd": "cmd_help_category_games"},
                                 "color": "secondary"},
                                {"label": "🔥 Полезное", "type": "text", "payload": {"cmd": "cmd_help_category_useful"},
                                 "color": "secondary"},
                                {"label": "🔦 Добыча", "type": "text", "payload": {"cmd": "cmd_help_category_mining"},
                                 "color": "secondary"}
                            ],
                            [
                                {"label": "💡 Разное", "type": "text", "payload": {"cmd": "cmd_help_category_other"},
                                 "color": "secondary"},
                                {"label": "◀ В главное меню", "type": "text", "payload": {"cmd": "cmd_mainmenu"},
                                 "color": "positive"}
                            ]
                        ]
                    ).get_json())
            else:
                await message.answer(
                    f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), разделы:\n"
                    f"🎉 Развлекательные\n"
                    f"💼 Бизнес\n"
                    f"🌽 Питомцы\n"
                    f"🚀 Игры\n"
                    f"🔥 Полезное\n"
                    f"🔦 Добыча\n"
                    f"💡 Разное\n"
                    f"🆘 Репорт [фраза] - ошибки или пожелания\n\n"
                    f"🔎 Для просмотра команд в разделе используйте \"помощь [раздел]\"", keyboard=HELP_KEYBOARD)
        elif param.lower() == 'развлекательные':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🎉 Развлекательные:\n"
                f"⠀⠀↪ Переверни [фраза]\n"
                f"⠀⠀🔮 Шар [фраза]\n"
                f"⠀⠀📊 Инфа [фраза]\n"
                f"⠀⠀📠 Реши [пример]\n"
                f"⠀⠀⚖ Выбери [фраза] или [фраза2]")
        elif param.lower() == 'бизнес':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"💼 Бизнес:\n"
                f"⠀⠀📈 Бизнес\n"
                f"⠀⠀💵 Бизнес снять [сумма]\n"
                f"⠀⠀👷 Бизнес нанять [кол-во]\n"
                f"⠀⠀✅ Бизнес улучшить")
        elif param.lower() == 'питомцы':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🌽 Питомцы:\n"
                f"⠀⠀🐒 Питомец\n"
                f"⠀⠀🐪 Питомец поход\n"
                f"⠀⠀🌟 Питомец улучшить")
        elif param.lower() == 'игры':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🚀 Игры:\n"
                f"⠀⠀🎲 Кубик\n"
                f"⠀⠀🎰 Казино [ставка]\n"
                f"⠀⠀📈 Трейд [вверх/вниз] [ставка]\n"
                f"⠀⠀🥛 Стаканчик [1-3] [ставка]\n"
                f"⠀⠀🦅 Монетка")
        elif param.lower() == 'полезное':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🔥 Полезное:\n"
                f"⠀⠀📒 Профиль\n"
                f"⠀⠀🛍 Магазин\n"
                f"⠀⠀💲 Баланс\n"
                f"⠀⠀💰 Банк\n"
                f"⠀⠀📦 Кейсы\n"
                f"⠀⠀🔋 Ферма\n"
                f"⠀⠀📊 Курс\n"
                f"⠀⠀🎁 Бонус")
        elif param.lower() == 'добыча':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🔦 Добыча:\n"
                f"⠀⠀🥈 Добывать железо\n"
                f"⠀⠀🏅 Добывать золото\n"
                f"⠀⠀💎 Добывать алмазы\n"
                f"⠀⠀🎆 Добывать материю")
        elif param.lower() == 'разное':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"💡 Разное:\n"
                f"⠀⠀⚔ Клан\n"
                f"⠀⠀🍹 Зелья\n"
                f"⠀⠀👑 Рейтинг - ваш рейтинг\n"
                f"⠀⠀🏆 Топ\n"
                f"⠀⠀💖 Брак\n"
                f"⠀⠀💔 Развод\n"
                f"⠀⠀✒ Ник [имя]\n"
                f"⠀⠀💸 Продать [предмет]\n"
                f"⠀⠀🤝 Передать [ID] [сумма]\n"
                f"⠀⠀👥 Реф\n"
                f"⠀⠀🏆 Реф топ\n"
                f"⠀⠀🎁 Донат")


# Help keyboard
@bot.on.message(payload={"cmd": "cmd_help_category_funny"})
@bot.on.message(payload={"cmd": "cmd_help_category_business"})
@bot.on.message(payload={"cmd": "cmd_help_category_pet"})
@bot.on.message(payload={"cmd": "cmd_help_category_games"})
@bot.on.message(payload={"cmd": "cmd_help_category_useful"})
@bot.on.message(payload={"cmd": "cmd_help_category_mining"})
@bot.on.message(payload={"cmd": "cmd_help_category_other"})
async def help_categories_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        help_category = message.payload.split('{"cmd":"cmd_help_category_')[1].split('"}')[0]
        if help_category == 'funny':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🎉 Развлекательные:\n"
                f"⠀⠀↪ Переверни [фраза]\n"
                f"⠀⠀🔮 Шар [фраза]\n"
                f"⠀⠀📊 Инфа [фраза]\n"
                f"⠀⠀📠 Реши [пример]\n"
                f"⠀⠀⚖ Выбери [фраза] или [фраза2]")
        elif help_category == 'business':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"💼 Бизнес:\n"
                f"⠀⠀📈 Бизнес\n"
                f"⠀⠀💵 Бизнес снять [сумма]\n"
                f"⠀⠀👷 Бизнес нанять [кол-во]\n"
                f"⠀⠀✅ Бизнес улучшить")
        elif help_category == 'pet':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🌽 Питомцы:\n"
                f"⠀⠀🐒 Питомец\n"
                f"⠀⠀🐪 Питомец поход\n"
                f"⠀⠀🌟 Питомец улучшить")
        elif help_category == 'games':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🚀 Игры:\n"
                f"⠀⠀🎲 Кубик\n"
                f"⠀⠀🎰 Казино [ставка]\n"
                f"⠀⠀📈 Трейд [вверх/вниз] [ставка]\n"
                f"⠀⠀🥛 Стаканчик [1-3] [ставка]\n"
                f"⠀⠀🦅 Монетка")
        elif help_category == 'useful':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🔥 Полезное:\n"
                f"⠀⠀📒 Профиль\n"
                f"⠀⠀🛍 Магазин\n"
                f"⠀⠀💲 Баланс\n"
                f"⠀⠀💰 Банк\n"
                f"⠀⠀📦 Кейсы\n"
                f"⠀⠀🔋 Ферма\n"
                f"⠀⠀📊 Курс\n"
                f"⠀⠀🎁 Бонус")
        elif help_category == 'mining':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"🔦 Добыча:\n"
                f"⠀⠀🥈 Добывать железо\n"
                f"⠀⠀🏅 Добывать золото\n"
                f"⠀⠀💎 Добывать алмазы\n"
                f"⠀⠀🎆 Добывать материю")
        elif help_category == 'other':
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои команды:\n"
                f"💡 Разное:\n"
                f"⠀⠀⚔ Клан\n"
                f"⠀⠀🍹 Зелья\n"
                f"⠀⠀👑 Рейтинг - ваш рейтинг\n"
                f"⠀⠀🏆 Топ\n"
                f"⠀⠀💖 Брак\n"
                f"⠀⠀💔 Развод\n"
                f"⠀⠀✒ Ник [имя]\n"
                f"⠀⠀💸 Продать [предмет]\n"
                f"⠀⠀🤝 Передать [ID] [сумма]\n"
                f"⠀⠀👥 Реф\n"
                f"⠀⠀🏆 Реф топ\n"
                f"⠀⠀🎁 Донат")


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

        if general.check_user_ban(user) is True:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш аккаунт заблокирован!')
        else:
            temp_message = f'@id{message.from_id} ({user[0]["Name"]}), Ваш профиль:\n'
            temp_message += f'🔎 ID: {user[0]["ID"]}\n'

            # Rank
            if user[0]["RankLevel"] == 2:
                temp_message += f'🔥 VIP игрок\n'
            elif user[0]["RankLevel"] == 3:
                temp_message += f'🔮 Premium игрок\n'
            elif user[0]["RankLevel"] == 4:
                temp_message += f'🌀 Модератор\n'
            elif user[0]["RankLevel"] >= 5:
                temp_message += f'👑 Администратор\n'

            # Main info
            if user[0]["EXP"] > 0:
                temp_message += f'⭐ Опыта: {general.change_number(user[0]["EXP"])}\n'
            temp_message += f'⚡ Энергия: {general.change_number(user[0]["Energy"])}\n'
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

            # Potion effect
            if user[0]["Potion"] > 0 and user[0]["PotionTime"] > 0:
                temp_message += f'\n🍹 Эффект от зелья:\n'
                if user[0]["Potion"] == 1:
                    temp_message += f'⠀🍀 Зелье удачи\n'
                    temp_message += f'⠀🕛 Время действия: {time.strftime("%M мин.", time.gmtime(user[0]["PotionTime"] * 60))}\n'
                elif user[0]["Potion"] == 2:
                    temp_message += f'⠀⚒ Зелье шахтера\n'
                    temp_message += f'⠀🕛 Время действия: {time.strftime("%M мин.", time.gmtime(user[0]["PotionTime"] * 60))}\n'
                elif user[0]["Potion"] == 3:
                    temp_message += f'⠀❌ Зелье неудачи\n'
                    temp_message += f'⠀🕛 Время действия: {time.strftime("%M мин.", time.gmtime(user[0]["PotionTime"] * 60))}\n'

            # Mined resource
            if user[0]["Iron"] > 0 or user[0]["Gold"] > 0 or user[0]["Diamond"] > 0 or user[0]["Matter"] > 0:
                temp_message += f'\n🔦 Ресурсы:\n'
                if user[0]["Iron"] > 0:
                    temp_message += f'⠀🥈 Железо: {general.change_number(user[0]["Iron"])} ед.\n'
                if user[0]["Gold"] > 0:
                    temp_message += f'⠀🏅 Золото: {general.change_number(user[0]["Gold"])} ед.\n'
                if user[0]["Diamond"] > 0:
                    temp_message += f'⠀💎 Алмазы: {general.change_number(user[0]["Diamond"])} ед.\n'
                if user[0]["Matter"] > 0:
                    temp_message += f'⠀🎆 Материя: {general.change_number(user[0]["Matter"])} ед.\n'

            # Registration date
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
            chats = {ID["ChatID"] for ID in MainData.get_chats()}
            if message.chat_id in chats:
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
                                     f'⠀📦 Кейсы\n'
                                     f'⠀🍹 Зелья'
                                     f'\n🔎 Для просмотра категории используйте "магазин [категория]".\n'
                                     f'🔎 Для покупки используйте "магазин [категория] купить [номер товара]".\n',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🚗 Машины", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_transport_cars"}, "color": "secondary"},
                                                 {"label": "🏍 Мотоциклы", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_transport_motorcycles"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "🏠 Дома", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_estate_houses"}, "color": "secondary"},
                                                 {"label": "🌇 Квартиры", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_estate_apartments"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "🔋 Фермы", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_other_farms"}, "color": "secondary"},
                                                 {"label": "💼 Бизнесы", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_other_businesses"},
                                                  "color": "secondary"},
                                                 {"label": "🐸 Питомцы", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_other_pets"}, "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "📦 Кейсы", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_other_cases"}, "color": "secondary"},
                                                 {"label": "🍹 Зелья", "type": "text",
                                                  "payload": {"cmd": "cmd_shop_other_potion"}, "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "◀ В главное меню", "type": "text",
                                                  "payload": {"cmd": "cmd_mainmenu"}, "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
            else:
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
                                     f'⠀📦 Кейсы\n'
                                     f'⠀🍹 Зелья'
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
                        if shop_data[0][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[0][int(product) - 1]["CarName"]} за '
                                                 f'{general.change_number(shop_data[0][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[0][int(product) - 1]["Image"])
                        else:
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
                        if shop_data[1][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[1][int(product) - 1]["YachtName"]} за '
                                                 f'{general.change_number(shop_data[1][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[1][int(product) - 1]["Image"])
                        else:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[1][int(product) - 1]["YachtName"]} за '
                                                 f'{general.change_number(shop_data[1][int(product) - 1]["Price"])}$')
        elif category.lower() == 'самолеты' or category.lower() == 'самолёты':
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
                        if shop_data[2][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[2][int(product) - 1]["AirplaneName"]} за '
                                                 f'{general.change_number(shop_data[2][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[2][int(product) - 1]["Image"])
                        else:
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
                        if shop_data[3][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[3][int(product) - 1]["HelicopterName"]} за '
                                                 f'{general.change_number(shop_data[3][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[3][int(product) - 1]["Image"])
                        else:
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
                        if shop_data[4][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[4][int(product) - 1]["HouseName"]} за '
                                                 f'{general.change_number(shop_data[4][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[4][int(product) - 1]["Image"])
                        else:
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
                        if shop_data[5][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[5][int(product) - 1]["ApartmentName"]} за '
                                                 f'{general.change_number(shop_data[5][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[5][int(product) - 1]["Image"])
                        else:
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
                        if shop_data[6][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[6][int(product) - 1]["PhoneName"]} за '
                                                 f'{general.change_number(shop_data[6][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[6][int(product) - 1]["Image"])
                        else:
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
                        if shop_data[8][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[8][int(product) - 1]["BusinessName"]} за '
                                                 f'{general.change_number(shop_data[8][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[8][int(product) - 1]["Image"])
                        else:
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
                        if shop_data[10][int(product) - 1]["Image"] != 0:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[10][int(product) - 1]["MotoName"]} за '
                                                 f'{general.change_number(shop_data[10][int(product) - 1]["Price"])}$',
                                                 attachment=shop_data[10][int(product) - 1]["Image"])
                        else:
                            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы приобрели себе '
                                                 f'{shop_data[10][int(product) - 1]["MotoName"]} за '
                                                 f'{general.change_number(shop_data[10][int(product) - 1]["Price"])}$')
        elif category.lower() == 'кейсы':
            if product is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), кейсы:\n'
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
        elif category.lower() == 'зелья':
            if product is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), зелья:\n'
                                     f'🔸 1. Зелье удачи на 10 минут 🍀 [1.000.000$]\n'
                                     f'🔸 2. Зелье шахтера на 30 минут ⚒ [10.000.000$]\n'
                                     f'🔸 3. Зелье неудачи на 10 минут ❌ [500.000$]\n'
                                     f'🔸 4. Молоко 🥛 [100.000$]\n\n'
                                     f'Каждое новое зелье отменияет эффект предыдущего❗\n'
                                     f'❓ Для покупки введите "магазин зелья купить [номер]"')
            elif product == '1':
                user[0]["Potion"] = 1
                user[0]["PotionTime"] = 10
                UserAction.save_user(message.from_id, user)
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы купили и выпили зелье удачи 🍀\n"
                                     f"Оно действует 10 минут ☺")
            elif product == '2':
                user[0]["Potion"] = 2
                user[0]["PotionTime"] = 30
                UserAction.save_user(message.from_id, user)
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы купили и выпили зелье шахтера ⚒\n"
                                     f"Оно действует 30 минут ☺")
            elif product == '3':
                user[0]["Potion"] = 3
                user[0]["PotionTime"] = 10
                UserAction.save_user(message.from_id, user)
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы купили и выпили зелье неудачи ❌\n"
                                     f"Оно действует 10 минут ☺")
            elif product == '4':
                user[0]["Potion"] = 0
                user[0]["PotionTime"] = 0
                UserAction.save_user(message.from_id, user)
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы купили и выпили молоко 🥛\n"
                                     f"Все эффекты сняты ☺")
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
@bot.on.message(payload={"cmd": "cmd_shop_other_potion"})
async def shop_products_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        # shop_data = MainData.get_shop_data()
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
        if products_category == 'other_potion':
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), зелья:\n'
                                 f'🔸 1. Зелье удачи на 10 минут 🍀 [1.000.000$]\n'
                                 f'🔸 2. Зелье шахтера на 30 минут ⚒ [10.000.000$]\n'
                                 f'🔸 3. Зелье неудачи на 10 минут ❌ [500.000$]\n'
                                 f'🔸 4. Молоко 🥛 [100.000$]\n\n'
                                 f'Каждое новое зелье отменияет эффект предыдущего❗\n'
                                 f'❓ Для покупки введите "магазин зелья купить [номер]"')


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
                user[0]["Bonus"] = 24 * 60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money)} $. '
                                     f'Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"] * 60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"] * 60))}.')
            elif user[0]["RankLevel"] == 2:
                user[0]["Money"] += temp_money * 2
                user[0]["BTC"] += temp_btc
                user[0]["Bonus"] = 12 * 60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 2)} $ '
                                     f'и {general.change_number(temp_btc)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"] * 60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"] * 60))}')
            elif user[0]["RankLevel"] == 3:
                user[0]["Money"] += temp_money * 3
                user[0]["BTC"] += temp_btc * 2
                user[0]["Bonus"] = 6 * 60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 3)} $ '
                                     f'и {general.change_number(temp_btc * 2)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"] * 60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"] * 60))}')
            elif user[0]["RankLevel"] == 4:
                user[0]["Money"] += temp_money * 4
                user[0]["BTC"] += temp_btc * 3
                user[0]["Bonus"] = 3 * 60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 4)} $ '
                                     f'и {general.change_number(temp_btc * 3)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"] * 60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"] * 60))}')
            elif user[0]["RankLevel"] >= 5:
                user[0]["Money"] += temp_money * 5
                user[0]["BTC"] += temp_btc * 4
                user[0]["Bonus"] = 1 * 60
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваш сегодняшний бонус '
                                     f'{general.change_number(temp_money * 5)} $ '
                                     f'и {general.change_number(temp_btc * 4)} ₿. Возвращайтесь через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"] * 60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"] * 60))}')
            UserAction.save_user(message.from_id, user)
        else:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам еще недоступен бонус! Возвращайтесь '
                                 f'через {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["Bonus"] * 60)) if user[0]["Bonus"] >= 60 else time.strftime("%M мин.", time.gmtime(user[0]["Bonus"] * 60))}')


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
        if user[0]["BanTrade"] > 0:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам запрещено писать в репорт!\n'
                                 f'Ожидайте: {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["BanTrade"] * 60)) if user[0]["BanTrade"] > 60 else time.strftime("%M мин.", time.gmtime(user[0]["BanTrade"]  * 60))}')
        else:
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


@bot.on.message(text=["Настройки", "настройки"])
@bot.on.message(payload={'cmd': "cmd_settings"})
async def settings_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if message.chat_id in chats:
            if user[0]["Notifications"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), настройки:',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🔔 Включить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_enable"},
                                                  "color": "secondary"},
                                                 {"label": "🔕 Выключить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_disable"},
                                                  "color": "primary"}
                                             ],
                                             [
                                                 {"label": "◀ В раздел \"разное\"", "type": "text",
                                                  "payload": {"cmd": "cmd_other"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
            elif user[0]["Notifications"] == 1:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), настройки:',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🔔 Включить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_enable"},
                                                  "color": "primary"},
                                                 {"label": "🔕 Выключить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_disable"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "◀ В раздел \"разное\"", "type": "text",
                                                  "payload": {"cmd": "cmd_other"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
        else:
            if user[0]["Notifications"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), настройки:',
                                     keyboard=Keyboard(one_time=False, inline=False).schema(
                                         [
                                             [
                                                 {"label": "🔔 Включить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_enable"},
                                                  "color": "secondary"},
                                                 {"label": "🔕 Выключить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_disable"},
                                                  "color": "primary"}
                                             ],
                                             [
                                                 {"label": "◀ В раздел \"разное\"", "type": "text",
                                                  "payload": {"cmd": "cmd_other"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
            elif user[0]["Notifications"] == 1:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), настройки:',
                                     keyboard=Keyboard(one_time=False, inline=False).schema(
                                         [
                                             [
                                                 {"label": "🔔 Включить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_enable"},
                                                  "color": "primary"},
                                                 {"label": "🔕 Выключить уведомления", "type": "text",
                                                  "payload": {"cmd": "settings_notifications_disable"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "◀ В раздел \"разное\"", "type": "text",
                                                  "payload": {"cmd": "cmd_other"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())


@bot.on.message(payload={"cmd": "settings_notifications_enable"})
@bot.on.message(payload={"cmd": "settings_notifications_disable"})
async def settings_change_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\n"
                             f"Ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        temp = message.payload.split('{"cmd":"settings_')[1].split('"}')[0]
        if temp == 'notifications_enable':
            if user[0]["Notifications"] == 1:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже включены уведомления')
            else:
                user[0]["Notifications"] = 1
                chats = {ID["ChatID"] for ID in MainData.get_chats()}
                if message.chat_id in chats:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы включили уведомления',
                                         keyboard=Keyboard(one_time=False, inline=True).schema(
                                             [
                                                 [
                                                     {"label": "🔔 Включить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_enable"},
                                                      "color": "primary"},
                                                     {"label": "🔕 Выключить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_disable"},
                                                      "color": "secondary"}
                                                 ],
                                                 [
                                                     {"label": "◀ В раздел \"разное\"", "type": "text",
                                                      "payload": {"cmd": "cmd_other"},
                                                      "color": "positive"}
                                                 ]
                                             ]
                                         ).get_json())
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы включили уведомления',
                                         keyboard=Keyboard(one_time=False, inline=False).schema(
                                             [
                                                 [
                                                     {"label": "🔔 Включить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_enable"},
                                                      "color": "primary"},
                                                     {"label": "🔕 Выключить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_disable"},
                                                      "color": "secondary"}
                                                 ],
                                                 [
                                                     {"label": "◀ В раздел \"разное\"", "type": "text",
                                                      "payload": {"cmd": "cmd_other"},
                                                      "color": "positive"}
                                                 ]
                                             ]
                                         ).get_json())
        elif temp == 'notifications_disable':
            if user[0]["Notifications"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже отключены уведомления')
            else:
                user[0]["Notifications"] = 0
                chats = {ID["ChatID"] for ID in MainData.get_chats()}
                if message.chat_id in chats:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы отключили уведомления',
                                         keyboard=Keyboard(one_time=False, inline=True).schema(
                                             [
                                                 [
                                                     {"label": "🔔 Включить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_enable"},
                                                      "color": "secondary"},
                                                     {"label": "🔕 Выключить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_disable"},
                                                      "color": "primary"}
                                                 ],
                                                 [
                                                     {"label": "◀ В раздел \"разное\"", "type": "text",
                                                      "payload": {"cmd": "cmd_other"},
                                                      "color": "positive"}
                                                 ]
                                             ]
                                         ).get_json())
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы отключили уведомления',
                                         keyboard=Keyboard(one_time=False, inline=False).schema(
                                             [
                                                 [
                                                     {"label": "🔔 Включить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_enable"},
                                                      "color": "secondary"},
                                                     {"label": "🔕 Выключить уведомления", "type": "text",
                                                      "payload": {"cmd": "settings_notifications_disable"},
                                                      "color": "primary"}
                                                 ],
                                                 [
                                                     {"label": "◀ В раздел \"разное\"", "type": "text",
                                                      "payload": {"cmd": "cmd_other"},
                                                      "color": "positive"}
                                                 ]
                                             ]
                                         ).get_json())
        UserAction.save_user(message.from_id, user)


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
                                 f"⠀🐸 питомец\n"
                                 f"⠀🥈 железо [кол-во]⠀⠀{general.change_number(MainData.get_settings()[0]['IronPrice'])}$/ед.\n"
                                 f"⠀🏅 золото [кол-во]⠀⠀{general.change_number(MainData.get_settings()[0]['GoldPrice'])}$/ед.\n"
                                 f"⠀💎 алмазы [кол-во]⠀⠀{general.change_number(MainData.get_settings()[0]['DiamondPrice'])}$/ед.\n"
                                 f"⠀🎆 материю [кол-во]⠀⠀{general.change_number(MainData.get_settings()[0]['MatterPrice'])}$/ед.\n")
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
        elif property_name == 'железо':
            if count is None or count == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для продажи железа используйте: '
                                     f'продать железо [кол-во]')
            else:
                if user[0]["Iron"] < count:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько железа! Для '
                                         f'добычи используйте: добывать железо')
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                         f'{general.change_number(count)} железа за '
                                         f'{general.change_number(MainData.get_settings()[0]["IronPrice"] * count)}$')
                    user[0]["Money"] += MainData.get_settings()[0]["IronPrice"] * count
                    user[0]["Iron"] -= count
                    UserAction.save_user(message.from_id, user)
        elif property_name == 'золото':
            if count is None or count == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для продажи золота используйте: '
                                     f'продать золото [кол-во]')
            else:
                if user[0]["Gold"] < count:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько золота! Для '
                                         f'добычи используйте: добывать золото')
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                         f'{general.change_number(count)} золота за '
                                         f'{general.change_number(MainData.get_settings()[0]["GoldPrice"] * count)}$')
                    user[0]["Money"] += MainData.get_settings()[0]["GoldPrice"] * count
                    user[0]["Gold"] -= count
                    UserAction.save_user(message.from_id, user)
        elif property_name == 'алмазы':
            if count is None or count == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для продажи алмазов используйте: '
                                     f'продать алмазы [кол-во]')
            else:
                if user[0]["Diamond"] < count:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько алмазов! Для '
                                         f'добычи используйте: добывать алмазы')
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                         f'{general.change_number(count)} алмаза(-ов) за '
                                         f'{general.change_number(MainData.get_settings()[0]["DiamondPrice"] * count)}$')
                    user[0]["Money"] += MainData.get_settings()[0]["DiamondPrice"] * count
                    user[0]["Diamond"] -= count
                    UserAction.save_user(message.from_id, user)
        elif property_name == 'материю':
            if count is None or count == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для продажи материи используйте: '
                                     f'продать матрею [кол-во]')
            else:
                if user[0]["Matter"] < count:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет столько матери! Для '
                                         f'добычи используйте: добывать материю')
                else:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы продали '
                                         f'{general.change_number(count)} материи за '
                                         f'{general.change_number(MainData.get_settings()[0]["MatterPrice"] * count)}$')
                    user[0]["Money"] += MainData.get_settings()[0]["MatterPrice"] * count
                    user[0]["Matter"] -= count
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
        if user[0]["BanReport"] > 0:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вам запрещено писать в репорт!\n'
                                 f'Ожидайте: {time.strftime("%H ч. %M мин.", time.gmtime(user[0]["BanReport"] * 60)) if user[0]["BanReport"] > 60 else time.strftime("%M мин.", time.gmtime(user[0]["BanReport"] * 60))}')
        else:
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
                    temp_hunger = random.randint(1, 15)
                    temp_joy = random.randint(1, 15)
                    if chance_loss == 1:
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец потерялся в походе 😔')
                        user[0]["Pet_Fatigue"] = 0
                        user[0]["Pet_Hunger"] = 0
                        user[0]["Pet_Joy"] = 0
                        user[1]["Pet"] = 0
                        user[1]["PetLevel"] = 0
                        UserAction.save_user(message.from_id, user)
                    else:
                        user[0]["Money"] += found_money
                        user[0]["Pet_Fatigue"] = 60
                        if user[0]["Pet_Joy"] - temp_joy < 0:
                            user[0]["Pet_Joy"] = 0
                        else:
                            user[0]["Pet_Joy"] -= temp_joy
                        if user[0]["Pet_Hunger"] - temp_hunger < 0:
                            user[0]["Pet_Hunger"] = 0
                        else:
                            user[0]["Pet_Hunger"] -= temp_hunger
                        UserAction.save_user(message.from_id, user)
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец нашел в походе {general.change_number(found_money)}$')
        elif action == 'найти':
            if user[1]["Pet"] != 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас уже есть питомец')
            else:
                if user[0]["Energy"] <= 0:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас недостаточно энергии 😔')
                else:
                    chance_found = random.randint(0, 70)
                    if chance_found == 1:
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), Вы нашли питомца «{pets[0]["PetName"]}»')
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
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), Вы не смогли найти питомца 😔\n'
                            f'💡 Ваша энергия: {user[0]["Energy"]}\n'
                            f'Попробуйте еще раз')
        elif action == 'поиграть':
            if user[1]["Pet"] == 0:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет питомца.\n'
                                     f'Вы можете найти питомца. Используйте: питомец найти\n'
                                     f'или используйте магазин для покупки')
            else:
                if user[0]["Pet_Joy"] == 100:
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), Ваш питомец и так в хорошем настроении')
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
                elif user[0]["Money"] < user[1]["PetLevel"] * 3:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас недостаточно денег, чтобы '
                                         f'покормить питомца 😔')
                else:
                    user[0]["Money"] -= user[1]["PetLevel"] * 3
                    user[0]["Pet_Hunger"] = 100
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы покормили своего питомца за '
                                         f'{general.change_number(user[1]["PetLevel"] * 3)}$\n'
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
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if message.chat_id in chats:
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои игры: \n"
                f"🔫 Рулетка - русская рулетка\n"
                f"🎲 Кубик [1-6]\n"
                f"🎰 Казино [сумма]\n"
                f"📈 Трейд [вверх/вниз] [сумма]\n"
                f"🥛 Стаканчик [1-3] [сумма]\n"
                f"🦅 Монетка [орёл/решка] [сумма]",
                keyboard=Keyboard(one_time=False, inline=True).schema(
                    [
                        [
                            {"label": "🔫 Рулетка", "type": "text", "payload": {"cmd": "game_roulette"},
                             "color": "secondary"},
                            {"label": "🎲 Кубик", "type": "text", "payload": {"cmd": "game_cube"},
                             "color": "secondary"},
                            {"label": "🎰 Казино", "type": "text", "payload": {"cmd": "game_casino"},
                             "color": "secondary"}
                        ],
                        [
                            {"label": "📈 Трейд", "type": "text", "payload": {"cmd": "game_trade"},
                             "color": "secondary"},
                            {"label": "🥛 Стаканчик", "type": "text", "payload": {"cmd": "game_cup"},
                             "color": "secondary"},
                            {"label": "🦅 Монетка", "type": "text", "payload": {"cmd": "game_coin"},
                             "color": "secondary"}
                        ],
                        [
                            {"label": "◀ В раздел \"разное\"", "type": "text", "payload": {"cmd": "cmd_other"},
                             "color": "positive"}
                        ]
                    ]
                ).get_json())
        else:
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), мои игры: \n"
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
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if message.chat_id in chats:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы начали игру в \"Русскую рулетку\" 👍\n"
                                 f"🔫 Для игры введите \"выстрелить\"\n"
                                 f"❌ Чтобы выйти из игры, напишет \"остановиться\"",
                                 keyboard=Keyboard(one_time=False, inline=True).schema(
                                     [
                                         [
                                             {"label": "🔫 Выстрелить", "type": "text",
                                              "payload": {"cmd": "game_roulette_shot"}, "color": "secondary"},
                                             {"label": "💵 Остановиться", "type": "text",
                                              "payload": {"cmd": "game_roulette_stop"},
                                              "color": "secondary"},
                                         ],
                                         [
                                             {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"},
                                              "color": "positive"}
                                         ]
                                     ]
                                 ).get_json())
        else:
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
            chats = {ID["ChatID"] for ID in MainData.get_chats()}
            if message.chat_id in chats:
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), Вы начали игру в \"Русскую рулетку\" 👍\n'
                    f'🔫 Для игры введите \"выстрелить\"\n'
                    f'❌ Чтобы выйти из игры, напишет \"остановиться\"',
                    keyboard=Keyboard(one_time=False, inline=True).schema(
                        [
                            [
                                {"label": "🔫 Выстрелить", "type": "text", "payload": {"cmd": "game_roulette_shot"},
                                 "color": "secondary"},
                                {"label": "💵 Остановиться", "type": "text", "payload": {"cmd": "game_roulette_stop"},
                                 "color": "secondary"},
                            ],
                            [
                                {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"},
                                 "color": "positive"}
                            ]
                        ]
                    ).get_json())
            else:
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), Вы начали игру в \"Русскую рулетку\" 👍\n'
                    f'🔫 Для игры введите \"выстрелить\"\n'
                    f'❌ Чтобы выйти из игры, напишет \"остановиться\"', keyboard=GAME_ROULETTE_KEYBOARD)
        else:
            if shot == 1 and user[0]["Roulette_Shots"] > 0:
                if user[0]["Money"] >= 800:
                    heal_money = random.randint(1, 8) * 100
                    chats = {ID["ChatID"] for ID in MainData.get_chats()}
                    if message.chat_id in chats:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы выстрелили на '
                                             f'{user[0]["Roulette_Shots"]}-й попытке ☹\n'
                                             f'💸 Ваш выигрыш: {general.change_number(user[0]["Roulette_Shots"] * 100)}$\n'
                                             f'❤ На лечение потрачено: {general.change_number(heal_money)}$',
                                             keyboard=Keyboard(one_time=False, inline=True).schema(
                                                 [
                                                     [
                                                         {"label": "🔫 Выстрелить", "type": "text",
                                                          "payload": {"cmd": "game_roulette_shot"},
                                                          "color": "secondary"},
                                                         {"label": "💵 Остановиться", "type": "text",
                                                          "payload": {"cmd": "game_roulette_stop"},
                                                          "color": "secondary"},
                                                     ],
                                                     [
                                                         {"label": "◀ Игры", "type": "text",
                                                          "payload": {"cmd": "cmd_games"}, "color": "positive"}
                                                     ]
                                                 ]
                                             ).get_json())
                    else:
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
                    chats = {ID["ChatID"] for ID in MainData.get_chats()}
                    if message.chat_id in chats:
                        await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы выстрелили на '
                                             f'{user[0]["Roulette_Shots"]}-й попытке ☹\n'
                                             f'💸 Ваш выигрыш: {general.change_number(user[0]["Roulette_Shots"] * 100)}$',
                                             keyboard=Keyboard(one_time=False, inline=True).schema(
                                                 [
                                                     [
                                                         {"label": "🔫 Выстрелить", "type": "text",
                                                          "payload": {"cmd": "game_roulette_shot"},
                                                          "color": "secondary"},
                                                         {"label": "💵 Остановиться", "type": "text",
                                                          "payload": {"cmd": "game_roulette_stop"},
                                                          "color": "secondary"},
                                                     ],
                                                     [
                                                         {"label": "◀ Игры", "type": "text",
                                                          "payload": {"cmd": "cmd_games"}, "color": "positive"}
                                                     ]
                                                 ]
                                             ).get_json())
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
                chats = {ID["ChatID"] for ID in MainData.get_chats()}
                if message.chat_id in chats:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы сделали '
                                         f'{user[0]["Roulette_Shots"] - 1}-ю осечку',
                                         keyboard=Keyboard(one_time=False, inline=True).schema(
                                             [
                                                 [
                                                     {"label": "🔫 Выстрелить", "type": "text",
                                                      "payload": {"cmd": "game_roulette_shot"}, "color": "secondary"},
                                                     {"label": "💵 Остановиться", "type": "text",
                                                      "payload": {"cmd": "game_roulette_stop"},
                                                      "color": "secondary"},
                                                 ],
                                                 [
                                                     {"label": "◀ Игры", "type": "text",
                                                      "payload": {"cmd": "cmd_games"}, "color": "positive"}
                                                 ]
                                             ]
                                         ).get_json())
                else:
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
            chats = {ID["ChatID"] for ID in MainData.get_chats()}
            if message.chat_id in chats:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не играли в \"Русскую рулетку\"\n'
                                     f'🔫 Для начала игры введите \"рулетка\"\n',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🔫 Рулетка", "type": "text",
                                                  "payload": {"cmd": "game_roulette"}, "color": "secondary"},
                                                 {"label": "🎲 Кубик", "type": "text", "payload": {"cmd": "game_cube"},
                                                  "color": "secondary"},
                                                 {"label": "🎰 Казино", "type": "text",
                                                  "payload": {"cmd": "game_casino"}, "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "📈 Трейд", "type": "text", "payload": {"cmd": "game_trade"},
                                                  "color": "secondary"},
                                                 {"label": "🥛 Стаканчик", "type": "text",
                                                  "payload": {"cmd": "game_cup"}, "color": "secondary"},
                                                 {"label": "🦅 Монетка", "type": "text",
                                                  "payload": {"cmd": "game_coin"}, "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "◀ В раздел \"разное\"", "type": "text",
                                                  "payload": {"cmd": "cmd_other"}, "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не играли в \"Русскую рулетку\"\n'
                                     f'🔫 Для начала игры введите \"рулетка\"\n', keyboard=GAMES_KEYBOARD)
        else:
            if user[0]["Roulette_Shots"] - 1 > 0:
                chats = {ID["ChatID"] for ID in MainData.get_chats()}
                if message.chat_id in chats:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы остановилсь на '
                                         f'{user[0]["Roulette_Shots"]}-й попытке 👍\n'
                                         f'💸 Ваш выигрыш: {general.change_number(user[0]["Roulette_Shots"] * 100)}$',
                                         keyboard=Keyboard(one_time=False, inline=True).schema(
                                             [
                                                 [
                                                     {"label": "🔫 Рулетка", "type": "text",
                                                      "payload": {"cmd": "game_roulette"}, "color": "secondary"},
                                                     {"label": "🎲 Кубик", "type": "text",
                                                      "payload": {"cmd": "game_cube"}, "color": "secondary"},
                                                     {"label": "🎰 Казино", "type": "text",
                                                      "payload": {"cmd": "game_casino"}, "color": "secondary"}
                                                 ],
                                                 [
                                                     {"label": "📈 Трейд", "type": "text",
                                                      "payload": {"cmd": "game_trade"}, "color": "secondary"},
                                                     {"label": "🥛 Стаканчик", "type": "text",
                                                      "payload": {"cmd": "game_cup"}, "color": "secondary"},
                                                     {"label": "🦅 Монетка", "type": "text",
                                                      "payload": {"cmd": "game_coin"}, "color": "secondary"}
                                                 ],
                                                 [
                                                     {"label": "◀ В раздел \"разное\"", "type": "text",
                                                      "payload": {"cmd": "cmd_other"}, "color": "positive"}
                                                 ]
                                             ]
                                         ).get_json())
                else:
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
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if message.chat_id in chats:
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), Вы начали игру в \"Кубик\" 👍\n"
                f"🎲 Для игры в кубик выбирайте числа от 1 до 6\n",
                keyboard=Keyboard(one_time=False, inline=True).schema(
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
                ).get_json())
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
            chats = {ID["ChatID"] for ID in MainData.get_chats()}
            if message.chat_id in chats:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы угадали 🎉\n'
                                     f'🎲 Выпало число: {cube_temp}\n'
                                     f'💸 Ваш выигрыш: {general.change_number(cube_prize)}$',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🎲 1", "type": "text", "payload": {"cmd": "game_cube_1"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 2", "type": "text", "payload": {"cmd": "game_cube_2"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 3", "type": "text", "payload": {"cmd": "game_cube_3"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "🎲 4", "type": "text", "payload": {"cmd": "game_cube_4"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 5", "type": "text", "payload": {"cmd": "game_cube_5"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 6", "type": "text", "payload": {"cmd": "game_cube_6"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы угадали 🎉\n'
                                     f'🎲 Выпало число: {cube_temp}\n'
                                     f'💸 Ваш выигрыш: {general.change_number(cube_prize)}$',
                                     keyboard=GAME_CUBE_KEYBOARD)
            user[0]["Money"] += cube_prize
            UserAction.save_user(message.from_id, user)
        else:
            chats = {ID["ChatID"] for ID in MainData.get_chats()}
            if message.chat_id in chats:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не угадали 😟\n'
                                     f'🎲 Выпало число: {cube_temp}',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🎲 1", "type": "text", "payload": {"cmd": "game_cube_1"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 2", "type": "text", "payload": {"cmd": "game_cube_2"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 3", "type": "text", "payload": {"cmd": "game_cube_3"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "🎲 4", "type": "text", "payload": {"cmd": "game_cube_4"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 5", "type": "text", "payload": {"cmd": "game_cube_5"},
                                                  "color": "secondary"},
                                                 {"label": "🎲 6", "type": "text", "payload": {"cmd": "game_cube_6"},
                                                  "color": "secondary"}
                                             ],
                                             [
                                                 {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
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
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if message.chat_id in chats:
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), Вы начали игру в \"Монетка\" 👍\n"
                f"🦅 Для игры в кубик выбирайте \"Орел\" или \"Решка\"\n",
                keyboard=Keyboard(one_time=False, inline=True).schema(
                    [
                        [
                            {"label": "🦅 Орел", "type": "text", "payload": {"cmd": "game_coin_1"},
                             "color": "secondary"},
                            {"label": "🗂 Решка", "type": "text", "payload": {"cmd": "game_coin_2"},
                             "color": "secondary"},
                        ],
                        [
                            {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"}, "color": "positive"}
                        ]
                    ]
                ).get_json())
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
            chats = {ID["ChatID"] for ID in MainData.get_chats()}
            if message.chat_id in chats:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы угадали 🎉\n'
                                     f'🦅 Выпало: {"орел" if coin_temp == 1 else "решка"}\n'
                                     f'💸 Ваш выигрыш: {general.change_number(coin_prize)}$',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🦅 Орел", "type": "text", "payload": {"cmd": "game_coin_1"},
                                                  "color": "secondary"},
                                                 {"label": "🗂 Решка", "type": "text",
                                                  "payload": {"cmd": "game_coin_2"}, "color": "secondary"},
                                             ],
                                             [
                                                 {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы угадали 🎉\n'
                                     f'🦅 Выпало: {"орел" if coin_temp == 1 else "решка"}\n'
                                     f'💸 Ваш выигрыш: {general.change_number(coin_prize)}$',
                                     keyboard=GAME_COIN_KEYBOARD)
            user[0]["Money"] += coin_prize
            UserAction.save_user(message.from_id, user)
        else:
            chats = {ID["ChatID"] for ID in MainData.get_chats()}
            if message.chat_id in chats:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы не угадали 😟\n'
                                     f'🦅 Выпало: {"орел" if coin_temp == 1 else "решка"}',
                                     keyboard=Keyboard(one_time=False, inline=True).schema(
                                         [
                                             [
                                                 {"label": "🦅 Орел", "type": "text", "payload": {"cmd": "game_coin_1"},
                                                  "color": "secondary"},
                                                 {"label": "🗂 Решка", "type": "text",
                                                  "payload": {"cmd": "game_coin_2"}, "color": "secondary"},
                                             ],
                                             [
                                                 {"label": "◀ Игры", "type": "text", "payload": {"cmd": "cmd_games"},
                                                  "color": "positive"}
                                             ]
                                         ]
                                     ).get_json())
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
@bot.on.message(text=["Казино", "казино"])
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
            if user[0]["Potion"] == 1 and user[0]["PotionTime"] > 1:
                casino_temp = random.choice([2, 5, 10])
            elif user[0]["Potion"] == 3 and user[0]["PotionTime"] > 1:
                casino_temp = random.choice([0, 0.5, 2])
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


# todo Изменить, когда будет сайт!
# Donate command
@bot.on.message(text=["Донат", "донат"])
@bot.on.message(payload={"cmd": "cmd_donate"})
async def donate_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        businesses = MainData.get_data('businesses')
        pets = MainData.get_data('pets')
        await message.answer(f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), "
                             f"В ДАННЫЙ МОМЕНТ, ДЛЯ ПОКУПКИ ДОНАТ УСГУЛ, ОБРАЩАТЬСЯ К @id503006053 (ОСНОВАТЕЛЬ) ИЛИ @manderr (ЗАМЕСТИТЕЛЬ)!\n"
                             f"ЗА ПЕРЕВОД СРЕДСТВ И НЕ ПОЛУЧЕНИЕ СВОЕГО ТОВАРА ОТВЕТСТВЕННОСТЬ ЛОЖИТЬСЯ ТОЛЬКО НА ВАС!!!\n\n"
                             f"Доступный донат:\n"
                             f"1.🎥 Бизнес «Киностудия», один из самых лучших бизнесов, с прибылью в {general.change_number(businesses[20 - 1]['MoneyPerHouse'] * 2)}$\n"
                             f"🔹Продать бизнес можно за {general.change_number(math.trunc(businesses[20 - 1]['Price'] / 2))}$\n"
                             f"🔸Цена: 47₽\n\n"
                             f"2.💼 Бизнес «Межпланетный Экспресс», самый лучший бизнес, с прибылью в {general.change_number(businesses[21 - 1]['MoneyPerHouse'] * 2)}$\n"
                             f"🔹Продать бизнес можно за {general.change_number(math.trunc(businesses[21 - 1]['Price'] / 2))}$\n"
                             f"🔸Цена: 144₽\n\n"
                             f"3.🦠 Питомец «Короновирус», самый лучший питомец\n"
                             f"🔹При максимальном уровне приносит до {general.change_number(pets[14 - 1]['PetMaxMoney'])}$\n"
                             f"🔹Короновирус невозможно потерять в походе\n"
                             f"🔹Короновирус устаёт всего на 15 минут вместо 60-ти\n"
                             f"🔸Продать Короновирус можно за {general.change_number(math.trunc(pets[14 - 1]['Price'] / 2))}$\n"
                             f"🔸Цена: 47₽\n\n"
                             f"4.🔮 Статус «Premium», самый лучший донат статус\n"
                             f"🔹Подробное описание здесь: COMING SOON\n"
                             f"🔸Цена: 225₽\n"
                             f"5.🔥 Статус «VIP», самый дешёвый донат статус\n"
                             f"🔹Подробное описание здесь: COMING SOON\n"
                             f"🔸Цена: 47₽\n\n"
                             f"Приобрести донат в автоматическом режиме можно на нашем сайте: {MainData.get_settings()[0]['SiteURL']} ✅\n"
                             f"🎲 При покупке укажите ваш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")


# Work commands
@bot.on.message(text=["Работа", "работа"])
@bot.on.message(text=["Работа <param>", "работа <param>"])
@bot.on.message(text=["Работа <param> устроиться <param2>", "работа <param> устроиться <param2>"])
@bot.on.message(payload={"cmd": "cmd_work"})
async def work_handler(message: Message, info: UsersUserXtrCounters, param: Optional[str] = None,
                       param2: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if param is None:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                 f"Вы можете устроиться в одну из организаций:\n"
                                 f"🔹 1. ЖКХ\n"
                                 f"🔎 Для просмотра вакансий используйте \"работа [организация]\"")
        elif param.lower() == 'уволиться':
            user[0]["Work"] = 0
            user[0]["WorkCooldown"] = 0
            UserAction.save_user(message.from_id, user)
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы уволились с работы\n"
                                 f"Используйте \"Работа\", чтобы опять устроиться")
        elif param == '1':
            if user[0]["Work"] > 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы уже где-то работаете, "
                                     f"вам необходимо уволиться\n"
                                     f"Используйте \"Работа уволиться\", чтобы уволиться")
            else:
                if param2 is None:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                         f"Доступные вакансии в ЖКХ:\n"
                                         f"🔹 1. Дворник [до 4.500$/нед.]\n"
                                         f"🔹 2. Электрик [до 7.000$/нед.]\n"
                                         f"🔎 Чтобы устроиться используйте \"работа [организация] устроиться [вакансия]\"")
                elif param2 == '1':
                    user[0]["Work"] = 1
                    user[0]["WorkCooldown"] = 0
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы устроились в ЖКХ дворником\n"
                                         f"Используйте \"Работать\", чтобы работать")
                elif param2 == '2':
                    user[0]["Work"] = 2
                    user[0]["WorkCooldown"] = 0
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы устроились в ЖКХ электриком\n"
                                         f"Используйте \"Работать\", чтобы работать")


@bot.on.message(text=["Работать", "работать"])
@bot.on.message(payload={"cmd": "cmd_worked"})
async def worked_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if user[0]["Work"] == 0:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), вы нигде не работаете!\n"
                                 f"Ипользуйте \"Работа\", чтобы устроиться на работу")
        elif user[0]["WorkCooldown"] == 7:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), рабочая неделя окончена 🚫\n"
                                 f"Ожидайте час, чтобы опять работать")
        elif user[0]["Energy"] <= 0:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы слишком устали 🚫\n"
                                 f"Ваша энергия: {general.change_number(user[0]['Energy'])}")
        else:
            if user[0]["Work"] == 1:
                earned_money = random.randint(100, 645)
                user[0]["Money"] += earned_money
                user[0]["WorkCooldown"] += 1
                user[0]["Energy"] -= 1
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), рабочий день окончен...\n\n"
                                     f"Ваш сегодняшний доход: {general.change_number(earned_money)}$\n"
                                     f"Ваш баланс: {general.change_number(user[0]['Money'])}$")
                UserAction.save_user(message.from_id, user)
            if user[0]["Work"] == 2:
                earned_money = random.randint(250, 1000)
                user[0]["Money"] += earned_money
                user[0]["WorkCooldown"] += 1
                user[0]["Energy"] -= 1
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), рабочий день окончен...\n\n"
                                     f"Ваш сегодняшний доход: {general.change_number(earned_money)}$\n"
                                     f"Ваш баланс: {general.change_number(user[0]['Money'])}$")
                UserAction.save_user(message.from_id, user)


# Top command
@bot.on.message(text=["Топ", "топ"])
@bot.on.message(payload={"cmd": "cmd_top"})
async def top_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        users = UserAction.get_users_top()
        top_numbers = ("1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟")
        top_text = ''
        for iteration, user in enumerate(users):
            top_text += f'\n{top_numbers[iteration]} @id{user["VK_ID"]} ({user["Name"]}) — {general.change_number(user["Rating"])}🏆'
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), топ-10 игроков: {top_text}")


# Clans commands
@bot.on.message(text=["Клан", "клан"])
@bot.on.message(text=["Клан <action>", "клан <action>"])
@bot.on.message(text=["Клан <action> <param>", "клан <action> <param>"])
@bot.on.message(text=["Клан <action> <param> <param2>", "клан <action> <param> <param2>"])
async def clan_handler(message: Message, info: UsersUserXtrCounters, action: Optional[str] = None,
                       param: Optional[str] = None, param2: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        clan = 0 if user[0]["ClanID"] == 0 else MainData.get_clan(user[0]["ClanID"])
        if action is None and user[0]["ClanID"] == 0:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}),\n"
                                 f"1⃣ Клан — информация о клане\n"
                                 f"2⃣ Клан создать [название] — стоимость {general.change_number(MainData.get_settings()[0]['ClanPrice'])}$\n"
                                 f"3⃣ Клан распустить — распустить клан\n"
                                 f"4⃣ Клан пригласить [ID игрока] — пригласить игрока в клан\n"
                                 f"5⃣ Клан исключить [ID игрока] — исключить игрока из клана\n"
                                 f"6⃣ Клан выйти — выйти из клана\n"
                                 f"7⃣ Клан принять/отклонить — принять/отклонить приглашение в клан\n"
                                 f"8⃣ Клан топ — рейтинг кланов\n"
                                 f"9⃣ Клан казна — история пополнения казны за сутки\n"
                                 f"🔟 Клан казна пополнить/снять [сумма] — пополнить/снять (из) казну(-ы) клана\n"
                                 f"1⃣1⃣ Клан изменить [название] — сменить название\n"
                                 f"1⃣2⃣ Клан состав — участники клана\n"
                                 f"1⃣3⃣ Клан магазмагазин — покупка войск для клана\n"
                                 f"1⃣4⃣ Клан атака — напасть на другой клан\n"
                                 f"1⃣5⃣ Клан ранг [ID игрока] — изменить ранг игроку\n"
                                 f"1⃣6⃣ Клан ризменить [ранг] [название] - изменить название ранга\n")
        elif action is None and user[0]["ClanID"] != 0:
            if clan[0]["GuardTime"] > 0:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), информация о клане «{clan[0]['Name']}»:\n\n"
                    f"📜 ID клана: {clan[0]['ID']}\n"
                    f"👑 Рейтинг клана: {clan[0]['Rating']}\n"
                    f"💰 В казне клана: {general.change_number(clan[0]['Money'])}$\n"
                    f"⚔ В клане состоит: {clan[0]['Players']}/50 участников\n"
                    f"🥇 Побед: {clan[0]['Victories']}, поражений: {clan[0]['Losses']}\n\n"
                    f"🔒 Щит: {time.strftime('%H ч. %M мин.', time.gmtime(clan[0]['GuardTime'] * 60)) if clan[0]['GuardTime'] >= 60 else time.strftime('%M мин.', time.gmtime(clan[0]['GuardTime'] * 60))}\n\n"
                    f"🛡 Войско:\n"
                    f"⠀🗡 Рыцарей: {clan[0]['Knights']}\n"
                    f"⠀🏹 Лучников: {clan[0]['Bowman']}\n\n"
                    f"👑 Создатель клана: "
                    f"@id{UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID']} "
                    f"({UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['Name']})\n")
            else:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), информация о клане «{clan[0]['Name']}»:\n\n"
                    f"📜 ID клана: {clan[0]['ID']}\n"
                    f"👑 Рейтинг клана: {clan[0]['Rating']}\n"
                    f"💰 В казне клана: {general.change_number(clan[0]['Money'])}$\n"
                    f"⚔ В клане состоит: {clan[0]['Players']}/50 участников\n"
                    f"🥇 Побед: {clan[0]['Victories']}, поражений: {clan[0]['Losses']}\n\n"
                    f"🛡 Войско:\n"
                    f"⠀🗡 Рыцарей: {clan[0]['Knights']}\n"
                    f"⠀🏹 Лучников: {clan[0]['Bowman']}\n\n"
                    f"👑 Создатель клана: "
                    f"@id{UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID']} "
                    f"({UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['Name']})\n")
        elif action.lower() == 'помощь':
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}),\n"
                                 f"1⃣ Клан — информация о клане\n"
                                 f"2⃣ Клан создать [название] — стоимость {general.change_number(MainData.get_settings()[0]['ClanPrice'])}$\n"
                                 f"3⃣ Клан распустить — распустить клан\n"
                                 f"4⃣ Клан пригласить [ID игрока] — пригласить игрока в клан\n"
                                 f"5⃣ Клан исключить [ID игрока] — исключить игрока из клана\n"
                                 f"6⃣ Клан выйти — выйти из клана\n"
                                 f"7⃣ Клан принять/отклонить — принять/отклонить приглашение в клан\n"
                                 f"8⃣ Клан топ — рейтинг кланов\n"
                                 f"9⃣ Клан казна — история пополнения казны за сутки\n"
                                 f"🔟 Клан казна пополнить/снять [сумма] — пополнить/снять (из) казну(-ы) клана\n"
                                 f"1⃣1⃣ Клан изменить [название] — сменить название\n"
                                 f"1⃣2⃣ Клан состав — участники клана\n"
                                 f"1⃣3⃣ Клан магазин — покупка войск для клана\n"
                                 f"1⃣4⃣ Клан атака — напасть на другой клан\n"
                                 f"1⃣5⃣ Клан ранг [ID игрока] — изменить ранг игроку\n"
                                 f"1⃣6⃣ Клан ризменить [ранг] [название] - изменить название ранга\n")
        elif action.lower() == 'создать':
            if user[0]["ClanID"] != 0:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), Вы уже состоите в клане {clan[0]['Name']}\n"
                    f"Чтобы покинуть клан, используйте: клан выйти")
            else:
                if param is None:
                    await message.answer(
                        f"@id{message.from_id} ({user[0]['Name']}), используйте: клан создать [название]\n"
                        f"Стоимость создания клана: {general.change_number(MainData.get_settings()[0]['ClanPrice'])}$")
                else:
                    if user[0]["Money"] < MainData.get_settings()[0]["ClanPrice"]:
                        await message.answer(
                            f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно денег для создания клана")
                    else:
                        if param2 is None:
                            user[0]["Money"] -= MainData.get_settings()[0]["ClanPrice"]
                            MainData.add_clan(Name=param, OwnerID=user[0]["ID"])
                            user_clan = MainData.get_clan_userid(user[0]["ID"])
                            user[0]["ClanID"] = user_clan[0]["ID"]
                            user[0]["ClanRank"] = 5
                            UserAction.save_user(message.from_id, user)
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), поздравляем 🎉\n"
                                                 f"Теперь у Вас есть свой клан {param}\n"
                                                 f"Чтобы узнать доступные команды, используйте: клан помощь")
                        else:
                            user[0]["Money"] -= MainData.get_settings()[0]["ClanPrice"]
                            MainData.add_clan(Name=param + ' ' + param2, OwnerID=user[0]["ID"])
                            user_clan = MainData.get_clan_userid(user[0]["ID"])
                            user[0]["ClanID"] = user_clan[0]["ID"]
                            user[0]["ClanRank"] = 5
                            UserAction.save_user(message.from_id, user)
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), поздравляем 🎉\n"
                                                 f"Теперь у Вас есть свой клан {param + ' ' + param2}\n"
                                                 f"Чтобы узнать доступные команды, используйте: клан помощь")
        elif action.lower() == 'распустить':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), у Вас нет клана")
            elif user[0]["ClanID"] != 0 and user[0]["ClanRank"] < 5:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав для роспуска клана")
            else:
                UserAction.kick_users_from_clan(ClanID=0, ClanRank=0, KickClanID=clan[0]["ID"])
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), Вы распустили свой клан {clan[0]['Name']}")
                MainData.remove_clan(clan[0]["ID"])
        elif action.lower() == 'пригласить':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanID"] != 0 and user[0]["ClanRank"] < 2:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав для приглашения игроков в данный клан")
            else:
                if param is None:
                    await message.answer(
                        f"@id{message.from_id} ({user[0]['Name']}), используйте: клан пригласить [ID игрока]")
                else:
                    if not general.isint(param):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID игрока должен быть числом")
                    else:
                        invite_user = UserAction.get_user_by_gameid(int(param))
                        if invite_user is False:
                            await message.answer(
                                f"@id{message.from_id} ({user[0]['Name']}), такого игрока не существует")
                        elif invite_user[0]["ClanID"] != 0:
                            await message.answer(
                                f"@id{message.from_id} ({user[0]['Name']}), игрока уже состоит в клане")
                        elif invite_user[0]["ClanRequest"] != 0:
                            await message.answer(
                                f"@id{message.from_id} ({user[0]['Name']}), игрока уже пригласили в клан")
                        else:
                            invite_user[0]["ClanRequest"] = clan[0]["ID"]
                            UserAction.save_user(invite_user[0]["VK_ID"], invite_user)
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы пригласили "
                                                 f"@id{invite_user[0]['VK_ID']} ({invite_user[0]['Name']}) в клан")
                            await message.answer(f"@id{invite_user[0]['VK_ID']} ({invite_user[0]['Name']}), "
                                                 f"@id{user[0]['VK_ID']} ({user[0]['Name']}) пригласил Вас в клан "
                                                 f"{clan[0]['Name']}\n\n"
                                                 f"🔎 Чтобы принять/отклонить приглашение, используйте: клан принять/отклонить",
                                                 user_id=invite_user[0]['VK_ID'])
        elif action.lower() == 'исключить':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanID"] != 0 and user[0]["ClanRank"] < 3:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав для исключения игроков из клана")
            else:
                if param is None:
                    await message.answer(
                        f"@id{message.from_id} ({user[0]['Name']}), используйте: клан исключить [ID игрока]")
                else:
                    if not general.isint(param):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID игрока должен быть числом")
                    else:
                        uninvite_user = UserAction.get_user_by_gameid(int(param))
                        if uninvite_user is False:
                            await message.answer(
                                f"@id{message.from_id} ({user[0]['Name']}), такого игрока не существует")
                        elif uninvite_user[0]["ClanID"] != clan[0]["ID"]:
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), в клане нет такого игрока")
                        elif uninvite_user[0]["ClanRank"] > 3 and user[0]["ClanRank"] != 5:
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                                 f"Вы не можете исключить администратора клана")
                        else:
                            uninvite_user[0]["ClanID"] = 0
                            uninvite_user[0]["ClanRank"] = 0
                            clan[0]["Players"] -= 1
                            UserAction.save_user(uninvite_user[0]["VK_ID"], uninvite_user)
                            MainData.save_clan(clan[0]["ID"], clan)
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы исключили "
                                                 f"@id{uninvite_user[0]['VK_ID']} ({uninvite_user[0]['Name']}) из клана")
                            await message.answer(f"@id{uninvite_user[0]['VK_ID']} ({uninvite_user[0]['Name']}), "
                                                 f"@id{user[0]['VK_ID']} ({user[0]['Name']}) исключил Вас из клана "
                                                 f"{clan[0]['Name']}\n\n", user_id=uninvite_user[0]['VK_ID'])
        elif action.lower() == 'выйти':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanRank"] == 5:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), создатель не может покинуть клан\n"
                                     f"Вы моежет распустить его: клан распустить")
            else:
                user[0]["ClanID"] = 0
                user[0]["ClanRank"] = 0
                clan[0]["Players"] -= 1
                UserAction.save_user(message.from_id, user)
                MainData.save_clan(clan[0]["ID"], clan)
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы покинули клан {clan[0]['Name']}")
                await message.answer(f"@id{UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID']} "
                                     f"({UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['Name']}), игрок "
                                     f"@id{user[0]['VK_ID']} ({user[0]['Name']}) покинул Ваш клан",
                                     user_id=UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID'])
        elif action.lower() == 'принять':
            if user[0]["ClanID"] != 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы уже состоите в клане")
            elif user[0]["ClanRequest"] == 0:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), Вам не поступало приглашений вступить в клан")
            else:
                user_clan = MainData.get_clan(user[0]["ClanRequest"])
                user[0]["ClanID"] = user[0]["ClanRequest"]
                user[0]["ClanRequest"] = 0
                user[0]["ClanRank"] = 1
                user_clan[0]["Players"] += 1
                UserAction.save_user(message.from_id, user)
                MainData.save_clan(user_clan[0]["ID"], user_clan)
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), Вы вступили в клан {user_clan[0]['Name']}")
                await message.answer(f"@id{UserAction.get_user_by_gameid(user_clan[0]['OwnerID'])[0]['VK_ID']} "
                                     f"({UserAction.get_user_by_gameid(user_clan[0]['OwnerID'])[0]['Name']}), игрок "
                                     f"@id{user[0]['VK_ID']} ({user[0]['Name']}) вступил в Ваш клан",
                                     user_id=UserAction.get_user_by_gameid(user_clan[0]['OwnerID'])[0]['VK_ID'])
        elif action.lower() == 'отклонить':
            if user[0]["ClanID"] != 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы состоите в клане")
            elif user[0]["ClanRequest"] == 0:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), Вам не поступало приглашений вступить в клан")
            else:
                user_clan = MainData.get_clan(user[0]["ClanRequest"])
                user[0]["ClanRequest"] = 0
                UserAction.save_user(message.from_id, user)
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                     f"Вы отказались вступить в клан {user_clan[0]['Name']}")
                await message.answer(f"@id{UserAction.get_user_by_gameid(user_clan[0]['OwnerID'])[0]['VK_ID']} "
                                     f"({UserAction.get_user_by_gameid(user_clan[0]['OwnerID'])[0]['Name']}), игрок "
                                     f"@id{user[0]['VK_ID']} ({user[0]['Name']}) отказался вступить в Ваш клан",
                                     user_id=UserAction.get_user_by_gameid(user_clan[0]['OwnerID'])[0]['VK_ID'])
        elif action.lower() == 'топ':
            clans = MainData.get_clans_top()
            top_numbers = ("1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟")
            top_text = ''
            if clans is False:
                await message.answer(f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), "
                                     f"в топе пока что нет кланов 😔")
            else:
                for iteration, clan_top in enumerate(clans):
                    top_text += f'\n{top_numbers[iteration]} {clan_top["Name"]} ({clan_top["Victories"]}/{clan_top["Losses"]}) — {clan_top["Rating"]}🏆'
                top_text += '\n\n📢 Рейтинг клана складывается из побед и поражений.'
                await message.answer(
                    f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), топ кланов: {top_text}")
        elif action.lower() == 'казна':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            else:
                if param is None or param2 is None:
                    temp_text = ''
                    payers = 0 if clan[0]["MoneyRefill"] == '0-0' else clan[0]["MoneyRefill"].split(',')[:-1]
                    if payers == 0:
                        await message.answer(
                            f"@id{message.from_id} ({user[0]['Name']}), казну еще никто не пополнял...\n\n"
                            f"🔎 Чтобы пополнить/снять, используйте \"клан казна пополнить/снять [сумма]\"")
                    else:
                        for payer in payers:
                            payer_user = UserAction.get_user_by_gameid(payer.split("-")[0])
                            if payer_user[0]["ClanRank"] == 5:
                                temp_text += f'\n🎖 @id{payer_user[0]["VK_ID"]} ' \
                                             f'({payer_user[0]["Name"]}) ' \
                                             f'({payer.split("-")[0]}) пополнил на {general.change_number(int(payer.split("-")[1]))}$'
                            elif payer_user[0]["ClanRank"] == 4:
                                temp_text += f'\n👑 @id{payer_user[0]["VK_ID"]} ' \
                                             f'({payer_user[0]["Name"]}) ' \
                                             f'({payer.split("-")[0]}) пополнил на {general.change_number(int(payer.split("-")[1]))}$'
                            else:
                                temp_text += f'\n🗿 @id{payer_user[0]["VK_ID"]} ' \
                                             f'({payer_user[0]["Name"]}) ' \
                                             f'({payer.split("-")[0]}) пополнил на {general.change_number(int(payer.split("-")[1]))}$'
                        await message.answer(
                            f"@id{message.from_id} ({user[0]['Name']}), последние 7 пополнений казны: {temp_text}\n\n"
                            f"🔎 Чтобы пополнить/снять, используйте \"клан казна пополнить/снять [сумма]\"")
                elif param.lower() == 'пополнить':
                    if not general.isint(param2):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), сумма должна быть числом")
                    elif user[0]["Money"] < int(param2):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), у Вас нет столько денег")
                    else:
                        user[0]["Money"] -= int(param2)
                        clan[0]["Money"] += int(param2)
                        if clan[0]["MoneyRefill"] == '0-0':
                            clan[0]["MoneyRefill"] = f'{user[0]["ID"]}-{param2},' if len(
                                clan[0]["MoneyRefill"].split(',')[:-1]) < 7 else f'{user[0]["ID"]}-{param2},'
                        else:
                            clan[0]["MoneyRefill"] = clan[0]["MoneyRefill"] + f'{user[0]["ID"]}-{param2},' if len(
                                clan[0]["MoneyRefill"].split(',')[:-1]) < 7 else f'{user[0]["ID"]}-{param2},'
                        UserAction.save_user(message.from_id, user)
                        MainData.save_clan(clan[0]["ID"], clan)
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                             f"Вы пополнили казну клана на {general.change_number(int(param2))}$")
                        await message.answer(f"@id{UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID']} "
                                             f"({UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['Name']}), игрок "
                                             f"@id{user[0]['VK_ID']} ({user[0]['Name']}) пополнил казну на {general.change_number(int(param2))}$",
                                             user_id=UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID'])
                elif param.lower() == 'снять':
                    if not general.isint(param2):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), сумма должна быть числом")
                    elif user[0]["ClanRank"] < 4:
                        await message.answer(
                            f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав для снятия денег с казны")
                    elif clan[0]["Money"] < int(param2):
                        await message.answer(
                            f"@id{message.from_id} ({user[0]['Name']}), в казне клана нет столько денег")
                    else:
                        user[0]["Money"] += int(param2)
                        clan[0]["Money"] -= int(param2)
                        UserAction.save_user(message.from_id, user)
                        MainData.save_clan(clan[0]["ID"], clan)
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                             f"Вы сняли из казны кланы {general.change_number(int(param2))}$")
                        await message.answer(f"@id{UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID']} "
                                             f"({UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['Name']}), игрок "
                                             f"@id{user[0]['VK_ID']} ({user[0]['Name']}) снял из казны {general.change_number(int(param2))}$",
                                             user_id=UserAction.get_user_by_gameid(clan[0]['OwnerID'])[0]['VK_ID'])
        elif action.lower() == 'изменить':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanRank"] < 4:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав, чтобы изменить название клана")
            else:
                if param is None:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), чтобы изменить название, "
                                         f"используйте: клан изменить [название]")
                else:
                    if param2 is None:
                        clan[0]["Name"] = param
                        MainData.save_clan(clan[0]["ID"], clan)
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                             f"Вы изменили название клана на {param}")
                    else:
                        clan[0]["Name"] = param + ' ' + param2
                        MainData.save_clan(clan[0]["ID"], clan)
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                             f"Вы изменили название клана на {param + ' ' + param2}")
        elif action.lower() == 'состав':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            else:
                clan_users = UserAction.get_users_clan(clan[0]["ID"])
                temp_text = ''
                ranks = {rank.split("-")[0]: rank.split("-")[1] for rank in clan[0]["Ranks"].split(',')[:-1]}
                for clan_user in clan_users:
                    if clan_user["ClanRank"] == 5:
                        temp_text += f'\n👑 @id{clan_user["VK_ID"]} ({clan_user["Name"]}) ({clan_user["ID"]}) - {ranks["5"]}'
                    elif clan_user["ClanRank"] == 4:
                        temp_text += f'\n🎖 @id{clan_user["VK_ID"]} ({clan_user["Name"]}) ({clan_user["ID"]}) - {ranks["4"]}'
                    elif clan_user["ClanRank"] == 3:
                        temp_text += f'\n🥇 @id{clan_user["VK_ID"]} ({clan_user["Name"]}) ({clan_user["ID"]}) - {ranks["3"]}'
                    elif clan_user["ClanRank"] == 2:
                        temp_text += f'\n🥈 @id{clan_user["VK_ID"]} ({clan_user["Name"]}) ({clan_user["ID"]}) - {ranks["2"]}'
                    else:
                        temp_text += f'\n🗿 @id{clan_user["VK_ID"]} ({clan_user["Name"]}) ({clan_user["ID"]}) - {ranks["1"]}'
                await message.answer(
                    f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), состав клана {clan[0]['Name']}: {temp_text}")
        elif action.lower() == 'ранг':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanRank"] < 3:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав, чтобы изменить название клана")
            else:
                ranks = {rank.split("-")[0]: rank.split("-")[1] for rank in clan[0]["Ranks"].split(',')[:-1]}
                if param is None or param2 is None:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), чтобы выдать ранг, "
                                         f"используйте: клан ранг [ID игрока] [ранг]\n\n"
                                         f"1 - {ranks['1']}\n"
                                         f"2 - {ranks['2']}\n"
                                         f"3 - {ranks['3']}\n"
                                         f"4 - {ranks['4']}\n"
                                         f"5 - {ranks['5']}")
                else:
                    if not general.isint(param):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID игрока должен быть числом")
                    elif not general.isint(param2):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ранг должен быть числом")
                    elif int(param2) > 5 or int(param2) < 1:
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ранг может быть от 1 до 5\n\n"
                                             f"1 - {ranks['1']}\n"
                                             f"2 - {ranks['2']}\n"
                                             f"3 - {ranks['3']}\n"
                                             f"4 - {ranks['4']}\n"
                                             f"5 - {ranks['5']}")
                    else:
                        rang_user = UserAction.get_user_by_gameid(param)
                        rang_user[0]["ClanRank"] = int(param2)
                        UserAction.save_user(rang_user[0]["VK_ID"], rang_user)
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                             f"Вы изменили игроку @id{rang_user[0]['VK_ID']} ({rang_user[0]['Name']}) "
                                             f"ранг на {param2} - {ranks[f'{param2}']}")
                        await message.answer(f"@id{rang_user[0]['VK_ID']} ({rang_user[0]['Name']}), "
                                             f"руководитель @id{user[0]['VK_ID']} ({user[0]['Name']}) "
                                             f"изменил Вам ранг на {param2} - {ranks[f'{param2}']}",
                                             user_id=rang_user[0]['VK_ID'])
        elif action.lower() == 'магазин':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanRank"] < 2:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав, чтобы использовать магазин для этого клана")
            else:
                if param is None or param2 is None:
                    if param == '3':
                        if clan[0]["Money"] < 1000000:
                            await message.answer(
                                f"@id{message.from_id} ({user[0]['Name']}), в казне клана недостаточно денег")
                        else:
                            clan[0]["Money"] -= 1000000
                            clan[0]["GuardTime"] += 1440
                            MainData.save_clan(clan[0]["ID"], clan)
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                                 f"Вы купили щит на сутки за "
                                                 f"{general.change_number(1000000)}$")
                    else:
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), доступный товар:\n"
                                             f"1. Рыцарь - 400.000$\n"
                                             f"2. Лучник - 600.000$\n"
                                             f"3. Щит на сутки - 1.000.000$\n"
                                             f"🔎 Купить: «Клан магазин [номер] [количество]»")
                else:
                    if not general.isint(param):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID товара должен быть числом")
                    elif not general.isint(param2):
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), количество долнжо быть числом")
                    else:
                        if param == '1':
                            if clan[0]["Money"] < 400000 * int(param2):
                                await message.answer(
                                    f"@id{message.from_id} ({user[0]['Name']}), в казне клана недостаточно денег")
                            else:
                                clan[0]["Money"] -= 400000 * int(param2)
                                clan[0]["Knights"] += int(param2)
                                MainData.save_clan(clan[0]["ID"], clan)
                                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                                     f"Вы купили {general.change_number(int(param2))} рыцаря(-ей) за "
                                                     f"{general.change_number(400000 * int(param2))}$")
                        elif param == '2':
                            if clan[0]["Money"] < 600000 * int(param2):
                                await message.answer(
                                    f"@id{message.from_id} ({user[0]['Name']}), в казне клана недостаточно денег")
                            else:
                                clan[0]["Money"] -= 600000 * int(param2)
                                clan[0]["Bowman"] += int(param2)
                                MainData.save_clan(clan[0]["ID"], clan)
                                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                                     f"Вы купили {general.change_number(int(param2))} лучника(-ов) за "
                                                     f"{general.change_number(600000 * int(param2))}$")
                        else:
                            await message.answer(
                                f"@id{message.from_id} ({user[0]['Name']}), такого товара не существует")
        elif action.lower() == 'атака':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanRank"] < 2:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав, чтобы атаковать")
            else:
                if clan[0]["TimeAttack"] > 0:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), атаковать можно раз в 10 минут")
                else:
                    clan_for_attack = [
                        random.choice(MainData.get_clans_attack(clan[0]["Rating"])) if MainData.get_clans_attack(
                            clan[0]["Rating"]) is not False else 0]
                    if clan_for_attack == 0:
                        await message.answer(
                            f"@id{message.from_id} ({user[0]['Name']}), не удалось найти подходящий для атаки клан...")
                    else:
                        clan[0]["GuardTime"] = 0
                        if (clan[0]["Knights"] + clan[0]["Bowman"]) < (
                                clan_for_attack[0]["Knights"] + clan_for_attack[0]["Bowman"]):
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                                 f"ваш клан потерпел поражение перед «{clan_for_attack[0]['Name']}», "
                                                 f"вы потеряли {math.trunc(clan[0]['Knights'] / 1.7) + math.trunc(clan[0]['Bowman'] / 1.7)} своего войска "
                                                 f"и одну единицу рейтинга ❌")
                            clan[0]["Knights"] = math.trunc(clan[0]["Knights"] / 1.7)
                            clan[0]["Bowman"] = math.trunc(clan[0]["Bowman"] / 1.7)
                            clan[0]["Rating"] = 0 if clan[0]["Rating"] - 1 < 1 else clan[0]["Rating"] - 1
                            clan[0]["Losses"] += 1
                            clan[0]["TimeAttack"] = 10
                            clan_for_attack[0]["Rating"] += 1
                            clan_for_attack[0]["Victories"] += 1
                            MainData.save_clan(clan[0]["ID"], clan)
                            MainData.save_clan(clan_for_attack[0]["ID"], clan_for_attack)
                        elif (clan[0]["Knights"] + clan[0]["Bowman"]) > (
                                clan_for_attack[0]["Knights"] + clan_for_attack[0]["Bowman"]):
                            take_money = math.trunc(clan_for_attack[0]["Money"] / random.randint(10, 20))
                            clan_for_attack[0]["Rating"] = 0 if clan[0]["Rating"] - 1 < 1 else clan[0]["Rating"] - 1
                            clan_for_attack[0]["Losses"] += 1
                            clan_for_attack[0]["GuardTime"] = 60
                            clan_for_attack[0]["Money"] -= take_money
                            clan[0]["Rating"] += 1
                            clan[0]["Victories"] += 1
                            clan[0]["TimeAttack"] = 10
                            clan[0]["Money"] += take_money
                            MainData.save_clan(clan[0]["ID"], clan)
                            MainData.save_clan(clan_for_attack[0]["ID"], clan_for_attack)
                            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                                 f"ваш клан одержал победу перед «{clan_for_attack[0]['Name']}», украдено: {general.change_number(take_money)}$. ✅")
                        else:
                            await message.answer(
                                f"@id{message.from_id} ({user[0]['Name']}), у Вас слишком мало войска, чтобы драться с этим кланом\n"
                                f"Используйте \"клан магазин\", чтобы приобрести войско")
        elif action.lower() == 'ризменить':
            if user[0]["ClanID"] == 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы не состоите в клане")
            elif user[0]["ClanRank"] < 5:
                await message.answer(
                    f"@id{message.from_id} ({user[0]['Name']}), у Вас недостаточно прав, чтобы изменять название рангов клана")
            else:
                if param is None or param2 is None:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), чтобы изменить название ранга, "
                                         f"используйте: клан ризменить [ранг(1-5)] [название]")
                else:
                    if ',' in param2 or '-' in param2:
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                             f"название ранга не должно сдержать \"-\" и \",\"\n\n"
                                             f"Чтобы изменить название ранга, "
                                             f"используйте: клан ризменить [ранг(1-5)] [название]")
                    else:
                        ranks = {rank.split("-")[0]: rank.split("-")[1] for rank in clan[0]["Ranks"].split(',')[:-1]}
                        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                             f"Вы изменили название ранга {param} ({ranks[param]}) на {param2}")
                        ranks[param] = param2
                        clan[0]["Ranks"] = ','.join(map(lambda rank: f'{rank[0]}-{rank[1]}', ranks.items())) + ','
                        MainData.save_clan(clan[0]["ID"], clan)
        else:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), проверьте правильность введенных данных!")


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
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if message.chat_id in chats:
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), раздел \"Разное\" 💡",
                keyboard=Keyboard(one_time=False, inline=True).schema(
                    [
                        [
                            {"label": "🚀 Игры", "type": "text", "payload": {"cmd": "cmd_games"}, "color": "secondary"},
                            {"label": "🖨 Реши", "type": "text", "payload": {"cmd": "cmd_equation"},
                             "color": "secondary"},
                            {"label": "📊 Курс", "type": "text", "payload": {"cmd": "cmd_course"}, "color": "secondary"}
                        ],
                        [
                            {"label": "🏆 Топ", "type": "text", "payload": {"cmd": "cmd_top"}, "color": "secondary"},
                            {"label": "🤝 Передать", "type": "text", "payload": {"cmd": "cmd_transfer"},
                             "color": "secondary"}
                        ],
                        [
                            {"label": "⚙ Настройки", "type": "text", "payload": {"cmd": "cmd_settings"},
                             "color": "primary"},
                            {"label": "◀ В главное меню", "type": "text", "payload": {"cmd": "cmd_mainmenu"},
                             "color": "positive"}
                        ]
                    ]
                ).get_json())
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
        chats = {ID["ChatID"] for ID in MainData.get_chats()}
        if message.chat_id in chats:
            await message.answer(
                f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), раздел \"Главное меню\" 💡",
                keyboard=Keyboard(one_time=False, inline=True).schema(
                    [
                        [
                            {"label": "📒 Профиль", "type": "text", "payload": {"cmd": "cmd_profile"},
                             "color": "primary"},
                            {"label": "💲 Баланс", "type": "text", "payload": {"cmd": "cmd_balance"},
                             "color": "secondary"},
                            {"label": "👑 Рейтинг", "type": "text", "payload": {"cmd": "cmd_rating"},
                             "color": "secondary"}
                        ],
                        [
                            {"label": "🛍 Магазин", "type": "text", "payload": {"cmd": "cmd_shop"},
                             "color": "secondary"},
                            {"label": "💰 Банк", "type": "text", "payload": {"cmd": "cmd_bank"}, "color": "secondary"}
                        ],
                        [
                            {"label": "❓ Помощь", "type": "text", "payload": {"cmd": "cmd_help"}, "color": "secondary"},
                            {"label": "💡 Разное", "type": "text", "payload": {"cmd": "cmd_other"},
                             "color": "secondary"}
                        ],
                        [
                            {"label": "🎁 Получить бонус", "type": "text", "payload": {"cmd": "cmd_bonus"},
                             "color": "positive"}
                        ]
                    ]
                ).get_json())
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


# Mining commands
@bot.on.message(text=["Добывать", "добывать"])
@bot.on.message(text=["Добывать <param>", "добывать <param>"])
async def mining_handler(message: Message, info: UsersUserXtrCounters, param: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if param is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                 f'используйте: добывать [железо/золото/алмазы/материю]')
        else:
            if user[0]["Energy"] <= 0:
                await message.answer(
                    f'@id{message.from_id} ({user[0]["Name"]}), Вы слишком устали, необходимо подождать 🚫\n'
                    f'Энергия восстанавливается единица в час\n')
            else:
                total_mined = random.randint(10, 50) if user[0]["Potion"] == 2 and user[0][
                    "PotionTime"] > 0 else random.randint(5, 20)
                if param == 'железо':
                    user[0]["Iron"] += total_mined
                    user[0]["Energy"] -= 1
                    user[0]["EXP"] += 1
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы добыли {total_mined} железа\n\n'
                                         f'У Вас:\n'
                                         f'⠀Железо: {user[0]["Iron"]} 🥈\n'
                                         f'⠀Энергия: {user[0]["Energy"]} ⚡\n'
                                         f'⠀Опыт: {user[0]["EXP"]} ⭐')
                elif param == 'золото':
                    if user[0]["EXP"] < 1000:
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), чтобы добывать золото Вам необходимо иметь 1000+ опыта 🚫\n'
                            f'У Вас {user[0]["EXP"]} ⭐')
                    else:
                        user[0]["Gold"] += total_mined
                        user[0]["Energy"] -= 1
                        user[0]["EXP"] += random.randint(1, 3)
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), Вы добыли {total_mined} золота\n\n'
                            f'У Вас:\n'
                            f'⠀Золото: {user[0]["Gold"]} 🏅\n'
                            f'⠀Энергия: {user[0]["Energy"]} ⚡\n'
                            f'⠀Опыт: {user[0]["EXP"]} ⭐')
                elif param == 'алмазы':
                    if user[0]["EXP"] < 2500:
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), чтобы добывать алмазы Вам необходимо иметь 2500+ опыта 🚫\n'
                            f'У Вас {user[0]["EXP"]} ⭐')
                    else:
                        user[0]["Diamond"] += total_mined
                        user[0]["Energy"] -= 1
                        user[0]["EXP"] += random.randint(2, 6)
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), Вы добыли {total_mined} алмаза(-ов)\n\n'
                            f'У Вас:\n'
                            f'⠀Алмазы: {user[0]["Diamond"]} 💎\n'
                            f'⠀Энергия: {user[0]["Energy"]} ⚡\n'
                            f'⠀Опыт: {user[0]["EXP"]} ⭐')
                elif param == 'материю':
                    if user[0]["EXP"] < 5000 and user[0]["RankLevel"] < 3:
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), чтобы добывать материю Вам необходимо иметь 5000+ опыта 🚫\n'
                            f'У Вас {user[0]["EXP"]} ⭐\n\n'
                            f'Вы так же можете приобресети Premium статус, чтобы добывать данный ресурс.\n'
                            f'Испоьзуйте: донат')
                    else:
                        user[0]["Matter"] += total_mined
                        user[0]["Energy"] -= 1
                        user[0]["EXP"] += random.randint(4, 8)
                        await message.answer(
                            f'@id{message.from_id} ({user[0]["Name"]}), Вы добыли {total_mined} материи\n\n'
                            f'У Вас:\n'
                            f'⠀Материя: {user[0]["Matter"]} 🎆\n'
                            f'⠀Энергия: {user[0]["Energy"]} ⚡\n'
                            f'⠀Опыт: {user[0]["EXP"]} ⭐')
                else:
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), проверьте правильность введенных данных')
                UserAction.save_user(message.from_id, user)


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
        case_prizes = [['exp', 'money'],
                       ['exp', 'money', 'btc'],
                       ['exp', 'money', 'btc', 'rating'],
                       ['exp', 'money', 'btc', 'rating', 'pet', 'business']]
        if case_type is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Ваши кейсы:\n'
                                 f'🥉 Bronze Case {general.change_number(user[0]["Bronze_Case"])} шт.\n'
                                 f'🥈 Silver Case {general.change_number(user[0]["Silver_Case"])} шт.\n'
                                 f'🥇 Gold Case {general.change_number(user[0]["Gold_Case"])} шт.\n'
                                 f'🏅 Premium Case {general.change_number(user[0]["Premium_Case"])} шт.\n\n'
                                 f'Команды доступные для кейсов:\n'
                                 f'кейсы [тип кейса (bronze, silver, gold, premium)] открыть')
        elif case_type == 'bronze':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '
                                     f'{general.change_number(user[0]["Bronze_Case"])} 🥉 Bronze Case\n\n'
                                     f'Что может выпасть:\n'
                                     f'- Опыт\n'
                                     f'- Деньги\n\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы bronze открыть')
            elif action == 'открыть':
                if user[0]["Bronze_Case"] < 1:
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Bronze Case 😔\n'
                        f'Для покупки, используйте: магазин кейсы')
                else:
                    user[0]["Bronze_Case"] -= 1
                    if random.choice(case_prizes[0]) == 'exp':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(10, 50)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                        else:
                            case_prize = random.randint(1, 20)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                    else:
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(6000, 15000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                        else:
                            case_prize = random.randint(500, 9000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Bronze Case 🎉\n'
                                         f'Ваш приз: {case_prize}')
        elif case_type == 'silver':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '
                                     f'{general.change_number(user[0]["Silver_Case"])} 🥈 Silver Case\n\n'
                                     f'Что может выпасть:\n'
                                     f'- Опыт\n'
                                     f'- Деньги\n'
                                     f'- Биткоины\n\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы silver открыть')
            elif action == 'открыть':
                if user[0]["Silver_Case"] < 1:
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Silver Case 😔\n'
                        f'Для покупки, используйте: магазин кейсы')
                else:
                    user[0]["Silver_Case"] -= 1
                    if random.choice(case_prizes[1]) == 'exp':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(50, 100)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                        else:
                            case_prize = random.randint(10, 50)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                    elif random.choice(case_prizes[1]) == 'money':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(35000, 65000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                        else:
                            case_prize = random.randint(10000, 59000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                    else:
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(10, 100)
                            user[0]["BTC"] += case_prize
                            case_prize = f'биткоины ({general.change_number(case_prize)}) ₿'
                        else:
                            case_prize = random.randint(1, 10)
                            user[0]["BTC"] += case_prize
                            case_prize = f'биткоины ({general.change_number(case_prize)}) ₿'
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Silver Case 🎉\n'
                                         f'Ваш приз: {case_prize}')
        elif case_type == 'gold':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '
                                     f'{general.change_number(user[0]["Gold_Case"])} 🥇 Gold Case\n\n'
                                     f'Что может выпасть:\n'
                                     f'- Опыт\n'
                                     f'- Деньги\n'
                                     f'- Биткоины\n'
                                     f'- Рейтинг\n\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы gold открыть')
            elif action == 'открыть':
                if user[0]["Gold_Case"] < 1:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Gold Case 😔\n'
                                         f'Для покупки, используйте: магазин кейсы')
                else:
                    user[0]["Gold_Case"] -= 1
                    if random.choice(case_prizes[2]) == 'exp':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(100, 300)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                        else:
                            case_prize = random.randint(50, 100)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                    elif random.choice(case_prizes[2]) == 'money':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(100000, 155000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                        else:
                            case_prize = random.randint(50000, 149000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                    elif random.choice(case_prizes[2]) == 'btc':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(30, 100)
                            user[0]["BTC"] += case_prize
                            case_prize = f'биткоины ({general.change_number(case_prize)}) ₿'
                        else:
                            case_prize = random.randint(5, 30)
                            user[0]["BTC"] += case_prize
                            case_prize = f'биткоины ({general.change_number(case_prize)}) ₿'
                    else:
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(2, 3)
                            user[0]["Rating"] += case_prize
                            case_prize = f'рейтинг ({general.change_number(case_prize)}) 👑'
                        else:
                            case_prize = random.randint(1, 2)
                            user[0]["Rating"] += case_prize
                            case_prize = f'рейтинг ({general.change_number(case_prize)}) 👑'
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Gold Case 🎉\n'
                                         f'Ваш приз: {case_prize}')
        elif case_type == 'premium':
            if action is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), у Вас '
                                     f'{general.change_number(user[0]["Premium_Case"])} 🥇 Premium Case\n\n'
                                     f'Что может выпасть:\n'
                                     f'- Опыт\n'
                                     f'- Деньги\n'
                                     f'- Биткоины\n'
                                     f'- Рейтинг\n'
                                     f'- 🎖 Лучший питомец\n'
                                     f'- 🏆 Лучший бизнес\n'
                                     f'Чтобы открыть, используйте:\n'
                                     f'кейсы premium открыть')
            elif action == 'открыть':
                if user[0]["Premium_Case"] < 1:
                    await message.answer(
                        f'@id{message.from_id} ({user[0]["Name"]}), у Вас нет ни одного Premium Case 😔\n'
                        f'Для покупки, используйте: донат')
                else:
                    user[0]["Premium_Case"] -= 1

                    if random.randint(1, 100000) == 1:
                        user[0]["Pet_Hunger"] = 100
                        user[0]["Pet_Joy"] = 100
                        user[0]["Pet_Fatigue"] = 0
                        user[1]["PetLevel"] = 1
                        user[1]["Pet"] = 14
                        case_prize = f'лучший питомец 🦠 Коронавирус'
                    elif random.randint(1, 1000000) == 1:
                        user[0]["Workers_In_Business"] = 0
                        user[0]["Money_In_Business"] = 0
                        user[1]["Business"] = 21
                        user[1]["BusinessLevel"] = 1
                        case_prize = f'лучший бизнес Межпланетный экспресс'
                    elif random.choice(case_prizes[3]) == 'exp':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(300, 600)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                        else:
                            case_prize = random.randint(100, 300)
                            user[0]["EXP"] += case_prize
                            case_prize = f'опыт ({general.change_number(case_prize)}) 🔥'
                    elif random.choice(case_prizes[3]) == 'money':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(200000, 400000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                        else:
                            case_prize = random.randint(100000, 300000)
                            user[0]["Money"] += case_prize
                            case_prize = f'деньги ({general.change_number(case_prize)}) 💵'
                    elif random.choice(case_prizes[3]) == 'btc':
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(50, 150)
                            user[0]["BTC"] += case_prize
                            case_prize = f'биткоины ({general.change_number(case_prize)}) ₿'
                        else:
                            case_prize = random.randint(10, 50)
                            user[0]["BTC"] += case_prize
                            case_prize = f'биткоины ({general.change_number(case_prize)}) ₿'
                    else:
                        if random.randint(1, 1000) == 1:
                            case_prize = random.randint(3, 5)
                            user[0]["Rating"] += case_prize
                            case_prize = f'рейтинг ({general.change_number(case_prize)}) 👑'
                        else:
                            case_prize = random.randint(1, 3)
                            user[0]["Rating"] += case_prize
                            case_prize = f'рейтинг ({general.change_number(case_prize)}) 👑'

                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), Вы открыли Premium Case 🎉\n'
                                         f'Ваш приз: {case_prize}')


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
            f"⠀1. репорты - посмотреть список репортов\n"
            f"⠀2. getbaninfo [ID] - узнать информацию о бане игрока\n"
            f"⠀3. get [ID] - узнать информацию об игроке\n"
            f"⠀4. ban [ID] [тип (игровой/репорт/трейд/топ)] [время (мин.)] - выдать игроку бан\n"
            f"⠀5. unban [ID] [тип (игровой/репорт/трейд/топ)] - разблокировать игрока\n"
            f"⠀6. статистика - общая статистика бота\n"
            f"⠀7. getid [ссылка] - узнать игровой ID игрока")
    elif user[0]["RankLevel"] == 5:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), команды модератора:\n"
            f"⠀1. репорты - посмотреть список репортов\n"
            f"⠀2. getbaninfo [ID] - узнать информацию о бане игрока\n"
            f"⠀3. get [ID] - узнать информацию об игроке\n"
            f"⠀4. ban [ID] [тип (игровой/репорт/трейд/топ)] [время (мин.)] - выдать игроку бан\n"
            f"⠀5. unban [ID] [тип (игровой/репорт/трейд/топ)] - разблокировать игрока\n"
            f"⠀6. статистика - общая статистика бота\n"
            f"⠀7. getid [ссылка] - узнать игровой ID игрока\n"
            f"⠀\nКоманды администратора:\n"
            f"⠀1. выдать [ID] [тип (деньги/рейтинг/биткоины/опыт)] [кол-во]\n"
            f"⠀2. setnick [ID] [ник] - изменить игроку ник")
    elif user[0]["RankLevel"] > 5:
        await message.answer(
            f"@id{message.from_id} ({UserAction.get_user(message.from_id)[0]['Name']}), команды модератора:\n"
            f"⠀1. репорты - посмотреть список репортов\n"
            f"⠀2. getbaninfo [ID] - узнать информацию о бане игрока\n"
            f"⠀3. get [ID] - узнать информацию об игроке\n"
            f"⠀4. ban [ID] [тип (игровой/репорт/трейд/топ)] [время (мин.)] - выдать игроку бан\n"
            f"⠀5. unban [ID] [тип (игровой/репорт/трейд/топ)] - разблокировать игрока\n"
            f"⠀6. статистика - общая статистика бота\n"
            f"⠀7. getid [ссылка] - узнать игровой ID игрока\n"
            f"\nКоманды администратора:\n"
            f"⠀1. выдать [ID] [тип (деньги/рейтинг/биткоины/опыт)] [кол-во]\n"
            f" 2. setnick [ID] [ник] - изменить игроку ник\n"
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
            f"\nСтатусы:\n"
            f"⠀1 - обычный игрок\n"
            f"⠀2 - VIP\n"
            f"⠀3 - Premium\n"
            f"⠀4 - Модератор\n"
            f"⠀5 - Администратор")


@bot.on.message(text=["getbaninfo"])
@bot.on.message(text=["getbaninfo <user_id>"])
async def getbaninfo_handler(message: Message, info: UsersUserXtrCounters, user_id: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    elif user_id is None:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'getbaninfo [ID]'")
    elif general.isint(user_id) is False:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID должно быть числом")
    else:
        temp_text = ''
        info_user = UserAction.get_user_by_gameid(int(user_id))
        if info_user is False:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), такого игрока не существует")
        else:
            if info_user[0]["Ban"] > 0:
                temp_text += f'\nИгрвой бан: {time.strftime("%H ч. %M мин.", time.gmtime(info_user[0]["Ban"] * 60)) if info_user[0]["Ban"] >= 60 else time.strftime("%M мин.", time.gmtime(info_user[0]["Ban"] * 60))}'
            if info_user[0]["BanReport"] > 0:
                temp_text += f'\nБан репорта: {time.strftime("%H ч. %M мин.", time.gmtime(info_user[0]["BanReport"] * 60)) if info_user[0]["BanReport"] >= 60 else time.strftime("%M мин.", time.gmtime(info_user[0]["BanReport"] * 60))}'
            if info_user[0]["BanTrade"] > 0:
                temp_text += f'\nБан трейда: {time.strftime("%H ч. %M мин.", time.gmtime(info_user[0]["BanTrade"] * 60)) if info_user[0]["BanTrade"] >= 60 else time.strftime("%M мин.", time.gmtime(info_user[0]["BanTrade"] * 60))}'
            if info_user[0]["BanTop"] > 0:
                temp_text += f'\nБан топа: {time.strftime("%H ч. %M мин.", time.gmtime(info_user[0]["BanTop"] * 60)) if info_user[0]["BanTop"] >= 60 else time.strftime("%M мин.", time.gmtime(info_user[0]["BanTop"] * 60))}'
            if info_user[0]["Ban"] > 0 or info_user[0]["BanReport"] > 0 or info_user[0]["BanTrade"] > 0 or info_user[0][
                "BanTop"] > 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                     f"информация о банах игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}):\n\n"
                                     f"{temp_text}")
            else:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                     f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) нет банов")


@bot.on.message(text=["get"])
@bot.on.message(text=["get <user_id>"])
async def get_handler(message: Message, info: UsersUserXtrCounters, user_id: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    elif user_id is None:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'get [ID]'")
    elif general.isint(user_id) is False:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID должно быть числом")
    else:
        temp_text = ''
        info_user = UserAction.get_user_by_gameid(int(user_id))

        if info_user is False:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), такого игрока не существует")
        else:
            temp_text += f'🔎 ID: {info_user[0]["ID"]}\n'

            # Rank
            if info_user[0]["RankLevel"] == 2:
                temp_text += f'🔥 VIP игрок\n'
            elif info_user[0]["RankLevel"] == 3:
                temp_text += f'🔮 Premium игрок\n'
            elif info_user[0]["RankLevel"] == 4:
                temp_text += f'🌀 Модератор\n'
            elif info_user[0]["RankLevel"] >= 5:
                temp_text += f'👑 Администратор\n'

            # Main info
            if info_user[0]["EXP"] > 0:
                temp_text += f'⭐ Опыта: {general.change_number(info_user[0]["EXP"])}\n'
            temp_text += f'⚡ Энергия: {general.change_number(info_user[0]["Energy"])}\n'
            if info_user[0]["Money"] > 0:
                temp_text += f'💰 Денег: {general.change_number(info_user[0]["Money"])}$\n'
            if info_user[0]["BTC"] > 0:
                temp_text += f'🌐 Биткоинов: {general.change_number(info_user[0]["BTC"])}₿\n'
            if info_user[0]["Rating"] > 0:
                temp_text += f'👑 Рейтинг: {general.change_number(info_user[0]["Rating"])}\n'
            if info_user[0]["Marriage_Partner"] > 0:
                temp_text += f'💖 Партнер: @id{UserAction.get_user_by_gameid(info_user[0]["Marriage_Partner"])[0]["VK_ID"]}' \
                             f' ({UserAction.get_user_by_gameid(info_user[0]["Marriage_Partner"])[0]["Name"]})\n'
            # Property
            temp_text += f'\n🔑 Имущество:\n'
            if info_user[1]["Car"] > 0:
                temp_text += f'⠀🚗 Машина: {MainData.get_data("cars")[info_user[1]["Car"] - 1]["CarName"]}\n'
            if info_user[1]["Motorcycle"] > 0:
                temp_text += f'⠀🏍 Мотоцикл: {MainData.get_data("motorcycles")[info_user[1]["Motorcycle"] - 1]["MotoName"]}\n'
            if info_user[1]["Yacht"] > 0:
                temp_text += f'⠀🛥 Яхта: {MainData.get_data("yachts")[info_user[1]["Yacht"] - 1]["YachtName"]}\n'
            if info_user[1]["Airplane"] > 0:
                temp_text += f'⠀✈ Самолет: ' \
                             f'{MainData.get_data("airplanes")[info_user[1]["Airplane"] - 1]["AirplaneName"]}\n'
            if info_user[1]["Helicopter"] > 0:
                temp_text += f'⠀🚁 Вертолет: ' \
                             f'{MainData.get_data("helicopters")[info_user[1]["Helicopter"] - 1]["HelicopterName"]}\n'
            if info_user[1]["House"] > 0:
                temp_text += f'⠀🏠 Дом: {MainData.get_data("houses")[info_user[1]["House"] - 1]["HouseName"]}\n'
            if info_user[1]["Apartment"] > 0:
                temp_text += f'⠀🌇 Квартира: ' \
                             f'{MainData.get_data("apartments")[info_user[1]["Apartment"] - 1]["ApartmentName"]}\n'
            if info_user[1]["Business"] > 0:
                temp_text += f'⠀💼 Бизнес: ' \
                             f'{MainData.get_data("businesses")[info_user[1]["Business"] - 1]["BusinessName"]}\n'
            if info_user[1]["Pet"] > 0:
                temp_text += f'⠀{MainData.get_data("pets")[info_user[1]["Pet"] - 1]["PetIcon"]} Питомец: ' \
                             f'{MainData.get_data("pets")[info_user[1]["Pet"] - 1]["PetName"]}\n'
            if info_user[1]["Farms"] > 0:
                temp_text += f'⠀🔋 Фермы: {MainData.get_data("farms")[info_user[1]["FarmsType"] - 1]["FarmName"]} ' \
                             f'({general.change_number(info_user[1]["Farms"])} шт.)\n'
            if info_user[1]["Phone"] > 0:
                temp_text += f'⠀📱 Телефон: {MainData.get_data("phones")[info_user[1]["Phone"] - 1]["PhoneName"]}\n'

            # Potion effect
            if info_user[0]["Potion"] > 0 and info_user[0]["PotionTime"] > 0:
                temp_text += f'\n🍹 Эффект от зелья:\n'
                if info_user[0]["Potion"] == 1:
                    temp_text += f'⠀🍀 Зелье удачи\n'
                    temp_text += f'⠀🕛 Время действия: {time.strftime("%M мин.", time.gmtime(info_user[0]["PotionTime"] * 60))}\n'
                elif info_user[0]["Potion"] == 2:
                    temp_text += f'⠀⚒ Зелье шахтера\n'
                    temp_text += f'⠀🕛 Время действия: {time.strftime("%M мин.", time.gmtime(info_user[0]["PotionTime"] * 60))}\n'
                elif info_user[0]["Potion"] == 3:
                    temp_text += f'⠀❌ Зелье неудачи\n'
                    temp_text += f'⠀🕛 Время действия: {time.strftime("%M мин.", time.gmtime(info_user[0]["PotionTime"] * 60))}\n'

            # Mined resource
            if info_user[0]["Iron"] > 0 or info_user[0]["Gold"] > 0 or info_user[0]["Diamond"] > 0 or info_user[0][
                "Matter"] > 0:
                temp_text += f'\n🔦 Ресурсы:\n'
                if info_user[0]["Iron"] > 0:
                    temp_text += f'⠀🥈 Железо: {general.change_number(info_user[0]["Iron"])} ед.\n'
                if info_user[0]["Gold"] > 0:
                    temp_text += f'⠀🏅 Золото: {general.change_number(info_user[0]["Gold"])} ед.\n'
                if info_user[0]["Diamond"] > 0:
                    temp_text += f'⠀💎 Алмазы: {general.change_number(info_user[0]["Diamond"])} ед.\n'
                if info_user[0]["Matter"] > 0:
                    temp_text += f'⠀🎆 Материя: {general.change_number(user[0]["Matter"])} ед.\n'

            # Registration date
            temp_text += f'\n📗 Дата регистрации: {info_user[0]["Register_Data"].strftime("%d.%m.%Y, %H:%M:%S")}\n'
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                 f"информация о игроке @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}):\n\n"
                                 f"{temp_text}")


@bot.on.message(text=["getid"])
@bot.on.message(text=["getid <vk_id>"])
async def get_handler(message: Message, info: UsersUserXtrCounters, vk_id: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    elif vk_id is None:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'getid [VK_ID]'")
    elif general.isint(vk_id) is False:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), VK_ID должно быть числом")
    else:
        info_user = UserAction.get_user(int(vk_id))

        if info_user is False:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), такого игрока не существует")
        else:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                 f"Игровой ID у @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) - {info_user[0]['ID']}")


@bot.on.message(text=["ban"])
@bot.on.message(text=["ban <user_id> <ban_type> <ban_time>"])
async def getbaninfo_handler(message: Message, info: UsersUserXtrCounters,
                             user_id: Optional[str] = None,
                             ban_type: Optional[str] = None, ban_time: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    elif user_id is None or ban_type is None or ban_time is None:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                             f"используйте 'ban [ID] [тип (игровой/репорт/трейд/топ)] [время (мин.)]'")
    elif general.isint(user_id) is False or general.isint(ban_time) is False:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID и время должны быть числом")
    else:
        info_user = UserAction.get_user_by_gameid(int(user_id))
        if info_user is False:
            await message.answer(f"@id{message.from_id} ({user[0]['Name']}), такого игрока не существует")
        else:
            if ban_type == 'игровой':
                if info_user[0]["Ban"] > 0:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                         f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                         f"уже есть иговой бан")
                else:
                    info_user[0]["Ban"] += int(ban_time)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                         f'Вы выдали игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) '
                                         f'игровой бан на {time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}')
                    await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                         f'администратор @id{message.from_id} ({user[0]["Name"]}) выдал Вам игровой бан на '
                                         f'{time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}',
                                         user_id=info_user[0]["VK_ID"])
            if ban_type == 'репорт':
                if info_user[0]["BanReport"] > 0:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                         f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                         f"уже есть бан репорта")
                else:
                    info_user[0]["BanReport"] += int(ban_time)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                         f'Вы выдали игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) '
                                         f'бан репорта на {time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}')
                    await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                         f'администратор @id{message.from_id} ({user[0]["Name"]}) выдал Вам бан репорта на '
                                         f'{time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}',
                                         user_id=info_user[0]["VK_ID"])
            if ban_type == 'трейд':
                if info_user[0]["BanTrade"] > 0:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                         f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                         f"уже есть бан трейда")
                else:
                    info_user[0]["BanTrade"] += int(ban_time)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                         f'Вы выдали игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) '
                                         f'бан трейда на {time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}')
                    await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                         f'администратор @id{message.from_id} ({user[0]["Name"]}) выдал Вам бан трейда на '
                                         f'{time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}',
                                         user_id=info_user[0]["VK_ID"])
            if ban_type == 'топ':
                if info_user[0]["BanTop"] > 0:
                    await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                         f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                         f"уже есть бан топа")
                else:
                    info_user[0]["BanTop"] += int(ban_time)
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                         f'Вы выдали игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) '
                                         f'бан топа на {time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}')
                    await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                         f'администратор @id{message.from_id} ({user[0]["Name"]}) выдал Вам бан топа на '
                                         f'{time.strftime("%H ч. %M мин.", time.gmtime(int(ban_time) * 60)) if int(ban_time) >= 60 else time.strftime("%M мин.", time.gmtime(int(ban_time) * 60))}',
                                         user_id=info_user[0]["VK_ID"])
            UserAction.save_user(info_user[0]["VK_ID"], info_user)


@bot.on.message(text=["unban"])
@bot.on.message(text=["unban <user_id> <ban_type>"])
async def unban_handler(message: Message, info: UsersUserXtrCounters,
                        user_id: Optional[str] = None, ban_type: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    elif user_id is None or ban_type is None:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                             f"используйте 'unban [ID] [тип (игровой/репорт/трейд/топ)]'")
    elif general.isint(user_id) is False:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID должны быть числом")
    else:
        info_user = UserAction.get_user_by_gameid(int(user_id))
        if ban_type == 'игровой':
            if info_user[0]["Ban"] <= 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                     f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                     f"нет бана")
            else:
                info_user[0]["Ban"] = 0
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                     f'Вы сняли игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) игровой бан')
                await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                     f'администратор @id{message.from_id} ({user[0]["Name"]}) снял Вам игровой бан',
                                     user_id=info_user[0]["VK_ID"])
        if ban_type == 'репорт':
            if info_user[0]["BanReport"] <= 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                     f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                     f"нет бана репорта")
            else:
                info_user[0]["BanReport"] = 0
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                     f'Вы сняли игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) бан репорта')
                await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                     f'администратор @id{message.from_id} ({user[0]["Name"]}) снял Вам бан репорта',
                                     user_id=info_user[0]["VK_ID"])
        if ban_type == 'трейд':
            if info_user[0]["BanTrade"] <= 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                     f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                     f"нет бана трейда")
            else:
                info_user[0]["BanTrade"] = 0
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                     f'Вы сняли игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) бан трейда')
                await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                     f'администратор @id{message.from_id} ({user[0]["Name"]}) снял Вам бан трейда',
                                     user_id=info_user[0]["VK_ID"])
        if ban_type == 'топ':
            if info_user[0]["BanTop"] <= 0:
                await message.answer(f"@id{message.from_id} ({user[0]['Name']}), "
                                     f"у игрока @id{info_user[0]['VK_ID']} ({info_user[0]['Name']}) "
                                     f"нет бана топа")
            else:
                info_user[0]["BanTop"] = 0
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                     f'Вы сняли игроку @id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}) бан топа')
                await message.answer(f'@id{info_user[0]["VK_ID"]} ({info_user[0]["Name"]}), '
                                     f'администратор @id{message.from_id} ({user[0]["Name"]}) снял Вам бан топа',
                                     user_id=info_user[0]["VK_ID"])
        UserAction.save_user(info_user[0]["VK_ID"], info_user)


@bot.on.message(text=["Статистика", "статистика"])
async def statistic_handler(message: Message, info: UsersUserXtrCounters):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 6:
        return True
    else:
        temp_text = ''
        top_user_with_ban_top = UserAction.custom_query('SELECT ID, Name, Money FROM users WHERE BanTop>0 ORDER BY Money DESC LIMIT 1')
        top_user = UserAction.custom_query('SELECT ID, Name, Money FROM users WHERE BanTop<1 ORDER BY Money DESC LIMIT 1')
        top_btc_user = UserAction.custom_query('SELECT ID, Name, BTC FROM users ORDER BY BTC DESC LIMIT 1')
        temp_text += f"😸 Всего игроков: {general.change_number(len(UserAction.custom_query('SELECT * FROM users')))}\n"
        temp_text += f"⛔ Заблокировано: {general.change_number(len(UserAction.custom_query('SELECT * FROM users WHERE Ban>0')))}\n"
        temp_text += f"💰 Сумма всех денег игроков: {general.change_number(int(UserAction.custom_query('SELECT SUM(Money) FROM users')[0]['SUM(Money)']))}$\n"
        temp_text += f"💳 Сумма всех денег в банке игроков: {general.change_number(int(UserAction.custom_query('SELECT SUM(Bank_Money) FROM users')[0]['SUM(Bank_Money)']))}$\n"
        temp_text += f"🔋 Сумма всех ферм игроков: {general.change_number(int(UserAction.custom_query('SELECT SUM(BTC_In_Farms) FROM users')[0]['SUM(BTC_In_Farms)']))}₿\n"
        temp_text += f"👑 Сумма всего рейтинга игроков: {general.change_number(int(UserAction.custom_query('SELECT SUM(Rating) FROM users')[0]['SUM(Rating)']))}\n"
        if top_user_with_ban_top is True:
            temp_text += f"🔱 Самый богатый игрок[WITH BAN]: " \
                         f"{top_user_with_ban_top[0]['Name']}[{top_user_with_ban_top[0]['ID']}] - " \
                         f"{general.change_number(top_user_with_ban_top[0]['Money'])}$\n"
        temp_text += f"🔱 Самый богатый игрок[WITHOUT BAN]: {top_user[0]['Name']}[{top_user[0]['ID']}] - " \
                     f"{general.change_number(top_user[0]['Money'])}$\n"
        temp_text += f"🔱 Самое большое кол-во биткоинов у: {top_btc_user[0]['Name']}[{top_btc_user[0]['ID']}] - {top_btc_user[0]['BTC']}₿\n"
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), общая статистика бота:\n"
                             f"{temp_text}\n"
                             f"Created by Kinder\n"
                             f"Version: 0.8.5 (Beta)\n "
                             f"Copyright ©{date.today().year}")


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


# Admins commands
@bot.on.message(text=["Рассылка", "рассылка"])
@bot.on.message(text=["Рассылка <send_type>", "рассылка <send_type>"])
@bot.on.message(text=["Рассылка <send_type> <text>", "рассылка <send_type> <text>"])
@bot.on.message(text=["Рассылка <send_type> <wall> <text>", "рассылка <send_type> <wall> <text>"])
async def admin_mailing_handler(message: Message, info: UsersUserXtrCounters,
                                send_type: Optional[str] = None, text: Optional[str] = None,
                                wall: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 5:
        return True
    else:
        users = UserAction.get_users_with_notifications()
        users_id = []
        users_id.extend(map(lambda x: x["VK_ID"], UserAction.get_users_with_notifications()))
        users_count = 0
        if send_type is None or text is None:
            await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                 f'используйте: рассылка [тип(сообщения/поста)] [текст]')
        elif send_type == 'сообщения':
            if users is False:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), некому рассылать сообщения')
            else:
                if wall is None:
                    for chunk in general.chunks(users_id):
                        await bot.api.messages.send(peer_ids=','.join([str(i) for i in chunk]),
                                                    message=f'📢 {text}\n\n'
                                                            f'❗ Это автоматическая рассылка\n'
                                                            f'🔕 Чтобы отключить уведомления, используйте "Настройки"',
                                                    random_id=message.id)
                        users_count += 1
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                         f'сообщение с текстом {text} успешно разослано '
                                         f'{users_count} пользователю(-ям)"')
                else:
                    for chunk in general.chunks(users_id):
                        await bot.api.messages.send(peer_ids=','.join([str(i) for i in chunk]),
                                                    message=f'📢 {wall + " " + text}\n\n'
                                                            f'❗ Это автоматическая рассылка\n'
                                                            f'🔕 Чтобы отключить уведомления, используйте "Настройки"',
                                                    random_id=message.id)
                        users_count += 1
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                         f'сообщение с текстом \n\n{wall + " " + text}\n\n успешно разослано '
                                         f'{users_count} пользователю(-ям)"')
        elif send_type == 'поста':
            if users is False:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), некому рассылать пост')
            else:
                if 'wall-' not in wall:
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), для рассылки поста, используйте: '
                                         f'рассылка поста [пост(wall-000000000_00)] [текст]\n'
                                         f'Пост обязатно должен быть указан так "wall-000000000_00"')
                else:
                    for chunk in general.chunks(users_id):
                        await bot.api.messages.send(peer_ids=','.join([str(i) for i in chunk]),
                                                    message=f'📢 {text}\n\n'
                                                            f'❗ Это автоматическая рассылка\n'
                                                            f'🔕 Чтобы отключить уведомления, используйте "Настройки"',
                                                    random_id=message.id, attachment=wall)
                        users_count += 1
                    await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), '
                                         f'пост vk.com/{wall} с текстом \n\n{text}\n\n успешно разослан '
                                         f'{users_count} пользователю(-ям)"')


@bot.on.message(text=["setnick"])
@bot.on.message(text=["setnick <user_id>"])
@bot.on.message(text=["setnick <user_id> <nick>"])
async def setnick_handler(message: Message, info: UsersUserXtrCounters,
                          user_id: Optional[str] = None, nick: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 5:
        return True
    elif user_id is None or nick is None:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'setnick [ID] [ник]'")
    elif general.isint(user_id) is False:
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID должно быть числом")
    else:
        change_user = UserAction.get_user_by_gameid(int(user_id))
        change_user[0]["Name"] = nick
        UserAction.save_user(change_user[0]["VK_ID"], change_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы изменили игркоку "
                             f"@id{change_user[0]['VK_ID']} ({change_user[0]['Name']}) ник на {nick}")
        await message.answer(f"@id{change_user[0]['VK_ID']} ({change_user[0]['Name']}), "
                             f"администратор изменил вам ник на {nick}", user_id=change_user[0]["VK_ID"])


@bot.on.message(text=["выдать"])
@bot.on.message(text=["выдать <user_id>"])
@bot.on.message(text=["выдать <user_id> <type_giving>"])
@bot.on.message(text=["выдать <user_id> <type_giving> <count>"])
async  def admin_give_handler(message: Message, info: UsersUserXtrCounters,
                              user_id: Optional[int] = None, type_giving: Optional[str] = None,
                              count: Optional[int] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]['RankLevel'] < 5:
        return True
    elif user_id is None or type_giving is None or count is None:
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'выдать [ID] [тип (деньги/рейтинг/биткоины/опыт)] [кол-во]'")
    elif not general.isint(user_id) or not general.isint(count):
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID и количество доджны быть цифрами")
    giving_user = UserAction.get_user_by_gameid(int(user_id))
    if giving_user is False:
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), такого пользователя не существует")
    if type_giving == "деньги":
        giving_user[0]["Money"] += int(count)
        UserAction.save_user(giving_user[0]["VK_ID"], giving_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}) {general.change_number(int(count))}$")
        await message.answer(f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}), "
                             f"администратор выдал Вам {general.change_number(int(count))}$", user_id=giving_user[0]["VK_ID"])
    elif type_giving == "рейтинг":
        giving_user[0]["Rating"] += int(count)
        UserAction.save_user(giving_user[0]["VK_ID"], giving_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}) {general.change_number(int(count))} рейтинга")
        await message.answer(f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}), "
                             f"администратор выдал Вам {general.change_number(int(count))} рейтинга", user_id=giving_user[0]["VK_ID"])
    elif type_giving == "биткоины":
        giving_user[0]["BTC"] += int(count)
        UserAction.save_user(giving_user[0]["VK_ID"], giving_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}) {general.change_number(int(count))}₿")
        await message.answer(f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}), "
                             f"администратор выдал Вам {general.change_number(int(count))}₿", user_id=giving_user[0]["VK_ID"])
    elif type_giving == "опыт":
        giving_user[0]["EXP"] += int(count)
        UserAction.save_user(giving_user[0]["VK_ID"], giving_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}) {general.change_number(int(count))} опыта")
        await message.answer(f"@id{giving_user[0]['VK_ID']} ({giving_user[0]['Name']}), "
                             f"администратор выдал Вам {general.change_number(int(count))} опыта", user_id=giving_user[0]["VK_ID"])
    else:
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), проверьте правильность введнных данныых")


# FD commands
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
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'add_property [тип]'")
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
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), проверьте правильность введенных данных!")


@bot.on.message(text=["измранг"])
@bot.on.message(text=["измранг <user_id>"])
@bot.on.message(text=["измранг <user_id> <rank>"])
async def admin_give_rank_handler(message: Message, info: UsersUserXtrCounters,
                                 user_id: Optional[int] = None, rank: Optional[int] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 6:
        return True
    elif user_id is None or rank is None:
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), используйте 'измранг [ID] [значение]'")
    elif not general.isint(user_id) or not general.isint(rank):
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), ID и значение должны быть цифрами")
    give_rank_user = UserAction.get_user_by_gameid(int(user_id))
    if give_rank_user is False:
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), такого пользователя не существует")
    if rank == '1':
        give_rank_user[0]["RankLevel"] = 1
        UserAction.save_user(give_rank_user[0]['VK_ID'], give_rank_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}) статус игрока")
        await message.answer(f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}), "
                             f"администратор выдал Вам статус игрока", user_id=give_rank_user[0]["VK_ID"])
    elif rank == '2':
        give_rank_user[0]["RankLevel"] = 2
        UserAction.save_user(give_rank_user[0]['VK_ID'], give_rank_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}) VIP статус")
        await message.answer(f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}), "
                             f"администратор выдал Вам VIP статус", user_id=give_rank_user[0]["VK_ID"])
    elif rank == '3':
        give_rank_user[0]["RankLevel"] = 3
        UserAction.save_user(give_rank_user[0]['VK_ID'], give_rank_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}) Premium статус")
        await message.answer(f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}), "
                             f"администратор выдал Вам Premium статус", user_id=give_rank_user[0]["VK_ID"])
    elif rank == '4':
        give_rank_user[0]["RankLevel"] = 4
        UserAction.save_user(give_rank_user[0]['VK_ID'], give_rank_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}) статус модератора")
        await message.answer(f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}), "
                             f"администратор выдал Вам статус модератора", user_id=give_rank_user[0]["VK_ID"])
    elif rank == '5':
        give_rank_user[0]["RankLevel"] = 5
        UserAction.save_user(give_rank_user[0]['VK_ID'], give_rank_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}) статус администратора")
        await message.answer(f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}), "
                             f"администратор выдал Вам статус администратора", user_id=give_rank_user[0]["VK_ID"])
    elif rank == '6':
        give_rank_user[0]["RankLevel"] = 6
        UserAction.save_user(give_rank_user[0]['VK_ID'], give_rank_user)
        await message.answer(f"@id{message.from_id} ({user[0]['Name']}), Вы выдали игркоку "
                             f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}) статус основателя")
        await message.answer(f"@id{give_rank_user[0]['VK_ID']} ({give_rank_user[0]['Name']}), "
                             f"администратор выдал Вам статус основателя", user_id=give_rank_user[0]["VK_ID"])
    else:
        return await message.answer(f"@id{message.from_id} ({user[0]['Name']}), проверьте правильность введенных данных!")


# RP Commands
@bot.on.message(text=["<rp_command>"])
@bot.on.message(text=["<rp_command> <action_name>"])
async def rp_commands_handler(message: Message, info: UsersUserXtrCounters, rp_command: Optional[str] = None,
                              action_name: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id, info.first_name)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: "
                             f"{info.first_name}\nВаш игровой ID: {UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if rp_command.lower() == 'обнять':
            if action_name is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: обнять [имя]')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), вы обняли {action_name} 🤗')
        elif rp_command.lower() == 'поцеловать':
            if action_name is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: поцеловать [имя]')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), вы поцеловали {action_name} 😚')
        elif rp_command.lower() == 'ударить':
            if action_name is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: ударить [имя]')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), вы ударили {action_name} 🤜🏻')
        elif rp_command.lower() == 'изнасиловать':
            if action_name is None:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), используйте: изнасиловать [имя]')
            else:
                await message.answer(f'@id{message.from_id} ({user[0]["Name"]}), вы изнасиловали {action_name} 🔞')


# noinspection PyTypeChecker
@bot.on.raw_event(GroupEventType.GROUP_JOIN, dataclass=GroupTypes.GroupJoin)
async def group_join_handler(event: GroupTypes.GroupJoin):
    await bot.api.messages.send(peer_id=event.object.user_id, message="Спасибо за подписку!", random_id=0,
                                keyboard=START_KEYBOARD)


# noinspection PyTypeChecker
# @bot.on.raw_event(GroupEventType.MESSAGE_NEW, dataclass=GroupTypes.MessageNew)
# async def add_in_chat_handler(event: GroupTypes.MessageNew):
#     print(event.object.message.peer_id)
#     MainData.add_chat(ChatID=event.object.message.chat_id)
#     await bot.api.messages.send(peer_id=event.object.message.peer_id, message=event.object.message.title, random_id=0)

async def widget_update_handler():
    while True:
        time.sleep(300)
        users = UserAction.get_users_top()
        widget_top = {"title": "🔝 Лучшие игоки 🔝",
                      "head":
                          [
                              {"text": "Ник игрока 📛", "align": "left"},
                              {"text": "Деньги 💵", "align": "center"},
                              {"text": "Рейтинг 🏆", "align": "right"}
                          ],
                      "body": []
                      }
        for user in users:
            widget_top["body"].append([
                {"icon_id": f"id{user['VK_ID']}", "text": f"{user['Name']}", "url": f"vk.com/id{user['VK_ID']}"},
                {"text": f"{general.change_number(user['Money'])}$"},
                {'text': f'{general.change_number(user["Rating"])}'}])
        await widget.api.app_widgets.update(code=f'return {widget_top};', type="table")


def start_update_widget():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(widget_update_handler())


Thread(target=start_update_widget).start()
bot.labeler.message_view.register_middleware(NoBotMiddleware())
bot.labeler.message_view.register_middleware(RegistrationMiddleware())
bot.labeler.message_view.register_middleware(InfoMiddleware())
bot.run_forever()
