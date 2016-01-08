#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月24日

@author: sanhe
'''
import torndb

Session_SerailMap = {}

def getSerialCOM():
    import commands;
    comArr = {}
    status, str1 = commands.getstatusoutput('ls /dev/serial/by-path')
    if status == 0:
        arr = str1.splitlines()
        for strtemp in arr:
            cmd = "ls -la /dev/serial/by-path | grep " + strtemp + " | cut -d '/' -f3"
            comArr[strtemp] = commands.getoutput(cmd)
        return comArr

def InitSerialNo(db):
    dit = getSerialCOM()
    print dit
    mdit = sorted(dit.items(), key=lambda dit:dit[0])
    sqlConnection = torndb.Connection(db.addr, db.name, user=db.user, password=db.password)
    first_index = None
    second_index = None
    if len(mdit) == 12:
        i = 0
        strtemp = mdit[1][0]
        for c in strtemp:
            if c != mdit[0][0][i]:
                second_index = i
                exe = "update SerialSearch set value = %d where index_name = 'second_index'" % second_index
                sqlConnection.execute(exe)
            i = i+1
        i = 0
        strtemp = mdit[4][0]
        for c in strtemp:
            if c != mdit[0][0][i]:
                first_index = i
                exe = "update SerialSearch set value = %d where index_name = 'first_index'" % first_index
                sqlConnection.execute(exe)
            i = i+1
        i = 1
        for item in mdit:
            Session_SerailMap[i] = item[1]
            i = i+1
    elif 0 < len(mdit) < 12:
        sqlString = "select * from SerialSearch where inex_name = 'first_index'"
        res = sqlConnection.query(sqlString)
        first = res[0]['value']
        sqlString = "select * from SerialSearch where inex_name = 'second_index'"
        res = sqlConnection.query(sqlString)
        second = res[0]['value']
        for item in mdit:
            Session_SerailMap[(item[0][second] - 2) * 4 + first] = item[1]