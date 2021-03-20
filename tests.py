import math
import random
import json
import datetime
import configparser
import asyncio
from threading import Thread
import re

import pymysql
import requests

from vkbottle import GroupEventType, GroupTypes, Keyboard, ABCHandler, ABCView, \
    BaseMiddleware, \
    CtxStorage, Text
from vkbottle.bot import Bot, Message, rules
from vkbottle_types.objects import UsersUserXtrCounters

import classes.mysql

config = configparser.ConfigParser()
config.read("config/vk.ini")
bot = Bot('9b5bcceffcc1fc90e6b16ccc7e265433be149758191feccc7672f939ec7db215351229bc331011ce8da07')
MySQL = classes.mysql.MySQL()
UserAction = classes.mysql.UserAction()
MainData = classes.mysql.MainData()

fliptext_dict = {'q': 'q', 'w': 'ʍ', 'e': 'ǝ', 'r': 'ɹ', 't': 'ʇ', 'y': 'ʎ', 'u': 'u', 'i': 'ᴉ', 'o': 'o', 'p': 'p',
                 'a': 'ɐ', 's': 's', 'd': 'd', 'f': 'ɟ', 'g': 'ƃ', 'h': 'ɥ', 'j': 'ɾ', 'k': 'ʞ', 'l': 'l', 'z': 'z',
                 'x': 'x', 'c': 'ɔ', 'v': 'ʌ', 'b': 'b', 'n': 'n', 'm': 'ɯ',
                 'й': 'ņ', 'ц': 'ǹ', 'у': 'ʎ', 'к': 'ʞ', 'е': 'ǝ', 'н': 'н', 'г': 'ɹ', 'ш': 'm', 'щ': 'm', 'з': 'ε',
                 'х': 'х', 'ъ': 'q', 'ф': 'ф', 'ы': 'ıq', 'в': 'ʚ', 'а': 'ɐ', 'п': 'u', 'р': 'd', 'о': 'о', 'л': 'v',
                 'д': 'ɓ', 'ж': 'ж', 'э': 'є', 'я': 'ʁ', 'ч': 'һ', 'с': 'ɔ', 'м': 'w', 'и': 'и', 'т': 'ɯ', 'ь': 'q',
                 'б': 'ƍ', 'ю': 'oı'}


def chunks(users: list, count: int = 100):
    start = 0

    for i in range(math.ceil(len(users) / count)):
        stop = start + count
        yield users[start:stop]
        start = stop


user1 = UserAction.get_user(503006053)


def test(user):
    print(UserAction.custom_query('SELECT SUM(Money) FROM users')[0]['SUM(Money)'])


test(user1)
