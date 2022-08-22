"""
Yujia Liu    yujialiu@uchicago.edu
08/19/22

Measurements of the evaporation rate of samples inside
a 96-well PCR plate (Bio-rad HSP9601).
Samples have 17.5% glycerol
"""

import numpy as np

# evaporation rate is the function of both time and
# the initial volume (which changes the surface area)
# unit: ul

def evap_vol_2h(v_0):
    
    evap_v = 0.1167 * v_0 + 0.8333
    evap_v = np.round(evap_v, 1)
    
    return evap_v

def evap_vol_4h(v_0):
    
    evap_v = 0.1867 * v_0 + 1.8667
    evap_v = np.round(evap_v, 1)
    
    return evap_v