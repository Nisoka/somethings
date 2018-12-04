
import pandas as pd

pdFrame = pd.DataFrame(
    data=[[   0,    0,    2,    5,    0],
          [1478, 3877, 3674, 2328, 2539],
          [1613, 4088, 3991, 6461, 2691],
          [1560, 3392, 3826, 4787, 2613],
          [1608, 4802, 3932, 4477, 2705],
          [1576, 3933, 3909, 4979, 2685],
          [  95,  229,  255,  496,  201],
          [   2,    0,    1,   27,    0],
          [1438, 3785, 3589, 4174, 2215],
          [1342, 4043, 4009, 4665, 3033]],
    index=['05-01-11', '05-02-11', '05-03-11', '05-04-11', '05-05-11',
           '05-06-11', '05-07-11', '05-08-11', '05-09-11', '05-10-11'],
    columns=['R003', 'R004', 'R005', 'R006', 'R007'])


print(pdFrame)
print(pdFrame.columns)
print(pdFrame.columns.tolist())

import struct

res = struct.pack('<L', 1000000)
print(len(res), res)
value = struct.unpack('<L', res)
print(value)

a = b'\x02'
print(len(a), a)
# a = struct.pack('<c', '2')
# print(a)

dataLen = b'\xca\x00\x00\x00'
dataLen = struct.unpack('<L', dataLen)
print(dataLen)
result = b'\xca\x00\x00\x00\xa7\x86\x01\x00ct:0.62066966;id:4.1746232e-05;ja:0.0038012192;kazak:0.37128043;ko:6.292939000000001e-05;ru:0.00013279534;tibetan:0.0010944003999999998;uyghur:0.0019999123;vi:3.1383409999999996e-05;zh:0.0008855543;'
print(len(result))

import socket
import socket

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

print(get_host_ip())


fdw = open("curLearn.fd", 'w')

fdw.writelines()