#!/bin/env python

# Message Struct
MsgS = {
    "ModelID_s": 0,
    "ModelID_e": 10,
    "srcModelID_s": 10,
    "srcModelID_e": 20,
    "Cmd_s": 20,
    "Cmd_e": 30,
    "BytesCnt_s": 30,
    "BytesCnt_e": 34,
    "Data_s": 34
}


class Msg():
    def __init__(self, isDiscons=True, data_bytes="", tarID="LRManager:", srcID="LRManager:",
                 cmd="CONFIG", msg="MASSAGE"):
        if isDiscons == True:
            self.data_bytes = data_bytes
            data = str(data_bytes, encoding='utf-8')
            self.tarModelID = data[MsgS["ModelID_s"]: MsgS["ModelID_e"]]
            self.srcModelID = data[MsgS["srcModelID_s"]: MsgS["srcModelID_e"]]
            self.cmd = data[MsgS["Cmd_s"]: MsgS["Cmd_e"]].strip()
            self.BytesCnt = int(data[MsgS["BytesCnt_s"]: MsgS["BytesCnt_e"]])
            self.msg = data[MsgS["Data_s"]: MsgS["Data_s"] + self.BytesCnt]
        else:
            self.tarModelID = tarID
            self.srcModelID = srcID
            self.cmd = cmd
            self.BytesCnt = len(msg)
            self.msg = msg
            data = "{:<10}{:<10}{:<10}{:4d}{}".format(self.tarModelID, self.srcModelID, self.cmd, self.BytesCnt,
                                                      self.msg)
            self.data_bytes = bytes(data, encoding='utf-8')

    def getTarModelID(self):
        return self.tarModelID

    def getSrcModelID(self):
        return self.srcModelID

    def getCmd(self):
        return self.cmd

    def getMsg(self):
        return self.msg

    def getDataBytes(self):
        return self.data_bytes