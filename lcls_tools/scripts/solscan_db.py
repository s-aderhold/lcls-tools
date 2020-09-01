import glob
import h5py
import numpy as np
import sys
import glob
from datetime import datetime, timedelta, timezone

sys.path.append('../image_processing')
sys.path.append('../data_analysis')
sys.path.append('../cor_plot')
sys.path.append('../emit_scan')

import meme
from epics import PV
from archiver import * 
from dataset import *

#Correlation plot scan data
#solfiles  = glob.glob('/mccfs2/u1/lcls/matlab/data/2020/2020-0{6,7}/2020-0{6,7}-{21,22,8,9}/Cor*SOLN*')
#solfiles = glob.glob('/Users/nneveu/Google Drive File Stream/Shared drives/Injector Modeling/measurements/cu_inj/2020-0*/Cor*SOLN*')

print('Number of SOL scans', len(solfiles))
# Make h5 file, give data description
cp_h5 = h5py.File('2020_sol_data.h5', 'w')
cp_h5.attrs['short_description'] = 'cu inj pvs and data'
cp_h5.attrs['scan_information'] = 'Solenoid scan last about 5 minutes, the timestamp is associated with the end of the scan.'
cp_h5.attrs['step_information'] = 'Each step is taken at a different solenoid value, the step number matches the index of the solenoid data. There are five samples per step, and several fit methods used to calculate the beam size. Fit methods are used as the name of the samaple set.'
 

pv_list = ['IRIS:LR20:130:MOTR_ANGLE','SOLN:IN20:121:BDES',
          'QUAD:IN20:121:BDES','QUAD:IN20:122:BDES', 
          'ACCL:IN20:300:L0A_PDES','ACCL:IN20:400:L0B_PDES']

for filename in solfiles:
    try:
        # Check file is ok
        matstamp = check_corplot_load(filename)
       
        #Save beam data and magnet strengths
        #beam    = cp_group.create_group('beam_data')
        save_corplot_solenoid_scan(filename, cp_h5)
        
        # Injector PV keys
        #pv_list = get_pvdata_names(partial_pv)
        
        # Save pv data given time stamp
        #save_pvdata_to_h5(pv_list, cp_group, isotime)
    except:
        print('Unable to save data from:', filename)

cp_h5.close()





