#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月26日

@author: sanhe
'''
from UserDict import UserDict
from datetime import datetime
import torndb
import threading
import time
import multiprocessing
from basedata import data_param
from deviceSet import deviceSet
from data_session import data_session

class data_server():
    dataConfs = UserDict()
    def __init__(self, db, server_ip, server_name, doConnectState=None,sockSession=None):
        self.server_ip = server_ip
        self.server_name = server_name
        self.sockSession = sockSession
        self.db = db
        self.state = True
        self.stateTime = datetime.min
        self.dev_data = None 
        self.udev_data = UserDict()
        self.init_ip = None
        self.handleTask = None
        self.handleResult = None
        self.doConnectState = doConnectState
        
    def startWork(self):
        if self.dev_data:
            self.dev_data.startPatrol()
        else:
            pass
        
    def stopWork(self):
        if self.dev_data:
            self.dev_data.stopPatrol()
        else:
            pass
        
    def getDataSession(self, session_name):
        if self.dev_data:
            return self.dev_data.get(session_name)
        else:
            pass
        
    def getDataSessionNames(self):
        if self.dev_data:
            return self.dev_data.keys()
        else:
            pass
        
    def setServerState(self, state, stateTime):
        if self.state != state:
            self.state = state
            self.stateTime = stateTime
            if self.doConnectState:
                self.doConnectState(self)
        else:
            self.stateTime = stateTime
        
    def getDataItem(self, data_conf):
        if isinstance(data_conf, UserDict):
            return self.dev_data.getDataItem(data_conf.get('session_name'), 
                                      data_conf.get('dev_name'), 
                                      data_conf.get('conf_name'))
        else:
            pass
        
    def getDataValue(self, data_conf):
        value = None
        if isinstance(data_conf, UserDict):
            session_name = data_conf.get('session_name')
            dev_name = data_conf.get('dev_name')
            conf_name = data_conf.get('conf_name')
            value = self.dev_data.getData(session_name, dev_name, conf_name)
            if self.state:
                return value
            else:
                dis_interval = self.dev_data.getDisInterval(session_name, dev_name, conf_name)
                if (datetime.now() - self.stateTime).total_seconds() > dis_interval * 60:
                    return value
                else:
                    pass
        else:
            pass
        
    def getRealValue(self, data_conf):
        if isinstance(data_conf, UserDict):
            return self.dev_data.getRealValue(data_conf.get('session_name'), 
                                              data_conf.get('dev_name'), 
                                              data_conf.get('conf_name'))
        else:
            pass
        
    def getData(self, data_conf):
        if data_conf.get('data_type') is None:
            if isinstance(data_conf, UserDict):
                return self.dev_data.getData(data_conf.get('session_name'), 
                                                  data_conf.get('dev_name'), 
                                                  data_conf.get('conf_name'))
            else:
                pass
        else:
            dataset = self.udev_data.get(data_conf.get('data_type'))
            if dataset:
                return dataset.get(data_conf.get('data_ename'))
            pass
    
    def setData(self, data_conf, data):
        data_type =  data_conf.get('data_type')
        if data_type is None:
            self.dev_data.setData(data_conf.get('session_name'), 
                                  data_conf.get('dev_name'), 
                                  data_conf.get('conf_name'),
                                  data)
        else:
            
            if data_type in self.udev_data:
                data_ename = data_conf.get('ename_name')
                if data_ename in self.udev_data[data_type]:
                    self.udev_data[data_type][data_ename].setData(data)
                    
    def initServerState(self, init_ip):
        db = self.db
        if db:
            db.addr = init_ip + ':3306'
            sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
            ress = sqlConnection.query("select server_state, updatetime from \
                ServerState where server_name = %s",self.server_name)
            if len(ress) > 0:
                self.setServerState(ress[0]['server_state'],ress[0]['updatetime'])
            else:
                self.setServerState(False,datetime.min)
        else:
            pass
            
        
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
        if db:
            db.addr = init_ip + ':3306'
        else:
            pass
        self.dev_data.init(db)
        
    def __initUDevData(self, init_ip):
        db = self.db
        db.addr = init_ip + ':3306'
        sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        ress = sqlConnection.query("select data_type from DataType where data_type is not NULL \
        and server_name = %s group by data_type",self.server_name)
        for res in ress:
            self.udev_data[res['data_type']] = UserDict()
            for k in self.udev_data:
                ress = sqlConnection.query("select DataType.data_type,DataType.pri,\
                DataInfo.data_ename,DataInfo.value,DataInfo.error_flag,DataInfo.time,\
                DataConstraint.min_variation,DataConstraint.min_val,DataConstraint.max_val,\
                DataConstraint.dis_interval from DataInfo inner join DataConstraint inner join \
                DataType on DataInfo.data_ename = DataConstraint.data_ename and \
                DataInfo.data_ename = DataType.data_ename and DataType.server_name = %s \
                and DataType.data_type = %s",self.server_name,k)
                for res in ress:
                    dataconstraint = UserDict()
                    temlist = {'min_variation', 'min_val', 'max_val', 'dis_interval'}
                    for k in temlist:
                        v = res[k]
                        dataconstraint[k] = float(v) if v else v
                    dataitem = data_param(res['data_ename'],dataconstraint,
                                                  float(res['value']),res['error_flag'],
                                                  res['time'])
                    self.udev_data[res['data_type']][res['data_ename']] = dataitem
            sqlConnection.close()
        else:
            pass
        
    def __initDataConfs(self, init_ip):
        db = self.db
        if db:
            db.addr = init_ip + ':3306'
            sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
            ress = sqlConnection.query("select data_ename,data_cname,data_type from DataType where data_type is not NULL")
            for res in ress:
                data_conf = UserDict()
                for k, v in res.items():
                    data_conf[k] = v
                self.dataConfs[res['data_ename']] = data_conf
            ress = sqlConnection.query('select DataType.data_ename,DataType.pri,DataType.data_cname,DataType.conf_name, \
            Device.dev_name, Device.session_name from DataType  inner join Device on \
            DataType.dev_name = Device.dev_name and DataType.server_name  = %s',self.server_name)
            for res in ress:
                data_conf = UserDict()
                for k, v in res.items():
                    data_conf[k] = v
                self.dataConfs[res['data_ename']] = data_conf
            sqlConnection.close()
        else:
            pass

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

class sessionSet(UserDict):
    def __init__(self, server_name, handleTask=None, handleResult=None):
        UserDict.__init__(self)
        self.server_name = server_name
        self.handleTask = handleTask
        self.handleResult = handleResult
        self.process_map = {}
        self.thread_map = {}
        
    def setSessionState(self, session_name, state, stateTime):
        if session_name in self:
            self['session_name'].setSessionState(state, stateTime)
        else:
            pass
        
    def getDisInterval(self, session_name, dev_name, conf_name):
        if session_name in self:
            return self[session_name].getDisInterval(dev_name, conf_name)
        else:
            pass
        
    def getDeviceData(self, session_name, dev_name):
        if session_name in self:
            return self[session_name].getDeviceData(dev_name)
        else:
            pass
    
    def getDataItem(self, session_name, dev_name, conf_name):
        if session_name in self:
            return self[session_name].getDataItem(dev_name, conf_name)
        else:
            pass
        
    def getData(self, session_name, dev_name, conf_name):
        if session_name in self:
            return self[session_name].getData(dev_name, conf_name)
        else:
            pass
        
    def setData(self, session_name, dev_name, conf_name, data):
        if session_name in self:
            self[session_name].setData(dev_name,conf_name,data)
        else:
            pass
            
    def getDataValue(self, session_name, dev_name, conf_name):
        if session_name in self:
            return self[session_name].getDataValue(dev_name, conf_name)
        else:
            pass
    
    def getRealValue(self, session_name, dev_name, conf_name):
        if session_name in self:
            return self[session_name].getRealValue(dev_name, conf_name)
        else:
            pass
            
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
            self.session_map[session_name].useflag = True
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
            sqlString = "select SessionState.session_name, SessionState.session_state,\
            SessionState.updatetime,DataSession.session_id from SessionState inner join \
            DataSession on SessionState.session_name = DataSession.session_name and \
            server_name = %s"
            sessions = sqlConnection.query(sqlString, self.server_name)
            for session in sessions:
                devSet = deviceSet(session['session_name'], db)
                devSet.initData()
                sess = data_session(self.server_name,
                                    session['session_name'],
                                    session['session_id'],
                                    devSet,
                                    self.handleTask)
                sess.setSessionState(session['session_state'], session['updatetime'])
                self.session_map[session['session_name']] = sess
            sqlConnection.close()
        else:
            pass