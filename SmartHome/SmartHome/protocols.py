#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月18日

@author: sanhe
'''
import json
import struct
import SmartServer
from mydevice import device_Dict,sesstype_Dict

packProtocolhandlers = {}

doRequest = {}

local_name = u'西山游泳馆'

def packDataInfo(data,reason,code):
    try:
        head = range(4)
        head[0] = 1
        head[1] = 0
        head[2] = 15
        head[3] = 0
        body = {}
        body['ename'] = data.ename
        body['value'] = data.value
        body['error_flag'] = data.error_flag
        body['time'] = str(data.time)[:19]
        body['dis_flag'] = data.dis_flag
        body['dis_time'] = str(data.dis_time)[:19]
#         if data.ename in SmartServer.data_server.dataPriors:
#             body['prior_flag'] = True
#             body['prior'] = SmartServer.data_server.dataPriors[data.ename]
#         else:
#             body['prior_flag'] = False
        if reason:
            body['reason_flag'] = True
            rs_body = {}
            rs_data = reason.getReasonValue()
            if type(rs_data) is type(data):
                rs_body['type'] = 3
                temp_body = {}
                temp_body['ename'] = rs_data.ename
                temp_body['value'] = rs_data.value
                temp_body['error_flag'] = rs_data.error_flag
                temp_body['time'] = str(rs_data.time)[:19]
                temp_body['dis_flag'] = rs_data.dis_flag
                temp_body['dis_time'] = str(rs_data.dis_time)[:19]
                rs_body['rs_data'] = temp_body
            else:
                if reason.RS_id:
                    rs_body['type'] = 1
                else:
                    rs_body['type'] = 2
                rs_body['rs_data'] = rs_data
        else:
            body['reason_flag'] = False
        body['local_name'] = local_name
        body['status_code'] = code
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        return data
    except Exception as e:
        print 'packDataInfo got Error : ', e

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
packProtocolhandlers['DataInfo'] = packDataInfo

def handleDeviceTypes(head,body,user):
    try:
        head = list(head)
        member = []
        if body['status_code'] == 1:
            for dev_type,description in device_Dict.items():
                item = {}
                item['dev_type'] = dev_type
                item['description'] = description
                member.append(item)
            body['status_code'] = 2
        else:
            pass
        body['member'] = member
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        user.sendData(data)
    except Exception as e:
        print 'handleDeviceTypes got Error : ', e
        
def handleSessionTypes(head,body,user):
    try:
        head = list(head)
        member = []
        if body['status_code'] == 1:
            for session_type,description in sesstype_Dict.items():
                item = {}
                item['session_type'] = session_type
                item['description'] = description
                member.append(item)
            body['status_code'] = 2
        else:
            pass
        body['member'] = member
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        user.sendData(data)
    except Exception as e:
        print 'handleSessionTypes got Error : ', e
        
def handleServerParam(head,body,user):
    try:
        head = list(head)
        member = []
        if body['status_code'] == 1:
            item = {}
            item['server_name'] = 'region'
            item['server_type'] = 'region'
            item['server_ip'] = SmartServer.DSAURServer.region_ip
            member.append(item)
            for s_ip in SmartServer.DSAURServer.unit_ipset:
                item = {}
                item['server_name'] = SmartServer.DSAURServer.ip_name_map[s_ip]
                item['server_type'] = 'unit'
                item['server_ip'] = s_ip
                member.append(item)
            for s_ip in SmartServer.DSAURServer.node_ipset:
                item = {}
                item['server_name'] = SmartServer.DSAURServer.ip_name_map[s_ip]
                item['server_type'] = 'unit'
                item['server_ip'] = s_ip
                member.append(item)
            body['status_code'] = 2
        else:
            pass
        body['member'] = member
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        user.sendData(data)
    except Exception as e:
        print 'handleServerParam got Error : ', e
        
def handleNodeUnitMap(head,body,user):
    try:
        head = list(head)
        member = []
        if body['status_code'] == 1:
            for node_name,unit_name in SmartServer.DSAURServer.node_unit_map.items():
                item = {}
                item['node_name'] = node_name
                item['unit_name'] = unit_name
                member.append(item)
            body['status_code'] = 2
        else:
            pass
        body['member'] = member
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        user.sendData(data)
    except Exception as e:
        print 'handleNodeUnitMap got Error : ', e
        
def handleSessions(head,body,user):
    try:
        head = list(head)
        member = []
        if body['status_code'] == 1:
            server_name = body['server_name']
            sesslist = SmartServer.DSAURServer().getDataSessions(server_name)
            for sess in sesslist:
                item = {}
                item['session_name'] = sess.session_name
                item['session_id'] = sess.session_id
                item['session_type'] = 1
                member.append(item)
            body['status_code'] = 2
        else:
            pass
        body['member'] = member
        encodedjson = json.dumps(body)
        head[3] = len(encodedjson)
        data = struct.pack('!4i{}s'.format(head[3]), head[0], head[1], head[2], head[3], encodedjson)
        user.sendData(data)
    except Exception as e:
        print 'handleSessions got Error : ', e

doRequest[1] = handleDeviceTypes
doRequest[2] = handleSessionTypes
doRequest[3] = handleServerParam
doRequest[4] = handleNodeUnitMap
doRequest[5] = handleSessions
