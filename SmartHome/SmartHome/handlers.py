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
    ename = data['ename']
    from SmartServer import DSAURServer
    data_conf = DSAURServer().getDataConf(ename)
    prior = data_conf.get('prior')
    rs_data = DSAURServer().getReason(ename)
    rs_data = None
    DSAURServer().putDataToCache(ename, {'data' : data, 'reason' : rs_data})
    data = packProtocolhandlers['DataInfo'](data,prior,rs_data,255)
    DSAURServer().SendUploadData(data)

def doCyclePeriod(data):
    print data
    from SmartServer import DSAURServer
    data = packProtocolhandlers['SessionPeriod'](data['session_name'],
                                                 data['period'],
                                                 str(datetime.now())[:19])
    DSAURServer().SendUploadData(data)
    
def doSessionState(data):
    print data
    from SmartServer import DSAURServer
    sess = DSAURServer().getDataSession(data['session_name'])
    sess.alive = data['state']
    data = packProtocolhandlers['SessionState'](data['session_name'],
                                                data['state'],
                                                str(data['time'])[:19],
                                                255)
    DSAURServer().SendUploadData(data)