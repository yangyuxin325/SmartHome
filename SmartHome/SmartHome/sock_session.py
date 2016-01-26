#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月26日

@author: sanhe
'''
import asyncore
import socket
import torndb
import threading
import struct
import time
import SmartServer

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
            self.sqlConsession_mapnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(self.addr)
        self.handleData = handleData
        self.timer = threading.Timer(3,self.handle_timer)
        
    def handle_timer(self):
        if self.connected:
            print self.addr, self.connected
            self.send(struct.pack('!4i', 0, 0, 0, 0))
            self.timer = threading.Timer(3,self.handle_timer)
            self.timer.start()
        else:
            pass
        
        
    def handle_read(self):
        asyncore.dispatcher_with_send.handle_read(self)
        self.timer.cancel()
        if self.connected:
            if self.handleData:
                self.handleData(self)
            else:
                buf = self.recv(100)
                print buf.strip()
        else:
            pass
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        
    def handle_connect(self):
        asyncore.dispatcher_with_send.handle_connect(self)
        if self.connected:
            SmartServer.doConnect(self)
            self.timer = threading.Timer(3,self.handle_timer)
            self.timer.start()
        else:
            pass
        
    def handle_close(self):
        asyncore.dispatcher_with_send.handle_close(self)
        try:
            SmartServer.doClose(self)
            time.sleep(1)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(self.addr)
        except Exception as e:
            self.connecting = False
            print e
        
    def sendData(self,data):
        self.timer.cancel()
        if self.connected:
            self.send(data)
        else:
            pass

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
        if self.connected:
            if self.handleData:
                self.handleData(self)
            else:
                buf = self.recv(100)
                print buf.strip()
        else:
            pass
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        
    def handle_timer(self):
        if self.connected:
            self.send(struct.pack('!4i', 0, 0, 0, 0))
        else:
            pass
        self.timer = threading.Timer(3,self.handle_timer)
        self.timer.start()
        
    def sendData(self,data):
        self.timer.cancel()
        if self.connected:
            self.send(data)
        else:
            pass
        
    def handle_close(self):
        asyncore.dispatcher_with_send.handle_close(self)
        if self.sqlConnection:
            self.sqlConnection.close()
            self.sqlConnection = None
            SmartServer.doClose(self)
        
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