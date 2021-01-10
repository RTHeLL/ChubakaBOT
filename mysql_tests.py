import unittest

import classes.mysql

mysql = classes.mysql.MySQL()


class TestsMySQL(unittest.TestCase):
    
    def test_update_user(self):
        user = mysql.check_user('503006053')
        mysql.update_user('503006053', user)