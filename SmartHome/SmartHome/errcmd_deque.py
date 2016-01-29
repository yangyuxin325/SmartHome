#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月22日

@author: sanhe1
'''
from collections import deque

class errcmd_deque():
    def __init__(self):
        self.__errcmd = {}
        self.__id_deque = deque()

    def push(self , cmd):
        self.__id_deque.append(cmd['dev_id'])
        if self.__errcmd.has_key(cmd['dev_id']):
            self.__errcmd[cmd['dev_id']].append(cmd)
        else:
            self.__errcmd[cmd['dev_id']] = deque()
            self.__errcmd[cmd['dev_id']].append(cmd)
            
    def popcmd(self):
        if len(self.__id_deque) > 0:
            dev_id = self.__id_deque.pop()
            if self.__errcmd.has_key(dev_id):
                if len(self.__errcmd[dev_id]) > 0:
                    data = self.__errcmd[dev_id].popleft()
                    if len(self.__errcmd[dev_id]) == 0:
                        del self.__errcmd[dev_id]
                    else:
                        pass
                    return data
                else:
                    pass      
            else:
                pass 
        else:
            pass
                
    def popcmdset(self, dev_id):
        if dev_id in self.__errcmd:
            for i  in range(self.__id_deque.count(dev_id)):
                self.__id_deque.remove(dev_id)
            return self.__errcmd.pop(dev_id)
        else:
            return deque()
        
    def popcmdall(self):
        m_deque = deque()
#         for (k, v) in self.__errcmd.items():
#             m_deque.append(v)
        for i  in self.__errcmd:
            m_deque.append(self.__errcmd[i])
        self.__errcmd.clear()
        self.__id_deque.clear()
        return m_deque
    
    def empty(self):
        if len(self.__errcmd) > 0:
            return True
        else:
            return False
            
            
            