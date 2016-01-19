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
import com_handlers
import struct

# 被动socket数据处理
def handleData(sockSession):
    buf = sockSession.recv(100)
    print buf.strip()
    sockSession.sendData("yang")
    
# 主动socket数据处理
def handleDataAct(sockSession):
    buf = sockSession.recv(100)
    print buf.strip()
    sockSession.sendData("yang")

# data_session中的任务处理句柄
def handleTask(data_sess, data):
    com_handlers.MsgDict[data['MsgType']](data_sess,data)

# MyThread中的结果处理句柄
def handleResult(result_data):
    result_data['handle'](result_data['data'])

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
    if DSAURServer().server_type == 'area':
        if c_ip in DSAURServer().server.unit_server_map:
            DSAURServer().server.unit_server_map[c_ip].setState(True)
        else:
            pass
    elif DSAURServer().server_type == 'node':
        DSAURServer().server.setUploadSessionflag(True)
        
def deleteClient(client):
    if id(client) in DSAURServer.client_map:
        del DSAURServer.client_map[id(client)]
        
def doClose(session):
    c_ip = session.addr[0]
    if DSAURServer().server_type == 'area':
        if c_ip in DSAURServer().server.unit_server_map:
            DSAURServer().server.unit_server_map[c_ip].setState(False)
        else:
            deleteClient(session)
    elif DSAURServer().server_type == 'unit':
        if c_ip == DSAURServer().server.region_ip:
            DSAURServer().server.setUploadSession(None)
        elif c_ip in DSAURServer().server.node_server_map:
            DSAURServer().server.node_server_map[c_ip].setState(False)
        else:
            deleteClient(session)
    elif DSAURServer().server_type == 'node':
        if c_ip == DSAURServer().server.unit_ip:
            DSAURServer().server.setUploadSessionflag(False)
        else:
            deleteClient(session)

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
        self.send(struct.pack('!4i', 0, 0, 0, 0))
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
        self.send(struct.pack('!4i', 0, 0, 0, 0))
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
            
    def stopSession(self, session_name):
        try:
            if session_name in self.process_map :
                if not self.session_map[session_name].alive:
                    del self.process_map[session_name]
                else :
                    self.session_map[session_name].putTaskQueue({'MsgType' : 1, 'data' : {'state' : 0}})
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
        
    def startSession(self, session_name):
        try:
            if session_name in self.process_map :
                if not self.session_map[session_name].alive:
                    del self.process_map[session_name]
                else :
                    self.session_map[session_name].putTaskQueue({'MsgType' : 1, 'data' : {'state' : 0}})
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
            
    def stopPatrol(self):
        for session_name in self.session_map:
            self.stopSession(session_name)
        
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
            if res['server_type'] == 'area':
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
        
    def startService(self,handleConnect):
        self.Service = AsyncServer(self.server_ip,self.port,handleConnect)
        self.initData()
        self.server.startWork()
        self.Service.run()
        asyncore.loop()
        
    def initData(self):
        if self.server_type in Server_dict:
            self.server = \
            Server_dict[self.server_type](self.server_ip,
                                          self.ip_name_map[self.server_ip],
                                          DoInithandle_dict[self.server_type])
            self.server.initServer(**DOhandles_Args_dict[self.server_type])
        else:
            print 'No Data init!'
            
    def SendUploadData(self,data):
        if self.server.upload_Session is not None:
            self.server.upload_Session.sendData(data)
        for client in self.client_map.values():
            client.sendData(data)
            
    def getDataSession(self, session_name):
        return self.server.getDataSession(session_name)
            
class data_server():
    dataConfs = {}
    def __init__(self, server_ip, server_name, state = True, sockSession=None):
        self.server_ip = server_ip
        self.server_name = server_name
        self.sockSession = sockSession
        self.db = DSAURServer().db
        self.state = state
        self.dis_time = None
        self.dev_data = None 
        self.udev_data = {}
        self.init_ip = None
        self.handleTask = None
        self.handleResult = None
        
    def startWork(self):
        self.dev_data.startPatrol()
        
    def stopWork(self):
        self.dev_data.stopPatrol()
        
    def getDataSession(self, session_name):
        if session_name in self.dev_data.session_map:
            return self.dev_data.session_map[session_name]
        
    def getDataSessionNames(self):
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
                dataconstraint = data_constraint(float(res['min_variation']),\
                float(res['min_val']) if res['min_val'] else res['min_val'],\
                float(res['max_val']) if res['max_val'] else res['max_val'],\
                                                     res['dis_interval'])
                data = basic_data(res['data_ename'],float(res['value']),res['error_flag'],res['time'],res['dis_flag'],res['dis_time'])
                self.udev_data[res['data_type']][res['data_ename']] = data_param(data,dataconstraint)
        sqlConnection.close()
        
    def __initDataConfs(self, init_ip):
        db = self.db
        db.addr = init_ip + ':3306'
        sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        ress = sqlConnection.query("select data_ename,data_cname,data_type from DataType where data_type is not NULL")
        for res in ress:
            self.dataConfs[res['data_ename']] = data_conf(res['data_ename'],res['data_cname'],self.server_name,res['data_type'])
        ress = sqlConnection.query('select DataType.data_ename,DataType.data_cname,DataType.conf_name, \
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
    
def doRegionInit(region_server):
    for key, server in region_server.unit_server_map:
        if server.state is False:
            region_server.setUnitState(key, False)
        else:
            pass
        
class RegionDataServer(data_server):
    total_distime = datetime.min
    unitfinishflags = {}
    wait_interval = 3
    def __init__(self, server_ip, server_name, handleTimer):
        data_server.__init__(self, server_ip, server_name, True)
        self.server_type = 'area'
        self.unit_server_map = {}
        self.node_server_map = {}
        self.name_ip_map = {}
        self.handleTimer = handleTimer
        self.upload_Session = None
        
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
        
    def setUnitState(self, unit_ip ,flag):
        self.unit_server_map[unit_ip].setState(flag)
        unit_name = DSAURServer().ip_unit_map[unit_ip]
        for node,unit in DSAURServer().node_unit_map:
            if unit == unit_name:
                node_ip = DSAURServer().ip_node_map[node]
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
        
    def initServer(self, **args):
        for u_ip in DSAURServer().unit_ipset:
            u_name = DSAURServer().ip_name_map[u_ip]
            self.unitfinishflags[u_name] = {'flag' : False, 'time' : datetime.now()}
            self.unit_server_map[u_ip] = data_server(u_ip, u_name, False, 
                    AsyncSession(self.server_ip,8899,args['handleData'],
                                 Server_Param(u_ip,u_name,'unit'),self.db))
            self.name_ip_map[u_name] = u_ip
        for n_ip in DSAURServer().node_ipset:
            n_name = DSAURServer().ip_name_map[n_ip]
            self.node_server_map[n_ip] = data_server(n_ip, n_name, False, None)
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
    total_distime = datetime.min
    sessfinishflags = {}
    wait_interval = 3
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
        
    def setUploadSession(self, session, flag):
        self.upload_Session = session
        if flag is False:
            self.dis_time = datetime.now()
        else:
            if self.firstflag is False:
                self.initData(self.region, self.handleTask, self.handleResult)
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
            elif dataconf.sever_name in DSAURServer().node_ip_map:
                n_ip = DSAURServer().node_ip_map[dataconf.sever_name]
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
        
    def initServer(self, **args):
        if PingIP(self.region_ip):
            self.init_ip = self.region_ip
        else:
            pass
        self.initData(self.init_ip, args['handleTask'], args['handleResult'])
        for node, unit in DSAURServer().node_unit_map:
            if unit == self.server_name:
                node_ip = DSAURServer().name_ip_map[node]
                self.node_server_map[node_ip] = data_server(node_ip,node,False)
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
            data = basic_data(sets[0]['data_ename'],float(sets[0]['value']),sets[0]['error_flag'],sets[0]['time'],sets[0]['dis_flag'],sets[0]['dis_time'])
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
        self.handleData = None
        self.handleTask = None
        self.handleResult = None
        self.handleTimer = handleTimer
        
    def getDataSession(self, session_name):
        data_sess = self.getDataSession(session_name)
        if data_sess:
            return data_sess
        
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
    if addr[0] == DSAURServer().region_ip:
        sockSession = AsyncClient(sock,handleData,('area',addr[0],'area'))
        DSAURServer().server.setUploadSession(sockSession)
    elif addr[0] in DSAURServer().node_ipset:
        sockSession = AsyncClient(sock,handleData,(DSAURServer().ip_node_map[addr[0]],addr[0],'node'))
        DSAURServer().server.node_server_map[addr[0]].sockSession = sockSession
        DSAURServer().server.node_server_map[addr[0]].setState(True)
    else:
        sockSession = AsyncClient(sock,handleData)
        DSAURServer.client_map[id(sockSession)] = sockSession
    print sockSession
