import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile,GuiDataSet
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
except ImportError:
    from MJOLNIR_Data import GuiDataFile,GuiDataSet
    from _tools import ProgressBarDecoratorArguments

from os import path
from PyQt5 import QtWidgets,uic
import numpy as np


def setupRaw1DCutSpinBoxes(self):
    self.ui.Raw1D_Analyzer_spinBox.valueChanged.connect(self.raw1DCutAnalyzerSpinBoxChanged)
    self.ui.Raw1D_Detector_spinBox.valueChanged.connect(self.raw1DCutDetectorSpinBoxChanged)
    self.resetRaw1DCutSpinBoxes()

        
def resetRaw1DCutSpinBoxes(self):
    self.ui.Raw1D_Analyzer_spinBox.setEnabled(False)
    self.ui.Raw1D_Detector_spinBox.setEnabled(False)
    self.ui.Raw1D_Analyzer_spinBox.setValue(0)
    self.ui.Raw1D_Detector_spinBox.setValue(0)

    self.ui.Raw1D_Analyzer_Original_label.setText('Original N/A')
    self.ui.Raw1D_Detector_Original_label.setText('Original N/A')

    EfEntry = '{:.2f}'.format(0).rjust(9,' ')
    A4Entry = '{:+.2f}'.format(0).rjust(9,' ')

    self.ui.Raw1D_Analyzer_label.setText('Analyzer number (Ef = {} meV)'.format(EfEntry))
    self.ui.Raw1D_Detector_label.setText('Detector number (A4 = {} deg)'.format(A4Entry))


def updateRaw1DCutSpinBoxes(self,dfs=None):
    if dfs is None:
        dfs = self.DataFileModel.getCurrentDatafiles()
        if dfs is None:
            return self.resetRaw1DCutSpinBoxes()
    if len(dfs)>1:
        return self.resetRaw1DCutSpinBoxes()
    
    df = dfs[0]
    

    self.ui.Raw1D_Analyzer_spinBox.setEnabled(True)
    self.ui.Raw1D_Detector_spinBox.setEnabled(True)
    self.ui.Raw1D_Analyzer_spinBox.setValue(df.analyzerSelection)
    self.ui.Raw1D_Detector_spinBox.setValue(df.detectorSelection)
    self.updateRaw1DCutLabels(dfs)
    

def updateRaw1DCutLabels(self,dfs=None):
    if dfs is None:
        dfs = self.DataFileModel.getCurrentDatafiles()
        if dfs is None:
            return self.resetRaw1DCutSpinBoxes()
    if len(dfs)>1:
        return self.resetRaw1DCutSpinBoxes()
    
    df = dfs[0]

    self.ui.Raw1D_Analyzer_Original_label.setText('Original {}'.format(df.analyzerSelectionOriginal))
    self.ui.Raw1D_Detector_Original_label.setText('Original {}'.format(df.detectorSelectionOriginal))
    
    if df.instrument == 'CAMEA':
        EPrDetector = 8 
        detectors = 104
    elif df.type == 'MultiFLEXX':
        EPrDetector = 1
        detectors = 31
    elif df.type == 'FlatCone':
        EPrDetector = 1
        detectors = 31

    binning = 1
    calibrationIndex = list(df.possibleBinnings).index(binning) # Only binning 1 is used for raw plotting
    instrumentCalibrationEf,instrumentCalibrationA4,_ = df.instrumentCalibrations[calibrationIndex]
    
    
    instrumentCalibrationEf.shape = (detectors,EPrDetector*binning,4)
    instrumentCalibrationA4.shape = (detectors,EPrDetector*binning)

    analyzerValue = self.ui.Raw1D_Analyzer_spinBox.value()
    detectorValue = self.ui.Raw1D_Detector_spinBox.value() #
    Ef = instrumentCalibrationEf[detectorValue,analyzerValue,1]
    A4 = instrumentCalibrationA4[detectorValue,analyzerValue]

    EfEntry = '{:.2f}'.format(Ef).rjust(9,' ')
    A4Entry = '{:+.2f}'.format(A4).rjust(9,' ')

    self.ui.Raw1D_Analyzer_label.setText('Analyzer number (Ef = {} meV)'.format(EfEntry))
    self.ui.Raw1D_Detector_label.setText('Detector number (A4 = {} deg)'.format(A4Entry))

    
def raw1DCutAnalyzerSpinBoxChanged(self):
    value = self.ui.Raw1D_Analyzer_spinBox.value()
    dfs = self.DataFileModel.getCurrentDatafiles()
    if dfs is None:
        return None
    if len(dfs)>1:
        return None
    
    df = dfs[0]
    df.analyzerSelection = np.array(value)
    self.updateRaw1DCutLabels(dfs=dfs)

def raw1DCutDetectorSpinBoxChanged(self):
    value = self.ui.Raw1D_Detector_spinBox.value()
    dfs = self.DataFileModel.getCurrentDatafiles()
    if dfs is None:
        return None
    if len(dfs)>1:
        return None
    
    df = dfs[0]
    df.detectorSelection = np.array(value)
    self.updateRaw1DCutLabels(dfs=dfs)
        
@ProgressBarDecoratorArguments(runningText='Plotting raw 1D Data',completedText='Plotting Done')
def Raw1D_plot_button_function(self):
    if not self.stateMachine.requireStateByName('Raw'):
        return False
    dataFiles = self.DataFileModel.getCurrentDatafiles()
    if dataFiles is None:
        ds = self.DataSetModel.getCurrentDataSet()
    elif len(dataFiles) == 0: # No data files selected, use them all
        ds = self.DataSetModel.getCurrentDataSet()
    else:
        ds = GuiDataSet(dataFiles)
    
    if ds is None:
        return False

    
    ax = ds.plotRaw1D()
    self.windows.append(ax.get_figure())
    return True


try:
    Raw1DManagerBase, Raw1DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Raw1D.ui"))
except:
    try:
        Raw1DManagerBase, Raw1DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Raw1D.ui"))
    except:
        Raw1DManagerBase, Raw1DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Raw1D.ui"))

class Raw1DManager(Raw1DManagerBase, Raw1DManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(Raw1DManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initRaw1DManager()


    def initRaw1DManager(self):

        self.guiWindow.setupRaw1DCutSpinBoxes = lambda: setupRaw1DCutSpinBoxes(self.guiWindow)
        self.guiWindow.resetRaw1DCutSpinBoxes = lambda: resetRaw1DCutSpinBoxes(self.guiWindow)
        self.guiWindow.updateRaw1DCutSpinBoxes = lambda dfs=None: updateRaw1DCutSpinBoxes(self.guiWindow, dfs)
        self.guiWindow.updateRaw1DCutLabels = lambda dfs=None: updateRaw1DCutLabels(self.guiWindow,dfs)
        self.guiWindow.raw1DCutAnalyzerSpinBoxChanged = lambda: raw1DCutAnalyzerSpinBoxChanged(self.guiWindow)
        
        self.guiWindow.raw1DCutDetectorSpinBoxChanged = lambda: raw1DCutDetectorSpinBoxChanged(self.guiWindow)
        self.guiWindow.Raw1D_plot_button_function = lambda: Raw1D_plot_button_function(self.guiWindow)

        for key,value in self.__dict__.items():
            if 'Raw1D' in key:
                self.guiWindow.ui.__dict__[key] = value

    def setup(self):
        
        self.guiWindow.ui.Raw1D_plot_button.clicked.connect(self.guiWindow.Raw1D_plot_button_function)
    