import sys
sys.path.append('..')

try:
    from MJOLNIRGui._tools import ProgressBarDecoratorArguments
    import MJOLNIRGui._tools as _GUItools
except ModuleNotFoundError:
    from _tools import ProgressBarDecoratorArguments
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets, uic
import numpy as np


@ProgressBarDecoratorArguments(runningText='Plotting Cut1D',completedText='Plotting Done')
def Cut1D_plot_button_funcion(self):
    if not self.stateMachine.requireStateByName('Converted'):
        return False

    HStart = self.ui.Cut1D_HStart_lineEdit.text()
    HEnd = self.ui.Cut1D_HEnd_lineEdit.text()
    KStart = self.ui.Cut1D_KStart_lineEdit.text()
    KEnd = self.ui.Cut1D_KEnd_lineEdit.text()
    LStart = self.ui.Cut1D_LStart_lineEdit.text()
    LEnd = self.ui.Cut1D_LEnd_lineEdit.text()

    EMax = float(self.ui.Cut1D_EMax_lineEdit.text())
    EMin = float(self.ui.Cut1D_EMin_lineEdit.text())

    width = float(self.ui.Cut1D_Width_lineEdit.text())
    minPixel = float(self.ui.Cut1D_MinPixel_lineEdit.text())

    ds = self.DataSetModel.getCurrentDataSet()

    q1 = np.array([HStart,KStart,LStart],dtype=float)
    q2 = np.array([HEnd,KEnd,LEnd],dtype=float)

    
    try:
        ax,*_ = ds.plotCut1D(q1=q1,q2=q2,width=width,minPixel=minPixel,Emin=EMin,Emax=EMax,rlu=True,constantBins=False)
        self.windows.append(ax.get_figure())
        self.Cut1D=ax
        return True
    except:
        _GUItools.dialog(text='1D Cut could not be made. Check the limits for the cut and try again!')
        return False

def Cut1D_SetTitle_button_function(self):
    TitleText=self.ui.Cut1D_SetTitle_lineEdit.text()        
    if hasattr(self, 'Cut1D'):
        TitleText=self.ui.Cut1D_SetTitle_lineEdit.text()        
        self.Cut1D.set_title(TitleText)
        fig = self.Cut1D.get_figure()
        fig.canvas.draw()

try:
    Cut1DManagerBase, Cut1DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Cut1D.ui"))
except:
    Cut1DManagerBase, Cut1DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Cut1D.ui"))
class Cut1DManager(Cut1DManagerBase, Cut1DManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(Cut1DManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initCut1DManager()

    def initCut1DManager(self):
        self.guiWindow.Cut1D_plot_button_funcion = lambda: Cut1D_plot_button_funcion(self.guiWindow)
        self.guiWindow.Cut1D_SetTitle_button_function = lambda: Cut1D_SetTitle_button_function(self.guiWindow)

        for key,value in self.__dict__.items():
                if 'Cut1D' in key:
                    self.guiWindow.ui.__dict__[key] = value
        
    def setup(self):
        self.guiWindow.ui.Cut1D_plot_button.clicked.connect(self.guiWindow.Cut1D_plot_button_funcion)
        self.guiWindow.ui.Cut1D_SetTitle_button.clicked.connect(self.guiWindow.Cut1D_SetTitle_button_function)
    
    