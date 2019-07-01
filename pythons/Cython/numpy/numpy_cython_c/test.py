# file: test.py
import cos_doubles
import numpy as np
import matplotlib.pyplot as plt

a = np.linspace(-5, 5, 100)
b = np.empty_like(a)
# cos_doubles.cos_doubles_func(a, b)
# print(a[-10:])
# print(b[-10:])
# plt.plot(b)
# plt.show()
# exit(0)

a = a.reshape(4, -1)
b = np.empty_like(a)
cos_doubles.cos_doubles_matrix_func(a, b)
a = a.reshape(100)
b = b.reshape(100)
print(a[-10:])
print(b[-10:])
plt.plot(b)
plt.show()