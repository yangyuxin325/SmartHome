#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月21日

@author: sanhe
'''
import torndb
import mydevice
from decimal import *
from collections import deque

class DB_conf():
    def __init__(self, addr, name, user, password):
        self.addr = addr
        self.name = name
        self.user = user
        self.password = password

def HexToString(array):
    snd = ''
    for i in array:
        snd += '%02x' % i
    return snd

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
        self.name_idMap = {}
        self.id_nameMap = {}
        self.db = db
        
    def getCmdSet(self):
        cycleCmds = {}
        for dev_id, dev in self.dev_dict.items():
            cycleCmds[dev_id] = dev.genPratrolInstr(dev_id)
        cmdCount = 0
        #line_cmdList = []
        line_cmdList = deque()
        for key,cmds in cycleCmds.items():
            for cmd in cmds :
                cmdCount += 1
                line_cmdList.append({"id" : cmdCount, "cmd" : HexToString(cmd), "dev_id" : key})
        return line_cmdList
     
    def initData(self):
        if self.db is not None:
            sqlConnection = torndb.Connection(self.db.addr, self.db.name, user=self.db.user, password=self.db.password)
            sqlString = 'select dev_name, dev_type, dev_id from Device where session_name = %s'
            devices = sqlConnection.query(sqlString,self.session_name)
            for device in devices:
                self.dev_dict[device['dev_id']] = self.device_dict[device['dev_type']]()
                self.name_idMap[device['dev_name']] = device['dev_id']
                self.id_nameMap[device['dev_id']] = device['dev_name']
                sqlString = 'select data_ename, conf_name, link_flag, write_flag, algorithm from DataType where dev_name = %s'
                data_confs = sqlConnection.query(sqlString, device['dev_name'])
                for data_conf in data_confs:
                    sqlString = 'select min_variation, min_val, max_val, dis_interval from DataConstraint where data_ename = %s'
                    res = sqlConnection.query(sqlString, data_conf['data_ename'])
                    from basedata import data_constraint
                    dataconstraint = data_constraint(float(res[0]['min_variation']),\
                    float(res[0]['min_val']) if res[0]['min_val'] else res[0]['min_val'],\
                    float(res[0]['max_val']) if res[0]['max_val'] else res[0]['max_val'],\
                                                     res[0]['dis_interval'])
                    sqlString = 'select value, error_flag, time, dis_flag, dis_time from DataInfo where data_ename = %s'
                    res = sqlConnection.query(sqlString, data_conf['data_ename'])
                    from basedata import basic_data
                    data = basic_data(data_conf['data_ename'],float(res[0]['value']),res[0]['error_flag'],res[0]['time'],res[0]['dis_flag'],res[0]['dis_time'])
                    from basedata import data_param
                    if data_conf['write_flag']:
                        sqlString = 'select value, updatetime from WDataInfo where data_ename = %s'
                        res = sqlConnection.query(sqlString, data_conf['data_ename'])
                        if len(res):
                            self.dev_dict[device['dev_id']].addData(data_conf['conf_name'],
                                data_param(data,dataconstraint,res[0]['value'],res[0]['updatetime']))
                        else:
                            pass
                    else:
                        self.dev_dict[device['dev_id']].addData(data_conf['conf_name'],data_param(data,dataconstraint))
                    if data_conf['link_flag']:
                        sqlString = 'select link_key, link_type, link_para1 from DataLink where dev_name = %s and conf_name = %s'
                        link_data = sqlConnection.query(sqlString,device['dev_name'],data_conf['conf_name'])
                        if link_data[0]['link_type'] == 'average':
                            dataitem = data_param(data,dataconstraint,None,None,link_data[0]['link_para1'])
                            self.dev_dict[device['dev_id']].addData(data_conf['conf_name'],dataitem,link_data[0]['link_key'])
                    if data_conf['algorithm'] is not None:
                        self.dev_dict[device['dev_id']].addAlgorithm(data_conf['conf_name'],data_conf['algorithm'])
            sqlConnection.close()
            
<<<<<<< HEAD
    def getDeviceDataItem(self, dev_name, conf_name):
=======
    def getDeviceData(self, dev_name):
>>>>>>> refs/remotes/origin/yang
        if dev_name in self.name_idMap:
<<<<<<< HEAD
            return self.device_dict[dev_name].getDataItem(conf_name)
=======
            return self.get(self.name_idMap[dev_name])
        else:
            pass
            
    def getValue(self, dev_name, conf_name):
        dev_data = self.getDeviceData(dev_name)
        if dev_data:
            return dev_data.getValue(conf_name)
        else:
            pass
        
    def getRealValue(self, dev_name, conf_name):
        dev_data = self.getDeviceData(dev_name)
        if dev_data:
            return dev_data.getRealValue(conf_name)
>>>>>>> refs/remotes/origin/yang
        else:
            pass
            
    def getData(self, dev_name, conf_name):
<<<<<<< HEAD
        if dev_name in self.name_idMap:
            self.device_dict[self.name_idMap[dev_name]].getData(conf_name)
=======
        dev_data = self.getDeviceData(dev_name)
        if dev_data:
            return dev_data.get(conf_name)
>>>>>>> refs/remotes/origin/yang
        else:
            pass
        
    def setData(self, dev_name, conf_name, data):
        if dev_name in self.name_idMap:
            self.device_dict[self.name_idMap[dev_name]].setData(conf_name, data)
        else:
            pass
            
    def setDisConnect(self, dev_id, flag):
        if dev_id in self.dev_dict:
            self.dev_dict[dev_id].setDisConnect(flag)
        else:
            pass
    
<<<<<<< HEAD
    def getConnectState(self, dev_id):
        if dev_id in self.dev_dict:
            return self.dev_dict[dev_id].getConnectState()
=======
    def getConnectState(self, key):
        if self.get(key):
            return self.get(key).getConnectState()
>>>>>>> refs/remotes/origin/yang
        else:
            pass
    
    def ParseData(self, dev_id, data):
        if dev_id in self.dev_dict:
            self.dev_dict[dev_id].dataParse(data)
        else:
            print "there is not device which it dev_id = " , dev_id , " in Session ", self._session_name
