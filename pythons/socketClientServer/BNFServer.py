#!/usr/local/bin/python

"""
client.py
"""
import sys
import time
import socket
import threading
import subprocess

from communicate import Client, commConfigs, KeyValue, get_host_ip
from LRModelMsg import Msg
from langRecConfig import LRConfig, testDir, nnPath

BUT_SPEECH_PATH="/home/liujunnan/git-nan/code/pytools/BUT-Speech/BottleneckFeatureExtractor"
sys.path.append(BUT_SPEECH_PATH)
from PipeAudio2BNF import extractBNF

class BNFServer(Client):
    def __init__(self, host, port=7000, timeout=1, reconnect=2):
        Client.__init__(self, host, port=7000, timeout=1, reconnect=2)
        self.Manager = "LRManager:"
        self.modelID = "BNFServer:"


        self.bnfThreadCnt = LRConfig["extractBNFLimit"]
        self.curUseEntry = 0

        self.extractThreadList = []
        for i in range(self.bnfThreadCnt):
            self.extractThreadList.append(None)
        self.extractThreadFlag = {}
        
        # uttID  wavfile
        # "10001  /data/test/10001.wav"

        self.entryListList = []
        for i in range(self.bnfThreadCnt):
            self.entryListList.append([])
            
        self.entryLockList = []
        for i in range(self.bnfThreadCnt):
            self.entryLockList.append(threading.Lock())
        
        
    def extractSingel(self, msgMsg):
        # print(msgMsg)
        [uttID, wavfile] = msgMsg.split(" ")
        wavfile = wavfile.strip()
        uttID = uttID.strip()
        fea_output = LRConfig["bnfOutDir"] + "/" + uttID + ".bnf"
        
        try:
            # cmd = "sox -t wav {} -r 8k -t wav {}.8k".format(wavfile, wavfile)
            # proc = subprocess.Popen(cmd, shell=True, stdout=None)
            # retCode = proc.wait()
            # wavfile = wavfile + ".8k"
            pipeFile = "sox -t wav {} -r 8k -t wav -".format(wavfile)
            cmd = "python3 {}/PipeAudio2BNF.py '{}' {}".format(BUT_SPEECH_PATH, pipeFile, fea_output)
            # state = extractBNF(wavfile, fea_output, nnPath=nnPath)
            proc = subprocess.Popen(cmd, shell=True, stdout=None)
            state = proc.wait()
        except Exception as e:
            print("ERROR: Extract BNF Error! {}".format(e))
        else:
            if state == 0:
                # print("{} extract BNF over".format(uttID))
                tarID = "IVEServer:"
                srcID = self.modelID
                cmd = "Extract"
                msg = uttID + LRConfig["pairSplit"] + fea_output + "\n"
                # msg = data
                sendMsg = Msg(isDiscons=False, tarID=tarID, srcID=srcID, cmd=cmd, msg=msg)
                self.sendMsg(sendMsg)
                # DoClean
                cmd = "rm -f {}".format(wavfile)
                proc = subprocess.Popen(cmd, shell=True, stdout=None)
            else:
                print("extract BNF Fail")

    def extractBNFThread(self, thisEntryIndex):
        thread = threading.currentThread()
        while True:
            time.sleep(0.05)
            if self.extractThreadFlag[thread] == False:
                self.extractThreadList.remove(thread)
                del self.extractThreadFlag[thread]
                return 1
            
            if self.entryLockList[thisEntryIndex].acquire():
                if len(self.entryListList[thisEntryIndex]) > 0:
                    msgMsg = self.entryListList[thisEntryIndex].pop(0)
                    self.extractSingel(msgMsg)
                self.entryLockList[thisEntryIndex].release()



    def extractBNFMoniterThread(self):
        threadMoniter = threading.currentThread()
        print("extractMoniter: {}".format(threadMoniter))
        while True:
            time.sleep(0.05)
            if self.otherThreadFlagList[threadMoniter] == False:
                self.otherThreadList.remove(threadMoniter)
                del self.otherThreadFlagList[threadMoniter]
                for thread in self.extractThreadList:
                    self.extractThreadFlag[thread] = False
                return 1

            for i in range(self.bnfThreadCnt):
                if self.extractThreadList[i] == None:
                    thread = threading.Thread(target=self.extractBNFThread, args=(i, ), name="extractBNF-{}".format(i))
                    self.extractThreadList[i] = thread
                    self.extractThreadFlag[thread] = True
                    thread.start()
                    print(thread.getName())
            

    # You should define your processMsg(can use thread)
    def processMsg(self, msg, sk_in=None):
        msgModelID = msg.getTarModelID()
        if msgModelID == self.modelID:
            msgCmd = msg.getCmd()
            msgMsg = msg.getMsg()
            if msgCmd == "CONFIG":
                if msgMsg == "repeat":
                    self.stopMoniter = True
            elif msgCmd == "Extract":

                if self.curUseEntry >= self.bnfThreadCnt:
                    self.curUseEntry = 0
                
                if self.entryLockList[self.curUseEntry].acquire():
                    self.entryListList[self.curUseEntry].append(msgMsg)
                    self.entryLockList[self.curUseEntry].release()
                    self.curUseEntry += 1
                    
                


if "__main__" == __name__:
    hostAddr = get_host_ip()
    bnfServer = BNFServer(hostAddr)
    
    otherThreads = []
    threadKeyValue = KeyValue(bnfServer.extractBNFMoniterThread, "extractBNFMoniterThread")
    otherThreads.append(threadKeyValue)
    
    bnfServer.threadMoniter(otherThreads)
