#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月21日

@author: sanhe
'''
from SmartHome import mydevice

class DB_conf():
    def __init__(self, addr, name, user, password):
        self.addr = addr
        self.name = name
        self.user = user
        self.password = password


class deviceSet():
    device_dict = {
               'infrared' : mydevice.infrared,
               'co2' : mydevice.co2,
               'stc_1' : mydevice.stc_1,
               'plc' : mydevice.plc,
               'sansu' : mydevice.sansu,
               'triplecng' : mydevice.triplecng,
               'voc' : mydevice.voc,
               'wenkong' : mydevice.wenkong,
               'ZMA194E' : mydevice.ZMA194E,
               }
    def __init__(self, session_name, db = None):
        self.session_name = session_name
        self.dev_dict = {}
        
    def getCmdSet(self):
        pass
        