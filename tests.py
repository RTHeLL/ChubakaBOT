import unittest

import classes.mysql

mysql = classes.mysql.MainData()


def test_get_user():
    name = "Ferrari ввапы"
    price = 52000
    mysql.add_static_property("cars", CarName=name, CarPrice=price)


test_get_user()
