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

#Emit scan data
emit1 = glob.glob('/u1/lcls/matlab/data/2020/2020-06/2020-06-*[21,22]/Emit*scan*')
emit2 = glob.glob('/u1/lcls/matlab/data/2020/2020-07/2020-07-*[08,09]/Emit*scan*')
emitfiles = emit1 + emit2
print('Number of emit scans', len(emitfiles))

# Make h5 file, give data description
emit_h5 = h5py.File('2020_summer_cu_inj_emit_data.h5', 'w')
emit_h5.attrs['short_description'] = 'cu inj pvs and emittance data'
emit_h5.attrs['scan_information'] = 'Emittances scans last about 1-5 minutes, the timestamp is associated with the end of the scan.'
emit_h5.attrs['step_information'] = 'Each step is taken at a different quad or solenoid value, the step number matches the index of the magnet data. There can be more than one sample per step, and several fit methods used to calculate the beam size.'

pv_list = ['IRIS:LR20:130:MOTR_ANGLE','SOLN:IN20:121:BDES',
           'QUAD:IN20:121:BDES','QUAD:IN20:122:BDES', 
           'ACCL:IN20:300:L0A_PDES','ACCL:IN20:400:L0B_PDES']

for filename in emitfiles:
    try:
        # Check file is ok get time stamp
        matstamp = check_emitscan_load(filename)
        # Convert matlab time to isotime
        pydatetime = datenum_to_datetime(matstamp)
        isotime    = pydatetime.isoformat()+'-07:00'
        
        # Save emittance data and magnet strengths
        magpv, file_group = save_emit_scan(filename, emit_h5)
        # Save pv data given time stamp
        save_pvdata_to_h5(pv_list, file_group, isotime)

        # Get pv unit for magpv
        pvname = magpv+':BCTRL'
        pv     = PV(pvname)
        pvunit = pv.get_ctrlvars()['units']

        step = file_group['beam_data']['beam_sizes']
        for group in step:
            step[group].attrs[pvname+'.EGU'] = pvunit
	
    except:
        print('could not load this file', filename)
    #    pass

emit_h5.close()




