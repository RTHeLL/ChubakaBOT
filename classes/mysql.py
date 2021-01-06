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
        logging.log(logging.INFO, "MySQL success connected!")
    except MySQLError as e:
        logging.log(logging.FATAL, e)

    def check_user(self, vk_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `ID` FROM `users` WHERE `VK_ID`=%s"
            cursor.execute(sql, vk_id)
            result = cursor.fetchone()
            if result == "None":
                return False
            else:
                return result

    def get_user(self, vk_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `ID` FROM `users` WHERE `VK_ID`=%s"
            cursor.execute(sql, vk_id)
            result = cursor.fetchone()
            print(result)
