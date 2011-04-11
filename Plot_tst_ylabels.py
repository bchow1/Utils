import matplotlib.pyplot as plt
import numpy as np

x,y = np.random.randn(2,100)
fig = plt.figure()
ax1 = fig.add_subplot(121)
ax1.xcorr(x, y, usevlines=True, maxlags=50, normed=True, lw=2)
ax1.grid(True)
ax1.axhline(0, color='black', lw=2)

ax2 = fig.add_subplot(122, sharey=ax1)
ax2.acorr(x, usevlines=True, normed=True, maxlags=50, lw=2)
ax2.grid(True)
ax2.axhline(0, color='black', lw=2)
#ax2.set_yticklabels(,ha='right')
ax2.text(0.5,-0.13,'ylabel',transform=ax2.transAxes,ha='center',va='center') 

plt.show()
