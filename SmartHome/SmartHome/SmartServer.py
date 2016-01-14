#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月28日

@author: sanhe
'''
import asyncore
import socket
import threading
import torndb
import time
import multiprocessing
from datetime import datetime
from basedata import data_conf
from basedata import basic_data
from basedata import data_constraint
from basedata import data_param
from copy import deepcopy
from decimal import *

class Server_Param():
    def __init__(self, server_name, server_ip, server_type):
        self.server_name = server_name
        self.server_ip = server_ip
        self.server_type = server_type
        
def doConnect(session):
    c_ip = session.addr[0]
    if SmartServer().server_type == 'area':
        if c_ip in SmartServer().server.unit_server_map:
            SmartServer().server.unit_server_map[c_ip].setState(True)
        else:
            pass
    elif SmartServer().server_type == 'node':
        SmartServer().server.setUploadSessionflag(True)
        
def doClose(session):
    c_ip = session.addr[0]
    if SmartServer().server_type == 'area':
        if c_ip in SmartServer().server.unit_server_map:
            SmartServer().server.unit_server_map[c_ip].setState(False)
        else:
            pass
    elif SmartServer().server_type == 'unit':
        if c_ip == SmartServer().server.area_ip:
            SmartServer().server.setUploadSession(None)
        elif c_ip in SmartServer().server.node_server_map:
            SmartServer().server.node_server_map[c_ip].setState(False)
    elif SmartServer().server_type == 'node':
        if c_ip == SmartServer().server.unit_ip:
            SmartServer().server.setUploadSessionflag(False)
        else:
            pass

class AsyncSession(asyncore.dispatcher_with_send):
    def __init__(self, host, port, handleData, server_para, db=None):
        asyncore.dispatcher_with_send.__init__(self)
        self.server_name = server_para.server_name
        self.server_type = server_para.server_type
        self.server_ip = server_para.server_ip
        self.startUpload = False
        self.addr = (host, port)
        self.sqlConnection = None
        if db is not None:
            self.sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.handleData = handleData
        self.timer = threading.Timer(3,self.handle_timer)
        
    def handle_timer(self):
        self.send('1234567890\n')
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        
    def handle_read(self):
        asyncore.dispatcher_with_send.handle_read(self)
        self.timer.cancel()
        if self.handleData:
            self.handleData(self)
        else:
            buf = self.recv(100)
            print buf.strip()
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        
    def handle_connect(self):
        asyncore.dispatcher_with_send.handle_connect(self)
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        doConnect(self)
        
    def handle_close(self):
        asyncore.dispatcher_with_send.handle_close(self)
        self.close()
        try:
            doClose(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(self.addr)
        except Exception as e:
            print e
        
    def sendData(self,data):
        self.timer.cancel()
        self.send(data)

class AsyncClient(asyncore.dispatcher_with_send):
    def __init__(self, sock, handleData, server_para=None, db = None):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.server_name = None
        self.server_type = 'client'
        self.server_ip = None
        self.startUpload = False
        if server_para is not None:
            self.server_name = server_para.server_name
            self.server_type = server_para.server_type
            self.server_ip = server_para.server_ip
        self.handleData =handleData
        self.sqlConnection = None
        if db is not None:
            self.sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        if self.connected:
            self.timer = threading.Timer(3,self.handle_timer)
            self.timer.start()
        
    def handle_read(self):
        asyncore.dispatcher_with_send.handle_read(self)
        self.timer.cancel()
        if self.handleData:
            self.handleData(self)
        else:
            buf = self.recv(100)
            print buf.strip()
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        
    def handle_timer(self):
        self.send('1234567890\n')
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        
    def sendData(self,data):
        self.timer.cancel()
        self.send(data)
        
    def handle_close(self):
        asyncore.dispatcher_with_send.handle_close(self)
        if self.sqlConnection:
            self.sqlConnection.close()
            self.sqlConnection = None
            doClose(self)
        
class AsyncServer(asyncore.dispatcher):
    def __init__(self, host, port, handleConnect):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host,port))
        self.handleConnect = handleConnect
        
    def run(self):
        self.listen(5)
        
    def handle_accept(self):
        asyncore.dispatcher.handle_accept(self)
        pair = self.accept()
        if self.handleConnect:
            self.handleConnect(pair)
        
class MyThread(threading.Thread):
    def __init__(self, session, handleResult):
        threading.Thread.__init__(self)
        self.session = session
        self.stop_thread = False
        self.handleResult = handleResult
        
    def run(self):
        while not self.stop_thread :
            task = self.session.getResultQueue()
            if task :
                self.handleResult(task)
            time.sleep(0.01)
            
    def stop(self):
        self.stop_thread = True
        
class sessionSet():
    def __init__(self, server_name, handleTask=None, handleResult=None):
        self.server_name = server_name
        self.session_map = {}
        self.handleTask = handleTask
        self.handleResult = handleResult
        self.process_map = {}
        self.thread_map = {}
    
    def getDataItem(self, session_name, dev_name, conf_name):
        if session_name in self.session_map:
            return self.session_map[session_name].getDataItem(dev_name, conf_name)
        else:
            pass
        
    def getData(self, session_name, dev_name, conf_name):
        if session_name in self.session_map:
            return self.session_map[session_name].getData(dev_name, conf_name)
        else:
            pass
        
    def setData(self, session_name, dev_name, conf_name, data):
        if session_name in self.session_map:
            self.session_map[session_name].setData(dev_name,conf_name,data)
        
    def startSession(self, session_name):
        try:
            if session_name in self.process_map :
                if not self.session_map[session_name].alive:
                    del self.process_map[session_name]
                else :
                    self.session_map[session_name].putTaskQueue({'MsgType' : 3, 'data' : {'state' : 0}})
                    while self.dataSession_map[session_name].alive():
                        time.sleep(3)
                    del self.process_map[session_name]
                if session_name in self.thread_map :
                    if self.thread_map[session_name].is_alive:
                        self.thread_map[session_name].stop()
                    del self.thread_map[session_name]
                else:
                    pass
        except Exception as e:
            print "startSession Error : " , e
        if session_name in self.session_map :
            p = multiprocessing.Process(target=self.session_map[session_name])
            self.process_map[session_name] = p
            p.start()
            th = MyThread(self.session_map[session_name],self.handleResult)
            self.thread_map[session_name] = th
            th.start()
        else:
            pass
        
    def startPatrol(self):
        for session_name in self.session_map:
            p = multiprocessing.Process(target=self.session_map[session_name])
            self.process_map[session_name] = p
            p.start()
            th = MyThread(self.session_map[session_name],self.handleResult)
            self.thread_map[session_name] = th
            th.start()
        
    def init(self, db):
        if db is not None:
            sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
            sqlString = "select session_name, session_id from DataSession Where server_name = %s"
            sessions = sqlConnection.query(sqlString, self.server_name)
            from deviceSet import deviceSet
            from data_session import data_session
            for session in sessions:
                devSet = deviceSet(session['session_name'], db)
                devSet.initData()
                self.session_map[session['session_name']] = data_session(self.server_name,
                                                                         session['session_name'],
                                                                         session['session_id'],
                                                                         devSet,
                                                                         self.handleTask)
            sqlConnection.close()
        else:
            pass
        
class SmartServer(object):
    instance = None
    area_ip = None
    ip_name_map = {}
    name_ip_map = {}
    unit_ipset = set()
    node_ipset = set()
    node_unit_map = {}
    startCmpFlag = False
    start_lock = threading.Lock()
    cache_data = {}
    cache_mutex =  threading.Lock()
        
    def __new__(cls, *args, **kwarg):
        if not cls.instance:
            cls.instance = super(SmartServer, cls).__new__(cls, *args, **kwarg)
        return cls.instance
    
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
            if res['server_type'] == 'area':
                self.area_ip = res['server_ip']
            elif res['server_type'] == 'unit':
                self.unit_ipset.add(res['server_ip'])
            elif res['server_type'] == 'node':
                self.node_ipset.add(res['server_ip'])
            else:
                pass
        sqlConnection.close()
        if self.server_ip == self.area_ip:
            print 'Area'
            self.server_type = 'area'
        elif self.server_ip in self.unit_ipset:
            print 'Unit'
            self.server_type = 'unit'
        elif self.server_ip in self.node_ipset:
            print 'Node'
            self.server_type = 'node'
        else:
            print 'Nothing'
    
    def checkCmpStart(self, session_name):
        flag = False
        startFlag = True
        dis_interval = 3
        if self.server:
            if session_name in self.server.upload_flag_map:
                self.server.upload_flag_map[session_name]['flag'] = True
                self.server.upload_flag_map[session_name]['time'] = datetime.now()
            else:
                pass
                return
            for sess_name, value in self.server.upload_flag_map.items():
                if sess_name != 'total':
                    if value['time'] < self.server.upload_flag_map['total']['time']:
                        value = self.upload_flag_map['total']
                    else:
                        pass
                    if value['flag'] is False:
                        if (datetime.now() - value['time']).total_seconds() < dis_interval:
                            startFlag = False
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
        else:
            pass
        if startFlag and startFlag is True:
            if self.startCmpFlag is False:
                self.start_lock.acquire()
                self.startCmpFlag = True
                flag = True
                self.start_lock.realease()
            else:
                pass
        else:
            pass
        return flag
            
        
    def finishCmpSet(self):
        self.server.upload_flag_map['total']['time'] = datetime.now()
                    
            
    def stop(self):
        asyncore.close_all()
        
    def startService(self,handleConnect):
        self.Service = AsyncServer(self.server_ip,self.port,handleConnect)
        self.Service.run()
        asyncore.loop()
        
    def initData(self):
        if self.server_type in Server_dict:
            Server_dict[self.server_type](self.server_ip,self.ip_name_map[self.server_ip])
        else:
            print 'No Data init!'
            
class data_server():
    dataConfs = {}
    upload_flag_map = {'total' : {'flag' : False, 'time' : datetime.now()}}
    def __init__(self, server_ip, server_name, state = True, sockSession=None):
        self.server_ip = server_ip
        self.server_name = server_name
        self.sockSession = sockSession
        self.db = SmartServer().db
        self.state = state
        self.dis_time = None
        self.dev_data = None 
        self.udev_data = {}
        self.init_ip = None
        self.handleTask = None
        self.handleResult = None
        
    def getDataSessions(self):
        return self.dev_data.session_map.keys()
        
    def setState(self, flag):
        if self.state != flag:
            self.state = flag
            if self.state is False:
                self.dis_time = datetime.now()
        else:
            pass
        
    def getDataItem(self, data_conf):
        data = self.getData(data_conf)
        dataitem = None
        if data:
            if data_conf.data_type is None:
                dataitem = self.dev_data.session_map[data_conf.session_name].getDataItem(
                                            data_conf.device_name,data_conf.conf_name)
                dataitem.setData(data)
            else:
                dataitem = self.udev_data[data_conf.data_type][data_conf.ename]
            dataitem.setData(data)
            return dataitem
        else:
            pass
        
    def getDataValue(self, data_conf):
        dataitem = self.getDataItem(data_conf)
        if dataitem:
                return dataitem.getValue()
        else:
            pass
        
    def getRealValue(self, data_conf):
        data = self.getData(data_conf)
        return data.getRealValue()
        
    def getData(self, data_conf):
        if data_conf.data_type is None:
            data = self.dev_data.getData(data_conf.session_name, data_conf.dev_name, data_conf.conf_name)
            if data.dis_time < self.dis_time:
                if self.state is False:
                    data.dis_flag = True
                    data.dis_time = self.dis_time
                else:
                    pass
            else:
                pass
            return data
        else:
            data = None
            if data_conf.data_type in self.udev_data:
                if data_conf.server_name in self.udev_data[data_conf.data_type]:
                    dataitem = self.udev_data[data_conf.data_type][data_conf.ename]
                    data = dataitem.getData()
                else:
                    pass
            else:
                pass
            if data is not None:
                if self.state is False:
                    data.dis_flag = True
                    data.dis_flag = self.dis_time
            return data
    
    def setData(self, data_conf, data):
        if data_conf.data_type is None:
            self.dev_data.setData(data_conf.session_name, data_conf.dev_name, data_conf.conf_name, data)
        else:
            if data_conf.data_type in self.udev_data:
                if data_conf.server_name in self.udev_data[data_conf.data_type]:
                    self.udev_data[data_conf.data_type][data_conf.ename].setData(data)
        
    def initData(self, init_ip, handleTask=None, handleResult=None):
        self.init_ip = init_ip
        self.handleTask = handleTask
        self.handleResult = handleResult
        self.__initDataConfs(init_ip)
        self.__initDevData(init_ip, handleTask, handleResult)
        self.__initUDevData(init_ip)
        
    def __initDevData(self, init_ip, handleTask=None, handleResult=None):
        self.dev_data = sessionSet(self.server_name, handleTask, handleResult)
        db = self.db
        db.addr = init_ip + ':3306'
        self.dev_data.init(db)
        
    def __initUDevData(self, init_ip):
        db = self.db
        db.addr = init_ip + ':3306'
        sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        ress = sqlConnection.query("select data_type from DataType where data_type is not NULL \
        and server_name = %s group by data_type",self.server_name)
        for res in ress:
            self.udev_data[res['data_type']] = {}
        for k in self.udev_data.keys():
            ress = sqlConnection.query("select DataType.data_type,DataInfo.data_ename,DataInfo.value,\
            DataInfo.error_flag,DataInfo.time,DataInfo.dis_flag,DataInfo.dis_time,\
            DataConstraint.min_variation,DataConstraint.min_val,DataConstraint.max_val,\
            DataConstraint.dis_interval from DataInfo inner join DataConstraint inner join \
            DataType on DataInfo.data_ename = DataConstraint.data_ename and \
            DataInfo.data_ename = DataType.data_ename and DataType.server_name = %s \
            and DataType.data_type = %s",self.server_name,k)
            for res in ress:
                dataconstraint = data_constraint(float(res[0]['min_variation']),\
                float(res[0]['min_val']) if res[0]['min_val'] else res[0]['min_val'],\
                float(res[0]['max_val']) if res[0]['max_val'] else res[0]['max_val'],\
                                                     res[0]['dis_interval'])
                data = basic_data(float(res['value']),res['error_flag'],res['time'],res['dis_flag'],res['dis_time'])
                self.udev_data[res['data_type']][res['data_ename']] = data_param(data,dataconstraint)
        sqlConnection.close()
        
    def __initDataConfs(self, init_ip):
        db = self.db
        db.addr = init_ip + ':3306'
        sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        ress = sqlConnection.query("select data_ename,data_cname,data_type from DataType where data_type is not NULL")
        for res in ress:
            self.dataConfs[res['data_ename']] = data_conf(res['data_ename'],res['data_cname'],self.server_name,res['data_type'])
        sqlConnection.query('select DataType.data_ename,DataType.data_cname,DataType.conf_name, \
        Device.dev_name, Device.session_name from DataType  inner join Device on \
        DataType.dev_name = Device.dev_name and DataType.server_name  = %s',self.server_name)
        for res in ress:
            self.dataConfs[res['data_ename']] = data_conf(res['data_ename'],res['data_cname'],
                                                          self.server_name,None,res['session_name'],
                                                          res['dev_name'],res['conf_name'])
        sqlConnection.close()
        
def PingIP(strIp):
    import os
    ret = os.system('ping -c 1 -W 1 %s' % strIp)
    if ret:
        return False
    else:
        return True
    
def doAreaInit(area_server):
    for key, server in area_server.unit_server_map:
        if server.state is False:
            area_server.setUnitState(key, False)
        else:
            pass
        
class AreaDataServer(data_server):
    def __init__(self, server_ip, server_name, handleTimer):
        data_server.__init__(self, server_ip, server_name, True)
        self.server_type = 'area'
        self.unit_server_map = {}
        self.node_server_map = {}
        self.name_ip_map = {}
        self.handleTimer = handleTimer
        
    def setUnitState(self, unit_ip ,flag):
        self.unit_server_map[unit_ip].setState(flag)
        unit_name = SmartServer().ip_unit_map[unit_ip]
        for node,unit in SmartServer().node_unit_map:
            if unit == unit_name:
                node_ip = SmartServer().ip_node_map[node]
                self.node_server_map[node_ip].setState(flag)
            else:
                pass
            
    def getRealValue(self, ename):
        dataitem = self.getDataItem(ename)
        if dataitem:
                return dataitem.getRealValue()
        else:
            pass
    
    def getDataItem(self, ename):
        dataitem = None
        if ename in self.dataConfs:
            dataconf = self.dataConfs[ename]
            if dataconf.sever_name == self.server_name:
                dataitem = data_server.getDataItem(self, data_conf)
            elif dataconf.sever_name in self.name_ip_map:
                server_ip = self.name_ip_map[dataconf.sever_name]
                if server_ip in self.unit_server_map:
                    dataitem = self.unit_server_map[server_ip].getDataItem(dataconf)
                else:
                    dataitem = self.node_server_map[server_ip].getDataItem(dataconf)
            else:
                pass
        else:
            pass
        return dataitem
    
    def getData(self, ename):
        dataitem = self.getDataItem(ename)
        if dataitem:
                return dataitem.getData()
        else:
            pass
            
    def getDataValue(self, ename):
        dataitem = self.getDataItem(ename)
        if dataitem:
                return dataitem.getValue()
        else:
            pass
        
    def initServer(self, handleData):
        for u_ip in SmartServer().unit_ipset:
            u_name = SmartServer().ip_name_map[u_ip]
            self.unit_server_map[u_ip] = data_server(u_ip, u_name, False, 
                    AsyncSession(self.server_ip,8899,handleData,
                                 Server_Param(u_ip,u_name,'unit'),self.db))
            self.name_ip_map[u_name] = u_ip
        for n_ip in SmartServer().node_ipset:
            n_name = SmartServer().ip_name_map[n_ip]
            self.node_server_map[n_ip] = data_server(n_ip, n_name, False, None)
            self.name_ip_map[n_name] = n_ip
        for server in self.unit_server_map.values():
            for session_name in server.getDataSessions():
                self.upload_flag_map[session_name] = {'flag' : False, 'time' : datetime.now()}
        for server in self.node_server_map.values():
            for session_name in server.getDataSessions():
                self.upload_flag_map[session_name] = {'flag' : False, 'time' : datetime.now()}
        self.timer = threading.Timer(3,self.handleTimer)
        self.timer.start()
    
def doUnitInit(unit_server):
    for key,server in unit_server.node_server_map:
        if server.state is False:
            unit_server.setNodeState(key,False)
        else:
            pass
    if unit_server.upload_Session is None or unit_server.upload_Session.connected is False:
        unit_server.setUploadSession(None,False)
    else:
        pass
            

class UnitDataServer(data_server):
    def __init__(self, server_ip, server_name, handleTimer):
        data_server.__init__(self, server_ip, server_name, True)
        self.server_type = 'unit'
        self.upload_Session = None
        self.dis_time = None
        self.node_server_map = {}
        self.name_ip_map = {}
        self.AreaSendData = {}
        self.transmitData = {}
        self.init_ip = self.server_ip
        self.area_ip = SmartServer().area_ip
        self.handleTimer = handleTimer
        self.firstflag = True
        self.handleTask = None
        self.handleResult = None
        
    def setUploadSession(self, session, flag):
        self.upload_Session = session
        if flag is False:
            self.dis_time = datetime.now()
        else:
            if self.firstflag is False:
                self.initData(self.area_ip, self.handleTask, self.handleResult)
#                 程序计算开始
            if self.firstflag:
                self.firstflag = False
        
    def setNodeState(self, node_ip ,flag):
        self.node_server_map[node_ip].setState(flag)
        
    def getRealValue(self, ename):
        value = None
        if ename in self.dataConfs:
            dataconf = self.dataConfs[ename]
            value = data_server.getRealValue(self, data_conf)
        elif dataconf.server_name in self.name_ip_map:
            value = self.node_server_map[self.name_ip_map[dataconf.server_name]].\
            getRealValue(dataconf)
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
            dataconf = self.dataConfs[ename]
            if dataconf.server_name == self.server_name:
                value = data_server.getDataValue(self, data_conf)
            elif dataconf.server_name in self.name_ip_map:
                value = self.node_server_map[self.name_ip_map[dataconf.server_name]].\
                getDataValue(data_conf)
            else:
                value = None
                if ename in self.AreaSendData or ename in self.transmitData:
                    dataitem = self.AreaSendData[ename]
                    data = self.getData(data_conf)
                    dataitem.setData(data)
                    value = dataitem.getValue()
                else:
                    pass
        else:
            pass
        return value
        
    def getData(self, ename):
        rd = None
        if ename in self.dataConfs:
            dataconf = self.dataConfs[ename]
            if dataconf.sever_name == self.server_name:
                rd = data_server.getData(self, dataconf)
            elif dataconf.sever_name in SmartServer().node_ip_map:
                n_ip = SmartServer().node_ip_map[dataconf.sever_name]
                if n_ip in self.node_server_map:
                    rd = self.node_server_map[n_ip].getData(dataconf)
                else:
                    pass
            else:
                if dataconf.sever_name == 'area':
                    if ename in self.AreaSendData:
                        rd = self.AreaSendData[ename].getData()
                    else:
                        pass
                else:
                    if ename in self.transmitData:
                        rd = self.transmitData[ename].getData()
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
        
    def initServer(self, handleTask, handleResult):
        if PingIP(self.area_ip):
            self.init_ip = self.area_ip
        else:
            pass
        self.initData(self.init_ip, handleTask, handleResult)
        for node, unit in SmartServer().node_unit_map:
            if unit == self.server_name:
                node_ip = SmartServer().name_ip_map[node]
                self.node_server_map[node_ip] = data_server(node_ip,node,False)
                self.node_server_map[node_ip].initData(self.init_ip)
                self.name_ip_map[node] = node_ip
        self.__initOtherData()
        for session_name in self.getDataSessions():
            self.upload_flag_map[session_name] = {'flag' : False, 'time' : datetime.now()}
        for server in self.node_server_map.values():
            for session_name in server.getDataSessions():
                self.upload_flag_map[session_name] = {'flag' : False, 'time' : datetime.now()}
        self.timer = threading.Timer(3,self.handleTimer)
        self.timer.start()
        
    def __initOtherData(self):
        db = self.db
        sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        ress = sqlConnection.query("select DataType.data_ename,DataType.data_cname,DataType.server_name,\
        DataType.data_type, DataType.dev_name, DataType.conf_name from DataType inner join \
        transmitData on DataType.data_ename = transmitData.data_ename and \
        transmitData.server_name = %s",self.server_name)
        for res in ress:
            if res['dev_name']:
                    items = sqlConnection.query("select session_name,dev_id from Device Where dev_name = %s",res['dev_name'])
                    self.dataConfs[res['data_ename']] = data_conf(res['data_ename'],res['data_cname'],
                                                          self.server_name,None,items[0]['session_name'],
                                                          items[0]['dev_id'],res['conf_name'])
            else:
                self.dataConfs[res['data_ename']] = data_conf(res['data_ename'],res['data_cname'],
                                                          self.server_name,res['data_type'])
            sets = sqlConnection.query("select DataInfo.data_ename,DataInfo.value,\
            DataInfo.error_flag,DataInfo.time,DataInfo.dis_flag,DataInfo.dis_time,\
            DataConstraint.min_variation,DataConstraint.min_val,DataConstraint.max_val,\
            DataConstraint.dis_interval from DataInfo inner join DataConstraint inner join \
            on DataInfo.data_ename = DataConstraint.data_ename and \
            DataInfo.data_ename = %s",res['data_ename'])
            dataconstraint = data_constraint(float(sets[0]['min_variation']),\
                    float(sets[0]['min_val']) if sets[0]['min_val'] else sets[0]['min_val'],\
                    float(sets[0]['max_val']) if sets[0]['max_val'] else sets[0]['max_val'],\
                                                     sets[0]['dis_interval'])
            data = basic_data(float(sets[0]['value']),sets[0]['error_flag'],sets[0]['time'],sets[0]['dis_flag'],sets[0]['dis_time'])
            if res['server_name'] == 'area':
                self.AreaSendData[res['data_ename']] = data_param(data,dataconstraint)
            else:
                self.transmitData[res['data_ename']] = data_param(data,dataconstraint)
        sqlConnection.close()
        
def doNodeInit(node_server):
    if node_server.upload_Session.connected is False:
        node_server.setUploadSessionflag(False)
    else:
        pass
            
class NodeDataServer(data_server):
    def __init__(self, server_ip, server_name, handleTimer):
        data_server.__init__(self, server_ip, server_name, True)
        self.server_type = 'node'
        self.init_ip = self.server_ip
        self.upload_Session = None
        self.dis_time = None
        self.unit_ip = None
        self.firstflag = True
        self.handleTask = None
        self.handleResult = None
        self.handleTimer = handleTimer
        
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
        
    def getData(self, ename):
        if ename in self.dataConfs:
            dataconf = self.dataConfs[ename]
            if dataconf.sever_name == self.server_name:
                data_server.getData(self, dataconf)
            else:
                pass
        else:
            pass
    
    def initServer(self, handleTask, handleResult):
        self.handleTask = handleTask
        self.handleResult = handleResult
        area_ip = SmartServer().area_ip
        unit_name = SmartServer().name_ip_map[self.server_name]
        unit_ip = SmartServer().ip_name_map[unit_name]
        self.unit_ip = unit_ip
        if PingIP(unit_ip):
            if PingIP(area_ip):
                self.init_ip = area_ip
            else:
                self.init_ip = unit_ip
        else:
            pass
        self.initData(self.init_ip, handleTask, handleResult)
        self.upload_Session = AsyncSession(unit_ip,8899,handleData,
                                 Server_Param(unit_name,unit_ip,'unit'),self.db)
        for session_name in self.getDataSessions():
            self.upload_flag_map[session_name] = {'flag' : False, 'time' : datetime.now()}
        self.timer = threading.Timer(3,self.handleTimer)
        self.timer.start()
        
Server_dict = {
               'area'  :  AreaDataServer,
               'unit'  :  UnitDataServer,
               'node' : NodeDataServer,
               }
        
def handleData(client):
    buf = client.recv(100)
    print buf.strip()
    client.sendData("yang")
    
global FLAG
FLAG = False

def handleConnect(pair):
    global FLAG
    print FLAG
    try:
        if not FLAG:
            FLAG = True
        else:
            FLAG = False
        if FLAG:
            SmartServer().stop()
#             time.sleep(2)
            SmartServer().startService(handleConnect)
            print 'restart'
        else:
            SmartServer().stop()
            print "start"
        return
    except Exception as e:
        print e
        return
    sock, addr = pair
    print addr
    sockSession = None
    if addr[0] == SmartServer().area_ip:
        sockSession = AsyncClient(sock,handleData,('area',addr[0],'area'))
        SmartServer().server.setUploadSession(sockSession)
    elif addr[0] in SmartServer().ip_node_map:
        sockSession = AsyncClient(sock,handleData,(SmartServer().ip_node_map[addr[0]],addr[0],'node'))
        SmartServer().server.node_server_map[addr[0]].sockSession = sockSession
        SmartServer().server.node_server_map[addr[0]].setState(True)
    else:
        sockSession = AsyncClient(sock,handleData)
    print sockSession
        
if __name__ == "__main__" :
    SmartServer().Init('172.16.1.16', 8899)
    SmartServer().startService(handleConnect)
#     server = AsyncServer('172.16.1.16',8899,handleConnect)
#     server.run()
#     asyncore.loop()
