import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
    import MJOLNIRGui.src.main.python._tools as _GUItools
except ImportError:
    from _tools import ProgressBarDecoratorArguments
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets, uic
import numpy as np


@ProgressBarDecoratorArguments(runningText='Generating QELine plot',completedText='QELine plot generated')
def QELine_plot_button_function(self):    
    # First check if we have data, otherwise convert data
    if not self.stateMachine.requireStateByName('Converted'):
        return False
    
    ds = self.DataSetModel.getCurrentDataSet()
    if len(ds.convertedFiles)==0:
        self.DataSet_convertData_button_function()
        
    # Get the Q points
    HStart=float(self.ui.QELine_HStart_lineEdit.text())
    KStart=float(self.ui.QELine_KStart_lineEdit.text())
    LStart=float(self.ui.QELine_LStart_lineEdit.text())
    
    HEnd=float(self.ui.QELine_HEnd_lineEdit.text())
    KEnd=float(self.ui.QELine_KEnd_lineEdit.text())
    LEnd=float(self.ui.QELine_LEnd_lineEdit.text())
            
    if self.ui.QELine_SelectUnits_RLU_radioButton.isChecked():
        rlu=True
        Q1 = np.array([HStart,KStart,LStart])
        Q2 = np.array([HEnd,KEnd,LEnd])
    else:
        rlu=False   
        Q1 = np.array([HStart,KStart])
        Q2 = np.array([HEnd,KEnd])
   
    # Collect them into one array
    QPoints = np.array([Q1,Q2])
    
    # Define orthogonal width and minimum pixel size along Q-cut
    width = float(self.ui.QELine_Width_lineEdit.text())   
    minPixel = float(self.ui.QELine_MinPixel_lineEdit.text()) 

    # Define energy bins
    EMin=float(self.ui.QELine_EMin_lineEdit.text())
    EMax=float(self.ui.QELine_EMax_lineEdit.text())
    NPoints=int(self.ui.QELine_NPoints_lineEdit.text())        
    EnergyBins=np.linspace(EMin,EMax,NPoints)

    # Check various plot settings

    if self.ui.QELine_LogScale_checkBox.isChecked():
        log=True
    else:
        log=False  
        
    if self.ui.QELine_ConstantBins_checkBox.isChecked():
        constantBins=True
    else:
        constantBins=False              


    try:
        # Make plot
        ax,DataLists,Bins,BinCenters,Offsets = \
        ds.plotCutQELine(QPoints=QPoints, width=width, \
                                        minPixel=minPixel, EnergyBins=EnergyBins,\
                                            rlu=rlu,log=log,constantBins=constantBins)
    
        # Make some final changes to the plot
        self.QELine=ax    
        fig = self.QELine.get_figure()
        fig.set_size_inches(8,6)
    
        if self.ui.QELine_Grid_checkBox.isChecked():
            ax.grid(True)
        else:
            ax.grid(False)
        
        self.QELine_setCAxis_button_function()
    
        self.windows.append(self.QELine.get_figure())
        self.QELine_SetTitle_button_function()
    
        return True
    except:
        _GUItools.dialog(text='QELine cut could not be made. Check the limits for the cut and try again!')
        return False

def QELine_toggle_units_function(self):
    if self.ui.QELine_SelectUnits_RLU_radioButton.isChecked(): # changed to RLU
        # Change titles
        self.ui.QELine_HLabel.setText('H')
        self.ui.QELine_KLabel.setText('K')
        self.ui.QELine_LLabel.setText('L')
        self.ui.QELine_LStart_lineEdit.setEnabled(True)
        self.ui.QELine_LEnd_lineEdit.setEnabled(True)
    else: # Changing to AA
        self.ui.QELine_HLabel.setText('Qx')
        self.ui.QELine_KLabel.setText('Qy')
        self.ui.QELine_LLabel.setText('N/A')
        self.ui.QELine_LStart_lineEdit.setEnabled(False)
        self.ui.QELine_LEnd_lineEdit.setEnabled(False)

def QELine_setCAxis_button_function(self):       
    CAxisMin=float(self.ui.QELine_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.QELine_CAxisMax_lineEdit.text())
    
    self.QELine.set_clim(CAxisMin,CAxisMax)
    fig = self.QELine.get_figure()
    fig.canvas.draw()

def QELine_SetTitle_button_function(self):
    if hasattr(self, 'QELine'):
        TitleText=self.ui.QELine_SetTitle_lineEdit.text()        
        self.QELine.set_title(TitleText)
        fig = self.QELine.get_figure()
        fig.canvas.draw()

try:
    QELineManagerBase, QELineManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"QELine.ui"))
except:
    try:
        QELineManagerBase, QELineManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"QELine.ui"))
    except:
        QELineManagerBase, QELineManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"QELine.ui"))
class QELineManager(QELineManagerBase, QELineManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(QELineManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initQELineManager()

    def initQELineManager(self):
        self.guiWindow.QELine_plot_button_function = lambda: QELine_plot_button_function(self.guiWindow)
        self.guiWindow.QELine_setCAxis_button_function = lambda: QELine_setCAxis_button_function(self.guiWindow)
        self.guiWindow.QELine_SetTitle_button_function = lambda: QELine_SetTitle_button_function(self.guiWindow)
        self.guiWindow.QELine_toggle_units_function = lambda: QELine_toggle_units_function(self.guiWindow)

        for key,value in self.__dict__.items():
            if 'QELine' in key:
                self.guiWindow.ui.__dict__[key] = value

    def setup(self):
        
        self.guiWindow.ui.QELine_plot_button.clicked.connect(self.guiWindow.QELine_plot_button_function)
        self.guiWindow.ui.QELine_setCAxis_button.clicked.connect(self.guiWindow.QELine_setCAxis_button_function)
        self.guiWindow.ui.QELine_SetTitle_button.clicked.connect(self.guiWindow.QELine_SetTitle_button_function)
        self.guiWindow.ui.QELine_SelectUnits_RLU_radioButton.toggled.connect(self.guiWindow.QELine_toggle_units_function)
