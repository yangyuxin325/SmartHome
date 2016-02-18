#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月18日

@author: sanhe
'''
import SmartServer
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import socket
import fcntl
import struct
from serialsearch import InitSerialNo

def get_ip_address( ifname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return socket.inet_ntoa(fcntl.ioctl(
                                        sock.fileno(),
                                        0x8915,  # SIOCGIFADDR
                                        struct.pack('256s', ifname[:15])
                                        )[20:24])
import asyncore
if __name__ == "__main__" :
    try:
        SmartServer.DSAURServer().Init(get_ip_address('eth0'), 8899)
        InitSerialNo(SmartServer.DSAURServer().db)
        SmartServer.DSAURServer().startService(SmartServer.handleConnect)
    except Exception as e:
        print e
        
        
        
