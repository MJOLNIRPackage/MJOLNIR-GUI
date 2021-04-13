import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
    import MJOLNIRGui.src.main.python._tools as _GUItools
except ImportError:
    from _tools import ProgressBarDecoratorArguments
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import numpy as np
from MJOLNIR.TasUBlibDEG import calTwoTheta,calculateBMatrix,calcCell
from MJOLNIR.Geometry.Instrument import prediction
import pyperclip

# Handles all functionality related to the PredictionToolManager. 

try:
    PredictionToolManagerBase, PredictionToolManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Prediction.ui"))
except:
    try:
        PredictionToolManagerBase, PredictionToolManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Prediction.ui"))
    except:
        PredictionToolManagerBase, PredictionToolManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Prediction.ui"))
# All of this connects the buttons and their functions to the main window.
       


def FocusOut(self,event,manager):
    """Custom function to overwrite default FocusOut event"""
    R = [manager.getAlignment(x) for x in [1,2]]
    if not np.all([manager.validateR(r) for r in R]): # If not valid
       manager.notValidated()
    else:
        manager.validated()
    self.focusOutEvent_old(event)


def textChangedA4Calc(alignment,manager):
    if not isinstance(alignment,list):
        alignment = [alignment]
    for a in alignment:
        A4 = manager.calculateA4(alignment=a)
        if not A4 is None:
            getattr(manager,'alignment{}_a4_spinBox'.format(a)).setValue(A4)
    



class PredictionToolManager(PredictionToolManagerBase, PredictionToolManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(PredictionToolManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow

        self.a4Validator = QtGui.QRegExpValidator()
       
        regExp = QtCore.QRegExp(r'(-?[0-9]*\.[0-9]+|-?[0-9]+)(,(-?[0-9]*\.[0-9]+|-?[0-9]+))*')
        self.a4Validator.setRegExp(regExp)


        self.initPredictionToolManager()
        
    def initPredictionToolManager(self):    

        self.setup()
        

    def setup(self):
        # Update all boxes with check on out focus

        self.cell_a_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_b_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_c_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_alpha_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_beta_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_gamma_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))

        self.alignment1_ei_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_ef_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_h_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_k_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_l_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))

        self.alignment2_ei_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_ef_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_h_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_k_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_l_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))

        
        self.scan_a4_lineEdit.setValidator(self.a4Validator)

        self.tool_generate_button.clicked.connect(self.generatePrediction)

    def getAlignment(self,alignment=1):
        """Get values for alignment vector 1"""
        Ei = getattr(self,'alignment{}_ei_spinBox'.format(alignment)).value()
        Ef = getattr(self,'alignment{}_ef_spinBox'.format(alignment)).value()

        H = getattr(self,'alignment{}_h_spinBox'.format(alignment)).value()
        K = getattr(self,'alignment{}_k_spinBox'.format(alignment)).value()
        L = getattr(self,'alignment{}_l_spinBox'.format(alignment)).value()
        A3 = getattr(self,'alignment{}_a3_spinBox'.format(alignment)).value()
        A4 = getattr(self,'alignment{}_a4_spinBox'.format(alignment)).value()

        return [H,K,L,A3,A4,0.0,0.0,Ei,Ef] # H,K,L,A3,A4,phi,chi,Ei,Ef
        

    def calculateA4(self,alignment=1):
        cell = self.getCell()
        r = self.getAlignment(alignment=alignment)

        Cell = calcCell(cell)
        B = calculateBMatrix(Cell)

        # H,K,L,Ei,Ef
        qe = np.concatenate([r[:3],r[-2:]])

        A4 = calTwoTheta(B=B,qe=qe,ss=-1)
        return A4



    def validated(self):
        self.tool_generate_button.setDisabled(False)
        self.tool_generate_button.setStyleSheet("color: black;")

    def notValidated(self):
        self.tool_generate_button.setDisabled(True)
        self.tool_generate_button.setStyleSheet("color: red;")

    def validateR(self,r):
        """Validate if r vector is valid. If HKL is nonzero, A4 is nonzero and Energies are nonzero."""

        H,K,L,_,A4,_,_,Ei,Ef = r
        if np.isclose(np.linalg.norm([H,K,L]),0.0):
            return False
        if np.isclose(A4,0.0):
            return False
        if np.any([np.isclose(E,0.0) for E in [Ei,Ef]]):
            return False
        
        return True
    
        
    def generatePrediction(self):
        """Generate prediction window from MJOLNIR"""
        A3Start,A3Stop,A3Steps,Ei,A4,points = self.getScan()
        r1 = np.array(self.getAlignment(alignment=1))
        r2 = np.array(self.getAlignment(alignment=2))

        cell = np.array(self.getCell())

        ax = prediction(A3Start=A3Start,A3Stop=A3Stop,A3Steps=A3Steps,A4Positions=A4,Ei=Ei,Cell=cell,r1=r1,r2=r2,points=points)

        self.guiWindow.windows.append(ax[0].get_figure())
        

    def getScan(self):
        A3Start = self.scan_a3Start_spinBox.value()
        A3Stop = self.scan_a3Stop_spinBox.value()
        A3Steps = self.scan_a3Steps_spinBox.value()
        Ei = self.scan_ei_spinBox.value()

        A4 = self.formatA4String(self.scan_a4_lineEdit.text())

        points = self.scan_plot_checkBox.isChecked()

        return A3Start,A3Stop,A3Steps,Ei,A4,points

    
    def formatA4String(self,A4String):
        if ',' in A4String:
            A4 = [float(x) for x in A4String.split(',')]
        else:
            A4 = [float(A4String)]

        return A4

    def getCell(self):
        a = self.cell_a_spinBox.value()
        b = self.cell_b_spinBox.value()
        c = self.cell_c_spinBox.value()
        alpha = self.cell_alpha_spinBox.value()
        beta = self.cell_beta_spinBox.value()
        gamma = self.cell_gamma_spinBox.value()

        return a,b,c,alpha,beta,gamma