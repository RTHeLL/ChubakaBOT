import classes.mysql
import pymysql

MySQL = classes.mysql.MySQL()


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
        MySQL.connection.commit()