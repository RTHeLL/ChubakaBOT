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

    def check_user(self, vk_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `users` WHERE `VK_ID`=%s"
            cursor.execute(sql, vk_id)
            result = cursor.fetchone()
            if result == "None":
                return False
            else:
                return result

    def create_user(self, vk_id):
        with self.connection.cursor() as cursor:
            sql = f"INSERT INTO `users` (VK_ID, Money) VALUES (%s,'500')"
            cursor.execute(sql, int(vk_id))
        self.connection.commit()
