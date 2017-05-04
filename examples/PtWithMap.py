from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()

bmap = Basemap(projection='merc', lat_0 = 57, lon_0 = -135,
    resolution = 'h', area_thresh = 0.1,
    llcrnrlon=-136.25, llcrnrlat=56.0,
    urcrnrlon=-134.25, urcrnrlat=57.75)

bmap.drawcoastlines()
bmap.drawcountries()
bmap.fillcontinents(color = 'gray', zorder = 0)
bmap.drawmapboundary()

lons = [-135.3318, -134.8331, -134.6572]
lats = [57.0799, 57.0894, 56.2399]
x,y = bmap(lons, lats)
pts = bmap.scatter(x[0], y[0], c ='b', marker = 'o', s = 80, alpha = 1.0)
pts = bmap.scatter(x[1], y[1], c ='g', marker = 'o', s = 80, alpha = 1.0)
pts = bmap.scatter(x[2], y[2], c ='r', marker = 'o', s = 80)
#pts.set_facecolor([(0.7, 0.3, 0.3, 0.2), (1, 0.0, 1, 0.5), (1.0, 1.0, 0.2, 0.2)])
fig.canvas.draw()
plt.show()