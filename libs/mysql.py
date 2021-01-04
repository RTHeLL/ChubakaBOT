# coding: utf-8

import pymysql

class MySQL():
    
    def __init__(self, host = 'localhost', user = 'root', password = '', db='bot'):
        try:
            self.connection = pymysql.connect(host, user, password, db,  charset='utf8', use_unicode=True, autocommit=True)
         
            self.handle = self.connection.cursor()
        
            self.data = None
            
            print('[MySQL] Connection TRUE!')
            
        except:
            print('[MySQL] Connection FALSE!')
         
    def fetchOne(self, sql):
		
        self.handle.execute(sql)
    
        self.data = self.handle.fetchone()
        
        return self.data
        
    def fetchAll(self, sql):
		
        self.handle.execute(sql)
    
        self.data = self.handle.fetchall()
        
        return self.data
        
    def ex(self, sql):
		
        self.data = self.handle.execute(sql)
		
        return self.data
		
		
