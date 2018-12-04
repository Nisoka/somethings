#!/usr/local/bin/python

"""
client.py
"""
import os
import sys
import time
import threading
import subprocess
import pandas as pd
import struct
import socket

from communicate import Client, commConfigs, KeyValue, get_host_ip
from LRModelMsg import Msg
from langRecConfig import workDir, LRConfig
from RESServer import NRESServer

class FileRWer(object):
    def __init__(self):
        self.fdDict = {}
        self.fdLineCntDict = {}

    def writeLine(self, filePath, line):
        if filePath not in self.fdDict:
            path = os.path.dirname(filePath)
            try:
                os.makedirs(path)
            except:
                print("mkdir {} ERROR!!!".format(path))
            fd = open(filePath, 'w')
            self.fdDict[filePath] = fd
            self.fdLineCntDict[filePath] = 0

        fd = self.fdDict[filePath]
        self.fdLineCntDict[filePath] += 1
        fd.write(line)

    def count(self, filePath):
        return self.fdLineCntDict[filePath]

    def close(self, filePath):
        if filePath in self.fdDict:
            fd = self.fdDict[filePath]
            fd.close()
            del self.fdDict[filePath]
            del self.fdLineCntDict[filePath]


def readScores(score_f):
    readFrame = pd.DataFrame.from_csv(score_f, sep='\t')
    indexList = readFrame.index.tolist()
    columnsList = readFrame.columns.tolist()
    resultList = []
    for index in indexList:
        indexResultList = []
        for label in columnsList:
            value = '{:.2f}'.format(readFrame.loc[index, label])
            indexResultList.append("{}:{};".format(label,value))
        resultList.append(''.join(indexResultList))
    return indexList,resultList
    

def formatResultAsProtol(score_f):
    # data_bytes = b'\x02\xca\x00\x00\x00\xa7\x86\x01\x00ct:0.62066966;id:4.1746232e-05;ja:0.0038012192;kazak:0.37128043;ko:6.292939000000001e-05;ru:0.00013279534;tibetan:0.0010944003999999998;uyghur:0.0019999123;vi:3.1383409999999996e-05;zh:0.0008855543;'
    # formatResult = []
    # for i in range(10):
    #     formatResult.append(data_bytes)

    # return formatResult
    indexList, resultList = readScores(score_f)
    cmd = b'\x02'
    formatResult = []
    resultLogList = []
    for i in range(len(indexList)):
        index = int(indexList[i])
        
        resultLog = str(index) + " "
        
        index = struct.pack('<L', index)
        resultString = resultList[i]
        
        resultLog = resultLog + resultString + "\n"
        
        result = bytes(resultString, encoding='utf-8')
        dataLen = len(index) + len(result)
        dataLen = struct.pack('<L', dataLen)
        data_bytes = cmd + dataLen + index + result
        formatResult.append(data_bytes)
        resultLogList.append(resultLog)

    return formatResult, resultLogList



    

class IVEServer(Client):
    def __init__(self, host, port=7000, timeout=1, reconnect=2):
        Client.__init__(self, host, port=port, timeout=timeout, reconnect=reconnect)
        self.Manager = "LRManager:"
        self.modelID = "IVEServer:"
        self.cacheMsgList = []
        self.cacheMsgTimeList = []
        # self.rwTer = FileRWer()
        self.lastBatchTime = 0

        # self.curFeatscp = None
        # self.working = False
        self.rwMutex = threading.Lock()
        self.kaldiThreadList = []

        self.logFile = open("logFile", 'w')
        self.logInCnt = 0
        self.logProcessedCnt = 0

        # For Test
        # Need to part other places
        self.resServer = NRESServer(host, port=7007)
    def startRESThread(self):
        return self.resServer.threadMoniter()
    

    def kaldiWorkThread(self, dataDir):
        print("kaldiWorkThread: {}".format(threading.currentThread()))
        # copy-feats; transform BNF-HTKType => KaldiType
        # extract-ivector;
        # processedIvector;
        # classify
        # 10    [12:06:13]    [12:06:34] = 21s
        # 100 - [12:07:42]    [12:08:40] = 58s
        # 1000  [12:11:04]    [12:14:49] = 225s
        retCode = 0
        processCmd = "./runKaldiSteps.sh --nj {} 0 {} {}".format(LRConfig["kaldiNj"], dataDir, dataDir)
        logFile = "{}/log/{}".format(dataDir, "copy-ivec-processed-class")
        proc = subprocess.Popen(processCmd, shell=True, stdout=None)
        retCode = proc.wait()
        if retCode == 0:
            score_f = "{}/score.pd".format(dataDir)
            resultList, resultLogList = formatResultAsProtol(score_f)
            for i in range(len(resultList)):
                self.logProcessedCnt += 1
                resultData = resultList[i]
                resultLog = resultLogList[i]
                self.resServer.sendData(resultData)
                self.logFile.write(resultLog)
                time.sleep(0.4)
                
            print("KALDI OK {}, -----------------------------------------  IN {} OUT {}".format(dataDir,
                                                                                                self.logInCnt,
                                                                                                self.logProcessedCnt))
        else:
            print("KALDI ERROR! {} XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ".format(dataDir))

        self.kaldiThreadList.remove(threading.current_thread())
                

    def kaldiWorkMoniterThread(self):
        threadMoniter = threading.currentThread()
        print("kaldiMoniter: {}".format(threadMoniter))
        while True:
            if self.otherThreadFlagList[threadMoniter] == False:
                self.otherThreadList.remove(threadMoniter)
                del self.otherThreadFlagList[threadMoniter]
                self.logFile.close()
                return 1

            time.sleep(1)
            curTime = time.time()
            if curTime - self.lastBatchTime > LRConfig["batchTime"]:
                
                if len(self.kaldiThreadList) >= LRConfig["kaldiProcessLimit"]:
                    continue

                if self.rwMutex.acquire():
                    linesToWrite = []
                    dirTime = None
                    while len(self.cacheMsgList) > 0 and len(linesToWrite) < LRConfig["batchCntLimit"]:
                        msg = self.cacheMsgList.pop(0)
                        msgTime = self.cacheMsgTimeList.pop(0)
                        if dirTime == None:
                            dirTime = msgTime
                        linesToWrite.append(msg)
                    self.rwMutex.release()

                    if len(linesToWrite) <= 0:
                        continue
                    
                    dirTimePart = time.strftime("%Y%m%d/%H/%M-%S", time.localtime(dirTime))
                    curFeatscp = "{}/{}/Bnfeatures.scp".format(workDir, dirTimePart)
                    curFeatsDir = os.path.dirname(curFeatscp)
                    os.makedirs(curFeatsDir, exist_ok = True)
                    
                    feat_fd = open(curFeatscp, 'w')
                    feat_fd.writelines(linesToWrite)
                    feat_fd.close()

                    threadKaldi = threading.Thread(target=self.kaldiWorkThread,
                                                   args=(os.path.dirname(curFeatscp),),
                                                   name="kaldiStep-{}".format(dirTimePart))

                    self.kaldiThreadList.append(threadKaldi)
                    threadKaldi.start()
                    self.lastBatchTime = curTime


    # You should define your processMsg(can use thread)
    def processMsg(self, msg, sk_in=None):
        self.logInCnt += 1
        msgModelID = msg.getTarModelID()
        if msgModelID == self.modelID:
            msgCmd = msg.getCmd()
            msgMsg = msg.getMsg()
            if msgCmd == "CONFIG":
                if msgMsg == "repeat":
                    self.stopMoniter = True
            elif msgCmd == "Extract":
                # msgMsg -- uttID  BnfeatFile
               
                if self.rwMutex.acquire():
                    msgTime = time.time()
                    self.cacheMsgList.append(msgMsg)
                    self.cacheMsgTimeList.append(msgTime)
                    self.rwMutex.release()
                    
if "__main__" == __name__:
    hostAddr = get_host_ip()
    ivecServer = IVEServer(hostAddr)
    ivecServer.startRESThread()
    
    otherThreads = []
    threadKeyValue = KeyValue(ivecServer.kaldiWorkMoniterThread, "kaldiWorkMoniterThread")
    otherThreads.append(threadKeyValue)
    
    ivecServer.threadMoniter(otherThreads)
    
    

