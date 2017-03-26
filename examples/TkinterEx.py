import numpy as np
import pylab
import matplotlib.pyplot as plt
import Tkinter
#style.use('seaborn-white')

x = [0,8,-3,-8]
y = [0,8,1,-8]
color=['w','w','w','w']

fig = plt.figure()
ax1 = fig.add_subplot(111)

plt.scatter(x,y, s=100 ,marker='.', c=color,edgecolor='w')
plt.ylabel('X')
plt.xlabel('Y')
ax1.yaxis.label.set_rotation(0)
circle1=plt.Circle((0,0),5,color='r',fill=False,linewidth='4')
fig = plt.gcf()
fig.gca().add_artist(circle1)
left,right = ax1.get_xlim()
low,high = ax1.get_ylim()
plt.arrow( left, 0, right -left, 0, length_includes_head = True, head_width = 0.15 )
plt.arrow( 0, low, 0, high-low, length_includes_head = True, head_width = 0.15 )


fig = pylab.gcf()
fig.canvas.set_window_title('Inner Slip Ring')



root = Tkinter.Tk()
##.label = Tkinter.Label(text="")
w=Tkinter.Label(root, text="hello")
w.pack()
#root.mainloop()

plt.grid()
plt.show()
