#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月15日

@author: sanhe
'''
from datetime import datetime

def doDataProcess(session):
    for dev in session.dev_set.values():
        dataitem = dev.get('DisCount')
        from handlers import doDataParam
        if dataitem is None or dataitem.getValue() == 0:
            for dataitem in dev.values():
                if dataitem:
                    flag = dataitem.getChangeFlag()
                    if flag:
                        paradata = {'ename' : dataitem.ename,
                                    'value' : dataitem.value,
                                    'error_flag' : dataitem.error_flag,
                                    'time' : dataitem.time,
                                    'dis_flag' : dev.state,
                                    'dis_time' : dev.stateTime,
                                    'change_flag' : flag
                                    }
                        session.putResultQueue(doDataParam,paradata)
                    else:
                        pass
                else:
                    pass
        else:
            flag = dataitem.getChangeFlag()
            if flag:
                dev.setDisConnect(True)
                for dataitem in dev.values():
                    if dataitem:
                        change_flag = 3
                        if dataitem.ename == 'DisCount':
                            change_flag = flag
                        else:
                            pass
                        paradata = {'ename' : dataitem.ename,
                                    'value' : dataitem.value,
                                    'error_flag' : dataitem.error_flag,
                                    'time' : dataitem.time,
                                    'dis_flag' : dev.state,
                                    'dis_time' : dev.stateTime,
                                    'change_flag' : change_flag
                                    }
                        session.putResultQueue(doDataParam,paradata)
                    else:
                        pass
            else:
                pass
    from handlers import doCyclePeriod
    session.putResultQueue(doCyclePeriod,
                           {'session_name' : session.session_name,
                            'period' : session.periods})
    
    
def doSessionState(session, state):
    from handlers import doSessionState
    session.putResultQueue(doSessionState,
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