__author__ = 'Sri Rama'
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
#from matplotlib.backend_bases import key_press_handler
import globals
import tkMessageBox
import numpy as np

class Anplot(object):
    def __init__(self,Frame,Tab):
        self.Frame    = Frame
        self.Tab      = Tab
        self.a        = 0
        self.data     = 0
        self.ax2      = 0
        self.a2       = []
        self.a3       = []
        self.xList    = []
        self.yList    = []
        self.index    = 0
        self.pullData = 0
        self.dataList = 0
        self.B1       = 0
        self.B2       = 0
        self.B3       = 0
        self.B4       = 0
        self.B5       = 0
        self.B6       = 0
        self.B7       = 0
        self.B8       = 0
        self.line1    = 0
        self._points  = 0

    #def on_key_event(self,event):
    #    key_press_handler(event, self.canvas)#, toolbar)

    def create_canvas(self):
        self.f        = Figure(figsize=(5,3.5),dpi=100,edgecolor= 'white',linewidth=2)
        self.a        = self.f.add_subplot(111)
        self.canvas   = FigureCanvasTkAgg(self.f,self.Frame)
        self.data     = globals.data_path
        self.ax2      = self.a.twiny()
        ##################################################################
        self.f.patch.set_facecolor('white')
        self.a.patch.set_visible(False)
        self.a.patch.set_edgecolor('white')
        toolbar = NavigationToolbar2TkAgg(self.f.canvas, self.Frame)
        toolbar.update()
        toolbar.place(x = 400,y = 425)
        self.f.canvas.mpl_connect('button_press_event',self.onclick)

    def onclick(self,event):
        _ix, _iy     = event.x, event.y
        ix, iy     = event.xdata, event.ydata
        _kx,_ky = self.snap(_ix,iy)
        print '_kx = %d, _ky = %d -----------------------------------------'%(_kx,_ky)
        globals.Zx = _ky
        print "globals.Zx = %f " %(globals.Zx)
        self.a.annotate(
            'point',
            xy = (_kx,_ky), xytext = (-20, 20),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        self.f.canvas.draw()

    def snap(self, x, y):
        """Return the value in self._points closest to (x, y).
        """
        #idx = np.nanargmin(((self._points - (x,y))**2).sum(axis = -1))
        #idx = np.nanargmin(((self._points - (x,y))).sum(axis = -1))
        idx = np.nanargmin(((self._points - (x,y))**2).sum(axis = -1))
        return self._points[idx]

    def show_plotXY(self):
        self.a.clear()
        self._points = np.column_stack((globals.X_val,globals.Y_val))
        self.line1, = self.a.plot(globals.X_val, globals.Y_val,'x',color = 'red')
        self.a.set_ylim(globals.Y_val[0]-100,globals.Y_val[len(globals.Y_val)-1] + 100)
        self.a.set_xlim(globals.X_val[0],globals.X_val[len(globals.X_val)-1])
        self.a.tick_params(axis='x', labelsize=7)
        self.a.set_xlabel(r"Time",fontsize=7)
        self.a.tick_params(axis='y', labelsize=7)
        self.a.set_ylabel(r"Impedence",fontsize=7)
        self.top_axis()
        self.show_animate()

    def top_axis(self):
        x = 0
        for v in globals.Z_val:
            x = x + v
            self.a2.append(x)
        self.a3 = ["BL","B1","B2","B3","B4","B5","B6","B7","B8"]
        self.ax2.set_xticks(self.a2,minor=False)
        self.ax2.set_xticklabels(self.a3)
        self.ax2.set_xlabel(r"Breaths",fontsize=7)
        self.ax2.tick_params(labelsize = 7)
        self.ax2.grid(b=True,color='r')

    def create_animate(self):
        self.create_canvas()
        self.show_plotXY()

    def show_animate(self):
        try:
            self.canvas.show()
            self.canvas.get_tk_widget().place(x=205,y=35)
            self.canvas.toolbar.place(x = 400,y = 425)
        except Exception as e:
            print "def show_animate(self):"

    def clear_animate(self):
        try:
            self.canvas.get_tk_widget().place_forget()
            self.canvas.toolbar.place_forget()
        except Exception as e:
            print "def clear_animate(self):"

    def destroy_animate(self):
        self.f.canvas.get_tk_widget().destroy()
        self.f.canvas.toolbar.destroy()

    def An_calculate(self):
        print self.a2
        globals.Z0_sum = 0
        self.index = self.a2[0]
        i = self.index
        print "index :",
        print i

        while (i > 0):
            globals.Z0_sum = globals.Z0_sum + globals.Y_val[i]
            i -= 1

        print "Z0:"
        print globals.Z0_sum

        try:
            globals.Z0 = float(float(globals.Z0_sum)/self.index)
            temp = float((globals.Zx/globals.Z0) - 1)
            globals.algoResult = round(float(str((globals.algoM))) * temp + float(str(globals.algoC)),2)
            print "globals.Zx:--",
            print globals.Zx
            print "globals.Z0:--",
            print globals.Z0
            print "temp:--",
            print temp
            print "globals.algoM:--",
            print globals.algoM
            print "globals.algoC :--",
            print globals.algoC
        except Exception as e:
            print "KISBAMBA :" ,e
            globals.algoResult = " "
            tkMessageBox.showinfo("Error", "Please select the required Algorithm")
        globals.tkl_Andisplay_result.config(text =globals.algoResult)