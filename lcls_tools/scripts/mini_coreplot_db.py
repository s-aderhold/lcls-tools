import glob
import h5py 
import numpy 
import sys
sys.path.append('/nfs/slac/staas/fs1/g/accelerator_modeling/nneveu/lcls-tools/lcls_tools/cor_plot')
sys.path.append('../image_processing')
sys.path.append('../data_analysis')

from cor_plot_mat_scan import CorPlotMatScan as CPMS
from mat_image import MatImage as MI
from archiver import get_iso_time, datenum_to_datetime, save_mat_image_to_h5, save_pvdata_to_h5

#Correlation plot scan data
date  = '/mccfs2/u1/lcls/matlab/data/2020/2020-06/2020-06-21/'
dtype = 'CorrelationPlot-SOLN_IN20_121_BCTRL-2020-06-21-091733.mat'

# Load correlation plot data
cpms      = CPMS(date+dtype)
ctrlpv    = cpms.ctrl_pv
solvals   = cpms.ctrl_vals
matstamp  = cpms.timestamp
beam_data = cpms.beam

# Injector PV keys
pv_names = ['IRIS:LR20:%','%:IN20:%:BACT','ACCL:IN20:*00:L0%','SIOC:SYS0:ML01:CALCOUT008']

# Make h5 file, give data description
cp_h5 = h5py.File('corplot_test.h5', 'w')
cp_h5.attrs['information'] = 'cu inj pvs and data for solenoid scan on YAG02'
cp_group = cp_h5.create_group('YAG02')

# Convert matlab time to isotime
timestamp = datenum_to_datetime(matstamp)
isotime   = get_iso_time(timestamp)
cp_group.attrs['isotime'] = isotime

# Save pv data given time stamp
save_pvdata_to_h5(pv_names,cp_group, isotime)

# Save beam data and magnet strengths
beam = cp_group.create_group('beam_data')
beam.create_dataset('magnet_strengths', data = solvals)

fits = ['Gaussian', 'Asymmetric', 'Super', 'RMS', 'RMS cut peak', 'RMS cut area', 'RMS floor']

for i in range(len(solvals)):
    step_data  = beam_data[i]
    step_group = beam.create_group('solval='+str(solvals(i)))
    #import pdb; pdb.set_trace()

    for n in range(len(step_data)):
        sample = step_group.create_group('sample'+str(n))
        for j, fit in enumerate(fits):
            sample.create_dataset(fit+'_xStat', data = step_data[n][j]['xStat'])
            sample.create_dataset(fit+'_yStat', data = step_data[n][j]['yStat'])

cp_h5.close()
