#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月28日

@author: sanhe
'''
import asyncore
import threading
import torndb
from datetime import datetime
from basedata import data_param
from copy import deepcopy
from sock_session import AsyncServer
from sock_session import AsyncSession
from sock_session import AsyncClient
import struct
import json
from UserDict import UserDict
from data_server import data_server

# 被动socket数据处理
def handleData(sockSession):
    buf1 = sockSession.recv(16)
    if len(buf1) == 16 :
        head = struct.unpack('!4i', buf1)
        if head[3] > 0 :
            buf2 = sockSession.recv(head[3])
            body = json.loads(buf2)
            if body['status_code'] == 255:
                DSAURServer().SendUploadData(buf1+buf2)
            elif body['status_code'] == 254:
                pass
            else:
                import handlers.RequestProtocolData
                handlers.RequestProtocolData(head,body,sockSession)
        else:
            print '+++++++++++++++++++'
            #pass
    else:
        print buf1.strip()
    
# 主动socket数据处理
def handleDataAct(sockSession):
    buf1 = sockSession.recv(16)
    databuf = ''
    if len(buf1) == 16 :
        head = struct.unpack('!4i', buf1)
        if head[3] > 0 :
            rd_len = head[3]
            while len(databuf) < rd_len:
                rd_len = rd_len - len(databuf)
                tempdata = sockSession.recv(rd_len)
                databuf.join(tempdata)
            buf2 = databuf
            sockSession.databuf = sockSession.databuf[head[3]:]
            body = json.loads(buf2)
            print body
            if body['status_code'] == 255:
                DSAURServer().SendUploadData(buf1.join(buf2))
            else:
                pass
        else:
            pass
    else:
        print buf1.strip()

# data_session中的任务处理句柄
def handleTask(data_sess, data):
    from com_handlers import MsgDict
    MsgDict[data['MsgType']](data_sess,data)

# MyThread中的结果处理句柄
def handleResult(result_data):
    if result_data['handle']:
        result_data['handle'](result_data['data'])
    else:
        pass

DOhandles_Args_dict = {
                       'region' : {'handleData' : handleDataAct},
                       'unit' : {'handleTask' : handleTask, 'handleResult' : handleResult},
                       'node' : {'handleData' : handleDataAct, 'handleTask' : handleTask, 'handleResult' : handleResult},
                       }

class Server_Param():
    def __init__(self, server_name, server_ip, server_type):
        self.server_name = server_name
        self.server_ip = server_ip
        self.server_type = server_type
        
def doConnect(session):
    c_ip = session.addr[0]
    if DSAURServer().server_type == 'region':
        if c_ip in DSAURServer().server.unit_server_map:
            DSAURServer().server.unit_server_map[c_ip].setServerState(True,datetime.now())
        else:
            pass
    elif DSAURServer().server_type == 'node':
        DSAURServer().server.setUploadSessionflag(True)
        
def doClose(session):
    c_ip = session.addr[0]
    if DSAURServer().server_type == 'region':
        if c_ip in DSAURServer().server.unit_server_map:
            DSAURServer().server.unit_server_map[c_ip].setServerState(False,datetime.now())
        else:
            DSAURServer().delClient(id(session))
    elif DSAURServer().server_type == 'unit':
        if c_ip == DSAURServer().server.region_ip:
            DSAURServer().server.setUploadSession(None,False)
        elif c_ip in DSAURServer().server.node_server_map:
            DSAURServer().setNodeState(c_ip,False,datetime.now())
        else:
            DSAURServer().delClient(id(session))
    elif DSAURServer().server_type == 'node':
        if c_ip == DSAURServer().server.unit_ip:
            DSAURServer().server.setUploadSessionflag(False)
        else:
            DSAURServer().delClient(id(session))
            
class DSAURServer(object):
    instance = None
    region_ip = None
    ip_name_map = {}
    name_ip_map = {}
    unit_ipset = set()
    node_ipset = set()
    node_unit_map = {}
    cache_data = {}
    cache_mutex =  threading.Lock()
    client_map = {}
    logic_start_flag = False
    logic_start_mutex = threading.Lock()
        
    def __new__(cls, *args, **kwarg):
        if not cls.instance:
            cls.instance = super(DSAURServer, cls).__new__(cls, *args, **kwarg)
        return cls.instance
    
    def getDataItem(self, ename):
        data_conf = self.getDataConf(ename)
        if data_conf:
            return self.server.getDataItem(data_conf)
        else:
            pass
    
    def getDataValue(self, ename):
        return self.server.getDataValue(ename)
    
    def getDataConf(self, ename):
        if self.server:
            return self.server.getDataConf(ename)
        else:
            pass
        
    def getReason(self, ename):
        data_conf = self.getDataConf(ename)
        if data_conf:
            return self.server.getReason(data_conf)
        else:
            pass
        
    def setReason(self, ename):
        data_conf = self.getDataConf(ename)
        if data_conf:
            self.server.setReason(data_conf)
        else:
            pass
    
    def getLogicStartFlag(self):
        return self.logic_start_flag
        
    def doFinish(self):
        self.server.finishCmpSet()
        self.logic_start_mutex.acquire()
        self.logic_start_flag = False
        self.logic_start_mutex.release()
    
    def setFinishFlag(self, name):
        flag = self.server.checkStartFlag(name)
        if self.logic_start_flag != flag:
            self.logic_start_mutex.acquire()
            self.logic_start_flag = flag
            self.logic_start_mutex.release()
        else:
            pass
    
    @classmethod
    def putDataToCache(self, ename, data):
        self.cache_mutex.acquire()
        self.cache_data[ename] = data
        self.cache_mutex.release()
        
    @classmethod
    def getAndClearDataCache(self):
        cache = {}
        self.cache_mutex.acquire()
        deepcopy(self.cache_data)
        self.cache_data.clear()
        self.cache_mutex.release()
        return cache
    
    def Init(self, server_ip, port):
        self.server_ip = server_ip
        self.server_type = None
        self.port = port
        self.server = None
        self.Service = None
        from deviceSet import DB_conf
        self.db = DB_conf(server_ip+':3306','smarthomeDB','root','123456')
        sqlConnection = torndb.Connection(server_ip+':3306','smarthomeDB', user='root', password='123456')
        ress = sqlConnection.query("select server_name,server_type,server_ip from ServerParam")
        for res in ress:
            self.name_ip_map[res['server_name']] = res['server_ip']
            self.ip_name_map[res['server_ip']] = res['server_name']
            if res['server_type'] == 'region':
                self.region_ip = res['server_ip']
            elif res['server_type'] == 'unit':
                self.unit_ipset.add(res['server_ip'])
            elif res['server_type'] == 'node':
                self.node_ipset.add(res['server_ip'])
            else:
                pass
        sqlConnection.close()
        if self.server_ip == self.region_ip:
            print 'region'
            self.server_type = 'region'
        elif self.server_ip in self.unit_ipset:
            print 'Unit'
            self.server_type = 'unit'
        elif self.server_ip in self.node_ipset:
            print 'Node'
            self.server_type = 'node'
        else:
            print 'Nothing'
            
    def stop(self):
        self.server.stopWork()
        asyncore.close_all()
        
    def addClient(self, sockSession):
        self.client_map[id(sockSession)] = sockSession
        
    def delClient(self, Id):
        del self.client_map[Id]
        
    def startService(self,handleConnect):
        self.Service = AsyncServer(self.server_ip,self.port,handleConnect)
        self.Service.run()
        self.initData()
        self.server.startWork()
        asyncore.loop()
        
    def initData(self):
        if self.server_type in Server_dict:
            self.server = \
            Server_dict[self.server_type](self.db,
                                          self.server_ip,
                                          self.ip_name_map[self.server_ip],
                                          DoInithandle_dict[self.server_type])
            self.server.initServer(**DOhandles_Args_dict[self.server_type])
        else:
            print 'No Data init!'
            
    def SendUploadData(self,data):
        try:
            if self.server.upload_Session is not None:
                self.server.upload_Session.sendData(data)
            for client in self.client_map.values():
                client.sendData(data)
        except Exception as e:
            print 'SendUploadData Error :' , e
            
    def getDataSession(self, session_name):
        return self.server.getDataSession(session_name)
    
    def getDataSessions(self, server_name):
        return self.server.getDataSessions(server_name)
        
def PingIP(strIp):
    import os
    ret = os.system('ping -c 1 -W 1 %s' % strIp)
    if ret:
        return False
    else:
        return True
    
def doRegionInit(region_server):
    for key, server in region_server.unit_server_map.items():
        if server.state is False:
            region_server.setUnitState(key, False, datetime.now())
        else:
            pass
        
class RegionDataServer(data_server):
    total_distime = datetime.min
    unitfinishflags = {}
    wait_interval = 3
    def __init__(self, db, server_ip, server_name, handleTimer):
        data_server.__init__(self, db, server_ip, server_name)
        self.server_type = 'region'
        self.unit_server_map = {}
        self.node_server_map = {}
        self.name_ip_map = {}
        self.handleTimer = handleTimer
        self.upload_Session = None
        
    def getDataSessions(self, server_name):
        if server_name in self.name_ip_map:
            server_ip = self.name_ip_map[server_name]
            server = None
            if server_ip in self.unit_server_map:
                server = self.unit_server_map[server_ip]
            else:
                server = self.node_server_map[server_ip]
            return server.getDataSessions()
        else:
            return []
        
    def getDataSession(self, session_name):
        data_sess = self.getDataSession(session_name)
        if data_sess:
            return data_sess
        for ser in self.unit_server_map.values():
            data_sess = ser.getDataSession(session_name)
            if data_sess:
                return data_sess
        for ser in self.node_server_map.values():
            data_sess = ser.getDataSession(session_name)
            if data_sess:
                return data_sess
        
    def setUnitState(self, unit_ip ,state, stateTime):
        self.unit_server_map[unit_ip].setServerState(state, stateTime)
        unit_name = DSAURServer().ip_name_map[unit_ip]
        for node,unit in DSAURServer().node_unit_map:
            if unit == unit_name:
                node_ip = DSAURServer().ip_name_map[node]
                self.setNodeState(node_ip, state, stateTime)
            else:
                pass
            
    def setNodeState(self, node_ip ,state, stateTime):
        self.node_server_map[node_ip].setServerState(state, stateTime)
    
            
    def getRealValue(self, ename):
        dataitem = self.getDataItem(ename)
        if dataitem:
                return dataitem.getRealValue()
        else:
            pass
        
    def getDataValue(self, ename):
        data_conf = self.dataConfs.get(ename)
        if data_conf:
            server_name = data_conf['server_name']
            if server_name == self.server_name:
                return self.getDataValue(data_conf)
            elif server_name in self.name_ip_map:
                server_ip = self.name_ip_map[server_name]
                if server_ip in self.unit_server_map:
                    return self.unit_server_map[server_name].getDataValue(data_conf)
                else:
                    return self.node_server_map[server_name].getDataValue(data_conf)
            else:
                pass
            
    
    def getDataItem(self, ename):
        dataitem = None
        if ename in self.dataConfs:
            data_conf = self.dataConfs[ename]
            if data_conf['server_name'] == self.server_name:
                dataitem = data_server.getDataItem(self, data_conf)
            elif data_conf['server_name'] in self.name_ip_map:
                server_ip = self.name_ip_map[data_conf['server_name']]
                if server_ip in self.unit_server_map:
                    dataitem = self.unit_server_map[server_ip].getDataItem(data_conf)
                else:
                    dataitem = self.node_server_map[server_ip].getDataItem(data_conf)
            else:
                pass
        else:
            pass
        return dataitem
        
    def initServer(self, **args):
        for u_ip in DSAURServer().unit_ipset:
            u_name = DSAURServer().ip_name_map[u_ip]
            self.unitfinishflags[u_name] = {'flag' : False, 'time' : datetime.now()}
            self.unit_server_map[u_ip] = data_server(u_ip, u_name,
                    AsyncSession(u_ip,8899,args['handleData'],
                                 Server_Param(u_ip,u_name,'unit'),self.db))
        for n_ip in DSAURServer().node_ipset:
            n_name = DSAURServer().ip_name_map[n_ip]
            self.node_server_map[n_ip] = data_server(n_ip, n_name, None)
            self.name_ip_map[n_name] = n_ip
        self.timer = threading.Timer(3,self.handleTimer,args=[self,])
        self.timer.start()
        
    def finishCmpSet(self):
        self.total_distime = datetime.now()
        
    def checkStartFlag(self, unit_name):
        flag = True
        dis_time = self.total_distime
        if unit_name in self.sessfinishflags:
            self.unitfinishflags[unit_name] = {'flag' : True, 'time' : datetime.now()}
        else:
            pass
        for item in self.unitfinishflags.items():
            if item['time'] > dis_time:
                if item['flag'] is False:
                    if (datetime.now() - item['time']).total_seconds() > self.wait_interval:
                        flag = False
                        break
                else:
                    pass
            else:
                if (datetime.now() - dis_time).total_seconds() > self.wait_interval:
                    flag = False
                    break
        return flag
    
def doUnitInit(unit_server):
    for node_ip in unit_server.node_server_map.keys():
        if unit_server.getNodeState(node_ip):
            unit_server.setNodeState(node_ip, False, datetime.now())
        else:
            pass
    if unit_server.getUploadSessionState() is False:
        unit_server.setUploadSession(None,False)
    else:
        pass
            

class UnitDataServer(data_server):
    total_distime = datetime.min
    sessfinishflags = {}
    wait_interval = 3
    def __init__(self, db, server_ip, server_name, handleTimer):
        data_server.__init__(self, db, server_ip, server_name)
        self.server_type = 'unit'
        self.upload_Session = None
        self.dis_time = datetime.min
        self.node_server_map = {}
        self.name_ip_map = {}
        self.AreaSendData = {}
        self.transmitData = {}
        self.init_ip = self.server_ip
        self.region_ip = DSAURServer().region_ip
        self.handleTimer = handleTimer
        self.firstflag = True
        self.handleTask = None
        self.handleResult = None
        
    def getDataSession(self, session_name):
        data_sess = data_server.getDataSession(self,session_name)
        if data_sess:
            return data_sess
        for ser in self.node_server_map.values():
            data_sess = ser.getDataSession(session_name)
            if data_sess:
                return data_sess
            
    def getDataSessions(self, server_name):
        if self.server_name == server_name:
            return data_server.dev_data
        else:
            pass
        if server_name in self.name_ip_map:
            server_ip = self.name_ip_map[server_name]
            return self.node_server_map[server_ip].dev_data
        else:
            return dict()
        
    def getUploadSessionState(self):
        if self.upload_Session:
            return self.upload_Session.connected
        else:
            return False
        
    def setUploadSession(self, session, flag):
        self.upload_Session = session
        if flag is False:
            self.dis_time = datetime.now()
        else:
            if self.firstflag is False:
                self.initData(self.region_ip, self.handleTask, self.handleResult)
            else:
                self.firstflag = False
                
    def setNodeSession(self, node_ip, session):
        self.node_server_map[node_ip].sockSession = session
        
    def getNodeState(self, node_ip):
        if node_ip in self.node_server_map:
            return self.node_server_map[node_ip].connected
        else:
            return False
        
    def setNodeState(self, node_ip ,state, stateTime):
        self.node_server_map[node_ip].setServerState(state, stateTime)
        
    def getRealValue(self, ename):
        value = None
        if ename in self.dataConfs:
            data_conf = self.dataConfs[ename]
            value = data_server.getRealValue(self, data_conf)
        elif data_conf['server_name'] in self.name_ip_map:
            value = self.node_server_map[self.name_ip_map[data_conf['server_name']]].\
            getRealValue(data_conf)
        else:
            value = None
            if ename in self.AreaSendData or ename in self.transmitData:
                data = self.getData(data_conf)
                value = data.getRealValue()
            else:
                pass
        return value
        
    def getDataValue(self, ename):
        value = None
        if ename in self.dataConfs:
            data_conf = self.dataConfs[ename]
            if data_conf['server_name'] == self.server_name:
                value = data_server.getDataValue(self, data_conf)
            elif data_conf['server_name'] in self.name_ip_map:
                value = self.node_server_map[self.name_ip_map[data_conf['server_name']]].\
                getDataValue(data_conf)
            else:
                value = None
                if ename in self.AreaSendData or ename in self.transmitData:
                    dataitem = self.AreaSendData[ename]
                    if self.upload_Session and self.upload_Session.connected:
                        value = dataitem.value
                    else:
                        dis_interval = dataitem.getDisInterval()
                        if (datetime.now() - self.dis_time).total_seconds() < dis_interval * 60:
                            value = dataitem.value
                        else:
                            pass
                else:
                    pass
        else:
            pass
        return value
        
    def getDataItem(self, ename):
        data_conf = self.dataConfs.get(ename)
        if ename in self.dataConfs:
            data_conf = self.dataConfs[ename]
            if data_conf.sever_name == self.server_name:
                rd = data_server.getDataItem(self, data_conf)
            elif data_conf.sever_name in DSAURServer().node_ip_map:
                n_ip = DSAURServer().node_ip_map[data_conf.sever_name]
                if n_ip in self.node_server_map:
                    rd = self.node_server_map[n_ip].getDataItem(data_conf)
                else:
                    pass
            else:
                if data_conf.sever_name == 'region':
                    if ename in self.AreaSendData:
                        rd = self.AreaSendData[ename]
                    else:
                        pass
                else:
                    if ename in self.transmitData:
                        rd = self.transmitData[ename]
                    else:
                        pass
                if rd and rd.dis_time < self.dis_time:
                    rd.dis_flag = True
                    rd.dis_flag = self.dis_time
                else:
                    pass
        else:
            pass
        return rd
        
    def initServer(self, **args):
        if PingIP(self.region_ip):
            self.init_ip = self.region_ip
        else:
            pass
        self.initData(self.init_ip, args['handleTask'], args['handleResult'])
        for node, unit in DSAURServer().node_unit_map:
            if unit == self.server_name:
                node_ip = DSAURServer().name_ip_map[node]
                self.node_server_map[node_ip] = data_server(node_ip,node)
                self.node_server_map[node_ip].initServerState(self.init_ip)
                self.node_server_map[node_ip].initData(self.init_ip)
                self.name_ip_map[node] = node_ip
        self.__initOtherData()
        for sess_name in self.getDataSessionNames():
            self.sessfinishflags[sess_name] = {'flag' : False, 'time' : datetime.now()}
        for node_server in self.node_server_map.values():
            for sess_name in node_server.getDataSessionNames():
                self.sessfinishflags[sess_name] = {'flag' : False, 'time' : datetime.now()}
        self.timer = threading.Timer(3,self.handleTimer,args=[self,])
        self.timer.start()
        
    def finishCmpSet(self):
        self.total_distime = datetime.now()
        
    def checkStartFlag(self, sess_name):
        flag = True
        dis_time = self.total_distime
        if sess_name in self.sessfinishflags:
            self.sessfinishflags[sess_name] = {'flag' : True, 'time' : datetime.now()}
        else:
            pass
        for item in self.sessfinishflags.items():
            if item['time'] > dis_time:
                if item['flag'] is False:
                    if (datetime.now() - item['time']).total_seconds() > self.wait_interval:
                        flag = False
                        break
                else:
                    pass
            else:
                if (datetime.now() - dis_time).total_seconds() > self.wait_interval:
                    flag = False
                    break
        return flag
        
    def __initOtherData(self):
        db = self.db
        sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        ress = sqlConnection.query("select DataType.data_ename,DataType.pri,DataType.data_cname,\
        DataType.server_name,DataType.data_type, DataType.dev_name, DataType.conf_name from \
        DataType inner join transmitData on DataType.data_ename = transmitData.data_ename and \
        transmitData.server_name = %s",self.server_name)
        for res in ress:
            data_conf = UserDict()
            for k, v in res:
                data_conf[k] = v
            if res['dev_name']:
                    items = sqlConnection.query("select session_name,dev_id from Device \
                    Where dev_name = %s",res['dev_name'])
                    
                    
                    self.dataConfs[res['data_ename']] = data_conf(res['data_ename'],res['data_cname'],
                                                          self.server_name,None,items[0]['session_name'],
                                                          items[0]['dev_id'],res['conf_name'])
            else:
                self.dataConfs[res['data_ename']] = data_conf(res['data_ename'],res['data_cname'],
                                                          self.server_name,res['data_type'])
            if res['pri'] != 0:
                self.dataPriors[res['data_ename']] = res['pri']
            else:
                pass
            sets = sqlConnection.query("select DataInfo.data_ename,DataInfo.value,\
            DataInfo.error_flag,DataInfo.time,DataInfo.dis_flag,DataInfo.dis_time,\
            DataConstraint.min_variation,DataConstraint.min_val,DataConstraint.max_val,\
            DataConstraint.dis_interval from DataInfo inner join DataConstraint inner join \
            on DataInfo.data_ename = DataConstraint.data_ename and \
            DataInfo.data_ename = %s",res['data_ename'])
            dataconstraint = UserDict()
            templist = ['min_variation', 'min_val', 'max_val', 'dis_interval']
            for k in templist:
                dataconstraint[k] = float(sets[0][k]) if sets[0][k] else sets[0][k]
            dataitem = data_param(res['data_ename'],dataconstraint,
                                                  float(sets[0]['value']),sets[0]['error_flag'],
                                                  sets[0]['time'])
            if res['server_name'] == 'region':
                self.AreaSendData[res['data_ename']] = dataitem
            else:
                self.transmitData[res['data_ename']] = dataitem
        sqlConnection.close()
        
def doNodeInit(node_server):
    if node_server.getUploadSessionState() is False:
        node_server.setUploadSessionflag(False)
    else:
        pass
            
class NodeDataServer(data_server):
    def __init__(self, db, server_ip, server_name, handleTimer):
        data_server.__init__(self, db, server_ip, server_name, True)
        self.server_type = 'node'
        self.init_ip = self.server_ip
        self.upload_Session = None
        self.dis_time = None
        self.unit_ip = None
        self.firstflag = True
        self.handleData = None
        self.handleTask = None
        self.handleResult = None
        self.handleTimer = handleTimer
        
    def getUploadSessionState(self):
        if self.upload_Session:
            return self.upload_Session.connected
        else:
            return False
        
    def getDataSession(self, session_name):
        data_sess = data_server.getDataSession(self,session_name)
        if data_sess:
            return data_sess
        
    def getDataSessions(self, server_name):
        if self.server_name == server_name:
            return data_server.dev_data
        else:
            return []
        
    def setUploadSessionflag(self, flag):
        startcmp = False
        if flag is False:
            self.dis_time = datetime.now()
        else:
            if self.firstflag:
                self.firstflag = False
                if self.init_ip == self.server_ip:
                    self.initServer(self.handleTask, self.handleResult)
                    startcmp = True
                else:
                    pass
            else:
                self.initServer(self.handleTask, self.handleResult)
                startcmp = True
        if startcmp:
            pass
#             程序计算开始
        
    def getDataItem(self, ename):
        data_conf = self.dataConfs.get(ename)
        if data_conf:
            return data_server.getDataItem(self, data_conf)
        else:
            pass
        
    def getDataValue(self, ename):
        data_conf = self.dataConfs.get(ename)
        if data_conf:
            return self.getDataValue(data_conf)
        else:
            pass
    
    def initServer(self, **args):
        self.handleData = args['handleData']
        self.handleTask = args['handleTask']
        self.handleResult = args['handleResult']
        region_ip = DSAURServer().region_ip
        unit_name = DSAURServer().name_ip_map[self.server_name]
        unit_ip = DSAURServer().ip_name_map[unit_name]
        self.unit_ip = unit_ip
        if PingIP(unit_ip):
            if PingIP(region_ip):
                self.init_ip = region_ip
            else:
                self.init_ip = unit_ip
        else:
            pass
        self.initData(self.init_ip, self.handleTask, self.handleResult)
        self.upload_Session = AsyncSession(unit_ip,8899,self.handleData,
                                 Server_Param(unit_name,unit_ip,'unit'),self.db)
        self.timer = threading.Timer(3,self.handleTimer,args=[self,])
        self.timer.start()
        
Server_dict = {
               'region'  :  RegionDataServer,
               'unit'  :  UnitDataServer,
               'node' : NodeDataServer,
               }

DoInithandle_dict = {
                 'region'  :  doRegionInit,
                 'unit'  :  doUnitInit,
                 'node' : doNodeInit,
                 }

def restartService():
    try:
        DSAURServer().stop()
        DSAURServer().startService(handleConnect)
    except Exception as e:
        print e

def handleConnect(pair):
    sock, addr = pair
    print addr
    sockSession = None
    if DSAURServer().server_type == 'unit':
        if addr[0] == DSAURServer().region_ip:
            sockSession = AsyncClient(sock,handleData,Server_Param('region',addr[0],'region'))
            DSAURServer().server.setUploadSession(sockSession,True)
#             上报各个节点的连接状态
        elif addr[0] in DSAURServer().node_ipset:
            sockSession = AsyncClient(sock,handleData,
                                      Server_Param(DSAURServer().ip_name_map[addr[0]],addr[0],'node'))
            DSAURServer().server.setNodeSession(addr[0],sockSession)
            DSAURServer().server.setNodeState(addr[0],True,datetime.now())
        else:
            sockSession = AsyncClient(sock,handleData)
            DSAURServer().addClient(sockSession)
    else:
        sockSession = AsyncClient(sock,handleData)
        DSAURServer().addClient(sockSession)
    print sockSession
