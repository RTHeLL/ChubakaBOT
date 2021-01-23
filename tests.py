import math
import random
import json
import datetime

import pymysql
import requests

import classes.mysql

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


def test_get_user():
    shop_data = MainData.get_shop_data()

    print(shop_data[0][1])
    print(shop_data[1][1])
    print(shop_data[2][1])
    print(shop_data[3][1])
    print(shop_data[4][1])
    print(shop_data[5][1])
    print(shop_data[6][1])
    print(shop_data[7][1])
    print(shop_data[8][1])
    print(shop_data[9][1])


test_get_user()
