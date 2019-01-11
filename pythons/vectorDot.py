import numpy as np

a = np.array([-0.40546, 2.11443])
b = np.array([-0.87941, 0.47605])

prjLen = 0
for i in range(2):
    prjLen += a[i]*b[i]

prjLen = prjLen / (np.linalg.norm(b) * np.linalg.norm(b))

res = a - prjLen*b

print(res)
