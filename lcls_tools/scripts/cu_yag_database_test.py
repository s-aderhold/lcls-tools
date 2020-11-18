import glob
import h5py
import numpy as np
import os,sys
from datetime import datetime
from epics import PV

sys.path.append('../image_processing')
sys.path.append('../data_analysis')
sys.path.append('../cor_plot')
sys.path.append('../emit_scan')

import meme
import meme.archive
import meme.names
from mat_image import MatImage as MI
from archiver import * #get_iso_time, datenum_to_datetime, save_mat_image_to_h5, save_pvdata_to_h5

from archiver import *
from dataset import *

# VCC and YAG images on LCLS-II
# PV Notes:
# 'IRIS:LGUN:%' = SC laser PV's
# 

#H5FILE = 'oct_2019_vcc_database.h5'
#
##FILES = glob.glob('/u1/lcls/matlab/data/2018/2018-11/2018-11-*/ProfMon-CAMR_IN20_*')
##FILES = glob.glob('/u1/lcls/matlab/data/2019/2019-10/2019*/ProfMon*LGUN*')
#VFILES = glob.glob('/u1/lcls/matlab/data/2019/2019-10/2019-10-3*/ProfMon*LGUN*')
#YFILES = glob.glob('/u1/lcls/matlab/data/2019/2019-10/2019-10-3*/ProfMon-YAGS_GUNB*')
#
## Must contain pv's searchable by meme
#pv_groups = ['IRIS:LGUN:%','%:GUNB:%:BACT','%:GUNB:%:AACT','TORO:GUNB:%:CHRG']
#
## Must contain the following:
## data file paths, output filename, pv types and labels.
#input_dict = {
#            'vcc_files': VFILES,
#            'yag_files': YFILES, 
#            'outfile':H5FILE,
#            'short_description': 'lcls_sc_image_and_pv_data'}  
#
#long_description = "vcc and YAG images with corresponding pv names and data values for EIC area"
#
##test_db = make_vcc_db(input_dict, pv_groups, info=long_description)

def make_cuinj_yag_db(input_dict, pv_list, info='No info given at run time.'):
    """
    Return a h5 database with PV names and values
    corresponding to each YAG image.
    
    Assumes the user is supplying VCC and YAG images.
    This means only one set of PV values apply to each image.
    The data was only taken at ONE timestamp.
    This will not work for correlation plots, or scans.
    """
    yag_files = input_dict['image_files']
    outname   = input_dict['outfile']
    #top_group = input_dict['short_description']

    vhf = h5py.File(outname, 'w')
    vhf.attrs['information'] = info
    for filename in yag_files:
        # Load vcc image
        mimage    = MI()
        mimage.load_mat_image(filename)
        isotime, short_time    = get_isotimes(mimage.timestamp)
        name    = filename.split('-2020')[0]
        yagname = name.split('/')[-1]
        #import pdb; pdb.set_trace()
        # check if node exists
        if yagname in vhf.keys():
            group = vhf[yagname]
        else:
            group = vhf.create_group(yagname)
     
        try:
            # Save vcc image + metadata
            image_group = save_mat_image_to_h5(mimage, group)
            # Save pv data related to image
            #import pdb; pdb.set_trace()
            save_pvdata_to_h5(pv_list,image_group, isotime)
        except:
            print('Could not save YAG file:', filename)

    vhf.close()

# DATA on LCLS Cu
H5FILE = '2020_summer_lcls_cu_inj_vcc_and_yag_database.h5'

#Correlation plot scan data
yag1 = glob.glob('/u1/lcls/matlab/data/2020/2020-06/2020-06-*[21,22]/ProfMon*')
yag2 = glob.glob('/u1/lcls/matlab/data/2020/2020-07/2020-07-*[08,09]/ProfMon*')
YFILES = yag1 + yag2

#basedir = '/mccfs2/u1/lcls/matlab/data/2020'
#day1    = '/2020-06/2020-06-21/'
#day2    = '/2020-06/2020-06-22/'
#day3    = '/2020-07/2020-07-08/'
#day4    = '/2020-07/2020-07-09/'
#prof    = 'Prof*_IN20_*'
#corr    = 'Corr_IN20_*'
#
# 6/21, 6/22, 7/8, 7/9
#YFILES = glob.glob(basedir+day4+'ProfMon-OTRS_IN20_571*')
#CFILES = glob.glob(basedir+day4+'Corr_IN20_*')


# Must contain pv's searchable by meme
pv_groups = ['IRIS:LR20:130:MOTR_ANGLE','SOLN:IN20:121:BACT',
	     'QUAD:IN20:121:BACT','QUAD:IN20:122:BACT',
             'ACCL:IN20:300:L0A_ADES', 'ACCL:IN20:400:L0B_ADES',
             'ACCL:IN20:300:L0A_PDES', 'ACCL:IN20:400:L0B_PDES']

#QUAD:IN21:122:BDES
# Must contain the following:
# data file paths, output filename, pv types and labels.
input_dict = {
            'image_files': YFILES, 
            'outfile':H5FILE,}
            #'short_description': 'lcls_sc_image_and_pv_data'}  

#long_description = "yag, emittance, bunch length data for lcls cu inj"
long_description = "all YAG and VCC images taken during shifts on 06/21-22, and 07/08-09 for lcls cu inj"
test_db = make_cuinj_yag_db(input_dict, pv_groups, info=long_description)

