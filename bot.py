import configparser
import logging
import random
from typing import Optional, Any, List

from vkbottle import GroupEventType, GroupTypes, Keyboard, VKAPIError, ABCHandler, ABCView, \
    BaseMiddleware, Callback, \
    CtxStorage
from vkbottle.bot import Bot, Message
from vkbottle_types.objects import UsersUserXtrCounters

import classes.mysql

mysql = classes.mysql.MySQL()
dummy_db = CtxStorage()
config = configparser.ConfigParser()
config.read("data/vk_config.ini")

# Logs
logging.basicConfig(filename="logs/logs.log")

# VK Connection
bot = Bot(config["VK_DATA"]["GROUP_TOKEN"])

logging.basicConfig(level=logging.INFO)

START_KEYBOARD = (
    Keyboard(one_time=False).add(Callback("❓ Помощь", payload={"cmd": "cmd_help"})).get_json()
)
MAIN_KEYBOARD = Keyboard(one_time=False).schema(
    [
        [{"label": "Профиль", "type": "text", "color": "positive"}],
        [
            {"label": "Помощь", "type": "text", "color": "primary"},
            {"label": "Тест 1", "type": "text", "color": "primary"},
            {"label": "Тест 2", "type": "text", "color": "primary"},
            {"label": "Тест 3", "type": "text", "color": "primary"},
        ],
    ]
).get_json()


# Subs classes
class NoBotMiddleware(BaseMiddleware):
    async def pre(self, message: Message):
        return message.from_id > 0  # True / False


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


# Bot commands
@bot.on.message(text=["Начать", "Старт", "начать", "старт"])
@bot.on.message(payload={"cmd": "cmd_start"})
async def start_handler(message: Message, info: UsersUserXtrCounters):
    if not mysql.check_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        mysql.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{mysql.check_user(message.from_id)[0]}")
    else:
        await message.answer(f"Вы уже зарегистрированы в боте!\nИспользуйте команду \"Помощь\", для получения списка "
                             f"команд")


@bot.on.message(text=["Помощь", "помощь"])
@bot.on.message(payload={"cmd": "cmd_help"})
async def help_handler(message: Message, info: UsersUserXtrCounters):
    if not mysql.check_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        mysql.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{mysql.check_user(message.from_id)[0]}")
    else:
        await message.answer(f"@id{message.from_id} ({info.first_name}), мои команды:\n🎉 Развлекательные:\n⠀⠀😐 "
                             f"Анекдот\n⠀⠀↪ Переверни [фраза]\n⠀⠀🔮 Шар [фраза]\n⠀⠀📊 Инфа [фраза]\n⠀⠀⚖ Выбери [фраза] "
                             f"или [фраза2]\n\n🚀 Игры:\n⠀⠀🎲 Кубик [1-6]\n⠀⠀🎰 Казино [сумма]\n⠀⠀📈 Трейд ["
                             f"вверх/вниз] [сумма]\n⠀⠀🥛 Стаканчик [1-3] [сумма]\n⠀⠀🦅 Монетка [орёл/решка] ["
                             f"сумма]\n⠀⠀📦 Кейсы\n\n💼 Бизнес:\n⠀⠀📃 Бизнесы [1/2] - список бизнесов\n⠀⠀📈 Бизнес - "
                             f"статистика\n⠀⠀💵 Бизнес снять [кол-во] - снять деньги со счёта\n⠀⠀👷 Бизнес нанять - "
                             f"нанять рабочих\n\n🌽 Питомцы:\n⠀⠀🐒 Питомец - информация\n⠀⠀🐪 Питомец поход\n⠀⠀🌟 "
                             f"Питомец улучшить\n\n🔥 Полезное:\n⠀⠀📠 Реши [пример]\n⠀⠀📊 Курс\n⠀⠀🆕 /кнопки\n\n💡 "
                             f"Разное:\n⠀⠀📒 Профиль\n⠀⠀⚔ Клан\n⠀⠀🍹 Зелья\n⠀⠀💲 Баланс\n⠀⠀💰 Банк\n⠀⠀💳 Банк помощь - все "
                             f"команды банка\n⠀⠀👑 Рейтинг - ваш рейтинг\n⠀⠀🏆 Топ\n⠀⠀✒ Ник [ник/вкл/выкл]\n⠀⠀🛍 "
                             f"Магазин\n⠀⠀💸 Продать [предмет]\n⠀⠀🔋 Ферма - биткоин ферма\n⠀⠀🤝 Передать [ID] ["
                             f"сумма]\n⠀⠀💎 Бонус - ежедневный бонус\n⠀⠀👥 Реn\n⠀⠀🏆 Реф топ\n⠀⠀🎁 Донат\n\n🆘 Репорт ["
                             f"фраза] - ошибки или пожелания", keyboard=MAIN_KEYBOARD)


@bot.on.message(text=["Профиль", "профиль"])
@bot.on.message(payload={"cmd": "cmd_profile"})
async def profile_handler(message: Message, info: UsersUserXtrCounters):
    if not mysql.check_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        mysql.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{mysql.check_user(message.from_id)[0]}")
    else:
        user = mysql.check_user(message.from_id)

        temp_message = f'@id{message.from_id} ({info.first_name}), Ваш профиль:\n'
        temp_message += f'🔎 ID: {user[0]["ID"]}\n'
        # Check rank
        if user[0]["Rank"] == 2:
            temp_message += f'🔥 VIP игрок\n'
        elif user[0]["Rank"] == 3:
            temp_message += f'🔮 Premium игрок\n'
        elif user[0]["Rank"] == 4:
            temp_message += f'🌀 Модератор\n'
        elif user[0]["Rank"] >= 5:
            temp_message += f'👑 Администратор\n'
        # Basic check
        if user[0]["EXP"] > 0:
            temp_message += f'⭐ Опыта: {user[0]["EXP"]}\n'
        if user[0]["Money"] > 0:
            temp_message += f'💰 Денег: {user[0]["Money"]}\n'
        if user[0]["BTC"] > 0:
            temp_message += f'🌐 Биткоинов: {user[0]["BTC"]}\n'
        if user[0]["Rating"] > 0:
            temp_message += f'👑 Рейтинг: {user[0]["Rating"]}\n'

        temp_message += f'📗 Дата регистрации: {user[0]["Register_Data"].strftime("%d.%m.%Y, %H:%M:%S")}\n'
        await message.answer(temp_message)


@bot.on.message(text=["Банк <item1> <item2>", "банк <item1> <item2>"])
@bot.on.message(payload={"cmd": "cmd_bank"})
async def bank_handler(message: Message, info: UsersUserXtrCounters, item1: Optional[str] = None,
                       item2: Optional[int] = None):
    if not mysql.check_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        mysql.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{mysql.check_user(message.from_id)[0]}")
    else:
        user = mysql.check_user(message.from_id)
        print(1)
        if item1 is None and item2 is None:
            print(1)
            await message.answer(
                f'@id{message.from_id} ({info.first_name}), на Вашем банковском счете: {user[0]["Bank_Money"]}')
        elif item1 == "положить":
            if item2 is None:
                await message.answer(f'@id{message.from_id} ({info.first_name}), используйте "банк "положить" "сумма", '
                                     f'чтобы положить деньги на счет"')
            else:
                user[0]["Bank_Money"] += int(item2)
                user[0]["Money"] -= int(item2)
                mysql.update_user(message.from_id, user)
                await message.answer(
                    f'@id{message.from_id} ({info.first_name}), Вы пополнили свой банковский счет на {item2}$')


@bot.on.message(text=["Выбери <item1> <item2>", "выбери <item1> <item2>"])
@bot.on.message(payload={"cmd": "cmd_selecttext"})
async def selecttext_handler(message: Message, info: UsersUserXtrCounters, item1: Optional[str] = None,
                             item2: Optional[str] = None):
    if not mysql.check_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        mysql.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{mysql.check_user(message.from_id)[0]}")
    else:
        if item1 is None or item2 is None:
            await message.answer(f"Используйте: выбери \"фраза 1\" \"фраза 2\"")
        else:
            temp_var = random.randint(0, 1)
            if temp_var == 0:
                await message.answer(
                    f"@id{message.from_id} ({info.first_name}), мне кажется лучше \"{item1}\", чем \"{item2}\"")
            elif temp_var == 1:
                await message.answer(
                    f"@id{message.from_id} ({info.first_name}), мне кажется лучше \"{item2}\", чем \"{item1}\"")


# If you need to make handler respond for 2 different rule set you can
# use double decorator like here it is or use filters (OrFilter here)
# @bot.on.message(text=["/съесть <item>", "/съесть"])
# @bot.on.message(payload={"cmd": "eat"})
# async def eat_handler(message: Message, item: Optional[str] = None):
#     if item is None:
#         item = random.choice(EATABLE)
#     await message.answer(f"Ты съел <<{item}>>!", keyboard=KEYBOARD)


@bot.on.raw_event(GroupEventType.GROUP_JOIN, dataclass=GroupTypes.GroupJoin)
async def group_join_handler(event: GroupTypes.GroupJoin):
    try:
        await bot.api.messages.send(
            peer_id=event.object.user_id, message="Спасибо за подписку!", random_id=0, keyboard=MAIN_KEYBOARD
        )
    except VKAPIError(901):
        pass


# Runs loop > loop.run_forever() > with tasks created in loop_wrapper before,
# read the loop wrapper documentation to comprehend this > tools/loop-wrapper.
# The main polling task for bot is bot.run_polling()
bot.labeler.message_view.register_middleware(NoBotMiddleware())
bot.labeler.message_view.register_middleware(RegistrationMiddleware())
bot.labeler.message_view.register_middleware(InfoMiddleware())
bot.run_forever()
