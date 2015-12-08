# Example from http://stackoverflow.com/questions/3554241/how-to-embed-this-matplotlib-code-into-tkinter-canvas
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np


try:
    import Tkinter as Tk
except ImportError:
    import tkinter as Tk


class Scope:
    def __init__(self, ax, maxt=10, dt=0.01):
        self.ax = ax
        self.canvas = ax.figure.canvas
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.ydata = [0]
        self.line = Line2D(self.tdata, self.ydata, animated=True)
        self.ax.add_line(self.line)
        self.background = None
        self.canvas.mpl_connect('draw_event', self.update_background)
        self.ax.set_ylim(-.1, 1.1)
        self.ax.set_xlim(0, self.maxt)

    def update_background(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def emitter(self, p=0.01):
        'return a random value with probability p, else 0'
        v = np.random.rand(1)
        if v>p: return 0.
        else: return np.random.rand(1)

    def update_view(self, *args):
        if self.background is None: return True
        y = self.emitter()
        lastt = self.tdata[-1]
        if lastt>self.tdata[0]+self.maxt:
            self.tdata = [self.tdata[-1]]
            self.ydata = [self.ydata[-1]]
            self.ax.set_xlim(self.tdata[0], self.tdata[0]+self.maxt)
            self.ax.figure.canvas.draw()

        self.canvas.restore_region(self.background)

        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.ydata.append(y)
        self.line.set_data(self.tdata, self.ydata)
        self.ax.draw_artist(self.line)

        self.canvas.blit(self.ax.bbox)
        self.canvas.get_tk_widget().after(25, self.update_view) # ***important
        return True


root = Tk.Tk()

f = Figure()
ax = f.add_subplot(111)

canvas = FigureCanvasTkAgg(f, master=root)
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
canvas.show()

toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
toolbar.update()

button = Tk.Button(master=root, text='Quit', command=root.destroy)
button.pack(side=Tk.BOTTOM)

scope = Scope(ax)
root.after(50, scope.update_view)
root.mainloop()