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
#date  = '/mccfs2/u1/lcls/matlab/data/2020/2020-06/2020-06-21/'
#solfiles  = glob.glob('/mccfs2/u1/lcls/matlab/data/2020/2020-0{6,7}/2020-0{6,7}-{21,22,8,9}/Cor*SOLN*')
#import pdb; pdb.set_trace()
#date      = '/Users/nneveu/Google Drive File Stream/Shared drives/Injector Modeling/measurements/cu_inj/2020-06-21/'
#dtype     = 'CorrelationPlot-SOLN_IN20_121_BCTRL-2020-06-21-091733.mat'
#scan_file = date+dtype

#solfiles = glob.glob('/Users/nneveu/Google Drive File Stream/Shared drives/Injector Modeling/measurements/cu_inj/2020-0*/Cor*SOLN*')

sol6 = glob.glob('/mccfs2/u1/lcls/matlab/data/2020/2020-06/2020-06-*[21,22]/Cor*SOLN*')
sol7 = glob.glob('/mccfs2/u1/lcls/matlab/data/2020/2020-07/2020-07-*[08,09]/Cor*SOLN*')

solfiles = sol6+sol7

print('Number of SOL scans', len(solfiles))
# Make h5 file, give data description
cp_h5 = h5py.File('2020_sol_data.h5', 'w')
cp_h5.attrs['information'] = 'cu inj pvs and data'

for filename in solfiles[:2]:
    try:
        # Check file is ok
        matstamp = check_corplot_load(filename)
        # Convert matlab time to isotime
        pydatetime = datenum_to_datetime(matstamp)
        isotime    = pydatetime.isoformat()+'-07:00'
        cp_group   = cp_h5.create_group('solenoid_scan_'+isotime)
        #cp_group.attrs['isotime'] = isotime
        cp_group.attrs['scan_information'] = 'Solenoid scan last about 5 minutes, the timestamp is associated with the end of the scan.'
        cp_group.attrs['step_information'] = 'Each step is taken at a different solenoid value, the step number matches the index of the solenoid data. There are five samples per step, and several fit methods used to calculate the beam size. Fit methods are used as the name of the samaple set.'
        
        #Save beam data and magnet strengths
        beam    = cp_group.create_group('beam_data')
        #import pdb; pdb.set_trace()
        save_corplot_solenoid_scan(filename, beam)
       
        # Injector PV keys
        partial_pv = ['IRIS:LR20:130:CONFG_SEL','%:IN20:%:BACT','ACCL:IN20:300:L0A_PDES','ACCL:IN20:400:L0B_PDES', 'SIOC:SYS0:ML01:CALCOUT008']
        pv_list = get_pvdata_names(partial_pv)
        
        # Save pv data given time stamp
        pv_group = cp_group.create_group('pvdata')
        save_pvdata_to_h5(pv_list, pv_group, isotime)

    except: 
        pass

cp_h5.close()





