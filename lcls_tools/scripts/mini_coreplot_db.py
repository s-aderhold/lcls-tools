import glob
import h5py 
import numpy as np 
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
nsamples  = cpms.samples     #n samples per magnet setting
nsteps    = cpms.iterations  #number of magnet settings
pvunits   = cpms.control_dict[0]['egu'] #units for sol strength

    
# Injector PV keys
pv_names = ['IRIS:LR20:%','%:IN20:%:BACT','ACCL:IN20:300:L0A_PDES','ACCL:IN20:400:L0B_PDES', 'SIOC:SYS0:ML01:CALCOUT008']

# Make h5 file, give data description
cp_h5 = h5py.File('corplot_test.h5', 'w')
cp_h5.attrs['information'] = 'cu inj pvs and data for solenoid scan on YAG02'
cp_group = cp_h5.create_group('YAG02')

# Convert matlab time to isotime
timestamp = datenum_to_datetime(matstamp)
isotime   = get_iso_time(timestamp)
cp_group.attrs['isotime'] = isotime
cp_group.attrs['information'] = 'Solenoid scan last about 5 minutes, the timestamp is associated with the end of the scan.'

# Save pv data given time stamp
save_pvdata_to_h5(pv_names,cp_group, isotime)

# Save beam data and magnet strengths
beam    = cp_group.create_group('beam_data')
beam.attrs['information'] = 'Each step is taken at a different solenoid value, the step number matches the index of the solenoid data. There are five samples per step, and several fit methods used to calculate the beam size. Fit methods are used as the name of the samaple set.'

magdata = beam.create_dataset(ctrlpv, data = solvals)
magdata.attrs['unit'] = pvunits
magdata.attrs['information'] = 'This is the pv changed during the scan, and resulting values'

fits = ['Gaussian', 'Asymmetric', 'Super', 'RMS', 'RMS cut peak', 'RMS cut area', 'RMS floor']

for i in range(0, nsteps):
    step_data  = beam_data[i]
    step_group = beam.create_group('Step'+str(i))

    xvals = step_group.create_group('beam_sizes_x')
    yvals = step_group.create_group('beam_sizes_y')
    #import pdb; pdb.set_trace()

    for fit in range(0,len(fits)):
        xdata = []
        ydata = []
        for sample in range(0,nsamples):
            xdata.append(((step_data[sample][fit]['xStat'])[0])[2])
            ydata.append(((step_data[sample][fit]['yStat'])[0])[2])

        savex = xvals.create_dataset(fits[fit], data=np.array(xdata))
        savey = yvals.create_dataset(fits[fit], data=np.array(ydata))

        savex.attrs['unit'] = 'um'
        savey.attrs['unit'] = 'um' 
cp_h5.close()
