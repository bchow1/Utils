# Downloaded from http://mindseye.no/2011/04/03/animating-plots-and-waves-in-python-using-matplotlib/


from matplotlib.pylab import *  # pylab is the easiest approach to any plotting
import time                     # we'll do this rendering i real time
 
ion()                           # interaction mode needs to be turned off
 
x = arange(0,2*pi,0.01)         # we'll create an x-axis from 0 to 2 pi
line, = plot(x,x)               # this is our initial plot, and does nothing
line.axes.set_ylim(-3,3)        # set the range for our plot
 
starttime = time.time()         # this is our start time
t = 0                           # this is our relative start time
 
while(t < 5.0):                 # we'll limit ourselves to 5 seconds.
                                # set this to while(True) if you want to loop forever
    t = time.time() - starttime # find out how long the script has been running
    y = -2*sin(x)*sin(t)        # just a function for a standing wave
                                # replace this with any function you want to animate
                                # for instance, y = sin(x-t)
 
    line.set_ydata(y)           # update the plot data
    draw()                      # redraw the canvas
    
    
'''
fig = figure(figsize=(16,9),dpi=80)     # create a figure in 1280 x 720 pixels
                                # this is not as simple as it could be, but
                                # it is like this because matplotlib is focused
                                # on print, not screen
 
x = arange(0,2*pi,0.01)         # we'll create an x-axis from 0 to 2 pi
line, = plot(x,x)               # this is our initial plot, and does nothing
line.axes.set_ylim(-3,3)        # set the range for our plot
 
t = 0                           # this is our relative start time
dt = 0.04
i = 0
while(t < 5.0):                 # we'll limit ourselves to 5 seconds.
                                # set this to while(True) if you want to loop forever
    y = -2*sin(x)*sin(t)        # just a function for a standing wave
                                # replace this with any function you want to animate
                                # for instance, y = sin(x-t)
 
    line.set_ydata(y)           # update the plot data
    draw()                      # redraw the canvas
 
    t = t + dt                  # increase the time
    i = i + 1                   # increase our counter
 
    # save the figure with a 4-digit number
    savefig("outdata/blah" + '%04d' % i + ".png")
'''