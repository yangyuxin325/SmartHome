#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月15日

@author: sanhe
'''
from protocols import packProtocolhandlers
from protocols import doRequest
from datetime import datetime

def RequestProtocolData(head,body,user):
    if head[2] in doRequest:
        doRequest[head[2]](head,body,user)
    else:
        pass

def doDataParam(data):
    print data
                

def doCyclePeriod(data):
    print data
#     import SmartServer
#     data = packProtocolhandlers['SessionPeriod'](data['session_name'],
#                                                  data['period'],
#                                                  str(datetime.now())[:19])
#     SmartServer.DSAURServer().SendUploadData(data)
    
def doSessionState(data):
    print data
#     import SmartServer
#     sess = SmartServer.DSAURServer().getDataSession(data['session_name'])
#     sess.alive = data['state']
#     data = packProtocolhandlers['SessionState'](data['session_name'],
#                                                 data['state'],
#                                                 str(data['time'])[:19],
#                                                 255)
#     SmartServer.DSAURServer().SendUploadData(data)