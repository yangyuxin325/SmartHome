#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月21日

@author: sanhe
'''
import time
import multiprocessing

class data_session():
    def __init__(self, session_name, session_id, dev_set, handleTask=None):
        self.session_name = session_name
        self.session_id = session_id
        self.baudrate = 9600
        self.interval = 0.5
        self.dev_set = dev_set
        self.cycleCmdList = self.dev_set.getCmdSet()
        self.cycleCmdList.append({"id" : 0, "cmd" : "", "dev_id" : -1})
        self.ctrlCmdList = {}
        self.errCmdList = {}
        self.errStartTime = time.time()
        self.resultQueue = multiprocessing.Queue()
        self.taskQueue = multiprocessing.Queue()
        self.rLock = multiprocessing.Lock()
        self.tLock = multiprocessing.Lock()
        self.handleTask = handleTask
        self.alive = False
        self.com = None
        
    def putResultQueue(self, handle, data):
        self.rLock.acquire()
        self.resultQueue.put_nowait({'handle' : handle, 'data' : data})
        self.rLock.release()
        
    def getResultQueue(self):
        res = None
        self.rLock.acquire()
        if not self.resultQueue.empty():
            res = self.resultQueue.get_nowait()
        self.rLock.release()
        if res:
            return res
        
    def putTaskQueue(self, data):
        self.tLock.acquire()
        self.taskQueue.put_nowait(data)
        self.tLock.release()
        
    def getTaskQueue(self):
        res = None
        self.tLock.acquire()
        if not self.taskQueue.empty():
            res = self.taskQueue.get_nowait()
        self.tLock.release()
        if res:
            return res
        
    def openSerial(self):
        try:
            import serial
            self._com = serial.Serial(self._port,self._baudrate)
        except:
            print 'Open %s , %s Serial fail' % (self._name, self._port)   