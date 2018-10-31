#!/usr/local/bin/python

"""
client.py
"""
import sys
import time

from communicate import Client, commConfigs
from LRModelMsg import Msg
from langRecConfig import LRConfig

class FileRWer(object):
    def __init__(self):
        self.fdDict = {}

    def writeLine(self, filePath, line):
        if filePath not in self.fdDict:
            fd = open(filePath, 'w')
            self.fdDict[filePath] = fd

        fd = self.fdDict[filePath]
        fd.write(line)

    def close(self, filePath):
        if filePath in self.fdDict:
            fd = self.fdDict[filePath]
            fd.close()
            del self.fdDict[filePath]


class IVEServer(Client):
    def __init__(self, host, port=37777, timeout=1, reconnect=2):
        Client.__init__(self, host, port=37777, timeout=1, reconnect=2)
        self.Manager = "LRManager:"
        self.modelID = "IVEServer:"
        self.rwTer = FileRWer()
        self.batchTime_s = None

    # You should define your processMsg(can use thread)
    def processMsg(self, data_bytes, sk_in=None):
        msg = Msg(data_bytes=data_bytes)
        msgModelID = msg.getTarModelID()
        if msgModelID == self.modelID:
            msgCmd = msg.getCmd()
            msgMsg = msg.getMsg()
            if msgCmd == "CONFIG":
                if msgMsg == "repeat":
                    self.stopMoniter = True
            elif msgCmd == "Extract":
                [uttID, featFile] = msgMsg.split("=>")
                uttID = uttID.strip()
                featFile = featFile.strip()
                featPair = uttID + LRConfig["pairSplit"] +  featFile
                # Construct feats.scp
                dataDir = LRConfig["dataDir"]
                featscp = dataDir + "/feats.scp{}".format(self.batchTime_s)
                self.rwTer.writeLine(featscp, featPair)

                curTime = time.time()
                if self.batchTime_s == None:
                    self.batchTime_s = curTime
                if curTime - self.batchTime_s > LRConfig["batchTime"]:
                    self.rwTer.close(featscp)
                    # newThread;
                    # close(feats.scp); rename featsExtracting.scp;
                    # copy-feats; pipe; ivector extractor;
                    # => ivector.scp
                    #
                    self.batchTime_s = curTime
                    pass


                ive_output = LRConfig["iveOutDir"]

                # if state == True:
                #     tarID = "LRManager:"
                #     srcID = self.modelID
                #     cmd = "TESTING"
                #     msg = fea_output
                #     # msg = data
                #     sendMsg = Msg(isDiscons=False, tarID=tarID, srcID=srcID, cmd=cmd, msg=msg)
                #     self.sendMsg(sendMsg)



if "__main__" == __name__:
    IVEServer('127.0.0.1').threadMoniter()
