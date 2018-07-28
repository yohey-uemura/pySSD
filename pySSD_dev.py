import sys
import os
import string
import glob
import re
import yaml
import math
# import StringIO as IO
import io as IO
import matplotlib


matplotlib.use('Qt5Agg')
#matplotlib.rcParams['backend.qt5'] = 'PySide2'

#import matplotlib.pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import numpy as np
import numpy.linalg as linalg
import scipy.optimize as optim
from scipy.signal import savgol_filter
import shutil
import pandas as pd
import use_larch

#from PySide2 import QtCore, QtWidgets, QtGui
from PyQt5 import QtCore, QtWidgets, QtGui
app = QtWidgets.QApplication(sys.argv)
screen_resolution = app.desktop().screenGeometry()
# screen_resolution = Desktop.screenGeometry()
resolution = str(screen_resolution.width()) +','+str(screen_resolution.height())

from UI_pySSD_win_2 import Ui_MainWindow

from plot_dialog import Ui_Dialog

from CH_BL36XU import Ui_Form_BL36XU as wid_BL36XU
from CH_BL14B1 import Ui_Form_BL14B1 as wid_BL14B1
from SDD_7element import Ui_Form as wid_7elementsSDD
from SSD_DUBBLE import Ui_Form as wid_DUBBLE

home_dir = QtCore.QDir()
text = home_dir.homePath()
cwd = os.getcwd()

#print shaping_t
list = ["no correction", "0.25 us", "0.50 us", "1.00 us", "2.00 us", "3.00 us", "6.00 us"]

def hex2rgb(hexcode):
    rgb = [int(hexcode[1:3],16),int(hexcode[3:5],16),int(hexcode[5:],16)]
    return rgb


class params:
    D = None
    ignore_or_not = []
    angles = []
    i0 = []
    ICR = []
    darray = np.empty([1, 1])
    Energy = []
    dat = []
    which_BL = "BL12C"
    len_eff = None
    sum = np.ndarray([0])
    dir = ""
    current_dfile = ""
    outdir = ""
    current_ofile = ""
    dfiles = []
    d_rbs = []
    dfiles_36XU = []
    d_rbs_36XU = []
    aq_time = []
    shaping_time = ""
    grid = QtWidgets.QGridLayout()
    grid2 = QtWidgets.QGridLayout()
    grid3 = QtWidgets.QGridLayout()
    grid4 = QtWidgets.QGridLayout()
    grid5 = QtWidgets.QGridLayout()
    grid6 = QtWidgets.QGridLayout()
    grid7 = QtWidgets.QGridLayout()
    grid_dialog = QtWidgets.QGridLayout()
    cbs = []
    ex3 = []
    E_intp = []
    path_to_ex3 = ""
    colors = ["Red", "Blue", "Green", "DeepPink", "Black", "Orange", "Brown","OrangeRed",
               "DarkRed","Crimson", "DarkBlue", "DarkGreen", "Hotpink","Coral",
              "DarkMagenta",  "FireBrick", "GoldenRod", "Grey",
              "Indigo", "MediumBlue", "MediumVioletRed"]
    colors_in_rgb = ["#FF0000","#0000FF", "#00FF00" ,"#FF1493","#000000","#FFA500","#A52A2A","#FF4500",
                     "#8B0000","#DC143C","#00008B","#006400","#FF69B4","#FF7F50",
                     "#8B008B","#B22222","#DAA520","#BEBEBE",
                     "#00416A","#0000CD","#C71585"]
    rgb_color = ["#FF0000","#0000FF","#00CC00","#FF1493","#000000"]
    if sys.platform == 'win32':
        homedir = os.environ['HOMEPATH']
    else:
        homedir = os.environ['HOME']
    xanes =[]
    exafs = []
    # xanes_data = {}
    path_to_xanes = ""
    path_to_exafs = ""
    data_length =""
    exafs_rb = QtWidgets.QButtonGroup()
    data_and_conditions = {}
    current_EXAFS = ''

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__()
#        QtWidgets.QMainWindow.__init__(self, parent)
        self.u = Ui_MainWindow()
        self.u.setupUi(self)
        self.u.comboBox.addItems(list)
        self.u.comboBox_2.addItems(["K", "L"])
        self.u.comboBox_3.addItems(["K", "L"])
        self.u.comboBox_4.addItems(["PFBL9A", "PFBL12C", "PFNW10A", "SP8_01B1"])
        self.u.comboBox_5.addItems(["K", "L"])
        self.u.comboBox_6.addItems(["Transmission", "Fluorescence", "SSD_wCorrection"])
        self.u.rb_sum.toggle()
        self.u.tabWidget.setTabEnabled(4,False)
        scroll_layout = QtWidgets.QVBoxLayout()
        scroll_widgets = QtWidgets.QWidget()
        scroll_widgets.setLayout(scroll_layout)
        self.u.scrollArea.setWidget(scroll_widgets)
        params.cbs = [self.u.ch_1, self.u.ch_2, self.u.ch_3,
                      self.u.ch_4, self.u.ch_5, self.u.ch_6, self.u.ch_7,
                      self.u.ch_8, self.u.ch_9, self.u.ch_10, self.u.ch_11, self.u.ch_12,
                      self.u.ch_13, self.u.ch_14,self.u.ch_15, self.u.ch_16,
                      self.u.ch_17, self.u.ch_18, self.u.ch_19]
        scroll_layout2 = QtWidgets.QVBoxLayout()
        scroll_widgets2 = QtWidgets.QWidget()
        scroll_widgets2.setLayout(scroll_layout2)
        self.u.scrollArea_2.setWidget(scroll_widgets2)
        self.u.pushButton_8.setEnabled(False)
        params.rb_REX = [self.u.radioButton, self.u.radioButton_3, self.u.radioButton_5]
        # self.u.comboBox_bk.addItems(['average','linear','victoreen'])
        self.dialog = QtWidgets.QDialog()
        self.plot_dialog = Ui_Dialog()
        self.plot_dialog.setupUi(self.dialog)
        self.plot_dialog.comboBox_Ftype.addItems(['average','linear','victoreen'])

        def toggle_rbs_REX():
            for rb in params.rb_REX:
                rb.toggle()

        for rb in params.rb_REX:
            rb.setObjectName(".ex3")
            rb.toggle()
            rb.clicked.connect(toggle_rbs_REX)
        params.rb_Athena = [self.u.radioButton_2, self.u.radioButton_4, self.u.radioButton_6]

        def toggle_rbs_ATHENA():
            for rb in params.rb_Athena:
                rb.toggle()

        for rb in params.rb_Athena:
            rb.setObjectName(".dat")
            rb.clicked.connect(toggle_rbs_ATHENA)

        scroll_layout3 = QtWidgets.QVBoxLayout()
        scroll_widgets3 = QtWidgets.QWidget()
        scroll_widgets3.setLayout(scroll_layout3)
        self.u.scrollArea_3.setWidget(scroll_widgets3)

        scroll_layout4 = QtWidgets.QVBoxLayout()
        scroll_widgets4 = QtWidgets.QWidget()
        scroll_widgets4.setLayout(scroll_layout4)
        self.u.scrollArea_4.setWidget(scroll_widgets4)

        for cb in params.cbs:
            cb.setAutoFillBackground(True)
            plt = cb.palette()
            if params.cbs.index(cb) >= 0 and params.cbs.index(cb) <=2:
                #plt.setColor(cb.backgroundRole(), params.rgb_color[0])
                RGBCOLOR = hex2rgb(params.rgb_color[0])
                plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            elif params.cbs.index(cb) >= 3 and params.cbs.index(cb) <=6:
                #plt.setColor(cb.backgroundRole(), params.rgb_color[1])\
                RGBCOLOR = hex2rgb(params.rgb_color[1])
                plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            elif params.cbs.index(cb) >= 7 and params.cbs.index(cb) <=11:
                #plt.setColor(cb.backgroundRole(), params.rgb_color[2])
                RGBCOLOR = hex2rgb(params.rgb_color[2])
                plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            elif params.cbs.index(cb) >= 12 and params.cbs.index(cb) <=15:
                #plt.setColor(cb.backgroundRole(), params.rgb_color[3])
                RGBCOLOR = hex2rgb(params.rgb_color[3])
                plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            elif params.cbs.index(cb) >= 16 and params.cbs.index(cb) <=18:
                #plt.setColor(cb.backgroundRole(), params.rgb_color[4])
                RGBCOLOR = hex2rgb(params.rgb_color[4])
                plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            RGBCOLOR = hex2rgb("#FFFFFF")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            cb.setPalette(plt)
        palette = self.u.frame.palette()
        RGBCOLOR = hex2rgb("#808080")
        palette.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))


        #Figure for Transmission & Fluorescence
        fig4 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        # position = 111
        ax4 = fig4.add_subplot(111)
        ax4.set_xlabel("E / eV")
        ax4.set_ylabel("$\mu$ t")
        canvas4 = FigureCanvas(fig4)
        navibar_4 = NavigationToolbar(canvas4, self.u.widget_4)
        self.u.widget_4.setLayout(params.grid4)
        params.grid4.addWidget(canvas4, 0, 0)
        params.grid4.addWidget(navibar_4)

        #Figure for SSD (left)
        fig = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        ax = fig.add_subplot(111)
        ax.set_xlabel("E / eV")
        ax.set_ylabel("$\mu$ t")
        canvas = FigureCanvas(fig)
        self.u.widget.setLayout(params.grid)
        navibar_1 = NavigationToolbar(canvas, self.u.widget)
        params.grid.addWidget(canvas, 0, 0)
        params.grid.addWidget(navibar_1)
        # print "--- item at----"
        # print params.grid.itemAt(0).widget().figure
        # print ax.figure

        #Figure for SSD (right)
        fig2 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        ax2 = fig2.add_subplot(111)
        ax2.set_xlabel("E / eV")
        ax2.set_ylabel("$\mu$ t")
        canvas2 = FigureCanvas(fig2)
        self.u.widget_2.setLayout(params.grid2)
        navibar_2 = NavigationToolbar(canvas2, self.u.widget_2)
        self.u.widget_2.setLayout(params.grid2)
        params.grid2.addWidget(canvas2, 0, 0)
        params.grid2.addWidget(navibar_2)


        #Figure for XANES Compare
        self.fig5 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax5 = self.fig5.add_subplot(111)
        self.ax5.set_xlabel("E / eV")
        self.ax5.set_ylabel("$\mu$ t")
        self.canvas5 = FigureCanvas(self.fig5)
        self.navibar_5 = NavigationToolbar(self.canvas5, self.u.widget_5)
        self.u.widget_5.setLayout(params.grid5)
        params.grid5.addWidget(self.canvas5, 0, 0)
        params.grid5.addWidget(self.navibar_5)

        #Figure for XANES plot (dialog)
        self.fig_dialog = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax_dialog = self.fig_dialog.add_subplot(121)
        self.ax_dialog.set_xlabel("E / eV")
        self.ax_dialog.set_ylabel("$\mu$ t")
        self.ax_dialog_norm = self.fig_dialog.add_subplot(122)
        self.ax_dialog_norm.set_xlabel("E / eV")
        self.ax_dialog_norm.set_ylabel("$\mu$ t")
        self.canvas_dialog = FigureCanvas(self.fig_dialog)
        self.navibar_dialog = NavigationToolbar(self.canvas_dialog, self.plot_dialog.widget)
        self.plot_dialog.widget.setLayout(params.grid_dialog)
        params.grid_dialog.addWidget(self.canvas_dialog, 0, 0)
        params.grid_dialog.addWidget(self.navibar_dialog)

        #Figure for interpolation and summation
        fig3 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        ax3 = fig3.add_subplot(111)
        ax3.set_xlabel("E / eV")
        ax3.set_ylabel("$\mu$ t")
        canvas3 = FigureCanvas(fig3)
        navibar_3 = NavigationToolbar(canvas3, self.u.widget_3)
        self.u.widget_3.setLayout(params.grid3)
        params.grid3.addWidget(canvas3, 0, 0)
        params.grid3.addWidget(navibar_3)

        def change_CB3():
            self.u.comboBox_3.setCurrentIndex(self.u.comboBox_2.currentIndex())

        def change_lineEdit2():
            self.u.lineEdit_2.clear()
            self.u.lineEdit_2.setText(self.u.lineEdit.text())

        def define_outdir():
            self.u.textBrowser.clear()
            FO_dialog = QtWidgets.QFileDialog(self)
            params.outdir = FO_dialog.getExistingDirectory(None, params.dir)
            self.u.textBrowser.append(params.outdir)
            if self.u.textBrowser_2.toPlainText() == "":
                self.u.textBrowser_2.append(params.outdir)

        def define_outdir_for_sum():
            self.u.textBrowser_2.clear()
            FO_dialog = QtWidgets.QFileDialog(self)
            directory = ""
            if params.outdir == "":
                directory = params.outdir
            else:
                directory = home_dir
            params.outdir = FO_dialog.getExistingDirectory(None, directory)
            self.u.textBrowser_2.append(params.outdir)

        def read_dat(Test_Dat):
            params.ignore_or_not = []
            params.angles = []
            params.aq_time = []
            params.i0 = []
            params.dat = []
            params.ICR = []
            params.Energy = []
            params.darray = np.empty([1, 1])
            f = open(Test_Dat, "r")
            i = 0
            for line in f:
                line.rstrip()
                if re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line):
                    if re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "BL9A":
                        self.u.comboBox_4.setCurrentIndex(0)
                    elif re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "BL12C":
                        self.u.comboBox_4.setCurrentIndex(1)
                    elif re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "NW10A":
                        self.u.comboBox_4.setCurrentIndex(2)
                    elif re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "01b1":
                        self.u.comboBox_4.setCurrentIndex(3)
                elif re.match(r".+D=(.+)A.+", line):
                    params.D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                #print str(params.D)
                elif re.match(r"\s+Angle\(c\).+", line):
                    t_array = line.split()
                #print t_array[0]
                elif re.match(r"\s+Mode", line):
                    t_array = line.split()
                    params.ignore_or_not = t_array[3:23]
                #print params.ignore_or_not
                elif re.match(r"\s+Offset", line):
                    pass
                elif len(line.split()) > 23:
                    t_array = line.split()
                    params.angles.append(t_array[1])
                    params.aq_time.append(float(t_array[2]))
                    params.i0.append(float(t_array[22]))
                    params.dat.append(t_array[3:23])
                    params.ICR.append(t_array[23:])
                #print i
                i += 1
            print (params.aq_time)
            k = 0
            while k < 19:
                if params.ignore_or_not[k] == "0":
                    params.cbs[k].setCheckState(QtCore.Qt.Unchecked)
                    params.cbs[k].setEnabled(False)
                elif params.ignore_or_not[k] != "0":
                    if self.u.cB_keep_condition.isChecked():
                        pass
                    else:
                        params.cbs[k].setCheckState(QtCore.Qt.Checked)
                k += 1
            params.darray.resize(19, len(params.dat))
            k = 0
            while k < 19:
                j = 0
                while j < len(params.dat):
                    params.darray[k][j] = float(params.dat[j][k])
                    j += 1
                k += 1
            #print params.darray[1]
            j = 0
            while j < len(params.dat):
                E = 12398.52 / (2 * float(params.D) * np.sin(float(params.angles[j]) / 180 * np.pi))
                params.Energy.append(E)
                j += 1

        def return_new_axis(gridlayout):
            t_fig = gridlayout.itemAt(0).widget().figure
            num = len(t_fig.axes)
            for axis in t_fig.axes:
                t_fig.delaxes(axis)
            array_axis = []
            for i in range(0,num):
                position = eval('1'+str(num)+str(i+1))
                array_axis.append(t_fig.add_subplot(position))
            return array_axis


        def plot_each_ch():
            conf = cwd + "/" + self.u.comboBox_4.currentText() + ".conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            # params.grid.removeItem(params.grid.itemAt(0))
            # params.grid.removeItem(params.grid.itemAt(0))
            # fig = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=
            # fig = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
            # fig = params.grid.itemAt(0).widget().figure
            ax_array = return_new_axis(params.grid)
            # ax = fig.add_subplot(111)
            ax = ax_array[0]
            ax.set_xlabel("E / eV")
            ax.set_ylabel("$\mu$ t")
            # canvas = FigureCanvas(fig)
            # navibar_1 = NavigationToolbar(canvas, self.u.widget)

            # params.grid2.removeItem(params.grid2.itemAt(0))
            # params.grid2.removeItem(params.grid2.itemAt(0))
            # fig2 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
            # ax2 = fig2.add_subplot(111)
            ax_array = return_new_axis(params.grid2)
            ax2 = ax_array[0]
            ax2.set_xlabel("E / eV")
            ax2.set_ylabel("$\mu$ t")
            # canvas2 = FigureCanvas(fig2)
            # navibar_2 = NavigationToolbar(canvas2, self.u.widget_2)
            if self.u.comboBox.currentText() == "no correction":
                for cb in params.cbs:
                    if cb.isChecked():
                        ut = np.divide(np.array(params.darray[params.cbs.index(cb)]), np.array(params.i0))
                        sum = np.add(sum, np.array(params.darray[params.cbs.index(cb)]))
                        if params.cbs.index(cb) >= 0 and params.cbs.index(cb) <=2:
                            ax.plot(params.Energy, ut, color=params.colors[0])
                        elif params.cbs.index(cb) >= 3 and params.cbs.index(cb) <=6:
                            ax.plot(params.Energy, ut, color=params.colors[1])
                        elif params.cbs.index(cb) >= 7 and params.cbs.index(cb) <=11:
                            ax.plot(params.Energy, ut, color=params.colors[2])
                        elif params.cbs.index(cb) >= 12 and params.cbs.index(cb) <=15:
                            ax.plot(params.Energy, ut, color=params.colors[3])
                        elif params.cbs.index(cb) >= 16 and params.cbs.index(cb) <=18:
                            ax.plot(params.Energy, ut, color=params.colors[4])
                        #ax.plot(params.Energy, ut, color=params.colors[params.cbs.index(cb)])
            elif self.u.comboBox.currentText() != "no correction":
                if self.u.comboBox.currentText() == "0.25 us":
                    params.shaping_time = "us025"
                elif self.u.comboBox.currentText() == "0.50 us":
                    params.shaping_time = "us050"
                elif self.u.comboBox.currentText() == "1.00 us":
                    params.shaping_time = "us100"
                elif self.u.comboBox.currentText() == "2.00 us":
                    params.shaping_time = "us200"
                elif self.u.comboBox.currentText() == "3.00 us":
                    params.shaping_time = "us300"
                elif self.u.comboBox.currentText() == "6.00 us":
                    params.shaping_time = "us600"
                micro = math.pow(10, -6)
                k = 0
                while k < 19:
                    if params.cbs[k].isChecked():
                        j = 0
                        ut = np.zeros(len(params.Energy))
                        while j < len(params.Energy):
                            ut[j] = params.darray[k][j] * (
                                1 + micro * float(params.ICR[j][k]) / float(params.aq_time[j]) * float(
                                    DT["PF"]["individual"]["preamp"][k])) / (
                                        1 - micro * float(params.ICR[j][k]) / float(params.aq_time[j]) * float(
                                            DT["PF"]["individual"]["amp"][params.shaping_time][k]))
                            #ut[j] = params.darray[k][j]/(1-micro*float(params.ICR[j][k])/float(params.aq_time[j])*(float(DT["PF"]["individual"]["amp"][params.shaping_time][k])+float(DT["PF"]["individual"]["preamp"][k])))
                            sum[j] += params.darray[k][j] * (
                                1 + micro * float(params.ICR[j][k]) / float(params.aq_time[j]) * float(
                                    DT["PF"]["individual"]["preamp"][k])) / (
                                          1 - micro * float(params.ICR[j][k]) / float(params.aq_time[j]) * float(
                                              DT["PF"]["individual"]["amp"][params.shaping_time][k]))
                            #sum[j] += params.darray[k][j]/(1-micro*float(params.ICR[j][k])/float(params.aq_time[j])*(float(DT["PF"]["individual"]["amp"][params.shaping_time][k])+float(DT["PF"]["individual"]["preamp"][k])))
                            j += 1
                        if k >= 0 and k <=2:
                            ax.plot(params.Energy, np.divide(ut, params.i0), color=params.colors[0])
                        elif k >= 3 and k <=6:
                            ax.plot(params.Energy, np.divide(ut, params.i0), color=params.colors[1])
                        elif k >= 7 and k <=11:
                            ax.plot(params.Energy, np.divide(ut, params.i0), color=params.colors[2])
                        elif k >= 12 and k <=15:
                            ax.plot(params.Energy, np.divide(ut, params.i0), color=params.colors[3])
                        elif k >= 16 and k <=18:
                            ax.plot(params.Energy, np.divide(ut, params.i0), color=params.colors[4])
                        #ax.plot(params.Energy, np.divide(ut, params.i0), color=params.colors[k])
                    k += 1
            # params.grid.addWidget(canvas, 0, 0)
            # params.grid.addWidget(navibar_1)
            ax2.plot(params.Energy, np.divide(sum, params.i0))
            canvas.draw()
            canvas2.draw()
            # params.grid2.addWidget(canvas2, 0, 0)
            # params.grid2.addWidget(navibar_2)

        def select_or_release_all():
            checked_cb = []
            for cb in params.cbs:
                if cb.isChecked():
                    checked_cb.append(cb)
            if len(checked_cb) > 0:
                self.u.pushButton_5.setText("Select All")
                for cb in checked_cb:
                    cb.setCheckState(QtCore.Qt.Unchecked)
            elif len(checked_cb) == 0:
                self.u.pushButton_5.setText("Release All")
                k = 0
                while k < 19:
                    if params.ignore_or_not[k] != "0":
                        params.cbs[k].setCheckState(QtCore.Qt.Checked)
                    elif params.ignore_or_not[k] == "0":
                        params.cbs[k].setEnabled(False)
                    k += 1
            plot_each_ch()

        def plot_():
            params.current_dfile = ""
            params.current_ofile = ""
            if self.u.cB_keep_condition.isChecked():
                for cb in params.cbs:
                    cb.setEnabled(True)
            else:
                for cb in params.cbs:
                    cb.setEnabled(True)
                    cb.setCheckState(QtCore.Qt.Unchecked)
            for t_rb in params.d_rbs:
                if t_rb.isChecked():
                    params.current_dfile = params.dir + "/" + t_rb.objectName()
                    if re.match(r"(.+)\.\d+", t_rb.objectName()) is None:
                        #params.current_ofile = o_dir + "/" + t_rb.objectName() + "_000" + ".ex3"
                        break
                    elif re.match(r"(.+)\.(\d+)", t_rb.objectName()):
                        t_line = t_rb.objectName().split(".")
                        #params.current_ofile =o_dir + "/" + t_line[0] + "_" + t_line[1]  + ".ex3"
                        break
            read_dat(params.current_dfile)
            plot_each_ch()

        def func_for_rb():
            plot_()
            self.u.pushButton_5.setText("Release all")

        def openFiles():
            print ("here")
            while scroll_layout.count() > 0:
                b = scroll_layout.takeAt(len(params.d_rbs) - 1)
                params.dfiles.pop()
                params.d_rbs.pop()
                b.widget().deleteLater()
            self.u.cB_keep_condition.setCheckState(QtCore.Qt.Unchecked)
            dat_dir = home_dir.homePath()
            if params.dir == "":
                dat_dir = home_dir.homePath()
            elif params.dir != "":
                dat_dir = params.dir
            FO_dialog = QtWidgets.QFileDialog(self)
            #files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir)
            files = FO_dialog.getOpenFileNames(None, 'Open dat files', dat_dir,
                                              "dat files(*)")
            if files:
                finfo = QtCore.QFileInfo(files[0][0])
            
                params.dir = finfo.path()
                for fname in files[0]:
                    info = QtCore.QFileInfo(fname)
                    params.dfiles.append(info.fileName())
                for d_file in params.dfiles:
                    rb = QtWidgets.QRadioButton(d_file)
                    rb.setObjectName(d_file)
                    params.d_rbs.append(rb)
                    scroll_layout.addWidget(rb)
                for t_rb in params.d_rbs:
                    t_rb.clicked.connect(func_for_rb)
                params.d_rbs[0].click

        def Save():
            conf = cwd + "/" + self.u.comboBox_4.currentText() + ".conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            if self.u.radioButton.isChecked():
                exd = self.u.radioButton.objectName()
            else:
                exd = self.u.radioButton_2.objectName()
            if params.outdir == "":
                o_dir = params.dir
            elif os.path.exists(params.outdir):
                o_dir = params.outdir
            for t_rb in params.d_rbs:
                if t_rb.isChecked():
                    if re.match(r"(.+)\.\d+", t_rb.objectName()) is None:
                        params.current_ofile = o_dir + "/" + t_rb.objectName() + "_000" + exd
                        break
                    elif re.match(r"(.+)\.(\d+)", t_rb.objectName()):
                        t_line = t_rb.objectName().split(".")
                        params.current_ofile = o_dir + "/" + t_line[0] + "_" + t_line[1] + exd
                        break
            out = open(params.current_ofile, "w")
            if self.u.radioButton.isChecked():
                line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                atom = "*EX_ATOM=" + self.u.lineEdit.text() + "\n"
                edge = "*EX_EDGE=" + self.u.comboBox_2.currentText() + "\n"
                line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                line3 = "\n[EX_BEGIN]\n"
                out.write(line + atom + edge + line2 + line3)
            else:
                out.write("#Energy  ut\n")
            if self.u.comboBox.currentText() == "no correction":
                for cb in params.cbs:
                    if cb.isChecked():
                        sum = np.add(sum, np.array(params.darray[params.cbs.index(cb)]))
            elif self.u.comboBox.currentText() != "no correction":
                if self.u.comboBox.currentText() == "25 us":
                    params.shaping_time = "us025"
                elif self.u.comboBox.currentText() == "50 us":
                    params.shaping_time = "us050"
                elif self.u.comboBox.currentText() == "100 us":
                    params.shaping_time = "us100"
                elif self.u.comboBox.currentText() == "200 us":
                    params.shaping_time = "us200"
                elif self.u.comboBox.currentText() == "300 us":
                    params.shaping_time = "us300"
                elif self.u.comboBox.currentText() == "600 us":
                    params.shaping_time = "us600"
                micro = math.pow(10, -6)
                k = 0
                while k < 19:
                    if params.cbs[k].isChecked():
                        j = 0
                        while j < len(params.Energy):
                            sum[j] += params.darray[k][j] * (
                                1 + micro * float(params.ICR[j][k]) / float(params.aq_time[j]) * float(
                                    DT["PF"]["individual"]["preamp"][k])) / (
                                          1 - micro * float(params.ICR[j][k]) / float(params.aq_time[j]) * float(
                                              DT["PF"]["individual"]["amp"][params.shaping_time][k]))
                            #sum[j] += params.darray[k][j]/(1-micro*float(params.ICR[j][k])/float(params.aq_time[k])*(float(DT["PF"]["individual"]["amp"][params.shaping_time][k])+float(DT["PF"]["individual"]["preamp"][k])))
                            j += 1
                    k += 1
            ut = np.divide(sum, params.i0)
            k = 0
            while k < len(params.Energy):
                str_ = "%7.3f  %1.8f\n" % (params.Energy[k], ut[k])
                out.write(str_)
                k += 1
            if self.u.radioButton.isChecked():
                out.write("\n[EX_END]\n")
            else:
                pass

        def read_SSD(fname):
            ignore_or_not = []
            angles = []
            aq_time = []
            i0 = []
            dat = []
            ICR = []
            Energy = []
            darray = np.empty([1, 1])
            D = 0.0
            BL = 0.0
            f = open(fname, "r")
            #angles, aq_time, i0, dat, ICR, Energy, darray, D, BL
            i = 0
            for line in f:
                line.rstrip()
                if re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line):
                    if re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "BL9A":
                        BL="BL9A"
                    elif re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "BL12C":
                        BL="BL12C"
                    elif re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "NW10A":
                        BL="NW10A"
                    elif re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(2) == "01b1":
                        BL="01b1"
                elif re.match(r".+D=(.+)A.+", line):
                    D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                #print str(params.D)
                elif re.match(r"\s+Angle\(c\).+", line):
                    t_array = line.split()
                #print t_array[0]
                elif re.match(r"\s+Mode", line):
                    t_array = line.split()
                    ignore_or_not = t_array[3:23]
                #print params.ignore_or_not
                elif re.match(r"\s+Offset", line):
                    pass
                elif len(line.split()) > 23:
                    t_array = line.split()
                    angles.append(t_array[1])
                    aq_time.append(float(t_array[2]))
                    i0.append(float(t_array[22]))
                    dat.append(t_array[3:23])
                    ICR.append(t_array[23:])
                #print i
                i += 1
            darray.resize(19, len(dat))
            k = 0
            while k < 19:
                j = 0
                while j < len(dat):
                    darray[k][j] = float(dat[j][k])
                    j += 1
                k += 1
            j = 0
            while j < len(dat):
                E = 12398.52 / (2 * float(D) * np.sin(float(angles[j]) / 180 * np.pi))
                Energy.append(E)
                j += 1
            return np.array(Energy), np.array(aq_time), np.array(i0), np.array(ICR),  np.array(darray), BL

        def Save_all_as_Current():
            conf = cwd + "/" + self.u.comboBox_4.currentText() + ".conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            # sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            current_ofile = ""
            if self.u.radioButton.isChecked():
                exd = self.u.radioButton.objectName()
            else:
                exd = self.u.radioButton_2.objectName()
            if params.outdir == "":
                o_dir = params.dir
            elif os.path.exists(params.outdir):
                o_dir = params.outdir
            for t_rb in params.d_rbs:
                # sum = np.zeros(len(params.Energy))
                Energy, aq_time, i0, ICR, darray, BL = read_SSD(params.dir + "/"+t_rb.objectName())
                sum = np.zeros(len(Energy))
                if re.match(r"(.+)\.\d+", t_rb.objectName()) is None:
                    current_ofile = o_dir + "/" + t_rb.objectName() + "_000" + exd
                elif re.match(r"(.+)\.(\d+)", t_rb.objectName()):
                    t_line = t_rb.objectName().split(".")
                    current_ofile = o_dir + "/" + t_line[0] + "_" + t_line[1] + exd
                out = open(current_ofile, "w")
                if self.u.radioButton.isChecked():
                    line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                    atom = "*EX_ATOM=" + self.u.lineEdit.text() + "\n"
                    edge = "*EX_EDGE=" + self.u.comboBox_2.currentText() + "\n"
                    line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                    line3 = "\n[EX_BEGIN]\n"
                    out.write(line + atom + edge + line2 + line3)
                else:
                    out.write("#Energy  ut\n")
                if self.u.comboBox.currentText() == "no correction":
                    for cb in params.cbs:
                        if cb.isChecked():
                            sum = np.add(sum, np.array(darray[params.cbs.index(cb)]))
                elif self.u.comboBox.currentText() != "no correction":
                    if self.u.comboBox.currentText() == "25 us":
                        params.shaping_time = "us025"
                    elif self.u.comboBox.currentText() == "50 us":
                        params.shaping_time = "us050"
                    elif self.u.comboBox.currentText() == "100 us":
                        params.shaping_time = "us100"
                    elif self.u.comboBox.currentText() == "200 us":
                        params.shaping_time = "us200"
                    elif self.u.comboBox.currentText() == "300 us":
                        params.shaping_time = "us300"
                    elif self.u.comboBox.currentText() == "600 us":
                        params.shaping_time = "us600"
                    micro = math.pow(10, -6)
                    k = 0
                    while k < 19:
                        if params.cbs[k].isChecked():
                            j = 0
                            while j < len(params.Energy):
                                sum[j] += darray[k][j] * (
                                    1 + micro * float(ICR[j][k]) / float(aq_time[j]) * float(
                                        DT["PF"]["individual"]["preamp"][k])) / (
                                            1 - micro * float(ICR[j][k]) / float(aq_time[j]) * float(
                                                DT["PF"]["individual"]["amp"][params.shaping_time][k]))
                            #sum[j] += params.darray[k][j]/(1-micro*float(params.ICR[j][k])/float(params.aq_time[k])*(float(DT["PF"]["individual"]["amp"][params.shaping_time][k])+float(DT["PF"]["individual"]["preamp"][k])))
                                j += 1
                        k += 1
                ut = np.divide(sum, i0)
                k = 0
                while k < len(Energy):
                    str_ = "%7.3f  %1.8f\n" % (Energy[k], ut[k])
                    out.write(str_)
                    k += 1
                if self.u.radioButton.isChecked():
                    out.write("\n[EX_END]\n")
                else:
                    pass

        def func_pushButton_3():
            while scroll_layout2.count() > 0:
                b = scroll_layout2.takeAt(len(params.ex3) - 1)
                params.ex3.pop()
                b.widget().deleteLater()
            FO_dialog = QtWidgets.QFileDialog(self)
            # files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=params.outdir,
            #                                    filter="xas files(*.ex3 *.dat)")
            files = FO_dialog.getOpenFileNames(None, 'Open dat files', params.outdir,
                                              "dat files(*.ex3 *.dat)")
            finfo = QtCore.QFileInfo(files[0][0])
            params.path_to_ex3 = finfo.path()
            j = 0
            for fname in files[0]:
                info = QtCore.QFileInfo(fname)
                cb = QtWidgets.QCheckBox(info.fileName())
                cb.setObjectName(info.fileName())
                params.ex3.append(cb)
                cb.setCheckState(QtCore.Qt.Checked)
                scroll_layout2.addWidget(cb)
                j += 1
            if self.u.textBrowser_2.toPlainText() == "":
                self.u.textBrowser_2.append(finfo.path())
            click_pB4()

        def plot_in_tab2(E, ut):
            # params.grid3.removeItem(params.grid3.itemAt(0))
            # params.grid3.removeItem(params.grid3.itemAt(0))
            # fig3 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
            ax_array = return_new_axis(params.grid3)
            ax3 = ax_array[0]
            ax3.set_xlabel("E / eV")
            ax3.set_ylabel("$\mu$ t")
            # canvas3 = FigureCanvas(fig3)
            # navibar_3 = NavigationToolbar(canvas3, self.u.widget_3)
            ax3.plot(E, ut)
            # params.grid3.addWidget(canvas3, 0, 0)
            # params.grid3.addWidget(navibar_3)
            canvas3.draw()

        def set_interpolation_file():
            self.u.textBrowser_4.clear()
            FO_dialog = QtWidgets.QFileDialog(self)
            # files = FO_dialog.getOpenFileName(parent=None, caption="", dir=params.outdir,
            #                                   filter="xas files(*.ex3 *.dat)")
            files = FO_dialog.getOpenFileName(None, 'Open dat files', params.outdir,
                                              "dat files(*.ex3 *.dat)")
            finfo = QtCore.QFileInfo(files[0])
            if os.path.exists(finfo.filePath()):
                self.u.textBrowser_4.append(finfo.filePath())
            click_pB4()

        def make_sum():
            if len(params.E_intp) != 0:
                params.E_intp = []
            fname = self.u.textBrowser_4.toPlainText()
            if os.path.basename(fname).split('.')[1] == 'ex3':
                f_ex3 = open(fname, "r")
                for line in f_ex3:
                    line.rstrip()
                    if re.match(r"^\d+\.\d+\s+\-?\d+\.\d+", line):
                        t_array = line.split()
                        params.E_intp.append(float(t_array[0]))
            elif os.path.basename(fname).split('.')[1] == 'dat':
                df = pd.read_csv(open(fname,'r'),delimiter=r"\s+",dtype=np.float)
                header = 'Energy'
                for key in df.keys():
                    if re.search(r"(?i)energy",key):
                        header = key
                params.E_intp = df[header].values
                print (params.E_intp)
            params.sum = np.zeros(len(params.E_intp))
            params.int_checked = 0
            if os.path.basename(fname).split('.')[1] == 'ex3':
                for cb in params.ex3:
                    if cb.isChecked():
                        params.int_checked += 1
                        E_ = []
                        ut = []
                        fname = params.path_to_ex3 + "/" + cb.objectName()
                        f = open(fname, "r")
                        for line in f:
                            line.rstrip()
                            if re.match(r"^\d+\.\d+\s+\-?\d+\.\d+", line):
                                t_array = line.split()
                                E_.append(float(t_array[0]))
                                ut.append(float(t_array[1]))
                        ut_intp = np.interp(np.array(params.E_intp), np.array(E_), np.array(ut))
                        #print ut_intp
                        params.sum = np.add(params.sum, ut_intp)
            elif os.path.basename(fname).split('.')[1] == 'dat':
                for cb in params.ex3:
                    if cb.isChecked():
                        params.int_checked += 1
                        E_ = []
                        ut = []
                        fname = params.path_to_ex3 + "/" + cb.objectName()
                        df = pd.read_csv(open(fname, "r"),delimiter=r"\s+",dtype=np.float)
                        print (df.keys())
                        E_ = df['#Energy'].values
                        ut = df['ut'].values
                        ut_intp = np.interp(np.array(params.E_intp), np.array(E_), np.array(ut))
                        #print ut_intp
                        params.sum = np.add(params.sum, ut_intp)
            params.avg = params.sum / params.int_checked
            if self.u.rb_sum.isChecked():
                plot_in_tab2(np.array(params.E_intp), params.sum)
            elif self.u.rb_avg.isChecked():
                plot_in_tab2(np.array(params.E_intp), params.avg)
            self.u.pushButton_8.setEnabled(True)

        def Save_sum_and_avg():
            FO_dialog = QtWidgets.QFileDialog(self)
            outdir = ""
            exd = ""
            if self.u.radioButton_3.isChecked():
                exd = self.u.radioButton_3.objectName()
            else:
                exd = self.u.radioButton_4.objectName()
            if self.u.textBrowser_2.toPlainText() != "":
                outdir = self.u.textBrowser_2.toPlainText()
            else:
                outdir = home_dir.homePath()
            Ffilter = "xas file (*" + exd + ")"
            # files = FO_dialog.getSaveFileName(parent=None, caption="Write a file name like \"******.***\"", dir=outdir,
            #                                   filter=Ffilter)
            files = FO_dialog.getSaveFileName(None, '"Write a file name like \"******.***\""', outdir,
                                              "xas files(*.ex3 *.dat)")
            print (files)
            finfo = QtCore.QFileInfo(files[0])
            arr_fname = finfo.fileName().split(".")
            fname = finfo.path() + "/" + arr_fname[0] + "_sum" + exd
            f_sum = open(fname, "w")
            if self.u.radioButton_3.isChecked():
                line1 = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                atom = "*EX_ATOM=" + self.u.lineEdit_2.text() + "\n"
                edge = "*EX_EDGE=" + self.u.comboBox_3.currentText() + "\n"
                line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                line3 = "\n[EX_BEGIN]\n"
                header_str = line1 + atom + edge + line2 + line3
                f_sum.write(header_str)
                str_ = pd.DataFrame({"#Energy": params.E_intp,"ut":params.sum}).to_csv(index=None,header=None,sep=' ')
                f_sum.write(str_)
                f_sum.write("\n[EX_END]\n")
                f_sum.close()
            else:
                str_ = pd.DataFrame({"#Energy": params.E_intp,"ut":params.sum}).to_csv(index=None,sep=' ')
            # for energy in params.E_intp:
            #     str_ = "%7.3f  %1.8f\n" % (energy, params.sum[params.E_intp.index(energy)])
                f_sum.write(str_)
                f_sum.close()
            # if self.u.radioButton_3.isChecked():
            #     f_sum.write("\n[EX_END]\n")
            # else:
            #     pass
            # f_sum.close()

            fname = finfo.path() + "/" + arr_fname[0] + "_avg" + exd
            f_sum = open(fname, "w")
            if self.u.radioButton_3.isChecked():
                line1 = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                atom = "*EX_ATOM=" + self.u.lineEdit_2.text() + "\n"
                edge = "*EX_EDGE=" + self.u.comboBox_3.currentText() + "\n"
                line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                line3 = "\n[EX_BEGIN]\n"
                header_str = line1 + atom + edge + line2 + line3
                f_sum.write(header_str)
                str_ = pd.DataFrame({"#Energy": params.E_intp,"ut":params.avg}).to_csv(index=None,header=None,sep=' ')
                f_sum.write(str_)
                f_sum.write("\n[EX_END]\n")
                f_sum.close()
            else:
                str_ = pd.DataFrame({"#Energy": params.E_intp,"ut":params.avg}).to_csv(index=None,sep=' ')
                f_sum.write(str_)
                f_sum.close()
            # if self.u.radioButton_3.isChecked():
            #     f_sum.write("\n[EX_END]\n")
            # else:
            #     pass
            # f_sum.close()
            self.u.pushButton_8.setEnabled(False)

        def plot_sum():
            if len(params.E_intp) != 0:
                plot_in_tab2(np.array(params.E_intp), params.sum)

        def plot_avg():
            if len(params.E_intp) != 0:
                plot_in_tab2(np.array(params.E_intp), params.avg)

        def change_CB4():
            if len(params.d_rbs) != 0:
                for t_rb in params.d_rbs:
                    if t_rb.isChecked():
                        plot_each_ch()
                        break
                    else:
                        pass

        def click_pB4():
            if len(params.ex3) != 0 and os.path.exists(self.u.textBrowser_4.toPlainText()):
                make_sum()

        # Functions for Transmissions and Fluorescense
        def define_outdir9809():
            self.u.textBrowser_3.clear()
            FO_dialog = QtWidgets.QFileDialog(self)
            dir_ = FO_dialog.getExistingDirectory(None, params.dir)
            self.u.textBrowser_3.append(dir_)

        def open_9809():
            while scroll_layout3.count() > 0:
                b = scroll_layout3.takeAt(len(params.cb9809) - 1)
                params.cb9809.pop()
                params.rb9809.pop()
                b.widget().deleteLater()
            params.dir9809 = ""
            FO_dialog = QtWidgets.QFileDialog(self)
            # files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=home_dir.homePath())
            files = FO_dialog.getOpenFileNames(None, 'Open dat files', home_dir.homePath(),
                                              "")
            if files:
                finfo = QtCore.QFileInfo(files[0][0])
                params.dir9809 = finfo.path()
                if self.u.textBrowser_3.toPlainText() == "":
                    self.u.textBrowser_3.append(params.dir9809)
                params.d9809 = []
                params.cb9809 = []
                params.rb9809 = []
                params.bg9809 = QtWidgets.QButtonGroup()
                j = 0
                for fname in files[0]:
                    widget = QtWidgets.QWidget()
                    hlayout = QtWidgets.QHBoxLayout()
                    widget.setLayout(hlayout)
                    info = QtCore.QFileInfo(fname)
                    params.d9809.append(info.fileName())
                    cb = QtWidgets.QCheckBox(info.fileName())
                    cb.setObjectName(info.fileName())
                    cb.setCheckState(QtCore.Qt.Checked)
                    params.cb9809.append(cb)
                    rb = QtWidgets.QRadioButton()
                    rb.setObjectName(info.fileName())
                    params.rb9809.append(rb)
                    params.bg9809.addButton(rb, j)
                    hlayout.addWidget(cb)
                    hlayout.addWidget(rb)
                    scroll_layout3.addWidget(widget)
                    j += 1
                for rb in params.rb9809:
                    rb.clicked.connect(plot_9809)

        def calc_ut(i0, i, mode):
            if mode == "Transmission":
                return math.log(i0 / i)
            elif mode == "Fluorescence":
                return i / i0

        def calc_ut_wcollection(i0, i, ICR, t_m, t1, t2):
            micro = math.pow(10, -6)
            return i * ((1 + ICR / t_m * micro * t1) / (1 - ICR / t_m * micro * t2)) / i0

        def open_interp_data_TAB1():
            self.u.textBrowser_5.clear()
            dat_dir = params.homedir
            if params.path_to_exafs !='':
                dat_dir = params.path_to_exafs
            FO_dialog = QtWidgets.QFileDialog(self)
            # file = FO_dialog.getOpenFileName(parent=None, caption="", dir=dat_dir,
            #                                    filter="xas files(*.ex3 *.dat)")
            file = FO_dialog.getOpenFileName(None, 'Open dat files', params.outdir,
                                              "dat files(*.ex3 *.dat)")
            self.u.textBrowser_5.append(file[0])

        def convert_9809():
            def readREX(fname):
                E_ = []
                ut = []
                if os.path.basename(fname).split('.')[1] == 'ex3':
                    f = open(fname, "r")
                    for line in f:
                        line.rstrip()
                        if re.match(r"^\d+\.\d+\s+\-?\d+\.\d+", line):
                            t_array = line.split()
                            E_.append(float(t_array[0]))
                            ut.append(float(t_array[1]))
                    return np.array(E_), np.array(ut), len(E_)
                elif os.path.basename(fname).split('.')[1] == 'dat':
                    df = pd.read_csv(open(fname, "r"), delimiter=r"\s+", dtype=np.float)
                    header = 'Energy'
                    data = 'ut'
                    for key in df.keys():
                        if re.search(r"(?i)energy", key) != None:
                            header = key
                        elif re.search(r"(?i)energy", key) == None:
                            data = key
                    return df[header].values, df[data].values, len(df[header].values)

            line1 = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
            atom = "*EX_ATOM=" + self.u.lineEdit_3.text() + "\n"
            edge = "*EX_EDGE=" + self.u.comboBox_5.currentText() + "\n"
            line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
            line3 = "\n[EX_BEGIN]\n"
            line4 = "\n[EX_END]\n"
            exd = ""
            t1 = 0.0
            t2 = 0.0
            if self.u.comboBox_6.currentText() == "SSSD_wCorrection" and os.path.exists(
                            params.homedir + "/deadtime.txt"):
                print ("deadtime collection")
                f_ = open(params.homedir + "/deadtime.txt")
                t_line = f_.readline().rstrip()
                [t1, t2] = [float(t_line.split(",")[0]), float(t_line.split(",")[1])]
            if self.u.radioButton_5.isChecked():
                exd = self.u.radioButton_5.objectName()
            else:
                exd = self.u.radioButton_6.objectName()
            if len(params.cb9809) != 0 and not self.u.checkBox_3.isChecked():
                for cb in params.cb9809:
                    f_in = ""
                    f_out = ""
                    D = ""
                    BL = ""
                    if cb.isChecked():
                        f_in = params.dir9809 + "/" + cb.objectName()
                        if re.match(r".+\.(\d+|[a-zA-Z]+)", cb.objectName()) is None:
                            f_out = self.u.textBrowser_3.toPlainText() + "/" + cb.objectName() + "_000" + exd
                        elif re.match(r".+\.\d+", cb.objectName()):
                            t_array = cb.objectName().split(".")
                            f_out = self.u.textBrowser_3.toPlainText() + "/" + t_array[0] + "_" + t_array[1] + exd
                        elif re.match(r".+\.[a-zA-Z]+", cb.objectName()):
                            t_array = cb.objectName().split(".")
                            f_out = self.u.textBrowser_3.toPlainText() + "/" + t_array[0] + exd
                        data = open(f_in, "r")
                        ut_out = open(f_out, "w")
                        if self.u.radioButton_5.isChecked():
                            ut_out.write(line1 + atom + edge + line2 + line3)
                        else:
                            ut_out.write("#Energy  ut\n")
                        firstline = data.readline()
                        if 'ESRF DUBBLE' in firstline:
                            # self.u.rB_DUBBLE.toggle()
                        # if self.u.rB_DUBBLE.isChecked():
                            labels = ['Energy', 'I0', 'It', 'Iref', 'lnI0It', 'lnItIref',
                                      'FF', 'FF/I0', 'Time','time']
                            df = pd.read_csv(f_in, comment='#',names=labels, sep=r'\s+')
                            Energy = df['Energy'].values.tolist()
                            ut = df['lnI0It'].values.tolist()
                            for i in range(len(Energy)):
                                str_ = "%7.3f  %1.8f\n" % (Energy[i], ut[i])
                                ut_out.write(str_)
                        elif re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", firstline):
                            for line in data:
                                line.rstrip()
                                # if re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line):
                                #     BL = re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(1)
                                #     print BL
                                if re.match(r".+D=(.+)A.+", line):
                                    D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                                elif re.match(r"^\s+\d+\.\d+.+", line):
                                    str_ = ""
                                    t_array = line.split()
                                    Energy = 12398.52 / (2 * D * np.sin(float(t_array[1]) / 180 * np.pi))
                                    if self.u.comboBox_6.currentText() == "SSSD_wCorrection":
                                        ut = calc_ut_wcollection(float(t_array[3]), float(t_array[4]), float(t_array[5]),
                                                                 float(t_array[2]), t1, t2)
                                        str_ = "%7.3f  %1.8f\n" % (Energy, ut)
                                    else:
                                        ut = calc_ut(float(t_array[3]), float(t_array[4]), self.u.comboBox_6.currentText())
                                        str_ = "%7.3f  %1.8f\n" % (Energy, ut)
                                    ut_out.write(str_)
                        if self.u.radioButton_5.isChecked():
                            ut_out.write(line4)
                        else:
                            pass
            elif len(params.cb9809) != 0 and self.u.checkBox_3.isChecked():
                for cb in params.cb9809:
                    f_in = ""
                    f_out = ""
                    D = ""
                    BL = ""
                    Energy_data = []
                    ut_data = []
                    ut_smth = []
                    Energy_itp = []
                    if self.u.textBrowser_5.toPlainText() != '':
                        Energy_itp, tmp_ut, tmp_len = readREX(self.u.textBrowser_5.toPlainText())

                    if cb.isChecked():
                        f_in = params.dir9809 + "/" + cb.objectName()
                        if re.match(r".+\.(\d+|[a-zA-Z]+)", cb.objectName()) is None:
                            f_out = self.u.textBrowser_3.toPlainText() + "/" + cb.objectName() + "_000" + '_inpt'+ exd
                        elif re.match(r".+\.\d+", cb.objectName()):
                            t_array = cb.objectName().split(".")
                            f_out = self.u.textBrowser_3.toPlainText() + "/" + t_array[0] + "_" + \
                                    t_array[1] + '_inpt'+ exd
                        elif re.match(r".+\.[a-zA-Z]+", cb.objectName()):
                            t_array = cb.objectName().split(".")
                            f_out = self.u.textBrowser_3.toPlainText() + "/" + t_array[0] + '_inpt'+ exd
                        data = open(f_in, "r")
                        ut_out = open(f_out, "w")
                        if self.u.radioButton_5.isChecked():
                            ut_out.write(line1 + atom + edge + line2 + line3)
                        else:
                            ut_out.write("#Energy  ut\n")
                        for line in data:
                            line.rstrip()
                            if re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line):
                                BL = re.match(r"\s+9809\s+(KEK\-PF|SPring\-8)\s+(\w+)", line).group(1)
                                print (BL)
                            elif re.match(r".+D=(.+)A.+", line):
                                D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                            elif re.match(r"^\s+\d+\.\d+.+", line):
                                t_array = line.split()
                                Energy_data.append(12398.52 / (2 * D * np.sin(float(t_array[1]) / 180 * np.pi)))
                                ut_data.append(calc_ut(float(t_array[3]), float(t_array[4]),
                                                              self.u.comboBox_6.currentText()))
                        ut_smth = savgol_filter(np.array(ut_data), self.u.spinBox.value(), self.u.spinBox_2.value())
                        ut_intp = np.interp(Energy_itp, np.array(Energy_data),ut_smth)
                        str_ = ""
                        for i in range(len(Energy_itp)):
                            str_ += "%7.3f  %1.8f\n" % (Energy_itp[i], ut_intp[i])
                        ut_out.write(str_)
                                # if self.u.comboBox_6.currentText() == "SSSD_wCorrection":
                                #     ut = calc_ut_wcollection(float(t_array[3]), float(t_array[4]),
                                #                              float(t_array[5]),
                                #                              float(t_array[2]), t1, t2)
                                #     str_ = "%7.3f  %1.8f\n" % (Energy, ut)
                                # else:
                                #     ut = calc_ut(float(t_array[3]), float(t_array[4]),
                                #                  self.u.comboBox_6.currentText())
                                #     str_ = "%7.3f  %1.8f\n" % (Energy, ut)
                                # ut_out.write(str_)
                        if self.u.radioButton_5.isChecked():
                            ut_out.write(line4)
                        else:
                            pass
                        #ax4.plot(np.array(Energy),np.array(ut))
                        #params.grid4.addWidget(canvas4,0,0)

        def plot_9809():
            # params.grid4.removeItem(params.grid4.itemAt(0))
            # params.grid4.removeItem(params.grid4.itemAt(0))
            # fig4 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
            ax_array = return_new_axis(params.grid4)
            ax4 = ax_array[0]
            ax4.set_xlabel("E / eV")
            ax4.set_ylabel("$\mu$ t")
            # canvas4 = FigureCanvas(fig4)
            # navibar_4 = NavigationToolbar(canvas4, self.u.widget_4)
            t1 = 0.0
            t2 = 0.0
            if self.u.comboBox_6.currentText() == "SSSD_wCorrection" and os.path.exists(
                            params.homedir + "/deadtime.txt"):
                print ("deadtime collection")
                f_ = open(params.homedir + "/deadtime.txt")
                t_line = f_.readline().rstrip()
                [t1, t2] = [float(t_line.split(",")[0]), float(t_line.split(",")[1])]
            if len(params.rb9809) != 0:
                f_in = ""
                D = ""
                BL = ""
                Energy = []
                ut = []
                for rb in params.rb9809:
                    if rb.isChecked():
                        f_in = params.dir9809 + "/" + rb.objectName()
                        data = open(f_in, "r")
                        firstline = data.readline().rstrip()
                        if 'ESRF DUBBLE' in firstline:
                            self.u.rB_DUBBLE.toggle()
                        if self.u.rB_DUBBLE.isChecked():
                            labels = ['Energy', 'I0', 'It', 'Iref', 'lnI0It', 'lnItIref',
                                      'FF', 'FF/I0', 'Time','time']
                            df = pd.read_csv(f_in, comment='#',names=labels, sep=r'\s+')
                            Energy = df['Energy'].values.tolist()
                            ut = df['lnI0It'].values.tolist()
                        elif self.u.rB_9809.isChecked():
                            if re.match(r"\s+9809\s+KEK\-PF\s+(\w+)", firstline):
                                BL = re.match(r"\s+9809\s+KEK\-PF\s+(\w+)", firstline).group(1)
                            elif re.match(r"\s+9809\s+KEK\-PF\s+(\w+)", firstline):
                                BL = re.match(r"\s+9809\s+SPring\-8\s+(\w+)", firstline).group(1)
                            for line in data:
                                line.rstrip()
                                if re.match(r".+D=(.+)A.+", line):
                                    D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                                elif re.match(r"^\s+\d+\.\d+.+", line):
                                    t_array = line.split()
                                    Energy.append(12398.52 / (2 * D * np.sin(float(t_array[1]) / 180 * np.pi)))
                                    if self.u.comboBox_6.currentText() == "SSSD_wCorrection":
                                        ut.append(
                                            calc_ut_wcollection(float(t_array[3]), float(t_array[4]), float(t_array[5]),
                                                                float(t_array[2]), t1, t2))
                                    else:
                                        ut.append(
                                            calc_ut(float(t_array[3]), float(t_array[4]), self.u.comboBox_6.currentText()))
                        ax4.plot(np.array(Energy), np.array(ut))
                        # params.grid4.addWidget(canvas4, 0, 0)
                        # params.grid4.addWidget(navibar_4)
                        canvas4.draw()
                        break

        def readREX(fname):
            E_ = []
            ut = []
            if os.path.basename(fname).split('.')[1] == 'ex3':
                f = open(fname, "r")
                for line in f:
                    line.rstrip()
                    if re.match(r"^\d+\.\d+\s+\-?\d+\.\d+", line):
                        t_array = line.split()
                        E_.append(float(t_array[0]))
                        ut.append(float(t_array[1]))
                return np.array(E_), np.array(ut), len(E_)
            elif os.path.basename(fname).split('.')[1] == 'dat':
                df = pd.read_csv(open(fname, "r"),delimiter=r"\s+",dtype=np.float)
                header = 'Energy'
                data = 'ut'
                for key in df.keys():
                    if re.search(r"(?i)energy",key) != None:
                        header = key
                    elif re.search(r"(?i)energy",key) == None:
                        data = key
                return df[header].values, df[data].values, len(df[header].values)


        def readREX_for_save(fname):
            E_ = []
            ut = []
            edge = ""
            atom = ""
            f = open(fname, "r")
            for line in f:
                line.rstrip()
                if re.match(r"^\d+\.\d+\s+\-?\d+\.\d+", line):
                    t_array = line.split()
                    E_.append(float(t_array[0]))
                    ut.append(float(t_array[1]))
                elif re.match(r"\*EX_ATOM\=(\s*)(\w+)",line):
                    atom = re.match(r"\*EX_ATOM\=(\s*)(\w+)",line).group(2)
                elif re.match(r"\*EX_EDGE\=(\s*)(\w+)",line):
                    edge = re.match(r"\*EX_EDGE\=(\s*)(\w+)",line).group(2)
            return E_, ut, atom, edge

        def saveXANES():
            dat_dir =  params.path_to_xanes
            FO_dialog = QtWidgets.QFileDialog(self)
            
            #savefile = FO_dialog.getSaveFileName(parent=None, dir=dat_dir,filter="csv files(*.csv *.CSV)")
            savefile = F0_dialog.getSaveFileName(None, "", dat_dir, "csv files(*.csv *.CSV)")
            if self.ax5.lines:
                for tline in self.ax5.lines:
                    print (tline.get_color())
            if len(params.xanes) != 0:
                #dict = {}
                order_array = []
                dataframes = []
                for cb in params.xanes:
                    if cb.isChecked():
                        Energy = self.lines_in_xanes[cb.objectName()].get_xdata()
                        ut =self.lines_in_xanes[cb.objectName()].get_ydata()
                        file = cb.objectName()
                        name = os.path.basename(cb.objectName()).split('.')[0]
                        dataframes.append(pd.DataFrame({name+':ene':Energy[:],name+':ut':ut[:]}))
                        order_array.append(name + ':ene')
                        order_array.append(name + ':ut')
                tmp_df = pd.concat(dataframes,axis=1)
                df = tmp_df[order_array[:]]
                df.to_csv(os.path.abspath(savefile[0]),index=False,sep=' ')


        def calc_delta_ut(file):
            energy_, ut_, length = readREX(file)
            delta_ut_ = []
            i = 1
            while i+1 < len(ut_):
                delta_ut_.append(((ut_[i+1]-ut_[i])/(energy_[i+1]-energy_[i])+(ut_[i]-ut_[i-1])/(energy_[i]-energy_[i-1]))/2)
                i += 1
            delta_ut_.append(0.0)
            delta_ut_.insert(0,0.0)
            return energy_, ut_, np.array(delta_ut_)

        def XANES_norm(datafile,fit_s,fit_e,nor_bE0_s,nor_bE0_e,nor_aE0_s,nor_aE0_e,func_type):
            energy, ut_, length = readREX(datafile)
            print (len(ut_))
            delta_ut = []
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
            if func_type == 1:
                fit_r = np.polyfit(energy[startpoint:endpoint],ut_[startpoint:endpoint],1)
                print (fit_r)
                pre_edge = fit_r[0]*energy + fit_r[1]
                ut_wo_bk = ut_ - pre_edge
                base = np.average(ut_wo_bk[find_near(energy,nor_bE0_s):find_near(energy,nor_bE0_e)])
                after_edge = np.average(ut_wo_bk[find_near(energy,nor_aE0_s):find_near(energy,nor_aE0_e)])
                ut_nor = (ut_wo_bk-base)/(after_edge-base)
                return energy, ut_, np.array(delta_ut), pre_edge, ut_nor
            elif func_type == 2:
                fit_lin = np.polyfit(energy[startpoint:endpoint],ut_[startpoint:endpoint],1)
                def fit_f(x,C,D,Y):
                    return Y + C/x**3 - D/x**4
                E_s_and_e = [energy[startpoint],energy[endpoint]]
                ut_s_and_e = [ut_[startpoint],ut_[endpoint]]
                X = np.vstack([E_s_and_e ,np.ones(len(E_s_and_e))]).T
                DAT = [energy[startpoint]**4*(ut_[startpoint]-fit_lin[1]),energy[endpoint]**4*(ut_[endpoint]-fit_lin[1])]
                c, d = linalg.lstsq(X,DAT)[0]
                print (c,d)
                opt, pconv = optim.curve_fit(fit_f,energy[startpoint:endpoint],ut_[startpoint:endpoint],p0=[c,d,fit_lin[1]])
                print (opt)
                pre_edge = fit_f(energy,opt[0],opt[1],opt[2])
                ut_wo_bk = ut_ - pre_edge
                base = np.average(ut_wo_bk[find_near(energy,nor_bE0_s):find_near(energy,nor_bE0_e)])
                after_edge = np.average(ut_wo_bk[find_near(energy,nor_aE0_s):find_near(energy,nor_aE0_e)])
                ut_nor = (ut_wo_bk-base)/(after_edge-base)
                return energy, ut_, np.array(delta_ut), pre_edge, ut_nor
            elif func_type == 0:
                pre_edge = np.average(ut_[find_near(energy,nor_bE0_s):find_near(energy,nor_bE0_e)])
                ut_wo_bk = ut_ - pre_edge
                after_edge = np.average(ut_wo_bk[find_near(energy,nor_aE0_s):find_near(energy,nor_aE0_e)])
                ut_nor = ut_wo_bk/after_edge
                return energy, ut_, np.array(delta_ut), pre_edge*np.ones(len(ut_)), ut_nor


        def plot_xanes():
            # while len(self.ax5.lines) !=0:
            #     self.ax5.lines.pop()
            self.lines_in_xanes = {}
            ax_array = return_new_axis(params.grid5)
            self.ax5 = ax_array[0]
            if len(params.xanes) != 0:
                print ('----plot_XANES----')
                for cb in params.xanes:
                    if cb.isChecked():
                        index = params.xanes.index(cb)%len(params.colors)
                        file = cb.objectName()
                        fit_s = self.findChild(QtWidgets.QDoubleSpinBox,cb.objectName()+'dSB_L').value()
                        #print fit_s
                        fit_e = self.findChild(QtWidgets.QDoubleSpinBox,cb.objectName()+'dSB_H').value()
                        func_type = self.findChild(QtWidgets.QComboBox,cb.objectName()+'_cmb').currentIndex()
                        #print fit_e
                        nor_bE0_s = self.u.doubleSpinBox.value()
                        nor_bE0_e = self.u.doubleSpinBox_2.value()
                        nor_aE0_s = self.u.doubleSpinBox_3.value()
                        nor_aE0_e = self.u.doubleSpinBox_4.value()
                        #func_type = self.u.comboBox_bk.currentIndex()
                        Energy, ut_, delta_ut, pre_edge, ut_nor = XANES_norm(file,fit_s,fit_e,nor_bE0_s,nor_bE0_e,nor_aE0_s,nor_aE0_e,func_type)
                        self.ax5.plot(Energy,ut_nor,label = os.path.basename(cb.objectName()),color = params.colors[index])
                        self.lines_in_xanes[cb.objectName()] = self.ax5.lines[-1]
                #self.ax5.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
                self.ax5.relim()
                self.ax5.autoscale_view()
                self.navibar_5.update()
                self.canvas5.draw()
            # for line in self.ax5.lines:
            #     print line.label

        def set_dialog_parameters():
            #self.plot_dialog.comboBox.setCurrentIndex(0)
            index = self.plot_dialog.comboBox.currentIndex()
            file = params.xanes[index].objectName()
            # self.plot_dialog.doubleSpinBox_LE.setValue(params.xanes_data[os.path.basename(file)][0])
            # self.plot_dialog.doubleSpinBox_HE.setValue(params.xanes_data[os.path.basename(file)][1])
            # self.plot_dialog.comboBox_Ftype.setCurrentIndex(params.xanes_data[os.path.basename(file)][2])
            dSpinBox = self.findChild(QtWidgets.QDoubleSpinBox,params.xanes[index].objectName()+'dSB_L')
            self.plot_dialog.doubleSpinBox_LE.setValue(dSpinBox.value())
            dSpinBox = self.findChild(QtWidgets.QDoubleSpinBox,params.xanes[index].objectName()+'dSB_H')
            self.plot_dialog.doubleSpinBox_HE.setValue(dSpinBox.value())
            comboBox = self.findChild(QtWidgets.QComboBox,params.xanes[index].objectName()+'_cmb')
            self.plot_dialog.comboBox_Ftype.setCurrentIndex(comboBox.currentIndex())

        def plot_xanes_in_dialog():
            tfig = params.grid_dialog.itemAt(0).widget().figure
            tfig.delaxes(self.ax_dialog)
            self.ax_dialog = tfig.add_subplot(121)
            if len(params.xanes) != 0:
                print ('----plot_xanes_in_dialog----')
                index = self.plot_dialog.comboBox.currentIndex()
                file = params.xanes[index].objectName()
                fit_s = self.plot_dialog.doubleSpinBox_LE.value()
                fit_e = self.plot_dialog.doubleSpinBox_HE.value()
                nor_bE0_s = self.u.doubleSpinBox.value()
                nor_bE0_e = self.u.doubleSpinBox_2.value()
                nor_aE0_s = self.u.doubleSpinBox_3.value()
                nor_aE0_e = self.u.doubleSpinBox_4.value()
                func_type = self.plot_dialog.comboBox_Ftype.currentIndex()
                #func_type = params.xanes_data[os.path.basename(file)][2]
                Energy, ut_, delta_ut, pre_edge, ut_nor = XANES_norm(file,fit_s,fit_e,nor_bE0_s,nor_bE0_e,nor_aE0_s,nor_aE0_e,func_type)
                self.ax_dialog.plot(Energy,ut_,label = 'XANES',color = params.colors[index], linewidth=2.0)
                self.ax_dialog.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
                self.ax_dialog.plot(Energy,pre_edge,label = 'bk',color = 'Black', linewidth=1.0)
                self.ax_dialog.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
                self.ax_dialog.relim()
                self.ax_dialog.autoscale_view()
                self.navibar_dialog.update()
                yrange = self.ax_dialog.get_ylim()
                print (yrange)
                self.annotate1 = matplotlib.text.Annotation("bk start",xy=(fit_s, ut_[find_near(Energy,fit_s)]),
                                                            xytext=(fit_s, ut_[find_near(Energy,fit_s)]-(yrange[1]-yrange[0])/5.0),
                                                            xycoords='data',
                                                            arrowprops=dict(arrowstyle="->"),
                                                            )
                self.annotate2 = matplotlib.text.Annotation("bk end",xy=(fit_e, ut_[find_near(Energy,fit_e)]),
                                                            xytext=(fit_e, ut_[find_near(Energy,fit_e)]-(yrange[1]-yrange[0])/5.0),
                                                            xycoords='data',
                                                            arrowprops=dict(arrowstyle="->"),
                                                            )
                self.ax_dialog.add_artist(self.annotate1)
                self.ax_dialog.add_artist(self.annotate2)
                self.canvas_dialog.draw()


        def plot_norm_XANES():
            tfig = params.grid_dialog.itemAt(0).widget().figure
            tfig.delaxes(self.ax_dialog_norm)
            self.ax_dialog_norm = tfig.add_subplot(122)
            for cb in params.xanes:
                if cb.isChecked():
                    print ('---plot norm XANES---')
                    index_ = params.xanes.index(cb)
                    #print index
                    file = params.xanes[index_].objectName()
                    #print file
                    fit_s = self.findChild(QtWidgets.QDoubleSpinBox,cb.objectName()+'dSB_L').value()
                    #print fit_s
                    fit_e = self.findChild(QtWidgets.QDoubleSpinBox,cb.objectName()+'dSB_H').value()
                    func_type = self.findChild(QtWidgets.QComboBox,cb.objectName()+'_cmb').currentIndex()
                    #print fit_e
                    nor_bE0_s = self.u.doubleSpinBox.value()
                    nor_bE0_e = self.u.doubleSpinBox_2.value()
                    nor_aE0_s = self.u.doubleSpinBox_3.value()
                    nor_aE0_e = self.u.doubleSpinBox_4.value()
                    Energy, ut_, delta_ut, pre_edge, ut_nor = XANES_norm(file,fit_s,fit_e,nor_bE0_s,nor_bE0_e,nor_aE0_s,nor_aE0_e,func_type)
                    self.ax_dialog_norm.plot(Energy,ut_nor,label = os.path.basename(params.xanes[index_].objectName()),color = params.colors[index_], linewidth=2.0)
                   #self.ax_dialog_norm.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, mode="expand", borderaxespad=0.)
                   #self.ax_dialog_norm.plot(Energy,pre_edge,label = os.path.basename(params.xanes[index].objectName()),color = 'Black', linewidth=1.0)
                   #self.ax_dialog_norm.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
                    self.ax_dialog_norm.relim()
                    self.ax_dialog_norm.autoscale_view()
                    #xrange = self.ax_dialog_norm.get_xlim()
                    self.ax_dialog_norm.axhline(y=1.0,color='k',linestyle='--')
                    self.ax_dialog_norm.axhline(y=0.0,color='k',linestyle='--')
                    #self.navibar_dialog.update()
                    self.canvas_dialog.draw()



        def find_near(Energy,req_Energy):
            array = np.absolute(Energy - req_Energy)
            return np.argmin(array)

        def openXANES_Files():
            print ('---open XANES Files---')
            while scroll_layout4.count() > 0:
                b = scroll_layout4.takeAt(len(params.xanes) - 1)
                params.xanes.pop()
                b.widget().deleteLater()
            if params.path_to_xanes =="":
                dat_dir = params.homedir
            else:
                dat_dir = params.path_to_xanes
            params.xanes_data = {}
            FO_dialog = QtWidgets.QFileDialog(self)
            # files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir,
            #                                    filter="xas files(*.ex3 *.dat)")
            files = FO_dialog.getOpenFileNames(None, 'Open dat files', params.outdir,
                                              "dat files(*.ex3 *.dat)")
            finfo = QtCore.QFileInfo(files[0][0])
            params.path_to_xanes = finfo.path()
            j = 0
            spinBoxes_L = []
            spinBoxes_H = []
            file = files[0][0]
            energy_, ut_, delta_ut_ = calc_delta_ut(file)
            E0 = energy_[np.argmax(delta_ut_)]
            for fname in files[0]:
            # if os.path.basename(fname).split('.')[1] == 'ex3':
                info = QtCore.QFileInfo(fname)
                cb = QtWidgets.QCheckBox(info.fileName())
                cb.setObjectName(info.absoluteFilePath())
                #print cb.objectName()
                params.xanes.append(cb)
                cb.setCheckState(QtCore.Qt.Checked)
                widget = QtWidgets.QWidget()
                layout = QtWidgets.QHBoxLayout()
                widget.setLayout(layout)
                layout.addWidget(cb)
                doubleSB_L = QtWidgets.QDoubleSpinBox()
                doubleSB_L.setObjectName(cb.objectName()+'dSB_L')
                spinBoxes_L.append(doubleSB_L)
                doubleSB_H = QtWidgets.QDoubleSpinBox()
                doubleSB_H.setObjectName(cb.objectName()+'dSB_H')
                spinBoxes_H.append(doubleSB_H)
                combobox_bk = QtWidgets.QComboBox()
                combobox_bk.setObjectName(cb.objectName() + '_cmb')
                combobox_bk.addItems(['average','linear','victoreen'])
                layout.addWidget(doubleSB_L)
                layout.addWidget(doubleSB_H)
                layout.addWidget(combobox_bk)
                scroll_layout4.addWidget(widget)
                # params.xanes_data[info.fileName()] = [energy_[find_near(energy_,E0-55)],energy_[find_near(energy_,E0-15)],1]
                j += 1
            [tmp_Energy,tmp_ut,length] = readREX(file)
            spinboxes = [self.u.doubleSpinBox,self.u.doubleSpinBox_2,self.u.doubleSpinBox_3,self.u.doubleSpinBox_4]
            for sB in spinboxes:
                sB.setMinimum(tmp_Energy[0])
                sB.setMaximum(tmp_Energy[-1])
                #print self.findChild(QtGui.QDoubleSpinBox,sB.objectName())
            print (E0)
            print (energy_[find_near(energy_,E0-15)])
            print (energy_[find_near(energy_,E0-55)])
            self.u.doubleSpinBox_2.setValue(energy_[find_near(energy_,E0-15)])
            self.u.doubleSpinBox.setValue(energy_[find_near(energy_,E0-55)])

            for sB in spinBoxes_L:
                sB.setMinimum(tmp_Energy[0])
                sB.setMaximum(tmp_Energy[-1])
                sB.setValue(energy_[find_near(energy_,E0-55)])
            for sB in spinBoxes_H:
                sB.setMinimum(tmp_Energy[0])
                sB.setMaximum(tmp_Energy[-1])
                sB.setValue(energy_[find_near(energy_,E0-15)])
            self.u.doubleSpinBox_3.setValue(energy_[find_near(energy_,E0+15)])
            self.u.doubleSpinBox_4.setValue(energy_[find_near(energy_,E0+55)])
            for cb in params.xanes:
                text = "color: "+params.colors[params.xanes.index(cb)%len(params.colors)]
                cb.setStyleSheet(text)
            plot_xanes()


        def addXANES_Files():
            print (params.homedir)
            if params.path_to_xanes =="":
                dat_dir = params.homedir
            else:
                dat_dir = params.path_to_xanes
            widgets_in_layout = []
            # while scroll_layout4.count() > 0:
            #     b = scroll_layout4.takeAt(len(params.xanes) - 1)
            #     b.widget().deleteLater()
            #     widgets_in_layout.append(scroll_layout4.itemAt(scroll_layout4.count()-1).widget())
            #     scroll_layout4.removeWidget(scroll_layout4.itemAt(scroll_layout4.count()-1).widget())
            # print widgets_in_layout
            FO_dialog = QtWidgets.QFileDialog(self)
            #files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir, filter="xas files(*.ex3 *.dat)")
            files = FO_dialog.getOpenFileNames(None, 'Open dat files', dat_dir,
                                              "dat files(*.ex3 *.dat)")
            finfo = QtCore.QFileInfo(files[0][0])
            params.path_to_xanes = finfo.path()
            j = 0
            if len(params.xanes) == 0:
                spinBoxes_L = []
                spinBoxes_H = []
                for w in widgets_in_layout:
                    scroll_layout4.addWidget(w)
                params.xanes_data = {}
                file = os.path.abspath(files[0][0])
                energy_, ut_, delta_ut_ = calc_delta_ut(file)
                E0 = energy_[np.argmax(delta_ut_)]
                [tmp_Energy, tmp_ut, length] = readREX(file)
                for fname in files[0]:
                    info = QtCore.QFileInfo(fname)
                    cb = QtWidgets.QCheckBox(info.fileName())
                    cb.setObjectName(info.absoluteFilePath())
                    params.xanes.append(cb)
                    cb.setCheckState(QtCore.Qt.Checked)
                    widget = QtWidgets.QWidget()
                    layout = QtWidgets.QHBoxLayout()
                    widget.setLayout(layout)
                    layout.addWidget(cb)
                    doubleSB_L = QtWidgets.QDoubleSpinBox()
                    doubleSB_L.setObjectName(cb.objectName()+'dSB_L')
                    spinBoxes_L.append(doubleSB_L)
                    doubleSB_H = QtWidgets.QDoubleSpinBox()
                    doubleSB_H.setObjectName(cb.objectName()+'dSB_H')
                    # params.xanes_data[info.fileName()] = [energy_[find_near(energy_,E0-55)],energy_[find_near(energy_,E0-15)],1]
                    combobox_bk = QtWidgets.QComboBox()
                    combobox_bk.setObjectName(cb.objectName() + '_cmb')
                    combobox_bk.addItems(['average', 'linear', 'victoreen'])
                    spinBoxes_H.append(doubleSB_H)
                    layout.addWidget(doubleSB_L)
                    layout.addWidget(doubleSB_H)
                    layout.addWidget(combobox_bk)
                    scroll_layout4.addWidget(widget)
                    j += 1
                file = params.xanes[0].objectName()
                # spinboxes = [self.u.spinBox,self.u.spinBox_2,self.u.spinBox_3,self.u.spinBox_4]
                spinboxes = [self.u.doubleSpinBox, self.u.doubleSpinBox_2, self.u.doubleSpinBox_3,self.u.doubleSpinBox_4]
                self.u.doubleSpinBox_2.setValue(find_near(energy_,E0-15))
                self.u.doubleSpinBox.setValue(find_near(energy_,E0-55))
                for sB in spinboxes:
                    sB.setMinimum(tmp_Energy[0])
                    sB.setMaximum(tmp_Energy[-1])
                self.u.doubleSpinBox_2.setValue(energy_[find_near(energy_,E0-15)])
                self.u.doubleSpinBox.setValue(energy_[find_near(energy_,E0-55)])
                for sB in spinBoxes_H:
                    sB.setMinimum(tmp_Energy[0])
                    sB.setMaximum(tmp_Energy[-1])
                    sB.setValue(energy_[find_near(energy_,E0-15)])
                for sB in spinBoxes_L:
                    sB.setMinimum(tmp_Energy[0])
                    sB.setMaximum(tmp_Energy[-1])
                    sB.setValue(energy_[find_near(energy_,E0-55)])
                self.u.doubleSpinBox_3.setValue(energy_[find_near(energy_,E0+15)])
                self.u.doubleSpinBox_4.setValue(energy_[find_near(energy_,E0+55)])
            else:
                spinBoxes_L = []
                spinBoxes_H = []
                file = params.xanes[0].objectName()
                [tmp_Energy, tmp_ut, length] = readREX(file)
                file = params.xanes[0].objectName()
                energy_, ut_, delta_ut_ = calc_delta_ut(file)
                E0 = energy_[np.argmax(delta_ut_)]
                for fname in files[0]:
                    info = QtCore.QFileInfo(fname)
                    sign = "add"
                    for cb in params.xanes:
                        if info.fileName() == cb.objectName():
                            sign = "not add"
                    if sign == "add":
                        cb = QtWidgets.QCheckBox(info.fileName())
                        cb.setObjectName(info.absoluteFilePath())
                        params.xanes.append(cb)
                        cb.setCheckState(QtCore.Qt.Checked)
                        widget = QtWidgets.QWidget()
                        layout = QtWidgets.QHBoxLayout()
                        widget.setLayout(layout)
                        layout.addWidget(cb)
                        doubleSB_L = QtWidgets.QDoubleSpinBox()
                        doubleSB_L.setObjectName(cb.objectName()+'dSB_L')
                        spinBoxes_L.append(doubleSB_L)
                        doubleSB_H = QtWidgets.QDoubleSpinBox()
                        doubleSB_H.setObjectName(cb.objectName()+'dSB_H')
                        spinBoxes_H.append(doubleSB_H)
                        combobox_bk = QtWidgets.QComboBox()
                        combobox_bk.setObjectName(cb.objectName() + '_cmb')
                        combobox_bk.addItems(['average', 'linear', 'victoreen'])
                        # params.xanes_data[info.fileName()] = [energy_[find_near(energy_, E0 - 55)],
                        #                                       energy_[find_near(energy_, E0 - 15)], 1]
                        layout.addWidget(doubleSB_L)
                        layout.addWidget(doubleSB_H)
                        layout.addWidget(combobox_bk)
                        scroll_layout4.addWidget(widget)
                        j += 1

                for sB in spinBoxes_H:
                    sB.setMinimum(tmp_Energy[0])
                    sB.setMaximum(tmp_Energy[-1])
                    sB.setValue(energy_[find_near(energy_,E0-15)])
                for sB in spinBoxes_L:
                    sB.setMinimum(tmp_Energy[0])
                    sB.setMaximum(tmp_Energy[-1])
                    sB.setValue(energy_[find_near(energy_,E0-55)])
            for cb in params.xanes:
                text = "color: "+params.colors[params.xanes.index(cb)]
                cb.setStyleSheet(text)
            plot_xanes()

        def ShowDialog():
            if self.u.checkBox.isChecked():
                self.dialog.show()
                set_dialog_parameters()
                if self.plot_dialog.comboBox.count != 0:
                    self.plot_dialog.comboBox.clear()
                data = []
                for item in params.xanes:
                    data.append(os.path.basename(item.objectName()))
                model = self.plot_dialog.comboBox.model()
                for term in data:
                    item = QtGui.QStandardItem(term)
                    item.setForeground(QtGui.QColor(params.colors[data.index(term)]))
                    #font = item.font()
                    #font.setPointSize(10)
                    #item.setFont(font)
                    model.appendRow(item)
                #self.plot_dialog.comboBox.addItems(data)
                # self.plot_dialog.comboBox_Ftype.setCurrentIndex(self.u.comboBox_bk.currentIndex())
                plot_xanes_in_dialog()
                plot_norm_XANES()
            else:
                pass

        def HideDialog():
            if self.u.checkBox.isChecked():
                self.dialog.done(1)
                self.u.checkBox.setCheckState(QtCore.Qt.Unchecked)
                self.u.pushButton_15.click()

        def comboBox_changed():
            set_dialog_parameters()
            plot_xanes_in_dialog()

        def pB_refresh_clicked():
            index = self.plot_dialog.comboBox.currentIndex()
            target_value = self.plot_dialog.doubleSpinBox_LE.value()
            self.findChild(QtWidgets.QDoubleSpinBox,params.xanes[index].objectName()+'dSB_L').setValue(target_value)
            target_value = self.plot_dialog.doubleSpinBox_HE.value()
            self.findChild(QtWidgets.QDoubleSpinBox,params.xanes[index].objectName()+'dSB_H').setValue(target_value)
            # self.u.comboBox_bk.setCurrentIndex(self.plot_dialog.comboBox_Ftype.currentIndex())
            plot_xanes_in_dialog()
            plot_norm_XANES()

        def copy_to_main_LE(value):
            i = self.plot_dialog.comboBox.currentIndex()
            sB = self.findChild(QtWidgets.QDoubleSpinBox,params.xanes[i].objectName()+'dSB_L')
            if abs(value - sB.value()) > 0.05:
                sB.setValue(value)

        def copy_to_main_HE(value):
            i = self.plot_dialog.comboBox.currentIndex()
            sB = self.findChild(QtWidgets.QDoubleSpinBox,params.xanes[i].objectName()+'dSB_H')
            if abs(value - sB.value()) > 0.05:
                sB.setValue(value)

        def copy_to_main_cmbbk(value):
            i = self.plot_dialog.comboBox.currentIndex()
            cmb = self.findChild(QtWidgets.QComboBox, params.xanes[i].objectName() + '_cmb')
            cmb.setCurrentIndex(value)

        def copy_to_all_data():
            for cb in params.xanes:
                self.findChild(QtWidgets.QDoubleSpinBox,cb.objectName()+'dSB_L').setValue(self.plot_dialog.doubleSpinBox_LE.value())
                self.findChild(QtWidgets.QDoubleSpinBox,cb.objectName()+'dSB_H').setValue(self.plot_dialog.doubleSpinBox_HE.value())
                self.findChild(QtWidgets.QComboBox, cb.objectName() + '_cmb').setCurrentIndex(self.plot_dialog.comboBox_Ftype.currentIndex())


        self.plot_dialog.comboBox.currentIndexChanged.connect(comboBox_changed)
        self.plot_dialog.pushButton.clicked.connect(HideDialog)
        self.plot_dialog.pB_refresh.clicked.connect(pB_refresh_clicked)
        self.plot_dialog.doubleSpinBox_LE.valueChanged[float].connect(copy_to_main_LE)
        self.plot_dialog.doubleSpinBox_HE.valueChanged[float].connect(copy_to_main_HE)
        self.plot_dialog.comboBox_Ftype.currentIndexChanged[int].connect(copy_to_main_cmbbk)
        self.plot_dialog.pB_copy_for_all.clicked.connect(copy_to_all_data)

        self.u.pushButton_2.clicked.connect(openFiles)
        self.u.pushButton.clicked.connect(define_outdir)
        self.u.pushButton_5.clicked.connect(select_or_release_all)
        self.u.pushButton_6.clicked.connect(Save)
        self.u.pB_save_all_SSD.clicked.connect(Save_all_as_Current)
        self.u.pushButton_3.clicked.connect(func_pushButton_3)
        self.u.pushButton_4.clicked.connect(click_pB4)
        self.u.pushButton_7.clicked.connect(define_outdir_for_sum)
        self.u.pushButton_8.clicked.connect(Save_sum_and_avg)
        self.u.pushButton_12.clicked.connect(set_interpolation_file)
        self.u.rb_sum.clicked.connect(plot_sum)
        self.u.rb_avg.clicked.connect(plot_avg)
        self.u.comboBox_2.currentIndexChanged.connect(change_CB3)
        self.u.comboBox.currentIndexChanged.connect(change_CB4)
        self.u.comboBox_6.currentIndexChanged.connect(plot_9809)
        self.u.lineEdit.textChanged.connect(change_lineEdit2)
        self.u.pushButton_9.clicked.connect(open_9809)
        self.u.pushButton_10.clicked.connect(define_outdir9809)
        self.u.pushButton_11.clicked.connect(convert_9809)
        self.u.pushButton_22.clicked.connect(open_interp_data_TAB1)
        self.u.pushButton_14.clicked.connect(openXANES_Files)
        self.u.pushButton_13.clicked.connect(addXANES_Files)
        self.u.pushButton_15.clicked.connect(plot_xanes)
        self.u.pushButton_16.clicked.connect(saveXANES)
        for cb in params.cbs:
            cb.clicked.connect(plot_each_ch)
        self.u.checkBox.toggled.connect(ShowDialog)

        self.u.EXAFSBK_type.addItems(['autobk','spline_smoothing'])
        self.u.comboBox_preEdge.addItems(['average','linear','victoreen'])
        self.u.comboBox_preEdge.setCurrentIndex(1)
        scroll_layout_exafs = QtWidgets.QVBoxLayout()
        scroll_widgets_exafs = QtWidgets.QWidget()
        scroll_widgets_exafs.setLayout(scroll_layout_exafs)
        self.u.scrollArea_6.setWidget(scroll_widgets_exafs)
        self.u.FT_kweight.addItems(['3','2','1','0'])

        #Figure for EXAFS Compare
        ##XAFS##
        params.grid_exafs_bk_ut = QtWidgets.QGridLayout()
        self.fig_exafsbk_ut = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax_exafsbk_ut = self.fig_exafsbk_ut.add_subplot(111)
        self.ax_exafsbk_ut.set_xlabel("E / eV")
        self.ax_exafsbk_ut.set_ylabel("$\mu$ t")
        self.canvas_exafsbk_ut = FigureCanvas(self.fig_exafsbk_ut)
        self.navibar_exafsbk_ut = NavigationToolbar(self.canvas_exafsbk_ut, self.u.widget_EXAFS)
        self.u.widget_EXAFS.setLayout(params.grid_exafs_bk_ut)
        params.grid_exafs_bk_ut.addWidget(self.canvas_exafsbk_ut, 0, 0)
        params.grid_exafs_bk_ut.addWidget(self.navibar_exafsbk_ut)
        ##chi(k) in EXAFS##
        params.grid_exafs_bk_chi = QtWidgets.QGridLayout()
        self.fig_exafsbk_chi = Figure(figsize=(200, 200), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax_exafsbk_chi = self.fig_exafsbk_chi.add_subplot(111)
        self.ax_exafsbk_chi.set_xlabel("k / $\AA^{-1}$")
        self.ax_exafsbk_chi.set_ylabel("$k^{3}\chi$ (k)")
        self.canvas_exafsbk_chi = FigureCanvas(self.fig_exafsbk_chi)
        self.fig_exafsbk_chi.subplots_adjust(bottom=0.15)
        #self.navibar_exafsbk_chi = NavigationToolbar(self.canvas_exafsbk_chi, self.u.mini_chi_k)
        self.u.mini_chi_k.setLayout(params.grid_exafs_bk_chi)
        params.grid_exafs_bk_chi.addWidget(self.canvas_exafsbk_chi, 0, 0)

        ##chi(r) in EXAFS##
        params.grid_exafs_bk_chir = QtWidgets.QGridLayout()
        self.fig_exafsbk_chir = Figure(figsize=(200, 200), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax_exafsbk_chir = self.fig_exafsbk_chir.add_subplot(111)
        self.ax_exafsbk_chir.set_xlabel("r / $\AA$")
        self.ax_exafsbk_chir.set_ylabel("FT(r)")
        self.canvas_exafsbk_chir = FigureCanvas(self.fig_exafsbk_chir)
        self.fig_exafsbk_chir.subplots_adjust(bottom=0.15)
        #self.navibar_exafsbk_chi = NavigationToolbar(self.canvas_exafsbk_chi, self.u.mini_chi_k)
        self.u.mini_FT.setLayout(params.grid_exafs_bk_chir)
        params.grid_exafs_bk_chir.addWidget(self.canvas_exafsbk_chir, 0, 0)

        ##chi(k) in chi##
        params.grid_chi_k = QtWidgets.QGridLayout()
        self.fig_chi_k = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax_chi_k = self.fig_chi_k.add_subplot(111)
        self.ax_chi_k.set_xlabel("k / $\AA{-1}$")
        self.ax_chi_k.set_ylabel("$k^{n}\chi$ (k)")
        self.canvas_chi_k = FigureCanvas(self.fig_chi_k)
        self.navibar_chi = NavigationToolbar(self.canvas_chi_k, self.u.w_chi_k)
        self.fig_chi_k.subplots_adjust(bottom=0.15)
        self.u.w_chi_k.setLayout(params.grid_chi_k)
        params.grid_chi_k.addWidget(self.canvas_chi_k, 0, 0)
        params.grid_chi_k.addWidget(self.navibar_chi)

        ###FT(r) in FT###
        params.grid_FT = QtWidgets.QGridLayout()
        self.fig_FT = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax_ft = self.fig_FT.add_subplot(111)
        self.ax_ft.set_xlabel("r / $\AA$")
        self.ax_ft.set_ylabel("$FT")
        self.canvas_FT = FigureCanvas(self.fig_FT)
        self.navibar_FT = NavigationToolbar(self.canvas_FT, self.u.w_FT)
        self.fig_FT.subplots_adjust(bottom=0.15)
        self.u.w_FT.setLayout(params.grid_FT)
        params.grid_FT.addWidget(self.canvas_FT, 0, 0)
        params.grid_FT.addWidget(self.navibar_FT)

        def comboBox_EXAFSBK_changed():
            return

        def subtract_exafsbk(button):
            print ('--- subtract exafs ---')
            #button = params.exafs_rb.checkedButton()
            name = os.path.basename(button.objectName())
            Energy = params.data_and_conditions[name+':'+'Energy']
            ut = params.data_and_conditions[name+':'+'ut']
            E0 = self.u.double_sB_E0_bk.value()
            k_min = self.u.double_sB_sP_start.value()
            k_max = self.u.double_sB_sP_end.value()
            pre_start = self.u.double_sB_pre_start.value()
            pre_end = self.u.double_sB_pre_end.value()
            post_start = self.u.double_sB_post_start.value()
            post_end = self.u.double_sB_post_end.value()
            EXAFSBK_type = self.u.EXAFSBK_type.currentIndex()
            preEdge_type = self.u.comboBox_preEdge.currentIndex()
            kweight = self.u.sB_kweight.value()
            degree_SS = self.u.degree_SS.value()
            rbkg = self.u.double_sB_rbkg.value()
            sf = self.u.SmoothF.value()
            [bkg, Lpre_edge, Lpost_edge, k, chi_k, r, ft_mag, ft_im] = [np.zeros(len(Energy)), np.zeros(len(Energy)), np.zeros(len(Energy)), np.zeros(len(Energy)), np.zeros(len(Energy)), np.zeros(len(Energy)), np.zeros(len(Energy)), np.zeros(len(Energy))]
            if len(params.data_and_conditions[name+':'+'ut']) != 0:
                if self.u.EXAFSBK_type.currentIndex() == 0:
                    print ('--run autobk--')
                    bkg, Lpre_edge, Lpost_edge, chi_k, k, r, ft_mag, ft_im = use_larch.run_autobk(Energy,ut,E0,rbkg,kweight,k_min,k_max,
                                                                                              pre_start,pre_end,post_start,post_end,
                                                                                              preEdge_type)
                    params.data_and_conditions[name+':'+'bkg'] = bkg
                    params.data_and_conditions[name+':'+'Lpre_edge'] = Lpre_edge
                    params.data_and_conditions[name+':'+'Lpost_edge'] = Lpost_edge
                    params.data_and_conditions[name+':'+'chi_k'] = chi_k
                    params.data_and_conditions[name+':'+'k'] = k
                    params.data_and_conditions[name+':'+'r'] = r
                    params.data_and_conditions[name+':'+'ft_mag'] = ft_mag
                    params.data_and_conditions[name+':'+'ft_im'] = ft_im
                elif self.u.EXAFSBK_type.currentIndex() == 1:
                    print ('--use spline smoothing--')
                    if self.u.checkBox_2.isChecked():
                        bkg, Lpre_edge, Lpost_edge, chi_k, k, r, ft_mag, ft_im, sf_ = use_larch.Cook_Sayers_rotine_(Energy,ut,E0,pre_start,pre_end,post_start,post_end,
                                                             preEdge_type,degree_SS,kweight,sf)
                        self.u.sB_kweight.setValue(kweight)
                        self.u.SmoothF.setValue(sf_)
                        params.data_and_conditions[name+':'+self.u.SmoothF.objectName()] = sf_
                        params.data_and_conditions[name+':'+'bkg'] = bkg
                        params.data_and_conditions[name+':'+'Lpre_edge'] = Lpre_edge
                        params.data_and_conditions[name+':'+'Lpost_edge'] = Lpost_edge
                        params.data_and_conditions[name+':'+'chi_k'] = chi_k
                        params.data_and_conditions[name+':'+'k'] = k
                        params.data_and_conditions[name+':'+'r'] = r
                        params.data_and_conditions[name+':'+'ft_mag'] = ft_mag
                        params.data_and_conditions[name+':'+'ft_im'] = ft_im
                        params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()] = kweight
                        #params.data_and_conditions[name+':'+self.u.SmoothF.objectName()] = sf
                    else:
                        bkg, Lpre_edge, Lpost_edge, chi_k,\
                            k, r, ft_mag, ft_im, sf_ = use_larch.calc_exafs_SplineSmoothing(Energy,ut, E0, pre_start,pre_end,post_start,
                                                                                                post_end,preEdge_type,degree_SS,kweight,sf)
                        #self.u.sB_kweight.setValue(kweight)
                        #self.u.SmoothF.setValue(sf)
                        params.data_and_conditions[name+':'+self.u.SmoothF.objectName()] = sf
                        params.data_and_conditions[name+':'+'bkg'] = bkg
                        params.data_and_conditions[name+':'+'Lpre_edge'] = Lpre_edge
                        params.data_and_conditions[name+':'+'Lpost_edge'] = Lpost_edge
                        params.data_and_conditions[name+':'+'chi_k'] = chi_k
                        params.data_and_conditions[name+':'+'k'] = k
                        params.data_and_conditions[name+':'+'r'] = r
                        params.data_and_conditions[name+':'+'ft_mag'] = ft_mag
                        params.data_and_conditions[name+':'+'ft_im'] = ft_im
                        params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()] = kweight


                return Energy, ut, bkg, Lpre_edge, Lpost_edge, k, chi_k, r, ft_mag, ft_im

        def setup_exafsbk():
            print ('---setup_exafsbk---')
            rb = params.exafs_rb.checkedButton()
            name = os.path.basename(rb.objectName())
            E0 = params.data_and_conditions[name+':'+self.u.double_sB_E0_bk.objectName()]
            energy = params.data_and_conditions[name+':'+'Energy']
            kmax = math.sqrt(0.2626*abs(E0-energy[-1]))
            self.u.double_sB_pre_start.setMinimum(energy[0])
            self.u.double_sB_pre_start.setMaximum(E0+10.0)
            self.u.double_sB_pre_end.setMinimum(energy[0])
            self.u.double_sB_pre_end.setMaximum(E0+10.0)
            self.u.double_sB_post_start.setMinimum(E0-10.0)
            self.u.double_sB_post_start.setMaximum(energy[-1])
            self.u.double_sB_post_end.setMinimum(E0-10.0)
            self.u.double_sB_post_end.setMaximum(energy[-1])
            self.u.double_sB_sP_end.setMaximum(kmax)
            pre_start = params.data_and_conditions[name+':'+self.u.double_sB_pre_start.objectName()]
            pre_end = params.data_and_conditions[name+':'+self.u.double_sB_pre_end.objectName()]
            post_start = params.data_and_conditions[name+':'+self.u.double_sB_post_start.objectName()]
            post_end = params.data_and_conditions[name+':'+self.u.double_sB_post_end.objectName()]
            bk_method = params.data_and_conditions[name+':'+self.u.EXAFSBK_type.objectName()]
            preEdge_method = params.data_and_conditions[name+':'+self.u.comboBox_preEdge.objectName()]
            k_min = params.data_and_conditions[name+':'+self.u.double_sB_sP_start.objectName()]
            k_max = params.data_and_conditions[name+':'+self.u.double_sB_sP_end.objectName()]
            weight = params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()]
            Factor_SS = params.data_and_conditions[name+':'+self.u.degree_SS.objectName()]
            rbkg = params.data_and_conditions[name+':'+self.u.double_sB_rbkg.objectName()]
            if params.data_and_conditions.__getitem__(name+':'+self.u.sB_kweight.objectName()):
                self.u.sB_kweight.setValue(params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()])
            self.u.double_sB_E0_bk.setValue(E0)
            self.u.double_sB_pre_start.setValue(pre_start)
            self.u.double_sB_pre_end.setValue(pre_end)
            self.u.double_sB_post_start.setValue(post_start)
            self.u.double_sB_post_end.setValue(post_end)
            self.u.EXAFSBK_type.setCurrentIndex(bk_method)
            self.u.double_sB_sP_start.setValue(k_min)
            self.u.double_sB_sP_end.setValue(k_max)
            self.u.comboBox_preEdge.setCurrentIndex(preEdge_method)
            self.u.sB_kweight.setValue(weight)
            self.u.degree_SS.setValue(Factor_SS)
            self.u.double_sB_rbkg.setValue(rbkg)
            self.u.EXAFSBK_type.setCurrentIndex(1)
            self.u.EXAFSBK_type.setCurrentIndex(0)


        def preserve_condition():
            print ('---preserve condition---')
            rb = params.exafs_rb.checkedButton()
            name = os.path.basename(rb.objectName())
            params.data_and_conditions[name+':'+self.u.double_sB_E0_bk.objectName()] = self.u.double_sB_E0_bk.value()
            params.data_and_conditions[name+':'+self.u.double_sB_pre_start.objectName()] = self.u.double_sB_pre_start.value()
            params.data_and_conditions[name+':'+self.u.double_sB_pre_end.objectName()] = self.u.double_sB_pre_end.value()
            params.data_and_conditions[name+':'+self.u.double_sB_post_start.objectName()] = self.u.double_sB_post_start.value()
            params.data_and_conditions[name+':'+self.u.double_sB_post_end.objectName()] = self.u.double_sB_post_end.value()
            params.data_and_conditions[name+':'+self.u.EXAFSBK_type.objectName()] = self.u.EXAFSBK_type.currentIndex()
            params.data_and_conditions[name+':'+self.u.comboBox_preEdge.objectName()] = self.u.comboBox_preEdge.currentIndex()
            params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()] = self.u.sB_kweight.value()
            params.data_and_conditions[name+':'+self.u.degree_SS.objectName()] = self.u.degree_SS.value()
            params.data_and_conditions[name+':'+self.u.double_sB_rbkg.objectName()] = self.u.double_sB_rbkg.value()
            params.data_and_conditions[name+':'+self.u.SmoothF.objectName()] = self.u.SmoothF.value()
            params.data_and_conditions[name+':'+self.u.double_sB_sP_start.objectName()] = self.u.double_sB_sP_start.value()
            params.data_and_conditions[name+':'+self.u.double_sB_sP_end.objectName()] = self.u.double_sB_sP_end.value()

        def plot_exafs():
            print ('---plot exafs---')
            Energy, ut, bkg, Lpre_edge, Lpost_edge, k, chi_k, r, ft_mag, ft_im = subtract_exafsbk(params.exafs_rb.checkedButton())
            # while len(self.ax_exafsbk_ut.lines) > 0:
            #     self.ax_exafsbk_ut.lines.pop()
            # while len(self.ax_exafsbk_chi.lines)>0:
            #     self.ax_exafsbk_chi.lines.pop()
            # while len(self.ax_exafsbk_chir.lines)>0:
            #     self.ax_exafsbk_chir.lines.pop()
            for term in ['ax_exafsbk_ut','ax_exafsbk_chi','ax_exafsbk_chir']:
                tfig = getattr(self,term).figure
                tfig.delaxes(getattr(self,term))
                setattr(self,term,tfig.add_subplot(111))
                if term == 'ax_exafsbk_ut':
                    getattr(self,term).set_xlabel("E / eV")
                    getattr(self,term).set_ylabel("$\mu$ t")
                elif term == 'ax_exafsbk_chi':
                    getattr(self,term).set_xlabel("k / $\AA^{-1}$")
                    getattr(self,term).set_ylabel("$k^{3}\chi$ (k)")
                elif term == 'ax_exafsbk_chir':
                    getattr(self,term).set_xlabel("r / $\AA$")
                    getattr(self,term).set_ylabel("FT(r)")
            E0 = self.u.double_sB_E0_bk.value()
            self.ax_exafsbk_ut.plot(Energy, ut, 'r')
            self.ax_exafsbk_ut.plot(Energy,Lpre_edge,'k')
            self.ax_exafsbk_ut.plot(Energy[find_near(Energy,E0):],Lpost_edge[find_near(Energy,E0):],'k')
            self.ax_exafsbk_chi.plot(k,chi_k*k**3,'b')
            self.ax_exafsbk_chir.plot(r,ft_mag,'b',r,ft_im,'r')
            self.ax_exafsbk_chir.set_xlim([0.0,6.0])
            for canvas in [self.canvas_exafsbk_ut,self.canvas_exafsbk_chi,self.canvas_exafsbk_chir]:
                canvas.draw()

        def plot_chi_k():
            print  ('---- plot chi(k) ----')
            # while len(self.ax_chi_k.lines) > 0:
            #     self.ax_chi_k.lines.pop()
            tfig = self.ax_chi_k.figure
            tfig.delaxes(self.ax_chi_k)
            self.ax_chi_k = tfig.add_subplot(111)
            self.ax_chi_k.set_xlabel("k / $\AA{-1}$")
            self.ax_chi_k.set_ylabel("$k^{n}\chi$ (k)")
            # self.ax_chi_k.relim()
            # self.ax_chi_k.autoscale_view()
            if len(params.exafs) != 0:
                for cb in params.exafs:
                    name = os.path.basename(cb.objectName())
                    if params.data_and_conditions.__contains__(name+':'+'chi_k') and cb.isChecked():
                        self.ax_chi_k.plot(params.data_and_conditions[name+':'+'k'],params.data_and_conditions[name+':'+'chi_k']*params.data_and_conditions[name+':'+'k']**self.u.sB_chi_kw.value(),params.colors[params.exafs.index(cb)%len(params.colors)])
                    else:
                        pass
                self.canvas_chi_k.draw()
        def plot_ft():
            # while len(self.ax_ft.lines) > 0:
            #     self.ax_ft.lines.pop()
            # self.ax_ft.relim()
            # self.ax_ft.autoscale_view()
            tfig = self.ax_ft.figure
            tfig.delaxes(self.ax_ft)
            self.ax_ft = tfig.add_subplot(111)
            self.ax_ft.set_xlabel("r / $\AA$")
            self.ax_ft.set_ylabel("$FT[k^{n}\chi$ (k)]")
            self.ax_ft.set_xlim([0.0,6.0])
            if len(params.exafs) != 0:
                for cb in params.exafs:
                    name = os.path.basename(cb.objectName())
                    if params.data_and_conditions.__contains__(name+':'+'chi_k') and cb.isChecked():
                        k = params.data_and_conditions[name+':'+'k']
                        chi = params.data_and_conditions[name+':'+'chi_k']
                        kweight = abs(self.u.FT_kweight.currentIndex()-3)
                        kmin = self.u.double_sB_kmin.value()
                        kmax = self.u.double_sB_kmax.value()
                        r, ft_mag, ft_img = use_larch.calc_FT(k,chi,kmin,kmax,kweight)
                        self.ax_ft.plot(r,ft_mag,params.colors[params.exafs.index(cb)%len(params.colors)])
                self.canvas_FT.draw()

        def plot_ft_():
            currentI = 3 - self.u.sB_chi_kw.value()
            self.u.FT_kweight.setCurrentIndex(abs(currentI))
            print ('FT_kweight CurrentIndex is ' + str(self.u.FT_kweight.currentIndex()))
            print ('FT kweight is ' + self.u.FT_kweight.currentText())
            self.u.tabWidget_2.setCurrentIndex(2)
            plot_ft()

        def plot_exafs_chi_ft(currentI):
            if currentI == 0:
                plot_exafs
            elif currentI == 1:
                plot_chi_k()
            elif currentI == 2:
                plot_ft()

        def func_for_cb_exafs():
            if self.u.tabWidget_2.currentIndex() == 1:
                plot_chi_k()
            elif self.u.tabWidget_2.currentIndex() == 2:
                plot_ft()

        @QtCore.Slot()
        def change_kweight():
            print ('----change_kweight----')
            if self.u.EXAFSBK_type.currentIndex() == 0:
                self.u.sB_kweight.setValue(3.0)
            elif self.u.EXAFSBK_type.currentIndex() == 1:
                self.u.sB_kweight.setValue(0.0)

        def func_rb():
            setup_exafsbk()
            plot_exafs()

        def func_pB20():
            plot_exafs()
            preserve_condition()

        def open_exafs_files():
            print ('---open EXAFS Files---')
            while scroll_layout_exafs.count() > 0:
                #params.current_EXAFS = ''
                b = scroll_layout_exafs.takeAt(len(params.exafs) - 1)
                params.exafs.pop()
                params.exafs_rb.removeButton(params.exafs_rb.buttons().pop())
                b.widget().deleteLater()
            if params.path_to_exafs =="":
                dat_dir = params.homedir
            else:
                dat_dir = params.path_to_xanes
            FO_dialog = QtWidgets.QFileDialog(self)
            if self.u.tabWidget_2.tabText(self.u.tabWidget_2.currentIndex()) == 'chi_k':
                # files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir,
                #                                    filter="xas files(*.rex *.xi *.chi)")
                files = FO_dialog.getOpenFileNames(None, 'Open dat files', dat_dir,
                                              "dat files(*.rex *.xi *.chi)")
                finfo = QtCore.QFileInfo(files[0][0])
                params.path_to_exafs = finfo.path()
                j = 0
                for fname in files[0]:
                    info = QtCore.QFileInfo(fname)
                    cb = QtWidgets.QCheckBox(info.fileName())
                    cb.setObjectName(info.absoluteFilePath())
                    cb.clicked.connect(func_for_cb_exafs)
                    params.exafs.append(cb)
                    k, chi = use_larch.read_chi_file(cb.objectName())
                    name = os.path.basename(cb.objectName())
                    params.data_and_conditions[name+':'+'k'] = k[:]
                    params.data_and_conditions[name+':'+'chi_k'] = chi[:]
                for cb in params.exafs:
                    text = "color: "+params.colors[params.exafs.index(cb)%len(params.colors)]
                    cb.setStyleSheet(text)
                    scroll_layout_exafs.addWidget(cb)
            else:
                # files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir,
                #                                    filter="xas files(*.ex3 *.dat)")
                files = FO_dialog.getOpenFileNames(None, 'Open dat files', dat_dir,
                                              "dat files(*.ex3 *.dat)")
                finfo = QtCore.QFileInfo(files[0][0])
                params.path_to_exafs = finfo.path()
                j = 0
                for fname in files[0]:
                    info = QtCore.QFileInfo(fname)
                    cb = QtWidgets.QCheckBox(info.fileName())
                    cb.setObjectName(info.absoluteFilePath())
                    cb.clicked.connect(func_for_cb_exafs)
                    params.exafs.append(cb)
                    energy, ut = use_larch.read_file(cb.objectName())
                    first_div, num_of_E0 = use_larch.calc_1st_derivative(energy,ut)
                    k_max = math.sqrt(0.2626*abs(energy[num_of_E0]-energy[-1]))
                    print (k_max)
                    name = os.path.basename(cb.objectName())
                    params.data_and_conditions[name+':'+'Energy'] = energy[:]
                    params.data_and_conditions[name+':'+'ut'] = ut[:]
                    params.data_and_conditions[name+':'+self.u.double_sB_E0_bk.objectName()] = energy[num_of_E0]
                    params.data_and_conditions[name+':'+self.u.double_sB_pre_start.objectName()] = energy[0]
                    params.data_and_conditions[name+':'+self.u.double_sB_pre_end.objectName()] = energy[num_of_E0] - 30.0
                    params.data_and_conditions[name+':'+self.u.double_sB_post_start.objectName()] = energy[num_of_E0] + 10.0
                    params.data_and_conditions[name+':'+self.u.double_sB_post_end.objectName()] = energy[-1]
                    params.data_and_conditions[name+':'+self.u.double_sB_sP_start.objectName()] = 0.5
                    params.data_and_conditions[name+':'+self.u.double_sB_sP_end.objectName()] = k_max
                    params.data_and_conditions[name+':'+self.u.EXAFSBK_type.objectName()] = self.u.EXAFSBK_type.currentIndex()
                    params.data_and_conditions[name+':'+self.u.comboBox_preEdge.objectName()] = self.u.comboBox_preEdge.currentIndex()
                    params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()] = self.u.sB_kweight.value()
                    params.data_and_conditions[name+':'+self.u.degree_SS.objectName()] = self.u.degree_SS.value()
                    params.data_and_conditions[name+':'+self.u.double_sB_rbkg.objectName()] = self.u.double_sB_rbkg.value()
                    cb.setCheckState(QtCore.Qt.Checked)
                    widget = QtWidgets.QWidget()
                    layout = QtWidgets.QHBoxLayout()
                    widget.setLayout(layout)
                    rb = QtWidgets.QRadioButton()
                    rb.setObjectName(cb.objectName())
                    print (rb.objectName())
                    rb.toggled.connect(func_rb)
                    params.exafs_rb.addButton(rb)
                    layout.addWidget(cb)
                    layout.addWidget(rb)
                    scroll_layout_exafs.addWidget(widget)
                    j += 1
                for cb in params.exafs:
                    text = "color: "+params.colors[params.exafs.index(cb)%len(params.colors)]
                    cb.setStyleSheet(text)
                params.exafs_rb.buttons()[0].toggle()

        def add_exafs_files():
            if len(params.exafs) == 0:
                open_exafs_files()
            else:
                print ('---add EXAFS Files---')
                if params.path_to_exafs =="":
                    dat_dir = params.homedir
                else:
                    dat_dir = params.path_to_xanes
                FO_dialog = QtWidgets.QFileDialog(self)
                if self.u.tabWidget_2.tabText(self.u.tabWidget_2.currentIndex()) == 'chi_k':
                    # files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir,
                    #                                    filter="xas files(*.rex *.xi *.chi)")
                    files = FO_dialog.getOpenFileNames(None, 'Open dat files', dat_dir,
                                              "dat files(*.rex *.xi *.chi)")
                    finfo = QtCore.QFileInfo(files[0][0])
                    params.path_to_exafs = finfo.path()
                    j = 0
                    num = len(params.exafs) -1
                    for fname in files[0]:
                        info = QtCore.QFileInfo(fname)
                        sign = 'make'
                        for cb in params.exafs:
                            if cb.objectName() == info.absoluteFilePath():
                                sign = 'not make'
                            else:
                                pass
                        if sign == 'not make':
                            pass
                        elif sign == 'make':
                            cb = QtWidgets.QCheckBox(info.fileName())
                            cb.setObjectName(info.absoluteFilePath())
                            cb.clicked.connect(func_for_cb_exafs)
                            params.exafs.append(cb)
                            k, chi = use_larch.read_chi_file(cb.objectName())
                            name = os.path.basename(cb.objectName())
                            params.data_and_conditions[name+':'+'k'] = k[:]
                            params.data_and_conditions[name+':'+'chi_k'] = chi[:]
                    for cb in params.exafs[num+1:]:
                        text = "color: "+params.colors[params.exafs.index(cb)%len(params.colors)]
                        cb.setStyleSheet(text)
                        scroll_layout_exafs.addWidget(cb)
                else:
                    # files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir,
                    #                                    filter="xas files(*.ex3 *.dat)")
                    files = FO_dialog.getOpenFileNames(None, 'Open dat files', dat_dir,
                                              "dat files(*.ex3 *.dat)")
                    finfo = QtCore.QFileInfo(files[0][0])
                    params.path_to_exafs = finfo.path()
                    j = 0
                    num = len(params.exafs) -1
                    for fname in files[0]:
                        info = QtCore.QFileInfo(fname)
                        sign = 'make'
                        for cb in params.exafs:
                            if cb.objectName() == info.absoluteFilePath():
                                sign = 'not make'
                            else:
                                pass
                        if sign == 'not make':
                            pass
                        elif sign == 'make':
                            cb = QtWidgets.QCheckBox(info.fileName())
                            cb.setObjectName(info.absoluteFilePath())
                            cb.clicked.connect(func_for_cb_exafs)
                            params.exafs.append(cb)
                            energy, ut = use_larch.read_file(cb.objectName())
                            first_div, num_of_E0 = use_larch.calc_1st_derivative(energy,ut)
                            name = os.path.basename(cb.objectName())
                            k_max = math.sqrt(0.2626*abs(energy[num_of_E0]-energy[-1]))
                            params.data_and_conditions[name+':'+'Energy'] = energy[:]
                            params.data_and_conditions[name+':'+'ut'] = ut[:]
                            params.data_and_conditions[name+':'+self.u.double_sB_E0_bk.objectName()] = energy[num_of_E0]
                            params.data_and_conditions[name+':'+self.u.double_sB_pre_start.objectName()] = energy[0]
                            params.data_and_conditions[name+':'+self.u.double_sB_pre_end.objectName()] = energy[num_of_E0] - 30.0
                            params.data_and_conditions[name+':'+self.u.double_sB_post_start.objectName()] = energy[num_of_E0] + 10.0
                            params.data_and_conditions[name+':'+self.u.double_sB_post_end.objectName()] = energy[-1]
                            params.data_and_conditions[name+':'+self.u.double_sB_sP_start.objectName()] = 0.5
                            params.data_and_conditions[name+':'+self.u.double_sB_sP_end.objectName()] = k_max
                            params.data_and_conditions[name+':'+self.u.EXAFSBK_type.objectName()] = self.u.EXAFSBK_type.currentIndex()
                            params.data_and_conditions[name+':'+self.u.comboBox_preEdge.objectName()] = self.u.comboBox_preEdge.currentIndex()
                            params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()] = self.u.sB_kweight.value()
                            params.data_and_conditions[name+':'+self.u.degree_SS.objectName()] = self.u.degree_SS.value()
                            params.data_and_conditions[name+':'+self.u.double_sB_rbkg.objectName()] = self.u.double_sB_rbkg.value()
                            cb.setCheckState(QtCore.Qt.Checked)
                            widget = QtWidgets.QWidget()
                            layout = QtWidgets.QHBoxLayout()
                            widget.setLayout(layout)
                            rb = QtWidgets.QRadioButton()
                            rb.setObjectName(cb.objectName())
                            print (rb.objectName())
                            rb.toggled.connect(func_rb)
                            params.exafs_rb.addButton(rb)
                            layout.addWidget(cb)
                            layout.addWidget(rb)
                            scroll_layout_exafs.addWidget(widget)
                            j += 1
                    for cb in params.exafs[num+1:]:
                        text = "color: "+params.colors[params.exafs.index(cb)%len(params.colors)]
                        cb.setStyleSheet(text)

        def copy_current_to_all():
            if len(params.exafs) != 0:
                for cb in params.exafs:
                    name = os.path.basename(cb.objectName())
                    if cb.isChecked() and len(params.data_and_conditions[name+':'+'Energy']) !=0:
                        params.data_and_conditions[name+':'+self.u.double_sB_E0_bk.objectName()] = self.u.double_sB_E0_bk.value()
                        params.data_and_conditions[name+':'+self.u.double_sB_pre_start.objectName()] = self.u.double_sB_pre_start.value()
                        params.data_and_conditions[name+':'+self.u.double_sB_pre_end.objectName()] = self.u.double_sB_pre_end.value()
                        params.data_and_conditions[name+':'+self.u.double_sB_post_start.objectName()] = self.u.double_sB_post_start.value()
                        params.data_and_conditions[name+':'+self.u.double_sB_post_end.objectName()] = self.u.double_sB_post_end.value()
                        params.data_and_conditions[name+':'+self.u.double_sB_sP_start.objectName()] = self.u.double_sB_sP_start.value()
                        params.data_and_conditions[name+':'+self.u.double_sB_sP_end.objectName()] = self.u.double_sB_sP_end.value()
                        params.data_and_conditions[name+':'+self.u.EXAFSBK_type.objectName()] = self.u.EXAFSBK_type.currentIndex()
                        params.data_and_conditions[name+':'+self.u.comboBox_preEdge.objectName()] = self.u.comboBox_preEdge.currentIndex()
                        params.data_and_conditions[name+':'+self.u.sB_kweight.objectName()] = self.u.sB_kweight.value()
                        params.data_and_conditions[name+':'+self.u.degree_SS.objectName()] = self.u.degree_SS.value()
                        params.data_and_conditions[name+':'+self.u.double_sB_rbkg.objectName()] = self.u.double_sB_rbkg.value()
                        subtract_exafsbk(cb)
                if self.u.EXAFSBK_type.currentIndex() == 1:
                    self.u.checkBox_2.setCheckState(QtCore.Qt.Unchecked)

        def Save_chi_ft():
            if self.u.tabWidget_2.currentIndex() == 0:
                print ('--- Save current chi file ---')
                if len(params.exafs) !=0:
                    dat_dir =  os.path.dirname(params.exafs_rb.checkedButton().objectName())
                    FO_dialog = QtWidgets.QFileDialog(self)
                    # file = FO_dialog.getSaveFileName(parent=None, dir=dat_dir,filter="chi files(*.dat)")
                    file = F0_dialog.getSaveFileName(None, "", dat_dir, "chi files(*.csv *.CSV)")
                    f = open(file[0],'w')
                    df = pd.DataFrame(columns=['#k','chi'])
                    name = os.path.basename(params.exafs_rb.checkedButton().objectName())
                    df['#k'] = params.data_and_conditions[name+':'+'k'][:]
                    df['chi'] = params.data_and_conditions[name+':'+'chi_k'][:]
                    df.to_csv(f,index=False,sep='\t')
            elif self.u.tabWidget_2.currentIndex() == 1:
                print ('--- Save chi files ---')
                if len(params.exafs) !=0:
                    dat_dir =  os.path.dirname(params.exafs[0].objectName())
                    FO_dialog = QtWidgets.QFileDialog(self)
                    #file = FO_dialog.getSaveFileName(parent=None, dir=dat_dir,filter="chi files(*.dat)")
                    file = F0_dialog.getSaveFileName(None, "", dat_dir, "chi files(*.dat)")
                    f = open(file[0],'w')
                    df = pd.DataFrame(columns=['#k'])
                    i = 0
                    b_name = os.path.basename(params.exafs[0].objectName())
                    for cb in params.exafs:
                        if cb.isChecked() and i == 0:
                            df['#k'] = params.data_and_conditions[b_name+':'+'k']
                            df.add_prefix('chi_'+b_name)
                            df['chi_'+b_name] = params.data_and_conditions[b_name+':'+'chi_k']
                            i += 1
                        elif cb.isChecked() and i > 0:
                            name = os.path.basename(cb.objectName())
                            df.add_prefix('chi_'+name)
                            k_interp = params.data_and_conditions[b_name+':'+'k']
                            t_k = params.data_and_conditions[name+':'+'k']
                            chi_interp = np.interp(k_interp,t_k,params.data_and_conditions[name+':'+'chi_k'])
                            df['chi_'+name] = chi_interp[:]
                            i += 1
                        else:
                            i += 1
                    df.to_csv(f,index=False,sep='\t')
            elif self.u.tabWidget_2.currentIndex() == 2:
                print ('--- Save FT files ---')
                if len(params.exafs) !=0:
                    dat_dir =  os.path.dirname(params.exafs[0].objectName())
                    FO_dialog = QtWidgets.QFileDialog(self)
                    #file = FO_dialog.getSaveFileName(parent=None, dir=dat_dir,filter="FT files(*.dat)")
                    file = FO_dialog.getSaveFileName(None, "", dat_dir,"FT files(*.dat)")
                    f = open(file[0],'w')
                    df = pd.DataFrame(columns=['#r'])
                    i = 0
                    b_name = os.path.basename(params.exafs[0].objectName())
                    for cb in params.exafs:
                        if cb.isChecked() and i == 0:
                            df['#r'] = params.data_and_conditions[b_name+':'+'r']
                            df.add_prefix('FT_mag:'+b_name)
                            df['FT_mag:'+b_name] = params.data_and_conditions[b_name+':'+'ft_mag']
                            df.add_prefix('FT_im:'+b_name)
                            df['FT_im:'+b_name] = params.data_and_conditions[b_name+':'+'ft_im']
                            i += 1
                        elif cb.isChecked() and i > 0:
                            name = os.path.basename(cb.objectName())
                            df.add_prefix('FT_mag:'+name)
                            r_interp = params.data_and_conditions[b_name+':'+'r']
                            t_r = params.data_and_conditions[name+':'+'r']
                            ft_interp_mag = np.interp(r_interp,t_r,params.data_and_conditions[name+':'+'ft_mag'])
                            df['FT_mag:'+name] = ft_interp_mag[:]
                            df.add_prefix('FT_im:'+name)
                            ft_interp_im = np.interp(r_interp,t_r,params.data_and_conditions[name+':'+'ft_im'])
                            df['FT_im:'+name] = ft_interp_im[:]
                            i += 1
                        else:
                            i += 1
                    df.to_csv(f,index=False,sep='\t')

        self.u.EXAFSBK_type.currentIndexChanged.connect(comboBox_EXAFSBK_changed)
        self.u.EXAFSBK_type.currentIndexChanged.connect(change_kweight)
        self.u.pushButton_17.clicked.connect(open_exafs_files)
        self.u.pushButton_18.clicked.connect(add_exafs_files)
        self.u.pushButton_20.clicked.connect(func_pB20)
        self.u.tabWidget_2.currentChanged[int].connect(plot_exafs_chi_ft)
        self.u.pushButton_21.clicked.connect(plot_ft_)
        self.u.FT_kweight.currentIndexChanged.connect(plot_ft)
        self.u.pB_cp_to_all_EXAFS.clicked.connect(copy_current_to_all)
        self.u.pushButton_19.clicked.connect(Save_chi_ft)



        ###############BL36XU, BL14B1, 7-elements SDD###############
        Widget_for_36XU = QtWidgets.QWidget()
        self.wid_BL36XU = wid_BL36XU()
        self.wid_BL36XU.setupUi(Widget_for_36XU)
        Widget_for_BL14 = QtWidgets.QWidget()
        self.wid_BL14B1 = wid_BL14B1()
        self.wid_BL14B1.setupUi(Widget_for_BL14)
        Widget_for_7SDD = QtWidgets.QWidget()
        self.Widget_for_7SDD = wid_7elementsSDD()
        self.Widget_for_7SDD.setupUi(Widget_for_7SDD)
        Widget_for_DUBBLE = QtWidgets.QWidget()
        self.Widget_for_DUBBLE = wid_DUBBLE()
        self.Widget_for_DUBBLE.setupUi(Widget_for_DUBBLE)
        params.cBs_36XU = [self.wid_BL36XU.BL36XU_ch1,self.wid_BL36XU.BL36XU_ch2,self.wid_BL36XU.BL36XU_ch3,self.wid_BL36XU.BL36XU_ch4,self.wid_BL36XU.BL36XU_ch5,
                           self.wid_BL36XU.BL36XU_ch6,self.wid_BL36XU.BL36XU_ch7,self.wid_BL36XU.BL36XU_ch8,self.wid_BL36XU.BL36XU_ch9,self.wid_BL36XU.BL36XU_ch10,
                           self.wid_BL36XU.BL36XU_ch11,self.wid_BL36XU.BL36XU_ch12,self.wid_BL36XU.BL36XU_ch13,self.wid_BL36XU.BL36XU_ch14,self.wid_BL36XU.BL36XU_ch15,
                           self.wid_BL36XU.BL36XU_ch16,self.wid_BL36XU.BL36XU_ch17,self.wid_BL36XU.BL36XU_ch18,self.wid_BL36XU.BL36XU_ch19,self.wid_BL36XU.BL36XU_ch20,
                           self.wid_BL36XU.BL36XU_ch21,self.wid_BL36XU.BL36XU_ch22,self.wid_BL36XU.BL36XU_ch23,self.wid_BL36XU.BL36XU_ch24,self.wid_BL36XU.BL36XU_ch25]
        params.cBs_36XU_checkstates = []

        for cb in params.cBs_36XU:
            cb.setCheckState(QtCore.Qt.Checked)
            params.cBs_36XU_checkstates.append(cb.checkState())

        def record_CheckState_BL36XU():
            params.cBs_36XU_checkstates =[]
            for cb in params.cBs_36XU:
                params.cBs_36XU_checkstates.append(cb.checkState())

        params.cBs_BL14B1 = []
        for i in range(1, 37):
            params.cBs_BL14B1.append(getattr(self.wid_BL14B1, 'BL14_ch' + str(i)))

        params.cBs_BL14B1_checkstates = []
        for cb in params.cBs_BL14B1:
            cb.setCheckState(QtCore.Qt.Checked)
            params.cBs_BL14B1_checkstates.append(cb.checkState())
        def record_CheckState_BL14B1():
            params.cBs_BL14B1_checkstates =[]
            for cb in params.cBs_BL14B1:
                params.cBs_BL14B1_checkstates.append(cb.checkState())

        params.cBs_SDD = []
        self.Widget_for_7SDD.SDD_ch8.setEnabled(False)
        self.Widget_for_7SDD.SDD_ch9.setEnabled(False)
        for i in range(1, 8):
            params.cBs_SDD.append(getattr(self.Widget_for_7SDD, 'SDD_ch' + str(i)))

        params.cBs_SDD_checkstates = []
        for cb in params.cBs_SDD:
            cb.setCheckState(QtCore.Qt.Checked)
            params.cBs_SDD_checkstates.append(cb.checkState())
        def record_CheckState_SDD():
            params.cBs_SDD_checkstates = []
            for cb in params.cBs_SDD:
                params.cBs_SDD_checkstates.append(cb.checkState())

        params.cBs_DUBBLE = []
        for i in range(0, 9):
            params.cBs_DUBBLE.append(getattr(self.Widget_for_DUBBLE, 'SDD_ch' + str(i)))

        params.cBs_DUBBLE_checkstates = []
        for cb in params.cBs_DUBBLE:
            print (cb.objectName())
            cb.setCheckState(QtCore.Qt.Checked)
            params.cBs_DUBBLE_checkstates.append(cb.checkState())
        def record_CheckState_DUBBLE():
            params.cBs_DUBBLE_checkstates = []
            for cb in params.cBs_SDD:
                params.cBs_DUBBLE_checkstates.append(cb.checkState())


        params.colours5 = ["#FF0000","#0000FF","#00CC00","#FF007F","#000000"]
        params.colours6 = ["#FF0000", "#0000FF", "#00CC00", "#00008B", "#FF007F", "#000000"]

        for cb in params.cBs_36XU:
            cb.setAutoFillBackground(True)
            plt = cb.palette()
            j = params.cBs_36XU.index(cb)%5
            # print j
            print (params.colours5[j])
            RGBCOLOR = hex2rgb(params.colours5[j])
            plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            #plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(params.colours5[j]))
            RGBCOLOR = hex2rgb("#FFFFFF")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            cb.setPalette(plt)
            RGBCOLOR = hex2rgb("#808080")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            

        for cb in params.cBs_BL14B1:
            cb.setAutoFillBackground(True)
            plt = cb.palette()
            j = params.cBs_BL14B1.index(cb)%6
            # print j
            #plt.setColor(cb.backgroundRole(), params.colours6[j])
            RGBCOLOR = hex2rgb(params.colours6[j])
            plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            #plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(params.colours5[j]))
            RGBCOLOR = hex2rgb("#FFFFFF")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            cb.setPalette(plt)
            RGBCOLOR = hex2rgb("#808080")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            
            # plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(params.colours6[j]))
            # plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb("#FFFFFF"))
            # cb.setPalette(plt)
            # palette.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb("#808080"))
            

        for cb in params.cBs_SDD:
            cb.setAutoFillBackground(True)
            plt = cb.palette()
            RGBCOLOR = hex2rgb(params.colors_in_rgb[params.cBs_SDD.index(cb)])
            plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            #plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(params.colours5[j]))
            RGBCOLOR = hex2rgb("#FFFFFF")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            cb.setPalette(plt)
            RGBCOLOR = hex2rgb("#808080")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            
            #plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(params.colors[params.cBs_SDD.index(cb)]))
            #plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb("#FFFFFF"))
            #cb.setPalette(plt)
            #palette.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb("#808080"))
            #plt.setColor(cb.backgroundRole(), params.colors[params.cBs_SDD.index(cb)])
            #plt.setColor(cb.foregroundRole(), "#FFFFFF")
            #cb.setPalette(plt)
            #palette.setColor(cb.foregroundRole(), "Grey")

        for cb in params.cBs_DUBBLE:
            cb.setAutoFillBackground(True)
            plt = cb.palette()
            j = params.cBs_DUBBLE.index(cb)

            RGBCOLOR = hex2rgb(params.colors_in_rgb[j])
            plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            #plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(params.colours5[j]))
            RGBCOLOR = hex2rgb("#FFFFFF")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            cb.setPalette(plt)
            RGBCOLOR = hex2rgb("#808080")
            plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb(RGBCOLOR[0],RGBCOLOR[1],RGBCOLOR[2]))
            
            # plt.setColor(cb.backgroundRole(), QtGui.QColor.fromRgb(params.colors[j]))
            # plt.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb("#FFFFFF"))
            # cb.setPalette(plt)
            # palette.setColor(cb.foregroundRole(), QtGui.QColor.fromRgb("#808080"))
            
            # plt.setColor(cb.backgroundRole(), params.colors[j])
            # plt.setColor(cb.foregroundRole(), "#FFFFFF")
            # cb.setPalette(plt)
            # palette.setColor(cb.foregroundRole(), "Grey")

        params.BL36XU_ShapingTimes = ["no correction","C:0.5 us"]
        self.u.BL36XU_ST.addItems(params.BL36XU_ShapingTimes)
        self.u.BL36XU_ST.setCurrentIndex(0)
        self.u.BL36XU_Edge.addItems(["K","L"])
        self.u.BL36XU_rB_REX.toggle()

        fig_36XU_1 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        ax_36XU_1 = fig_36XU_1.add_subplot(111)
        ax_36XU_1.set_xlabel("E / eV")
        ax_36XU_1.set_ylabel("$\mu$ t")
        canvas_BL36XU_1 = FigureCanvas(fig_36XU_1)
        self.u.BL36XU_widget1.setLayout(params.grid6)
        BL36XU_navibar_1 = NavigationToolbar(canvas_BL36XU_1, self.u.BL36XU_widget1)
        params.grid6.addWidget(canvas_BL36XU_1, 0, 0)
        params.grid6.addWidget(BL36XU_navibar_1)

        fig_36XU_2 = Figure(figsize=(320, 320), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        ax_36XU_2 = fig_36XU_2.add_subplot(111)
        ax_36XU_2.set_xlabel("E / eV")
        ax_36XU_2.set_ylabel("$\mu$ t")
        canvas_BL36XU_2 = FigureCanvas(fig_36XU_2)
        self.u.BL36XU_widget2.setLayout(params.grid7)
        BL36XU_navibar_2 = NavigationToolbar(canvas_BL36XU_2, self.u.BL36XU_widget2)
        params.grid7.addWidget(canvas_BL36XU_2, 0, 0)
        params.grid7.addWidget(BL36XU_navibar_2)

        scroll_layout_36XU = QtWidgets.QVBoxLayout()
        scroll_widgets_36XU = QtWidgets.QWidget()
        scroll_widgets_36XU.setLayout(scroll_layout_36XU)
        self.u.scrollArea_17.setWidget(scroll_widgets_36XU)

        def plot_each_ch_36XU():
            conf = cwd + "/" + "BL36XU.conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            ax_array = return_new_axis(params.grid6)
            ax_36XU_1 = ax_array[0]
            ax_array = return_new_axis(params.grid7)
            ax_36XU_2 = ax_array[0]

            for axis in [ax_36XU_1,ax_36XU_2]:
                axis.set_xlabel("E / eV")
                axis.set_ylabel("$\mu$ t")
                axis.relim()
                axis.autoscale_view(True,True,True)
            if self.u.rB_BL36XU.isChecked():
                if self.u.BL36XU_ST.currentText() == "no correction":
                    for cb in params.cBs_36XU:
                        if cb.isChecked():
                            ut = np.divide(np.array(params.darray[params.cBs_36XU.index(cb)]), np.array(params.i0))
                            sum = np.add(sum, np.array(params.darray[params.cBs_36XU.index(cb)]))
                            ax_36XU_1.plot(params.Energy, ut, color=params.colours5[params.cBs_36XU.index(cb)%5])
                elif self.u.BL36XU_ST.currentText() != "no correction":
                    params.mode = self.u.BL36XU_ST.currentText().split(":")[0]+"-Mode"
                    #print self.u.BL36XU_ST.currentText().split(":")
                    params.shaping_time = "us" + "{0:0>3}".format(int(float(self.u.BL36XU_ST.currentText().split(":")[1].split(" ")[0])*100.0))
                    print (params.shaping_time)
                    micro = math.pow(10, -6)
                    #k = 0
                    #while k < 25:
                    t1 = float(DT[params.mode]["uni"]["preamp"])*micro
                    print (DT[params.mode]["uni"]["preamp"])
                    t2 = float(DT[params.mode]["uni"]["amp"][params.shaping_time])*micro
                    print (DT[params.mode]["uni"]["amp"][params.shaping_time])
                    for cb in params.cBs_36XU:
                        if cb.isChecked():
                            ut = np.divide(np.array(params.darray[params.cBs_36XU.index(cb)])*(1.0+t1*params.t_ICR[params.cBs_36XU.index(cb)])/(1.0-t2*params.t_ICR[params.cBs_36XU.index(cb)]), np.array(params.i0))
                            sum = np.add(sum, np.array(params.darray[params.cBs_36XU.index(cb)])*(1.0+t1*params.t_ICR[params.cBs_36XU.index(cb)])/(1.0-t2*params.t_ICR[params.cBs_36XU.index(cb)]))
                            ax_36XU_1.plot(params.Energy, ut, color=params.colours5[params.cBs_36XU.index(cb)%5])
                ax_36XU_2.plot(params.Energy, np.divide(sum, params.i0),color = "red")
            elif self.u.rB_BL14B1.isChecked():
                for cb in params.cBs_BL14B1:
                    if cb.isChecked():
                        ut = np.divide(np.array(params.darray[params.cBs_BL14B1.index(cb)]), np.array(params.i0))
                        sum = np.add(sum, np.array(params.darray[params.cBs_BL14B1.index(cb)]))
                        ax_36XU_1.plot(params.Energy, ut, color=params.colours6[params.cBs_BL14B1.index(cb)%6])
                ax_36XU_2.plot(params.Energy, np.divide(sum, params.i0), color="red")
            elif self.u.rB_7elements_SDD.isChecked():
                for cb in params.cBs_SDD:
                    if cb.isChecked():
                        ut = np.divide(np.array(params.darray[params.cBs_SDD.index(cb)]), np.array(params.i0))
                        sum = np.add(sum, np.array(params.darray[params.cBs_SDD.index(cb)]))
                        ax_36XU_1.plot(params.Energy, ut, color=params.colors[params.cBs_SDD.index(cb)])

                ax_36XU_2.plot(params.Energy, np.divide(sum, params.i0), color="red")
            elif self.u.rB_DUBBLE.isChecked():
                for cb in params.cBs_DUBBLE:
                    if cb.isChecked():
                        ut = np.divide(np.array(params.darray[params.cBs_DUBBLE.index(cb)]), np.array(params.i0))
                        sum = np.add(sum, np.array(params.darray[params.cBs_DUBBLE.index(cb)]))
                        ax_36XU_1.plot(params.Energy, ut, color=params.colors[params.cBs_DUBBLE.index(cb)])

                ax_36XU_2.plot(params.Energy, np.divide(sum, params.i0), color="red")

            canvas_BL36XU_1.draw()
            canvas_BL36XU_2.draw()


        def read_dat_36XU(Test_Dat):
            params.ignore_or_not = []
            params.angles = []
            params.aq_time = []
            params.i0 = []
            params.dat = []
            params.ICR = []
            params.Energy = []
            params.darray = np.empty([1, 1])
            params.t_ICR = np.empty([1, 1])
            f = open(Test_Dat, "r")
            if self.u.rB_BL36XU.isChecked():
                i = 0
                for line in f:
                    line.rstrip()
                    if re.match(r".+D=(.+)A.+", line):
                        params.D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                        print (str(params.D))
                    elif re.match(r"\s+Angle\(c\).+", line):
                        t_array = line.split()
                    elif re.match(r"\s+Mode", line):
                        t_array = line.split()
                        params.ignore_or_not = t_array[3:28]
                    elif re.match(r"\s+Offset", line):
                        pass
                    elif len(line.split()) > 23:
                        t_array = line.split()
                        params.angles.append(t_array[1])
                        params.aq_time.append(float(t_array[2]))
                        params.i0.append(float(t_array[28]))
                        params.dat.append(t_array[3:28])
                        params.ICR.append(t_array[31:56])
                    i += 1
                print (params.aq_time)
                k = 0
                while k < 25:
                    if params.ignore_or_not[k] != "0":
                    #print params.cbs[k].checkState()
                        params.cBs_36XU[k].setCheckState(QtCore.Qt.Checked)
                    elif params.ignore_or_not[k] == "0":
                        params.cBs_36XU[k].setEnabled(False)
                    k += 1
                if self.u.cB_keep_condition_2.isChecked():
                    for cb in params.cBs_36XU:
                        cb.setCheckState(params.cBs_36XU_checkstates[params.cBs_36XU.index(cb)])
                params.darray.resize(25, len(params.dat))
                params.t_ICR.resize(25, len(params.dat))
                k = 0
                while k < 25:
                    j = 0
                    while j < len(params.dat):
                        params.darray[k][j] = float(params.dat[j][k])
                        params.t_ICR[k][j] = float(params.ICR[j][k])
                        j += 1
                    k += 1
                j = 0
                while j < len(params.dat):
                    E = 12398.52 / (2 * float(params.D) * np.sin(float(params.angles[j]) / 180 * np.pi))
                    params.Energy.append(E)
                    j += 1
            elif self.u.rB_BL14B1.isChecked():
                i = 0
                for line in f:
                    line.rstrip()
                    if re.match(r".+D=(.+)A.+", line):
                        params.D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                        print (str(params.D))
                    elif re.match(r"\s+Angle\(c\).+", line):
                        t_array = line.split()
                    # print t_array[0]
                    elif re.match(r"\s+Mode", line):
                        t_array = line.split()
                        params.ignore_or_not = t_array[3:39]
                    # print params.ignore_or_not
                    # elif re.match(r"\s+Offset", line):
                    #     pass
                    elif (not 'Offset' in line.rstrip()) and len(line.split()) > 36:
                        t_array = line.split()
                        params.angles.append(t_array[1])
                        params.aq_time.append(float(t_array[2]))
                        params.i0.append(float(t_array[39]))
                        params.dat.append(t_array[3:39])
                        params.ICR.append(t_array[43:79])
                        # print t_array[31:56]
                    # print i
                    i += 1
                print (params.aq_time)
                k = 0
                while k < 36:
                    if params.ignore_or_not[k] != "0":
                        # print params.cbs[k].checkState()
                        params.cBs_BL14B1[k].setCheckState(QtCore.Qt.Checked)
                    elif params.ignore_or_not[k] == "0":
                        params.cBs_BL14B1[k].setEnabled(False)
                    k += 1
                if self.u.cB_keep_condition_2.isChecked():
                    for cb in params.cBs_BL14B1:
                        cb.setCheckState(params.cBs_BL14B1_checkstates[params.cBs_BL14B1.index(cb)])
                params.darray.resize(36, len(params.dat))
                params.t_ICR.resize(36, len(params.dat))
                k = 0
                while k < 36:
                    j = 0
                    while j < len(params.dat):
                        params.darray[k][j] = float(params.dat[j][k])
                        params.t_ICR[k][j] = float(params.ICR[j][k])
                        j += 1
                    k += 1
                # print params.darray[1]
                j = 0
                while j < len(params.dat):
                    E = 12398.52 / (2 * float(params.D) * np.sin(float(params.angles[j]) / 180 * np.pi))
                    params.Energy.append(E)
                    j += 1
            elif self.u.rB_7elements_SDD.isChecked():
                i = 0
                sign = 'None'
                txtData = ''
                for line in f:
                    line.rstrip()
                    if sign != 'read' and re.match(r".+D=(.+)A.+", line):
                        params.D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                        print (str(params.D))
                    elif sign != 'read' and re.match(r"\s+Angle\(c\).+", line):
                        t_array = line.split()
                    # print t_array[0]
                    elif sign != 'read' and re.match(r"\s+Mode", line):
                        # t_array = line.split()
                        # params.ignore_or_not = t_array[3:39]
                        pass
                    # print params.ignore_or_not
                    # elif re.match(r"\s+Offset", line):
                    #     pass
                    elif sign != 'read' and re.match(r"^\s+Offset.*", line):
                        sign = 'read'
                    elif sign == 'read':
                        txtData += line
                    i += 1
                # print params.aq_time
                # k = 0
                df = pd.read_csv(IO.StringIO(txtData), delimiter='\s+', header=None, index_col=False,
                                 names=['Angle(c)', 'Angle(o)', 'time', 'I0', 'CH:1', 'CH:2', 'CH:3', 'CH:4', 'CH:5',
                                        'CH:6', 'CH:7', 'CH:8', 'CH:9'])
                if self.u.cB_keep_condition_2.isChecked():
                    for cb in params.cBs_SDD:
                        cb.setCheckState(params.cBs_SDD_checkstates[params.cBs_SDD.index(cb)])
                # print df
                # if self.u.cB_keep_condition_ExMode.isChecked():
                #     for cb in params.cBs_ExMode:
                #         cb.setCheckState(params.cBs_ExMode_checkstates[params.cBs_ExMode.index(cb)])
                # else:
                #     for cb in params.cBs_SDD:
                #         cb.setCheckState(QtCore.Qt.Checked)
                params.angles = df['Angle(o)'].values
                params.i0 = df['I0'].values
                tmp_list = []
                for name in ['CH:1', 'CH:2', 'CH:3', 'CH:4', 'CH:5', 'CH:6', 'CH:7']:
                    tmp_list.append(df[name].values.tolist())
                params.darray.resize(np.array(tmp_list).shape)
                params.darray += np.array(tmp_list)
                for term in params.angles:
                    E = 12398.52 / (2 * float(params.D) * np.sin(float(term) / 180 * np.pi))
                    params.Energy.append(E)
            elif self.u.rB_DUBBLE.isChecked():
                labels = ['Energy', 'I0', 'It', 'Iref', 'lnI0It', 'lnItIref', 'FF', 'FF/I0', 'Time',
                          'Element:0','Element:1', 'Element:2', 'Element:3', 'Element:4',
                          'Element:5','Element:6', 'Element:7', 'Element:8', 'time']

                df = pd.read_csv(Test_Dat, comment='#',
                                 names=labels, sep=r'\s+')
                tmp_list = []
                for name in ['Element:0','Element:1', 'Element:2', 'Element:3', 'Element:4',
                             'Element:5','Element:6', 'Element:7', 'Element:8']:
                    tmp_list.append(df[name].values.tolist())
                params.i0 = df['I0'].values
                params.darray.resize(np.array(tmp_list).shape)
                params.darray += np.array(tmp_list)
                params.Energy = df['Energy'].values

        def read_dat_36XU_for_SaveMany(Test_Dat):
            ignore_or_not = []
            angles = []
            aq_time = []
            i0 = []
            dat = []
            ICR = []
            Energy = []
            darray = np.empty([1, 1])
            t_ICR = np.empty([1, 1])
            D = 0.0
            f = open(Test_Dat, "r")
            i = 0
            for line in f:
                line.rstrip()
                if re.match(r".+D=(.+)A.+", line):
                    D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                    print (str(D))
                elif re.match(r"\s+Angle\(c\).+", line):
                    t_array = line.split()
                elif re.match(r"\s+Mode", line):
                    t_array = line.split()
                    ignore_or_not = t_array[3:28]
                elif re.match(r"\s+Offset", line):
                    pass
                elif len(line.split()) > 23:
                    t_array = line.split()
                    angles.append(t_array[1])
                    aq_time.append(float(t_array[2]))
                    i0.append(float(t_array[28]))
                    dat.append(t_array[3:28])
                    ICR.append(t_array[31:56])
                    # print t_array[31:56]
                # print i
                i += 1
            k = 0
            darray.resize(25, len(dat))
            t_ICR.resize(25, len(dat))
            k = 0
            while k < 25:
                j = 0
                while j < len(dat):
                    darray[k][j] = float(dat[j][k])
                    t_ICR[k][j] = float(ICR[j][k])
                    j += 1
                k += 1
            # print params.darray[1]
            j = 0
            while j < len(dat):
                E = 12398.52 / (2 * float(D) * np.sin(float(angles[j]) / 180 * np.pi))
                Energy.append(E)
                j += 1
            return Energy, aq_time, i0, darray, t_ICR


        def select_or_release_all_36XU():
            checked_cb = []
            if self.u.rB_BL36XU.isChecked():
                for cb in params.cBs_36XU:
                    if cb.isChecked():
                        checked_cb.append(cb)
            elif self.u.rB_BL14B1.isChecked():
                for cb in params.cBs_BL14B1:
                    if cb.isChecked():
                        checked_cb.append(cb)
            elif self.u.rB_7elements_SDD.isChecked():
                for cb in params.cBs_SDD:
                    if cb.isChecked():
                        checked_cb.append(cb)
            if len(checked_cb) > 0:
                self.u.pushButton_5.setText("Select All")
                for cb in checked_cb:
                    cb.setCheckState(QtCore.Qt.Unchecked)
            elif len(checked_cb) == 0:
                self.u.pushButton_5.setText("Release All")
                if self.u.rB_BL36XU.isChecked():
                    for cb in params.cBs_36XU:
                        cb.setCheckState(QtCore.Qt.Checked)
                elif self.u.rB_BL14B1.isChecked():
                    for cb in params.cBs_BL14B1:
                        cb.setCheckState(QtCore.Qt.Checked)
                elif self.u.rB_7elements_SDD.isChecked():
                    for cb in params.cBs_SDD:
                        cb.setCheckState(QtCore.Qt.Checked)
                # k = 0
                # print len(params.ignore_or_not)
                # while k < 25:
                #     if params.ignore_or_not[k] != "0":
                #         params.cBs_36XU[k].setCheckState(QtCore.Qt.CheckState.Checked)
                #     elif params.ignore_or_not[k] == "0":
                #         params.cBs_36XU[k].setEnabled(False)
                #     k += 1
            plot_each_ch_36XU()

        def plot_36XU():
            params.current_dfile = ""
            params.current_ofile = ""
            for cb in params.cBs_36XU:
                cb.setEnabled(True)
                cb.setCheckState(QtCore.Qt.Unchecked)
            for t_rb in params.d_rbs_36XU:
                if t_rb.isChecked():
                    params.current_dfile = params.dir + "/" + t_rb.objectName()
                    if re.match(r"(.+)\.\d+", t_rb.objectName()) is None:
                        break
                    elif re.match(r"(.+)\.(\d+)", t_rb.objectName()):
                        t_line = t_rb.objectName().split(".")
                        break
            read_dat_36XU(params.current_dfile)
            plot_each_ch_36XU()

        def func_for_rb_36XU():
            plot_36XU()
            self.u.BL36XU_RSall.setText("Release all")

        def ChageState_BL36XU_ST():
            if self.u.rB_BL36XU.isChecked():
                self.u.BL36XU_ST.setEnabled(True)
            else:
                self.u.BL36XU_ST.setEnabled(False)
        for rB in [self.u.rB_BL36XU,self.u.rB_BL14B1,self.u.rB_7elements_SDD]:
            rB.toggled.connect(ChageState_BL36XU_ST)

        def openFiles_BL36XU():
            while scroll_layout_36XU.count() > 0:
                b = scroll_layout_36XU.takeAt(len(params.d_rbs_36XU) - 1)
                params.dfiles_36XU.pop()
                params.d_rbs_36XU.pop()
                b.widget().deleteLater()
            self.u.BL36XU_textBrowser.clear()
            self.u.scrollArea_16.takeWidget()
            dat_dir = home_dir.homePath()
            if params.dir == "":
                dat_dir = home_dir.homePath()
            elif params.dir != "":
                dat_dir = params.dir
            FO_dialog = QtWidgets.QFileDialog(self)
            #files = FO_dialog.getOpenFileNames(parent=None, caption="", dir=dat_dir)
            files = FO_dialog.getOpenFileNames(None, 'Open dat files', dat_dir,
                                              "dat files(*)")
            finfo = QtCore.QFileInfo(files[0][0])
            params.dir = finfo.path()
            self.u.BL36XU_textBrowser.append(params.dir)
            for fname in files[0]:
                info = QtCore.QFileInfo(fname)
                params.dfiles_36XU.append(info.fileName())
            for d_file in params.dfiles_36XU:
                rb = QtWidgets.QRadioButton(d_file)
                rb.setObjectName(d_file)
                params.d_rbs_36XU.append(rb)
                scroll_layout_36XU.addWidget(rb)
            for t_rb in params.d_rbs_36XU:
                t_rb.toggled.connect(func_for_rb_36XU)
            f = open(finfo.absoluteFilePath(),'r')
            line = f.readline().rstrip()
            print (line)
            if re.match(r'\s*9809\s+SPring\-8\s+36.+\s*',line):
                self.u.rB_BL36XU.toggle()
                self.u.scrollArea_16.setWidget(Widget_for_36XU)
            elif re.match(r'\s*9809\s+SPring\-8\s+14b1'r'\s*',line):
                self.u.rB_BL14B1.toggle()
                self.u.scrollArea_16.setWidget(Widget_for_BL14)
            elif re.match(r'\s*9809\s+KEK\-PF\s+(BL|NW).+',line):
                self.u.rB_7elements_SDD.toggle()
                self.u.scrollArea_16.setWidget(Widget_for_7SDD)
            elif 'ESRF DUBBLE' in line:
                self.u.rB_DUBBLE.toggle()
                self.u.scrollArea_16.setWidget(Widget_for_DUBBLE)
            params.d_rbs_36XU[0].toggle()


        def define_outdir_36XU():
            self.u.BL36XU_textBrowser.clear()
            FO_dialog = QtWidgets.QFileDialog(self)
            params.outdir = FO_dialog.getExistingDirectory(None, params.dir)
            self.u.BL36XU_textBrowser.append(params.outdir)

        def Save_36XU():
            conf = cwd + "/" + "BL36XU.conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = ".ex3"
            else:
                exd = ".dat"
            if params.outdir == "":
                o_dir = params.dir
            elif os.path.exists(params.outdir):
                o_dir = params.outdir
            for t_rb in params.d_rbs_36XU:
                if t_rb.isChecked():
                    params.current_ofile = o_dir + "/" + t_rb.objectName() + exd
                    break
                else:
                    pass
            out = open(params.current_ofile, "w")
            if self.u.BL36XU_rB_REX.isChecked():
                line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                atom = "*EX_ATOM=" + self.u.BL36XU_Atom.text() + "\n"
                edge = "*EX_EDGE=" + self.u.BL36XU_Edge.currentText() + "\n"
                line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                line3 = "\n[EX_BEGIN]\n"
                out.write(line + atom + edge + line2 + line3)
            else:
                out.write("#Energy  ut\n")
            if self.u.BL36XU_ST.currentText() == "no correction":
                for cb in params.cBs_36XU:
                    if cb.isChecked():
                        sum = np.add(sum, np.array(params.darray[params.cBs_36XU.index(cb)]))
                        ax_36XU_1.plot(params.Energy, ut, color=params.colours5[params.cBs_36XU.index(cb)%5])
            elif self.u.BL36XU_ST.currentText() != "no correction":
                params.mode = self.u.BL36XU_ST.currentText().split(":")[0]+"-Mode"
                params.shaping_time = "us" + "{0:0>3}".format(int(float(self.u.BL36XU_ST.currentText().split(":")[1].split(" ")[0])*100.0))
                print (params.shaping_time)
                micro = math.pow(10, -6)
                t1 = float(DT[params.mode]["uni"]["preamp"])*micro
                print (DT[params.mode]["uni"]["preamp"])
                t2 = float(DT[params.mode]["uni"]["amp"][params.shaping_time])*micro
                print (DT[params.mode]["uni"]["amp"][params.shaping_time])
                for cb in params.cBs_36XU:
                    if cb.isChecked():
                        #ut = np.divide(np.array(params.darray[params.cBs_36XU.index(cb)])*(1.0+t1*params.t_ICR[params.cBs_36XU.index(cb)])/(1.0-t2*params.t_ICR[params.cBs_36XU.index(cb)]), np.array(params.i0))
                        sum = np.add(sum, np.array(params.darray[params.cBs_36XU.index(cb)])*(1.0+t1*params.t_ICR[params.cBs_36XU.index(cb)])/(1.0-t2*params.t_ICR[params.cBs_36XU.index(cb)]))
                        ax_36XU_1.plot(params.Energy, ut, color=params.colours5[params.cBs_36XU.index(cb)%5])
            ut = np.divide(sum, params.i0)
            k = 0
            while k < len(params.Energy):
                str_ = "%7.3f  %1.8f\n" % (params.Energy[k], ut[k])
                out.write(str_)
                k += 1
            if self.u.BL36XU_rB_REX.isChecked():
                out.write("\n[EX_END]\n")
            else:
                pass

        def Save_all_as_Current_36XU():
            conf = cwd + "/" + "BL36XU.conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            current_ofile = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = '.ex3'
            else:
                exd = '.dat'
            if self.u.BL36XU_textBrowser.toPlainText() != '':
                o_dir = os.path.abspath(self.u.BL36XU_textBrowser.toPlainText())
            for t_rb in params.d_rbs_36XU:
                # sum = np.zeros(len(params.Energy))
                Energy, aq_time, i0, darray, ICR = read_dat_36XU_for_SaveMany(params.dir + "/" + t_rb.objectName())
                sum = np.zeros(len(Energy))
                if re.match(r"(.+)(\.|_)\d+", t_rb.objectName()) is None:
                    current_ofile = o_dir + "/" + t_rb.objectName() + "_000" + exd
                elif re.match(r"(.+)(\.|_)(\d+)", t_rb.objectName()):
                    basename = re.match(r"(.+)(\.|_)(\d+)", t_rb.objectName()).group(1)
                    number = re.match(r"(.+)(\.|_)(\d+)", t_rb.objectName()).group(3)
                    current_ofile = o_dir + "/" + basename + "_" + number + exd
                out = open(current_ofile, "w")
                if self.u.BL36XU_rB_REX.isChecked():
                    line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                    atom = "*EX_ATOM=" + self.u.lineEdit.text() + "\n"
                    edge = "*EX_EDGE=" + self.u.comboBox_2.currentText() + "\n"
                    line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                    line3 = "\n[EX_BEGIN]\n"
                    out.write(line + atom + edge + line2 + line3)
                else:
                    out.write("#Energy  ut\n")
                if self.u.BL36XU_ST.currentText() == "no correction":
                    one_zero_matrix = []
                    for cb in params.cBs_36XU:
                        if cb.isChecked():
                            one_zero_matrix.append(np.ones(len(Energy)))
                        else:
                            one_zero_matrix.append(np.zeros(len(Energy)))
                    sum = np.sum(np.array(darray)*np.array(one_zero_matrix),axis=0)
                elif self.u.BL36XU_ST.currentText() != "no correction":
                    shaping_time = 'us'+self.u.BL36XU_ST.currentText().replace(' ','').replace('us','')
                    micro = math.pow(10, -6)
                    k = 0
                    while k < 25:
                        if params.BL36XU_ST[k].isChecked():
                            j = 0
                            while j < len(params.Energy):
                                sum[j] += darray[k][j] * (
                                    1 + micro * float(ICR[j][k]) / float(aq_time[j]) * float(
                                        DT["C-Mode"]["uni"]["preamp"])) / (
                                              1 - micro * float(ICR[j]) / float(aq_time[j]) * float(
                                                  DT["C-Mode"]["uni"]["amp"][shaping_time]))
                                j += 1
                        k += 1
                ut = np.divide(sum, i0)
                k = 0
                while k < len(Energy):
                    str_ = "%7.3f  %1.8f\n" % (Energy[k], ut[k])
                    out.write(str_)
                    k += 1
                if self.u.BL36XU_rB_REX.isChecked():
                    out.write("\n[EX_END]\n")
                else:
                    pass
                out.close()

        def read_dat_BL14B1_for_SaveMany(Test_Dat):
            ignore_or_not = []
            angles = []
            aq_time = []
            i0 = []
            dat = []
            ICR = []
            Energy = []
            darray = np.empty([1, 1])
            t_ICR = np.empty([1, 1])
            D = 0.0
            f = open(Test_Dat, "r")
            i = 0
            for line in f:
                line.rstrip()
                if re.match(r".+D=(.+)A.+", line):
                    D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                    print (str(D))
                elif re.match(r"\s+Angle\(c\).+", line):
                    t_array = line.split()
                # print t_array[0]
                elif re.match(r"\s+Mode", line):
                    t_array = line.split()
                    ignore_or_not = t_array[3:28]
                # print params.ignore_or_not
                # elif re.match(r"\s+Offset", line):
                #     pass
                elif not("Offset" in line.rstrip()) and len(line.split()) > 23:
                    t_array = line.split()
                    angles.append(t_array[1])
                    aq_time.append(float(t_array[2]))
                    i0.append(float(t_array[39]))
                    dat.append(t_array[3:39])
                    ICR.append(t_array[43:79])
                i += 1
            darray.resize(36, len(dat))
            t_ICR.resize(36, len(dat))
            k = 0
            while k < 36:
                j = 0
                while j < len(dat):
                    darray[k][j] = float(dat[j][k])
                    t_ICR[k][j] = float(ICR[j][k])
                    j += 1
                k += 1
            # print params.darray[1]
            j = 0
            while j < len(dat):
                E = 12398.52 / (2 * float(D) * np.sin(float(angles[j]) / 180 * np.pi))
                Energy.append(E)
                j += 1
            return Energy, aq_time, i0, darray, t_ICR

        def Save_BL14():
            conf = cwd + "/" + "BL14.conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = ".ex3"
            else:
                exd = "_a.dat"
            if params.outdir == "":
                o_dir = params.dir
            elif os.path.exists(params.outdir):
                o_dir = params.outdir
            for t_rb in params.d_rbs_36XU:
                if t_rb.isChecked():
                    params.current_ofile = o_dir + "/" + t_rb.objectName().replace('.dat','') + exd
                    break
                else:
                    pass
            out = open(params.current_ofile, "w")
            if self.u.BL36XU_rB_REX.isChecked():
                line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                atom = "*EX_ATOM=" + self.u.BL36XU_Atom.text() + "\n"
                edge = "*EX_EDGE=" + self.u.BL36XU_Edge.currentText() + "\n"
                line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                line3 = "\n[EX_BEGIN]\n"
                out.write(line + atom + edge + line2 + line3)
            else:
                out.write("#Energy  ut\n")
            # if self.u.BL14_ST.currentText() == "no correction":
            for cb in params.cBs_BL14B1:
                if cb.isChecked():
                    #ut = np.divide(np.array(params.darray[params.cBs_BL14.index(cb)]), np.array(params.i0))
                    sum = np.add(sum, np.array(params.darray[params.cBs_BL14B1.index(cb)]))
                    #ax_36XU_1.plot(params.Energy, ut, color=params.colours6[params.cBs_BL14.index(cb)%6])
            # elif self.u.BL14_ST.currentText() != "no correction":
            #     params.mode = self.u.BL14_ST.currentText().split(":")[0]+"-Mode"
            #     #print self.u.BL14_ST.currentText().split(":")
            #     params.shaping_time = "us" + "{0:0>3}".format(int(float(self.u.BL14_ST.currentText().split(":")[1].split(" ")[0])*100.0))
            #     print params.shaping_time
            #     micro = math.pow(10, -6)
            #     #k = 0
            #     #while k < 25:
            #     t1 = float(DT[params.mode]["uni"]["preamp"])*micro
            #     print DT[params.mode]["uni"]["preamp"]
            #     t2 = float(DT[params.mode]["uni"]["amp"][params.shaping_time])*micro
            #     print DT[params.mode]["uni"]["amp"][params.shaping_time]
            #     for cb in params.cBs_BL14:
            #         if cb.isChecked():
            #             #ut = np.divide(np.array(params.darray[params.cBs_BL14.index(cb)])*(1.0+t1*params.t_ICR[params.cBs_BL14.index(cb)])/(1.0-t2*params.t_ICR[params.cBs_BL14.index(cb)]), np.array(params.i0))
            #             sum = np.add(sum, np.array(params.darray[params.cBs_BL14.index(cb)])*(1.0+t1*params.t_ICR[params.cBs_BL14.index(cb)])/(1.0-t2*params.t_ICR[params.cBs_BL14.index(cb)]))
            #             ax_BL14_1.plot(params.Energy, ut, color=params.colours6[params.cBs_BL14.index(cb)%6])
            ut = np.divide(sum, params.i0)
            k = 0
            while k < len(params.Energy):
                str_ = "%7.3f  %1.8f\n" % (params.Energy[k], ut[k])
                out.write(str_)
                k += 1
            if self.u.BL36XU_rB_REX.isChecked():
                out.write("\n[EX_END]\n")
            else:
                pass

        def read_dat_SDD(Test_Dat):
            params.ignore_or_not = []
            params.angles = []
            params.aq_time = []
            params.i0 = []
            params.dat = []
            params.ICR = []
            params.Energy = []
            params.darray = np.empty([1, 1])
            params.t_ICR = np.empty([1, 1])
            f = open(Test_Dat, "r")
            i = 0
            sign = 'None'
            txtData = ''
            for line in f:
                line.rstrip()
                if sign != 'read' and re.match(r".+D=(.+)A.+", line):
                    params.D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                    print (str(params.D))
                elif sign != 'read' and re.match(r"\s+Angle\(c\).+", line):
                    t_array = line.split()
                # print t_array[0]
                elif sign != 'read' and re.match(r"\s+Mode", line):
                    # t_array = line.split()
                    # params.ignore_or_not = t_array[3:39]
                    pass
                # print params.ignore_or_not
                # elif re.match(r"\s+Offset", line):
                #     pass
                elif sign != 'read' and re.match(r"^\s+Offset.*", line):
                    sign = 'read'
                elif sign =='read':
                    txtData += line
                i += 1
            # print params.aq_time
            # k = 0
            df = pd.read_csv(IO.StringIO(txtData),delimiter='\s+',header=None,index_col=False,
                             names=['Angle(c)','Angle(o)','time','I0','CH:1','CH:2','CH:3','CH:4','CH:5',
                                    'CH:6','CH:7','CH:8','CH:9'])
            # print df
            if self.u.cB_keep_condition_2.isChecked():
                for cb in params.cBs_SDD:
                    cb.setCheckState(params.cBs_SDD_checkstates[params.cBs_SDD.index(cb)])
            else:
                for cb in params.cBs_SDD:
                    cb.setCheckState(QtCore.Qt.Checked)
            params.angles = df['Angle(o)'].values
            params.i0 = df['I0'].values
            tmp_list = []
            for name in ['CH:1','CH:2','CH:3','CH:4','CH:5','CH:6','CH:7']:
                tmp_list.append(df[name].values.tolist())
            #print np.array(tmp_list)
            params.darray.resize(np.array(tmp_list).shape)
            params.darray += np.array(tmp_list)
            # params.darray.resize(36, len(params.dat))
            # params.t_ICR.resize(36, len(params.dat))
            # k = 0
            # while k < 36:
            #     j = 0
            #     while j < len(params.dat):
            #         params.darray[k][j] = float(params.dat[j][k])
            #         params.t_ICR[k][j] = float(params.ICR[j][k])
            #         j += 1
            #     k += 1
            # # print params.darray[1]
            # j = 0
            for term in params.angles:
                E = 12398.52 / (2 * float(params.D) * np.sin(float(term) / 180 * np.pi))
                params.Energy.append(E)

        def Save_SDD():
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = ".ex3"
            else:
                exd = "_a.dat"
            if params.outdir == "":
                o_dir = params.dir
            elif os.path.exists(params.outdir):
                o_dir = params.outdir
            for t_rb in params.d_rbs_36XU:
                if t_rb.isChecked():
                    params.current_ofile = o_dir + "/" + t_rb.objectName().replace('.dat', '') + exd
                    break
                else:
                    pass
            out = open(params.current_ofile, "w")
            if self.u.BL36XU_rB_REX.isChecked():
                line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                atom = "*EX_ATOM=" + self.u.BL36XU_Atom.text() + "\n"
                edge = "*EX_EDGE=" + self.u.BL36XU_Edge.currentText() + "\n"
                line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                line3 = "\n[EX_BEGIN]\n"
                out.write(line + atom + edge + line2 + line3)
            else:
                out.write("#Energy  ut\n")
            # if self.u.BL14_ST.currentText() == "no correction":
            for cb in params.cBs_SDD:
                if cb.isChecked():
                    # ut = np.divide(np.array(params.darray[params.cBs_BL14.index(cb)]), np.array(params.i0))
                    sum += params.darray[params.cBs_SDD.index(cb)]
                    # ax_ExMode_1.plot(params.Energy, ut, color=params.colors[params.cBs_SDD.index(cb)])
            ut = np.divide(sum, params.i0)
            k = 0
            while k < len(params.Energy):
                str_ = "%7.3f  %1.8f\n" % (params.Energy[k], ut[k])
                out.write(str_)
                k += 1
            if self.u.BL36XU_rB_REX.isChecked():
                out.write("\n[EX_END]\n")
            else:
                pass

        def read_dat_BL14B1_for_SaveMany(Test_Dat):
            ignore_or_not = []
            angles = []
            aq_time = []
            i0 = []
            dat = []
            ICR = []
            Energy = []
            darray = np.empty([1, 1])
            t_ICR = np.empty([1, 1])
            D = 0.0
            f = open(Test_Dat, "r")
            i = 0
            for line in f:
                line.rstrip()
                if re.match(r".+D=(.+)A.+", line):
                    D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                    print (str(D))
                elif re.match(r"\s+Angle\(c\).+", line):
                    t_array = line.split()
                # print t_array[0]
                elif re.match(r"\s+Mode", line):
                    t_array = line.split()
                    ignore_or_not = t_array[3:28]
                # print params.ignore_or_not
                # elif re.match(r"\s+Offset", line):
                #     pass
                elif not("Offset" in line.rstrip()) and len(line.split()) > 23:
                    t_array = line.split()
                    angles.append(t_array[1])
                    aq_time.append(float(t_array[2]))
                    i0.append(float(t_array[39]))
                    dat.append(t_array[3:39])
                    ICR.append(t_array[43:79])
                i += 1
            darray.resize(36, len(dat))
            t_ICR.resize(36, len(dat))
            k = 0
            while k < 36:
                j = 0
                while j < len(dat):
                    darray[k][j] = float(dat[j][k])
                    t_ICR[k][j] = float(ICR[j][k])
                    j += 1
                k += 1
            # print params.darray[1]
            j = 0
            while j < len(dat):
                E = 12398.52 / (2 * float(D) * np.sin(float(angles[j]) / 180 * np.pi))
                Energy.append(E)
                j += 1
            return Energy, aq_time, i0, darray, t_ICR

        def Save_all_as_Current_BL14B1():
            conf = cwd + "/" + "BL14.conf"
            str_tconst = open(conf).read()
            DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            current_ofile = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = '.ex3'
            else:
                exd = '_a.dat'
            if self.u.BL36XU_textBrowser.toPlainText() != '':
                o_dir = os.path.abspath(self.u.BL36XU_textBrowser.toPlainText())
            for t_rb in params.d_rbs_36XU:
                # sum = np.zeros(len(params.Energy))
                Energy, aq_time, i0, darray, ICR = read_dat_BL14B1_for_SaveMany(params.dir + "/" + t_rb.objectName())
                sum = np.zeros(len(Energy))
                if re.match(r"(.+)(\.|_)\d+(\.dat)?", t_rb.objectName()) is None:
                    current_ofile = o_dir + "/" + t_rb.objectName() + "_000" + exd
                elif re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()):
                    basename = re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()).group(1)
                    number = re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()).group(3)
                    current_ofile = o_dir + "/" + basename + "_" + number + exd
                out = open(current_ofile, "w")
                if self.u.BL36XU_rB_REX.isChecked():
                    line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                    atom = "*EX_ATOM=" + self.u.lineEdit.text() + "\n"
                    edge = "*EX_EDGE=" + self.u.comboBox_2.currentText() + "\n"
                    line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                    line3 = "\n[EX_BEGIN]\n"
                    out.write(line + atom + edge + line2 + line3)
                else:
                    out.write("#Energy  ut\n")
                # if self.u.BL14_ST.currentText() == "no correction":
                one_zero_matrix = []
                for cb in params.cBs_BL14B1:
                    if cb.isChecked():
                        one_zero_matrix.append(np.ones(len(Energy)))
                    else:
                        one_zero_matrix.append(np.zeros(len(Energy)))
                sum = np.sum(np.array(darray)*np.array(one_zero_matrix),axis=0)
                # elif self.u.BL14_ST.currentText() != "no correction":
                #     shaping_time = 'us'+self.u.BL14_ST.currentText().replace(' ','').replace('us','')
                #     micro = math.pow(10, -6)
                #     k = 0
                #     while k < 36:
                #         if params.BL14_ST[k].isChecked():
                #             j = 0
                #             while j < len(params.Energy):
                #                 sum[j] += darray[k][j] * (
                #                     1 + micro * float(ICR[j][k]) / float(aq_time[j]) * float(
                #                         DT["C-Mode"]["uni"]["preamp"])) / (
                #                               1 - micro * float(ICR[j]) / float(aq_time[j]) * float(
                #                                   DT["C-Mode"]["uni"]["amp"][shaping_time]))
                #                 # sum[j] += params.darray[k][j]/(1-micro*float(params.ICR[j][k])/float(params.aq_time[k])*(float(DT["PF"]["individual"]["amp"][params.shaping_time][k])+float(DT["PF"]["individual"]["preamp"][k])))
                #                 j += 1
                #         k += 1
                ut = np.divide(sum, i0)
                k = 0
                while k < len(Energy):
                    str_ = "%7.3f  %1.8f\n" % (Energy[k], ut[k])
                    out.write(str_)
                    k += 1
                if self.u.BL36XU_rB_REX.isChecked():
                    out.write("\n[EX_END]\n")
                else:
                    pass
                out.close()

        def read_dat_SDD_for_SaveMany(Test_Dat):
            angles = []
            aq_time = []
            i0 = []
            dat = []
            ICR = []
            darray = np.empty([1, 1])
            Energy = []
            f = open(Test_Dat, "r")
            i = 0
            sign = 'None'
            txtData = ''
            D = 3.13551
            for line in f:
                line.rstrip()
                if sign != 'read' and re.match(r".+D=(.+)A.+", line):
                    D = float(re.match(r".+D=\s+(.+)\sA.+", line).group(1))
                    print (str(params.D))
                elif sign != 'read' and re.match(r"\s+Angle\(c\).+", line):
                    t_array = line.split()
                elif sign != 'read' and re.match(r"\s+Mode", line):
                    pass
                elif sign != 'read' and re.match(r"^\s+Offset.*", line):
                    sign = 'read'
                elif sign == 'read':
                    txtData += line
                i += 1

            df = pd.read_csv(IO.StringIO(txtData), delimiter='\s+', header=None, index_col=False,
                             names=['Angle(c)', 'Angle(o)', 'time', 'I0', 'CH:1', 'CH:2', 'CH:3', 'CH:4', 'CH:5',
                                    'CH:6', 'CH:7', 'CH:8', 'CH:9'])

            if self.u.cB_keep_condition_2.isChecked():
                for cb in params.cBs_SDD:
                    cb.setCheckState(params.cBs_SDD_checkstates[params.cBs_SDD.index(cb)])
            else:
                for cb in params.cBs_SDD:
                    cb.setCheckState(QtCore.Qt.Checked)
            angles = df['Angle(o)'].values
            i0 = df['I0'].values
            tmp_list = []
            for name in ['CH:1', 'CH:2', 'CH:3', 'CH:4', 'CH:5', 'CH:6', 'CH:7']:
                tmp_list.append(df[name].values.tolist())
            # print np.array(tmp_list)
            darray.resize(np.array(tmp_list).shape)
            darray += np.array(tmp_list)
            for term in params.angles:
                E = 12398.52 / (2 * float(params.D) * np.sin(float(term) / 180 * np.pi))
                Energy.append(E)
            return Energy, aq_time, i0, darray

        def Save_all_as_Current_SDD():
            # conf = cwd + "/" + "BL14.conf"
            # str_tconst = open(conf).read()
            # DT = yaml.load(str_tconst)
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            current_ofile = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = '.ex3'
            else:
                exd = '_a.dat'
            if self.u.BL36XU_textBrowser.toPlainText() != '':
                o_dir = os.path.abspath(self.u.BL36XU_textBrowser.toPlainText())
            for t_rb in params.d_rbs_36XU:
                # sum = np.zeros(len(params.Energy))
                Energy, aq_time, i0, darray = read_dat_SDD_for_SaveMany(params.dir + "/" + t_rb.objectName())
                sum = np.zeros(len(Energy))
                if re.match(r"(.+)(\.|_)\d+(\.dat)?", t_rb.objectName()) is None:
                    current_ofile = o_dir + "/" + t_rb.objectName() + "_000" + exd
                elif re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()):
                    basename = re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()).group(1)
                    number = re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()).group(3)
                    current_ofile = o_dir + "/" + basename + "_" + number + exd
                out = open(current_ofile, "w")
                if self.u.BL36XU_rB_REX.isChecked():
                    line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                    atom = "*EX_ATOM=" + self.u.lineEdit.text() + "\n"
                    edge = "*EX_EDGE=" + self.u.comboBox_2.currentText() + "\n"
                    line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                    line3 = "\n[EX_BEGIN]\n"
                    out.write(line + atom + edge + line2 + line3)
                else:
                    out.write("#Energy  ut\n")
                # if self.u.BL14_ST.currentText() == "no correction":
                one_zero_matrix = []
                for cb in params.cBs_SDD:
                    if cb.isChecked():
                        one_zero_matrix.append(np.ones(len(Energy)))
                    else:
                        one_zero_matrix.append(np.zeros(len(Energy)))
                sum = np.sum(np.array(darray) * np.array(one_zero_matrix), axis=0)
                # elif self.u.ExMode_OUTPATH.currentText() != "no correction":
                #     shaping_time = 'us' + self.u.ExMode_OUTPATH.currentText().replace(' ', '').replace('us', '')
                #     micro = math.pow(10, -6)
                #     k = 0
                #     while k < 36:
                #         if params.BL14_ST[k].isChecked():
                #             j = 0
                #             while j < len(params.Energy):
                #                 sum[j] += darray[k][j] * (
                #                     1 + micro * float(ICR[j][k]) / float(aq_time[j]) * float(
                #                         DT["C-Mode"]["uni"]["preamp"])) / (
                #                               1 - micro * float(ICR[j]) / float(aq_time[j]) * float(
                #                                   DT["C-Mode"]["uni"]["amp"][shaping_time]))
                                # sum[j] += params.darray[k][j]/(1-micro*float(params.ICR[j][k])/float(params.aq_time[k])*(float(DT["PF"]["individual"]["amp"][params.shaping_time][k])+float(DT["PF"]["individual"]["preamp"][k])))
                                # j += 1
                        # k += 1
                ut = np.divide(sum, i0)
                k = 0
                while k < len(Energy):
                    str_ = "%7.3f  %1.8f\n" % (Energy[k], ut[k])
                    out.write(str_)
                    k += 1
                if self.u.BL36XU_rB_REX.isChecked():
                    out.write("\n[EX_END]\n")
                else:
                    pass
                out.close()

        def read_dat_DUBBLE_for_SaveMany(Test_Dat):
            i0 = []
            dat = []
            darray = np.empty([1, 1])
            Energy = []
            labels = ['Energy', 'I0', 'It', 'Iref', 'lnI0It', 'lnItIref', 'FF', 'FF/I0', 'Time', 'Element:0',
                      'Element:1', 'Element:2', 'Element:3', 'Element:4', 'Element:5',
                      'Element:6', 'Element:7', 'Element:8', 'time']
            df = pd.read_csv(Test_Dat, comment='#',
                             names=labels, sep=r'\s+')

            if self.u.cB_keep_condition_2.isChecked():
                for cb in params.cBs_SDD:
                    cb.setCheckState(params.cBs_DUBBLE_checkstates[params.cBs_DUBBLE.index(cb)])
            else:
                for cb in params.cBs_DUBBLE:
                    cb.setCheckState(QtCore.Qt.Checked)
            i0 = df['I0'].values
            tmp_list = []
            for name in ['Element:0','Element:1', 'Element:2', 'Element:3', 'Element:4',
                         'Element:5','Element:6', 'Element:7', 'Element:8']:
                tmp_list.append(df[name].values.tolist())
            # print np.array(tmp_list)
            darray.resize(np.array(tmp_list).shape)
            darray += np.array(tmp_list)
            Energy = df['Energy'].values
            print (Energy)
            return Energy, i0, darray

        def Save_all_as_Current_DUBBLLE():
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            current_ofile = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = '.ex3'
            else:
                exd = '_a.dat'
            if self.u.BL36XU_textBrowser.toPlainText() != '':
                o_dir = os.path.abspath(self.u.BL36XU_textBrowser.toPlainText())
            for t_rb in params.d_rbs_36XU:
                # sum = np.zeros(len(params.Energy))
                Energy, i0, darray = read_dat_DUBBLE_for_SaveMany(params.dir + "/" + t_rb.objectName())
                sum = np.zeros(len(Energy))
                if re.match(r"(.+)(\.|_)\d+(\.dat)?", t_rb.objectName()) is None:
                    current_ofile = o_dir + "/" + t_rb.objectName() + "_000" + exd
                elif re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()):
                    basename = re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()).group(1)
                    number = re.match(r"(.+)(\.|_)(\d+)(\.dat)?", t_rb.objectName()).group(3)
                    current_ofile = o_dir + "/" + basename + "_" + number + exd
                out = open(current_ofile, "w")
                if self.u.BL36XU_rB_REX.isChecked():
                    line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                    atom = "*EX_ATOM=" + self.u.lineEdit.text() + "\n"
                    edge = "*EX_EDGE=" + self.u.comboBox_2.currentText() + "\n"
                    line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                    line3 = "\n[EX_BEGIN]\n"
                    out.write(line + atom + edge + line2 + line3)
                else:
                    out.write("#Energy  ut\n")
                # if self.u.BL14_ST.currentText() == "no correction":
                one_zero_matrix = []
                for cb in params.cBs_DUBBLE:
                    if cb.isChecked():
                        one_zero_matrix.append(np.ones(len(Energy)))
                    else:
                        one_zero_matrix.append(np.zeros(len(Energy)))
                sum = np.sum(np.array(darray) * np.array(one_zero_matrix), axis=0)
                ut = np.divide(sum, i0)
                k = 0
                while k < len(Energy):
                    str_ = "%7.3f  %1.8f\n" % (Energy[k], ut[k])
                    out.write(str_)
                    k += 1
                if self.u.BL36XU_rB_REX.isChecked():
                    out.write("\n[EX_END]\n")
                else:
                    pass
                out.close()

        def Save_DUBBLE():
            sum = np.zeros(len(params.Energy))
            ut = np.zeros(len(params.Energy))
            o_dir = params.dir
            exd = ""
            if self.u.BL36XU_rB_REX.isChecked():
                exd = ".ex3"
            else:
                exd = "_a.dat"
            if params.outdir == "":
                o_dir = params.dir
            elif os.path.exists(params.outdir):
                o_dir = params.outdir
            for t_rb in params.d_rbs_36XU:
                if t_rb.isChecked():
                    params.current_ofile = o_dir + "/" + t_rb.objectName().replace('.dat', '') + exd
                    break
                else:
                    pass
            out = open(params.current_ofile, "w")
            if self.u.BL36XU_rB_REX.isChecked():
                line = "[EX_DATA]\n*DATE=\n*EX_SAMPLE=\n"
                atom = "*EX_ATOM=" + self.u.BL36XU_Atom.text() + "\n"
                edge = "*EX_EDGE=" + self.u.BL36XU_Edge.currentText() + "\n"
                line2 = "*EX_COMMENT=\n*EX_GONIO=\n*EX_ATTACHIMENT=\n*EX_TARGET=\n*EX_FILAMENT=\n*EX_MEASURE=\n*EX_I0_DETECTOR=\n*EX_I_DETECTOR=\n*EX_CRYSTAL=\n*EX_2D=\n*EX_KV=\n*EX_MA=\n*EX_SLIT_DS=\n*EX_SLIT_RS=\n*EX_SLIT_H=\n*EX_REPEAT=\n*EX_AREA1=\n*EX_AREA2=\n*EX_AREA3=\n*EX_AREA4=\n*EX_AREA5=\n"
                line3 = "\n[EX_BEGIN]\n"
                out.write(line + atom + edge + line2 + line3)
            else:
                out.write("#Energy  ut\n")
            # if self.u.BL14_ST.currentText() == "no correction":
            for cb in params.cBs_DUBBLE:
                if cb.isChecked():
                    # ut = np.divide(np.array(params.darray[params.cBs_BL14.index(cb)]), np.array(params.i0))
                    sum += params.darray[params.cBs_DUBBLE.index(cb)]
                    # ax_ExMode_1.plot(params.Energy, ut, color=params.colors[params.cBs_SDD.index(cb)])
            ut = np.divide(sum, params.i0)
            k = 0
            while k < len(params.Energy):
                str_ = "%7.3f  %1.8f\n" % (params.Energy[k], ut[k])
                out.write(str_)
                k += 1
            if self.u.BL36XU_rB_REX.isChecked():
                out.write("\n[EX_END]\n")
            else:
                pass

        def Save_each_data():
            if self.u.rB_BL36XU.isChecked():
                print ('Save_36XU')
                Save_36XU()
            elif self.u.rB_BL14B1.isChecked():
                print ('Save_BL14B1')
                Save_BL14()
            elif self.u.rB_7elements_SDD.isChecked():
                print ('Save SDD')
                Save_SDD()
            elif self.u.rB_DUBBLE.isChecked():
                print ('Save DUBBLE')
                Save_DUBBLE()

        def Save_many_data():
            if self.u.rB_BL36XU.isChecked():
                print ('Save_36XU')
                Save_all_as_Current_36XU()
            elif self.u.rB_BL14B1.isChecked():
                print ('Save_BL14B1')
                Save_all_as_Current_BL14B1()
            elif self.u.rB_7elements_SDD.isChecked():
                print ('Save SDD')
                Save_all_as_Current_SDD()
            elif self.u.rB_DUBBLE.isChecked():
                print ('Save DUBBLE')
                Save_all_as_Current_DUBBLLE()

        self.u.BL36XU_Open.clicked.connect(openFiles_BL36XU)
        self.u.BL36XU_RSall.clicked.connect(select_or_release_all_36XU)
        self.u.BL36XU_outpath.clicked.connect(define_outdir_36XU)
        self.u.BL36XU_ST.currentIndexChanged.connect(plot_each_ch_36XU)
        self.u.BL36XU_Save.clicked.connect(Save_each_data)
        self.u.pB_save_all_SSD_2.clicked.connect(Save_many_data)
        for cb in params.cBs_36XU:
            cb.clicked.connect(plot_each_ch_36XU)
            cb.clicked.connect(record_CheckState_BL36XU)
        for cb in params.cBs_BL14B1:
            cb.clicked.connect(plot_each_ch_36XU)
            cb.clicked.connect(record_CheckState_BL14B1)
        for cb in params.cBs_SDD:
            cb.clicked.connect(plot_each_ch_36XU)
            cb.clicked.connect(record_CheckState_SDD)
        for cb in params.cBs_DUBBLE:
            cb.clicked.connect(plot_each_ch_36XU)
            cb.clicked.connect(record_CheckState_DUBBLE)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()


if __name__ == "__main__":
    wid = MainWindow()
    sys.exit(app.exec_())
