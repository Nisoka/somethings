import struct

#
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