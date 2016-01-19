#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月18日

@author: sanhe
'''
import json
import struct

packProtocolhandlers = {}
unpackProtocolhanlers = {}

local_name = u'西山游泳馆'

def packSessionPeriod(session_name, period, strtime):
    try:
        head = range(4)
        head[0] = 1
        head[1] = 0
        head[2] = 19
        head[3] = 0
        body = {}
        body['session_name'] = session_name
        body['period'] = period
        body['time'] = strtime
        body['local_name'] = local_name
        body['status_code'] = 255
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        return data
    except Exception as e:
        print 'packSessionPeriod got Error : ', e

def packSessionState(session_name, state, strtime, code):
    try:
        head = range(4)
        head[0] = 1
        head[1] = 0
        head[2] = 9
        head[3] = 0
        body = {}
        body['session_name'] = session_name
        body['session_state'] = state
        body['time'] = strtime
        body['local_name'] = local_name
        body['status_code'] = code
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        return data
    except Exception as e:
        print 'packSessionState got Error : ', e

packProtocolhandlers['SessionState'] = packSessionState
packProtocolhandlers['SessionPeriod'] = packSessionPeriod