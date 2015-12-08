"""
  This program solves the non-linear diffusion equation
    ds/dt = d/dx(s^g-1*ds/dx)
  with Neumann boundary condition
    ds(0,t) = ds(1,t) = 0
  with the Initial Conditions
    s(x,0) = Sm
  over the domain x = [0, 1]
 
  The program solves the equation using a finite difference method
  where we use a center difference method in space implicit 
  in time.
"""

import sys
import scipy as sc
import scipy.sparse as sparse
import scipy.sparse.linalg
import numpy as np
import pylab as pl
#import include.CreateMovie as movie
import matplotlib.pyplot as plt
 
surface = 'Sand'
liquid  = 'TBP' # 'TEHP', 'TCP'

# Constants
C1    = 1.3
gamma = -0.516
 
if surface == 'Sand': # Ottawa
  phi    = 0.3 # Porosity
  nCorr  = 7   # Coordination number
  alpha  = 4.*np.pi*phi/(3.*nCorr*(1-phi))
  radius = 250*1e-6  # m
  
if liquid == 'TBP':
  mu    = 3.5  # mPa.s Viscosity
  sigma = 28   # mN.m  Surface tension
elif liquid == 'TEHP':
  mu    = 15   # mPa.s Viscosity
  sigma = 29   # mN.m  Surface tension
elif liquid == 'TCP':
  mu    = 20   # mPa.s Viscosity
  sigma = 42.5 # mN.m  Surface tension    
   
if surface == 'Sand' and liquid == 'TBP':
  lScale = 3.6*1e03 # Characteristic length scale
  Sm     = 0.1      # Characteristic saturation
   
# Number of internal points
N = 101
 
# Calculate Spatial Step-Size
dx = 1/(N-1.0)
 
# Create Temporal Step-Size, TFinal, Number of Time-Steps
dt = dx/1000
TFinal = 1
NumOfTimeSteps = int(TFinal/dt)
 
# Create grid-points on x axis
x = np.linspace(0,1,N)
#x = x[1:-1]
 
# Initial Conditions

Sn  = np.zeros_like(x) + Sm
gm1 = gamma-1 

Ds  = np.zeros_like(x)
a   = np.zeros_like(x)
b   = np.zeros_like(x)
c   = np.zeros_like(x)

# Identity Matrix
I = sparse.identity(N)

N = N-1
T = np.ones((3, N+1))
# Data for each time-step
Sdata = []

plt.clf()

for i in range(NumOfTimeSteps):

  Ds = np.power(Sn,gm1)
  
  xot = (4.*dx*dx)/dt
  
  a[1:N+1] = -Ds[0:N] - Ds[1:N+1]
  b[1:N]   = xot + Ds[0:N-1] + 2.*Ds[1:N] + Ds[2:N+1] 
  c[0:N]   = -Ds[0:N] - Ds[1:N+1] 
  
  a[0] = 0
  b[0] = xot +  Ds[2] 
  
  b[N] =  xot + Ds[N-1] 
  c[N] = -Ds[N]
  
  #print a
  #print b
  #print c
     
  # Second-Derivative Matrix
  T[0] = a
  T[1] = b
  T[2] = c
  diags = [-1,0,1]
  A = sparse.spdiags(T,diags,N+1,N+1)
  B = np.zeros_like(x)
  B[1:N] =  (Ds[0:N-1] + Ds[1:N])*Sn[0:N-1] + (xot - Ds[0:N-1] - 2.*Ds[1:N] - Ds[2:N+1])*Sn[1:N] +  (Ds[1:N] + Ds[2:N+1])*Sn[2:N+1]
  B[0]   =  (xot - Ds[1] - Ds[2])*Sn[1] +  (Ds[1] + Ds[2])*Sn[2]
  B[N]   = (Ds[N-1] + Ds[N])*Sn[N-1] + (xot - Ds[N-1] - Ds[N])*Sn[N]
  #print A.toarray()
  
  # Solve the System: Ax = B
  Sn1 = np.transpose(np.mat( sparse.linalg.spsolve( A, B ) ))
 
  print Sn1
  # Save Data
  Sdata.append(Sn1)
  Sn = np.ravel(Sn1)
  
  
  plt.plot(Sn/Sm,x)
  plt.title('Time = %g'%(i*dt))
  plt.xlabel('S/Sm (Normalized Saturation)')
  plt.ylabel('x/L ( Normalized Distance)')
  plt.savefig('Sat%03d.png'%i)
  #plt.show()


#plt.plot(x, data[int(NumOfTimeSteps*frame/(FPS*MovieLength))] )
#plt.axis((0,1,0,10.1))