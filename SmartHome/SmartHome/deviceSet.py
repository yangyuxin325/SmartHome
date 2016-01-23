#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月21日

@author: sanhe
'''
import torndb
import mydevice
from basedata import data_param
from decimal import *
from UserDict import UserDict

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

def doDeviceState(device):
    pass

def doWriteReturn(data_item):
    pass

class deviceSet(UserDict):
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
        UserDict.__init__(self)
        self.session_name = session_name
        self.name_idMap = {}
        self.id_nameMap = {}
        self.db = db
        
    def get(self, key, failobj=None):
        if key in self:
            return self[key]
        elif key in self.name_idMap:
            return self.get(self.name_idMap[key], failobj)
        else:
            return failobj
        
    def getInterval(self, dev_name, conf_name):
        if self.get(dev_name):
            return self.get(dev_name).getInterval(conf_name)
        else:
            return 0
        
    def getCmdSet(self):
        cycleCmds = {}
        for dev_id, dev in self.items():
            cycleCmds[dev_id] = dev.genPratrolInstr(dev_id)
        cmdCount = 0
        line_cmdList = []
        for key,cmds in cycleCmds.items():
            for cmd in cmds :
                cmdCount += 1
                line_cmdList.append({"id" : cmdCount, "cmd" : HexToString(cmd), "dev_id" : key})
        return line_cmdList
     
    def initData(self):
        if self.db is not None:
            sqlConnection = torndb.Connection(self.db.addr, self.db.name, 
                                              user=self.db.user, password=self.db.password)
            sqlString = 'select dev_name, dev_type, dev_id from Device where session_name = %s'
            devices = sqlConnection.query(sqlString,self.session_name)
            for device in devices:
                self[device['dev_id']] = self.device_dict[device['dev_type']](doDeviceState)
                self.name_idMap[device['dev_name']] = device['dev_id']
                self.id_nameMap[device['dev_id']] = device['dev_name']
                sqlString = 'select data_ename, conf_name, link_flag, write_flag, \
                algorithm from DataType where dev_name = %s'
                data_confs = sqlConnection.query(sqlString, device['dev_name'])
                for data_conf in data_confs:
                    sqlString = 'select min_variation, min_val, max_val, \
                    dis_interval from DataConstraint where data_ename = %s'
                    res = sqlConnection.query(sqlString, data_conf['data_ename'])
                    dataconstraint = UserDict()
                    for k,v in res[0].items():
                        dataconstraint[k] = float(v) if v else v
                    
                    sqlString = 'select value, error_flag, time from DataInfo where data_ename = %s'
                    res = sqlConnection.query(sqlString, data_conf['data_ename'])
                    if data_conf['write_flag']:
                        dataitem = data_param(data_conf['data_ename'],dataconstraint,
                                              float(res[0]['value']),res[0]['error_flag'],
                                              res[0]['time'],doWriteReturn)
                        self[device['dev_id']].addData(data_conf['conf_name'],dataitem)
                    else:
                        if data_conf['link_flag']:
                            sqlString = 'select link_key, link_type, link_para1 \
                            from DataLink where dev_name = %s and conf_name = %s'
                            link_data = sqlConnection.query(sqlString,
                                                            device['dev_name'],
                                                            data_conf['conf_name'])
                            if link_data[0]['link_type'] == 'average':
                                dataitem = data_param(data_conf['data_ename'],
                                                      dataconstraint,float(res[0]['value']),
                                                      res[0]['error_flag'],res[0]['time'],
                                                      None,link_data[0]['link_para1'])
                                self[device['dev_id']].addData(data_conf['conf_name'],
                                                                        dataitem,
                                                                        link_data[0]['link_key'])
                            else:
                                pass
                        else:
                            dataitem = data_param(data_conf['data_ename'],dataconstraint,
                                                  float(res[0]['value']),res[0]['error_flag'],
                                                  res[0]['time'])
                            self[device['dev_id']].addData(data_conf['conf_name'],dataitem)
                    if data_conf['algorithm'] is not None:
                        self[device['dev_id']].addAlgorithm(data_conf['conf_name'],
                                                                     data_conf['algorithm'])
                    else:
                        pass
            sqlConnection.close()
            
    def getValue(self, dev_name, conf_name):
        if dev_name in self.name_idMap:
            dev = self.get(self.name_idMap[dev_name])
            if dev:
                dev.getValue(conf_name)
        else:
            pass
        
    def getRealValue(self, dev_name, conf_name):
        if dev_name in self.name_idMap:
            dev = self.get(self.name_idMap[dev_name])
            if dev:
                dev.getRealValue(conf_name)
        else:
            pass
            
    def getData(self, dev_name, conf_name):
        if dev_name in self.name_idMap:
            dev = self.get(self.name_idMap[dev_name])
            if dev:
                return dev.get(conf_name)
            else:
                pass
        else:
            pass
        
    def setData(self, dev_name, conf_name, data):
        if dev_name in self.name_idMap:
            if self.get(self.name_idMap[dev_name]):
                self.get(self.name_idMap[dev_name]).setData(conf_name, data)
        else:
            pass
            
    def setDisConnect(self, dev_id, flag):
        if self.get(dev_id):
            self[dev_id].setDisConnect(flag)
        else:
            pass
    
    def getConnectState(self, key):
        if self.get(key):
            return self.get(key)
        else:
            pass
    
    def ParseData(self, dev_id, data):
        if self.get(dev_id):
            self[dev_id].dataParse(data)
        else:
            print "there is not device which it dev_id = " , dev_id , 
            " in Session ", self._session_name