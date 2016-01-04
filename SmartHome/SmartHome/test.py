#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月15日

@author: sanhe
'''
from deviceSet import deviceSet
from deviceSet import DB_conf
from data_session import data_session
import serialsearch
from datetime import datetime
from mydevice import infrared
import basedata
import os

v=('172.16.1.%d' % (x) for x in range(1,254))
for it in v:
    ret=os.system('ping -c 1 -W 1 %s' % it)
    if ret:
        print 'ping %s fail' % it
    else:
        print 'ping %s ok' % it