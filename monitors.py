"""
Hold information about different monitors. Use the dict format outlined below. 

""" 
monitors = [dict(monitor_name='cni_lcd', 
                 calib_file='cni_lums_20110718.csv', # photometer data calculated
                 # from Franco's calibration data.
                 calib_date='20110718',  
                 width=25.5, # in cm
                 distance=190, # viewing distance in cm
                 size=[2560, 1600],  # in pixels
                 notes="""
                 Parameters taken from the CNI wiki:
                 http://cni.stanford.edu/wiki/MR_Hardware#Flat_Panel. 
                 Accessed on 8/9/2011.
                 """
                 ),
             dict(monitor_name='mlw-mbpro',
                  width=33.2,
                  size=[1400, 900],
                  distance=63,
                  notes="")
             ]
