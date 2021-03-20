import logging
import pymysql
from pymysql import MySQLError
import configparser
import json5

config = configparser.ConfigParser()
config.read("config/mysql.ini")

table_for_insert = 'users'
table_for_insert1 = 'users_property'
columns_name = ('Name', 'Money', 'Bank_Money', 'BTC', 'EXP', 'Rating', 'BTC_In_Farms', 'Money_In_Business', 'VK_ID')
columns_name1 = ('Car', 'House', 'Apartment', 'Pet', 'PetLevel', 'Farms', 'Business', 'Yacht', 'Helicopter', 'Phone', 'Airplane', 'VK_ID')

# js_dict = {}

with open('base.json') as json_file:
    js_dict = json5.loads(json_file.read())

# print(list(map(int, id_dict))[0])

# for i in js_dict['bs']:
#     js_dict['bs'].update(vk_id=list(map(str, id_dict))[int(i)])
#     print(js_dict['bs'][i])

# py_dict = json5.loads(js_dict)
# print(py_dict)

# Connection
try:
    connection = pymysql.connect(config["DATA"]["SQL_HOST"], config["DATA"]["SQL_USER"],
                                 config["DATA"]["SQL_PASS"], config["DATA"]["SQL_DB"])
    print(f'MySQL success connected!')
except MySQLError as e:
    logging.log(logging.FATAL, e)


# Function paste in table
def fast_paste():
    with connection.cursor() as cursor:
        count = 0
        for i in js_dict['bs']:
            sql = "INSERT INTO `%s` (%s, %s, %s, %s, %s, %s, %s, %s, %s) VALUES ('%s', %s, %s, %s, %s, %s, %s, %s, %s)"
            sql1 = "INSERT INTO `%s` (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            try:
                cursor.execute(sql % (table_for_insert, columns_name[0], columns_name[1], columns_name[2],
                                      columns_name[3], columns_name[4], columns_name[5],
                                      columns_name[6], columns_name[7], columns_name[8],
                                      js_dict['bs'][i]['nick'], js_dict['bs'][i]['balance'],
                                      js_dict['bs'][i]['bank'], js_dict['bs'][i]['btc'], js_dict['bs'][i]['exp'],
                                      js_dict['bs'][i]['rating'], js_dict['bs'][i]['farm_btc'],
                                      js_dict['bs'][i]['biznesmoney'], js_dict['bs'][i]['id']))
                cursor.execute(sql1 % (table_for_insert1, columns_name1[0], columns_name1[1], columns_name1[2],
                                       columns_name1[3], columns_name1[4], columns_name1[5],
                                       columns_name1[6], columns_name1[7], columns_name1[8],
                                       columns_name1[10], columns_name1[11],
                                       js_dict['bs'][i]['carid'], js_dict['bs'][i]['homeid'],
                                       js_dict['bs'][i]['kvartiraid'], js_dict['bs'][i]['petid'],
                                       js_dict['bs'][i]['petlvl'], js_dict['bs'][i]['farms'],
                                       js_dict['bs'][i]['biznesid'], js_dict['bs'][i]['yachtid'],
                                       js_dict['bs'][i]['helicopterid'], js_dict['bs'][i]['airplaneid'],
                                       js_dict['bs'][i]['id']))
                print(sql % (table_for_insert, columns_name[0], columns_name[1], columns_name[2],
                             columns_name[3], columns_name[4], columns_name[5],
                             columns_name[6], columns_name[7], columns_name[8],
                             js_dict['bs'][i]['nick'], js_dict['bs'][i]['balance'],
                             js_dict['bs'][i]['bank'], js_dict['bs'][i]['btc'], js_dict['bs'][i]['exp'],
                             js_dict['bs'][i]['rating'], js_dict['bs'][i]['farm_btc'],
                             js_dict['bs'][i]['biznesmoney'], js_dict['bs'][i]['id']) + ' ----- OK!',
                      sql1 % (table_for_insert1, columns_name1[0], columns_name1[1], columns_name1[2],
                              columns_name1[3], columns_name1[4], columns_name1[5],
                              columns_name1[6], columns_name1[7], columns_name1[8],
                              columns_name1[10], columns_name1[11],
                              js_dict['bs'][i]['carid'], js_dict['bs'][i]['homeid'],
                              js_dict['bs'][i]['kvartiraid'], js_dict['bs'][i]['petid'],
                              js_dict['bs'][i]['petlvl'], js_dict['bs'][i]['farms'],
                              js_dict['bs'][i]['biznesid'], js_dict['bs'][i]['yachtid'],
                              js_dict['bs'][i]['helicopterid'], js_dict['bs'][i]['airplaneid'],
                              js_dict['bs'][i]['id']) + ' ----- OK!')
                count += 1
            except e:
                print(f'FATAL ERROR!')
        print(f'All done! Inserted '+str(count)+' rows')
    connection.commit()


fast_paste()
