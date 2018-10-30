#!/bin/env python

'''
langRec Manager 
relation:
1 BNF Extractor model
2 ivector Extractor model
3 classify model
'''
import sys
import time
import socket
import select
import logging
import queue
import threading
from communicate import commServer, MsgS, Msg, commConfigs

# BNF

class LangRecManager(commServer):
    def __init__(self, host='127.0.0.1', port=37777, timeout=2, client_nums=10):
        commServer.__init__(self, host, port, timeout, client_nums)
        self.modelID = "LRManager:"
        self.modelList = ["BNFServer:", "IVEServer:", "CLAServer:", "DATServer:"]
        self.modelSockets = {}
        self.modelConnectStatus = {}
        self.listenThread = None
        self.recvThreadList = []
        for i in range(commConfigs["MangerServeListCnt"]):
            self.recvThreadList.append(None)
        self.inputListListMutex = threading.Lock()
        self.sendThreadList = []
        for i in range(commConfigs["MangerServeListCnt"]):
            self.sendThreadList.append(None)
        self.outputListListMutex = threading.Lock()

    # def sendMsg(self, msg):
    #     sk_out = msg.getTargetSK()
    #     self.message_queues[sk_out].put(msg.getDataBytes())
    #     if sk_out not in self.outputs:
    #         self.outputs.append(sk_out)


    def removeFromOutputList(self, sk):
        if sk in self.outputs:
            self.outputs.remove(sk)

        for i in range(commConfigs["MangerServeListCnt"]):
            if sk in self.outputListList[i]:
                self.outputListList[i].remove(sk)

    def appendToOutputList(self, sk):

        if sk not in self.outputs:
            self.outputs.append(sk)
            minIndex = 0
            tempMin = 65535
            for i in range(commConfigs["MangerServeListCnt"]):
                cnt = len(self.outputListList[i])
                if tempMin > cnt:
                    tempMin = cnt
                    minIndex = i
            self.outputListList[minIndex].append(sk)  # 客户端添加到inputs
        else:
            return

    def appendToInputList(self, sk):
        pass
    def removeFromInputList(self, sk):
        pass

    def sendMsg(self, msg):
        sk_out = msg.getTargetSK()
        self.message_queues[sk_out].put(msg.getDataBytes())
        if sk_out not in self.outputs:
            self.outputs.append(sk_out)


    def cleanDelConn(self, s):
        clientID = self.client_info[s]
        print("DisConnet the {}".format(clientID))
        # print("clean inputs:{}, outputs{}".format(self.inputs, self.outputs))
        
        if s in self.inputs:
            # print("remove frome inputs")
            self.inputs.remove(s)

        if s in self.outputs:
            # print("remove frome outputs")
            self.outputs.remove(s)
                            
        if s in self.message_queues:
            # print("del message_queues")
            del self.message_queues[s]

        if s in self.client_info:
            # print("del client_info")
            del self.client_info[s]

        if clientID in self.modelSockets:
            # print("del the modelSockets")
            del self.modelSockets[clientID]

        if clientID in self.modelConnectStatus:
            # print("del the modelConnetStatus")
            del self.modelConnectStatus[clientID]

        s.close()



    def threadListen(self):
        while True:
            readable , _ , exceptional = select.select(self.serverList,
                                                       [],
                                                       self.serverList,
                                                       commConfigs["timeOut"])
            if not (readable or exceptional):
                continue

            # Conn In!!
            for s in readable :
                if s is self.server:#是客户端连接
                    connection, client_address = s.accept()
                    print("%s connect." % str(client_address))
                    connection.setblocking(0) #非阻塞
                    minIndex = 0
                    tempMin = 65535
                    for i in range(commConfigs["MangerServeListCnt"]):
                        cnt = len(self.inputListList[i])
                        if tempMin > cnt:
                            tempMin = cnt
                            minIndex = i

                    self.inputListList[minIndex].append(connection) #客户端添加到inputs
            # for s in exceptional:
            #     logging.error("Client:%s Close Error." % str(self.client_info[s]))
            #     self.cleanDelConn(s)


    def threadRecv(self, recvSelectListIndex):
        while True:
            readable, _, exceptional = select.select(self.inputListList[recvSelectListIndex],
                                                     [],
                                                     self.inputListList[recvSelectListIndex],
                                                     commConfigs["timeOut"])
            if not (readable or exceptional):
                continue

            # Data In!!
            for s in readable:
                try:
                    data_bytes = s.recv(1024)
                    print(data_bytes)
                except:
                    err_msg = "Client Error!"
                    logging.error(err_msg)

                if data_bytes:
                    self.processMsg(data_bytes, s)
                else:
                    print("Client:%s Close." % str(self.client_info[s]))
                    self.cleanDelConn(s)
            for s in exceptional:
                logging.error("Client:%s Close Error." % str(self.client_info[s]))
                self.cleanDelConn(s)

    def threadSend(self, sendSelectListIndex):
        while True:
            _, writable, exceptional = select.select([],
                                                     self.outputListList[sendSelectListIndex],
                                                     self.outputListList[sendSelectListIndex],
                                                     commConfigs["timeOut"])
            if not (writable or exceptional):
                continue

            for s in writable:
                try:
                    data_bytes = self.message_queues[s].get_nowait()  # 非阻塞获取
                except queue.Empty:
                    err_msg = "Output Queue is Empty!"
                    self.outputListList[sendSelectListIndex].remove(s)

                except Exception as e:
                    err_msg = "Send Data Error! ErrMsg:%s" % str(e)
                    logging.error(err_msg)
                    if s in self.outputListList[sendSelectListIndex]:
                        self.outputListList[sendSelectListIndex].remove(s)
                else:
                    tarSk = s
                    try:
                        tarSk.sendall(data_bytes)
                    except Exception as e:
                        err_msg = "Send Data to %s  Error! ErrMsg:%s" % (str(self.client_info[tarSk]), str(e))
                        logging.error(err_msg)
                        print("Client: %s Close Error." % str(self.client_info[tarSk]))
                        self.cleanDelConn(tarSk)
            for s in exceptional:
                logging.error("Client:%s Close Error." % str(self.client_info[s]))
                self.cleanDelConn(s)

    def threadMoniter(self):
        while True:
            if self.listenThread == None:
                self.listenThread = threading.Thread(target=self.threadListen,
                                                    name=self.modelID + "listenT")
                self.listenThread.start()

            for i in range(commConfigs["MangerServeListCnt"]):
                # recv Thread will select all the time, so, check every time
                if self.recvThreadList[i] == None:
                    if len(self.inputListList[i]) != 0:
                        self.recvThreadList[i] = \
                            threading.Thread(target=self.threadRecv,
                                             args=(i,),
                                             name=self.modelID + "recvT_{}".format(i))
                        self.recvThreadList[i].start()
                # all the send Thread must StartAllTime;
                # cause outputList could be change empty all the time,
                # so don't start/stop the thread all the time.
                if self.sendThreadList[i] == None:
                    self.sendThreadList[i] = \
                        threading.Thread(target=self.threadRecv,
                                             args=(i,),
                                             name=self.modelID + "recvT_{}".format(i))
                    self.sendThreadList[i].start()
            time.sleep(1)


    def run(self):
        while True:
            readable , writable , exceptional = select.select(self.inputs,
                                                              self.outputs,
                                                              self.inputs,
                                                              commConfigs["timeOut"])
            if not (readable or writable or exceptional) :
                continue

            # Data or Conn In!!
            for s in readable :
                if s is self.server:#是客户端连接
                    connection, client_address = s.accept()
                    print("%s connect." % str(client_address))
                    connection.setblocking(0) #非阻塞
                    self.inputs.append(connection) #客户端添加到inputs
                else:
                    try:
                        data_bytes = s.recv(1024)
                        print(data_bytes)
                    except:
                        err_msg = "Client Error!"
                        logging.error(err_msg)
        
                    if data_bytes:
                        self.processMsg(data_bytes, s)
                    else: 
                        print("Client:%s Close." % str(self.client_info[s]))
                        self.cleanDelConn(s)

            for s in writable: 
                try:
                    data_bytes = self.message_queues[s].get_nowait()  #非阻塞获取
                except queue.Empty:
                    err_msg = "Output Queue is Empty!"
                    self.outputs.remove(s)
                    
                except Exception as e:
                    err_msg = "Send Data Error! ErrMsg:%s" % str(e)
                    logging.error(err_msg)
                    if s in self.outputs:
                        self.outputs.remove(s)
                else:
                    tarSk = s
                    try:
                        tarSk.sendall(data_bytes)
                    except Exception as e:
                        err_msg = "Send Data to %s  Error! ErrMsg:%s" % (str(self.client_info[tarSk]), str(e))
                        logging.error(err_msg)
                        print("Client: %s Close Error." % str(self.client_info[tarSk]))
                        self.cleanDelConn(tarSk)

            for s in exceptional:
                logging.error("Client:%s Close Error." % str(self.client_info[s]))
                self.cleanDelConn(s)

    def processMsg(self, data_bytes, sk_in):
        msg = Msg(data_bytes=data_bytes)
        msgModelID = msg.getModelID()
        msgCmd = msg.getCmd()
        msgMsg = msg.getMsg()
        # confirm connected model.
        # modelID - LRManager:
        # cmd     - CONF
        # msg     - connectID(BNFServer:, IVECServer:, CLASServer:, DATAServer:)
        if msgModelID == self.modelID:
            if msgCmd == "CONF":
                clientID = msgMsg
                if clientID not in self.modelList:
                    self.modelConnectStatus[clientID] = True
                    self.modelSockets[clientID] = sk_in
                    self.message_queues[sk_in] = queue.Queue()
                    self.client_info[sk_in] = clientID
                    self.cleanDelConn(sk_in)
                    return None

                if clientID not in self.modelConnectStatus:
                    self.modelConnectStatus[clientID] = True
                    self.modelSockets[clientID] = sk_in
                    self.message_queues[sk_in] = queue.Queue()
                    self.client_info[sk_in] = clientID

                tarID = self.modelID
                sendMsg = Msg(isDiscons=False, tarID=tarID, cmd="CONF")
                sendMsg.setTargetSK(sk_in)
                self.sendMsg(sendMsg)

        for model in self.modelList:
            if msgModelID == model:
                if self.modelConnectStatus[model] == True:
                    target_sk = self.modelSockets[model]
                else:
                    target_sk = sk_in
                    return None

if "__main__" == __name__:
    LangRecManager().run()

