#coding=utf-8
#!/usr/bin/env python
'''
Created on 2015年12月16日

@author: sanhe
'''
from datetime import datetime
from UserDict import UserDict
from basedata import data_param
from basedata import basic_data
__metaclass__ = type

device_Dict = {}
device_Dict['infrared'] = u'红外探测器'
device_Dict['co2'] = u'co2探测器'
device_Dict['stc_1'] = u'模块stc_1'
device_Dict['stc_201'] = u'模块stc_201'
device_Dict['plc'] = u'可编程控制器'
device_Dict['sansu'] = u'三速风机'
device_Dict['triplecng'] = u'三联供机组'
device_Dict['voc'] = u'voc探测器'
device_Dict['wenkong'] = u'温控器'
device_Dict['ZMA194E'] = u'三相电表'

sesstype_Dict = {}
sesstype_Dict[1] = u'usb转485'

class crc16:  
    auchCRCHi = [ 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, \
                  0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, \
                  0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, \
                  0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, \
                  0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, \
                  0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, \
                  0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, \
                  0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, \
                  0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, \
                  0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, \
                  0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, \
                  0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, \
                  0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, \
                  0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, \
                  0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, \
                  0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, \
                  0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, \
                  0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, \
                  0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, \
                  0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, \
                  0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, \
                  0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, \
                  0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, \
                  0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, \
                  0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, \
                  0x80, 0x41, 0x00, 0xC1, 0x81, 0x40]  
  
    auchCRCLo = [ 0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, \
                  0x07, 0xC7, 0x05, 0xC5, 0xC4, 0x04, 0xCC, 0x0C, 0x0D, 0xCD, \
                  0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09, \
                  0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, \
                  0x1E, 0xDE, 0xDF, 0x1F, 0xDD, 0x1D, 0x1C, 0xDC, 0x14, 0xD4, \
                  0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3, \
                  0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, \
                  0xF2, 0x32, 0x36, 0xF6, 0xF7, 0x37, 0xF5, 0x35, 0x34, 0xF4, \
                  0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A, \
                  0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, \
                  0xEB, 0x2B, 0x2A, 0xEA, 0xEE, 0x2E, 0x2F, 0xEF, 0x2D, 0xED, \
                  0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26, \
                  0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, \
                  0x61, 0xA1, 0x63, 0xA3, 0xA2, 0x62, 0x66, 0xA6, 0xA7, 0x67, \
                  0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F, \
                  0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, \
                  0x78, 0xB8, 0xB9, 0x79, 0xBB, 0x7B, 0x7A, 0xBA, 0xBE, 0x7E, \
                  0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5, \
                  0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, \
                  0x70, 0xB0, 0x50, 0x90, 0x91, 0x51, 0x93, 0x53, 0x52, 0x92, \
                  0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C, \
                  0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, \
                  0x99, 0x59, 0x58, 0x98, 0x88, 0x48, 0x49, 0x89, 0x4B, 0x8B, \
                  0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C, \
                  0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, \
                  0x43, 0x83, 0x41, 0x81, 0x80, 0x40]
    
    def __init__(self):  
        pass  
    def createcrc(self, array):  
        crchi = 0xff  
        crclo = 0xff  
        for i in range(0, len(array)):  
            crcIndex = crchi ^ array[i]  
            crchi = crclo ^ self.auchCRCHi[crcIndex]  
            crclo = self.auchCRCLo[crcIndex]  
        return (crchi << 8 | crclo)  
    def createarray(self, array):  
        crcvalue = self.createcrc(array)  
        array.append(crcvalue >> 8)  
        array.append(crcvalue & 0xff)  
        return array      
    def calcrc(self, array):  
        crchi = 0xff  
        crclo = 0xff  
        lenarray = len(array)  
        for i in range(0, lenarray - 2):  
            crcIndex = crchi ^ array[i]  
            crchi = crclo ^ self.auchCRCHi[crcIndex]  
            crclo = self.auchCRCLo[crcIndex]  
        if crchi == array[lenarray - 2] and crclo == array[lenarray - 1] :  
            return True  
        else:  
            return False

class device(UserDict):
    def __init__(self,doDisConnect):
        UserDict.__init__(self)
        self.data_linkpara = {}
        self.linkset = set()
        self.disCount = None
        self.state = None
        self.stateTime = None 
        self.doDisConnect = doDisConnect
        
    def addData(self, conf_name, data, link_conf=None):
        if isinstance(data, data_param):
            self[conf_name] = data
            if conf_name == 'DisCount':
                self.disCount = data.value
                if self.disCount > 0:
                    self.state = False
                else:
                    self.state = True
                self.stateTime = data.time
            else:
                pass
            if link_conf:
                self.linkset.add(link_conf)
                self.data_linkpara[conf_name] = link_conf
            else:
                pass
        else:
            pass
                
    @classmethod
    def genPratrolInstr(self, ID):
        pass
                
    def __setValue(self, conf_name ,value):
        if self.get(conf_name):
            self[conf_name].setValue(value)
        else:
            pass
            
            
    def setDataValue(self, conf_name ,value):
        if conf_name in self:
            self.__setValue(conf_name, value)
            if conf_name in self.linkset:
                for k,v in self.data_linkpara.items():
                    if v == conf_name:
                        self.__setValue(k,value)
                    else:
                        pass
            else:
                pass
        else:
            pass
    
    def getDataItem(self, conf_name):
        return self.get(conf_name)
        
    def getDisInterval(self, conf_name):
        param = self.get(conf_name)
        if param:
            return param.getDisInterval() if param.getDisInterval() else 0
        else:
            return 0
        
    def getValue(self, conf_name):
        param = self.getDataItem(conf_name)
        value = None
        dis_interval = 0
        if param:
            value = param.getValue()
            dis_interval = param.getInterval() if param.getInterval() else 0
        else:
            pass
        if self.state :
            return value
        else:
            if (datetime.now() - self.stateTime).total_seconds() < dis_interval * 60:
                return value
            else:
                pass
        
    
    def getRealValue(self, conf_name):
        if self.get(conf_name):
            return self.get(conf_name).value
        else:
            pass
    
    def setData(self, conf_name, data):
        if conf_name in self:
            self[conf_name].setData(data)
            if conf_name == 'DisCount':
                self.disCount = data.value
                state = None
                if self.disCount > 0:
                    state = False
                else:
                    state = True
                stateTime = data.time
                self.setConnectState(state, stateTime)
            else:
                pass
        else:
            pass
                        
    def setDisConnect(self, flag):
        state = self.state
        if flag is False and self.disCount != 0:
            self.disCount = 0
            self.setDataValue('DisCount',self.disCount)
            state = True
        elif flag is True:
            self.disCount = self.disCount + 1
            if int(self['DisCount'].value) == 0:
                self.setDataValue('DisCount',self.disCount)
                if self.get('DisCount').value > 0:
                    state = False
                else:
                    pass
            else:
                pass
        else:
            pass
        if state != self.state:
            self.state = state
            if state is False:
                self.doDisConnect(self)
            else:
                pass
        else:
            pass
                    
    def getConnectState(self):
        return self.state
    
    def setConnectState(self, state, stateTime):
        self.state = state
        self.stateTime = stateTime
        
    def setDisFlag(self, conf_name):
        if conf_name in self:
                self[conf_name].setChangeFlag(3)
        else:
            pass
        
    def getReason(self, conf_name):
        if conf_name in self:
            return self[conf_name].getReason()
        else:
            pass
        
    def setReason(self, conf_name, reason):
        if conf_name in self:
            self[conf_name].setReason(reason)
        else:
            pass
        
    def dataParse(self, data):
        pass
    
class infrared(device):
    
    SUPPORTED_INSTRUCTIONS = {
        "LED_AUTO"   : 0 ,
        "LED_ON"     : 1 ,
        "LED_OFF"    : 2 ,
        "LED_URGENT" : 3 ,
                         }
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'YWren' : None,
                    'LedState' : None,
                    'DoorState' : None,
                    'InfoTime' : None,
                    'Temperature' : None,
                    'Humidity' : None,
                    'Lux' : None,
                    'DisCount' : None,
                    }
        self.update(self.data_dict)
            
    @classmethod
    def checkSum(self, array):
        check_sum = 0
        for data in array:
            check_sum += data
            check_sum &= 0xff
        array.append(check_sum)
        return array
        
    @classmethod
    def genPratrolInstr(self, ID):
        data = [0x99, ID, 0x00, 0xff, 0xff]
        return [self.checkSum(data)]
        
    @classmethod
    def genControlInstr(self, ID, instr):
        if instr not in self.SUPPORTED_INSTRUCTIONS.keys():
            err = "There is not a {} in infrared's SUPPORTED_INSTRUCTIONS".format(instr)
            raise Exception(err)
        data = [0x99, ID, 0x01, 0x00, self.SUPPORTED_INSTRUCTIONS[instr]]
        return self.checkSum(data)
    
    def dataParse(self, data):
        try:
            YWren = (data[3] & 3)
            LedState = ((data[3] & 12) >> 2)
            DoorState = (data[3] & 16) >> 4
    #         device_state = (data[3] & 32) >> 5
            InfoTime = (data[4] * 15000 + data[5] * 70) // 1000
            Temperature = float(data[7]) + float(data[8]) / 100.0
            if 1 == data[6]:
                Temperature = -self.Temperature
            Humidity = float(data[9]) + float(data[10]) / 100.0
            Lux = data[14] * 256 + data[15]
            self.setDataValue('YWren', YWren)
            self.setDataValue('LedState', LedState)
            self.setDataValue('DoorState', DoorState)
            self.setDataValue('InfoTime', InfoTime)
            self.setDataValue('Temperature', Temperature)
            self.setDataValue('Humidity', Humidity)
            self.setDataValue('Lux', Lux)
        except Exception as e:
            print "infrared dataParse Error : ", e

class co2(device):
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'CO2' : None,
                    'DisCount' : None,
                    }
        self.update(self.data_dict)
        
    @classmethod
    def genPratrolInstr(self, ID):
        data = [ID,0x04,0x00,0x00,0x00,0x01]
        crc = crc16()
        return [crc.createarray(data)]
    
    def dataParse(self, data):
        try :
            CO2 = data[3]*256 + data[4]
            self.setDataValue('CO2', CO2)
        except Exception as e:
            print "co2 dataParse Error : ", e
            
device_Dict['stc_1'] = '模块stc_1'

class stc_1(device):
    
    SUPPORTED_INSTRUCTIONS = {
        'DO' : (1, 8),
        'DI' : (2, 8),
        'AO' : (3, 0),
        'AI' : (4, 8),
                }
    
    AI_CONVERT_DICT = {
                   1 : lambda x : (x - 4000) / 160.0,                 # /*温度：0——100*/
                   2 : lambda x : (x - 4000) / 160.0 - 50.0,          # /*温度：-50——50*/
                   3 : lambda x : (x - 4000) * 10.197 / 16000.0,      # /*压力：0——10.197*/
                   4 : lambda x : (x - 4000) * 8.0 / 1600.0 - 20.0,   # /*温度：-20——60*/
                   5 : lambda x : (x - 400) / 16.0,                   # /*温度：0——100*/
                   6 : lambda x : (x - 400) / 16.0 - 50.0,            # /*温度：-50——50*/
                   7 : lambda x : (x - 400) * 10.197 / 1600.0,        # /*压力：0——10.197*/
                   8 : lambda x : (x - 400) * 8.0 / 160.0 - 20.0,     # /*温度：-20——60*/
                   }
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'DisCount' : None,
                    }
        for key in self.SUPPORTED_INSTRUCTIONS.keys() :
            str_fisrt = key
            if self.SUPPORTED_INSTRUCTIONS[key][1] > 0 :
                for num in range(self.SUPPORTED_INSTRUCTIONS[key][1]):
                    str_name = str_fisrt + str(num+1)
                    self.data_dict.update({str_name : None})
        self.update(self.data_dict)
        self._Algorithm_dict = {}
        
        self._Parsedict = {
                           1 : self._D_IOParse,
                           2 : self._D_IOParse,
                           3 : self._AOparse,
                           4 : self._AIParse,
                           }
            
    
    def addAlgorithm(self, key, a_type):
        if a_type in self.AI_CONVERT_DICT.keys() : 
            self._Algorithm_dict.update({key : self.AI_CONVERT_DICT[a_type]})
        
    @classmethod
    def genPratrolInstr(self, ID):
        instr = []
        for key,val in self.SUPPORTED_INSTRUCTIONS.values():
            if val > 0 : 
                data = [ID,key,0x00,0x00,0x00,val]
                crc = crc16()
                instr.append(crc.createarray(data))
        import copy
        return copy.deepcopy(instr)
        
    @classmethod
    def genControlInstr(self, ID, instr, io_port ,val):
        if instr not in ('DO', 'AO'):
            err = "There is not a {} in mokuai's SUPPORTED_INSTRUCTIONS".format(instr)
            raise Exception(err)
        if io_port < 1 or io_port > self.SUPPORTED_INSTRUCTIONS[instr][1] : 
            err = "There is not a {} in mokuai's IO_PORT".format(instr)
            raise Exception(err)
        data = [ID,self.SUPPORTED_INSTRUCTIONS[instr][0],0x00,io_port,0x00,0x00]
        if instr == 'DO':
            if val == 1:
                data[4] = 0xff
        elif instr == 'AO':
            data[2] = (40001+io_port) >> 8
            data[3] = (40001+io_port) - data[2]*256
            data[4] = val >> 8
            data[5] = val & 0xff
        crc = crc16()
        return crc.createarray(data)
    
    def _D_IOParse(self, data):
        try:
            str_first = None
            if data[1] == 1:
                str_first = 'DO'
            elif data[1] == 2:
                str_first = 'DI'
            val = None
            for i in range(8*data[2]):
                if i < 8 :
                    val = (data[3] & (1 << i)) >> i
                else:
                    val = (data[4] & (1 << (i - 8))) >> (i - 8)
                str_name = str_first + str(i+1)
                self.setDataValue(str_name, val)
        except Exception as e:
            print e
            
    def _AOparse(self, data):
        try:
            val1 = data[3] << 8 + data[4]
            val2 = data[5] << 8 + data[6]
            self.setDataValue('AO1', val1)
            self.setDataValue('AO2', val2)
        except Exception as e:
            print e
        
    def _AIParse(self, data):
        try:
            str_first = 'AI'
            val = None
            for i in range(data[2]/2):
                val = (data[i*2+3] << 8) + data[i*2+4]
                str_name = str_first + str(i+1)
                if str_name in self._Algorithm_dict.keys():
                    val = self._Algorithm_dict[str_name](val)
                self.setDataValue(str_name, val)
        except Exception as e:
            print "_AIParse : ", e
        
    def dataParse(self, data):
        try :
            self._Parsedict[data[1]](data)
        except Exception as e:
            print "mokuai dataParse :", e
            
class stc_201(device):
    
    SUPPORTED_INSTRUCTIONS = {
        'DO' : (1, 3),
        'DI' : (2, 6),
        'AO' : (3, 15),
        'AI' : (4, 19),
                }
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'DisCount' : None,
                    }
        for key in self.SUPPORTED_INSTRUCTIONS.keys() :
            str_fisrt = key
            if self.SUPPORTED_INSTRUCTIONS[key][1] > 0 :
                for num in range(self.SUPPORTED_INSTRUCTIONS[key][1]):
                    str_name = str_fisrt + str(num+1)
                    self.data_dict.update({str_name : None})
        self.update(self.data_dict)
        self._Algorithm_dict = {}
        
        self._Parsedict = {
                           1 : self._D_IOParse,
                           2 : self._D_IOParse,
                           3 : self._AOparse,
                           4 : self._AIParse,
                           }
            
    
    def addAlgorithm(self, key, a_type):
        if a_type in self.AI_CONVERT_DICT.keys() : 
            self._Algorithm_dict.update({key : self.AI_CONVERT_DICT[a_type]})
        
    @classmethod
    def genPratrolInstr(self, ID):
        instr = []
        for key,val in self.SUPPORTED_INSTRUCTIONS.values():
            if val > 0 : 
                data = [ID,key,0x00,0x00,0x00,val]
                crc = crc16()
                instr.append(crc.createarray(data))
        import copy
        return copy.deepcopy(instr)
        
    @classmethod
    def genControlInstr(self, ID, instr, io_port ,val):
        if instr not in ('DO', 'AO'):
            err = "There is not a {} in mokuai's SUPPORTED_INSTRUCTIONS".format(instr)
            raise Exception(err)
        if io_port < 1 or io_port > self.SUPPORTED_INSTRUCTIONS[instr][1] : 
            err = "There is not a {} in mokuai's IO_PORT".format(instr)
            raise Exception(err)
        data = [ID,self.SUPPORTED_INSTRUCTIONS[instr][0],0x00,io_port,0x00,0x00]
        if instr == 'DO':
            if val == 1:
                data[4] = 0xff
        elif instr == 'AO':
            data[2] = (40001+io_port) >> 8
            data[3] = (40001+io_port) - data[2]*256
            data[4] = val >> 8
            data[5] = val & 0xff
        crc = crc16()
        return crc.createarray(data)
    
    def _D_IOParse(self, data):
        try:
            str_first = None
            if data[1] == 1:
                str_first = 'DO'
            elif data[1] == 2:
                str_first = 'DI'
            val = None
            port_nums =self.SUPPORTED_INSTRUCTIONS[str_first][1]
            for i in range(port_nums*data[2]):
                if i < port_nums :
                    val = (data[3] & (1 << i)) >> i
                else:
                    val = (data[4] & (1 << (i - port_nums))) >> (i - port_nums)
                str_name = str_first + str(i+1)
                self.setDataValue(str_name, val)
                print str_name,val
        except Exception as e:
            print e
            
    def _AOparse(self, data):
        try:
            str_first = 'AO'
            val = None
            for i in range(data[2]/2):
                val = (data[i*2+4] << 8) + data[i*2+3]
                str_name = str_first + str(i+1)
                self.setDataValue(str_name, val)
                print str_name, val
        except Exception as e:
            print e
        
    def _AIParse(self, data):
        try:
            str_first = 'AI'
            val = None
            for i in range(data[2]/2):
                val = (data[i*2+3] << 8) + data[i*2+4]
                str_name = str_first + str(i+1)
                if i < 3 :
                    val = val / 10.0
                elif 2 < i < 7  or i == 16:
                    val = val / 100.0
                elif i == 15 or i > 16 :
                    val = val / 1000.0
                self.setDataValue(str_name, val)
                print str_name, val
        except Exception as e:
            print "_AIParse : ", e
            
    def dataParse(self, data):
        try :
            self._Parsedict[data[1]](data)
        except Exception as e:
            print "mokuai dataParse :", e
            
class plc(device):
    
    SUPPORTED_INSTRUCTIONS = {
        'DO' : (1, 8),
        'DI' : (2, 12),
        'AO' : (3, 2),
        'AI' : (4, 8),
                }
    
    AI_CONVERT_DICT = {
                   1 : lambda x : (x - 4000) / 160.0,                 # /*温度：0——100*/
                   2 : lambda x : (x - 4000) / 160.0 - 50.0,          # /*温度：-50——50*/
                   3 : lambda x : (x - 4000) * 10.197 / 16000.0,      # /*压力：0——10.197*/
                   4 : lambda x : (x - 4000) * 8.0 / 1600.0 - 20.0,   # /*温度：-20——60*/
                   5 : lambda x : (x - 400) / 16.0,                   # /*温度：0——100*/
                   6 : lambda x : (x - 400) / 16.0 - 50.0,            # /*温度：-50——50*/
                   7 : lambda x : (x - 400) * 10.197 / 1600.0,        # /*压力：0——10.197*/
                   8 : lambda x : (x - 400) * 8.0 / 160.0 - 20.0,     # /*温度：-20——60*/
                   }
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'DisCount' : None,
                    }
        for key in self.SUPPORTED_INSTRUCTIONS.keys() :
            str_fisrt = key
            if self.SUPPORTED_INSTRUCTIONS[key][1] > 0 :
                for num in range(self.SUPPORTED_INSTRUCTIONS[key][1]):
                    str_name = str_fisrt + str(num+1)
                    self.data_dict.update({str_name : None})
        self.update(self.data_dict)
        self._Algorithm_dict = {}
        
        self._Parsedict = {
                           1 : self._D_IOParse,
                           2 : self._D_IOParse,
                           3 : self._AOparse,
                           4 : self._AIParse,
                           }
        
    def addAlgorithm(self, key, a_type):
        if a_type in self.AI_CONVERT_DICT.keys() : 
            self._Algorithm_dict.update({key : self.AI_CONVERT_DICT[a_type]})
        
    @classmethod
    def genPratrolInstr(self, ID):
        instr = []
        for key,val in self.SUPPORTED_INSTRUCTIONS.values():
            if val > 0 : 
                data = [ID,key,0x00,0x00,0x00,val]
                crc = crc16()
                instr.append(crc.createarray(data))
        import copy
        return copy.deepcopy(instr)
        
    @classmethod
    def genControlInstr(self, ID, instr, io_port ,val):
        if instr not in ('DO', 'AO'):
            err = "There is not a {} in plc's SUPPORTED_INSTRUCTIONS".format(instr)
            raise Exception(err)
        if io_port < 1 or io_port > self.SUPPORTED_INSTRUCTIONS[instr][1] : 
            err = "There is not a {} in plc's IO_PORT".format(instr)
            raise Exception(err)
        data = [ID,self.SUPPORTED_INSTRUCTIONS[instr][0],0x00,io_port,0x00,0x00]
        if instr == 'DO':
            if val == 1:
                data[4] = 0xff
        elif instr == 'AO':
            data[2] = (40001+io_port) >> 8
            data[3] = (40001+io_port) - data[2]*256
            data[4] = val >> 8
            data[5] = val & 0xff
        crc = crc16()
        return crc.createarray(data)
    
    def _D_IOParse(self, data):
        str_first = None
        if data[1] == 1:
            str_first = 'DO'
        elif data[1] == 2:
            str_first = 'DI'
        val = None
        for i in range(8*data[2]):
            if i < 8 :
                val = (data[3] & (1 << i)) >> i
            else:
                val = (data[4] & (1 << (i - 8))) >> (i - 8)
            str_name = str_first + str(i+1)
            self.setDataValue(str_name, val)
            
    def _AOparse(self, data):
        val1 = (data[3] << 8) + data[4]
        val2 = (data[5] << 8) + data[6]
        self.setDataValue('AO1', val1)
        self.setDataValue('AO2', val2)
        
    def _AIParse(self, data):
        str_first = 'AI'
        val = None
        for i in range(data[2]/2):
            val = (data[i*2+3] << 8) + data[i*2+4]
            str_name = str_first + str(i+1)
            if str_name in self._Algorithm_dict.keys():
                val = self._Algorithm_dict[str_name](val)
            self.setDataValue(str_name, val)
            
    def dataParse(self, data):
        try :
            self._Parsedict[data[1]](data)
        except Exception as e:
            print "plc dataParse :", e
            
class sansu(device):
    
    SUPPORTED_INSTRUCTIONS = {
        "Wind"   : 0x64 ,
        "Fa1"    : 0x65 ,
        "Fa2"    : 0x66 ,
                         }
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'Wind' : None,
                    'Fa1' : None,
                    'Fa2' : None,
                    'DisCount' : None,
                    }
        self.update(self.data_dict)
        
    @classmethod
    def genPratrolInstr(self, ID):
        data = [ID,0x03,0x00,0x64,0x00,0x03]
        crc = crc16()
        return [crc.createarray(data)]
        
    @classmethod
    def genControlInstr(self, ID, instr, val):
        if instr not in self.SUPPORTED_INSTRUCTIONS.keys():
            err = "There is not a {} in sansu's SUPPORTED_INSTRUCTIONS".format(instr)
            raise Exception(err)
        data = [ID, 0x06, 0x00, self.SUPPORTED_INSTRUCTIONS[instr], 0x00, val]
        crc = crc16()
        return crc.createarray(data)

    def dataParse(self, data):
        device.dataParse(self, data)
        try :
            Wind = data[3]*256 + data[4]
            Fa1 = data[5]*256 + data[6]
            Fa2 = data[7]*256 + data[8]
            self.setDataValue('Wind', Wind)
            self.setDataValue('Fa1', Fa1)
            self.setDataValue('Fa2', Fa2)
        except Exception as e:
            print "sansu dataParse Error : ", e
            
class triplecng(device):
    
    SUPPORTED_INSTRUCTIONS = {
        "OnOff"   :  (49001,0) ,
        "Mode"    :  (49002,0) ,
        "AC_Cool" :  (49003,1) ,
        "AC_Warm" :  (49004,1) ,
        "HotWater":  (49005,1) ,
        "AC_Diff" :  (44313,1) ,
        "WB_Diff" :  (44314,1) ,
                         }
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    '1_1' : None,
                    '2_1Error' : None,
                    '2_2Error' : None,
                    '2_3Error' : None,
                    '2_4Error' : None,
                    '2_5Error' : None,
                    '2_6Error' : None,
                    '2_7Error' : None,
                    '2_8Error' : None,
                    '2_9Error' : None,
                    '2_10Error' : None,
                    '2_11Error' : None,
                    '2_12Error' : None,
                    '2_13Error' : None,
                    '2_14Error' : None,
                    '2_15Error' : None,
                    '2_16Error' : None,
                    '2_17Error' : None,
                    '2_18Error' : None,
                    '2_19Error' : None,
                    '2_20Error' : None,
                    '2_21Error' : None,
                    '2_22Error' : None,
                    '2_23Error' : None,
                    '2_24Error' : None,
                    '2_25Error' : None,
                    '2_26Error' : None,
                    '2_27Error' : None,
                    '2_28Error' : None,
                    '2_29Error' : None,
                    '2_30Error' : None,
                    '2_31Error' : None,
                    '2_32Error' : None,
                    '4_1' : None,
                    '4_2' : None,
                    '4_3' : None,
                    '4_4' : None,
                    '5_1' : None,
                    '5_2' : None,
                    '5_3' : None,
                    '5_4' : None,
                    '5_5' : None,
                    '6_1' : None,
                    '6_2' : None,
                    '6_3' : None,
                    '6_4' : None,
                    '6_5' : None,
                    '7_1' : None,
                    '7_2' : None,
                    '7_3' : None,
                    '7_4' : None,
                    '7_5' : None,
                    '7_6' : None,
                    '15_1' : None,
                    '15_2' : None,
                    '15_3' : None,
                    '15_4' : None,
                    '15_5' : None,
                    '15_6' : None,
                    '15_7' : None,
                    '15_8' : None,
                    '15_9' : None,
                    '15_10' : None,
                    '15_11' : None,
                    '15_12' : None,
                    '15_13' : None,
                    '15_14' : None,
                    '15_15' : None,
                    '16_1' : None,
                    '16_2' : None,
                    '16_3' : None,
                    '16_4' : None,
                    '16_5' : None,
                    '16_6' : None,
                    '16_7' : None,
                    '16_8' : None,
                    '16_9' : None,
                    '16_10' : None,
                    '16_11' : None,
                    '16_12' : None,
                    '16_13' : None,
                    '16_14' : None,
                    '16_15' : None,
                    '16_16' : None,
                    '25_1' : None,
                    '25_2' : None,
                    '25_3' : None,
                    '25_4' : None,
                    '25_5' : None,
                    '25_6' : None,
                    '25_7' : None,
                    '25_8' : None,
                    '25_9' : None,
                    '25_10' : None,
                    '25_11' : None,
                    '25_12' : None,
                    '25_13' : None,
                    '25_14' : None,
                    '25_15' : None,
                    '25_16' : None,
                    '25_17' : None,
                    '25_18' : None,
                    '25_19' : None,
                    '25_20' : None,
                    '25_21' : None,
                    '25_22' : None,
                    '25_23' : None,
                    '25_24' : None,
                    '25_25' : None,
                    'DisCount' : None,
                    }
        self.update(self.data_dict)

    @classmethod
    def genPratrolInstr(self, ID):
        instr = []
        addrs = {
            5:44310,
            4:44320,
            7:44330,
            25:44340,
            1:44370,
            6:49001,
            16:28401,
            15:27901,
            2:28901,
            }
        for addr in addrs.items():
            addr1 = addr[1] >> 8;
            addr2 = addr[1] & 0xff
            data = [ID,0x03,addr1,addr2,0x00,addr[0]]
            if addr[0] == 15 or addr[0] == 16 or addr[0] == 2 :
                data[1] = 0x04
            crc = crc16()
            instr.append(crc.createarray(data))
        import copy
        return copy.deepcopy(instr)
        
        
    @classmethod
    def genControlInstr(self, ID, instr, val):
        if instr not in self.SUPPORTED_INSTRUCTIONS.keys():
            err = "There is not a {} in triplecng's SUPPORTED_INSTRUCTIONS".format(instr)
            raise Exception(err)
        Addr = self.SUPPORTED_INSTRUCTIONS[instr][0]
        valtype = self.SUPPORTED_INSTRUCTIONS[instr][1]
        val1 = None
        val2 = None
        if valtype != 1 : 
            val1 = val >> 8
            val2 = val - val1 * 256
        else : 
            val1 = (val * 10 + 65536) >> 8
            val2 = (val * 10 + 65536) & 0xff
        data = [ID, 0x10, Addr >> 8, Addr & 0xff, 0x00, 0x01, 0x02, val1, val2]
        crc = crc16()
        return [crc.createarray(data)]
    
    
    def dataParse(self, data):
        device.dataParse(self, data)
        try:
            data_type = data[2]//2
            str_type = str(data_type)
            str_name = str_type + '_'
            if data_type == 1 : 
                str_temp = str_name + str(1)
                self.setDataValue(str_temp, data[3] << 8 + data[4])
            elif data_type == 2 :
                for i in range(32) :
                    str_temp = str_name + str(i+1) + 'Error'
                    if i < 8:
                        self.setDataValue(str_temp,(data[3] & (1 << i)) >> i) 
                    elif i < 16:
                        self.setDataValue(str_temp,(data[4] & (1 << (i-8))) >> (i-8))
                    elif i < 24:
                        self.setDataValue(str_temp,(data[5] & (1 << (i-16))) >> (i-16))
                    else:
                        self.setDataValue(str_temp,(data[6] & (1 << (i-24))) >> (i-24))
            elif data_type == 4 :
                for i in range(4) :
                    str_temp = str_name + str(i+1)
                    if i ==  1 :
                        self.setDataValue(str_temp,(data[i*2+3] << 8) + data[i*2+4])
                    else :
                        if 0xff == data[i*2+3]:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4] - 65536)//10)
                        else:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4])//10)
            elif data_type == 5 :
                for i in range(5) :
                    str_temp = str_name + str(i+1)
                    self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4])//10)
            elif data_type == 6 :
                for i in range(5) :
                    str_temp = str_name + str(i+1)
                    if i ==  0 or i == 1 :
                        self.setDataValue(str_temp,(data[i*2+3] << 8) + data[i*2+4])
                    else :
                        if 0xff == data[i*2+3]:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4] - 65536)//10)
                        else:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4])//10)
            elif data_type == 7 :
                for i in range(6) :
                    str_temp = str_name + str(i+1)
                    if i ==  0 or i == 2 or i == 4 :
                        self.setDataValue(str_temp,(data[i*2+3] << 8) + data[i*2+4])
                    else :
                        if 0xff == data[i*2+3]:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4] - 65536)//10)
                        else:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4])//10)
            elif data_type == 15 : 
                for i in range(15) :
                    str_temp = str_name + str(i+1)
                    self.setDataValue(str_temp,(data[i*2+3] << 8) + data[i*2+4])
            elif data_type == 16 : 
                for i in range(16) :
                    str_temp = str_name + str(i+1)
                    self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4])//10)
            elif data_type == 25 : 
                for i in range(25) :
#                     print "line",i,": ",data[i*2+3]<<8,data[i*2+4]
                    str_temp = str_name + str(i+1)
                    if 5<= i <= 6 or 9 == i or 13 == i or 17 == i or 24 == i:
                        if 0xff == data[i*2+3]:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4] - 65536)//10)
                        else:
                            self.setDataValue(str_temp,((data[i*2+3] << 8) + data[i*2+4])//10)
                    else:
                        self.setDataValue(str_temp,(data[i*2+3] << 8) + data[i*2+4])
        except Exception as e:
            print "triplecng dataParse Error : ", e
            

class voc(device):
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'VOC' : None,
                    'Temperature' : None,
                    'Humidity' : None,
                    'DisCount' : None,
                    }
        self.update(self.data_dict)
        
    @classmethod
    def genPratrolInstr(self, ID):
        data = [ID,0x04,0x00,0x00,0x00,0x06]
        crc = crc16()
        return [crc.createarray(data)]
    
    def dataParse(self, data):
        try:
            VOC = (data[3]*256 + data[4])/10.0
            Temperature = (data[5]*256 + data[6])/10.0
            Humidity = data[7]*256+data[8]
            self.setDataValue('VOC', VOC)
            self.setDataValue('Temperature', Temperature)
            self.setDataValue('Humidity', Humidity)
        except Exception as e:
            print "co2 dataParse Error : ", e

class wenkong(device):
    
    SUPPORTED_INSTRUCTIONS = {
        "OnOff"   : 2 ,
        "Mode"    : 3 ,
        "SetTemp" : 4 ,
        "Wind"    : 5 ,
                         }
    
    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                    'OnOff' : None,
                    'Mode' : None,
                    'SetTemp' : None,
                    'Wind' : None,
                    'Temperature' : None,
                    'DisCount' : None,
                    'Control_Mode' : None,
                    'Program_OnOff' : None,
                    }
        self.update(self.data_dict)
        
    @classmethod
    def genPratrolInstr(self, ID):
        data = [ID,0x03,0x00,0x02,0x00,0x08]
        crc = crc16()
        return [crc.createarray(data)]
        
    @classmethod
    def genControlInstr(self, ID, instr, val):
        if instr not in self.SUPPORTED_INSTRUCTIONS.keys():
            err = "There is not a {} in wenkong's SUPPORTED_INSTRUCTIONS".format(instr)
            raise Exception(err)
        data = [ID, 0x06, 0x00, self.SUPPORTED_INSTRUCTIONS[instr], 0x00, val]
        crc = crc16()
        return crc.createarray(data)
    
    def dataParse(self, data):
        try :
            OnOff = data[4]
            Mode = data[5] * 256 + data[6]
            SetTemp = data[7] + data[8]/10.0
            Wind = data[9]*256 + data[10]
            Temp = data[17] + data[18]/10.0
            self.setDataValue('OnOff', OnOff)
            self.setDataValue('Mode', Mode)
            self.setDataValue('SetTemp', SetTemp)
            self.setDataValue('Wind', Wind)
            self.setDataValue('Temperature', Temp)
            p_onff = self.getValue('Program_OnOff')
            c_mode = self.getValue('Control_Mode')
            if p_onff is not None and c_mode is not None:
                if (p_onff & 1) == OnOff :
                    self.setControlData('Control_Mode', 1)
                else:
                    self.setControlData('Control_Mode', 0)
        except Exception as e:
            print "wenkong dataParse Error : ", e
        
    def setControlData(self, dataname, value):
        if dataname not in ['Control_Mode','Program_OnOff']:
            err = "There is not a {} in wenkong's ControlData".format(dataname)
            raise Exception(err)
        self.setDataValue(self, dataname, value)
        
device_Dict['ZMA194E'] = '三相电表'

class ZMA194E(device):

    def __init__(self,doDisConnect):
        device.__init__(self,doDisConnect)
        self.data_dict = {
                          'DO1' : None,
                          'DO2' : None,
                          'DO3' : None,
                          'DO4' : None,
                          'DI1' : None,
                          'DI2' : None,
                          'DI3' : None,
                          'DI4' : None,
                          'RMSUA' : None,
                          'RMSUB' : None,
                          'RMSUC' : None,
                          'Udiff'  : None,
                          'RMSIA' : None,
                          'RMSIB' : None,
                          'RMSIC' : None,
                          'Idiff'  : None,
                          'Psum'  : None,
                          'Pfsum' : None,
                          'FreqA' : None,
                          'WH-1'  : None,
                          'DisCount' : None,
                    }
        self.update(self.data_dict)
        
    @classmethod
    def genPratrolInstr(self, ID):
        arr = []
        crc = crc16()
        data = [ID,0x03,0x00,0x14,0x00,0x03]
        arr.append(crc.createarray(data))
        data = [ID,0x03,0x00,0x17,0x00,0x1A]
        arr.append(crc.createarray(data))
        data = [ID,0x03,0x00,0x3F,0x00,0x12]
        arr.append(crc.createarray(data))
        data = [ID,0x03,0x00,0x57,0x00,0x02]
        arr.append(crc.createarray(data))
#         data = [ID,0x06,0x00,0x16,0x00,0x02]
#         arr.append(crc.createarray(data))
        return arr
    
    def dataParse(self, data):
        import struct
        try :
            data_type = data[2]//2
            if data_type == 3:
                self.setDataValue('DI4', (data[6] & 0x08) >> 3)
                self.setDataValue('DI3', (data[6] & 0x04) >> 2)
                self.setDataValue('DI2', (data[6] & 0x02) >> 1)
                self.setDataValue('DI1', data[6] & 0x01)
                self.setDataValue('DO4', (data[8] & 0x08) >> 3)
                self.setDataValue('DO3', (data[8] & 0x04) >> 2)
                self.setDataValue('DO2', (data[8] & 0x02) >> 1)
                self.setDataValue('DO1', data[8] & 0x01)
            elif data_type == 26:
                RMSUA = None
                RMSUB = None
                RMSUC = None
                RMSIA = None
                RMSIB = None
                RMSIC = None
                for i in range(13):
                    if i < 4 or 5 < i < 9 or i== 12: 
                        arr = data[3+i*4 : 7+i*4]
                        strdata = ''
                        for j in arr:
                            strdata = strdata + chr(j)
                        value = struct.unpack('!f',strdata)[0]
                        if i == 0:
                            RMSUA = value
                            self.setDataValue('RMSUA', value)
                        elif i == 1:
                            RMSUB = value
                            self.setDataValue('RMSUB', value)
                        elif i == 2:
                            RMSUC = value
                            self.setDataValue('RMSUC', value)
                        elif i == 6:
                            RMSIA = value
                            self.setDataValue('RMSIA', value)
                        elif i == 7:
                            RMSIB = value
                            self.setDataValue('RMSIB', value)
                        elif i == 8:
                            RMSIC = value
                            self.setDataValue('RMSIC', value)
                        elif i == 12:
                            self.setDataValue('Psum', value)
                import math                            
                Udiff = max(math.fabs(RMSUA - RMSUB), math.fabs(RMSUA - RMSUC), math.fabs(RMSUB - RMSUC))
                Idiff = max(math.fabs(RMSIA - RMSIB), math.fabs(RMSIA - RMSIC), math.fabs(RMSIB - RMSIC))
                self.setDataValue('Udiff', Udiff)
                self.setDataValue('Idiff', Idiff)
            elif data_type == 18:
                strdata = ''
                for j in data[3:7]:
                    strdata = strdata + chr(j)
                value = struct.unpack('!f',strdata)[0]
                self.setDataValue('Pfsum', value)
                strdata = ''
                for j in data[19:23]:
                    strdata = strdata + chr(j)
                value = struct.unpack('!f',strdata)[0]
                self.setDataValue('FreqA', value)
            elif data_type == 2:
                strdata = ''
                for j in data[3:7]:
                    strdata = strdata + chr(j)
                value = struct.unpack('!f',strdata)[0]
                self.setDataValue('WH-1', value)
        except Exception as e:
            print "ZMA194E dataParse Error : ", e