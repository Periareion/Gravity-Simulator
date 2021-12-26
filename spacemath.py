"""

"""

from astropy.constants import G, M_sun
from scipy.special import jv
import numpy as np

import time

# Current Time
t = time.time()

def kep_to_cart(mu,a,e,i,lon_AN,lon_Pe,ML,t=time.time(),Epoch=60*60*24*365.25*30):
    
    arg_Pe = lon_Pe - lon_AN
    
    n = np.sqrt(mu/(a**3))
    M = ML - lon_Pe + n*(t-Epoch)
    
    # EA: eccentric anomaly
    EA = M
    for k in range(1,24):
        EA += 2/k*jv(k,k*e)*np.sin(k*M)
    
    # nu: true anomaly
    nu = 2*np.arctan(np.sqrt((1+e)/(1-e)) * np.tan(EA/2))
    
    r = a*(1 - e*np.cos(EA))
    
    p = a*(1-e**2)
    
    h = np.sqrt(mu*p)

    Om = lon_AN
    w =  arg_Pe

    X = r*(np.cos(Om)*np.cos(w+nu) - np.sin(Om)*np.sin(w+nu)*np.cos(i))
    Y = r*(np.sin(Om)*np.cos(w+nu) + np.cos(Om)*np.sin(w+nu)*np.cos(i))
    Z = r*(np.sin(i)*np.sin(w+nu))

    V_X = (X*h*e/(r*p))*np.sin(nu) - (h/r)*(np.cos(Om)*np.sin(w+nu) + np.sin(Om)*np.cos(w+nu)*np.cos(i))
    V_Y = (Y*h*e/(r*p))*np.sin(nu) - (h/r)*(np.sin(Om)*np.sin(w+nu) - np.cos(Om)*np.cos(w+nu)*np.cos(i))
    V_Z = (Z*h*e/(r*p))*np.sin(nu) + (h/r)*(np.cos(w+nu)*np.sin(i))

    return [X,Y,Z],[V_X,V_Y,V_Z]
