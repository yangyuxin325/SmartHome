#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月21日

@author: sanhe
'''
import time
import multiprocessing
import threading
from greenlet import greenlet
from datetime import datetime
from com_handlers import doDataProcess
from com_handlers import doSessionState
from errcmd_deque import errcmd_deque
from collections import deque

def NotifyDisConnect(session,dev):
    dataitem = dev.get('DisCount')
    flag = dataitem.getChangeFlag()
    if flag:
        paradata = {'ename' : dataitem.ename,
                    'value' : dataitem.value,
                    'error_flag' : dataitem.error_flag,
                    'time' : dataitem.time,
                    'dis_flag' : dev.state,
                    'dis_time' : dev.stateTime,
                    'change_flag' : 1
                    }
        from handlers import doDataParam
        session.putResultQueue(doDataParam,paradata)
    else:
        pass

def Sum_Right(array):
    check_sum = 0
    for i in range(len(array) -1):
        check_sum += ord(array[i])
        check_sum &= 0xff
    if check_sum == ord(array[i+1]):
        return True
    else:
        return False

class data_session():
    def __init__(self, server_name, session_name, session_id, dev_set, handleTask=None):
        self.server_name = server_name
        self.session_name = session_name
        self.session_id = session_id
        self.baudrate = 9600
        self.interval = 0.5
        self.dev_set = dev_set
        self.resultQueue = multiprocessing.Queue()
        self.taskQueue = multiprocessing.Queue()
        self.rLock = multiprocessing.Lock()
        self.tLock = multiprocessing.Lock()
        self.handleTask = handleTask
        self.alive = False
        self.state = False
        self.stateTime = None
        self.com = None
        self.periods = None
        self.ctrlCmdDeque = deque()
        
#         self.errcmd = None
#         self.errStartTime = time.time()
#         self.cycleCmdDeque= self.dev_set.getCmdSet()
#         self.cycleCmdDeque.append({"id" : 0, "cmd" : "", "dev_id" : -1})
#         self.errCmdDeque = errcmd_deque()
        
    def getSessionState(self):
        return {'state' : self.state, 'stateTime' : self.stateTime}
        
    def setSessionState(self, state, stateTime):
        self.state = state
        self.stateTime = stateTime
        
    def getDisInterval(self, dev_name, conf_name):
        return self.dev_set.getDisInterval()
    
    def getDeviceData(self, dev_name):
        return self.dev_set.get(dev_name)
        
    def getDataItem(self, dev_name, conf_name):
        return self.dev_set.getDataItem(dev_name, conf_name)
        
    def getDataValue(self, dev_name, conf_name):
        value = self.dev_set.getDataValue()
        if value:
            if self.state:
                return value
            else:
                interval = self.getDisInterval(dev_name, conf_name)
                if (datetime.now() - self.stateTime).total_seconds() > interval * 60:
                    return value
                else:
                    pass
        else:
            pass
    
    def getRealValue(self, dev_name, conf_name):
        return self.dev_set.getRealValue()
    
    def setData(self, dev_name, conf_name, data):
        self.dev_set.setData(dev_name, conf_name, data)
        
    def getReason(self, dev_name, conf_name):
        return self.dev_set.getReason(dev_name, conf_name)
    
    def setReason(self, dev_name, conf_name, reason):
        self.dev_set.setReason(dev_name, conf_name, reason)
        
    def putResultQueue(self, handle, data):
        self.rLock.acquire()
        self.resultQueue.put_nowait({'handle' : handle, 'data' : data})
        self.rLock.release()
        
    def getResultQueue(self):
        res = None
        self.rLock.acquire()
        if not self.resultQueue.empty():
            res = self.resultQueue.get_nowait()
        else:
            pass
        self.rLock.release()
        if res:
            return res
        else:
            pass
        
    def putTaskQueue(self, data):
        self.tLock.acquire()
        self.taskQueue.put_nowait(data)
        self.tLock.release()
        
    def getTaskQueue(self):
        res = None
        self.tLock.acquire()
        if not self.taskQueue.empty():
            res = self.taskQueue.get_nowait()
        else:
            pass
        self.tLock.release()
        if res:
            return res
        else:
            pass
        
    def openSerial(self):
        try:
            import serial
            from serialsearch import Session_SerailMap
            if self.session_id in Session_SerailMap:
                self.port = "/dev/" + Session_SerailMap[self.session_id]
                self.com = serial.Serial(self.port,self.baudrate)
            else:
                print "Do not find data_session %s" % self.session_name
        except:
            print 'Open %s , %s Serial fail' % (self.session_name, self.port)
            
    def isOpen(self):
        if self.com :
            return self.com.isOpen()
        
    def __call__(self):
        self.start()
            
    def start(self):
        self.errcmd = None
        self.errStartTime = time.time()
        self.cycleCmdDeque= self.dev_set.getCmdSet()
        self.cycleCmdDeque.append({"id" : 0, "cmd" : "", "dev_id" : -1})
        self.errCmdDeque = errcmd_deque()
        if not self.isOpen() :
            self.openSerial()
        else:
            pass
        if self.isOpen() :
            self.alive = True
            doSessionState(self,self.alive)
            th = threading.Thread(target=self.__doTask)
            th.start()
            self.sendGR = greenlet(self.__sendData)
            self.recvGR = greenlet(self.__receiveData)
            self.sendGR.switch()
        else:
            self.dis_time = datetime.now()
            
    def __doTask(self):
        while self.alive:
            if self.taskQueue.empty() is False :
                print "Task Num : " , self.taskQueue.qsize()
                data = self.taskQueue.get_nowait()
                if self.handleTask is not None :
                    self.handleTask(self, data)
                else:
                    pass
            else:
                pass
            time.sleep(0.01)

    def __sendData(self):
        self.__cmd = None
        self.__startTime = time.time()
        while self.alive :
            try:
                cmd = None
                data = None
                if len(self.ctrlCmdDeque) > 0:
                    data = self.ctrlCmdDeque.popleft()
                elif len(self.cycleCmdDeque) > 0 :
                    cmd = self.cycleCmdDeque.popleft()
                    data = cmd["cmd"]
                else:
                    print "there is not cmds in queue!"
                    time.sleep(1)
                    if  self.errCmdDeque.empty():
                        self.closeSerial()
                        self.start()
                        return
                self.__cmd = cmd
                if data:
                    self.com.write(data.decode('hex'))
                    self.__sendTime = time.time()
                    self.recvGR.switch()
                else :
                    self.__NoSendData(cmd)
            except Exception as e:
                print '_sendData got an error : %s' % e, self.session_name, self.port  
                self.closeSerial()
                self.start()
                
    def closeSerial(self):
        if(type(self.com) != type(None)):
            self.alive = False
            doSessionState(self,self.alive)
            self.com.close()
        else:
            pass
                
    def __NoSendData(self, cmd):
        if cmd is not None and cmd["dev_id"] == -1 :
            self.periods = time.time() - self.__startTime
#             print "Cycle Period is", self.periods,"s."
            self.__startTime = time.time()
            doDataProcess(self)
            if len(self.cycleCmdDeque) == 0  or  time.time() - self.errStartTime > 60:
                if self.errCmdDeque.empty():
                    cmddata = self.errCmdDeque.popcmd()
                    self.errcmd  = cmddata
                    self.cycleCmdDeque.append(cmddata)
                    self.errStartTime = time.time()
                else:
                    pass
            else:
                pass
            self.cycleCmdDeque.append(self.__cmd)
            if len(self.cycleCmdDeque) == 1:
                time.sleep(10)
            else:
                pass
        else:
            pass
                    
    def __receiveData(self):
        self._read_interval = 0.01
        total =int(self.interval/self._read_interval)
        while self.alive :
            try:
                flag = True
                data = ""
                count = 0
                while flag:
                    time.sleep(self._read_interval)
                    count = count + 1
                    n = self.com.inWaiting()
                    flag1 = False
                    if n > 0:
                        if flag1 is True:
                            flag1 = False
                        else:
                            flag1 = True
                        subdata = self.com.read(n)
                        data = data + subdata
                        if flag1 is True:
                            continue
                    else:
                        flag1 = False
                    if (data is not "" and n == 0) or count == total:
                        flag = False
                        if count == total:
                            self.__DisConnectProcess()
                        else:
                            self.__dataProcess(data)
                    else:
                        pass
                self.sendGR.switch()
            except Exception as e:
                print '_receiveData got an error : %s' % e, self.session_name, self.port  
                self.closeSerial()
                self.start()
                
    def __dataProcess(self,data):
        strdata = data.encode("hex")
        listdata = []
        for i in range(0,len(strdata),2):
            listdata.append(int(strdata[i:i+2],16))
        dev_id = 0
        from mydevice import crc16
        if (ord(data[0]) == 0x99 and Sum_Right(data)) or crc16().calcrc(listdata):
            if (ord(data[0]) == 0x99) :
                dev_id = ord(data[1])
            else:
                dev_id = ord(data[0])
            self.dev_set.ParseData(dev_id,listdata)
            if self.__cmd is not None and self.__cmd['dev_id'] == dev_id :
                self.cycleCmdDeque.append(self.__cmd)
                if self.__cmd == self.errcmd:
                    self.errcmd = None
                    cmd_deque = deque()
                    cmd_deque = self.errCmdDeque.popcmdset(dev_id)
                    m_cmd =  self.errCmdDeque.popcmd()
                    if m_cmd is not None:
                        self.errcmd = m_cmd
                        cmd_deque.append(m_cmd)
                    self.cycleCmdDeque = self.cycleCmdDeque + cmd_deque
                    
                if self.dev_set.getConnectState(dev_id) :
                    self.dev_set.setDisConnect(dev_id,False)
                else:
                    pass
            else:
                pass
        else:
            self.__DisConnectProcess()
    
    def __DisConnectProcess(self):
        if self.__cmd is not None:
            flag = self.dev_set.setDisConnect(self.__cmd["dev_id"],True)
#             if self.dev_set.getConnectState(self.__cmd["dev_id"]) is False:
            if flag is False:
                self.errCmdDeque.push(self.__cmd)
                NotifyDisConnect(self,self.dev_set.get(self.__cmd["dev_id"]))
            else :
                self.cycleCmdDeque.append(self.__cmd)
                
    def __CmdThread(self, cmd, delay_second):
        time.sleep(delay_second)
        self.ctrlCmdDeque.append(cmd)
    
    def AddSendCmd(self, cmd, delay_second):
        if delay_second > 0 :
            th = threading.Thread(target= self.__CmdThread, args= (cmd, delay_second))
            th.start()
        else :
            self.ctrlCmdDeque.append(cmd)
