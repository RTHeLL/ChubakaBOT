import math

import requests

import classes.mysql
import pymysql

MySQL = classes.mysql.MySQL()
MainData = classes.mysql.MainData()


class Timers:
    @staticmethod
    def hour_timer():
        with MySQL.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Bonus
            sql = f"UPDATE users SET Bonus=Bonus-1 WHERE Bonus>0"
            cursor.execute(sql)

            # Farms
            sql = "SELECT u.VK_ID, u.BTC_In_Farms, c.Farms, c.FarmsType " \
                  "FROM users_property c " \
                  "INNER JOIN users u ON u.VK_ID = c.VK_ID"
            cursor.execute(sql)
            users = cursor.fetchall()
            sql = f"UPDATE users SET BTC_In_Farms=BTC_In_Farms+%s WHERE `VK_ID`=%s"
            for user in users:
                if user["FarmsType"] == 0:
                    continue
                elif user["FarmsType"] == 1:
                    cursor.execute(sql % (2*user["Farms"], user["VK_ID"]))
                elif user["FarmsType"] == 2:
                    cursor.execute(sql % (10*user["Farms"], user["VK_ID"]))
                elif user["FarmsType"] == 3:
                    cursor.execute(sql % (100*user["Farms"], user["VK_ID"]))

            # Curse btc/usd
            bit = requests.get('https://api.cryptonator.com/api/ticker/btc-usd',
                               headers={'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) '
                                                      'Gecko/20030624 Netscape/7.1 (ax)'}).json()
            sql = f"UPDATE settings SET BTC_USD_Curse=%s"
            cursor.execute(sql % math.trunc(float(bit["ticker"]["price"])))

            # Business
            sql = "SELECT u.VK_ID, u.Money_In_Business, u.Workers_In_Business, c.Business, c.BusinessLevel " \
                  "FROM users_property c " \
                  "INNER JOIN users u ON u.VK_ID = c.VK_ID"
            cursor.execute(sql)
            users = cursor.fetchall()
            sql = f"UPDATE users SET Money_In_Business=Money_In_Business+%s WHERE `VK_ID`=%s"
            for user in users:
                if user["BusinessLevel"] == 0:
                    continue
                elif user["BusinessLevel"] == 1:
                    if user["Workers_In_Business"] != MainData.get_data('businesses')[user[1]["Business"]-1]["BusinessWorkers"]:
                        cursor.execute(sql % (math.trunc(MainData.get_data('businesses')[user[1]["Business"]-1]["MoneyPerHouse"]/2), user["VK_ID"]))
                    else:
                        cursor.execute(sql % (MainData.get_data('businesses')[user[1]["Business"]-1]["MoneyPerHouse"], user["VK_ID"]))
                elif user["BusinessLevel"] == 2:
                    if user["Workers_In_Business"] != MainData.get_data('businesses')[user[1]["Business"]-1]["BusinessWorkers"]*2:
                        cursor.execute(sql % (MainData.get_data('businesses')[user[1]["Business"]-1]["MoneyPerHouse"]), user["VK_ID"])
                    else:
                        cursor.execute(sql % (MainData.get_data('businesses')[user[1]["Business"]-1]["MoneyPerHouse"]*2, user["VK_ID"]))
        MySQL.connection.commit()
