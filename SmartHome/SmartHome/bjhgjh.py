#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月21日

@author: sanhe1
'''
# import torndb
# sqlConnection = torndb.Connection("127.0.0.1:3306", "smarthomeDB", user = "root", password = "123456")
# sqlString = 'select * from DataInfo where data_ename = %s'
# data = sqlConnection.query(sqlString,'DN_PDG_1_GZ')
# print data
from deviceSet import DB_conf
import serialsearch

serialsearch.InitSerialNo(DB_conf("127.0.0.1:3306","smarthomeDB",'root','123456'))
print serialsearch.Session_SerailMap
def test():
    pass