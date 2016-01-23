#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月21日

@author: sanhe
'''
from datetime import datetime
from UserDict import UserDict
import math
__metaclass__ = type
        
class basic_data():
    def __init__(self, ename, value=None, error_flag=False, time=None):
        self.ename = ename
        self.value = value
        self.error_flag = error_flag
        self.time = time
        
    def __eq__(self,other):
        if self.value != other.value or \
            self.error_flag != other.error_flag:
            return False
        else:
            return True
        
    def __ne__(self,other):
        return not (self == other)
    
    def __str__(self):
        return '{ename : %s, value : %s, error_flag : %s, time : %s}' \
            % (str(self.ename),str(self.value),str(self.error_flag),str(self.time))
        
class data_param(basic_data):
    def __init__(self, ename, constraint, value=None, error_flag=False, time=None, doWriteReturn = None, minute= None):
        basic_data.__init__(self, ename, value, error_flag, time)
        self.__changeFlag = 0
        self.__constraint = constraint
        if isinstance(constraint, UserDict):
            pass
        else:
            self.__constraint = UserDict()
        self.doWriteReturn = doWriteReturn
        self.write_value = None
        self.write_time = None
        self.__minute = minute
        if self.__minute is not None:
            self.__total = 0
            self.__count = 0
            self.__start_time = None
        self.__reason = None
    
    def __str__(self):
        return '{ename : %s, value : %s, error_flag : %s, time : %s}' \
            % (self.ename,str(self.value),str(self.error_flag),str(self.time))

    def setData(self, data):
        if isinstance(data, basic_data):
            self.value = data.value
            self.error_flag = data.error_flag
            self.time = data.time
            if self.value == self.write_value and self.doWriteReturn:
                self.doWriteReturn(self)
        else:
            pass
                    
    def getData(self):
        return self.__data
    
    def getInterval(self):
        return self.__constraint['interval']
        
    def setConstraint(self, constraint):
        if self.__constraint != constraint:
            self.__constraint = constraint
            return self.__constraint
        
    def getConstraint(self):
        return self.__constraint
    
    def getChangeFlag(self):
        return self.__changeFlag
    
    def setChangeFlag(self, flag):
        self.__changeFlag = flag
    
    def setValue(self, value):
        error_flag = self.error_flag
        if value:
            if self.__constraint['min_val'] and self.__constraint['max_val']:
                if value < self.__constraint['min_val'] or value > self.__constraint['max_val']:
                    error_flag = True
                else:
                    error_flag = False
        else:
            pass
        if not self.__minute:
            if error_flag != self.error_flag:
                self.value = value
                self.__changeFlag = 2
                self.time = datetime.now()
            elif not self.value or math.fabs(value - self.value) > self.__constraint['min_variation']:
                self.value = value
                self.__changeFlag = 1
                self.time = datetime.now()
            else:
                self.__changeFlag = 0
        else:
            if not error_flag:
                self.__total = self.__total + value
                self.__count = self.__count + 1
                if self.__start_time:
                    if (datetime.now() - self.__start_time).total_seconds() >= self.__minute * 60:
                        ave_value = self.__total / self.__count
                        self.__start_time = None
                        if not self.value or math.fabs(value - self.value) > self.__constraint['min_variation']:
                            self.value = ave_value
                            self.__changeFlag = 1
                            self.time = datetime.now()
                        else:
                            pass
                    else:
                        pass
                else:
                    self.__start_time = datetime.now()
            else:
                pass
                            
    def getValue(self):
        if not self.error_flag:
            return self.value
        else:
            pass
    
    def setWriteValue(self, value):
        readvalue = self.getValue()
        if readvalue is not None:
            if readvalue != value:
                self.write_value = value
                self.write_time = datetime.now()
                return self.write_value
            
    def setReason(self, reason):
        self.__reason = reason
        
    def getReason(self):
        return self.__reason
    
class ReasonData():
    RS_DICT = {}
    def __init__(self):
        self.RS_Data = None
        self.RS_id = None
        self.padMac = None
        
    def setData(self,data):
        self.RS_id = None
        self.padMac = None
        self.RS_Data = data
        
    def setID(self,rs_id):
        self.padMac = None
        self.RS_Data = None
        self.RS_id = rs_id
        
    def setPad(self,mac):
        self.RS_Data = None
        self.RS_id = None
        self.padMac = mac
        
    def getReasonValue(self):
        if self.RS_Data is not None:
            return self.RS_Data
        elif self.RS_id is not None:
            if self.RS_id in self.RS_DICT:
                return self.RS_DICT[self.RS_id]
        elif self.padMac is not None:
            return self.padMac
        
    
