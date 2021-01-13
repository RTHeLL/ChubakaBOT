import configparser
import logging
import random
from typing import Optional, Any, List

from vkbottle import GroupEventType, GroupTypes, Keyboard, ABCHandler, ABCView, \
    BaseMiddleware, \
    CtxStorage, Text
from vkbottle.bot import Bot, Message
from vkbottle_types.objects import UsersUserXtrCounters

import classes.mysql

UserAction = classes.mysql.UserAction()
MainData = classes.mysql.MainData()
dummy_db = CtxStorage()
config = configparser.ConfigParser()
config.read("data/vk_config.ini")

# Logs
logging.basicConfig(filename="logs/logs.log")

# VK Connection
bot = Bot(config["VK_DATA"]["GROUP_TOKEN"])

logging.basicConfig(level=logging.INFO)

START_KEYBOARD = (
    Keyboard(one_time=False).add(Text("❓ Помощь", payload={"cmd": "cmd_help"})).get_json()
)

MAIN_KEYBOARD = Keyboard(one_time=False, inline=False).schema(
    [
        [
            {"label": "📒 Профиль", "type": "text", "payload": {"cmd": "cmd_profile"}, "color": "positive"},
            {"label": "💲 Баланс", "type": "text", "color": "secondary"},
            {"label": "👑 Рейтинг", "type": "text", "color": "secondary"}
        ],
        [
            {"label": "🛍 Магазин", "type": "text", "payload": {"cmd": "cmd_shop"}, "color": "secondary"},
            {"label": "💰 Банк", "type": "text", "payload": {"cmd": "cmd_bank"}, "color": "secondary"}
        ],
        [
            {"label": "🏆 Топ", "type": "text", "color": "secondary"},
            {"label": "🤝 Передать", "type": "text", "color": "secondary"}
        ],
        [
            {"label": "❓ Помощь", "type": "text", "payload": {"cmd": "cmd_help"}, "color": "secondary"},
            {"label": "💡 Разное", "type": "text", "color": "secondary"}
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


# Check for number function
def isint(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


fliptext_dict = {'q': 'q', 'w': 'ʍ', 'e': 'ǝ', 'r': 'ɹ', 't': 'ʇ', 'y': 'ʎ', 'u': 'u', 'i': 'ᴉ', 'o': 'o', 'p': 'p',
                 'a': 'ɐ', 's': 's', 'd': 'd', 'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ', 'j': 'ɾ', 'k': 'ʞ', 'l': 'l', 'z': 'z',
                 'x': 'x', 'c': 'ɔ', 'v': 'ʌ', 'b': 'b', 'n': 'n', 'm': 'ɯ',
                 'й': 'ņ', 'ц': 'ǹ', 'у': 'ʎ', 'к': 'ʞ', 'е': 'ǝ', 'н': 'н', 'г': 'ɹ', 'ш': 'm', 'щ': 'm', 'з': 'ε',
                 'х': 'х', 'ъ': 'q', 'ф': 'ф', 'ы': 'ıq', 'в': 'ʚ', 'а': 'ɐ', 'п': 'u', 'р': 'd', 'о': 'о', 'л': 'v',
                 'д': 'ɓ', 'ж': 'ж', 'э': 'є', 'я': 'ʁ', 'ч': 'һ', 'с': 'ɔ', 'м': 'w', 'и': 'и', 'т': 'ɯ', 'ь': 'q',
                 'б': 'ƍ', 'ю': 'oı'}


# User commands
@bot.on.message(text=["Начать", "Старт", "начать", "старт"])
@bot.on.message(payload={"cmd": "cmd_start"})
async def start_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        await message.answer(f"Вы уже зарегистрированы в боте!\nИспользуйте команду \"Помощь\", для получения списка "
                             f"команд")


@bot.on.message(text=["Помощь", "помощь"])
@bot.on.message(payload={"cmd": "cmd_help"})
async def help_handler(message: Message, info: UsersUserXtrCounters):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
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
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id), UserAction.get_user_property(message.from_id)

        temp_message = f'@id{message.from_id} ({info.first_name}), Ваш профиль:\n'
        temp_message += f'🔎 ID: {user[0][0]["ID"]}\n'
        # Check RankLevel
        if user[0][0]["RankLevel"] == 2:
            temp_message += f'🔥 VIP игрок\n'
        elif user[0][0]["RankLevel"] == 3:
            temp_message += f'🔮 Premium игрок\n'
        elif user[0][0]["RankLevel"] == 4:
            temp_message += f'🌀 Модератор\n'
        elif user[0][0]["RankLevel"] >= 5:
            temp_message += f'👑 Администратор\n'
        # Basic check
        if user[0][0]["EXP"] > 0:
            temp_message += f'⭐ Опыта: {user[0][0]["EXP"]}\n'
        if user[0][0]["Money"] > 0:
            temp_message += f'💰 Денег: {user[0][0]["Money"]}\n'
        if user[0][0]["BTC"] > 0:
            temp_message += f'🌐 Биткоинов: {user[0][0]["BTC"]}\n'
        if user[0][0]["Rating"] > 0:
            temp_message += f'👑 Рейтинг: {user[0][0]["Rating"]}\n'
        # Property
        temp_message += f'\n🔑 Имущество:\n'
        if user[1][0]["Car"] > 0:
            temp_message += f'⠀🚗 Машина: {MainData.get_data("cars")[user[1][0]["Car"] - 1]["CarName"]}\n'
        if user[1][0]["Yacht"] > 0:
            temp_message += f'⠀🛥 Яхта: {MainData.get_data("yachts")[user[1][0]["Yacht"] - 1]["YachtName"]}\n'
        if user[1][0]["Airplane"] > 0:
            temp_message += f'⠀✈ Самолет: ' \
                            f'{MainData.get_data("airplanes")[user[1][0]["Airplane"] - 1]["AirplaneName"]}\n'
        if user[1][0]["Helicopter"] > 0:
            temp_message += f'⠀🚁 Вертолет: ' \
                            f'{MainData.get_data("helicopters")[user[1][0]["Helicopter"] - 1]["HelicopterName"]}\n'
        if user[1][0]["House"] > 0:
            temp_message += f'⠀🏠 Дом: {MainData.get_data("houses")[user[1][0]["House"] - 1]["HouseName"]}\n'
        if user[1][0]["Apartment"] > 0:
            temp_message += f'⠀🌇 Квартира: ' \
                            f'{MainData.get_data("apartments")[user[1][0]["Apartment"] - 1]["ApartmentName"]}\n'
        if user[1][0]["Business"] > 0:
            temp_message += f'⠀💼 Бизнес: ' \
                            f'{MainData.get_data("businesses")[user[1][0]["Business"] - 1]["BusinessName"]}\n'
        if user[1][0]["Pet"] > 0:
            temp_message += f'⠀{MainData.get_data("pets")[user[1][0]["Pet"] - 1]["PetIcon"]} Питомец: ' \
                            f'{MainData.get_data("pets")[user[1][0]["Pet"] - 1]["PetName"]}\n'
        if user[1][0]["Farms"] > 0:
            temp_message += f'⠀🔋 Фермы: {MainData.get_data("farms")[user[1][0]["FarmsType"] - 1]["FarmName"]} ' \
                            f'({user[1][0]["Farms"]} шт.)\n'
        if user[1][0]["Phone"] > 0:
            temp_message += f'⠀📱 Телефон: {MainData.get_data("phones")[user[1][0]["Phone"] - 1]["PhoneName"]}\n'

        temp_message += f'\n📗 Дата регистрации: {user[0][0]["Register_Data"].strftime("%d.%m.%Y, %H:%M:%S")}\n'
        await message.answer(temp_message)


@bot.on.message(text=["Банк", "банк"])
@bot.on.message(text=["Банк <item1>", "банк <item1>"])
@bot.on.message(text=["Банк <item1> <item2:int>", "банк <item1> <item2:int>"])
@bot.on.message(payload={"cmd": "cmd_bank"})
async def bank_handler(message: Message, info: UsersUserXtrCounters, item1: Optional[str] = None,
                       item2: Optional[int] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        if item1 is None and item2 is None:
            await message.answer(
                f'@id{message.from_id} ({info.first_name}), на Вашем банковском счете: {user[0]["Bank_Money"]}$')
        elif item1 == "положить":
            if item2 is None or not isint(item2):
                await message.answer(f'@id{message.from_id} ({info.first_name}), используйте "банк положить [сумма], '
                                     f'чтобы положить деньги на счет')
            else:
                if user[0]["Money"] < item2:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Bank_Money"] += item2
                    user[0]["Money"] -= item2
                    UserAction.save_user(message.from_id, user)
                    await message.answer(
                        f'@id{message.from_id} ({info.first_name}), Вы пополнили свой банковский счет на {item2}$')
        elif item1 == "снять":
            if item2 is None or not isint(item2):
                await message.answer(f'@id{message.from_id} ({info.first_name}), используйте "банк снять [сумма], '
                                     f'чтобы снять деньги со счета')
            else:
                if user[0]["Bank_Money"] < item2:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), на Вашем банковском счете нет '
                                         f'столько денег!')
                else:
                    user[0]["Bank_Money"] -= item2
                    user[0]["Money"] += item2
                    UserAction.save_user(message.from_id, user)
                    await message.answer(
                        f'@id{message.from_id} ({info.first_name}), Вы сняли со своего банковского счета {item2}$')
        else:
            await message.answer(f'@id{message.from_id} ({info.first_name}), используйте "банк [положить/снять] [сумма]'
                                 f'"')


@bot.on.message(text=["Магазин", "магазин"])
@bot.on.message(text=["Магазин <category>", "магазин <category>"])
@bot.on.message(text=["Магазин <category> купить <product>", "магазин <category> купить <product>"])
@bot.on.message(payload={"cmd": "cmd_shop"})
async def shop_handler(message: Message, info: UsersUserXtrCounters, category: Optional[str] = None,
                       product: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        user = UserAction.get_user(message.from_id)
        shop_data = MainData.get_shop_data()
        temp_text = ''
        if category is None:
            await message.answer(f'@id{message.from_id} ({info.first_name}), разделы магазина:\n'
                                 f'🚙 Транспорт:\n'
                                 f'⠀🚗 Машины\n'
                                 f'⠀🛥 Яхты\n'
                                 f'⠀🛩 Самолеты\n'
                                 f'⠀🚁 Вертолеты\n'
                                 f'\n🏘 Недвижимость:\n'
                                 f'⠀🏠 Дома\n'
                                 f'⠀🌇 Квартиры\n'
                                 f'\n📌 Остальное:\n'
                                 f'⠀📱 Телефоны\n'
                                 f'⠀🔋 Фермы\n'
                                 f'⠀👑 Рейтинг [кол-во] - 150млн$\n'
                                 f'⠀💼 Бизнесы\n'
                                 f'⠀🌐 Биткоин [кол-во]\n'
                                 f'⠀🐸 Питомцы'
                                 f'\n🔎 Для просмотра категории используйте "магазин [категория]".\n'
                                 f'🔎 Для покупки используйте "магазин [категория] купить [номер товара]".\n')
        elif category.lower() == 'машины':
            if product is None:
                for car in shop_data[0]:
                    temp_text += f'\n🔸 {car["ID"]}. {car["CarName"]} [{car["CarPrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), машины: {temp_text}\n\n '
                                     f'❓ Для покупки введите "машина [номер]"')
            else:
                if user[0]["Money"] < shop_data[0][int(product)-1]["CarPrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[0][int(product)-1]["CarPrice"]
                    user[1]["Car"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[0][int(product)-1]["CarName"]} за {shop_data[0][int(product)-1]["CarPrice"]}$')
        elif category.lower() == 'яхты':
            if product is None:
                for yacht in shop_data[1]:
                    temp_text += f'\n🔸 {yacht["ID"]}. {yacht["YachtName"]} [{yacht["YachtPrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), яхты: {temp_text}\n\n '
                                     f'❓ Для покупки введите "яхта [номер]"')
            else:
                if user[0]["Money"] < shop_data[1][int(product)-1]["YachtPrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[1][int(product)-1]["YachtPrice"]
                    user[1]["Yacht"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[1][int(product)-1]["YachtName"]} за {shop_data[1][int(product)-1]["YachtPrice"]}$')
        elif category.lower() == 'самолеты':
            if product is None:
                for airplane in shop_data[2]:
                    temp_text += f'\n🔸 {airplane["ID"]}. {airplane["AirplaneName"]} [{airplane["AirplanePrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), самолеты: {temp_text}\n\n '
                                     f'❓ Для покупки введите "яхта [номер]"')
            else:
                if user[0]["Money"] < shop_data[2][int(product)-1]["AirplanePrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[2][int(product)-1]["AirplanePrice"]
                    user[1]["Airplane"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[2][int(product)-1]["AirplaneName"]} за '
                                         f'{shop_data[2][int(product)-1]["AirplanePrice"]}$')
        elif category.lower() == 'вертолеты':
            if product is None:
                for helicopters in shop_data[3]:
                    temp_text += f'\n🔸 {helicopters["ID"]}. {helicopters["HelicopterName"]} ' \
                                 f'[{helicopters["HelicopterPrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), вертолеты: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин вертолеты купить [номер]"')
            else:
                if user[0]["Money"] < shop_data[3][int(product)-1]["HelicopterPrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[3][int(product)-1]["HelicopterPrice"]
                    user[1]["Helicopter"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[3][int(product)-1]["HelicopterName"]} за '
                                         f'{shop_data[3][int(product)-1]["HelicopterPrice"]}$')
        elif category.lower() == 'дома':
            if product is None:
                for houses in shop_data[4]:
                    temp_text += f'\n🔸 {houses["ID"]}. {houses["HouseName"]} [{houses["HousePrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), дома: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин дома купить [номер]"')
            else:
                if user[0]["Money"] < shop_data[4][int(product)-1]["HousePrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[4][int(product)-1]["HousePrice"]
                    user[1]["House"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[4][int(product)-1]["HouseName"]} за '
                                         f'{shop_data[4][int(product)-1]["HousePrice"]}$')
        elif category.lower() == 'квартиры':
            if product is None:
                for apartments in shop_data[5]:
                    temp_text += f'\n🔸 {apartments["ID"]}. {apartments["ApartmentName"]} [{apartments["ApartmentPrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), квартиры: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин квартиры купить [номер]"')
            else:
                if user[0]["Money"] < shop_data[5][int(product)-1]["ApartmentPrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[5][int(product)-1]["ApartmentPrice"]
                    user[1]["Apartment"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[5][int(product)-1]["ApartmentName"]} за '
                                         f'{shop_data[5][int(product)-1]["ApartmentPrice"]}$')
        elif category.lower() == 'телефоны':
            if product is None:
                for phones in shop_data[6]:
                    temp_text += f'\n🔸 {phones["ID"]}. {phones["PhoneName"]} [{phones["PhonePrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), телефоны: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин телефоны купить [номер]"')
            else:
                if user[0]["Money"] < shop_data[6][int(product)-1]["PhonePrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[6][int(product)-1]["PhonePrice"]
                    user[1]["Phone"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[6][int(product)-1]["PhoneName"]} за '
                                         f'{shop_data[6][int(product)-1]["PhonePrice"]}$')
        elif category.lower() == 'фермы':
            if product is None:
                for farms in MainData.get_data("farms"):
                    temp_text += f'\n🔸 {farms["ID"]}. {farms["FarmName"]} - {farms["FarmBTCPerHour"]} ₿/час ' \
                                 f'[{farms["FarmPrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), фермы: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин фермы купить [номер]"')
            else:
                if user[0]["Money"] < shop_data[7][int(product)-1]["FarmPrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[7][int(product)-1]["FarmPrice"]
                    user[1]["Farms"] += 1
                    user[1]["FarmsType"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[7][int(product)-1]["FarmName"]} за '
                                         f'{shop_data[7][int(product)-1]["FarmPrice"]}$')
        elif category.lower() == 'рейтинг':
            if product is None:
                await message.answer(f'@id{message.from_id} ({info.first_name}), ❓ Для покупки введите "магазин рейтинг купить [кол-во]"')
            else:
                if user[0]["Money"] < int(product)*150000000:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= int(product)*150000000
                    user[0]["Rating"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{product} рейтинга за {int(product)*150000000}$')
        elif category.lower() == 'бизнесы':
            if product is None:
                for businesses in shop_data[8]:
                    temp_text += f'\n🔸 {businesses["ID"]}. {businesses["BusinessName"]} [{businesses["BusinessPrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), бизнесы: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин бизнесы купить [номер]"')
            else:
                if user[0]["Money"] < shop_data[8][int(product)-1]["BusinessPrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[8][int(product)-1]["BusinessPrice"]
                    user[1]["Business"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[8][int(product)-1]["BusinessName"]} за '
                                         f'{shop_data[8][int(product)-1]["BusinessPrice"]}$')
        elif category.lower() == 'биткоин':
            await message.answer(f'@id{message.from_id} ({info.first_name}), ❓ Для покупки введите "биткоин [кол-во]"')
        elif category.lower() == 'питомцы':
            if product is None:
                for pets in shop_data[9]:
                    temp_text += f'\n🔸 {pets["ID"]}. {pets["PetIcon"]} {pets["PetName"]} [{pets["PetPrice"]}$]'
                await message.answer(f'@id{message.from_id} ({info.first_name}), питомцы: {temp_text}\n\n '
                                     f'❓ Для покупки введите "магазин питомцы купить [номер]"')
            else:
                if user[0]["Money"] < shop_data[9][int(product)-1]["PetPrice"]:
                    await message.answer(f'@id{message.from_id} ({info.first_name}), у Вас нет столько денег!')
                else:
                    user[0]["Money"] -= shop_data[9][int(product)-1]["PetPrice"]
                    user[1]["Pet"] = product
                    UserAction.save_user(message.from_id, user)
                    await message.answer(f'@id{message.from_id} ({info.first_name}), Вы приобрели себе '
                                         f'{shop_data[9][int(product)-1]["PetIcon"]} '
                                         f'{shop_data[9][int(product)-1]["PetName"]} за '
                                         f'{shop_data[9][int(product)-1]["PetPrice"]}$')
        else:
            await message.answer(f"@id{message.from_id} ({info.first_name}), проверьте правильность введенных данных!")


# Other commands
@bot.on.message(text=["Выбери <item1> <item2>", "выбери <item1> <item2>"])
@bot.on.message(payload={"cmd": "cmd_selecttext"})
async def selecttext_handler(message: Message, info: UsersUserXtrCounters, item1: Optional[str] = None,
                             item2: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        if item1 is None or item2 is None:
            await message.answer(
                f"@id{message.from_id} ({info.first_name}), Используйте: выбери \"фраза 1\" \"фраза 2\"")
        else:
            temp_var = random.randint(0, 1)
            if temp_var == 0:
                await message.answer(
                    f"@id{message.from_id} ({info.first_name}), мне кажется лучше \"{item1}\", чем \"{item2}\"")
            elif temp_var == 1:
                await message.answer(
                    f"@id{message.from_id} ({info.first_name}), мне кажется лучше \"{item2}\", чем \"{item1}\"")


@bot.on.message(text=["Переверни", "переверни"])
@bot.on.message(text=["Переверни <item>", "переверни <item>"])
async def fliptext_handler(message: Message, info: UsersUserXtrCounters, item: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        if item is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), Используйте: переверни \"текст\"")
        else:
            await message.answer(
                f"@id{message.from_id} ({info.first_name}), держи \"{''.join(list(map(lambda x, y: x.replace(x, fliptext_dict.get(x)), ''.join(item.replace(' ', '').lower()), fliptext_dict)))}\"")


@bot.on.message(text=["Шар", "шар"])
@bot.on.message(text=["Шар <item>", "шар <item>"])
async def magicball_handler(message: Message, info: UsersUserXtrCounters, item: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
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
                f"@id{message.from_id} ({info.first_name}), {random.choice(ball_text)}")


@bot.on.message(text=["Инфа", "инфа"])
@bot.on.message(text=["Инфа <item>", "инфа <item>"])
async def infa_handler(message: Message, info: UsersUserXtrCounters, item: Optional[str] = None):
    if not UserAction.get_user(message.from_id):
        await message.answer(f"Вы не зарегестрированы в боте!\nСейчас будет выполнена автоматическая регистрация...")
        UserAction.create_user(message.from_id)
        await message.answer(f"Поздравляем!\nВаш аккаунт успешно создан!\nВаше имя: {info.first_name}\nВаш игровой ID: \
{UserAction.get_user(message.from_id)[0]['ID']}")
    else:
        if item is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), Используйте: инфа \"текст\"")
        else:
            infa_text = ('вероятность -', 'шанс этого', 'мне кажется около')
            await message.answer(f"@id{message.from_id} ({info.first_name}), {random.choice(infa_text)} "
                                 f"{random.randint(0, 100)}%")


# Admin commands
@bot.on.message(text=["Админпомощь", "админпомощь", "ahelp"])
@bot.on.message(payload={"cmd": "cmd_ahelp"})
async def ahelp_handler(message: Message, info: UsersUserXtrCounters):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 4:
        return True
    elif user[0]["RankLevel"] == 4:
        await message.answer(f"@id{message.from_id} ({info.first_name}), команды модератора:\n"
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
        await message.answer(f"@id{message.from_id} ({info.first_name}), команды модератора:\n"
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
        await message.answer(f"@id{message.from_id} ({info.first_name}), команды модератора:\n"
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
async def add_property_handler(message: Message, info: UsersUserXtrCounters, property_type: Optional[str] = None,
                               name: Optional[str] = None, price: Optional[int] = None, param1: Optional[int] = None,
                               param2: Optional[int] = None, param3: Optional[str] = None):
    user = UserAction.get_user(message.from_id)
    if user[0]["RankLevel"] < 6:
        return True
    elif property_type is None:
        await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property [тип]'")
    # elif not isint(price):
    #     await message.answer(f"@id{message.from_id} ({info.first_name}), неверно указана цена!")
    elif property_type == "машина":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property машина ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("cars", CarName=name, CarPrice=price)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новый автомобиль "
                                 f"{name} с ценой {price}$")
    elif property_type == "яхта":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property яхта ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("yachts", YachtName=name, YachtPrice=price)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новую яхту "
                                 f"{name} с ценой {price}$")
    elif property_type == "самолет":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property самолет ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("airplanes", AirplaneName=name, AirplanePrice=price)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новый самолет "
                                 f"{name} с ценой {price}$")
    elif property_type == "вертолет":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property вертолет ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("helicopters", HelicopterName=name, HelicopterPrice=price)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новый вертолет "
                                 f"{name} с ценой {price}$")
    elif property_type == "дом":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property дом ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("houses", HouseName=name, HousePrice=price)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новый дом "
                                 f"{name} с ценой {price}$")
    elif property_type == "квартира":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property квартира ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("apartments", ApartmentName=name, ApartmentPrice=price)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новую квартиру "
                                 f"{name} с ценой {price}$")
    elif property_type == "бизнес":
        if name is None or price is None or param1 is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property бизнес ["
                                 f"название] [цена] [кол-во рабочих]'")
        else:
            MainData.add_business(BusinessName=name, BusinessPrice=price, BusinessWorkers=param1)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новый бизнес "
                                 f"{name} с ценой {price}$ и максимальным количеством рабочих {param1}")
    elif property_type == "питомец":
        if name is None or price is None or param1 is None or param2 is None or param3 is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property питомец ["
                                 f"название] [цена] [мин кол-во добычи] [макс кол-во добычи] [иконка]'")
        else:
            MainData.add_pet(PetName=name, PetPrice=price, PetMinMoney=param1, PetMaxMoney=param2, PetIcon=param3)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили нового питомца "
                                 f"{name} с ценой {price}$, минимальной добычей {param1}, максимальной добычей {param2}"
                                 f" и иконкой {param3}")
    elif property_type == "ферма":
        if name is None or price is None or param1 is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property ферма ["
                                 f"название] [цена] [кол-во биткоинов в час]'")
        else:
            MainData.add_farm(FarmName=name, FarmPrice=price, FarmBTCPerHour=param1)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новую ферму "
                                 f"{name} с ценой {price}$ и количеством биткоинов в час {param1}")
    elif property_type == "телефон":
        if name is None or price is None:
            await message.answer(f"@id{message.from_id} ({info.first_name}), используйте 'add_property телефон ["
                                 f"название] [цена]'")
        else:
            MainData.add_static_property("phones", PhoneName=name, PhonePrice=price)
            await message.answer(f"@id{message.from_id} ({info.first_name}), Вы успешно добавили новый телефон "
                                 f"{name} с ценой {price}$")
    else:
        await message.answer(f"@id{message.from_id} ({info.first_name}), проверьте правильность введенных данных!")


# noinspection PyTypeChecker
@bot.on.raw_event(GroupEventType.GROUP_JOIN, dataclass=GroupTypes.GroupJoin)
async def group_join_handler(event: GroupTypes.GroupJoin):
    await bot.api.messages.send(peer_id=event.object.user_id, message="Спасибо за подписку!", random_id=0,
                                keyboard=START_KEYBOARD)


bot.labeler.message_view.register_middleware(NoBotMiddleware())
bot.labeler.message_view.register_middleware(RegistrationMiddleware())
bot.labeler.message_view.register_middleware(InfoMiddleware())
bot.run_forever()
