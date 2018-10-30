#!/bin/env python
import sys
import time
import socket
import select
import logging
import queue

commConfigs={
    "timeOut":10,
    "MangerServeListCnt":3
}

class commServer(object):
    def __init__(self, host='127.0.0.1', port=77777, timeout=2, client_nums=10):
        self.__host = host
        self.__port = port
        self.__timeout = timeout
        self.__client_nums = client_nums
        self.__buffer_size = 4096

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(False)
        self.server.settimeout(self.__timeout)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) #keepalive
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #端口复用
        server_host = (self.__host, self.__port)
        try:
            self.server.bind(server_host)
            self.server.listen(self.__client_nums)
        except:
            raise

        self.serverList = [self.server]
        # the self.inputs self.outputs is for single thread;
        # use multiThread use self.inputListList and self.outputListList instead
        self.inputs = [self.server]
        self.outputs = []

        # self.inputListList
        # [inputList1, inputList2, inputList3]
        self.inputListList = [] # Multi thread, every thread is a inputs!!
        for i in range(commConfigs["MangerServeListCnt"]):
            self.inputListList.append([])
        self.outputListList = [] #输出文件描述符列表
        for i in range(commConfigs["MangerServeListCnt"]):
            self.outputListList.append([])

        self.message_queues = {}#消息队列
        self.client_info = {}

    def cleanDelConn(self, s):
        # if s in self.inputs:
        #     print("remove frome inputs")
        #     self.inputs.remove(s)
        #
        # if s in self.outputs:
        #     print("remove frome outputs")
        #     self.outputs.remove(s)
        #
        # if s in self.client_info:
        #     print("del client_info")
        #     del self.client_info[s]
        #
        # if s in self.message_queues:
        #     print("del message_queues")
        #     del self.message_queues[s]
        #
        # s.close()
        pass
        
    def run(self):
        pass

# Message Struct
MsgS={
    "ModelID_s":0,
    "ModelID_e":10,
    "Cmd_s":10,
    "Cmd_e":14,
    "BytesCnt_s":14,
    "BytesCnt_e":18,
    "Data_s":18
}


class Msg():
    def __init__(self, isDiscons = True, data_bytes= "", tarID="LRManager:",
                 cmd = "CONF", msg="CONF"):
        if isDiscons == True:
            self.data_bytes = data_bytes
            data = str(data_bytes, encoding='utf-8')
            self.tarModelID = data[MsgS["ModelID_s"]: MsgS["ModelID_e"]]
            self.cmd = data[MsgS["Cmd_s"]: MsgS["Cmd_e"]]
            self.BytesCnt = int(data[MsgS["BytesCnt_s"]: MsgS["BytesCnt_e"]])
            self.msg = data[MsgS["Data_s"]: MsgS["Data_s"]+self.BytesCnt]
        else:
            self.tarModelID = tarID
            self.cmd = cmd
            self.BytesCnt = len(msg)
            self.msg = msg
            data = "{:<10}{:<4}{:4d}{}".format(self.tarModelID, self.cmd, self.BytesCnt,self.msg)
            self.data_bytes = bytes(data, encoding='utf-8')
            

    def setTargetSK(self, target_sk):
        self.target_sk = target_sk
    def getTargetSK(self):
        return self.target_sk

    def getModelID(self):
        return self.tarModelID
    
    def getCmd(self):
        return self.cmd
    
    def getMsg(self):
        return self.msg

    def getDataBytes(self):
        return self.data_bytes
