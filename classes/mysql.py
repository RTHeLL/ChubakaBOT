import pymysql
from pymysql import MySQLError
import configparser

config = configparser.ConfigParser()
config.read("data/mysql_config.ini")


class MySQL:
    # MySQL
    try:
        connection = pymysql.connect(config["MySQL_DATA"]["SQL_HOST"], config["MySQL_DATA"]["SQL_USER"],
                                     config["MySQL_DATA"]["SQL_PASS"], config["MySQL_DATA"]["SQL_DB"])
        print("MySQL success connected!")
    except MySQLError as e:
        print("Error code:", e)
        print("Error message:", e.args[0])

    def get_user(self, vk_id):
        with self.connection.cursor() as cursor:
            sql = "SELECT `ID` FROM `users` WHERE `VK_ID`=%s"
            cursor.execute(sql, vk_id)
            result = cursor.fetchone()
            print(result)
