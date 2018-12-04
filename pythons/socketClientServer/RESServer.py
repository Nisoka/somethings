
import sys
import time
import socket
import select
import logging
import queue
import threading
from communicate import commServer, commConfigs, recvMsg, get_host_ip

class NRESServer(commServer):
    def __init__(self, host='127.0.0.1', port=7007, timeout=2, client_nums=10):
        commServer.__init__(self, host, port, timeout, client_nums)
        self.runThread = None

    def processMsg(self, data_bytes, sk):
        pass
    
    def cleanDelConn(self, sk):
        if sk in self.inputs:
            self.inputs.remove(sk)
            
        if sk in self.outputs:
            self.outputs.remove(sk)
            
        if sk in self.message_queues:
            del self.message_queues[sk]

        if sk in self.client_info:
            del self.client_info[sk]
            
        if sk == self.client:
            self.client = None

        sk.close()

    def sendData(self, data_bytes):
        if self.client == None:
            print("=================== not get client !!!! ==============")
            return 
        sk_out = self.client
        self.message_queues[sk_out].put(data_bytes)
        if sk_out not in self.outputs:
            self.outputs.append(sk_out)
                
    def threadMoniter(self):
        self.runThread = threading.Thread(target=self.run, name="RESServerThread")
        self.runThread.start()


if __name__ == "__main__":
    hostAddr = get_host_ip()
    resServer = NRESServer(hostAddr)
    resThread = threading.Thread(target=resServer.run, name="resServerThread")
    resThread.start()
    time.sleep(1)
    while True:
        data = b'\x02`\x00\x00\x00\xa9\x86\x01\x00ct:0.01;id:0.00;ja:0.31;kazak:0.04;ko:0.00;ru:0.62;tibetan:0.00;uyghur:0.00;vi:0.02;zh:0.00;'
        resServer.sendData(data)
        time.sleep(10)
