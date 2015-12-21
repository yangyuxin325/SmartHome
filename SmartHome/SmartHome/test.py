#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月15日

@author: sanhe
'''
def getSerialCOM():
    import commands;
    comArr = {}
    status, str1 = commands.getstatusoutput('ls /dev/serial/by-path')
    if status == 0:
        arr = str1.splitlines()
        for strtemp in arr:
            cmd = "ls -la /dev/serial/by-path | grep " + strtemp + " | cut -d '/' -f3"
#             comArr[commands.getoutput(cmd)] = strtemp
            comArr[strtemp] = commands.getoutput(cmd)
        return comArr

dit = getSerialCOM()
mdit = sorted(dit.items(), key=lambda dit:dit[0])

port_map = {}
first_index = None
second_index = None

if len(mdit) == 12:
    i = 0
    strtemp = mdit[1][0]
    for c in strtemp:
        if c != mdit[0][0][i]:
            second_index = i
        i = i+1
    i = 0
    strtemp = mdit[4][0]
    for c in strtemp:
        if c != mdit[0][0][i]:
            first_index = i
        i = i+1
print first_index,second_index

if len(mdit) == 12:
    i = 1
    for item in mdit:
        print item
        port_map[i] = item[1]
        i = i+1
    print port_map
elif 0 < len(mdit) < 12:
    first = mdit[0]

>>>>>>> refs/remotes/origin/yang
