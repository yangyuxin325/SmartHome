#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月15日

@author: sanhe
'''
from datetime import datetime
import math
__metaclass__ = type
class data_conf():
    def __init__(self, ename, cname, server_name, data_type, sess_name=None, dev_name=None, conf_name=None):
        self.data_ename = ename
        self.data_cname = cname
        self.server_name = server_name
        self.data_type = data_type
        self.session_name = sess_name
        self.device_name = dev_name
        self.conf_name = conf_name
        
class data_constraint():
    def __init__(self, min_variation, min_val, max_val, dis_interval):
        self.min_variation = min_variation
        self.min_val = min_val
        self.max_val = max_val
        self.dis_interval = dis_interval
        
    def __eq__(self,other):
        if self.min_variation != other.min_variation or \
            self.min_val != other.min_val or \
            self.max_val != other.max_val or \
            self.dis_interval != other.dis_interval:
            return False
        else:
            return True
        
    def __ne__(self,other):
        return not (self == other)
        
class basic_data():
    def __init__(self, value=None, error_flag=False, time=None, dis_flag=True, dis_time=None):
        self.value = value
        self.error_flag = error_flag
        self.time = time
        self.dis_flag = dis_flag
        self.dis_time = dis_time
        
    def __eq__(self,other):
        if self.value != other.value or \
            self.error_flag != other.error_flag or \
            self.dis_flag != other.dis_flag:
            return False
        else:
            return True
        
    def __ne__(self,other):
        return not (self == other)
        
class data_param():
    def __init__(self, data, constraint, write_value=None, write_time=None, minute=None):
        self.__data = data
        self.__ischanged = False
        self.__constraint = constraint
        self.write_value = write_value
        self.write_time = write_time
        self.write_Return = None
        self.__minute = minute
        if self.__minute is not None:
            self.__total = 0
            self.__count = 0
            self.__start_time = None
        self.__reason = None

    def setData(self, data):
        if self.__data != data:
            self.__ischanged = True
            self.__data = data
            if self.write_Return is False:
                if self.__data.value == self.write_value:
                    self.write_Return = True
                    
    def getData(self):
        return self.__data
        
    def setConstraint(self, constraint):
        if self.__constraint != constraint:
            self.__constraint = constraint
            return self.__constraint
        
    def getConstraint(self):
        return self.__constraint
    
    def isChanged(self):
        return self.__ischanged
    
    def setValue(self, value):
        flag = False
        if self.__minute is None:
            if self.__data.value is None and self.__data.value != value:
                self.__data.value = value
                if value < self.__constraint.min_val or value > self.__constraint.max_val:
                    self.__data.error_flag = True
                self.__data.time = datetime.now()
                self.__data.dis_flag = False
                self.__data.dis_time = datetime.now()
                flag = True
            else:
                if math.fabs(self.__data.value - value) > self.__constraint.min_variation:
                    self.__data.value = value
                    if value < self.__constraint.min_val or value > self.__constraint.max_val:
                        self.__data.error_flag = True
                    else:
                        self.__data.error_flag = False
                    flag = True
                if self.__data.dis_flag is True:
                    self.__data.dis_flag = False
                    self.__data.dis_time = datetime.now()
                    flag = True
        else:
            if value is not None:
                if self.__constraint.min_val <= value <= self.__constraint.max_val:
                    self.__total = self.__total + value
                    self.__count = self.__count + 1
                    if self.__start_time is None:
                        self.__start_time = datetime.now()
                    if (datetime.now() - self.__start_time).total_seconds() >= self.__minute * 60:
                        ave_value = self.__total / self.__count
                        self.__start_time = None
                        if self.__data.value is None:
                            self.__data.value = ave_value
                            self.__data.time = datetime.now()
                        elif (math.fabs(self.__data.value - ave_value) - self.__constraint.min_variation) > 0:
                            self.__data.value = ave_value
                            self.__data.time = datetime.now()
                            if self.__data.dis_flag is True:
                                self.__data.dis_flag = False
                                self.__data.dis_time = datetime.now()
                            flag = True
        self.__ischanged = flag    
                            
    def getValue(self):
        if self.__data.error_flag is False and self.__data.dis_flag is False:
            return self.__data.value
        elif self.__data.error_flag is False and self.__data.dis_flag is True:
            if (datetime.now() - self.__data.dis_time).total_seconds() > self.__constraint.interval * 60:
                return self.__data.value
            
    def getRealValue(self):
        return self.__data.value
    
    def setWriteValue(self, value):
        readvalue = self.getValue()
        if readvalue is not None:
            if readvalue != value:
                self.write_value = value
                self.write_time = datetime.now()
                self.write_Return = False
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
        
    