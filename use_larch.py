import sys
import os
import string
import glob
import re
import yaml
import math
import numpy as np
import numpy.linalg as linalg
import scipy.optimize as optim
import scipy.interpolate as interp
import scipy.integrate as INT
import shutil
import pandas as pd
import larch
from larch_plugins.xafs import autobk, xftf, xftr
from larch_plugins.io import read_ascii
import larch.builtins as larch_builtins

mylarch = larch.Interpreter(with_plugins=False)

def read_file(file):
    m = re.search(r'\.[a-zA-Z0-9]+$',os.path.basename(file))
    df = pd.DataFrame()
    if m == None:
        print ('Nothing to match')
        return
    elif m.group(0) == '.ex3':
        t_df = pd.read_csv(file,names=['Energy','ut'],delim_whitespace=True,skiprows=27)
        df = t_df.ix[1:t_df.shape[0]-2]
        Energy = df['Energy'].values
        ut = df['ut'].values
        t_array = np.array([])
        for term in Energy:
            print (term)
            if re.match(r'\-?\d+\.\d+',str(term)):
                t_array = np.append(t_array,float(term))
        Energy = t_array[:]
        print (Energy)
        t_array = np.array([])
        for term in ut:
            if re.match(r'\-?\d+\.\d+',str(term)):
                t_array = np.append(t_array,float(term))
            ut = t_array[:]
        return Energy, ut
    else:
        dat = read_ascii(file,_larch=mylarch)
        return dat.data

def read_chi_file(file):
    k = np.array([])
    chi = np.array([])
    if re.match(r"(.+\.rex)",os.path.basename(file)):
        #print 'match'
        f = open(file,'r')
        sign = 'not read'
        for line in f:
            if sign == 'not read' and re.match (r"\[XI_BEGIN\]",line.rstrip()):
                sign = 'read'
                print (sign)
            elif sign == 'not read':
                pass
            elif sign == 'read' and re.match(r"^\d+\.\d+(\s+|\t+)\-?\d+\.\d+", line):
                t_array = line.split()
                k = np.append(k, float(t_array[0]))
                chi = np.append(chi, float(t_array[1]))
            elif sign == 'read' and re.match (r"\[XI_END\]",line.rstrip()):
                break
    elif re.match(r"(.+\.xi)",os.path.basename(file)):
        f = open(file,'r')
        sign = 'not read'
        for line in f:
            if sign == 'not read' and re.match (r"\[XI_BEGIN\]",line.rstrip()):
                sign = 'read'
                print (sign)
            elif sign == 'not read':
                pass
            elif sign == 'read' and re.match(r"^\d+\.\d+(,|\s+|\t+)\-?\d+\.\d+", line):
                t_array = line.split(',')
                k = np.append(k, float(t_array[0]))
                chi = np.append(chi, float(t_array[1]))
            elif sign == 'read' and re.match (r"\[XI_END\]",line.rstrip()):
                break
    else:
        dat = read_ascii(file,_larch=mylarch)
        return dat.data
    return k, chi

def run_autobk(Energy,Ut,E0,Rbkg,Kweight,k_min,k_max,fit_s,fit_e,nor_aE0_s,nor_aE0_e,pre_type):
    exafs = larch_builtins._group(mylarch)
    ft = larch_builtins._group(mylarch)
    Pre_edge_kws = {'pre1':fit_s-E0,'pre2':fit_e-E0,'norm1':nor_aE0_s-E0,'norm2':nor_aE0_e-E0}
    if pre_type == 2:
        Pre_edge_kws['nvict']=4
    else:
        pass
    autobk(Energy,mu=Ut,e0=E0,rbkg=Rbkg,kmin=k_min, kmax=k_max,kweight=Kweight,pre_edge_kws=Pre_edge_kws,group=exafs,_larch=mylarch)
    #print larch_builtins._groupitems(exafs,mylarch)
    xftf(exafs.k,exafs.chi,group=ft,kweight=3,kmin=3.0,kmax=12.0,_larch=mylarch)
    k_l = math.sqrt(0.2626*(nor_aE0_s-E0))
    k_h = math.sqrt(0.2626*(nor_aE0_e-E0))
    mask = np.concatenate([np.zeros(len(exafs.k[0:find_near(exafs.k,k_min)])),
                           np.ones(len(exafs.k[find_near(exafs.k,k_min):find_near(exafs.k,k_max)+1])),
                           np.zeros(len(exafs.k[find_near(exafs.k,k_max)+1:]))])
    return exafs.bkg, exafs.pre_edge, exafs.post_edge, exafs.chi, exafs.k, ft.r, ft.chir_mag, ft.chir_im

def find_near(Energy,req_Energy):
    array = np.absolute(Energy - req_Energy)
    return np.argmin(array)

def autofind_E0(energy,ut_):
    delta_ut = []
    i = 1
    while i+1 < len(ut_):
        delta_ut.append(((ut_[i+1]-ut_[i])/(energy[i+1]-energy[i])+(ut_[i]-ut_[i-1])/(energy[i]-energy[i-1]))/2)
        i += 1
    delta_ut.append(0.0)
    delta_ut.insert(0,0.0)
    return np.array(delta_ut)

def calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,nor_aE0_e,pre_type,degree,kweight,sf):
    delta_ut = []
    ut_wo_bk = np.array([])
    pre_edge = np.array([])
    post_edge = np.array([])
    i = 1
    while i+1 < len(ut_):
        delta_ut.append(((ut_[i+1]-ut_[i])/(energy[i+1]-energy[i])+(ut_[i]-ut_[i-1])/(energy[i]-energy[i-1]))/2)
        i += 1
    delta_ut.append(0.0)
    delta_ut.insert(0,0.0)
    #find nearest point
    startpoint = find_near(energy,fit_s)
    endpoint = find_near(energy,fit_e)
    print (startpoint)
    #print energy[startpoint:endpoint]
    if pre_type == 1:
        fit_r = np.polyfit(energy[startpoint:endpoint],ut_[startpoint:endpoint],1)
        print (fit_r)
        pre_edge = fit_r[0]*energy + fit_r[1]
        ut_wo_bk = ut_ - pre_edge
    elif pre_type == 2:
        fit_lin = np.polyfit(energy[startpoint:endpoint],ut_[startpoint:endpoint],1)
        def fit_f(x,C,D,Y):
            return Y + C/x**3 - D/x**4
        E_s_and_e = [energy[startpoint],energy[endpoint]]
        ut_s_and_e = [ut_[startpoint],ut_[endpoint]]
        X = np.vstack([E_s_and_e ,np.ones(len(E_s_and_e))]).T
        DAT = [energy[startpoint]**4*(ut_[startpoint]-fit_lin[1]),energy[endpoint]**4*(ut_[endpoint]-fit_lin[1])]
        c, d = linalg.lstsq(X,DAT)[0]
        opt, pconv = optim.curve_fit(fit_f,energy[startpoint:endpoint],ut_[startpoint:endpoint],p0=[c,d,fit_lin[1]])
        pre_edge = fit_f(energy,opt[0],opt[1],opt[2])
        ut_wo_bk = ut_ - pre_edge
    elif pre_type == 0:
        pre_edge = np.average(ut_[find_near(energy,fit_s):find_near(energy,fit_e)])
        ut_wo_bk = ut_ - pre_edge
    boundary = [find_near(energy,nor_aE0_s),find_near(energy,nor_aE0_e)]
    norm = np.average(ut_wo_bk[find_near(energy,E0+30.0):find_near(energy,E0+80.0)])
    k = np.array([])
    for e in energy:
        if E0 > e:
            k = np.append(k,(-1.0)*math.sqrt(0.2626*abs(e-E0)))
        else:
            k = np.append(k,math.sqrt(0.2626*abs(e-E0)))
    num = find_near(energy,E0)
    if k[num] < 0:
        num += 1
    array_weight = None
    if kweight != 0:
        array_weight = k[num:boundary[1]+1]**kweight
    #knots = []
    #if num_of_knots == 0:
    #    pass
    #else:
    #    j = 1
    #    delta_k = k[-1]/(num_of_knots+1)
    #    print delta_k
    #    while j < num_of_knots+1:
    #        knots.append(k[find_near(k,delta_k*j)])
    #        j += 1
    #knots = [k[find_near(k,2.0)],k[find_near(k,4.0)],k[find_near(k,6)],k[find_near(k,8.0)],k[find_near(k,10.0)],k[find_near(k,12.0)]]
    #knots_e = np.array(knots)**2/0.2626 + E0
    #print knots
    spline = interp.UnivariateSpline(k[num:boundary[1]+1],ut_wo_bk[num:boundary[1]+1]/norm,w = k[num:boundary[1]+1]**kweight, k=degree)
    spline_e = interp.UnivariateSpline(energy[num:boundary[1]+1],ut_wo_bk[num:boundary[1]+1]/norm, w = k[num:boundary[1]+1]**kweight, k=degree)
    spline.set_smoothing_factor(sf)
    post_edge = np.append(ut_wo_bk[:boundary[0]]/norm, spline(k[boundary[0]:boundary[1]+1]))
    post_edge = np.append(post_edge, ut_wo_bk[boundary[1]+1:]/norm)
    chi = ut_wo_bk/norm - post_edge
    bkg = pre_edge + post_edge*norm
    k_interp = np.array([])
    k_interp = np.append(k_interp,0.0)
    while k_interp[-1]-0.05 < k[-1]:
        k_interp = np.append(k_interp,k_interp[-1]+0.05)
    print (len(k_interp))
    chi_interp = np.interp(k_interp,k[num:],chi[num:])
    ft = larch_builtins._group(mylarch)
    #tft = larch_builtins._group(mylarch)
    #chi_q = larch_builtins._group(mylarch)
    xftf(k_interp,chi_interp,group=ft,kweight=3,kmin=3.0,kmax=12.0,_larch=mylarch)
    post_edge_ = np.append(ut_wo_bk[0:num]/norm,spline(k[num:]))
    return bkg, pre_edge, post_edge_*norm+pre_edge, chi_interp, k_interp, ft.r, ft.chir_mag, ft.chir_im, spline.get_knots()

def Cook_Sayers_rotine(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,nor_aE0_e,pre_type,degree,kweight,sf):
    print ('--- Cook and Sayers rotine ---')
    bkg, pre_edge, post_edge, chi_interp, \
    k_interp, ft_r, ft_chir_mag, ft_chir_im, knots = calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,
                                                                         nor_aE0_e,pre_type,degree,kweight,sf)
    print ('num of knots: ' + str(knots))
    r_low = find_near(ft_r,0.5)
    print ('low r is ' + str(r_low))
    H_R = np.average(ft_chir_mag[0:r_low+1])
    print ('H_R is ' + str(H_R))
    r_1A =  find_near(ft_r,1.0)
    r_5A = find_near(ft_r,5.0)
    H_M = np.max(ft_chir_mag[r_1A:r_5A])
    print ('H_M is ' + str(H_M))
    r_9A = find_near(ft_r,9.0)
    r_10A = find_near(ft_r,10.0)
    H_N = np.average(ft_chir_mag[r_9A:r_10A])
    print ('H_N is ' + str(H_N))
    def evaluation(H_R,H_M,H_N):
        if H_N > 0.1*H_M:
            return H_R - 0.1*H_M
        else:
            return (H_R-H_N) - 0.05*H_M
    i = 0
    Tol_ini = evaluation(H_R,H_M,H_N)
    print (Tol_ini)
    if Tol_ini < 0:
        return bkg, pre_edge, post_edge, chi_interp, k_interp, ft_r, ft_chir_mag, ft_chir_im, kweight, knots
    else:
        while i < 10:
            bkg, pre_edge, post_edge, chi_interp, \
            k_interp, ft_r, ft_chir_mag, ft_chir_im, knots = calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,
                                                                         nor_aE0_e,pre_type,degree,kweight-0.025,sf)
            r_low = find_near(ft_r,0.5)
            H_R = np.average(ft_chir_mag[0:r_low+1])
            r_1A =  find_near(ft_r,1.0)
            r_5A = find_near(ft_r,5.0)
            H_M = np.max(ft_chir_mag[r_1A:r_5A])
            r_9A = find_near(ft_r,9.0)
            r_10A = find_near(ft_r,10.0)
            H_N = np.average(ft_chir_mag[r_9A:r_10A])
            Tol_plus = evaluation(H_R,H_M,H_N)
            print ('Evaluation plus: ' + str(Tol_plus))
            bkg, pre_edge, post_edge, chi_interp, \
            k_interp, ft_r, ft_chir_mag, ft_chir_im, knots = calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,
                                                                         nor_aE0_e,pre_type,degree,kweight+0.05,sf)
            r_low = find_near(ft_r,0.5)
            H_R = np.average(ft_chir_mag[0:r_low+1])
            r_1A =  find_near(ft_r,1.0)
            r_5A = find_near(ft_r,5.0)
            H_M = np.max(ft_chir_mag[r_1A:r_5A])
            r_9A = find_near(ft_r,9.0)
            r_10A = find_near(ft_r,10.0)
            H_N = np.average(ft_chir_mag[r_9A:r_10A])
            Tol_minus  = evaluation(H_R,H_M,H_N)
            print ('Evaluation minus: ' + str(Tol_minus))
            if Tol_ini < Tol_minus and Tol_ini < Tol_plus:
                print ('Tol_ini is minimum.')
                break
                #return bkg, pre_edge, post_edge, chi_interp, k_interp, ft_r, ft_chir_mag, ft_chir_im
            elif Tol_minus - Tol_ini < 0 and Tol_ini - Tol_plus < 0:
                kweight -= 0.025
                Tol_ini = Tol_minus
                i += 1
            elif Tol_minus - Tol_ini > 0 and Tol_ini - Tol_plus > 0:
                kweight += 0.05
                Tol_ini = Tol_plus
                i += 1
            elif Tol_minus - Tol_ini < 0 and Tol_plus - Tol_ini < 0 and abs(Tol_minus - Tol_ini) > abs(Tol_plus - Tol_ini):
                kweight -= 0.025
                Tol_ini = Tol_minus
                i += 1
            elif Tol_minus - Tol_ini < 0 and Tol_plus - Tol_ini < 0 and abs(Tol_minus - Tol_ini) < abs(Tol_plus - Tol_ini):
                kweight += 0.05
                Tol_ini = Tol_plus
                i += 1
            elif sf < 0.0:
                break
            else:
                kweight += 0.01
                Tol_ini = Tol_minus
                i+= 1
        bkg, pre_edge, post_edge, chi_interp, \
        k_interp, ft_r, ft_chir_mag, ft_chir_im, knots = calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,
                                                                         nor_aE0_e,pre_type,degree,kweight,sf)
        return bkg, pre_edge, post_edge, chi_interp, k_interp, ft_r, ft_chir_mag, ft_chir_im, kweight, knots


def evaluation(x,energy,ut_, E0, fit_s,fit_e,nor_aE0_s,nor_aE0_e,pre_type,degree,kweight):
    bkg, pre_edge, post_edge, chi_interp, \
    k_interp, ft_r, ft_chir_mag, ft_chir_im, knots = calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,
                                                                         nor_aE0_e,pre_type,degree,kweight,x)
    r_low = find_near(ft_r,0.25)
    #print 'low r is ' + str(r_low)
    H_R = np.average(ft_chir_mag[0:r_low+1])
    #print 'H_R is ' + str(H_R)
    r_1A =  find_near(ft_r,1.0)
    r_5A = find_near(ft_r,5.0)
    H_M = np.max(ft_chir_mag[r_1A:r_5A])
    #print 'H_M is ' + str(H_M)
    r_9A = find_near(ft_r,9.0)
    r_10A = find_near(ft_r,10.0)
    H_N = np.average(ft_chir_mag[r_9A:r_10A])
    #print 'H_N is ' + str(H_N)
    if H_N > 0.1*H_M:
        return H_R - 0.1*H_M
    else:
        return (H_R-H_N) - 0.05*H_M

def Cook_Sayers_rotine_(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,nor_aE0_e,pre_type,degree,kweight,sf):
    print ('--- Cook and Sayers rotine ---')

    def const(x):
        return x
    result = optim.minimize(evaluation,x0=[sf],method='BFGS',args=tuple([energy,ut_, E0, fit_s,fit_e,nor_aE0_s,nor_aE0_e,pre_type,
                                                                          degree,sf]),constraints={'type':'ineq','fun':const})
    print (result)
    array = result.x
    if result.success:
        bkg, pre_edge, post_edge, chi_interp,\
            k_interp, ft_r, ft_chir_mag, ft_chir_im, knots = calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,
                                                                            nor_aE0_e,pre_type,degree,kweight,array[0])
        return bkg, pre_edge, post_edge, chi_interp, k_interp, ft_r, ft_chir_mag, ft_chir_im,  array[0]
    else:
        bkg, pre_edge, post_edge, chi_interp,\
            k_interp, ft_r, ft_chir_mag, ft_chir_im, knots = calc_exafs_SplineSmoothing(energy,ut_, E0, fit_s,fit_e,nor_aE0_s,
                                                                            nor_aE0_e,pre_type,degree,kweight,array[0])
        return bkg, pre_edge, post_edge, chi_interp, k_interp, ft_r, ft_chir_mag, ft_chir_im, array[0]
    #return result




def calc_1st_derivative(energy,ut):
    delta_ut_ = []
    i = 1
    while i+1 < len(ut):
        delta_ut_.append(((ut[i+1]-ut[i])/(energy[i+1]-energy[i])+(ut[i]-ut[i-1])/(energy[i]-energy[i-1]))/2)
        i += 1
    delta_ut_.append(0.0)
    delta_ut_.insert(0,0.0)
    return np.array(delta_ut_), np.argmax(delta_ut_)


def calc_FT(k,chi,kmin_,kmax_,kweight_):
    ft = larch_builtins._group(mylarch)
    xftf(k,chi,group=ft,kweight=kweight_,kmin=kmin_,kmax=kmax_,_larch=mylarch)
    return ft.r, ft.chir_mag, ft.chir_im
