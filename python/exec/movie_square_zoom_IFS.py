#!/usr/bin/env python

#       B a r a K u d a
#
#  Prepare 2D maps (monthly) that will later become a GIF animation!
#  NEMO output and observations needed
#
#    L. Brodeau, november 2016

import sys
import os
import numpy as nmp

from netCDF4 import Dataset

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import datetime

import barakuda_colmap as bcm

import barakuda_tool as bt
import barakuda_plot as bp


#venv_needed = {'ORCA','RUN','DIAG_D','MM_FILE','NN_SST','NN_T','NN_S','NN_ICEF',
#               'F_T_CLIM_3D_12','F_S_CLIM_3D_12','SST_CLIM_12','NN_SST_CLIM','NN_T_CLIM','NN_S_CLIM'}

#vdic = bt.check_env_var(sys.argv[0], venv_needed)

#CONFRUN = vdic['ORCA']+'-'+vdic['RUN']

tmin=-20. ;  tmax=12.   ;  dtemp = 1.
imin=0.  ;  imax=0.99  ;  dice = 0.1

fig_type='png'



#narg = len(sys.argv)
#if narg < 4:
#    print 'Usage: '+sys.argv[0]+' <NEMO file (1 year, monthyly)> <year>'
#    print '          ...'
#    sys.exit(0)

#cf_in = sys.argv[1]
#cy    = sys.argv[2] ; jy=int(cy)
#cvar  = sys.argv[3]

#if not cvar in ['sst','sss','ice']:
#    print 'ERROR (prepare_movies.py): variable '+cvar+' not supported yet!'
#    sys.exit(0)


cf_sst  = '/home/laurent/tmp/T2M_ICMGG_C120_1990.nc4'
csst  = 'T2M'

cf_msk = '/home/laurent/tmp/LSM_ICMGG_T255.nc4'
cmsk  = 'LSM'

# South Greenland:
i1 = 412; i2 =486
j1 = 22 ; j2 = 56

#Global T255:
#i1 = 0 ; i2 =512
#j1 = 0 ; j2 = 256


bt.chck4f(cf_msk)
id_msk = Dataset(cf_msk)
XMSK  = id_msk.variables[cmsk][0,j1:j2,i1:i2] ; # t, y, x
id_msk.close()


[ nj , ni ] = nmp.shape(XMSK)


cpal_sst = 'sstnw'
bt.chck4f(cf_sst)
id_sst = Dataset(cf_sst)
XSST   = id_sst.variables[csst][:,j1:j2,i1:i2] - 273.15 ; # t, y, x
id_sst.close()
[ Nt, nj0 , ni0 ] = nmp.shape(XSST)


#idx_oce = nmp.where(XMSK[:,:] > 0.01)

psst = nmp.zeros((nj,ni))


for jt in range(Nt):


    ct = '%3.3i'%(jt+1)

    cd = str(datetime.datetime.strptime('1990 '+ct, '%Y %j'))
    cdate = cd[:10] ; print ' *** cdate :', cdate

    cfig = 'IFS'+'_d'+ct+'.'+fig_type
    
    #psst = nmp.ma.masked_where(XMSK[:,:] < 0.2, XSST[jt,:,:])
    #pice = nmp.ma.masked_where(XMSK[:,:] < 0.2, XICE[jt,:,:])

    psst[:,:] = XSST[jt,:,:]

    vc_sst = nmp.arange(tmin, tmax + dtemp, dtemp)

    fig = plt.figure(num = 1, figsize=(10,8), dpi=None, facecolor='w', edgecolor='k')
    ax  = plt.axes([0.05, 0.06, 0.9, 0.86], axisbg = 'k')


    # Pal_Sst:
    pal_sst = bcm.chose_palette(cpal_sst)
    norm_sst = colors.Normalize(vmin = tmin, vmax = tmax, clip = False)

    pal_msk = bcm.chose_palette('blk')
    norm_msk = colors.Normalize(vmin = 0., vmax = 1., clip = False)

    

    plt.pcolor(nmp.flipud(psst), cmap = pal_sst, norm = norm_sst)


    # Mask
    pmsk = nmp.ma.masked_where(XMSK[:,:] < 0.5, XMSK[:,:]*0.+40.)
    plt.pcolor(nmp.flipud(pmsk), cmap = pal_msk, norm = norm_msk)


    
    plt.axis([ 0, ni+1, 0, nj+1])

    plt.title('Coupled ORCA12.L75 - T255.L91, '+cdate)

    
    plt.savefig(cfig, dpi=120, orientation='portrait', transparent=False)
    print cfig+' created!\n'
    plt.close(1)
                



sys.exit(0)


#bp.plot("2d")([0], [0], XSST[2,:,:],
#              XSST[2,:,:]*0.+1.,  tmin, tmax, dtemp,
#              lkcont=False, cpal_sst='RdBu_r',
#              cfignm='boo',
#              cbunit='deg.C', fig_type=fig_type,
#              ctitle='Ta mere',
#              lforce_lim=False, i_cb_subsamp=2)

