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

class Server_Param():
    def __init__(self, server_name, server_ip, server_type):
        self.server_name = server_name
        self.server_ip = server_ip
        self.server_type = server_type

class AsyncSession(asyncore.dispatcher_with_send):
    def __init__(self, host, port, handleData, server_para, db=None):
        asyncore.dispatcher_with_send.__init__(self)
        self.server_name = server_para.server_name
        self.server_type = server_para.server_type
        self.server_ip = server_para.server_ip
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
        
    def handle_close(self):
        asyncore.dispatcher_with_send.handle_close(self)
        self.close()
        try:
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
            
            
def handleData(client):
    buf = client.recv(100)
    print buf.strip()
    client.sendData("yang")

def handleConnect(pair):
    sock, addr = pair
    print addr
    AsyncClient(sock,handleData)
        
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
    def __init__(self, server_name, handleTask, handleResult):
        self.server_name = server_name
        self.session_map = {}
        self.handleTask = handleTask
        self.handleResult = handleResult
        self.process_map = {}
        self.thread_map = {}
        
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
        if self.db is not None:
            sqlConnection = torndb.Connection(self.db.addr, self.db.name, user=self.db.user, password=self.db.password)
            sqlString = "select session_name, session_id from DataSession Where server_name = %s"
            sessions = sqlConnection.query(sqlString, self.server_name)
            from deviceSet import deviceSet
            from data_session import data_session
            for session in sessions:
                devSet = deviceSet(session['session_name'], db)
                self.session_map[session['session_name']] = data_session(self.server_name,
                                                                         session['session_name'],
                                                                         session['session_id'],
                                                                         devSet,
                                                                         self.handleTask)
            sqlConnection.close()
        else:
            pass
    
class data_server(Server_Param):
    def __init__(self, server_name, server_ip, server_type, sockSession=None):
        Server_Param.__init__(self, server_name, server_ip, server_type)
        self.udevDataType = {}
        self.udevData = {}
        self.sess_Set = None
        self.sockSession = sockSession
    
    def intUdevData(self, db):
        if self.db is not None:
            sqlConnection = torndb.Connection(self.db.addr, self.db.name, user=self.db.user, password=self.db.password)
            
            sqlConnection.close()
        else:
            pass
            
    def init(self, handleTask, handleResult, db):
        if handleTask:
            self.sess_Set = sessionSet(self.server_para.server_name, handleTask, handleResult)
            self.sess_Set(db)
        else:
            pass
        self.intUdevData(db)
        
        
if __name__ == "__main__" :
    server = AsyncServer("172.16.1.16",8899,handleConnect)
    server.run()
    asyncore.loop()