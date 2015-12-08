#http://jkwiens.com/2010/01/02/creating-movies-with-pyplotpylab/
import CreateMovie as movie
import matplotlib.pyplot as plt
import numpy as np

 
x = np.linspace(-.5,4,500)
 
# Plots a given frame
def plotFunction( frame ):
	plt.plot(x, np.exp( -10*(x - frame/10.0)**2) )

	plt.axis((-.5,4,0,1.1))
 
movie.CreateMovie(plotFunction, 50)