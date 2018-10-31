#!/usr/local/bin/python

"""
client.py
"""
import sys
import time

from communicate import Client, commConfigs
from LRModelMsg import Msg
from langRecConfig import LRConfig

sys.path.append("/home/nan/git-nan/code/pytools/BUT-Speech/BottleneckFeatureExtractor")
from PipeAudio2BNF import extractBNF

class BNFServer(Client):
    def __init__(self, host, port=37777, timeout=1, reconnect=2):
        Client.__init__(self, host, port=37777, timeout=1, reconnect=2)
        self.Manager = "LRManager:"
        self.modelID = "BNFServer:"

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
                [uttID, wavfile] = msgMsg.split("=>")
                wavfile = wavfile.strip()
                uttID = uttID.strip()
                fea_output = LRConfig["bnfOutDir"] + "/" + uttID + ".bnf"
                state = extractBNF(wavfile, fea_output)
                if state == True:
                    tarID = "LRManager:"
                    srcID = self.modelID
                    cmd = "TESTING"
                    msg = fea_output
                    # msg = data
                    sendMsg = Msg(isDiscons=False, tarID=tarID, srcID=srcID, cmd=cmd, msg=msg)
                    self.sendMsg(sendMsg)



if "__main__" == __name__:
    BNFServer('127.0.0.1').threadMoniter()
