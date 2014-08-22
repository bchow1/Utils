#Python rewrite of 'DEM2XYZ.C' which isn't a friendly compile
# slower than C, sure. But it should work on Win and UNIX without any hassles.
#if this reads like a C program you know why. Sorry ;)

####
## from 'DEM2XYZ6.ZIP pulled from ftp.blm.gov
#
# Origional Header comments:
# convert dem to x, y, z format, one dem profile at a time,
# converts 3 arc second to lat/long, sol katz, mar. 94,
# added sampling and cutting to size, sol katz, apr 94
# changed the calculation of start position in sampling code,
# sol katz, jan 95
# ver 4, got rid of last 160 bytes on header line. sol katz, mar97

class DEM:
  mapLabel = None
  DEMlevel = None
  elevationPattern = None
  groundSystem = None
  groundZone = None
  projectParams = []
  planeUnitOfMeasure = None
  elevUnitOfMeasure = None
  polygonSizes = None
  groundCoords = {}
  elevBounds = None
  localRotation = None
  accuracyCode = None

#((),(),())
spatialResolution = ()

profileDimension = None
unknownA = None
unknownB = None
unknownC = None
unknownD = None
unknownE = None
unknownF = None
unknownG = None
unknownH = None

colStr = 0
def writeNormal(self, oh, XCoord, YCoord):
  if self.spatialResolution[1] == 3.0:
  #3 degrees of arc
  XCoord = XCoord / 3600.0
  YCoord = YCoord / 3600.0
  
  self.cellCount = 0
  
  for r in range(self.firstRow, self.lastRow, self.rowInt):
  #scale the raw value
  tempFloat = float(self.base[r]) * self.verticalScale
  oh.write("%f %f %i\n" % (XCoord, YCoord, int(tempFloat)))
  self.cellCount += 1
  #move up the delta y distance
  YCoord += self.deltaY
  return None

def writeSubset(self, oh, XCoord, YCoord):
return None

def getheader(self, fh):
print ""
self.mapLabel = fh.read(144)
print "Map label: %s" % self.mapLabel

self.DEMlevel = int(fh.read(6))
print "DEMlevel: %i" % self.DEMlevel

self.elevationPattern = int(fh.read(6))
print "elevation Pattern: %i" % self.elevationPattern

self.groundSystem = int(fh.read(6))
print "planimetric reference system: %i" % self.groundSystem

self.groundZone = int(fh.read(6))
print "ground Zone: %i" % self.groundZone

#pull off 15, 24 byte sections and store in projectParams list
for k in range(5):
for l in range(3):
value = fh.read(24)
#we need to handle the exponent.. a simple float()
ain't doing the trick.
self.projectParams.append(float(value.replace("D",
"E")))
print "proj: %15.7f %15.7f %15.7f" % (self.projectParams[-3],
self.projectParams[-2], self.projectParams[-1])

self.planeUnitOfMeasure = int(fh.read(6))
print "plane Unit Of Measure: %i" % self.planeUnitOfMeasure

self.elevUnitOfMeasure = int(fh.read(6))
print "elevation measurement units code: %i" %
self.elevUnitOfMeasure

self.polygonSizes = int(fh.read(6))
print "polygon Sides: %i" % self.polygonSizes

#nested list, ((lat,lng),(lat,lng),(lat,lng),(lat,lng))
for k in ["NW", "NE", "SW", "SE"]:
#NW, NE, SW, SE
lat = float(fh.read(24).replace("D", "E"))
lng = float(fh.read(24).replace("D", "E"))

self.groundCoords[k] = (lat, lng)
print "%s (%15.5f, %15.5f)" % (k, lat, lng)

self.elevBounds = (
float(fh.read(24).replace("D", "E")),
float(fh.read(24).replace("D", "E"))
)

self.localRotation = float(fh.read(24).replace("D", "E"))

self.accuracyCode = fh.read(6)
print "Min: %15.5f, Max: %15.5f, Accuracy Code: %s" %
(self.elevBounds[0], self.elevBounds[1], self.accuracyCode)

self.spatialResolution = (
float(fh.read(12)),
float(fh.read(12)),
float(fh.read(12))
)

print "Spatial Resolution: %15.5f, %15.5f, %15.5f" %
(self.spatialResolution[0],

self.spatialResolution[1],

self.spatialResolution[2]
)

self.profileDimension = (
int(fh.read(6)),
int(fh.read(6))
)
print "map size is %i x %i" % (self.profileDimension[0],
self.profileDimension[1])
#dump the next 160 bytes
self.unknownA = fh.read(6)
self.unknownB = fh.read(16)
self.unknownC = fh.read(2)
self.unknownD = fh.read(2)
self.unknownE = fh.read(2)
self.unknownF = fh.read(4)
self.unknownG = fh.read(4)
self.unknownH = fh.read(124)

return None

def processProfiles(self, fh, oh):
lastProfile = 0
for c in range(self.columnCount):
print "Working on column %s" % c
current, next = fh.read(6), fh.read(6)
try:
profileID = {"current": int(current), "next":
int(next)}
except:
raise "Failed: %s, %s" % (repr(current), repr(next))

print repr(profileID)
#profileID = (fh.read(6), int(fh.read(6)))
profileSize = {"alpha": int(fh.read(6)), "beta":
fh.read(6)}
print repr(profileSize)
#profileSize = (int(fh.read(6)), int(fh.read(6)))

planCoords = (
float(fh.read(24).replace("D", "E")),
float(fh.read(24).replace("D", "E")),
)
print "planCoords: %15.5f, %15.5f" % planCoords

localElevation = float(fh.read(24).replace("D", "E"))
elevExtremea = (
float(fh.read(24).replace("D", "E")),
float(fh.read(24).replace("D", "E"))
)

#'kludge to force the end of processing'???
#if (profileID["current"] - 1) != lastProfile:
# print "%s - 1 != %s" % (profileID["current"],
lastProfile)
# print "%i lines were written to the file" %
self.cellCount
# return None

lastProfile = profileID["next"]
print "Column %i has %i rows" % (profileID["next"],
profileSize["alpha"])
self.firstRow = int(planCoords[1] - self.southMostSample) /
self.spatialResolution[1]

self.lastRow = self.firstRow + profileSize["alpha"]

#skip ahead to the first row
self.base = []
for r in range(self.firstRow):
self.base.append(0)

for r in range(self.firstRow, self.lastRow):
value = fh.read(6)
print self.firstRow, r, self.lastRow, repr(value)
try:
self.base.append(int(value))
except:
raise "the horrors of war!"
#self.base.append(int(fh.read(3)))

#if cutting out a section, adjust the rows
if outType == 2:
#subset
self.firstRow = rowStr
planCoords[1] = planCoords[1] + (self.firstRow - 1) *
self.deltaY
lastRow = max(lastRow, rowEnd)

mod = c % colInt
if mod == 0 and c >= self.colStr:
if outType == 2:
writeSubset(oh, planCoords[0], planCoords[1])
else:
D.writeNormal(oh, planCoords[0], planCoords[1])

#trailer bytes?
#fh.read(424)

return None

YMAX = 2048
XMAX = 2048
SW = 0
NW = 1
NE = 2
SE = 3

infile = "/home/jkane/pypov-0.0.2/rawdata/1843.CDO"

print "DEM to x,y,z ascii file, Python variation based on C version 6"
print " Python version by Jason Kane, BroadLink Communications 2004"
print " C version by Sol Katz, BLM April 1997"

fh = open(infile)
D = DEM()
D.getheader(fh)

D.verticalScale = 1.0

#easy enough...
if D.spatialResolution[0] == 3.0:
comp = 2.0
D.deltaY = D.spatialResolution[0] / 3600
else:
comp = 0.0
D.deltaY = D.spatialResolution[0]

D.eastMost = max(D.groundCoords["NE"][0], D.groundCoords["SE"][0])
D.westMost = min(D.groundCoords["NW"][0], D.groundCoords["SW"][0])
D.northMost = max(D.groundCoords["NE"][1], D.groundCoords["NW"][1])
D.southMost = min(D.groundCoords["SW"][1], D.groundCoords["SE"][1])

#trunc' up to nearest spatialResolution
D.eastMostSample = int(D.eastMost / D.spatialResolution[0]) *
int(D.spatialResolution[0])
D.westMostSample = int((D.westMost + comp) / D.spatialResolution[0]) *
int(D.spatialResolution[0])
D.northMostSample = int(D.northMost / D.spatialResolution[1]) *
int(D.spatialResolution[1])
D.southMostSample = int((D.southMost + comp) / D.spatialResolution[1])
* int(D.spatialResolution[1])

if D.spatialResolution == 3.0:
#it's a 1x1 degree DEM
print "eastMostSample: %10f, westMostSample: %10f" %
(D.eastMostSample / 3600, D.westMostSample / 3600)
print "northMostSample: %10f, southMostSample: %10f" %
(D.northMostSample / 3600, D.southMostSample / 3600)

D.columnCount = (D.eastMostSample - D.westMostSample) /
int(D.spatialResolution[0]) + 1
D.rowCount = (D.northMostSample - D.southMostSample) /
int(D.spatialResolution[1]) + 1

if D.columnCount != D.profileDimension[1]:
print "CALCULATED column Count %i != HEADER %i" % (D.columnCount,
D.profileDimension[1])
print "will use SMALLER column Count"
D.columnCount = min(D.profileDimension[1], D.columnCount)

print "number of rows %i, number of columns %i" % (D.rowCount,
D.columnCount)
colInt = 1
D.rowInt = 1
outType = input("Enter 0 for all, 1 for samples, 2 for subset : ")

if outType == 1:
#samples
colInt = input("Enter Column sample interval : ")
D.rowInt = input("Enter row sample interval : ")
D.deltaY = D.deltaY * D.rowInt

elif outType == 2:
#subset
D.colStr = input("Enter start column (from left) : ")
colEnd = input("Enter end column (from left) : ")
rowStr = input("Enter start row (from bottom) : ")
rowEnd = input("Enter end row (from bottom) : ")

D.verticalScale = input("Enter a vertical scaling factor: ")

if (outType == 2 and D.columnCount > colEnd):
D.columnCount = colEnd

outfile = "outfile.xyz"
oh = open(outfile, "w")

D.processProfiles(fh, oh)

print "%i lines were written to the file." % D.cellCount