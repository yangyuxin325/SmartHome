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
import threading

def func(m):
    print m

timer = threading.Timer(1,func,args=[1,])
timer.start()



def f1(**args):
    print args['a']
    
def f2(**args):
    print args['a'],args['b']
    
def f3(**args):
    print args[0],args[1]
    
funcs_dict = {
              'area' : f1,
              'unit' : f2,
              'node' : f3,
              }

args_dict = {'area' : {'a' : 10},
             'unit' : {'a' : 1,'b' : 2},
             'node' : {'c' : 3, 'd' : 4},
             }

funcs_dict['unit'](**args_dict['unit'])


# v=('172.16.1.%d' % (x) for x in range(1,254))
# for it in v:
#     ret=os.system('ping -c 1 -W 1 %s' % it)
#     if ret:
#         print 'ping %s fail' % it
#     else:
#         print 'ping %s ok' % it