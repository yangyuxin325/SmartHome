#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月15日

@author: sanhe
'''
import handlers
from datetime import datetime


def doDataProcess(session):
    pass
#     for dev in session.dev_set.dev_dict.values():
#         for conf_name in dev.data_dict.keys():
#             dev.getData(conf_name)
#             if data_param.isChanged():
#                     session.putResultQueue(handlers.doDataParam,data_param)
#                 else:
#                     pass
#             else:
#                 pass
#     session.putResultQueue(handlers.doCyclePeriod,
#                            {'session_name' : session.session_name,
#                             'period' : session.periods})
    
    
def doSessionState(session, state):
    session.putResultQueue(handlers.doSessionState,
                           {'session_name' : session.session_name,
                            'state' : state,
                            'time' : datetime.now()})
    
    
def sessStartOrStop(datasession, data):
    print "sessStartOrStop: ", data
    if 1 == data['state'] :
        datasession.start()
    else:
        datasession.stop()
        
MsgDict = {
           1 : sessStartOrStop,
           }