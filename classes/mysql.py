import logging
import pymysql
from pymysql import MySQLError
import configparser

config = configparser.ConfigParser()
config.read("config/mysql.ini")


class MySQL:
    # Connection
    try:
        connection = pymysql.connect(host=config["DATA"]["SQL_HOST"], user=config["DATA"]["SQL_USER"],
                                     password=config["DATA"]["SQL_PASS"], database=config["DATA"]["SQL_DB"])
        print(f'MySQL success connected!')
    except MySQLError as e:
        logging.log(logging.FATAL, e)


class UserAction(MySQL):
    # Function creating user
    def create_user(self, vk_id, name):
        with self.connection.cursor() as cursor:
            for table in config.items("USERS_TABLES"):
                if table[0] == config["USERS_TABLES"]["USERS"]:
                    sql = f"INSERT INTO %s (VK_ID, %s) VALUES (%s, '%s')"
                    cursor.execute(sql % (table[0], config["USERS_COLUMNS"]["NAME"], vk_id, name))
                else:
                    sql = f"INSERT INTO %s (VK_ID) VALUES (%s)"
                    cursor.execute(sql % (table[0], vk_id))
        self.connection.commit()

    # Function getting user
    def get_user(self, vk_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `VK_ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS"], vk_id))
            result = cursor.fetchall()
            sql = "SELECT * FROM %s WHERE `VK_ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS_PROPERTY"], vk_id))
            result += cursor.fetchall()
            if len(result) == 0:
                return False
            else:
                return result

    # Function updating user
    def save_user(self, vk_id, user):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            if len(user) == 1:
                for row, column in user[0].items():
                    sql = "UPDATE %s SET %s='%s' WHERE `VK_ID`=%s"
                    if row == "ID" or row == "VK_ID" or row == "Register_Data":
                        continue
                    else:
                        cursor.execute(sql % (config["USERS_TABLES"]["USERS"], row, column, vk_id))
            else:
                for row, column in user[0].items():
                    sql = "UPDATE %s SET %s='%s' WHERE `VK_ID`=%s"
                    if row == "ID" or row == "VK_ID" or row == "Register_Data":
                        continue
                    else:
                        cursor.execute(sql % (config["USERS_TABLES"]["USERS"], row, column, vk_id))
                for row, column in user[1].items():
                    sql = "UPDATE %s SET %s=%s WHERE `VK_ID`=%s"
                    if row == "ID" or row == "VK_ID":
                        continue
                    else:
                        cursor.execute(sql % (config["USERS_TABLES"]["USERS_PROPERTY"], row, column, vk_id))
        self.connection.commit()

    # Function getting user property
    def get_user_property(self, vk_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `VK_ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS_PROPERTY"], vk_id))
            result = cursor.fetchall()
            if len(result) == 0:
                return False
            else:
                return result

    # Function checking user in DB
    def get_user_by_gameid(self, game_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS"], game_id))
            result = cursor.fetchall()
            if len(result) == 0:
                return False
            else:
                return result


class MainData(MySQL):
    # Function getting cars
    def get_data(self, table):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s"
            cursor.execute(sql % table)
            result = cursor.fetchall()
            if len(result) == 0:
                return False
            else:
                return result

    def get_shop_data(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            result = []
            for table in config.items("PROPERTY_TABLES"):
                sql = "SELECT * FROM %s ORDER BY Price"
                cursor.execute(sql % table[0])
                result.append(cursor.fetchall())
            if len(result) == 0:
                return False
            else:
                return result

    def add_static_property(self, table, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s) VALUES ('%s', %s)"
            cursor.execute(sql % (table, args_list[0], args_list[1], kwargs[args_list[0]], kwargs[args_list[1]]))
            logging.debug(f'New property "{kwargs[args_list[0]]} - {kwargs[args_list[1]]}$" added!')
        self.connection.commit()

    def add_business(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s, %s) VALUES ('%s', %s, %s)"
            cursor.execute(sql % (config["PROPERTY_TABLES"]["BUSINESSES"], args_list[0], args_list[1], args_list[2], kwargs[args_list[0]], kwargs[args_list[1]],
                                  kwargs[args_list[2]]))
            logging.debug(f'New business "{kwargs[args_list[0]]} - price: {kwargs[args_list[1]]}$, workers: '
                          f'{kwargs[args_list[2]]}" added!')
        self.connection.commit()

    def add_pet(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s, %s, %s, %s) VALUES ('%s', %s, %s, %s, '%s')"
            cursor.execute(sql % (config["PROPERTY_TABLES"]["PETS"], args_list[0], args_list[1], args_list[2], args_list[3], args_list[4],
                                  kwargs[args_list[0]], kwargs[args_list[1]], kwargs[args_list[2]],
                                  kwargs[args_list[3]], kwargs[args_list[4]]))
            logging.debug(f'New pet "{kwargs[args_list[0]]} - price: {kwargs[args_list[1]]}$, min: '
                          f'{kwargs[args_list[2]]}, max: {kwargs[args_list[3]]}, icon: {kwargs[args_list[4]]}" added!')
        self.connection.commit()

    def add_farm(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s, %s) VALUES ('%s', %s, %s)"
            cursor.execute(sql % (config["PROPERTY_TABLES"]["FARMS"], args_list[0], args_list[1], args_list[2], kwargs[args_list[0]], kwargs[args_list[1]],
                                  kwargs[args_list[2]]))
            logging.debug(f'New farm "{kwargs[args_list[0]]} - price: {kwargs[args_list[1]]}$, btc per hour: '
                          f'{kwargs[args_list[2]]}" added!')
        self.connection.commit()

    def get_settings(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM settings"
            cursor.execute(sql)
            result = cursor.fetchall()
            if len(result) == 0:
                return False
            else:
                return result
