#! ~/Build/bin/python
# -*- coding: utf-8 -*-
# simple.py
import sys
import os
import string
import glob
import re
import yaml
#import tifffile as TIFF
import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import shutil



from PySide import QtCore, QtGui
#from forPySide import Ui_MainWindow

home_dir = QtCore.QDir()
text = home_dir.homePath()
cwd = os.getcwd()

Test_Dat = cwd + "/" + "Pt10"
conf = cwd + "/" + "PFBL12C2.conf"
str_tconst = open(conf).read()
DT = yaml.load(str_tconst)
#print shaping_t
print Test_Dat

class params:
	D = None
	ignore_or_not = []
	angles=[]
	i0=[]
	ICR=[]
	darray=np.empty([1,1])
	Energy=[]
	dat=[]
	len_eff=None
	sum=np.ndarray([0])
	shaping_time="us025"

f = open(Test_Dat,"r")
i = 0
for line in f:
	line.rstrip()
	if re.match(r".+D=(.+)A.+", line):
		params.D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
		print str(params.D)
	elif re.match(r"\s+Angle\(c\).+", line):
		t_array = line.split()
		print t_array[0]
	elif re.match(r"\s+Mode", line):
		#print line
		t_array = line.split()
		params.ignore_or_not = t_array[3:23]
		print params.ignore_or_not
	elif re.match(r"\s+Offset", line):
		pass
	elif len(line.split()) > 23:
		t_array = line.split()
		params.angles.append(t_array[1])
		params.i0.append(t_array[22])
		params.dat.append(t_array[3:23])
		params.ICR.append(t_array[23:])
print len(params.dat[0])
#params.darray.resize(20,len(params.dat))

k = 0
j = 0
l = 0
while k < 20:
	if params.ignore_or_not[k] != "0":
		#print params.ignore_or_not[k]
		l += 1
		params.darray.resize(l,len(params.dat))
		while j < len(params.dat):
			#print j
			params.darray[l-1][j] = float(params.dat[j][k])*(1+float(params.ICR[j][k])*float(DT["PF"]["individual"]["preamp"][k]))/(1-float(params.ICR[j][k])*float(DT["PF"]["individual"]["amp"][params.shaping_time][k]))
			j += 1
	k += 1
params.len_eff = l
k = 0
params.sum.resize(len(params.dat))
while k < params.len_eff-1:
	j = 0
	if k == 0:
		while j < len(params.dat):
			params.sum[j] = params.darray[k][j]
			j += 1
	elif k >= 0:
		params.sum = np.add(params.sum,params.darray[k])
	k += 1
#print params.sum
#print k
fout = open("out.dat","w")
fout.write("#Energy, ut\n")
print len(params.i0)
j = 0
while j < len(params.sum):
	E = 12398.52/(2*float(params.D)*np.sin(float(params.angles[j])/180*np.pi))
	ut = params.sum[j]/float(params.i0[j])
	#print ut
	str_ = "%7.2f, %1.8f\n" %(E,ut)
	#print str_
	fout.write(str_)
	j += 1
	

def read_and_conv_dat(Test_Dat,outname):
		f = open(Test_Dat,"r")
		i = 0
		for line in f:
			line.rstrip()
			if re.match(r".+D=(.+)A.+", line):
				params.D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
				print str(params.D)
			elif re.match(r"\s+Angle\(c\).+", line):
				t_array = line.split()
				print t_array[0]
			elif re.match(r"\s+Mode", line):
				t_array = line.split()
				params.ignore_or_not = t_array[3:23]
				print params.ignore_or_not
			elif re.match(r"\s+Offset", line):
				pass
			elif len(line.split()) > 23:
				t_array = line.split()
				params.angles.append(t_array[1])
				params.i0.append(t_array[22])
				params.dat.append(t_array[3:23])
				params.ICR.append(t_array[23:])
				print len(params.dat[0])
		k = 0
		j = 0
		l = 0
		micro = 1/1000000
		while k < 20:
			if params.ignore_or_not[k] != "0":
				l += 1
				params.darray.resize(l,len(params.dat))
				while j < len(params.dat):
					params.darray[l-1][j] = float(params.dat[j][k])*(1+micro*float(params.ICR[j][k])*float(DT["PF"]["individual"]["preamp"][k]))/(1-micro*float(params.ICR[j][k])*float(DT["PF"]["individual"]["amp"][params.shaping_time][k]))
					j += 1
			k += 1
		params.len_eff = l
		k = 0
		params.sum.resize(len(params.dat))
		while k < params.len_eff-1:
			j = 0
			if k == 0:
				while j < len(params.dat):
					params.sum[j] = params.darray[k][j]
					j += 1
			elif k >= 0:
				params.sum = np.add(params.sum,params.darray[k])
			k += 1
		fout = open(outname,"w")
		fout.write("#Energy, ut\n")
		print len(params.i0)
		j = 0
		while j < len(params.sum):
			E = 12398.52/(2*float(params.D)*np.sin(float(params.angles[j])/180*np.pi))
			ut = params.sum[j]/float(params.i0[j])
			str_ = "%7.2f, %1.8f\n" %(E,ut)
			fout.write(str_)
			j += 1
        
        def plot():
        	Dat=""
			d_out=""
        	for d_file in params.d_rbs:
        		if d_file.isChecked():
        			Dat = params.dir + "/" + d_file.objectName()
				if re.match(r"(.+)\.\d+",d_file.objectName()) is None:
					d_out = d_file.objectName() + "_000" + ".dat"
				elif re.match(r"(.+)\.(\d+)",d_file.objectName()):
					t_line = d_file.objectName().split(".")
					d_out = t_line[0] + "_" + t_line[1]  + ".dat"
				print d_out
				read_and_conv_dat(Dat,d_out)
        			break
  