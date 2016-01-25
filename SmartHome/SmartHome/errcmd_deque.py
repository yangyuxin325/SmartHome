#coding=utf-8
#!/usr/bin/env python
'''
Created on 2016年1月22日

@author: sanhe1
'''
from collections import deque

class errcmd_deque():
    def __init__(self):
        self.errcmd = {}
        self.id_deque = deque()

    def push(self , cmd):
        self.id_deque.append(cmd['dev_id'])
        if self.errcmd.has_key(cmd['dev_id']):
            self.errcmd[cmd['dev_id']].append(cmd)
        else:
            self.errcmd[cmd['dev_id']] = deque()
            self.errcmd[cmd['dev_id']].append(cmd)
    
    def popcmd(self):
        if len(self.id_deque) > 0:
            dev_id = self.id_deque.pop()
            if len(self.errcmd[dev_id]) > 0:
                data = self.errcmd[dev_id].popleft()
                if len(self.errcmd[dev_id]) <= 0:
                    del self.errcmd[dev_id]
                return data
                
    def popcmdset(self, dev_id):
        if len(self.errcmd[dev_id]) > 0:
            data = self.errcmd[dev_id]
            del self.errcmd[dev_id]
            self.id_deque.remove(dev_id)
            return data
        
    def popcmdall(self):
        m_deque = deque()
#         for (k, v) in self.errcmd.items():
#             m_deque.append(v)
        for i  in self.errcmd:
            m_deque.append(self.errcmd[i])
        self.errcmd.clear()
        self.id_deque.clear()
        return m_deque
    
    def empty(self):
        if len(self.errcmd) > 0:
            return True
        else:
            return False
            
            
            