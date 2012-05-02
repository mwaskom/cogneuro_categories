"""Hold information about different monitors. Use the dict format outlined below.""" 
from textwrap import dedent

cni_lcd = dict(monitor_name='cni_lcd', 
               calib_file='calib/cni_lums_20110718.csv', # photometer data calculated
               # from Franco's calibration data.
               calib_date='20110718',  
               width=25.5, # in cm
               distance=190, # viewing distance in cm
               size=[2560, 1600],  # in pixels
               notes=dedent("""
               Parameters taken from the CNI wiki:
               http://cni.stanford.edu/wiki/MR_Hardware#Flat_Panel. 
               Accessed on 8/9/2011.
               """)
                 )

mlw_mbpro = dict(monitor_name='mlw-mbpro',
                 width=33.2,
                 size=[1400, 900],
                 distance=63,
                 notes="")

ben_octocore = dict(monitor_name='ben-octocore',
                    width=43.5,
                    size=[1680, 1050],
                    distance=60,
                    notes=dedent("""Horizontal monitor on the Mac Pro
                                 in MLW's office."""))
