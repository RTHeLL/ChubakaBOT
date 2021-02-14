import logging
import pymysql
import pymysqlpool
from pymysql import MySQLError
import configparser

config = configparser.ConfigParser()
config.read("config/mysql.ini")


class MySQL:
    # Connection
    try:
        pool = pymysqlpool.ConnectionPool(host=config["DATA"]["SQL_HOST"], user=config["DATA"]["SQL_USER"],
                                          password=config["DATA"]["SQL_PASS"], database=config["DATA"]["SQL_DB"],
                                          autocommit=True, charset='utf8mb4')  # SQL Pool connections
        connection = pool.get_connection()  # Main connection
        # Connections for timers
        connection_second_timer = pool.get_connection()
        connection_minute_timer = pool.get_connection()
        connection_hour_timer = pool.get_connection()
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
            cursor.close()

    # Function getting user
    def get_user(self, vk_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `VK_ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS"], vk_id))
            result = cursor.fetchall()
            sql = "SELECT * FROM %s WHERE `VK_ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS_PROPERTY"], vk_id))
            result += cursor.fetchall()
            cursor.close()
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
            cursor.close()
        # self.connection.commit()

    # Function getting user property
    def get_user_property(self, vk_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `VK_ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS_PROPERTY"], vk_id))
            result = cursor.fetchall()
            cursor.close()
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
            sql = "SELECT * FROM %s WHERE `ID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS_PROPERTY"], game_id))
            result += cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function get admins
    def get_admins(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `RankLevel`>6"
            cursor.execute(sql % config["USERS_TABLES"]["USERS"])
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function get users with notifications
    def get_users_with_notifications(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `Notifications`=1"
            cursor.execute(sql % config["USERS_TABLES"]["USERS"])
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function get users for top
    def get_users_top(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE Rating>0 ORDER BY Rating DESC LIMIT 10"
            cursor.execute(sql % config["USERS_TABLES"]["USERS"])
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function kick users from clan
    def kick_users_from_clan(self, **kwargs):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            args_list = list(kwargs.keys())
            sql = "UPDATE %s SET %s='%s', %s='%s' WHERE `ClanID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS"], args_list[0], kwargs[args_list[0]],
                                  args_list[1], kwargs[args_list[1]], kwargs[args_list[2]]))
            cursor.close()

    # Function get users for top
    def get_users_clan(self, clan_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `ClanID`=%s"
            cursor.execute(sql % (config["USERS_TABLES"]["USERS"], clan_id))
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result


class MainData(MySQL):
    # Function get property
    def get_data(self, table):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s"
            cursor.execute(sql % table)
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function get property for shop
    def get_shop_data(self, sort=None):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            result = []
            if sort == 1:
                for table in config.items("PROPERTY_TABLES"):
                    sql = "SELECT * FROM %s ORDER BY Price"
                    cursor.execute(sql % table[0])
                    result.append(cursor.fetchall())
            else:
                for table in config.items("PROPERTY_TABLES"):
                    sql = "SELECT * FROM %s"
                    cursor.execute(sql % table[0])
                    result.append(cursor.fetchall())
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function add static property
    def add_static_property(self, table, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s) VALUES ('%s', %s)"
            cursor.execute(sql % (table, args_list[0], args_list[1], kwargs[args_list[0]], kwargs[args_list[1]]))
            logging.debug(f'New property "{kwargs[args_list[0]]} - {kwargs[args_list[1]]}$" added!')
            cursor.close()

    # Function add businesses
    def add_business(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s, %s) VALUES ('%s', %s, %s)"
            cursor.execute(sql % (
                config["PROPERTY_TABLES"]["BUSINESSES"], args_list[0], args_list[1], args_list[2], kwargs[args_list[0]],
                kwargs[args_list[1]],
                kwargs[args_list[2]]))
            logging.debug(f'New business "{kwargs[args_list[0]]} - price: {kwargs[args_list[1]]}$, workers: '
                          f'{kwargs[args_list[2]]}" added!')
            cursor.close()

    # Function add pets
    def add_pet(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s, %s, %s, %s) VALUES ('%s', %s, %s, %s, '%s')"
            cursor.execute(sql % (
                config["PROPERTY_TABLES"]["PETS"], args_list[0], args_list[1], args_list[2], args_list[3], args_list[4],
                kwargs[args_list[0]], kwargs[args_list[1]], kwargs[args_list[2]],
                kwargs[args_list[3]], kwargs[args_list[4]]))
            logging.debug(f'New pet "{kwargs[args_list[0]]} - price: {kwargs[args_list[1]]}$, min: '
                          f'{kwargs[args_list[2]]}, max: {kwargs[args_list[3]]}, icon: {kwargs[args_list[4]]}" added!')
            cursor.close()

    # Function add farms
    def add_farm(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = f"INSERT INTO %s (%s, %s, %s) VALUES ('%s', %s, %s)"
            cursor.execute(sql % (
                config["PROPERTY_TABLES"]["FARMS"], args_list[0], args_list[1], args_list[2], kwargs[args_list[0]],
                kwargs[args_list[1]],
                kwargs[args_list[2]]))
            logging.debug(f'New farm "{kwargs[args_list[0]]} - price: {kwargs[args_list[1]]}$, btc per hour: '
                          f'{kwargs[args_list[2]]}" added!')
            cursor.close()

    # Function get settings
    def get_settings(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s"
            cursor.execute(sql % config["MAIN_TABLES"]["SETTINGS"])
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function add and update report
    def add_and_update_report(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            if len(args_list) > 2:
                sql = f"UPDATE %s SET %s='%s', %s=%s WHERE `ID`=%s"
                cursor.execute(
                    sql % (config["MAIN_TABLES"]["REPORTS"], args_list[0], kwargs[args_list[0]], args_list[1],
                           kwargs[args_list[1]], kwargs[args_list[2]]))
                logging.debug(f'New answer: {kwargs[args_list[0]]}. Answering: {kwargs[args_list[1]]}')
            else:
                sql = f"INSERT INTO %s (%s, %s) VALUES ('%s', '%s')"
                cursor.execute(
                    sql % (config["MAIN_TABLES"]["REPORTS"], args_list[0], args_list[1], kwargs[args_list[0]],
                           kwargs[args_list[1]]))
                logging.debug(f'New report: {kwargs[args_list[0]]}. Asked: {kwargs[args_list[1]]}')
            cursor.close()

    # Function get reports
    def get_reports(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s"
            cursor.execute(sql % config["MAIN_TABLES"]["REPORTS"])
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function add chat
    def add_chat(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = "INSERT INTO %s (%s) VALUES (%s)"
            cursor.execute(sql % (config["MAIN_TABLES"]["CHATS"], args_list[0], kwargs[args_list[0]]))
            logging.debug(f'New chat: {kwargs[args_list[0]]}')
            cursor.close()

    # Function get chats
    def get_chats(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s"
            cursor.execute(sql % config["MAIN_TABLES"]["CHATS"])
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function add clan
    def add_clan(self, **kwargs):
        with self.connection.cursor() as cursor:
            args_list = list(kwargs.keys())
            sql = "INSERT INTO %s (%s, %s, Players) VALUES ('%s', %s, Players+1)"
            cursor.execute(sql % (config["MAIN_TABLES"]["CLANS"], args_list[0], args_list[1],
                                  kwargs[args_list[0]], kwargs[args_list[1]]))
            logging.debug(f'New clan: {kwargs[args_list[0]]}')
            cursor.close()

    # Function get clans
    def get_clans_top(self):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE Rating>0 ORDER BY Rating DESC LIMIT 10"
            cursor.execute(sql % config["MAIN_TABLES"]["CLANS"])
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function get clans for attack
    def get_clans_attack(self, rating):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE (Rating>%s-1000 AND Rating<%s+1000) AND GuardTime<1"
            cursor.execute(sql % (config["MAIN_TABLES"]["CLANS"], rating, rating))
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function get clan where id
    def get_clan(self, clan_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `ID`=%s"
            cursor.execute(sql % (config["MAIN_TABLES"]["CLANS"], clan_id))
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function get clan where user_id
    def get_clan_userid(self, user_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM %s WHERE `OwnerID`=%s"
            cursor.execute(sql % (config["MAIN_TABLES"]["CLANS"], user_id))
            result = cursor.fetchall()
            cursor.close()
            if len(result) == 0:
                return False
            else:
                return result

    # Function save clan
    def save_clan(self, clan_id, clan):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            for row, column in clan[0].items():
                sql = "UPDATE %s SET %s='%s' WHERE `ID`=%s"
                if row == "ID":
                    continue
                else:
                    cursor.execute(sql % (config["MAIN_TABLES"]["CLANS"], row, column, clan_id))
            cursor.close()

    # Function remove clan
    def remove_clan(self, clan_id):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM %s WHERE `ID`=%s"
            cursor.execute(sql % (config["MAIN_TABLES"]["CLANS"], clan_id))
            cursor.close()
