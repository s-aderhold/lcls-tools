import numpy as np
from cor_plot_mat_scan import CorPlotMatScan as CPMS
from mat_emit_scan import MatEmitScan as MES
from archiver import *
from epics import PV

FITS = ['Gaussian', 'Asymmetric', 'Super', 'RMS', 'RMS cut peak', 'RMS cut area', 'RMS floor']
#class Database(object):
#    def __init__(self):
#        try 

LCLS_DIAGNOSTIC_MAP = {
        'YAG02':'YAGS:IN20:241', 
        'YAG03':'YAGS:IN20:351',
        'YAGS1':'YAGS:IN20:921',
        'YAGS2':'YAGS:IN20:995',
        'OTR1':'OTRS:IN20:541',
        'OTR2':'OTRS:IN20:571',
        'OTR3':'OTRS:IN20:621',
        'WS02': 'WIRE:IN20:561',
       }
def short_diagnostic_name(pv_name):
    """Replace YAG or WIRE PV name with short name"""
    for yag, yag_pv in LCLS_DIAGNOSTIC_MAP.items():
        if yag_pv in pv_name:
            yag_name = yag
            return yag_name
    print('Did not find short name for this pv:', pv_name)
    print('Returning original name for this group')
    return pv_name


def get_isotimes(mat_timestamp):
    '''Get shortened isotime for group name'''
    pydatetime = datenum_to_datetime(mat_timestamp)
    isotime    = pydatetime.isoformat()+'-07:00'
    return isotime, isotime.split('.')[0]



def check_emitscan_load(filename):
    """Load emit scan data"""
    mes      = MES(filename)
    ctrlpv   = mes.name
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
    
    standard_keys = ['XMEAN', 'YMEAN', 'XRMS', 'YRMS', 'CORR', 'SUM']
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
    if 'stats' == category:
        data_keys = standard_keys
        beam_data = beam_data[0]
    elif 'statsStd' in category:
        data_keys = [category]
    elif 'stats_std' == category:
        data_keys = standard_keys
        beam_data = beam_data[0]
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

    # Get screen PV name
    if len(cpms.prof_pv) > 1:
        name = cpms.prof_pv[0]
    else:
        name = cpms._prof_pv[cpms.prof_pv[0]][0][0][0] #AHHHH
 
    yag_name   = short_diagnostic_name(diagnostic_pv)
    isotime, short_time = get_isotimes(cpms.timestamp)
   
    # Make file group with screen and time in name
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
    
    return


def save_emit_scan(filename, h5group):
    '''Load emittance scan matlab data'''
    assert 'Emittance-scan' in filename

    mes           = MES(filename)
    diagnostic_pv = mes.name
    yag_name      = short_diagnostic_name(diagnostic_pv)
    isotime, short_time    = get_isotimes(mes.timestamp)

    # Make file group with screen and time in name
    emit_group = h5group.create_group('emit_scan_'+yag_name+'_'+short_time)
    beam       = emit_group.create_group('beam_data') 
    
    # Save some default info on top level
    h5group.attrs['file']         = mes.file
    h5group.attrs['isotime']      = isotime   
    h5group.attrs['data_types']   = mes.fields
    h5group.attrs['ctrl_pv']      = mes.quad_name
    #Have to get pv unit from EPICS!!!!!!!
    #h5group.attrs['ctrl_pv_unit'] = mes.control_dict[0]['egu']
    h5group.attrs['matlab_timestamp'] = mes.timestamp

    # Saving emittance data first
    beam_emit = beam.create_group('emittance')
    beam_emit.attrs['emittance_unit'] = 'micron'
    for key in mes.emit_x:
        fit = beam_emit.create_group(key)
        fit.create_dataset('emit_x', data=mes.emit_x[key])
        fit.create_dataset('emit_y', data=mes.emit_y[key])

    # Saving beam profiles
    beam_sizes = beam.create_group('beam_sizes')
    # Loop through measurment steps
    for i in range(0, mes.iterations):
        step_group = beam_sizes.create_group('step'+str(i))
        # Save ctrl pv and value, get beam data
        step_group.attrs[mes.quad_name] = mes.quad_vals[i]
        #step_group.attrs[mes.ctrl_pv+'.EGU'] = mes.control_dict[0]['egu'] 
        step_data  = mes.beam[i]
        skeys = step_data[0].keys()
        # Fitting functions used to calc beam sizes
        for ifit, fit in enumerate(FITS):
            # Create groups to save beam size data
            fit_group  = step_group.create_group(fit) 
            fit_group.attrs['unit'] = 'um'
            if 'Gaussian' in fit:
                # Looping over samples, i.e. # magnet settings
                raw_group    = step_group.create_group('raw_data')
                raw_group.attrs['unit'] = 'um'
                # 0 index = COORD
                # 1 index = PROF
                if 'profx' in skeys:
                    xdata = step_data[ifit]['profx']
                    raw_group.create_dataset('XCOORD', data=xdata[0])
                    raw_group.create_dataset('XPROF', data=xdata[1])
                elif 'profy' in skeys:
                    ydata = step_data[ifit]['profy']
                    raw_group.create_dataset('YCOORD', data=ydata[0])
                    raw_group.create_dataset('YPROF', data=ydata[1])
            
            # Different types of beam data
            for name in ['stats', 'stats_std']:
                # Unpacking a stats data
                small_data = unpack_mat_beam_data(step_data[ifit][name], name)
                for key in small_data:
                    if name=='stats_std':
                        name = 'statsStd'
                    data_type = name+'_'+key
                    save_data = fit_group.create_dataset(data_type, data=np.array(small_data[key]))
    return


