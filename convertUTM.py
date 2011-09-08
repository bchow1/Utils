# Original from http:#www.uwgb.edu/dutchs/UsefulData/ConvertUTMNoOZ.HTM
import math
    
def DDtoDMS():
    #Input= xd(long) and yd(lat)
    #Output = xdd xm xs (long) and ydd ym ys (lat)
    ydd = math.floor(math.abs(yd))
    ym = math.floor(60*(math.abs(yd) - ydd))
    ys = 3600*(math.abs(yd)-ydd - ym/60)
    if yd < 0:
      ydd = -ydd
    xdd = math.floor(math.abs(xd))
    xm = math.floor(60*(math.abs(xd) - xdd))
    xs = 3600*(math.abs(xd)-xdd - xm/60)
    if xd < 0:
      xdd = -xdd
    #End DDtoDMS
    
def DMStoDD():
    #Input = xdd xm xs (long) and ydd ym ys (lat)
    #Output= xd(long) and yd(lat)
    xd = math.abs(xdd) + xm/60 + xs/3600
    yd = math.abs(ydd) + ym/60 + ys/3600
    if ydd < 0:
      yd = -yd
    if xdd < 0:
      xd=-xd
    #End DMStoDD

class convertUTM(object):
  
  def __init__(self,Item=0):
  
    #Symbols as used in USGS PP 1395: Map Projections - A Working Manual
    DatumEqRad = [6378137.0,6378137.0,6378137.0,6378135.0,6378160.0,6378245.0,6378206.4,
    6378388.0,6378388.0,6378249.1,6378206.4,6377563.4,6377397.2,6377276.3]
    
    DatumFlat = [298.2572236, 298.2572236, 298.2572215, 298.2597208, 298.2497323, 298.2997381, 294.9786982,
    296.9993621, 296.9993621, 293.4660167, 294.9786982, 299.3247788, 299.1527052, 300.8021499] 

    self.drad = math.pi/180.  #Convert degrees to radians)
    self.k0 = 0.9996  #scale on central meridian
    
    self.a = DatumEqRad[Item]  #equatorial radius, meters. 
    self.f = 1./DatumFlat[Item]  #polar flattening.
    self.b = self.a*(1.-self.f)  #polar radius, meters
    self.e = math.sqrt(1.-(self.b/self.a)*(self.b/self.a))  #eccentricity
    self.e0 = self.e/math.sqrt(1. - self.e*self.e)  #e prime in reference
    self.esq = 1. - (self.b/self.a)*(self.b/self.a)  #e squared for use in expansions
    self.e0sq = self.e*self.e/(1.-self.e*self.e)  # e0 squared - always even powers 

    self.latd = 0. #latitude in degrees
    #self.phi = 0  #latitude (north +, south -), but uses phi in reference
    self.lng = 0.  #Longitude (e = +, w = -) - can't use long - reserved word
    self.lng0 = 0.  #longitude of central meridian
    self.lngd = 0.  #longitude in degrees
   
    self.x = 0.  #x coordinate
    self.y = 0.  #y coordinate
    self.k = 1.  #local scale
    self.utmz = 30  #utm zone
    self.zcm = 0  #zone central meridian
    
    self.DigraphLetrsE = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    self.DigraphLetrsN = "ABCDEFGHJKLMNPQRSTUV"
    
    self.OOZok = False
    self.sHem = False  # In southern hemisphere
    #Close declarations
    
  def GeogToUTM(self):
    '''Convert Latitude and Longitude to UTM'''
    #Input Geographic Coordinates lngd, latd
    if self.latd < -90. or self.latd > 90.:
      print "Latitude must be between -90 and 90"
    if self.lngd < -180. or self.lngd > 180.:
      print "Latitude must be between -180 and 180"

    phi = self.latd*self.drad  #Convert latitude to radians
    self.lng = self.lngd*self.drad  #Convert longitude to radians
    self.utmz = 1. + math.floor((self.lngd+180.)/6.) #calculate utm zone
    self.latz = 0  #Latitude zone: A-B S of -80, C-W -80 to +72, X 72-84, Y,Z N of 84
    if self.latd > -80 and self.latd < 72:
      self.latz = math.floor((self.latd + 80)/8)+2
    if self.latd > 72 and self.latd < 84:
      self.latz = 21
    if self.latd > 84:
      self.latz = 23
        
    self.zcm = 3 + 6*(self.utmz-1) - 180 #Central meridian of zone
    
    #Calculate Intermediate Terms
  
    N = self.a/math.sqrt(1-math.pow(self.e*math.sin(phi),2))
    T = math.pow(math.tan(phi),2)
    C = self.e0sq*math.pow(math.cos(phi),2)
    A = (self.lngd-self.zcm)*self.drad*math.cos(phi)

    #Calculate M
    M = phi*(1 - self.esq*(1./4. + self.esq*(3./64. + 5.*self.esq/256.)))
    M = M - math.sin(2.*phi)*(self.esq*(3./8. + self.esq*(3./32. + 45.*self.esq/1024.)))
    M = M + math.sin(4.*phi)*(self.esq*self.esq*(15./256. + self.esq*45./1024.))
    M = M - math.sin(6.*phi)*(self.esq*self.esq*self.esq*(35./3072.))
    M = M*self.a  # Arc length along standard meridian

    M0 = 0. #M0 is M for some origin latitude other than zero. Not needed for standard UTM

    #Calculate UTM Values
    self.x = self.k0*N*A*(1. + A*A*((1.-T+C)/6. + A*A*(5. - 18.*T + T*T + 72.*C -58.*self.e0sq)/120.)) #Easting relative to CM
    self.x = self.x + 500000. #Easting standard
    self.y = self.k0*(M - M0 + N*math.tan(phi)*\
            (A*A*(1./2. + A*A*((5. - T + 9.*C + 4.*C*C)/24. + \
            A*A*(61. - 58.*T + T*T + 600.*C - 330.*self.e0sq)/720.))))#Northing from equator
    yg = self.y + 10000000. #yg = y global, from S. Pole
    if self.y < 0.:
      self.y = 10000000. + self.y
    return

  def UTMtoGeog(self):
  
    #Convert UTM Coordinates to Geographic
    
    if self.x < 160000. or self.x > 840000.:
      print "Outside permissible range of easting values \n Results may be unreliable \n Use with caution"
    if self.y < 0.:
      print "Negative values not allowed \n Results may be unreliable \n Use with caution"
    if self.y > 10000000.:
      print "Northing may not exceed 10,000,000 \n Results may be unreliable \n Use with caution"
    zcm = 3. + 6.*(self.utmz-1.) - 180. #Central meridian of zone
    e1 = (1. - math.sqrt(1. - self.e*self.e))/(1. + math.sqrt(1. - self.e*self.e)) #Called e1 in USGS PP 1395 also
    print zcm, e1
    M0 = 0. #In case origin other than zero lat - not needed for standard UTM
    M = M0 + self.y/self.k0 #Arc length along standard meridian.
    print M
    if self.sHem == True:
      M = M0+(self.y - 10000000.)/self.k
    mu = M/(self.a*(1. - self.esq*(1./4. + self.esq*(3./64. + 5.*self.esq/256.))))
    phi1 = mu + e1*(3./2. - 27.*e1*e1/32.)*math.sin(2.*mu) + e1*e1*(21./16. -55.*e1*e1/32.)*math.sin(4.*mu) #Footprint Latitude
    phi1 = phi1 + e1*e1*e1*(math.sin(6.*mu)*151./96. + e1*math.sin(8.*mu)*1097./512.)
    C1 = self.e0sq*math.pow(math.cos(phi1),2)
    T1 = math.pow(math.tan(phi1),2)
    N1 = self.a/math.sqrt(1.-math.pow(self.e*math.sin(phi1),2))
    R1 = N1*(1.-self.e*self.e)/(1.-math.pow(self.e*math.sin(phi1),2))
    D = (self.x-500000.)/(N1*self.k0)
    phi = (D*D)*(1./2. - D*D*(5. + 3.*T1 + 10.*C1 - 4.*C1*C1 - 9.*self.e0sq)/24.)
    phi = phi + math.pow(D,6)*(61. + 90.*T1 + 298.*C1 + 45.*T1*T1 -252.*self.e0sq - 3.*C1*C1)/720.
    phi = phi1 - (N1*math.tan(phi1)/R1)*phi         
    #Output Latitude
    self.latd = phi/self.drad        
    #Output Longitude
    lng = D*(1. + D*D*((-1. -2.*T1 -C1)/6. + D*D*(5. - 2.*C1 + 28.*T1 - 3.*C1*C1 +8.*self.e0sq + 24.*T1*T1)/120.))/math.cos(phi1)
    self.lngd = zcm+lng/self.drad

    return

if __name__ == '__main__':
  LLtoUTM = True
  myConvertUTM = convertUTM()
  ll2utm = raw_input('Convert from Lat Lon to UTM (y/n)? :')
  if len(ll2utm) > 0:
    if ll2utm.strip()[0].lower() == 'n':
      LLtoUTM = False
  if LLtoUTM:
    myConvertUTM.latd,myConvertUTM.lngd = map(float,raw_input('Enter Latitude, Longitude :').strip().split())
    myConvertUTM.GeogToUTM()
    print myConvertUTM.x,myConvertUTM.y,myConvertUTM.utmz
  else:
    utm = raw_input('Enter x, y, zone :').strip().split()
    myConvertUTM.x,myConvertUTM.y = map(float,utm[:2])
    myConvertUTM.utmz = float(utm[2])
    myConvertUTM.UTMtoGeog()
    print myConvertUTM.latd,myConvertUTM.lngd
    
