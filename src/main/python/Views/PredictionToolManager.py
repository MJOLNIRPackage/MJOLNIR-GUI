import sys,os

from MJOLNIR import TasUBlibDEG
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments,loadUI
    import MJOLNIRGui.src.main.python._tools as _GUItools
except ImportError:
    from _tools import ProgressBarDecoratorArguments,loadUI
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import numpy as np
from MJOLNIR.TasUBlibDEG import calTwoTheta,calculateBMatrix,calcCell
from MJOLNIR.Geometry.Instrument import prediction,converterToA3A4,converterToQxQy,predictionInstrumentSupport
from MJOLNIR.Data import Sample
import MJOLNIR 
import pyperclip

# Handles all functionality related to the PredictionToolManager. 


PredictionToolManagerBase, PredictionToolManagerForm = loadUI('Prediction.ui')

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

    manager.updateSample()
    
def onFocus(self,event,others):
    for o in others:
        try:
            o.valueChanged.disconnect()
        except TypeError: # If no connection to remove
            try:
                o.currentIndexChanged.disconnect()
            except (TypeError,AttributeError):
                pass
    if hasattr(self,'onChangeFunction'):
        try:
            self.valueChanged.connect(self.onChangeFunction)
        except AttributeError:
            self.currentIndexChanged.connect(self.onChangeFunction)
    #   self.old_focusInEvent(event)


class PredictionToolManager(PredictionToolManagerBase, PredictionToolManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(PredictionToolManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.setWindowIcon(QtGui.QIcon(self.guiWindow.AppContext.get_resource('Icons/Own/predict.png')))

        self.a4Validator = QtGui.QRegExpValidator()
        self.predictionAX = None
        if not hasattr(self.guiWindow,'braggPoints'):
            self.guiWindow.braggPoints = None
       
        regExp = QtCore.QRegExp(r'(-?[0-9]*\.[0-9]+|-?[0-9]+)(,(-?[0-9]*\.[0-9]+|-?[0-9]+))*')
        self.a4Validator.setRegExp(regExp)


        self.initPredictionToolManager()
        
    def initPredictionToolManager(self):    
        self.loadEnergies()
        self.loadSettings()
        self.setup()
        self.generateScanCommands()
        self.updateSample()


    def setup(self):

        ## Add supported instruments to combobox
        self.instrument_comboBox.addItems(predictionInstrumentSupport)

        
        # Update all boxes with check on out focus

        self.cell_a_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_b_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_c_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_alpha_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_beta_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))
        self.cell_gamma_spinBox.valueChanged.connect(lambda: textChangedA4Calc([1,2],self))

        self.alignment1_ei_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_ef_comboBox.currentIndexChanged.connect(lambda Index: textChangedA4Calc(1,self))
        self.alignment1_h_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_k_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_l_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        self.alignment1_a3_spinBox.valueChanged.connect(lambda: textChangedA4Calc(1,self))
        
        self.alignment2_ei_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_ef_comboBox.currentIndexChanged.connect(lambda Index: textChangedA4Calc(2,self))
        self.alignment2_h_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_k_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_l_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))
        self.alignment2_a3_spinBox.valueChanged.connect(lambda: textChangedA4Calc(2,self))

        
        self.scan_a4_lineEdit.setValidator(self.a4Validator)

        self.scan_a3Start_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_a3Stop_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_a3Steps_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_ei_spinBox.valueChanged.connect(self.generateScanCommands)
        self.scan_a4_lineEdit.textChanged.connect(self.generateScanCommands)
        self.scan_monitor_spinBox.valueChanged.connect(self.generateScanCommands)

        self.scan_curratAxe_pushButton.clicked.connect(self.curratAxeList)

        self.tool_generate_button.clicked.connect(self.generatePrediction)

        self.HKL_ei_spinBox.onChangeFunction = self.calcualteHKLtoA3A4
        self.HKL_ef_comboBox.onChangeFunction = lambda I: self.calcualteHKLtoA3A4()

        self.HKL_H_doubleSpinBox.onChangeFunction = self.calcualteHKLtoA3A4
        self.HKL_K_doubleSpinBox.onChangeFunction = self.calcualteHKLtoA3A4
        self.HKL_L_doubleSpinBox.onChangeFunction = self.calcualteHKLtoA3A4

        self.HKL_A3_doubleSpinBox.onChangeFunction = self.calcualteA3A4toHKL
        self.HKL_A4_doubleSpinBox.onChangeFunction = self.calcualteA3A4toHKL


        self.HKL_A3_doubleSpinBox.old_focusInEvent = self.HKL_A3_doubleSpinBox.focusInEvent
        self.HKL_A4_doubleSpinBox.old_focusInEvent = self.HKL_A4_doubleSpinBox.focusInEvent
        self.HKL_H_doubleSpinBox.old_focusInEvent = self.HKL_H_doubleSpinBox.focusInEvent
        self.HKL_K_doubleSpinBox.old_focusInEvent = self.HKL_K_doubleSpinBox.focusInEvent
        self.HKL_L_doubleSpinBox.old_focusInEvent = self.HKL_L_doubleSpinBox.focusInEvent
        self.HKL_ei_spinBox.old_focusInEvent = self.HKL_ei_spinBox.focusInEvent
        self.HKL_ef_comboBox.old_focusInEvent = self.HKL_ef_comboBox.focusInEvent
        
        
        # Update focusing for A3 and A4
        others = [self.HKL_H_doubleSpinBox,self.HKL_K_doubleSpinBox,self.HKL_L_doubleSpinBox]
        self.HKL_A3_doubleSpinBox.focusInEvent= lambda event: onFocus(self.HKL_A3_doubleSpinBox,event,others)
        self.HKL_A4_doubleSpinBox.focusInEvent= lambda event: onFocus(self.HKL_A4_doubleSpinBox,event,others)

        # Update focusing for H,K,L,Ei,Ef
        others = [self.HKL_A3_doubleSpinBox,self.HKL_A4_doubleSpinBox]
        self.HKL_H_doubleSpinBox.focusInEvent= lambda event: onFocus(self.HKL_H_doubleSpinBox,event,others)
        self.HKL_K_doubleSpinBox.focusInEvent= lambda event: onFocus(self.HKL_K_doubleSpinBox,event,others)
        self.HKL_L_doubleSpinBox.focusInEvent= lambda event: onFocus(self.HKL_L_doubleSpinBox,event,others)

        self.HKL_ei_spinBox.focusInEvent= lambda event: onFocus(self.HKL_ei_spinBox,event,others)
        self.HKL_ef_comboBox.focusInEvent= lambda event: onFocus(self.HKL_ef_comboBox,event,others)    

        
        for key,value in self.__dict__.items():
            if hasattr(value,'valueCanged'):
                value.valueChanged.connect(self.updateSettings)
            elif hasattr(value,'textChanged'):
                value.textChanged.connect(self.updateSettings)
        
    def updateSample(self):
        cell = np.array(self.getCell())
        r1 = np.array(self.getAlignment(1))
        r2 = np.array(self.getAlignment(2))
        self.sample = Sample.Sample(*cell,projectionVector1=r1,projectionVector2=r2)
        self.calcualteHKLtoA3A4()

    def getAlignment(self,alignment=1):
        """Get values for alignment vector 1"""
        Ei = getattr(self,'alignment{}_ei_spinBox'.format(alignment)).value()
        EfIndex = getattr(self,'alignment{}_ef_comboBox'.format(alignment)).currentIndex()
        if EfIndex == len(self.Efs): # Equal to last entry => Ei=Ef
            Ef = Ei
        else:
            Ef = self.Efs[EfIndex]

        H = getattr(self,'alignment{}_h_spinBox'.format(alignment)).value()
        K = getattr(self,'alignment{}_k_spinBox'.format(alignment)).value()
        L = getattr(self,'alignment{}_l_spinBox'.format(alignment)).value()
        A3 = getattr(self,'alignment{}_a3_spinBox'.format(alignment)).value()
        A4 = getattr(self,'alignment{}_a4_spinBox'.format(alignment)).value()

        return [H,K,L,A3,A4,0.0,0.0,Ei,Ef] # H,K,L,A3,A4,phi,chi,Ei,Ef

    def setAlignment(self,R,alignment=1):
        [H,K,L,A3,A4,_,_,Ei,Ef] = R
        getattr(self,'alignment{}_ei_spinBox'.format(alignment)).setValue(Ei)
        EfIndex = np.argmin(np.abs(Ef-self.Efs))
        getattr(self,'alignment{}_ef_comboBox'.format(alignment)).setCurrentIndex(EfIndex)

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

    def loadEnergies(self,instrument='CAMEA'):
        if instrument == 'CAMEA':
            calibPath = MJOLNIR.__CAMEANormalizationBinning1__

            calib = np.loadtxt(calibPath,delimiter=',',skiprows=3)

            self.A4Instrument = calib[:,-1].reshape(104,8)
            self.EfInstrument = calib[:,4].reshape(104,8)
            self.EfInstrument[np.isclose(self.EfInstrument,0.0)]=np.nan
        else:
            raise NotImplementedError('Currently only CAMEA is created... sorry')

        self.Efs = np.nanmean(self.EfInstrument,axis=0)[::-1]
        for key,value in self.__dict__.items():
            if 'ef_comboBox' in key:
                for i,ef in enumerate(self.Efs):
                    value.addItem('{:.2f} ({:d})'.format(ef,len(self.Efs)-i-1))

                value.addItem(' = Ei')
        


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
        A3Start,A3Stop,A3Steps,Ei,A4,points,Monitor = self.getScan()
        r1 = np.array(self.getAlignment(alignment=1))
        r2 = np.array(self.getAlignment(alignment=2))

        cell = np.array(self.getCell())

        instrument = str(self.instrument_comboBox.currentText())

        ax = prediction(A3Start=A3Start,A3Stop=A3Stop,A3Steps=A3Steps,A4Positions=A4,Ei=Ei,Cell=cell,r1=r1,r2=r2,
        points=points,outputFunction=self.guiWindow.writeToStatus, instrument=instrument)

        self.predictionAx = ax
        self.guiWindow.windows.append(ax[0].get_figure())

        # make all figures have the same xlim and ylim by using the last axis

        for a in ax[:-1]:
            a.set_ylim(*ax[-1].get_ylim())
            a.set_xlim(*ax[-1].get_xlim())

        curratAxe = self.scan_curratAxe_checkBox.isChecked()

        if curratAxe:
            self.plotCurratAxe()
        
    def plotCurratAxe(self):
        if hasattr(self.guiWindow,'BraggListWindow'):
            BraggPoint = np.array(self.guiWindow.BraggListWindow.BraggListModel.getAllData())
        elif hasattr(self.guiWindow,'braggPoints'):
            BraggPoint = self.guiWindow.braggPoints
        else:
            return

        if not hasattr(self,'predictionAx'):
            return
        
        Ef = self.Efs[::-1]
        Ei = self.getScan()[3]
        SpurionPositionsMono = self.predictionAx[0].sample.CurratAxe(Ei=Ei,Ef=Ef,Bragg=BraggPoint,HKL=False,spurionType = 'Monochromator').reshape(len(BraggPoint),-1,3).transpose(1,0,2)
        SpurionPositionsAna  = self.predictionAx[0].sample.CurratAxe(Ei=Ei,Ef=Ef,Bragg=BraggPoint,HKL=False,spurionType = 'Analyser').reshape(len(BraggPoint),-1,3).transpose(1,0,2)
        
        
        self.monoPoints = []
        self.anaPoints = []
        for ax,posMono,posAna in zip(self.predictionAx,SpurionPositionsMono,SpurionPositionsAna):
            for bragg in posMono:
                self.monoPoints.append( ax.scatter(*bragg[:2],marker='o',color='r'))
            for bragg in posAna:
                self.anaPoints.append(ax.scatter(*bragg[:2],marker='o',color='k'))

    def removeCurratAxe(self):
        if hasattr(self,'predictionAx'):
            if hasattr(self,'monoPoints'):
                for p in np.concatenate(self.monoPoints,self.anaPoints):
                    p.setVisible(False)



    def getScan(self):
        A3Start = self.scan_a3Start_spinBox.value()
        A3Stop = self.scan_a3Stop_spinBox.value()
        A3Steps = self.scan_a3Steps_spinBox.value()
        Ei = self.scan_ei_spinBox.value()

        A4 = self.formatA4String(self.scan_a4_lineEdit.text())

        points = self.scan_plot_checkBox.isChecked()

        Monitor = self.scan_monitor_spinBox.value()

        return A3Start,A3Stop,A3Steps,Ei,A4,points,Monitor

    def setScan(self,scan):
        A3Start,A3Stop,A3Steps,Ei,A4,points,Monitor = scan
        self.scan_a3Start_spinBox.setValue(A3Start)
        self.scan_a3Stop_spinBox.setValue(A3Stop)
        self.scan_a3Steps_spinBox.setValue(A3Steps)
        self.scan_ei_spinBox.setValue(Ei)
        self.scan_monitor_spinBox.setValue(Monitor)

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
        calc = self.getCalculation()

        names = ['R1','R2','cell','scan','calc']
        values = [R1,R2,cell,scan,calc]
        for name,value in zip(names,values):
            self.guiWindow.predictionSettings[name] = value

    def loadSettings(self):
        # Set up saving of settings in guiWindow

        if hasattr(self.guiWindow,'predictionSettings'): 
            if self.guiWindow.predictionSettings: # If not empty
                R1 = self.guiWindow.predictionSettings['R1']
                R2 = self.guiWindow.predictionSettings['R2']
                cell = self.guiWindow.predictionSettings['cell']
                scan = self.guiWindow.predictionSettings['scan']
                calc = self.guiWindow.predictionSettings['calc']
                self.setAlignment(R1,alignment = 1)
                self.setAlignment(R2,alignment = 2)
                self.setCell(cell)
                self.setScan(scan)
                self.setCalculation(calc)
            else:# Create an empty dict
                self.guiWindow.predictionSettings = {}

        else:# Create an empty dict
            self.guiWindow.predictionSettings = {}

    def generateScanCommands(self):
        
        A3Start,A3Stop,A3Steps,Ei,A4,points,Monitor = self.getScan()
        if A3Steps == 1:
            A3StepSize = 0
        else:
            A3StepSize = (A3Stop-A3Start)/(A3Steps-1.0)
        A3middle = 0.5*(A3Start+A3Stop)

        #scanCommand = 'sc a3 {:.2f} da3 {:.2f} np {:d} mn {:}'.format(A3middle,A3StepSize,A3Steps,Monitor)
        scanCommand = 'scan(a3, {:.2f}, {:.2f},{:d},m={:})'.format(A3Start,A3StepSize,A3Steps,Monitor)

        commandString = []
        #commandString.append('dr 2t {:.2f}'.format(A4[0]))
        commandString.append('maw(s2t,{:.2f})'.format(A4[0]))
        #commandString.append('dr ei {:.2f}'.format(Ei))
        commandString.append('maw(ei,{:.2f})'.format(Ei))
        commandString.append('')
        for a4 in A4:
            #commandString.append('dr 2t {:.2f}'.format(a4))
            commandString.append('maw(s2t,{:.2f})'.format(a4))
            commandString.append(scanCommand)
            commandString.append('')

        commandString.append('')
        cmdStr = '\n'.join(commandString)
        self.scanCommand_textEdit.setText(cmdStr)

    def getCalculation(self):
        Ei = self.HKL_ei_spinBox.value()
        EfIndex = self.HKL_ef_comboBox.currentIndex()
        if EfIndex == len(self.Efs): # Equal to last entry => Ei=Ef
            Ef = Ei
        else:
            Ef = self.Efs[EfIndex]
        H = self.HKL_H_doubleSpinBox.value()
        K = self.HKL_K_doubleSpinBox.value()
        L = self.HKL_L_doubleSpinBox.value()
        A3 = self.HKL_A3_doubleSpinBox.value()
        A4 = self.HKL_A4_doubleSpinBox.value()

        return Ei,Ef,H,K,L,A3,A4,EfIndex

    def setCalculation(self,calc):
        Ei,Ef,H,K,L,A3,A4,EfIndex = calc

        self.HKL_ef_comboBox.setCurrentIndex(EfIndex)
        self.HKL_ei_spinBox.setValue(Ei)
        self.HKL_H_doubleSpinBox.setValue(H)
        self.HKL_K_doubleSpinBox.setValue(K)
        self.HKL_L_doubleSpinBox.setValue(L)
        self.HKL_A3_doubleSpinBox.setValue(A3)
        self.HKL_A4_doubleSpinBox.setValue(A4)

    def calcualteHKLtoA3A4(self):
        Ei,Ef,H,K,L,*_ = self.getCalculation()
        
        UB = self.sample.UB

        Qx,Qy,_ = np.dot(UB,[H,K,L])
        A3,A4 = converterToA3A4(Qx,Qy,Ei,Ef,A3Off=0.0,A4Sign=np.sign(self.sample.plane_vector1[4]))
        
        self.HKL_A3_doubleSpinBox.setValue(A3)
        self.HKL_A4_doubleSpinBox.setValue(A4)
        
    def calcualteA3A4toHKL(self):
        Ei,Ef,_,_,_,A3,A4,_ = self.getCalculation()
        Qx,Qy = converterToQxQy(A3,A4,Ei,Ef)
        H,K,L = self.sample.calculateQxQyToHKL(Qx,Qy)
        self.HKL_H_doubleSpinBox.setValue(H)
        self.HKL_K_doubleSpinBox.setValue(K)
        self.HKL_L_doubleSpinBox.setValue(L)

    def curratAxeList(self):
        self.guiWindow.openBraggListWindow()


    def closeEvent(self, event):
        self.updateSettings()