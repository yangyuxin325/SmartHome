#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月25日

@author: sanhe
'''
class server_param():
    def __init__(self,server_name, server_type, server_ip):
        self.server_name = server_name
        self.server_type = server_type
        self.server_ip = server_ip
        
class data_server():
    def __init__(self,sr_param):
        self.sr_param = sr_param
        self.sess_dict = {}