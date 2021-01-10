import logging
import pymysql
from pymysql import MySQLError
import configparser

config = configparser.ConfigParser()
config.read("data/mysql_config.ini")


class MySQL:
    # Connection
    try:
        connection = pymysql.connect(config["MySQL_DATA"]["SQL_HOST"], config["MySQL_DATA"]["SQL_USER"],
                                     config["MySQL_DATA"]["SQL_PASS"], config["MySQL_DATA"]["SQL_DB"])
        print(f'MySQL success connected!')
    except MySQLError as e:
        logging.log(logging.FATAL, e)


class UserAction(MySQL):
    # Function creating user
    def create_user(self, vk_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `users` (VK_ID) VALUES (%s)"
            cursor.execute(sql, vk_id)
            sql = f"INSERT INTO `users_property` (VK_ID) VALUES (%s)"
            cursor.execute(sql, vk_id)
        self.connection.commit()

    # Function getting user
    def get_user(self, vk_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM `users` WHERE `VK_ID`=%s"
            cursor.execute(sql, vk_id)
            result = cursor.fetchall()
            if cursor.fetchall() == "None":
                return False
            else:
                return result

    # Function updating user
    def update_user(self, vk_id, user):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            for row, column in user[0].items():
                sql = "UPDATE users SET %s=%s WHERE `VK_ID`=%s"
                if row == "ID" or row == "VK_ID" or row == "Register_Data":
                    continue
                else:
                    cursor.execute(sql % (row, column, vk_id))
        self.connection.commit()

    # Function getting user property
    def get_user_property(self, vk_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM `users_property` WHERE `VK_ID`=%s"
            cursor.execute(sql, vk_id)
            result = cursor.fetchall()
            if cursor.fetchall() == "None":
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
            if cursor.fetchall() == "None":
                return False
            else:
                return result
