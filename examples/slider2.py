import numpy as np
from scipy.stats import norm, lognorm, uniform
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons, CheckButtons
import math


#####Defining global variables#####

global mu_a1
global sigma_a1
global mu_b1
global sigma_b1
global mu_c1
global sigma_c1
global ix

#####_____#####



#####Generating random data#####

mu_a1 = 1
sigma_a1 =  0.14
mu_b1 = 10
sigma_b1 =  1.16
mu_c1 = -13
sigma_c1 =  2.87
mu_x01 = -11
sigma_x01 =  1.9

a1 = 0.75*mu_a1 + (1.25 - 0.75)*sigma_a1*np.random.sample(10000)
b1 = 8*mu_b1 + (12 - 8)*sigma_b1*np.random.sample(10000)
c1 = -12*mu_c1 + 2*sigma_c1*np.random.sample(10000)
x01 = (-b1 - np.sqrt(b1**2 - (4*a1*c1)))/(2*a1)

#####_____#####



#####Creating subplots & plotting distributions#####

fig = plt.figure()
plt.subplots_adjust(left=0.13,right=0.99,bottom=0.05)

def ax1():
    ax1 = fig.add_subplot(331)
    ax1.clear()
    ax1.set_xlabel('a' , fontsize = 14)
    ax1.grid(True)
    [n1,bins1,patches] = ax1.hist(a1, bins=50, color = 'red',alpha = 0.5, normed = True)
    return ax1

def ax4_ax5():
    ax4 = fig.add_subplot(132)
    ax4.clear()
    ax4.set_xlabel('x0' , fontsize = 14)
    ax4.grid(True)
    [n4,bins4,patches] = ax4.hist(x01, bins=50, color = 'red',alpha = 0.5, normed = True)
    ax4.axvline(np.mean(x01), color = 'black', linestyle = 'dashed', lw = 2)

    ax5 = fig.add_subplot(133)
    ax5.clear()
    ax5.set_xlabel('x0' , fontsize = 14)
    ax5.set_ylabel('CDF', fontsize = 14)
    ax5.grid(True)
    dx = bins4[1] - bins4[0]
    CDF = np.cumsum(n4)*dx
    ax5.plot(bins4[1:], CDF, color = 'red')
    return ax4,ax5

#####_____#####

ax1 = ax1()
ax4, ax5 = ax4_ax5()


#####Creating Sliders#####

axcolor = 'lightgoldenrodyellow'
axmu_331 = plt.axes([0.015, 0.67, 0.07, 0.015], axisbg=axcolor)
axsigma_331 = plt.axes([0.015, 0.65, 0.07, 0.015], axisbg=axcolor)
mu_331 = Slider(axmu_331, 'M', -13.0 , 10.0, valinit = 1.0)
sigma_331 = Slider(axsigma_331, 'SD', -3.0 , 3.0, valinit =1.0)

#####_____#####



#####Updating Sliders#####

def update_slider_331(val):
    mu_a1 = mu_331.val
    print mu_a1
    sigma_a1 = sigma_331.val
    print sigma_a1
    ax1.clear()
    ax4.clear()
    ax5.clear()
    ax1.grid(True)
    ax4.grid(True)
    ax5.grid(True)
    a1 = 0.75*mu_a1 + (1.25 - 0.75)*sigma_a1*np.random.sample(10000)
    [n1,bins1,patches] = ax1.hist(a1, bins=50, color = 'red',alpha = 0.5, normed = True)
    x01 = (-b1 - np.sqrt(b1**2 - (4*a1*c1)))/(2*a1)
    [n4,bins4,patches] = ax4.hist(x01, bins=50, color = 'red',alpha = 0.5, normed = True)
    ax4.axvline(np.mean(x01), color = 'black', linestyle = 'dashed', lw = 2)
    dx = bins4[1] - bins4[0]
    CDF = np.cumsum(n4)*dx
    ax5.plot(bins4[1:], CDF, color = 'red')
    plt.draw()

mu_331.on_changed(update_slider_331)
sigma_331.on_changed(update_slider_331)

#####_____#####

plt.show()