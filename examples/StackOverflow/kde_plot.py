import matplotlib.pyplot as plt
import numpy as np
from scipy.stats.kde import gaussian_kde


x, y = np.genfromtxt('pogba_prova.csv', delimiter=',', unpack=True)

#print(x[1], y[1])
y = y[np.logical_not(np.isnan(y))]
x = x[np.logical_not(np.isnan(x))]
k = gaussian_kde(np.vstack([x, y]))
xi, yi = np.mgrid[x.min():x.max():x.size**0.5*1j,y.min():y.max():y.size**0.5*1j]
zi = k(np.vstack([xi.flatten(), yi.flatten()]))

fig = plt.figure(figsize=(9,10))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

# alpha=0.5 will make the plots semitransparent
ax1.pcolormesh(xi, yi, zi.reshape(xi.shape), alpha=0.5)
ax2.contourf(xi, yi, zi.reshape(xi.shape), alpha=0.5)
ax1.plot(x,y, "o")
ax1.set_xlim(x.min(), x.max())
ax1.set_ylim(y.min(), y.max())
ax2.set_xlim(x.min(), x.max())
ax2.set_ylim(y.min(), y.max())

#overlay your soccer field
im = plt.imread('statszone_football_pitch.png')
ax1.imshow(im, extent=[x.min(), x.max(), y.min(), y.max()], aspect='auto')
ax2.imshow(im, extent=[x.min(), x.max(), y.min(), y.max()], aspect='auto')

plt.show()
#plt.savefig('heatmaps_tackles.png')

#fig.savefig('pogba1516.png')