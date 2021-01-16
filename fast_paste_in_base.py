import logging
import pymysql
from pymysql import MySQLError
import configparser
import json5

config = configparser.ConfigParser()
config.read("data/mysql.ini")

table_for_insert = 'pets'
columns_name = ('PetName', 'PetPrice', 'PetMinMoney', 'PetMaxMoney', 'PetIcon')

js_dict = "[ { name: 'Улитка', cost: 1000, min: 250, max: 1500, id: 1, icon: '🐌' }, \
            { name: 'Лягушка', cost: 25000, min: 5000, max: 15000, id: 2, icon: '🐸' }, \
            { name: 'Заяц', cost: 500000, min: 50000, max: 150000, id: 3, icon: '🐰' }, \
            { name: 'Свинья', cost: 300000000, min: 15000000, max: 30000000, id: 4, icon: '🐷' }, \
            { name: 'Лиса', cost: 1250000000, min: 50000000, max: 90000000, id: 5, icon: '🦊' }, \
            { name: 'Собака', cost: 5000000000, min: 100000000, max: 250000000, id: 6, icon: '🐶' }, \
            { name: 'Панда', cost: 30000000000, min: 5000000000, max: 7000000000, id: 7, icon: '🐼' }, \
            { name: 'Волк', cost: 180000000000, min: 15000000000, max: 32541252145, id: 8, icon: '🐺' }, \
            { name: 'Гориллка', cost: 180000000000, min: 15000000000, max: 35000000000, id: 9, icon: '🦍' }, \
            { name: 'Змея', cost: 290000000000, min: 1500000000, max: 54000000000, id: 10, icon: '🐍' }, \
            { name: 'Жираф', cost: 900000000000, min: 32541252145, max: 100000000000, id: 11, icon: '🦒' }, \
            { name: 'Летучая мышь', cost: 1400000000000, min: 150000000000, max: 332541252145, id: 12, icon: '🦇' }, \
            { name: 'Африканский крокодил', cost: 1400000000000, min: 150000000000, max: 332541252145, id: 13, icon: '🐊' }, \
            { name: 'Коронавирус', cost: 80000000000000, min: 150000000000, max: 50000000000000, id: 14, icon: '🦠' } ]"

py_dict = json5.loads(js_dict)
print(py_dict)

# Connection
try:
    connection = pymysql.connect(config["MySQL_DATA"]["SQL_HOST"], config["MySQL_DATA"]["SQL_USER"],
                                 config["MySQL_DATA"]["SQL_PASS"], config["MySQL_DATA"]["SQL_DB"])
    print(f'MySQL success connected!')
except MySQLError as e:
    logging.log(logging.FATAL, e)


# Function paste in table
def fast_paste():
    with connection.cursor() as cursor:
        count = 0
        for i in py_dict:
            sql = "INSERT INTO `%s` (%s, %s, %s, %s) VALUES ('%s', %s, %s, %s)"
            try:
                cursor.execute(sql % (table_for_insert, columns_name[0], columns_name[1], columns_name[2], columns_name[3], i["name"], i["cost"], i["min"], i["max"]))
                print(sql % (table_for_insert, columns_name[0], columns_name[1], columns_name[2], columns_name[3], i["name"], i["cost"], i["min"], i["max"]) + ' ----- OK!')
                count += 1
            except e:
                print(f'FATAL ERROR!')
        print(f'All done! Inserted '+str(count)+' rows')
    connection.commit()


fast_paste()
