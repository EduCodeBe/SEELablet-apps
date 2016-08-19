#!/usr/bin/python

"""

::

    This experiment is used to study non-inverting amplifiers

"""

from __future__ import print_function
from SEEL_Apps.utilitiesClass import utilitiesClass

from SEEL_Apps.templates import ui_template_graph_nofft as template_graph_nofft

import numpy as np
from PyQt4 import QtGui,QtCore
import pyqtgraph as pg
import sys,functools,time

params = {
'image' : 'tcd.png',
'name':'TCD1304AP\nCCD',
'hint':'''
	Acquire and plot data from a linear CCD array TCD1304AP.<br>
	Experimental feature. Sine waves will be disabled while it runs.<br>
	'''

}

class AppWindow(QtGui.QMainWindow, template_graph_nofft.Ui_MainWindow,utilitiesClass):
	def __init__(self, parent=None,**kwargs):
		super(AppWindow, self).__init__(parent)
		self.setupUi(self)
		self.I=kwargs.get('I',None)
		
		self.setWindowTitle(self.I.H.version_string+' : '+params.get('name','').replace('\n',' ') )

		from SEEL.analyticsClass import analyticsClass
		self.math = analyticsClass()
		self.prescalerValue=0

		self.plot=self.add2DPlot(self.plot_area,enableMenu=True)
		self.enableCrossHairs(self.plot,[])
		labelStyle = {'color': 'rgb(255,255,255)', 'font-size': '11pt'}
		self.plot.setLabel('left','V (CH1)', units='V',**labelStyle)
		self.plot.setLabel('bottom','Time', units='S',**labelStyle)
		self.hLine = pg.InfiniteLine(angle=0, movable=False,pen=[255,10,20,255])
		self.plot.addItem(self.hLine, ignoreBounds=True)
		self.hLine.setPos(3.3)

		self.sh=2; self.icg=2;
		self.samples=3694; self.tweak = 1
		self.chan = 'AN8'
		self.timer = self.newTimer()

		self.legend = self.plot.addLegend(offset=(-10,30))
		self.curveCH1 = self.addCurve(self.plot,'INPUT(%s)'%self.chan)
		self.autoRange()
		
		self.WidgetLayout.setAlignment(QtCore.Qt.AlignLeft)
		self.ControlsLayout.setAlignment(QtCore.Qt.AlignRight)
		self.addRegularButton(self.ControlsLayout,self.setRef,'Set reference')
		self.addRegularButton(self.ControlsLayout,self.resetRef,'Reset reference')
		self.absorbance = self.addPauseButton(self.ControlsLayout,self.calcAbsorbance)
		self.absorbance.setText('Absorbance')
		self.ControlsLayout.addWidget(self.setStateIcon(I=self.I))

		#Utility widgets
		#self.I.set_pv1(4)

		#Control widgets
		a1={'TITLE':'SH','MIN':2,'MAX':10,'FUNC':self.set_timebase,'UNITS':'S','TOOLTIP':'Set SH pulse width, and timebase'}
		self.ControlsLayout.addWidget(self.dialIcon(**a1))
		self.set_timebase(2)

		a1={'TITLE':'Average','MIN':1,'MAX':5,'FUNC':self.set_tweak,'UNITS':' times','TOOLTIP':'Average samples before displaying'}
		T = self.dialIcon(**a1)
		T.dial.setPageStep(1)
		T.dial.setValue(1)
		self.ControlsLayout.addWidget(T)

		a1={'TITLE':'ICG','MIN':1,'MAX':65000,'FUNC':self.set_icg,'UNITS':'S','TOOLTIP':'Set ICG'}
		self.WidgetLayout.addWidget(self.dialIcon(**a1))


		self.running=True
		self.fit = False
		self.timer.singleShot(100,self.run)
		self.Y = np.zeros(3648)
		self.REFY = np.zeros(3648)
		self.setRefFlag = False
		self.num = 0


	def setRef(self):
		self.setRefFlag = True
	def resetRef(self):
		self.REFY = np.zeros(3648)


	def set_tweak(self,g):
		self.tweak = g
		return g

	def set_timebase(self,g):
		self.sh = g
		return self.autoRange()

	def set_icg(self,g):
		self.icg = g
		return g*1e-6

	def calcAbsorbance(self):
		pass
		
	def autoRange(self):
		xlen = 3648
		self.plot.autoRange();
		chan = self.I.analogInputSources[self.chan]
		self.plot.setLimits(yMax=3.3,yMin=-3.3,xMin=0,xMax=xlen)
		self.plot.setYRange(-3.3,3.3)			
		self.plot.setXRange(0,xlen)

		return 3648



	def run(self):
		if not self.running: return
		try:
			self.Y = np.zeros(3648)
			self.num = self.tweak
			for a in range(self.num):
				self.I.opticalArray(self.sh,self.icg,self.chan,resolution=12)
				self.I.__fetch_channel__(1)
				self.Y+=self.I.achans[0].get_yaxis()[32:-14]

			x = range(3648,0,-1)
			self.Y = self.Y/self.num
			self.Y = 3.3-self.Y
			
			if self.setRefFlag:
				self.setRefFlag = False
				self.REFY = self.Y
			else:
				if self.absorbance.isChecked():
					ref = np.copy(self.REFY)
					ref[ref==0]=1
					self.Y = np.log10(self.Y/ref)
				else:
					self.Y -= self.REFY
			self.curveCH1.setData(x,self.Y,connect='finite')
			#print (x,self.Y/self.num)
		except Exception as b:
			#print (b)
			pass

		if self.running:self.timer.singleShot(200,self.run)


	def saveData(self):
		self.saveDataWindow([self.curveCH1],self.plot)

		
	def closeEvent(self, event):
		self.running=False
		self.timer.stop()
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

