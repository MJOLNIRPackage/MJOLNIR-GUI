import sys
sys.path.append('..')

from os import path
import numpy as np

from PyQt5 import uic
from MJOLNIR._tools import WavelengthK
from MJOLNIR.TasUBlibDEG import calcCell,calculateBMatrix,calTwoTheta
# Handles all functionality related to the CalculatorAdvancedManager. 

try:
    CalculatorAdvancedManagerBase, CalculatorAdvancedManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Calculator_Advanced.ui"))
except:
    try:
        CalculatorAdvancedManagerBase, CalculatorAdvancedManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Calculator_Advanced.ui"))
    except:
        CalculatorAdvancedManagerBase, CalculatorAdvancedManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Calculator_Advanced.ui"))
# All of this connects the buttons and their functions to the main window.
       

def textChangedCalculate(manager):
    cell = manager.getCell()
    r = manager.getPoint()

    Cell = calcCell(cell)
    B = calculateBMatrix(Cell)

    # H,K,L,Ei,Ef
    qe = np.concatenate([r[:3],r[-2:]])

    A4 = calTwoTheta(B=B,qe=qe,ss=-1)

    qLength = np.linalg.norm(np.dot(B,np.array(r[:3])))
    d = WavelengthK(qLength)

    dE = r[-2]-r[-1]

    manager.scattering_q_label.setText('{:.4}'.format(qLength))
    manager.scattering_d_label.setText('{:.4}'.format(d))
    manager.scattering_a4_label.setText('{:.4}'.format(A4))

    manager.scattering_de_spinBox.setValue(dE)

def textChangeDeltaE(manager):
    Ef = manager.scattering_ef_spinBox.value()
    dE = manager.scattering_de_spinBox.value()

    manager.scattering_ei_spinBox.setValue(Ef+dE)




class CalculatorAdvancedManager(CalculatorAdvancedManagerBase, CalculatorAdvancedManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(CalculatorAdvancedManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow

        self.initCalculatorAdvancedManager()
        
    def initCalculatorAdvancedManager(self):    
        self.setup()
        

    def setup(self):
        # Update all boxes with check on out focus

        self.cell_a_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.cell_b_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.cell_c_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.cell_alpha_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.cell_beta_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.cell_gamma_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))

        self.scattering_ei_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.scattering_ef_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        
        self.scattering_h_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.scattering_k_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))
        self.scattering_l_spinBox.valueChanged.connect(lambda: textChangedCalculate(self))

        self.scattering_de_spinBox.valueChanged.connect(lambda: textChangeDeltaE(self))
        
    def getPoint(self):
        """Get values for scattering point"""
        Ei = getattr(self,'scattering_ei_spinBox').value()
        Ef = getattr(self,'scattering_ef_spinBox').value()

        H = getattr(self,'scattering_h_spinBox').value()
        K = getattr(self,'scattering_k_spinBox').value()
        L = getattr(self,'scattering_l_spinBox').value()

        return H,K,L,0.0,0.0,Ei,Ef



    def getCell(self):
        a = self.cell_a_spinBox.value()
        b = self.cell_b_spinBox.value()
        c = self.cell_c_spinBox.value()
        alpha = self.cell_alpha_spinBox.value()
        beta = self.cell_beta_spinBox.value()
        gamma = self.cell_gamma_spinBox.value()

        return a,b,c,alpha,beta,gamma