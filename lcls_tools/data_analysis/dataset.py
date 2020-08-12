import numpy as np
from cor_plot_mat_scan import CorPlotMatScan as CPMS
from archiver import *

FITS = ['Gaussian', 'Asymmetric', 'Super', 'RMS', 'RMS cut peak', 'RMS cut area', 'RMS floor']
#class Database(object):
#    def __init__(self):
#        try 



def check_corplot_load(filename):
    """Load corplot data"""
    cpms      = CPMS(filename)
    ctrlpv    = cpms.ctrl_pv
    solvals   = cpms.ctrl_vals
    matstamp  = cpms.timestamp
    beam_data = cpms.beam
    nsamples  = cpms.samples     #n samples per magnet setting
    nsteps    = cpms.iterations  #number of magnet settings
    pvunits   = cpms.control_dict[0]['egu'] #units for sol strength
    return cpms.timestamp


def unpack_mat_beam_data(beam_data, category):
    """Gross"""
    data ={} 

    profkeys = ['COORD','PROF','FIT'] 

    if 'profx' in category:
        data_keys = ['X'+pkey for pkey in profkeys] 
    elif 'profy' in category:
        data_keys = ['Y'+pkey for pkey in profkeys] 
    elif 'profu' in category:
        data_keys = ['U'+pkey for pkey in profkeys]
    elif ('xStat' in category) or ('yStat' in category) or ('uStat' in category):
        data_keys = ['SUM', 'MEAN', 'RMS', 'SKEW', 'KURTOSIS']
        beam_data = beam_data[0]
    elif ('xStatStd' in category) or ('yStatStd' in category) or ('uStatStd' in category):
        data_keys = [category] 
    elif 'stats' in category:
        data_keys = ['XMEAN', 'YMEAN', 'XRMS', 'YRMS', 'CORR', 'SUM']
        beam_data = beam_data[0]
    elif 'statsStd' in category:
        data_keys = [category]
    
    if 'method' in category:
        return None
    else:
        for index, dtype in enumerate(data_keys):
            data[dtype] = beam_data[index]
        return data

def save_corplot_solenoid_scan(filename, h5group):
    """Load corplot data, save to h5"""
    cpms = CPMS(filename)
    #Make sure only one SOLN ctrl pv:
    assert isinstance(cpms.ctrl_pv, str) 
    assert 'SOLN' in cpms.ctrl_pv

    # Save some default info on top level
    try:
        #import pdb; pdb.set_trace()
        pydatetime = datenum_to_datetime(cpms.timestamp)
        isotime    = pydatetime.isoformat()+'-07:00'
        
        h5group.attrs['file']         = cpms.file
        h5group.attrs['isotime']      = isotime   
        h5group.attrs['accelerator']  = cpms.accelerator
        h5group.attrs['beam_names']   = cpms.beam_names
        h5group.attrs['ctrl_pv']      = cpms.ctrl_pv
        h5group.attrs['ctrl_pv_unit'] = cpms.control_dict[0]['egu']
        h5group.attrs['matlab_timestamp'] = cpms.timestamp
    except:
        print('ERROR: Missing attribute, or unexpected file format')
 
    # Loop through measurment steps
    for i in range(0, cpms.iterations):
        step_group = h5group.create_group('Step'+str(i))
        # Save ctrl pv and value, get beam data
        step_group.attrs[cpms.ctrl_pv]        = cpms.ctrl_vals[i]
        step_group.attrs[cpms.ctrl_pv+'.EGU'] = cpms.control_dict[0]['egu'] 
        step_data  = cpms.beam[i]
        # Create groups to save beam size data
        print('Trying to load the following types of data:', cpms.beam_names)
        # Different types of beam data
        for name in cpms.beam_names:
            # Fitting functions used to calc beam sizes
            for fit in range(0,len(FITS)):
                # Looping over samples, i.e. # magnet settings
                for sample in range(0,cpms.samples):
                    try:
                        sample_group = step_group.create_group('sample'+str(sample)) 
                    except:
                        pass

                    small_data   = unpack_mat_beam_data(step_data[sample][fit][name], name)
                    try:    
                        # Unpacking arrays in certain types of data
                        for key in small_data:
                            #import pdb; pdb.set_trace()
                            data_name = FITS[fit].replace(" ", "_") +'_'+name+'_'+key
                            save_data = step_group['sample'+str(sample)].create_dataset(data_name, data=np.array(small_data[key]))
                    except:
                        # Redundant method info
                        pass 

            if 'Stat' in name:
                save_data.attrs['unit'] = 'um'
    return




