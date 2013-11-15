#
import numpy as np
import matplotlib.pyplot as plt

x = np.array([float(i) for i in range(10)])
y = x*x

plt.plot(x,y)
#plt.title(r"$\sigma_{C}/C$")
#plt.title(r"$\int{\bar{D}dy}/\sigma_{y}$")
#plt.title(r"${\{\int{\widehat{{D^'}^{2}}dy}/\sigma_{y}\}}^{1/2}/\widehat{D}_{cw}$")
plt.title(r"$\sigma_{D_{cw}}/\bar{D}_{cw}$")
plt.savefig('Temp.png')
