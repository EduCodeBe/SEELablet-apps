#!/usr/bin/python

"""

::

    This experiment is used to study Half wave rectifiers


"""

from __future__ import print_function
from SEEL_Apps.utilitiesClass import utilitiesClass

from SEEL_Apps.templates import graph_and_sheet

import numpy as np
from PyQt4 import QtGui,QtCore
import pyqtgraph as pg
import sys,functools

params = {
'image' : 'clipping.png',
'name':"Ohm's Law",
'hint':'''
	Study Ohm's Law using resistors and the programmable current source(PCS).<br>
	
	'''

}

class AppWindow(QtGui.QMainWindow, graph_and_sheet.Ui_MainWindow,utilitiesClass):
	def __init__(self, parent=None,**kwargs):
		super(AppWindow, self).__init__(parent)
		self.setupUi(self)
		self.I=kwargs.get('I',None)
		
		self.setWindowTitle(self.I.H.version_string+' : '+params.get('name','').replace('\n',' ') )

		self.plot=self.add2DPlot(self.plot_area,enableMenu=False)
		labelStyle = {'color': 'rgb(255,255,255)', 'font-size': '11pt'}
		self.plot.setLabel('left','Voltage', units='V',**labelStyle)
		self.plot.setLabel('bottom','Current', units='A',**labelStyle)

		self.curve = self.addCurve(self.plot,'IV')
		self.WidgetLayout.setAlignment(QtCore.Qt.AlignLeft)

		self.table.setRowCount(50)
		self.table.setColumnCount(3)
		self.table.setHorizontalHeaderLabels(['Current (A)','Voltage (V)','Resistance'])
		for a in range(50):
			item = QtGui.QTableWidgetItem();item.setText('');self.table.setItem(a, 0, item)
			item = QtGui.QTableWidgetItem();item.setText('');self.table.setItem(a, 1, item)
			item = QtGui.QTableWidgetItem();item.setText('');self.table.setItem(a, 2, item)

		self.current = 0;
		self.readings = 0

		tmpfunc = functools.partial(self.I.DAC.__setRawVoltage__,'PCS')
		a1={'TITLE':'PCS','MIN':100,'MAX':2000,'FUNC':tmpfunc,'UNITS':'A','TOOLTIP':'Programmable Current Source','LINK':self.setCurrent}
		cr_icon = self.dialIcon(**a1);self.WidgetLayout.addWidget(cr_icon); cr_icon.setValue(100)

		tmpfunc = functools.partial(self.I.get_voltage,samples=10)
		a1={'TITLE':'VOLTMETER','FUNC':tmpfunc,'UNITS':'V','TOOLTIP':'Voltmeter','OPTIONS':self.I.allAnalogChannels,'LINK':self.setVoltage}
		self.WidgetLayout.addWidget(self.selectAndButtonIcon(**a1))
		

	def clearData(self):
		for a in range(50):
			self.table.item(a, 0).setText('')
			self.table.item(a, 1).setText('')
			self.table.item(a, 2).setText('')
		self.readings = 0
		self.curve.clear()
		
	def setCurrent(self,val,units=''):
		self.current = val

	def setVoltage(self,val):
		self.table.item(self.readings,0).setText('%.3e'%self.current)
		self.table.item(self.readings,1).setText('%.3e'%val)
		self.table.item(self.readings,2).setText('%.3e'%(val/self.current))
		self.readings+=1

	def plotData(self):
		I,V = self.fetchColumns(self.table,0,1)
		self.curve.setData(I,V)
		self.plot.autoRange()

	def saveData(self):
		self.saveDataWindow([self.curveCH1,self.curveCH2],self.plot)

		
	def closeEvent(self, event):
		self.running=False
		self.finished=True
		

	def __del__(self):
		self.timer.stop()
		print('bye')

if __name__ == "__main__":
    from SEEL import interface
    app = QtGui.QApplication(sys.argv)
    myapp = AppWindow(I=interface.connect())
    myapp.show()
    sys.exit(app.exec_())

