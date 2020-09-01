from datetime import datetime, timedelta
import meme.archive 
import meme.names 
from epics import PV

def datenum_to_datetime(datenum):
    """Convert Matlab datenum into Python datetime.

    :param datenum: Date in datenum format
    :return:        Datetime object corresponding to datenum.
    https://gist.github.com/victorkristof/b9d794fe1ed12e708b9d
    """
    days = datenum % 1
    return datetime.fromordinal(int(datenum)) \
           + timedelta(days=days) \
           - timedelta(days=366)

def save_mat_image_attributes(mi,h5):
    """Save mat image attrs to h5 dataset or group"""
    for attr, value in mi.__dict__.items():
        try:
            h5.attrs[attr[1:]] = value
        except:
            print('Did not save', attr, 'to attributes.')
    return None

def save_mat_image_to_h5(mi, h5group):
    """Save mat image and meta data to h5 file. 
    
       The data is seperated by timestamp, which 
       is converted from matlab datnum to python datetime.
       mi      -- matlab image object
       h5group -- h5 group or dataset to save attributes
    """ 
    timestamp   = datenum_to_datetime(mi.timestamp)
    isotime     = timestamp.isoformat()
    image_group = h5group.create_group(isotime)
    image_data  = image_group.create_dataset('image', data=mi.image)
    image_data.attrs['isotime'] = isotime
    save_mat_image_attributes(mi, image_data)
    return image_group

def get_pvdata_names(partial_listv):
    """Get list of pv names using wildcards and meme"""
    #timestamp = h5group['image'].attrs['isotime']
    #pv_group  = h5group.create_group('pvdata')
    #pv_names  = []
    for pv_name in partial_list:
        # Using wildcard to get all related PV names w/ meme
        pv_names  = pv_names + meme.names.list_pvs(pv_name)
   
    ## Converting isotime to datetime for meme 
    #time      = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
    #delta     = time + timedelta(days=0, milliseconds=1)
    #pv_values = meme.archive.get(pv_names, from_time=time, to_time=delta)
    #for entry in pv_values:
    #    label = entry['pvName']
    #    value = entry['value']['value']['values']
    #    pv_group.attrs[label] = value 

    return pv_list 

def save_pvdata_to_h5(pvlist, h5group, isotime):
    """Save pv data given timestamp to h5 file"""
    pv_group = h5group.create_group('pvdata')
    for pv_name in pvlist:
   	# get pv unit 
        pv       = PV(pv_name)
        d        = pv.get_ctrlvars()
        units    = d['units']
	# get pv value
        pv_value = meme.archive.get(pv_name, from_time=isotime, to_time=isotime)
        pv_num   = pv_value['values'][0]
	# save unit and value
        pv_group.attrs[pv_name]        = str(pv_num)
        pv_group.attrs[pv_name+'.EGU'] = units

    return None	
