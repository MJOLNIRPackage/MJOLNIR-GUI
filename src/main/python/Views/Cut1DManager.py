import sys
sys.path.append('..')

from _tools import ProgressBarDecoratorArguments

from os import path
from PyQt5 import QtWidgets
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

    
    ax,*_ = ds.plotCut1D(q1=q1,q2=q2,width=width,minPixel=minPixel,Emin=EMin,Emax=EMax,rlu=True,constantBins=False)
    self.windows.append(ax.get_figure())
    return True


def initCut1DManager(guiWindow):
    guiWindow.Cut1D_plot_button_funcion = lambda: Cut1D_plot_button_funcion(guiWindow)
    
def setupCut1DManager(guiWindow):
    guiWindow.ui.Cut1D_plot_button.clicked.connect(guiWindow.Cut1D_plot_button_funcion)
    