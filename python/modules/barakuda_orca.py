
import sys
import numpy as nmp


def get_basin_info( cf_bm ):    
    from netCDF4 import Dataset
    l_b_names = [] ; l_b_lgnms = []
    l_b_names.append(u'GLO') ; l_b_lgnms.append(u'Global Ocean')
    id_bm = Dataset(cf_bm)
    list_var = id_bm.variables.keys()
    for cv in list_var:
        if cv[:5] == 'tmask':
            l_b_names.append(cv[5:])
            l_b_lgnms.append(id_bm.variables[cv].long_name)
    id_bm.close()
    return l_b_names, l_b_lgnms


def lon_reorg_orca(ZZ, Xlong, ilon_ext=0, v_jx_jump_p=170., v_jx_jump_m=-170.):
    #
    #
    # IN:
    # ===
    # ZZ       : 1D, 2D, or 3D array to treat
    # Xlong    : 1D or 2D array containing the longitude, must be consistent with the shape of ZZ !
    # ilon_ext : longitude extention of the map you want (in degrees)
    #
    # OUT:
    # ====
    # ZZx     : re-organized array, mind the possibility of modified x dimension !
    #
    import barakuda_tool as bt
    #
    idim_lon = len(nmp.shape(Xlong))
    if idim_lon not in [ 1 , 2 ]:
        print 'util_orca.lon_reorg_orca: ERROR => longitude array "Xlong" must be 1D or 2D !'; sys.exit(0)
    #
    if idim_lon == 2: (nj,ni) = nmp.shape(Xlong)
    if idim_lon == 1:      ni = len(Xlong)
    #
    vlon = nmp.zeros(ni)
    #
    if idim_lon == 2: vlon[:] = Xlong[nj/3,:]
    if idim_lon == 1: vlon[:] = Xlong[:]
    #
    lfound_jx_jump = False
    ji=0
    while ( not lfound_jx_jump and ji < ni-1):
        if vlon[ji] > v_jx_jump_p and vlon[ji+1] < v_jx_jump_m:
            jx_jump = ji + 1
            lfound_jx_jump = True
        ji = ji + 1
    print "  *** barakuda_orca.lon_reorg_orca >> Longitude jump at ji = ", jx_jump
    #
    lfound_jx_zero = False
    ji=0
    while ( not lfound_jx_zero and ji < ni-1):
        if vlon[ji] < 0. and vlon[ji+1] > 0.:
            jx_zero = ji + 1
            lfound_jx_zero = True
        ji = ji + 1
    print "  *** barakuda_orca.lon_reorg_orca >> Longitude zero at ji = ", jx_zero
    #
    del vlon
    
    jx_oo = 2  # orca longitude overlap...
    vdim = ZZ.shape
    ndim = len(vdim)

    if ndim < 1 or ndim > 4:
        print 'util_orca.lon_reorg_orca: ERROR we only treat 1D, 2D, 3D or 4D arrays...'

    if ndim == 4:
        #
        [ nr, nz , ny , nx ] = vdim ;     nx0 = nx - jx_oo
        ZZx  = nmp.zeros((nr, nz, ny, nx0))
        ZZx_ext  = nmp.zeros((nr, nz, ny, (nx0+ilon_ext)))
        #
        for jx in range(jx_zero,nx):
            ZZx[:,:,:,jx-jx_zero] = ZZ[:,:,:,jx]
        for jx in range(jx_oo,jx_zero):
            ZZx[:,:,:,jx+(nx-jx_zero)-jx_oo] = ZZ[:,:,:,jx]
        #
        if ilon_ext == 0: ZZx_ext[:,:,:,:] = ZZx[:,:,:,:]
    #
    #
    if ndim == 3:
        #
        [ nz , ny , nx ] = vdim ;     nx0 = nx - jx_oo
        #print 'nx, ny, nz = ', nx, ny, nz
        #
        ZZx  = nmp.zeros(nx0*ny*nz) ;  ZZx.shape = [nz, ny, nx0]
        ZZx_ext  = nmp.zeros((nx0+ilon_ext)*ny*nz) ;  ZZx_ext.shape = [nz, ny, (nx0+ilon_ext)]
        #
        for jx in range(jx_zero,nx):
            ZZx[:,:,jx-jx_zero] = ZZ[:,:,jx]
        for jx in range(jx_oo,jx_zero):
            ZZx[:,:,jx+(nx-jx_zero)-jx_oo] = ZZ[:,:,jx]
        #
        if ilon_ext == 0: ZZx_ext[:,:,:] = ZZx[:,:,:]
    #
    #
    if ndim == 2:
        #
        [ ny , nx ] = vdim ;     nx0 = nx - jx_oo
        #print 'nx, ny = ', nx, ny
        #
        ZZx  = nmp.zeros(nx0*ny) ;  ZZx.shape = [ny, nx0]
        ZZx_ext  = nmp.zeros((nx0+ilon_ext)*ny) ;  ZZx_ext.shape = [ny, (nx0+ilon_ext)]
        #
        for jx in range(jx_zero,nx):
            ZZx[:,jx-jx_zero] = ZZ[:,jx]
        for jx in range(jx_oo,jx_zero):
            ZZx[:,jx+(nx-jx_zero)-jx_oo] = ZZ[:,jx]
        #
        if ilon_ext == 0: ZZx_ext[:,:] = ZZx[:,:]
    #
    #
    if ndim == 1:
        #
        [ nx ] = vdim ;     nx0 = nx - jx_oo
        #print 'nx = ', nx
        #
        ZZx  = nmp.zeros(nx0) ;  ZZx.shape = [nx0]
        ZZx_ext  = nmp.zeros(nx0+ilon_ext) ;  ZZx_ext.shape = [nx0+ilon_ext]
        #
        for jx in range(jx_zero,nx):
            ZZx[jx-jx_zero] = ZZ[jx]
            #print jx-jx_zero, 'prend', jx, '    ', vlon[jx]
            #
        #print ''
        for jx in range(jx_oo,jx_zero):
            ZZx[jx+(nx-jx_zero)-jx_oo] = ZZ[jx]
            #print jx+(nx-jx_zero)-jx_oo, 'prend', jx, '    ', vlon[jx]
        #
        if ilon_ext == 0: ZZx_ext[:] = ZZx[:]
        #iwa = nmp.where(vlon0 < 0.) ; vlon0[iwa] = vlon0[iwa] + 360.
        #
        #
        #
        # Now longitude extenstion:
    if ilon_ext > 0: ZZx_ext = bt.extend_domain(ZZx, ilon_ext)
    del ZZx

    return ZZx_ext








def conf_exp(ccexp):
    #
    # Find the CONF from CONF-EXP and exit if CONF does not exist!
    #
    i = 0 ; conf = ''
    while i < len(ccexp) and ccexp[i] != '-' : conf = conf+ccexp[i]; i=i+1
    #print 'conf =', conf, '\n'
    return conf



def mean_3d(XD, LSM, XVOL):
    #
    # XD             : 3D+T array containing data
    # LSM            : 3D land sea mask
    # XVOL           : 3D E1T*E2T*E3T  : 3D mesh volume
    #
    # RETURN vmean: vector containing 3d-averaged values at each time record

    ( lt, lz, ly, lx ) = nmp.shape(XD)

    if nmp.shape(LSM) != ( lz, ly, lx ):
        print 'ERROR: mean_3d.barakuda_orca.py => XD and LSM do not agree in shape!'
        sys.exit(0)
    if nmp.shape(XVOL) != ( lz, ly, lx ):
        print 'ERROR: mean_3d.barakuda_orca.py => XD and XVOL do not agree in shape!'
        sys.exit(0)

    vmean = nmp.zeros(lt)
    
    XX = LSM[:,:,:]*XVOL[:,:,:]
    rd = nmp.sum( XX )
    XX = XX/rd
    if rd > 0.:
        for jt in range(lt):
            vmean[jt] = nmp.sum( XD[jt,:,:,:]*XX )
    else:
        vmean[:] = nmp.nan

    return vmean


def mean_2d(XD, LSM, XAREA):
    #
    # XD             : 2D+T array containing data
    # LSM            : 2D land sea mask
    # XAREA          : 2D E1T*E2T  : mesh area
    #
    # RETURN vmean: vector containing 2d-averaged values at each time record

    ( lt, ly, lx ) = nmp.shape(XD)

    if nmp.shape(LSM) != ( ly, lx ):
        print 'ERROR: mean_2d.barakuda_orca.py => XD and LSM do not agree in shape!'
        sys.exit(0)
    if nmp.shape(XAREA) != ( ly, lx ):
        print 'ERROR: mean_2d.barakuda_orca.py => XD and XAREA do not agree in shape!'
        sys.exit(0)

    vmean = nmp.zeros(lt)
    XX = LSM[:,:]*XAREA[:,:]
    rd = nmp.sum( XX )

    # Sometimes LSM can be 0 everywhere! => rd == 0. !
    if rd > 0.:
        XX = XX/rd
        for jt in range(lt):
            vmean[jt] = nmp.sum( XD[jt,:,:]*XX )
    else:
        vmean[:] = nmp.nan

    return vmean






def ij_from_xy(xx, yy, xlon, xlat):
    #
    #=============================================================
    # Input:
    #       xx : longitude of searched point (float)
    #       yy : latitude  of searched point (float)
    #       xlon  : 2D array of longitudes of the ORCA grid
    #       xlat  : 2D array of latitudes  of the ORCA grid
    # Output:
    #       ( ji, jj ) : coresponding i and j indices on the ORCA grid    
    #=============================================================    
    #
    ji=0 ; jj=0
    #
    if xx < 0.: xx = xx + 360.
    #
    (nj , ni) = xlon.shape
    iwa = nmp.where(xlon < 0.) ; xlon[iwa] = xlon[iwa] + 360. # Want only positive values in longitude:
    #
    # Southernmost latitude of the ORCA domain:
    ji0 = nmp.argmin(xlat[0,:])
    lat_min = xlat[0,ji0]
    ji = ji0
    yy = max( yy, lat_min )
    #
    # Northernmost latitude of the ORCA domain:    
    ji0 = nmp.argmax(xlat[nj-1,:])
    lat_max = xlat[nj-1,ji0]
    yy = min( yy, lat_max )
    #
    A = nmp.abs( xlat[:-2,:-2]-yy ) + nmp.abs( xlon[:-2,:-2]-xx )
    (jj,ji) = nmp.unravel_index(A.argmin(), A.shape)
    #
    return ( ji, jj )



def transect_zon_or_med(x1, x2, y1, y2, xlon, xlat): #, rmin, rmax, dc):
    #
    #=============================================================
    # Input:
    #       x1,x2 : longitudes of point P1 and P2 defining the section (zonal OR meridional)
    #       y1,y2 : latitudes of point P1 and P2 defining the section (zonal OR meridional)
    #            => so yes! either x1==x2 or y1==y2 !
    #       xlon  : 2D array of longitudes of the ORCA grid
    #       xlat  : 2D array of latitudes  of the ORCA grid
    # Output:
    #       ( ji1, ji2, jj1, jj2 ) : coresponding i and j indices on the ORCA grid
    #=============================================================    
    #
    ji1=0 ; ji2=0 ; jj1=0 ; jj2=0
    lhori = False ; lvert = False
    #
    if y1 == y2: lhori = True
    if x1 == x2: lvert = True
    #
    if not (lhori or lvert) :
        print 'transect_zon_or_med only supports horizontal or vertical sections!'
        sys.exit(0)
    #
    (ji1,jj1) = ij_from_xy(x1, y1, xlon, xlat)
    (ji2,jj2) = ij_from_xy(x2, y2, xlon, xlat)
    #
    if lhori and (jj1 != jj2): jj2=jj1
    if lvert and (ji1 != ji2): ji2=ji1
    #
    return ( ji1, ji2, jj1, jj2 )


def shrink_domain(LSM):
    # Decrasing the domain size to only retain the (rectangular region) with
    # ocean points (LSM == 1)
    #
    # Input:
    #     LSM : 2D land sea mask array
    # Output:
    #  (i1,j1,i2,j2): coordinates of the 2 points defining the rectangular region 
    #
    ( ly, lx ) = nmp.shape(LSM)
    #
    #if nmp.shape(LSM) != ( lz, ly, lx ):
    #    print 'ERROR: shrink_domain.barakuda_orca.py => XD and LSM do not agree in shape!'
    #    sys.exit(0)
    (vjj , vji)  = nmp.where(LSM[:,:]>0.5)
    j1 = max( nmp.min(vjj)-2 , 0    )
    i1 = max( nmp.min(vji)-2 , 0    )
    j2 = min( nmp.max(vjj)+2 , ly-1 ) + 1
    i2 = min( nmp.max(vji)+2 , lx-1 ) + 1
    #
    if (i1,j1,i2,j2) != (0,0,lx,ly):
        print '       ===> zooming on i1,j1 -> i2,j2:', i1,j1,'->',i2,j2
    if (i1,i2) == (0,lx): i2 = i2-2 ; # Mind east-west periodicity overlap of 2 points...
    #
    return (i1,j1,i2,j2)
