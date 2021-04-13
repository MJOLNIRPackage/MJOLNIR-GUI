import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
except ImportError:
    from _tools import ProgressBarDecoratorArguments

from os import path
from PyQt5 import QtWidgets, uic
import numpy as np

def QPlane_plot_button_function(self):
    # Make plot
    if not self.stateMachine.requireStateByName('Converted'):
        return False
    ds = self.DataSetModel.getCurrentDataSet()
    if len(ds.convertedFiles)==0:
        self.DataSet_convertData_button_function()        
    
    # Check various plot settings
    if self.ui.QPlane_SelectUnits_RLU_radioButton.isChecked():
        rlu=True
    else:
        rlu=False        

    if self.ui.QPlane_LogScale_checkBox.isChecked():
        log=True
    else:
        log=False          

    EMin=float(self.ui.QPlane_EMin_lineEdit.text())
    EMax=float(self.ui.QPlane_EMax_lineEdit.text())
    xBinTolerance = float(self.ui.QPlane_xBinTolerance_lineEdit.text())           
    yBinTolerance = float(self.ui.QPlane_yBinTolerance_lineEdit.text())           

    Data,Bins,ax = ds.plotQPlane(EMin=EMin, EMax=EMax,xBinTolerance=xBinTolerance,yBinTolerance=yBinTolerance,log=log,rlu=rlu)
    
    self.QPlane=ax    
    
    fig = self.QPlane.get_figure()
    fig.colorbar(ax.pmeshs[0])
    fig.set_size_inches(8,6)

    if self.ui.QPlane_Grid_checkBox.isChecked():
        ax.grid(True)
    else:
        ax.grid(False)
    
    self.QPlane_setCAxis_button_function()
    self.QPlane_SetTitle_button_function()
    self.windows.append(self.QPlane.get_figure())

    return True
    

def QPlane_setCAxis_button_function(self):
    CAxisMin=float(self.ui.QPlane_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.QPlane_CAxisMax_lineEdit.text())

    self.QPlane.set_clim(CAxisMin,CAxisMax)
    fig = self.QPlane.get_figure()
    fig.canvas.draw()
    
def QPlane_SetTitle_button_function(self):
    TitleText=self.ui.QPlane_SetTitle_lineEdit.text()        
    if hasattr(self, 'QPlane'):
        TitleText=self.ui.QPlane_SetTitle_lineEdit.text()        
        self.QPlane.set_title(TitleText)
        fig = self.QPlane.get_figure()
        fig.canvas.draw()
    
try:
    QPlaneManagerBase, QPlaneManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"QPlane.ui"))
except:
    try:
        QPlaneManagerBase, QPlaneManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"QPlane.ui"))
    except:
        QPlaneManagerBase, QPlaneManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"QPlane.ui"))

class QPlaneManager(QPlaneManagerBase, QPlaneManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(QPlaneManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initQPlaneManager()

    def initQPlaneManager(self):
        self.guiWindow.QPlane_plot_button_function = lambda: QPlane_plot_button_function(self.guiWindow)
        self.guiWindow.QPlane_setCAxis_button_function = lambda: QPlane_setCAxis_button_function(self.guiWindow)
        self.guiWindow.QPlane_SetTitle_button_function = lambda: QPlane_SetTitle_button_function(self.guiWindow)
        for key,value in self.__dict__.items():
            if 'QPlane' in key:
                self.guiWindow.ui.__dict__[key] = value

    def setup(self):
        
        self.guiWindow.ui.QPlane_plot_button.clicked.connect(self.guiWindow.QPlane_plot_button_function)
        self.guiWindow.ui.QPlane_setCAxis_button.clicked.connect(self.guiWindow.QPlane_setCAxis_button_function)
        self.guiWindow.ui.QPlane_SetTitle_button.clicked.connect(self.guiWindow.QPlane_SetTitle_button_function)
