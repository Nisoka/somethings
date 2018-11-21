#!/bin/env python

'''
langRec Manager 
relation:
1 BNF Extractor model
2 ivector Extractor model
3 classify model
'''
import os
import sys
import time
import socket
import select
import logging
import queue
import threading
from communicate import Manager, commServer, commConfigs, recvMsg, get_host_ip, stdinCmd
from LRModelMsg import Msg, MsgS
from langRecConfig import recSysDir, workDir, wavDir
# BNF

class LangRecManager(Manager):
    def __init__(self, host='127.0.0.1', port=7000, timeout=2, client_nums=10):
        Manager.__init__(self, host, port, timeout, client_nums)
        
        self.modelID = "LRManager:"
        self.modelList = ["BNFServer:", "IVEServer:", "CLAServer:", "DATServer:", "DOWServer:"]

    def processMsg(self, msg, sk_in):
        msgTarModelID = msg.getTarModelID()
        msgSrcModelID = msg.getSrcModelID()
        msgCmd = msg.getCmd().strip()
        msgMsg = msg.getMsg()
        # confirm connected model.
        # modelID - LRManager:
        # cmd     - CONF
        # msg     - connectID(BNFServer:, IVECServer:, CLASServer:, DATAServer:)
        if msgTarModelID == self.modelID:
            # print("in processMsg self model!")
            if msgCmd == "CONFIG":
                clientID = msgSrcModelID
                if clientID not in self.modelList:
                    print("WRONG Client name {}, not in ManageList!".format(clientID))
                    self.cleanDelConn(sk_in)
                    return None

                if clientID not in self.modelConnectStatus:
                    print("Get the client Info {}, ".format(clientID) + threading.currentThread().getName())
                    self.modelConnectStatus[clientID] = True
                    self.modelSockets[clientID] = sk_in
                    self.message_queues[sk_in] = queue.Queue()
                    self.client_info[sk_in] = clientID
                else:
                    # There has a same model
                    print("Have Manager a same Client {}, You just stop Now!".format(clientID) + threading.currentThread().getName())
                    # don't save the client Info, just
                    self.message_queues[sk_in] = queue.Queue()
                    self.client_info[sk_in] = clientID+"-repeat"
                    sendMsg = Msg(isDiscons=False, tarID=clientID,
                                  srcID=self.modelID, cmd="CONFIG", msg="repeat")
                    self.sendMsg(sendMsg, sk_in)
            elif msgCmd == "TESTING" :
                print(msg.getDataBytes())
            elif msgCmd == "CMD:":
                print(msg.getDataBytes())
            else:
                pass

            return None


        if msgTarModelID in self.modelList:
            if msgTarModelID not in self.modelConnectStatus:
                sendMsg = Msg(isDiscons=False, tarID=msgSrcModelID,
                              srcID=self.modelID, cmd="CONFIG", msg="NotReady")
                self.sendMsg(sendMsg, sk_in)
                return None
            if self.modelConnectStatus[msgTarModelID] == True:
                target_sk = self.modelSockets[msgTarModelID]
                sendMsg = Msg(isDiscons=False, tarID=msgTarModelID,
                              srcID=msgSrcModelID, cmd=msgCmd, msg=msgMsg)
                self.sendMsg(sendMsg, target_sk)
            else:
                sendMsg = Msg(isDiscons=False, tarID=msgSrcModelID,
                              srcID=self.modelID, cmd="CONFIG", msg="NotReady")
                self.sendMsg(sendMsg, sk_in)
                return None
        else:
            print("{} msg To, No that Target:{}".format(msgSrcModelID, msgTarModelID))


    def TestFunc(self):
        while True:
            time.sleep(5)
            msgTarModelID = "BNFServer:"
            msgSrcModelID = "DOWServer:"
            msgCmd = "Extract"
            print("before send Extract")
            if msgTarModelID in self.modelSockets:
                print("One Test:{} {}".format(msgTarModelID, time.strftime("%Y%m%d %H:%M:%S", time.localtime(time.time()))))
                target_sk = self.modelSockets[msgTarModelID]
                pathDir = "/do2/home/langRec/wav"
                # msgMsg = "11-06-15-38-11-0120.wav {}/11-06-15-38-11-0120.wav".format(pathDir)
                # sendMsg = Msg(isDiscons=False, tarID=msgTarModelID,
                #               srcID=msgSrcModelID, cmd=msgCmd, msg=msgMsg)
                # self.sendMsg(sendMsg, target_sk)
                wavCnt = 0
                for maindir, subdir, file_name_list in os.walk(pathDir):
                    for fileName in file_name_list:
                        if fileName[-4:] == ".wav":
                            fileName = fileName[:-4]
                            msgMsg = "{} {}/{}.wav".format(wavCnt, pathDir, fileName)
                            sendMsg = Msg(isDiscons=False, tarID=msgTarModelID,
                                          srcID=msgSrcModelID, cmd=msgCmd, msg=msgMsg)
                            self.sendMsg(sendMsg, target_sk)
                            wavCnt += 1
                            if wavCnt == 10:
                                return None
                            time.sleep(0.1)
            else:
                pass    
            

    
                    
if "__main__" == __name__:
    hostAddr = get_host_ip()
    langRecManager = LangRecManager(hostAddr)
    os.makedirs(wavDir, exist_ok = True)
    os.makedirs(workDir, exist_ok = True)
    # testThread = threading.Thread(target=langRecManager.TestFunc, name="TestFunc")
    # testThread.start()
    langRecManager.threadMoniter()


