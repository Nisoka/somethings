#!/bin/env python
import sys
import time
import socket
import select
import logging
import queue
import threading

from LRModelMsg import Msg, MsgS

commConfigs={
    "timeOut":0.05,
    "MangerServeListCnt":3,
}

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.44.10', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def stdinCmd():
    readable, _, _ = select.select([sys.stdin], [], [], 0)
    if not readable:
        return False
    
    data = sys.stdin.readline().strip()
    if data == "":
        return False
    return data
    

class KeyValue(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def getKey(self):
        return self.key
    def getValue(self):
        return self.value


def recv_stable(sk, size):
    data_bytes = None
    recved_len = 0
    while recved_len < size:
        dataPart = sk.recv(size - recved_len)
        if not dataPart:
            return False
        recved_len += len(dataPart)
        if data_bytes == None:
            data_bytes = dataPart
        else:
            data_bytes += dataPart
    return data_bytes

def recvMsg(sk):
    data_bytes = recv_stable(sk, MsgS["BytesCnt_e"])
    if data_bytes == False:
        return False
    dataLen = int(data_bytes[MsgS["BytesCnt_s"] : MsgS["BytesCnt_e"]])
    data = recv_stable(sk, dataLen)
    data_bytes += data
    # print(data_bytes)
    return Msg(data_bytes=data_bytes)

   
    
class commServer(object):
    def __init__(self, host='127.0.0.1', port=7000, timeout=1, client_nums=10):
        self.__host = host
        self.__port = port
        print(self.__host, self.__port)
        self.__timeout = timeout
        self.__client_nums = client_nums
        self.__buffer_size = 1024

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

        # EASY USAGE: just run() Thread, and use the self.client, self.inputs, self.outputs,
        self.client = None
        # the self.inputs self.outputs is for single thread;
        # use multiThread use self.inputListList and self.outputListList instead
        self.inputs = [self.server]
        self.outputs = []

        self.message_queues = {}
        self.client_info = {}


    def cleanDelConn(self, sk):
        if sk in self.inputs:
            self.inputs.remove(sk)
            
        if sk in self.outputs:
            self.outputs.remove(sk)
            
        if sk in self.message_queues:
            del self.message_queues[sk]

        if sk in self.client_info:
            del self.client_info[sk]
            
        sk.close()
        
    
    def run(self, timeout=0.5):
        while True:
            readable , writable , exceptional = select.select(self.inputs,
                                                              self.outputs,
                                                              self.inputs,
                                                              timeout)
            if not (readable or writable or exceptional) :
                continue

            # Data or Conn In!!
            for s in readable :
                if s is self.server:#是客户端连接
                    if self.client == None:
                        connection, client_address = s.accept()
                        print("%s connect." % str(client_address))
                        connection.setblocking(True) #阻塞
                        self.client = connection
                        self.inputs.append(connection) #客户端添加到inputs
                        self.client_info[connection] = client_address
                        self.message_queues[connection] = queue.Queue()
                else:
                    try:
                        # Does not know the Msg struct;
                        data_bytes = s.recv(self.__buffer_size)
                        print(data_bytes)
                    except:
                        err_msg = "Client Error!"
                        logging.error(err_msg)
                        self.cleanDelConn(s)
                    else:
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


class Manager(commServer):
    def __init__(self, host='127.0.0.1', port=7000, timeout=2, client_nums=10):
        commServer.__init__(self, host, port, timeout, client_nums)

        # must be set when a new modelClient enrollment.
        self.modelSockets = {}
        self.modelConnectStatus = {}

        # For Server socket Listen
        self.serverList = [self.server]
        self.listenThread = None
        self.listenThreadFlag = False

        # For Client socket read Msg, the socket should be add, when a new connect come.
        # no matter if sk is in the ManagerList, but, if not be a Client, will be remove.
        # self.inputListList
        # [inputList1, inputList2, inputList3]
        self.inputListList = [] # Multi thread, every thread is a inputs!!
        for i in range(commConfigs["MangerServeListCnt"]):
            self.inputListList.append([])
        self.recvThreadList = []
        self.recvThreadFlag = {}
        for i in range(commConfigs["MangerServeListCnt"]):
            self.recvThreadList.append(None)
        self.inputListListMutex = threading.Lock()

        # For Client socket send Data
        self.outputListList = [] 
        for i in range(commConfigs["MangerServeListCnt"]):
            self.outputListList.append([])
        self.sendThreadList = []
        self.sendThreadFlag = {}
        for i in range(commConfigs["MangerServeListCnt"]):
            self.sendThreadList.append(None)
        self.outputListListMutex = threading.Lock()

        # /////////////////////////////////////
        # Must be set in the override class
        self.modelID = "LRManager:"
        self.modelList = ["BNFServer:", "IVEServer:", "CLAServer:", "DATServer:", "DOWServer:"]

        

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
            self.outputListList[minIndex].append(sk)  
        else:
            return

    def removeFromOutputList(self, sk):
        if sk in self.outputs:
            self.outputs.remove(sk)

        for i in range(commConfigs["MangerServeListCnt"]):
            if sk in self.outputListList[i]:
                self.outputListList[i].remove(sk)

    def appendToInputList(self, sk):
        if sk not in self.inputs:
            self.inputs.append(sk)
            minIndex = 0
            tempMin = 65535
            for i in range(commConfigs["MangerServeListCnt"]):
                cnt = len(self.inputListList[i])
                if tempMin > cnt:
                    tempMin = cnt
                    minIndex = i
            self.inputListList[minIndex].append(sk)  # 客户端添加到inputs
        else:
            return

    def removeFromInputList(self, sk):
        if sk in self.inputs:
            self.inputs.remove(sk)

        for i in range(commConfigs["MangerServeListCnt"]):
            if sk in self.inputListList[i]:
                self.inputListList[i].remove(sk)

    def sendMsg(self, msg, sk_out=None):
        tarModelID = msg.getTarModelID()
        if sk_out == None:
            sk_out = self.modelSockets[tarModelID]
            
        if sk_out in self.message_queues:
            self.message_queues[sk_out].put(msg.getDataBytes())
            self.appendToOutputList(sk_out)
        else:
            print("Client {} has disconnect! will Not Send!!".format(tarModelID))

            
    def processMsg(self, msg, sk):
        pass

    
    def cleanDelConn(self, s):
        # print(self.client_info.keys())
        clientID = "NoSuchModel"
        if s in self.client_info:
            clientID = self.client_info[s]
        print("DisConnet the {}".format(clientID))

        self.removeFromInputList(s)
        self.removeFromOutputList(s)

        # message_queus, client_info, modelSockets, modelConnectStatus
        # must be set when a known client enrollment
        if s in self.message_queues:
            del self.message_queues[s]

        if s in self.client_info:
            del self.client_info[s]

        if clientID in self.modelSockets:
            del self.modelSockets[clientID]

        if clientID in self.modelConnectStatus:
            del self.modelConnectStatus[clientID]

        s.close()



    def serverListen(self):
        while True:
            if self.listenThreadFlag == False:
                return 1
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
                    connection.setblocking(1) #非阻塞
                    self.appendToInputList(connection)

            # for s in exceptional:
            #     logging.error("Client:%s Close Error." % str(self.client_info[s]))
            #     self.cleanDelConn(s)


    def threadRecv(self, recvSelectListIndex):
        thread = threading.currentThread()
        while True:
            if self.recvThreadFlag[thread] == False:
                self.recvThreadList.remove(thread)
                del self.recvThreadFlag[thread]
                return 1
            readable, _, exceptional = select.select(self.inputListList[recvSelectListIndex],
                                                     [],
                                                     self.inputListList[recvSelectListIndex],
                                                     commConfigs["timeOut"])
            if not (readable or exceptional):
                continue

            # Data In!!
            for s in readable:
                try:
                    # 1 recv package Head;
                    # 2 get the data len
                    # 3 block read the datalen data.
                    msg = recvMsg(s)
                except socket.timeout:
                    continue
                except Exception as e:
                    err_msg = "Client Recv Error! {}".format(e)
                    logging.error(err_msg)
                    self.cleanDelConn(s)
                else:
                    if msg:
                        self.processMsg(msg, s)
                    else:
                        print("Client:%s Close." % str(self.client_info[s]))
                        print(threading.currentThread().getName())
                        self.cleanDelConn(s)


            for s in exceptional:
                logging.error("Client:%s Close Error." % str(self.client_info[s]))
                self.cleanDelConn(s)

    def threadSend(self, sendSelectListIndex):
        thread = threading.currentThread()
        while True:
            if self.sendThreadFlag[thread] == False:
                self.sendThreadList.remove(thread)
                del self.sendThreadFlag[thread]
                return 1
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
                    self.removeFromOutputList(s)
                except Exception as e:
                    err_msg = "Send Data Error! ErrMsg:%s" % str(e)
                    logging.error(err_msg)
                    self.removeFromOutputList(s)
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
        moniterFlag = True
        while True:

            # Stop Moniter, and remove the 1 listenThread, 2 recvThreads, 3 sendThreads, 4 clientSockets
            if moniterFlag == False:
                print("Stop Moniter {}".format(self.modelID))

                self.listenThreadFlag = False
                time.sleep(0.2)
                
                for thread in self.recvThreadList:
                    self.recvThreadFlag[thread] = False
                    time.sleep(0.2)
                for thread in self.sendThreadList:
                    self.sendThreadFlag[thread] = False
                    time.sleep(0.2)
                for sk in self.inputs:
                    self.cleanDelConn(sk)
                    time.sleep(0.2)
                time.sleep(2)
                exit(0)
                    

            # Moniter the listen Thread
            if self.listenThread == None:
                self.listenThread = threading.Thread(target=self.serverListen,
                                                    name=self.modelID + "listenT")
                self.listenThreadFlag = True
                self.listenThread.start()

            # Moniter the recv Threads, and send Threads
            for i in range(commConfigs["MangerServeListCnt"]):
                # recv Thread will select all the time, so, check every time
                if self.recvThreadList[i] == None:
                    if len(self.inputListList[i]) != 0:
                        thread = \
                                 threading.Thread(target=self.threadRecv,
                                                  args=(i,),
                                                  name=self.modelID + "recvT_{}".format(i))
                        self.recvThreadList[i] = thread
                        self.recvThreadFlag[thread] = True
                        self.recvThreadList[i].start()
                        print(self.recvThreadList[i].getName())

                # all the send Thread must StartAllTime;
                # cause outputList could be change empty all the time,
                # so don't start/stop the thread all the time.
                if self.sendThreadList[i] == None:
                    thread = \
                             threading.Thread(target=self.threadSend,
                                              args=(i,),
                                              name=self.modelID + "sendT_{}".format(i))
                    self.sendThreadList[i] = thread
                    self.sendThreadFlag[thread] = True
                    self.sendThreadList[i].start()
                    print(self.sendThreadList[i].getName())

                    
            time.sleep(0.2)

            # read the stdin, Get current CMD
            data = stdinCmd()
            if data == False:
                continue
            if data == "exit":
                moniterFlag = False



class Client(object):
    def __init__(self, host, port=7000, timeout=1, reconnect=2):
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
        # keyvalue struct
        self.otherThreadList = []
        self.otherThreadFlagList = {}

        self.inputs = []  
        self.outputs = [] 
        self.message_queues = {} 

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
            self.client = None
            return False
        self.inputs.append(self.client)
        self.message_queues[self.client] = queue.Queue()
        return True

    def sendMsg(self, msg):
        sk_out = self.client
        self.message_queues[sk_out].put(msg.getDataBytes())
        if sk_out not in self.outputs:
            self.outputs.append(sk_out)
            
    # You should define your processMsg(can use thread)
    def processMsg(self, data_bytes, sk_in=None):
        pass

    # You should define your enrollmentServer
    def enrollmentServer(self):
        tarID = self.Manager
        srcID = self.modelID
        cmd = "CONFIG"
        msg = "enrollment"
        # msg = data
        sendMsg = Msg(isDiscons=False, tarID=tarID, srcID=srcID, cmd=cmd, msg=msg)
        self.sendMsg(sendMsg)


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
            _, writable, exceptional = select.select([], self.outputs, self.outputs, commConfigs["timeOut"])

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

            readable, _, exceptional = select.select(self.inputs, [], self.inputs, commConfigs["timeOut"])
            if not (readable or exceptional):
                continue
            for s in readable:
                if s != self.client:
                    print("Debug the fd=-1")
                    self.cleanDelConn(self.client)
                    self.threadRecv = None
                    continue

                try:
                    msg = recvMsg(self.client)
                except socket.timeout:
                    continue
                except Exception as e:
                    err_msg = "recv Error! {}".format(e)
                    logging.error(err_msg)
                else:
                    if msg:
                        if self.useThreadProcessMsg == False:
                            self.processMsg(msg, s)
                        else:
                            print("-------- wait use a thread to processMsg -----")
                            pass
                    else:
                        print("Server close connect!")
                        self.cleanDelConn(self.client)
                        self.threadRecv = None

            for s in exceptional:
                print("connect close! recvExp")
                self.cleanDelConn(self.client)
                self.threadRecv = None


    def threadMoniter(self, otherThreadList=[]):
        self.threadMoniterFlag = True
        while True:
            if self.threadMoniterFlag == False:
                self.cleanDelConn(self.client)
                self.threadRecvFlag = False
                self.threadSendFlag = False
                for thread in self.otherThreadList:
                    self.otherThreadFlagList[thread] = False
                time.sleep(2)
                exit(0)

            if not (self.client and self.threadSend and self.threadRecv):
                while (self.threadRecv or self.threadSend):
                    if self.threadRecv is not None:
                        print("{} Moniter: Recv not stop".format(self.modelID))
                    if self.threadSend is not None:
                        print("{} Moniter: Send not stop".format(self.modelID))
                    time.sleep(0.5)
                    
                while len(self.otherThreadList) != 0:
                    print("bug in otherThread Moniter")
                    for thread in self.otherThreadList:
                        self.otherThreadFlagList[thread] = False
                    time.sleep(0.5)

                if self.__connect() == False:
                    continue
                
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

                for keyValue in otherThreadList:
                    threadFunc = keyValue.getKey()
                    threadName = keyValue.getValue()
                    thread = threading.Thread(target=threadFunc,
                                              name=self.modelID + threadName)
                    self.otherThreadList.append(thread)
                    self.otherThreadFlagList[thread] = True
                    thread.start()

                time.sleep(1)

                self.enrollmentServer()


            else:
                time.sleep(0.1)
                data = stdinCmd()
                if data == False:
                    continue
                
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

