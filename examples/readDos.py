#!/usr/bin/env python2.7
import os
#import matplotlib
#matplotlib.use('Agg')
#from matplotlib.mlab import griddata
#import matplotlib.pyplot as plt
import numpy as np
import struct

class FortranBinReader:
	def __init__(self, filename, recordlength):
		self.recordlength = recordlength
		self.bytesread = 0
		self.fp = open(filename, 'rb')

	# note that __del__ is called when __init__ fails, so this doesn't 
	# quite capture what we want...
	def __del__(self):
		self.fp.close()

	def nextrecord(self):
		self.fp.read(self.recordlength-self.bytesread)
		self.bytesread = 0

	def readstring(self, length):
		self.bytesread += length
		return(self.fp.read(length))

	def readint(self):
		self.bytesread += 4
		return(struct.unpack('=i', self.fp.read(4))[0])

	def readfloat(self):
		self.bytesread += 4
		return(struct.unpack('=f', self.fp.read(4))[0])

class QuadTree:
	def __init__(self, nx, ny, vals, refs):
		# at the coarsest level of refinement, the quadtree is just a nx by ny grid.
		self.nx = nx
		self.ny = ny
		# first we'll build the quadtree in a linear array, then map it to 2D coordinates
		self.tree = np.zeros(nx*ny, dtype=object)

		# the input is the quadtree specified in the linked-list structure that SCIPUFF uses
		def buildnode(val, ref):
			if ref == -1:
				return val
			else:
				# nodes in the quadtree are 2x2 grids, with Fortran ordering
				return np.array([[buildnode(vals[ref], refs[ref]), buildnode(vals[ref+2], refs[ref+2])],
								 [buildnode(vals[ref+1], refs[ref+1]), buildnode(vals[ref+3], refs[ref+3])]], dtype=object)

		# build the tree, recursively
		for i in range(nx*ny):
			self.tree[i] = buildnode(vals[i], refs[i])

		# make the tree 2D, remembering the data we read in is Fortran ordered
		self.tree = self.tree.reshape((self.nx, self.ny), order='F')

	# value at a node in the quad tree
	# if it's a number, return that number; if it's a grid, return the average of the grid
	def val(self, elem):
		if type(elem) == np.float64 or type(elem) == np.float32 or type(elem) == np.float or type(elem) == float:
			return(elem)
		else:
			return(0.25*(self.val(elem[0,0])+self.val(elem[1,0])+self.val(elem[0,1])+self.val(elem[1,1])))

	# for the grid with refinement level "level," determine the location 
	# of element (i,j) in the tree
	def treeloc(self, i, j, level):
		mylev = level
		loc = [(i,j)]
		while mylev > 0:
			I = int(np.floor(loc[0][0]/2.0))
			J = int(np.floor(loc[0][1]/2.0))
			dI = int(np.ceil(loc[0][0]/2.0))-I
			dJ = int(np.ceil(loc[0][1]/2.0))-J
			loc[0] = (I, J)
			loc.insert(1, (dI, dJ))
			mylev -= 1
		return(loc)

	# return the value at the node specified by loc
	def getval(self, loc):
		elem = self.tree
		while len(loc) > 0:
			if type(elem) == np.ndarray:
				elem = elem[loc.pop(0)]
			else:
				return(elem)
		return(self.val(elem))

	# create the grid at the specified level of refinement; level=0 is the coarsest
	def getgrid(self, level):
		grid = np.zeros((self.nx*2**level,self.ny*2**level), dtype=float, order='F')

		for i in range(grid.shape[0]):
			for j in range(grid.shape[1]):
				loc = self.treeloc(i, j, level)
				grid[i,j] = self.getval(loc)

		return(grid)		

if __name__ == '__main__':
	# Biswanath: these are the user-definable parameters
	# dosage filename
	os.chdir('/home/user/bnc/hpac/runs/hill')
	dosfilename = 'hill.dos'
	# time slice to extract (numbering is 0-based)
	timeslicenumber = 9
	# grid refinement level; 0=original 10x10 grid, 1=20x20 grid, ...
	# general grid size is 10*2**refinementlevel by 10*2**refinementlevel
	refinementlevel = 4	

	dosfile = FortranBinReader(dosfilename, 512*4)

	# metadata
	file_type = dosfile.readstring(13)
	nblk = dosfile.readint()
	iversion = dosfile.readint()

	# more metadata; note that below we assume there is only one block
	blk_name = []
	ifield = []
	nfield = []
	iaux = []
	for i in range(nblk):
		dosfile.nextrecord()
		blk_name.append(dosfile.readstring(64))
		ifield.append(dosfile.readint())
		nfield.append(dosfile.readint())
		iaux.append(dosfile.readint())

	# how many variables in the field?
	dosfile.nextrecord()
	nvar = dosfile.readint()

	# and what are their names?
	names = []
	for i in range(nvar):
		names.append(dosfile.readstring(4))

	print names

	# loop over time slices
	time = []
	ngrid = []
	nx = []
	ny = []
	xorg = []
	yorg = []
	dx = []
	dy = []
	mlev = []
	iref = []
	fields = []

	# timebreak header
	dosfile.nextrecord()
	thistime = dosfile.readfloat()
	thisngrid = dosfile.readint()
	thisnx = dosfile.readint()
	thisny = dosfile.readint()
	thisxorg = dosfile.readfloat()
	thisyorg = dosfile.readfloat()
	thisdx = dosfile.readfloat()
	thisdy = dosfile.readfloat()
	thismlev = dosfile.readint()

	while thisngrid > 0:
		time.append(thistime)
		ngrid.append(thisngrid)
		nx.append(thisnx)
		ny.append(thisny)
		xorg.append(thisxorg)
		yorg.append(thisyorg)
		dx.append(thisdx)
		dy.append(thisdy)
		mlev.append(thismlev)

		# grid index array
		thisiref = np.zeros(thisngrid, dtype=int)
		for i in range(thisngrid/128+1):
			jmax = min((i+1)*128, thisngrid)
			dosfile.nextrecord()
			for j in range(i*128,jmax):
				thisiref[j] = dosfile.readint() - 1
		iref.append(thisiref)

		# field data
		thisfields = np.zeros((thisngrid,nvar), dtype=float)
		for var in range(nvar):
			for i in range(thisngrid/128+1):
				jmax = min((i+1)*128, thisngrid)
				dosfile.nextrecord()
				for j in range(i*128,jmax):
					thisfields[j,var] = dosfile.readfloat()
		fields.append(thisfields)

		# timebreak header
		dosfile.nextrecord()
		thistime = dosfile.readfloat()
		thisngrid = dosfile.readint()
		thisnx = dosfile.readint()
		thisny = dosfile.readint()
		thisxorg = dosfile.readfloat()
		thisyorg = dosfile.readfloat()
		thisdx = dosfile.readfloat()
		thisdy = dosfile.readfloat()
		thismlev = dosfile.readint()

	print 'found', len(time), 'time slices:', time
	print 'ngrid:', ngrid

	k = timeslicenumber

	print time[k], ngrid[k], nx[k], ny[k], xorg[k], yorg[k], dx[k], dy[k], mlev[k]

	tree = QuadTree(nx[k], ny[k], fields[k][:,0], iref[k])
	grid = tree.getgrid(refinementlevel)

	for j in range(grid.shape[1]):
		for i in range(grid.shape[0]):
			print '%.3g'%grid[i,j],
		print

	#plotdata = np.log10(grid[0:grid.shape[0], grid.shape[1]/2-grid.shape[1]/10:grid.shape[1]/2+grid.shape[1]/10])
	#plotdata = np.log10(grid)

	# make a plot
	#fig = plt.figure()
	#ax = fig.add_subplot(111)
	#ax.grid(True)

	#cax = ax.imshow(plotdata.transpose(), origin='lower', vmin=-6.0, vmax=1.0)
	#cbar = fig.colorbar(cax, shrink=0.5)

	#ax.set_title('dosage')
	#plt.xlabel('x')
	#plt.ylabel('y')
	#outfile = 'test.pdf'
	#plt.savefig(outfile)
	#plt.clf()



