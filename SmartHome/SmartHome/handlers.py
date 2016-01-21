#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月15日

@author: sanhe
'''
import SmartServer
from protocols import packProtocolhandlers
from protocols import doRequest
from datetime import datetime

def RequestProtocolData(head,body,user):
    if head[2] in doRequest:
        doRequest[head[2]](head,body,user)
    else:
        pass

def doDataParam(dataparam):
    data = dataparam.getData()
    reason = dataparam.getReason()
    if dataparam.write_Return:
        if type(dataparam.getReason().getReasonValue()) is str:
            pass
        else:
            pass
    sdata =  packProtocolhandlers['DataInfo'](data,reason,255)
    SmartServer.DSAURServer.putDataToCache(data.ename, sdata)

def doCyclePeriod(data):
    data = packProtocolhandlers['SessionPeriod'](data['session_name'],
                                                 data['period'],
                                                 str(datetime.now())[:19])
    SmartServer.DSAURServer().SendUploadData(data)
    
def doSessionState(data):
    sess = SmartServer.DSAURServer().getDataSession(data['session_name'])
    sess.alive = data['state']
    data = packProtocolhandlers['SessionState'](data['session_name'],
                                                data['state'],
                                                str(data['time'])[:19],
                                                255)
    SmartServer.DSAURServer().SendUploadData(data)