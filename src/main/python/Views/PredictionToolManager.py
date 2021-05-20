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

        self.loadSettings()
        self.setup()
        self.generateScanCommands()
        

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

        self.scan_a3Start_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_a3Stop_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_a3Steps_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_ei_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_a4_lineEdit.textChanged.connect(self.generateScanCommands)

        self.tool_generate_button.clicked.connect(self.generatePrediction)

        for key,value in self.__dict__.items():
            if hasattr(value,'valueCanged'):
                value.valueChanged.connect(self.updateSettings)
            elif hasattr(value,'textChanged'):
                value.textChanged.connect(self.updateSettings)
        

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

    def setAlignment(self,R,alignment=1):
        [H,K,L,A3,A4,_,_,Ei,Ef] = R
        getattr(self,'alignment{}_ei_spinBox'.format(alignment)).setValue(Ei)
        getattr(self,'alignment{}_ef_spinBox'.format(alignment)).setValue(Ef)

        getattr(self,'alignment{}_h_spinBox'.format(alignment)).setValue(H)
        getattr(self,'alignment{}_k_spinBox'.format(alignment)).setValue(K)
        getattr(self,'alignment{}_l_spinBox'.format(alignment)).setValue(L)
        getattr(self,'alignment{}_a3_spinBox'.format(alignment)).setValue(A3)
        getattr(self,'alignment{}_a4_spinBox'.format(alignment)).setValue(A4)

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

    def setScan(self,scan):
        A3Start,A3Stop,A3Steps,Ei,A4,points = scan
        self.scan_a3Start_spinBox.setValue(A3Start)
        self.scan_a3Stop_spinBox.setValue(A3Stop)
        self.scan_a3Steps_spinBox.setValue(A3Steps)
        self.scan_ei_spinBox.setValue(Ei)

        strA4 = ','.join([str(a4) for a4 in A4])
        self.scan_a4_lineEdit.setText(strA4)
        
        points = self.scan_plot_checkBox.setChecked(points)

    
    def formatA4String(self,A4String):
        if ',' in A4String:
            A4 = []
            for x in A4String.split(','):
                try:
                    A4.append(float(x))
                except ValueError:
                    pass
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


    def setCell(self,cell):
        a,b,c,alpha,beta,gamma = cell

        self.cell_a_spinBox.setValue(a)
        self.cell_b_spinBox.setValue(b)
        self.cell_c_spinBox.setValue(c)
        self.cell_alpha_spinBox.setValue(alpha)
        self.cell_beta_spinBox.setValue(beta)
        self.cell_gamma_spinBox.setValue(gamma)

    def updateSettings(self):
        """Update self.guiWindow.predictionSettings with current settings"""
        R1 = self.getAlignment(alignment = 1)
        R2 = self.getAlignment(alignment = 2)
        cell = self.getCell()
        scan = self.getScan()

        names = ['R1','R2','cell','scan']
        values = [R1,R2,cell,scan]
        for name,value in zip(names,values):
            self.guiWindow.predictionSettings[name] = value

    def loadSettings(self):
        # Set up saving of settings in guiWindow

        if hasattr(self.guiWindow,'predictionSettings'): 
            R1 = self.guiWindow.predictionSettings['R1']
            R2 = self.guiWindow.predictionSettings['R2']
            cell = self.guiWindow.predictionSettings['cell']
            scan = self.guiWindow.predictionSettings['scan']
            self.setAlignment(R1,alignment = 1)
            self.setAlignment(R2,alignment = 2)
            self.setCell(cell)
            self.setScan(scan)

        else:# Create an empty dict
            self.guiWindow.predictionSettings = {}

    def generateScanCommands(self):
        
        A3Start,A3Stop,A3Steps,Ei,A4,points = self.getScan()
        if A3Steps == 1:
            A3StepSize = 0
        else:
            A3StepSize = (A3Stop-A3Start)/(A3Steps-1.0)
        A3middle = 0.5*(A3Start+A3Stop)

        scanCommand = 'sc a3 {:.2f} da3 {:.2f} np {:d} mn 100000'.format(A3middle,A3StepSize,A3Steps)

        commandString = []
        commandString.append('dr 2t {:.2f}'.format(A4[0]))
        commandString.append('dr ei {:.2f}'.format(Ei))
        commandString.append('')
        for a4 in A4:
            commandString.append('dr 2t {:.2f}'.format(a4))
            commandString.append(scanCommand)
            commandString.append('')

        commandString.append('')
        cmdStr = '\n'.join(commandString)
        self.scanCommand_textEdit.setText(cmdStr)

    def closeEvent(self, event):
        self.updateSettings()