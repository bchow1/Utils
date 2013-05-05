# Problem 1.3 Cutlip and Shacham ( www.engineeringwithpython.com, prob13)

# Import packages to help with solutions 

from scipy import * 
from scipy.optimize import * 
from scipy.stats import *
from matplotlib import * 
from pylab import * 

#Input the experimental Vapor Pressure and Temperature data as numpy arrays

vp = array([ 1.0 , 5.0, 10.0, 20.0, 40.0, 60.0, 100.0, 200.0, 400.0, 760.0], dtype=float)
vp_mean = mean(vp)

T = array([-36.7 , -19.6 , -11.5 , -2.6 , 7.6 , 15.4 , 26.1 , 42.2 , 60.6, 80.1], dtype=float)

# Fit data to a 3rd order polynomial
pf = polyfit(T,vp,3)
print 'p3 =' , poly1d( pf)

# Plot the data fit
figure()
plot(T,vp,'o')
xlabel = 'Temperature'
ylabel = 'Vapor Pressure'
#legend(['T',vp'])

plot(T,polyval(pf,T) ,'r-')
legend(['vp data','data fit'],'best')
title( 'Third Order Polynomial Fit')


# Calculate the cumulative error
A,B,C,D = pf
vp_calc = A*T**3 + B*T**2 + C*T + D

sse_3 = (vp - vp_calc )**2
print 'sse_3 =',sum(sse_3)

# Calculate the R^2 value
vp3_est = (vp_calc - vp_mean)**2
vp3 = (vp - vp_mean)**2
R2_vp3 = sum(vp3_est)/sum(vp3)
print 'R2_vp3 = ',R2_vp3

#Define a linear transformation or data: log_vp = log(vp)
#and T_k = 1/(T + 273 . 15)

log_vp = array(log(vp) , dtype=float)
log_vp_mean = mean(log_vp)
T_k = array(1/(T + 273.15), dtype=float)

pf_log = polyfit(T_k,log_vp,1)

A,B = pf_log
vp_calc_l = A*T_k + B

sse_log = (log(vp) - vp_calc_l)**2
print ' sse_log =' ,sum( sse_log )

# Calculate the R^2 value for linear fit

log_vp_est  = (vp_calc_l - log_vp_mean)**2
log_vp_meas = (log_vp - log_vp_mean)**2
R2_log_vp   = sum(log_vp_est )/sum(log_vp_meas)
print 'R2_log_vp = ' ,R2_log_vp

# Plot the data fit

figure()
plot(T_k,log_vp,' o ')
xlabel = '1/T'
ylabel = 'Log Vapor Pressure'
plot(T_k,polyval(pf_log,T_k),'r-')
legend(['Log(vp data)','Transtormed data fit'],'best' )
title('First Order Polynomial Fit of Transformed Data')
plt.show()

#Use an Antione equation to fit the data

pO = [10.0, 2000.0 , 273.15]

def residual(p,y,T):
  A,B,C = p
  ant_vp_calc = A - B/( T + C)
  err = y - ant_vp_calc
  return err

def ant_vp_eval(T,p):
  A,B,C = p
  return A - B/(T + C)

plsq = leastsq(residual,pO,args=(log_vp,T))
print 'Antione Coefficients'
print 'A= ', plsq[0][0],', B =' , plsq[0][1],', C = ' , plsq[0][2]

A,B,C = plsq[0]
ant_vp_calc =  A - B/( T + C)

sse_ant = (log_vp - ant_vp_calc)**2
print 'sse_ant = ',sum(sse_ant)

# Calculate the R^2 value for Antoine Fit

ant_vp_est  = (ant_vp_calc - log_vp_mean)**2
ant_vp_meas = (log_vp - log_vp_mean)**2
R2_ant_vp = sum(ant_vp_est)/sum( ant_vp_meas)
print 'R2_ant_vp = ' , R2_ant_vp

#Plot the Antione Equation Fit
figure()
plot(T,log_vp,'o')
xlabel= 'T'
ylabel = 'Log Vapor Pressure'
plot(T,ant_vp_eval(T,plsq[0]),'r-')
legend(['Log(vp data)','Antoine data fit'],'best' )
title( 'Least Squares fit of Antoine Coefficients')
plt.show()
