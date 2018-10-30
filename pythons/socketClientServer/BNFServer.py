#!/usr/local/bin/python

"""
client.py
"""
import sys
import time
import socket
import select
import logging
import queue
import threading

from communicate import MsgS, Msg, commConfigs


class Client(object):
    def __init__(self, host, port=37777, timeout=1, reconnect=2):
        self.__host = host
        self.__port = port
        self.__timeout = timeout
        self.__buffer_size = 1024
        self.__flag = 1
        self.client = None
        self.__lock = threading.Lock()
        self.threadSend = None
        self.threadRecv = None
        self.threadMutex = threading.Lock()
        self.modelID = "BNFServer:"

        self.inputs = [] #select 接收文件描述符列表
        self.outputs = [] #输出文件描述符列表
        self.message_queues = {}#消息队列
        self.client_info = {}
    
    @property
    def flag(self):
        return self.__flag

    @flag.setter
    def flag(self, new_num):
        self.__flag = new_num

    def __connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #client.bind(('0.0.0.0', 12345,))
        self.client.setblocking(True)
        self.client.settimeout(self.__timeout)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #端口复用
        server_host = (self.__host, self.__port)
        try:
            self.client.connect(server_host)
        except:
            raise
        self.inputs.append(self.client)
        self.message_queues[self.client] = queue.Queue()
        self.outputs = []

    def sendMsg(self, msg):
        sk_out = msg.getTargetSK()
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
        while True:
            if not self.client:
                self.threadSend = None
                return
            _, writable, exceptional = select.select([], self.outputs, self.outputs, 1)

            if not (writable or exceptional) :
                continue

            for s in writable:
                try:
                    # print("send:")
                    # print(s)
                    data_bytes = self.message_queues[s].get_nowait()  # 非阻塞获取
                except queue.Empty:
                    err_msg = "Output Queue is Empty!"
                    # logging.log(err_msg)
                    self.outputs.remove(s)
                except Exception as e:
                    err_msg = "Send Data Error! ErrMsg:%s" % str(e)
                    logging.error(err_msg)
                    if s in self.outputs:
                        self.outputs.remove(s)
                else:
                    tarSk = s
                    try:
                        # print(data_bytes)
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
        while True:
            if not self.client:
                self.threadRecv = None
                return

            readable , _ , exceptional = select.select(self.inputs, [], self.inputs, 1)
            if not (readable or exceptional) :
                continue
            for s in readable :
                if s != self.client:
                    print("Debug the fd=-1")
                    print(s)
                    print(self.client)
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
                        self.processMsg(data_bytes, s)
                        print("recv Data is %s\n" % data_bytes)
                    else:
                        print("Server close connect!")
                        self.cleanDelConn(self.client)
                        self.threadRecv = None

            for s in exceptional:
                print("connect close! recvExp")
                self.cleanDelConn(self.client)
                self.threadRecv = None

    # You should define your processMsg(can use thread)
    def processMsg(self, msg, sk_in=None):
        pass

    # You should define your enrollmentServer
    def enrollmentServer(self):
        tarID = "LRManager:"
        msg = "BNFServer:"
        # msg = data
        sendMsg = Msg(isDiscons=False, tarID=tarID, cmd="CONF", msg=msg)
        sendMsg.setTargetSK(self.client)
        self.sendMsg(sendMsg)

    def threadMoniter(self):
        while True:
            if not (self.client and self.threadSend and self.threadRecv ):
                while (self.threadRecv or self.threadSend):
                    if self.threadRecv is not None:
                        print("Moniter: Recv not stop")
                    if self.threadSend is not None:
                        print("Moniter: Send not stop")
                    time.sleep(1)


                self.__connect()
                time.sleep(0.5)
                print("Manager Connected! Start threads now!")
                # print(self.outputs)
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

                    # READ CMD FROME readLine
                    data = sys.stdin.readline().strip()
                    tarID = "LRManager:"
                    msg = data
                    sendMsg = Msg(isDiscons=False, tarID=tarID, cmd="CMD:", msg=msg)
                    sendMsg.setTargetSK(self.client)
                    if self.client == None:
                        continue
                    self.sendMsg(sendMsg)
                    # print(data)

                    if "exit" == data.lower():
                        print(data)


if "__main__" == __name__:
    Client('127.0.0.1').threadMoniter()
