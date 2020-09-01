import numpy as np
from cor_plot_mat_scan import CorPlotMatScan as CPMS
from mat_emit_scan import MatEmitScan as MES
from archiver import *
from epics import PV

FITS = ['Gaussian', 'Asymmetric', 'Super', 'RMS', 'RMS cut peak', 'RMS cut area', 'RMS floor']
#class Database(object):
#    def __init__(self):
#        try 

LCLS_YAG_MAP = {
        'YAG02':'YAGS:IN20:241', 
        'YAG03':'YAGS:IN20:351', 
        'YAGS2':'YAGS:IN20:995',
        'OTR1':'OTRS:IN20:541',
        'OTR2':'OTRS:IN20:571',
        'OTR3':'OTRS:IN20:621',
        }


def check_emitscan_load(filename):
    """Load emit scan data"""
    mes      = MES(filename)
    #ctrlpv   = mes.name
    quad     = mes.quad_name
    quadvals = mes.quad_vals
    emitx    = mes.emit_x
    emity    = mes.emit_y
    return mes.timestamp


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
    profpv    = cpms.prof_pv
    assert cpms.beam_names is not None
    assert cpms.prof_pv is not None
    return cpms.timestamp


def unpack_mat_beam_data(beam_data, category):
    """Gross...
    For the moment only saving stats. x/yStats are repeats mostly.

    NOTE: 
    Raw data (X/YPROF) is repeated in the following methods:
            - Gaussian
            - Asymmetric
            - Super
            - RMS
    Modified data (X/YPROF, X/YFIT) is in the following methods:
            - RMS Cut peak
            - RMS Cut area
            - RMS Floor 

    X/YCOORD is repeated in ALL metods.

    """
    data ={} 

    #profkeys = ['COORD','PROF','FIT'] 

    #if 'profx' in category:
    #    data_keys = 'XFIT' #['X'+pkey for pkey in profkeys] 
    #elif 'profy' in category:
    #    data_keys = 'YFIT' #['Y'+pkey for pkey in profkeys] 
    #elif 'profu' in category:
    #    data_keys = ['U'+pkey for pkey in profkeys]
    #elif ('xStat' in category) or ('yStat' in category): #or ('uStat' in category):
    #    data_keys = ['SUM', 'MEAN', 'RMS', 'SKEW', 'KURTOSIS']
    #    beam_data = beam_data[0]
    #elif ('xStatStd' in category) or ('yStatStd' in category): #or ('uStatStd' in category):
    #    data_keys = [category] 
    if 'stats' in category:
        data_keys = ['XMEAN', 'YMEAN', 'XRMS', 'YRMS', 'CORR', 'SUM']
        beam_data = beam_data[0]
    elif 'statsStd' in category:
        data_keys = [category]
    #elif 'method' in category:
    #    data_keys = [category]
    
    try:
        for index, dtype in enumerate(data_keys):
            data[dtype] = beam_data[index]
    except:
        pass #print('Not saving this key:', category)

    return data

def save_corplot_solenoid_scan(filename, h5group):
    """Load corplot data, save to h5"""
    cpms = CPMS(filename)
    #Make sure only one SOLN ctrl pv:
    assert isinstance(cpms.ctrl_pv, str) 
    assert 'SOLN' in cpms.ctrl_pv

    
    #import pdb; pdb.set_trace()
    pydatetime = datenum_to_datetime(cpms.timestamp)
    isotime    = pydatetime.isoformat()+'-07:00'
    short_time = isotime.split('.')[0]
    if len(cpms.prof_pv) > 1:
        name = cpms.prof_pv[0]
    else:
        name = cpms._prof_pv[cpms.prof_pv[0]][0][0][0] #AHHHH
   
    for yag, yag_pv in LCLS_YAG_MAP.items():
        if yag_pv in name:
            yag_name = yag
            print('YAH',yag_name)
    
    cp_group   = h5group.create_group('solenoid_scan_'+yag_name+'_'+short_time)
    beam       = cp_group.create_group('beam_data') 
            
    # Save some default info on top level
    h5group.attrs['file']         = cpms.file
    h5group.attrs['isotime']      = isotime   
    h5group.attrs['accelerator']  = cpms.accelerator
    h5group.attrs['beam_names']   = cpms.beam_names
    h5group.attrs['ctrl_pv']      = cpms.ctrl_pv
    h5group.attrs['ctrl_pv_unit'] = cpms.control_dict[0]['egu']
    h5group.attrs['matlab_timestamp'] = cpms.timestamp

    print('Trying to load the following types of data:', cpms.beam_names)
    # Loop through measurment steps
    for i in range(0, cpms.iterations):
        step_group = beam.create_group('Step'+str(i))
        # Save ctrl pv and value, get beam data
        step_group.attrs[cpms.ctrl_pv]        = cpms.ctrl_vals[i]
        step_group.attrs[cpms.ctrl_pv+'.EGU'] = cpms.control_dict[0]['egu'] 
        step_data  = cpms.beam[i]
        # Looping over samples, i.e. # magnet settings
        for sample in range(0,cpms.samples):
            sample_group = step_group.create_group('sample'+str(sample))
            raw_group    = sample_group.create_group('raw_data')
            raw_group.attrs['unit'] = 'um'
            # Fitting functions used to calc beam sizes
            for ifit, fit in enumerate(FITS):
                if 'Gaussian' in fit:
                    # 0 index = COORD
                    # 1 index = PROF
                    xdata = step_data[sample][ifit]['profx']
                    ydata = step_data[sample][ifit]['profy']
                    raw_group.create_dataset('XCOORD', data=xdata[0])
                    raw_group.create_dataset('XPROF', data=xdata[1])
                    raw_group.create_dataset('YCOORD', data=ydata[0])
                    raw_group.create_dataset('YPROF', data=ydata[1])
              
                # Create groups to save beam size data
                fit_group  = sample_group.create_group(fit) 
                fit_group.attrs['unit'] = 'um'
                # Different types of beam data
                for name in cpms.beam_names:
                    # Unpacking a stats data
                    small_data = unpack_mat_beam_data(step_data[sample][ifit][name], name)
                    for key in small_data:
                        data_type = name+'_'+key
                        save_data = fit_group.create_dataset(data_type, data=np.array(small_data[key]))
    
    return cp_group



def save_emit_scan(filename, h5group):
    '''Load emittance scan matlab data'''
    mes      = MES(filename)
    assert 'Emittance-scan' in mes.mat_file
    quad     = mes.quad_name
    quadvals = mes.quad_vals
    emitx    = mes.emit_x
    emity    = mes.emit_y
    try:
        for key in emitx:
            xname = key+'_x'
            yname = key+'_y'
            h5group.create_dataset(xname, data=emitx[key])
            h5group.create_dataset(yname, data=emity[key])
    except:
        print('Could not save emittance data')
    return 
