# coding: utf-8

import requests
import json
        
class VK_LongPoll():
	
    def __init__(self, token, group_id):
		
        self.key = None
        self.server = None
        self.ts = 0
        self.wait = 20
        
        self.session = requests.Session()
        
        self.v = '5.74'
        self.token = token
        self.id = group_id
        
        self.connect()
        
    def connect(self):
        
        response = self.method('groups.getLongPollServer', {'group_id' : self.id})
        
        try:
            self.server = response['response']['server']
            self.key = response['response']['key']
            self.ts = response['response']['ts']
            print('[LongPoll] Connection TRUE!')
        except: 
            print(response)
            
    def check(self):
		
        values = {
            'act': 'a_check',
            'key': self.key,
            'ts': self.ts,
            'wait': self.wait
        }
       
        response = self.session.get(
            self.server,
            params=values,
            timeout=25
        ).json()
            
        if 'failed' not in response:
            self.ts = response['ts']
            return response['updates']
            
        elif response['failed'] > 0:
            self.connect()
            
    def listen(self):
        while True:
            for event in self.check():
                yield event
         
        
    def method(self, method, values):
    
        values = values.copy() if values else {}
        values['access_token'] = self.token
        values['v'] = self.v
        
        response = self.session.post(
            'https://api.vk.com/method/' + method,
            values
        ).json()
        
        if 'error' in response:
            print('ERROR:\n' + response['error']['error_msg'])
            return False
        else:
            return response
            
    def sendMessage(self, user_id, text):
        values = {
            'user_id' : user_id,
            'message' : text
        }
        
        self.method('messages.send', values) 
        
        
              
        


