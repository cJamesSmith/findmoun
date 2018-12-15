"""
Author: Chen Xianwei & WangYufeng
Zhejiang University, Hangzhou, China
Date: 2018/11/21
Version: V 1.0

"""
from __future__ import with_statement
import numpy as np
import sys
import oscillator
from PyQt5 import QtCore, QtGui
from libs.oscilloscope.wave import Wave
from PyQt5 import QtWidgets
from Ui_qtdesigner import Ui_MainWindow
import os
import matplotlib.pyplot as plt
from pylab import *
import peakutils
from PyQt5.QtWidgets import QMessageBox
import time
import asyncio

class DesignerMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):        
        super(DesignerMainWindow, self).__init__(parent)               
        self.setupUi(self)
        self.selectButton.clicked.connect(self.Start_to_do_something)
        self.stopButton.clicked.connect(self.Start_to_do_nothing)
        self.tableWidget.cellClicked.connect(self.update_graph)
        self.actionexit_it.triggered.connect(app.quit)
        self.actionAbout_QT.triggered.connect(self.aboutQT)
        self.actionAbout_PYQT.triggered.connect(self.aboutPYQT)
        self.actionAbout_ZJU.triggered.connect(self.aboutZJU)
        self.tableWidget.setHorizontalHeaderLabels(['filename'])
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.line_Directory.setReadOnly(True)
        self.textEdit.setReadOnly(True)
        self.button_Browse.clicked.connect(self.browse)
        self.getthread = Getthread()
        self.analysis = Analysis()
        self.getthread.saving_signal.connect(self.Oscillator_save)
        self.analysis.saving_signal.connect(self.AnalysisInfo)
        self.analysis.save_img.connect(self.save_img)
        self.analysis.save_ans.connect(self.save_ans)
        self.analysis.save_pow.connect(self.save_pow)
        self.analysis.save_qow.connect(self.save_qow)
        self.currentwave = []
        self.count = 0
        self.modeposition = 0
        
    def browse(self): 
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Find Folder", QtCore.QDir.currentPath())
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.line_Directory.setText(directory)
        dirIterator = QtCore.QDirIterator(directory,  ['*.txt'])
        while(dirIterator.hasNext()):
            dirIterator.next()
            dataname = dirIterator.filePath()
            name = QtWidgets.QTableWidgetItem(dataname)
            analysis = QtWidgets.QTableWidgetItem('Not Yet')
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, name)

    
    def get_the_wave(self, filename):
        col1 = np.loadtxt(filename,  delimiter='\t',  usecols = (0,),  dtype = float)
        col2 = np.loadtxt(filename,  delimiter='\t',  usecols = (1,),  dtype = float)
        return col1,  col2
        
    def get_the_result(self,  t):
        self.currentwave = t

    def Oscillator_save(self,  x,  y,  n):
        if (Ui_MainWindow.stdo == 1):
            n = len(os.listdir(self.line_Directory.text()))
            self.textEdit.append('...We have already gotten ' + str(n) + ' signals')
            self.textEdit.append('...preparing for the next signal')
            self.textEdit.append('...connection rebuild')
            self.textEdit.append('...waiting for the next signal')
            self.textEdit.append('...')
            outfile = open(self.line_Directory.text() + '/' + str(n) + '.txt', 'w+')
            for _x, _y in zip(x,y):
                outfile.write(str(_x) + '\t' + str(_y) + '\n')
            outfile.close()
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            name = QtWidgets.QTableWidgetItem(self.line_Directory.text() + '/' + str(n) + '.txt')
            analysis = QtWidgets.QTableWidgetItem('Not Yet')
            self.tableWidget.setItem(row, 0, name)
            self.tableWidget.setItem(row, 1, analysis)
            time,  voltage = self.get_the_wave(self.tableWidget.item(row,  0).text())
            self.mpl.canvas.ax.clear()
            self.mpl.canvas.ax.get_xaxis().grid(True)  
            self.mpl.canvas.ax.get_yaxis().grid(True)
            self.mpl.canvas.ax.plot(voltage,  'k')
            self.mpl.canvas.ax.set_title('Original Wave')
            self.mpl.canvas.ax.set_ylabel(r'$Amplitude(V)$')
            self.mpl.canvas.ax.set_xticklabels(('0', '2.0', '4.0', '6.0', '8.0',  '10.0'))
            updated_voltage = np.fft.rfft(voltage)
            for i in range(len(updated_voltage)):
                updated_voltage[i] = 0
            updated_voltage = np.fft.irfft(updated_voltage)  
            self.mpl.canvas.draw()
        
       
    def Start_to_do_something(self):
        Ui_MainWindow.stdo = 1

        if self.folderbutton.isChecked():
            if len(self.line_Directory.text()) == 0:
                self.textEdit.append('Sorry! You must choose a directory!')
                return
            self.selectButton.setEnabled(False)
            self.folderbutton.setEnabled(False)
            self.directlybutton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.peakthresholdbox.setEnabled(False)
            self.peakthresholdbox_2.setEnabled(False)
            self.triggerbox.setEnabled(False)
            self.triggerbox_2.setEnabled(False)
            self.button_Browse.setEnabled(False)
            self.textEdit.append('<p><br /></p><p><strong>Analyzing......</strong></p><p><strong>It will take a long time.</strong></p><p><strong>Please wait patiently!</strong></p>')
            self.analysis.begin(self.line_Directory.text())

        
        else:
            if len(self.line_Directory.text()) == 0:
                self.textEdit.append('Sorry! You must choose a directory!')
                return
            self.selectButton.setEnabled(False)
            self.folderbutton.setEnabled(False)
            self.directlybutton.setEnabled(False)
            self.peakthresholdbox.setEnabled(False)
            self.peakthresholdbox_2.setEnabled(False)
            self.triggerbox.setEnabled(False)
            self.triggerbox_2.setEnabled(False)
            self.button_Browse.setEnabled(False)

            isgood = self.getthread.Begin(self.line_Directory.text() + '/')
            if isgood == -1:
                self.textEdit.append('Sorry! The device dose not work! Please check it out!')

    def Start_to_do_nothing(self):
        Ui_MainWindow.stdo = 0
        self.selectButton.setEnabled(True)
        self.folderbutton.setEnabled(True)
        self.directlybutton.setEnabled(True)
        self.peakthresholdbox.setEnabled(True)
        self.peakthresholdbox_2.setEnabled(True)
        self.triggerbox.setEnabled(True)
        self.triggerbox_2.setEnabled(True)
        self.button_Browse.setEnabled(True)
        
        
    def update_graph(self,  row,  col):
        time,  voltage = self.get_the_wave(self.tableWidget.item(row,  0).text())
        self.mpl.canvas.ax.clear()
        self.mpl.canvas.ax.get_xaxis().grid(True)  
        self.mpl.canvas.ax.get_yaxis().grid(True)
        self.mpl.canvas.ax.plot(voltage,  'k')
        self.mpl.canvas.ax.set_title('Original Wave')
        self.mpl.canvas.ax.set_ylabel(r'$Amplitude(V)$')
        self.mpl.canvas.ax.set_xticklabels(('0', '2.0', '4.0', '6.0', '8.0',  '10.0'))
        updated_voltage = np.fft.rfft(voltage)
        for i in range(len(updated_voltage)):
            if True:
                updated_voltage[i] = 0
        self.mpl.canvas.draw()

    def AnalysisInfo(self, _str):
        self.textEdit.append(_str)
        if _str == 'Done!!':
            self.selectButton.setEnabled(True)
            self.folderbutton.setEnabled(True)
            self.directlybutton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.peakthresholdbox.setEnabled(True)
            self.peakthresholdbox_2.setEnabled(True)
            self.triggerbox.setEnabled(True)
            self.triggerbox_2.setEnabled(True)
            self.button_Browse.setEnabled(True)

    def aboutQT(self):
        QMessageBox.aboutQt(self, 'About QT')

    def aboutPYQT(self):
        QMessageBox.about(self, 'About PYQT5', '<p><p style="text-align:justify;font-family:&quot;font-size:16px;background-color:#FFFFFF;">PyQt5 is dual licensed on all platforms under the Riverbank Commercial License and the GPL v3. Your PyQt5 license must be compatible with your Qt license. If you use the GPL version then your own code must also use a compatible license.</p><p style="text-align:justify;font-family:&quot;font-size:16px;background-color:#FFFFFF;">PyQt5, unlike Qt, is not available under the LGPL.</p><p style="text-align:justify;font-family:&quot;font-size:16px;background-color:#FFFFFF;">You can purchase a commercial PyQt5 license&nbsp;<a class="reference external" href="https://www.riverbankcomputing.com/commercial/buy">here</a>.</p></p>')
    
    def aboutZJU(self):
        QMessageBox.about(self, 'About ZJU', '<p>866 Yuhangtang Rd, Hangzhou 310058, P.R. China&nbsp;</p><p>Copyright &copy; 2018 <a href="http://www.zju.edu.cn/" target="_blank">Zhejiang University</a>&nbsp;</p><p>Seeking Truth, Pursuing Innovation.</p>')
    
        
    def save_img(self, x, y, i, indexes):
            plt.plot(x, y)
            plt.plot(x[indexes], y[indexes], 'o-r')
            plt.savefig(self.line_Directory.text() + '\\' + str(i) + '.jpg')
            plt.close()

    def save_ans(self, title, distribute):
            plt.bar(range(len(distribute)), distribute)
            plt.title(title)
            plt.xlabel('The life time of moun(us)')
            plt.ylabel('The number of the moun')
            plt.savefig(self.line_Directory.text() + '\\' + 'finalDistribution.jpg')
            plt.close()

    def save_pow(self, title, distribute):
            plt.bar(range(len(distribute)), distribute)
            plt.title(title)
            plt.xlabel('The power level of moun(V)')
            plt.ylabel('The number of the moun')
            plt.savefig(self.line_Directory.text() + '\\' + 'powerofMoun.jpg')
            plt.show()

    def save_qow(self, title, distribute):
            plt.bar(range(len(distribute)), distribute)
            plt.title(title)
            plt.xlabel('The power level of elec(V)')
            plt.ylabel('The number of the moun')
            plt.savefig(self.line_Directory.text() + '\\' + 'powerofElec.jpg')
            plt.close()

class Getthread(QtCore.QThread):
        #直接从示波器获取的线程
        _signal = QtCore.pyqtSignal(int)
        saving_signal = QtCore.pyqtSignal(list,  list,  int)
        def __init__(self):
            super(Getthread,self).__init__()
            self.isgood = -1
        def Begin(self,  directory):
            self.wave = oscillator.The_wave(directory)
            self.start()
            return self.isgood
        def run(self):
            n = 0
            while Ui_MainWindow.stdo == 1:
                n = n + 1
                try:
                    x,  y = self.wave.get_wave(dmw.triggerbox.value())
                except:
                    self.quit()
                    self.isgood = -1
                    return
                else:
                    self.isgood = 0
                    self.saving_signal.emit(x,  y,  n)

class Analysis(QtCore.QThread):
        #分析的线程
        #_signal = QtCore.pyqtSignal(int)
        saving_signal = QtCore.pyqtSignal(str)
        save_img = QtCore.pyqtSignal(np.ndarray, np.ndarray, int, np.ndarray)
        save_ans = QtCore.pyqtSignal(str, list)
        save_pow = QtCore.pyqtSignal(str, list)
        save_qow = QtCore.pyqtSignal(str, list)
        def __init__(self):
            super(Analysis, self).__init__()
        def begin(self, directory):
            self.directory = directory
            self.start()

        def run(self):
            while Ui_MainWindow.stdo == 1:
                distribute_lifetime = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                distribute_moun     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                distribute_elec     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                ave_time  = 0.0
                ave_power = 0.0
                ave_qower = 0.0

                num_of_moun   = 0
                power_of_moun = 0
                power_of_elec = 0

                try:
                    num_of_file = len(os.listdir(self.directory))
                except:
                    self.saving_signal.emit('Sorry! The directory is wrong! Please check it out!')
                    Ui_MainWindow.stdo = 0
                    return
                else:
                    pass
                for i in range(1, num_of_file):
                    filename = self.directory + '\\' + str(i) + ".txt"
                    try:
                        x = np.loadtxt(filename,  delimiter='\t',  usecols = (0,),  dtype = float)
                        y = np.loadtxt(filename,  delimiter='\t',  usecols = (1,),  dtype = float)

                    except IOError:
                        continue

                    else:
                        y = np.fft.rfft(y)

                        for j in range(len(y)):
                            y[j] = -y[j]
                            if abs(y[j]) < 30:
                                y[j] = 0

                        y = np.fft.irfft(y)

                        indexes = peakutils.indexes(y, thres=0.2, min_dist=20)


                        if (len(indexes) >= 2 and y[int((indexes[0] + indexes[1]) / 2)] < (0.9 * min(y[indexes[0]], y[indexes[1]])) and y[indexes[0]] == max(y[indexes])):

                            indexes = np.delete(indexes, range(2, len(indexes)))
                            print(indexes)
                            self.save_img.emit(x, y, i, indexes)

                            if x[indexes[1]] - x[indexes[0]] < 1e-6:
                                distribute_lifetime[0] += 1
                            elif 1e-6 <= x[indexes[1]] - x[indexes[0]] < 2e-6:
                                distribute_lifetime[1] += 1
                            elif 2e-6 <= x[indexes[1]] - x[indexes[0]] < 3e-6:
                                distribute_lifetime[2] += 1
                            elif 3e-6 <= x[indexes[1]] - x[indexes[0]] < 4e-6:
                                distribute_lifetime[3] += 1
                            elif 4e-6 <= x[indexes[1]] - x[indexes[0]] < 5e-6:
                                distribute_lifetime[4] += 1
                            elif 5e-6 <= x[indexes[1]] - x[indexes[0]] < 6e-6:
                                distribute_lifetime[5] += 1
                            elif 6e-6 <= x[indexes[1]] - x[indexes[0]] < 7e-6:
                                distribute_lifetime[6] += 1
                            elif 7e-6 <= x[indexes[1]] - x[indexes[0]] < 8e-6:
                                distribute_lifetime[7] += 1
                            elif 8e-6 <= x[indexes[1]] - x[indexes[0]] < 9e-6:
                                distribute_lifetime[8] += 1
                            elif 9e-6 <= x[indexes[1]] - x[indexes[0]] < 10e-6:
                                distribute_lifetime[9] += 1
                            else:
                                distribute_lifetime[10] += 1

                            ave_time += x[indexes[1]] - x[indexes[0]]

                            if y[indexes[0]] < 0.5:
                                distribute_moun[0] += 1
                            elif 0.5 <= y[indexes[0]] < 1:
                                distribute_moun[1] += 1
                            elif 1 <= y[indexes[0]] < 1.5:
                                distribute_moun[2] += 1
                            elif 1.5 <= y[indexes[0]] < 2:
                                distribute_moun[3] += 1
                            elif 2 <= y[indexes[0]] < 2.5:
                                distribute_moun[4] += 1
                            elif 2.5 <= y[indexes[0]] < 3:
                                distribute_moun[5] += 1
                            elif 3 <= y[indexes[0]] < 3.5:
                                distribute_moun[6] += 1
                            elif 3.5 <= y[indexes[0]] < 4:
                                distribute_moun[7] += 1
                            elif 4 <= y[indexes[0]] < 4.5:
                                distribute_moun[8] += 1
                            elif 4.5 <= y[indexes[0]] < 5:
                                distribute_moun[9] += 1
                            else:
                                distribute_moun[10] += 1

                            ave_power += y[indexes[0]]

                            if y[indexes[1]] < 0.5:
                                distribute_elec[0] += 1
                            elif 0.5 <= y[indexes[1]] < 1:
                                distribute_elec[1] += 1
                            elif 1 <= y[indexes[1]] < 1.5:
                                distribute_elec[2] += 1
                            elif 1.5 <= y[indexes[1]] < 2:
                                distribute_elec[3] += 1
                            elif 2 <= y[indexes[1]] < 2.5:
                                distribute_elec[4] += 1
                            elif 2.5 <= y[indexes[1]] < 3:
                                distribute_elec[5] += 1
                            elif 3 <= y[indexes[1]] < 3.5:
                                distribute_elec[6] += 1
                            elif 3.5 <= y[indexes[1]] < 4:
                                distribute_elec[7] += 1
                            elif 4 <= y[indexes[1]] < 4.5:
                                distribute_elec[8] += 1
                            elif 4.5 <= y[indexes[1]] < 5:
                                distribute_elec[9] += 1
                            else:
                                distribute_elec[10] += 1

                            ave_qower += y[indexes[1]]
            
                for item in distribute_lifetime:
                    num_of_moun += item
                for item in distribute_moun:
                    power_of_moun += item
                for item in distribute_elec:
                    power_of_elec += item
                try:
                    ave_time  /= num_of_moun
                    ave_power /= power_of_moun
                    ave_qower /= power_of_elec

                except ZeroDivisionError:
                    self.save_ans.emit('Sorry! No moun!', distribute_lifetime)
                    self.save_qow.emit('Sorry! No moun!', distribute_moun)
                    self.save_pow.emit('Sorry! No moun!', distribute_moun)
                    self.saving_signal.emit('Done!!')
                    self.saving_signal.emit('The number of moun is ' + str(num_of_moun) + ' in ' + str(len(os.listdir(self.directory))) + 'datas!')
                    Ui_MainWindow.stdo = 0

                else:
                    self.save_ans.emit('The number of moun is ' + str(num_of_moun) + '\n' + 'The average lifetime is ' + str(ave_time), distribute_lifetime)
                    self.save_qow.emit('The average power of moun is ' + str(ave_qower), distribute_elec)
                    self.save_pow.emit('The average power of moun is ' + str(ave_power), distribute_moun)
                    self.saving_signal.emit('Done!!')
                    self.saving_signal.emit('The number of moun is ' + str(num_of_moun) + ' in ' + str(len(os.listdir(self.directory))) + 'datas!')
                    self.saving_signal.emit('The average lifetime is' + str(ave_time))
                    self.saving_signal.emit('The average power of elec is' + str(ave_qower))
                    self.saving_signal.emit('The average power of moun is' + str(ave_power))
                    Ui_MainWindow.stdo = 0
                

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    t = QtCore.QElapsedTimer()
    t.start()
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap("logo.jpg"))
    while t.elapsed() < 1000:
        splash.show()
    splash.finish(splash)
    dmw = DesignerMainWindow()
    dmw.show()
    sys.exit(app.exec_())
