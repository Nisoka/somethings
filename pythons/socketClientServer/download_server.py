#!/usr/bin/python
# -*- coding: utf-8 -*- 
import socket
import hashlib
import struct
import time
import os
import threading
from SocketServer import TCPServer, StreamRequestHandler, ThreadingMixIn,ForkingMixIn
import datetime

from langRecConfig import recSysDir
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.44.10', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


#unpack to get file info
def unpack_file_info(file_info):
	file_name, file_name_len, file_size, md5 = struct.unpack(HEAD_STRUCT, file_info)
	file_name = file_name[:file_name_len]
	return file_name, file_size, md5

#pack file info
def pack_file_info(len,file_path):
	send_info = struct.pack(str(34+len)+'s',file_path)
	return send_info

host = get_host_ip()
port_sendpath = 7000
#set up speech recog connection
try:
	s_recog = socket.socket()
	s_recog.connect((host, port_sendpath))
	time.sleep(0.1)
	recog_cmd = 'LRManager:DOWServer:CONFIG      10enrollment'
	recog_start_msg = pack_file_info(10, recog_cmd)
	s_recog.send(recog_start_msg)
except socket.errno, e:
	raise Exception("DOWServer:Socket error: ", str(e))


#b'LRManager:DOWServer:CONFIG        10enrollment'
#b'BNFServer:DOWServer:Extract     len id path'

#calculate md5 to make sure the file is correct 
def cal_md5(file_path): 
	with open(file_path, 'rb') as fr: 
		md5 = hashlib.md5() 
		md5.update(fr.read()) 
		md5 = md5.hexdigest() 
		return md5


#receive file 
def recv_file(self,file_info):
	global s_recog
	try: 
		#file_info_package = self.request.recv(info_size) 
		#file_name, file_size, md5_recv = unpack_file_info(file_info_package)
		(file_lenth,file_id,file_name) = struct.unpack('2I19s', file_info[1:28])
                
                file_path = str(recSysDir) + '/wav/'+str(file_name)+'.wav'
		file_size = file_lenth - 4
		file_recv = file_path
		#print 'file_name',file_name
		with open(file_recv, 'wb') as fw:
			recved_size = 0
			while recved_size < file_size:
				remained_size = file_size - recved_size
				if remained_size > BUFFER_SIZE:
					recv_size = BUFFER_SIZE				
				else: 
					recv_size = remained_size 
				file_recv = self.request.recv(recv_size)
				recved_size += len(file_recv)
				fw.write(file_recv) 

		check_length = os.path.getsize(file_path)
		if check_length != file_size:
			print 'DOWServer:file recieve error',check_length,file_size
		else:
			#print 'Received successfully', file_name
			nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在
			# print 'current time is :',nowTime
			# print('thread name is', threading.current_thread().name)
			# s_recog = socket.socket()
			# s_recog.connect((host, port_sendpath))
			cmd_len = len(str(file_id))+len(file_path)+1
			# recog_cmd = 'LRManager:DOWServer:CONFIG      10enrollment'
			if len(str(cmd_len)) == 1:
				cmd_len_str = '000' + str(cmd_len)
			elif len(str(cmd_len)) == 2:
				cmd_len_str = '00' + str(cmd_len)
			elif len(str(cmd_len)) == 3:
				cmd_len_str = '0' + str(cmd_len)
			elif len(str(cmd_len)) == 4:
				cmd_len_str = str(cmd_len)
			else:
			 	raise Exception('id and file_path length more than 4 bit')
			recog_cmd = 'BNFServer:DOWServer:Extract   '+cmd_len_str+str(file_id)+' '+str(file_path)
			# print 'cmd::::::', recog_cmd
			recog_start_msg = pack_file_info(cmd_len, recog_cmd)
			s_recog.send(recog_start_msg)
	except socket.errno, e:
		raise Exception("DOWServer: Socket error  ",str(e))
	finally: 
		pass


class Server(ThreadingMixIn, TCPServer):pass

class Handler(StreamRequestHandler):
	def handle(self):
		addr = self.request.getpeername()
		nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 现在
		#print 'Got connection from ',addr
		#print 'current time is :', nowTime
		# msg = 'Thank you for connecting' + str(addr) + str(nowTime)
		# self.wfile.write(msg)  # have a little problem to reset connect
		file_info = self.request.recv(28)
		if len(file_info) < 28:
			print 'DOWServer:receive file info error'
		else:
			if struct.unpack('c', file_info[0])[0] == '1':
				# print 'pocess recv_file'
				recv_file(self,file_info)

if __name__ == "__main__":
	nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print 'DOWServer start , current time is :', nowTime
	BUFFER_SIZE = 1024
	HEAD_STRUCT = '128sIq32s'
	#info_size = struct.calcsize(HEAD_STRUCT)
	#host = socket.gethostname()
	port =7008

	server = Server((host, port), Handler)
	server.serve_forever()





