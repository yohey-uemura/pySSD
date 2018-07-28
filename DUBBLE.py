        def read_dat_DUBBLE_for_SaveMany(Test_Dat):
            i0 = []
            dat = []
            darray = np.empty([1, 1])
            Energy = []
            labels = ['Energy','I0','It','Iref','lnI0It','lnItIref','FF','FF/I0','Time','Element 0',
                      'Element:1','Element:2','Element:3','Element:4','Element:5',
                      'Element:6', 'Element:7','Element:8','time']
            df = pd.read_csv(Test_Dat, comment='#', 
                 names=labels,sep=r'\s+')            

            if self.u.cB_keep_condition_2.isChecked():
                for cb in params.cBs_SDD:
                    cb.setCheckState(params.cBs_DUBBLE_checkstates[params.cBs_DUBBLE.index(cb)])
            else:
                for cb in params.cBs_DUBBLE:
                    cb.setCheckState(QtCore.Qt.Checked)
            i0 = df['I0'].values
            tmp_list = []
            for name in ['Element:1','Element:2','Element:3','Element:4','Element:5',
                         'Element:6', 'Element:7','Element:8']
                tmp_list.append(df[name].values.tolist())
            # print np.array(tmp_list)
            darray.resize(np.array(tmp_list).shape)
            darray += np.array(tmp_list)
            Energy = df['Energy'].values
            return Energy, aq_time, i0, darray

        def Save_all_as_Current_DUBBLLE():
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
                Energy, aq_time, i0, darray = read_dat_DUBBLE_for_SaveMany(params.dir + "/" + t_rb.objectName())
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
