#!/bin/env python
import sys
import time
import socket
import select
import logging
import queue
import threading

from LRModelMsg import Msg

commConfigs={
    "timeOut":0.1,
    "MangerServeListCnt":3,
}

class commServer(object):
    def __init__(self, host='127.0.0.1', port=77777, timeout=1, client_nums=10):
        self.__host = host
        self.__port = port
        self.__timeout = timeout
        self.__client_nums = client_nums
        self.__buffer_size = 4096

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # no matter what the operate, recv send accept ...
        # blocking=false socket, will return rightnow, so will recv/send multi times to
        # complete a true recv/send
        # blocking=true socket, will wait for the recv/send data(unless the Tcp's half package, ),
        # self.server.setblocking(False)
        self.server.setblocking(True)

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
        pass
        
    def run(self):
        pass


class Client(object):
    def __init__(self, host, port=37777, timeout=1, reconnect=2):
        self.__host = host
        self.__port = port
        self.__timeout = timeout
        self.__buffer_size = 1024
        self.__flag = 1
        self.__lock = threading.Lock()

        self.client = None

        self.threadSend = None
        self.threadRecv = None
        self.threadSendFlag = False
        self.threadRecvFlag = False
        self.threadMoniterFlag = False
        self.threadMutex = threading.Lock()

        self.inputs = []  # select 接收文件描述符列表
        self.outputs = []  # 输出文件描述符列表
        self.message_queues = {}  # 消息队列
        self.client_info = {}

        self.useThreadProcessMsg = False
        self.modelID = ""
        self.Manager = ""

    @property
    def flag(self):
        return self.__flag

    @flag.setter
    def flag(self, new_num):
        self.__flag = new_num

    def __connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client.bind(('0.0.0.0', 12345,))
        self.client.setblocking(True)
        self.client.settimeout(self.__timeout)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用
        server_host = (self.__host, self.__port)
        try:
            self.client.connect(server_host)
        except:
            raise
        self.inputs.append(self.client)
        self.message_queues[self.client] = queue.Queue()
        self.outputs = []

    def sendMsg(self, msg):
        sk_out = self.client
        self.message_queues[sk_out].put(msg.getDataBytes())
        if sk_out not in self.outputs:
            self.outputs.append(sk_out)

    def cleanDelConn(self, s):
        if self.threadMutex.acquire():
            if s in self.inputs:
                print("remove inputs")
                self.inputs.remove(s)
            if s != None:
                s.close()
                if s == self.client:
                    self.client = None
            self.threadMutex.release()

    def sendThread(self):
        while self.threadSendFlag:
            if not self.client:
                self.threadSend = None
                return
            _, writable, exceptional = select.select([], self.outputs, self.outputs, 1)

            if not (writable or exceptional):
                continue

            for s in writable:
                try:
                    data_bytes = self.message_queues[s].get_nowait()  # 非阻塞获取
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
                        print("connect close! sendFail")
                        self.cleanDelConn(self.client)
                        self.threadSend = None

            for s in exceptional:
                print("connect close! sendExp")
                self.cleanDelConn(self.client)
                self.threadSend = None

    def recvThread(self):
        while self.threadRecvFlag:
            if not self.client:
                self.threadRecv = None
                return

            readable, _, exceptional = select.select(self.inputs, [], self.inputs, 1)
            if not (readable or exceptional):
                continue
            for s in readable:
                if s != self.client:
                    print("Debug the fd=-1")
                    self.cleanDelConn(self.client)
                    self.threadRecv = None
                    continue

                try:
                    data_bytes = self.client.recv(self.__buffer_size)
                except socket.timeout:
                    continue
                except Exception as e:
                    err_msg = "recv Error! {}".format(e)
                    logging.error(err_msg)
                else:
                    if data_bytes:
                        if self.useThreadProcessMsg == False:
                            self.processMsg(data_bytes, s)
                        else:
                            print("-------- wait use a thread to processMsg -----")
                            pass
                        print("recv Data is %s\n" % data_bytes)
                    else:
                        print("Server close connect!")
                        self.cleanDelConn(self.client)
                        self.threadRecv = None

            for s in exceptional:
                print("connect close! recvExp")
                self.cleanDelConn(self.client)
                self.threadRecv = None

    # You should define your enrollmentServer
    def enrollmentServer(self):
        tarID = self.Manager
        srcID = self.modelID
        cmd = "CONFIG"
        msg = "enrollment"
        # msg = data
        sendMsg = Msg(isDiscons=False, tarID=tarID, srcID=srcID, cmd=cmd, msg=msg)
        self.sendMsg(sendMsg)

    def threadMoniter(self):
        self.threadMoniterFlag = True
        while True:
            if self.threadMoniterFlag == False:
                self.cleanDelConn(self.client)
                self.threadRecvFlag = False
                self.threadSendFlag = False
                time.sleep(1)
                exit(0)

            if not (self.client and self.threadSend and self.threadRecv):
                while (self.threadRecv or self.threadSend):
                    if self.threadRecv is not None:
                        print("{} Moniter: Recv not stop".format(self.modelID))
                    if self.threadSend is not None:
                        print("{} Moniter: Send not stop".format(self.modelID))
                    time.sleep(0.5)

                self.__connect()
                time.sleep(0.5)
                self.threadRecvFlag = True
                self.threadSendFlag = True
                print("{} Connected! Start threads now!".format(self.modelID))
                self.threadSend = threading.Thread(target=self.sendThread,
                                                   name=self.modelID + "sendT")
                self.threadRecv = threading.Thread(target=self.recvThread,
                                                   name=self.modelID + "recvT")
                self.threadSend.start()
                self.threadRecv.start()
                time.sleep(1)

                self.enrollmentServer()

            else:
                time.sleep(0.1)
                readable, _, _ = select.select([sys.stdin], [], [], 0)
                if not readable:
                    continue
                for fd in readable:
                    if fd != sys.stdin:
                        continue

                    data = sys.stdin.readline().strip()
                    tarID = self.Manager
                    srcID = self.modelID
                    msg = data
                    sendMsg = Msg(isDiscons=False, tarID=tarID, srcID=srcID,
                                  cmd="CMD:", msg=msg)
                    if self.client == None:
                        continue
                    self.sendMsg(sendMsg)

                    if "exit" == data.lower():
                        self.threadMoniterFlag = False

    # You should define your processMsg(can use thread)
    def processMsg(self, data_bytes, sk_in=None):
        pass