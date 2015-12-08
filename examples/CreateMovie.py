# http://jkwiens.com/2010/01/02/creating-movies-with-pyplotpylab/
def CreateMovie(plotter, numberOfFrames, fps=10):
	import os, sys

	import matplotlib.pyplot as plt
 
	for i in range(numberOfFrames):
		plotter(i)

		fname = '_tmp%05d.png'%i
 
		plt.savefig(fname)
		plt.clf()
 
	os.system("rm movie.mp4")

	os.system("ffmpeg -r "+str(fps)+" -b 1800 -i _tmp%05d.png movie.mp4")
	os.system("rm _tmp*.png")