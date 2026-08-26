try:
    import IPython
    shell = IPython.get_ipython()
    shell.enable_matplotlib(gui='qt')
except:
    pass


from MJOLNIR import _tools # Useful tools useful across MJOLNIR
try:
    import _tools as _guitools
    from Views import BraggListManager
except ImportError:
    import MJOLNIRGui.src.main.python._tools as _guitools
    from MJOLNIRGui.src.main.python.Views import BraggListManager
import numpy as np
import matplotlib.pyplot as plt
import sys
import datetime
from time import sleep

from os import path
import os
version = '1.0.7'
plt.ion()
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
try:
    #from MJOLNIR_GUI_ui import Ui_MainWindow  
    
    from Views.main import Ui_MainWindow
    from Views.DataSetManager import DataSetManager
    from Views.View3DManager import View3DManager
    from Views.QELineManager import QELineManager
    from Views.QPlaneManager import QPlaneManager
    from Views.Cut1DManager import Cut1DManager
    from Views.MaskManager import MaskManager
    from Views.Raw1DManager import Raw1DManager
    from Views.NormalizationManager import NormalizationManager
    from Views.MolecularCalculationManager import MolecularCalculationManager
    from Views.PredictionToolManager import PredictionToolManager
    from Views.TimeEstimateManager import ScanListManager
    from Views.CalculatorManager import CalculatorManager
    from Views.SubtractionManager import SubtractionManager
    from Views.collapsibleBox import CollapsibleBox
    from Views.ElectronicLogBookManager import ElectronicLogBookManager
    from MJOLNIR_Data import GuiDataFile,GuiDataSet
    from DataModels import DataSetModel,DataFileModel
    from StateMachine import StateMachine
    from GuiStates import empty,partial,raw,converted
    from AboutDialog import AboutDialog
    from HelpDialog import HelpDialog
    from generateScripts import initGenerateScript,setupGenerateScript
    from _tools import loadSetting,updateSetting,ProgressBarDecoratorArguments
    
except ModuleNotFoundError:
    sys.path.append('.')
    
    #from .MJOLNIR_GUI_ui import Ui_MainWindow  
    from MJOLNIRGui.src.main.python.Views.main import Ui_MainWindow
    from MJOLNIRGui.src.main.python.Views.DataSetManager import DataSetManager
    from MJOLNIRGui.src.main.python.Views.View3DManager import View3DManager
    from MJOLNIRGui.src.main.python.Views.QELineManager import QELineManager
    from MJOLNIRGui.src.main.python.Views.QPlaneManager import QPlaneManager
    from MJOLNIRGui.src.main.python.Views.Cut1DManager import Cut1DManager
    from MJOLNIRGui.src.main.python.Views.MaskManager import MaskManager
    from MJOLNIRGui.src.main.python.Views.Raw1DManager import Raw1DManager
    from MJOLNIRGui.src.main.python.Views.NormalizationManager import NormalizationManager
    from MJOLNIRGui.src.main.python.Views.MolecularCalculationManager import MolecularCalculationManager
    from MJOLNIRGui.src.main.python.Views.PredictionToolManager import PredictionToolManager
    from MJOLNIRGui.src.main.python.Views.TimeEstimateManager import ScanListManager
    from MJOLNIRGui.src.main.python.Views.CalculatorManager import CalculatorManager
    from MJOLNIRGui.src.main.python.Views.SubtractionManager import SubtractionManager
    from MJOLNIRGui.src.main.python.Views.collapsibleBox import CollapsibleBox
    from MJOLNIRGui.src.main.python.Views.ElectronicLogBookManager import ElectronicLogBookManager
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile,GuiDataSet
    from MJOLNIRGui.src.main.python.DataModels import DataSetModel,DataFileModel
    from MJOLNIRGui.src.main.python.StateMachine import StateMachine
    from MJOLNIRGui.src.main.python.GuiStates import empty,partial,raw,converted
    from MJOLNIRGui.src.main.python.AboutDialog import AboutDialog
    from MJOLNIRGui.src.main.python.HelpDialog import HelpDialog
    from MJOLNIRGui.src.main.python.generateScripts import initGenerateScript,setupGenerateScript
    from MJOLNIRGui.src.main.python._tools import loadSetting,updateSetting,ProgressBarDecoratorArguments

import sys


from pathlib import Path
home = str(Path.home())


####

# Naming convention: WhereInGui_description_type
# Append _function if it is a function
# E.g.: View3D_plot_button and View3D_plot_button_function

#Headlines so far are:
#DataSet, View3D, QE Cut, QPlane, Cut1D, Raw1D


class MJOLNIRMainWindow(QtWidgets.QMainWindow):
    mask_changed = QtCore.pyqtSignal()
    state_changed = QtCore.pyqtSignal(str,str,name='stateChanged')
    def __init__(self,AppContext):

        super(MJOLNIRMainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.AppContext = AppContext
        self.version = version
        ### Settings saved in .MJOLNIRGuiSettings
        self.settingsFile = path.join(home,'.MJOLNIRGuiSettings')
        self.views = []
        guiSettings = loadSetting(self.settingsFile,'guiSettings')
        self.colormap = 'viridis'
        self.currentFolder = ''

        self.isClosing = False 
        self.ui.setupUi(self)
        self.update()

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.AppContext.get_resource('Icons/Own/MJOLNIR.png')))
        self.setWindowIcon(icon)

        # List to hold all views that need to be setup
        self.views = []
        ## Set up DataSetManager
        self.ui.dataSetManager = DataSetManager(None,self)
        vlay = QtWidgets.QVBoxLayout(self.ui.fixedOpen)
        vlay.addWidget(self.ui.dataSetManager)

        vlay.addStretch()

        self.update()
        self.views.append(self.ui.dataSetManager)

        self.windows = [] # Holder for generated plotting windows
        self.figureList = [] # Holder for selectable window list

        # Lists of views in shown order
        self.nameList = ['View3D','QE cuts','Q plane','1D cuts','1D raw data','Masking'] # 'Normalization'
        self.viewClasses = [View3DManager,QELineManager,QPlaneManager,Cut1DManager,Raw1DManager]#[View3D,View3D,View3D,Cut1D,Raw1D] # NormalizationManager
        self.startState = [True,False,False,False,True,False] # If not collapsed #False

        # Find correct layout to insert views
        vlay = QtWidgets.QVBoxLayout(self.ui.collapsibleContainer)
        # Insert all views
        self.boxContainers = []
        for name,Type,state in zip(self.nameList,self.viewClasses,self.startState):
            self.update()
            box = CollapsibleBox(name,startState=state)
            self.boxContainers.append(box)
            vlay.addWidget(box)
            lay = QtWidgets.QVBoxLayout()

            widget = Type(guiWindow=self)
            #if Type == NormalizationManager: # Get a reference to the sample manager directly in self
            #    self.normalizationManager = widget
            self.views.append(widget)
            lay.addWidget(widget)
           
            box.setContentLayout(lay)
        
        vlay.setAlignment(QtCore.Qt.AlignTop)

        self.dataSets = []

        self.current_timer = None
        
        self.blockItems = [getattr(self.ui,item) for item in self.ui.__dict__ if '_button' in item[-7:]] # Collect all items to block on calls
        self.blockItems.append(self.ui.DataSet_binning_comboBox)

        self.lineEdits = [getattr(self.ui,item) for item in self.ui.__dict__ if '_lineEdit' in item[-9:]] # Collect all lineedits
        self.radioButtons = [getattr(self.ui,item) for item in self.ui.__dict__ if '_radioButton' in item] # Collect all radiobuttons
        self.spinBoxes = [getattr(self.ui,item) for item in self.ui.__dict__ if '_spinBox' in item[-8:]] # Collect all spinboxes
        self.checkBoxes = [getattr(self.ui,item) for item in self.ui.__dict__ if '_checkBox' in item[-9:]] # Collect all checkboxes


        self.ui.actionSave_GUI_state.setShortcut("Ctrl+S")
        self.ui.actionLoad_GUI_state.setShortcut("Ctrl+O")
        self.ui.actionExit.setShortcut("Ctrl+Q")

        self.ui.actionHelp.setShortcut("Ctrl+?")

        self.log = _guitools.log(self.ui.textBrowser,button=self.ui.log_reset_btn)
        self.ui.log_reset_btn.clicked.connect(self.clearStatus)
        self._clearStatus() # Call underscore method to avoid decorator
        

        self.ui.progressBar._text = 'Ready'
        self.ui.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        

        def setText(self, text):
            self._text = text

        def text(self):
            if not self.value == 0:
                return self._text + ' ' + self._oldText()
            else:
                return self._text

        self.ui.progressBar.setText = lambda text: setText(self.ui.progressBar,text)
        self.ui.progressBar._oldText = self.ui.progressBar.text
        self.ui.progressBar.text = lambda: text(self.ui.progressBar)

        self.braggPoints = None

        self.update()
        initGenerateScript(self)

        for view in self.views: # Run through all views to set them up
            view.setup()

        self.maskingManager = MaskManager(self)

        setupGenerateScript(self)
        self.update()
        self.setupMenu()
        self.update()
        self.setupStateMachine()
        self.update()
        self.stateMachine.run()
        self.update()
        self.loadFolder() # Load last folder as default 
        self.loadedGuiSettings = None
        self.ui.menubar.setNativeMenuBar(False)
        
        if sys.platform.lower() == 'darwin':
        ## Update image of arrows to correct style on mac
            correctedArrows = """QToolButton::down-arrow {
        image: url("""+self.AppContext.get_resource('down.png')+""");
    }

    QToolButton::right-arrow {
        image: url("""+self.AppContext.get_resource('right.png')+""");
    }"""

            self.setStyleSheet(self.styleSheet()+correctedArrows)

        # Set up preset for electronic logbook
        self.logbookPreset = ['A3','twoTheta','sampleName','title','scanCommand','ei']

    def setupMenu(self): # Set up all QActions and menus
        self.ui.actionExit.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/cross-button.png')))
        self.ui.actionExit.setToolTip('Exit the application') 
        self.ui.actionExit.setStatusTip(self.ui.actionExit.toolTip())
        self.ui.actionExit.triggered.connect(self.close)

        self.ui.actionAbout.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/information-button.png')))
        self.ui.actionAbout.setToolTip('Show About') 
        self.ui.actionAbout.setStatusTip(self.ui.actionAbout.toolTip())
        self.ui.actionAbout.triggered.connect(self.about)

        self.ui.actionHelp.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/question-button.png')))
        self.ui.actionHelp.setToolTip('Show Help') 
        self.ui.actionHelp.setStatusTip(self.ui.actionHelp.toolTip())
        self.ui.actionHelp.triggered.connect(self.help)

        self.ui.actionSubtraction.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/question-button.png')))
        self.ui.actionSubtraction.setToolTip('Show Subtraction Help') 
        self.ui.actionSubtraction.setStatusTip(self.ui.actionSubtraction.toolTip())
        self.ui.actionSubtraction.triggered.connect(self.subtractionHelp)

        self.ui.actionSave_GUI_state.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/folder-save.png')))
        self.ui.actionSave_GUI_state.setToolTip('Save current Gui setup') 
        self.ui.actionSave_GUI_state.setStatusTip(self.ui.actionSave_GUI_state.toolTip())
        self.ui.actionSave_GUI_state.triggered.connect(self.saveCurrentGui)
        #self.actionSave_GUI_state_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        #self.ui.actionSave_GUI_state.triggered.connect(self.saveCurrentGui)

        self.ui.actionLoad_GUI_state.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/folder--arrow.png')))
        self.ui.actionLoad_GUI_state.setToolTip('Load Gui setup') 
        self.ui.actionLoad_GUI_state.setStatusTip(self.ui.actionLoad_GUI_state.toolTip())
        self.ui.actionLoad_GUI_state.triggered.connect(self.loadGui)
        #self.actionLoad_GUI_state_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self)
        #self.ui.actionLoad_GUI_state.triggered.connect(self.loadGui)

        self.ui.actionGenerate_View3d_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-3D.png')))
        self.ui.actionGenerate_View3d_script.setToolTip('Generate 3D Script') 
        self.ui.actionGenerate_View3d_script.setStatusTip(self.ui.actionGenerate_View3d_script.toolTip())
        self.ui.actionGenerate_View3d_script.triggered.connect(self.generate3DScript)

        self.ui.actionGenerate_QELine_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-QE.png')))
        self.ui.actionGenerate_QELine_script.setToolTip('Generate QE Cut Script') 
        self.ui.actionGenerate_QELine_script.setStatusTip(self.ui.actionGenerate_QELine_script.toolTip())
        self.ui.actionGenerate_QELine_script.triggered.connect(self.generateQEScript)
        
        self.ui.actionGenerate_QPlane_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-QP.png')))
        self.ui.actionGenerate_QPlane_script.setToolTip('Generate QPlane Script') 
        self.ui.actionGenerate_QPlane_script.setStatusTip(self.ui.actionGenerate_QPlane_script.toolTip())
        self.ui.actionGenerate_QPlane_script.triggered.connect(self.generateQPlaneScript)
        
        self.ui.actionGenerate_1d_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-1D.png')))
        self.ui.actionGenerate_1d_script.setToolTip('Generate Cut1D Script') 
        self.ui.actionGenerate_1d_script.setStatusTip(self.ui.actionGenerate_1d_script.toolTip())
        self.ui.actionGenerate_1d_script.triggered.connect(self.generateCut1DScript)
        
        self.ui.action_masking_gui.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/mask-open.png')))
        self.ui.action_masking_gui.setToolTip('Masking Gui') 
        self.ui.action_masking_gui.setStatusTip(self.ui.action_masking_gui.toolTip())
        self.ui.action_masking_gui.triggered.connect(self.maskingManager.setWindowVisible)
        self.ui.action_masking_gui.setShortcut("Ctrl+M")


        self.ui.actionSettings.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/settings.png')))
        self.ui.actionSettings.setDisabled(False)
        self.ui.actionSettings.setToolTip('Change View Settings') 
        self.ui.actionSettings.setStatusTip(self.ui.actionSettings.toolTip())
        self.ui.actionSettings.triggered.connect(self.settingsDialog)

        
        self.ui.actionClose_Windows.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/CloseWindows.png')))
        self.ui.actionClose_Windows.setDisabled(False)
        self.ui.actionClose_Windows.setToolTip('Close All Plotting Windows') 
        self.ui.actionClose_Windows.setStatusTip(self.ui.actionClose_Windows.toolTip())
        self.ui.actionClose_Windows.triggered.connect(self.closeWindows)


        self.ui.actionGenerate_Normalization.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/ruler.png')))
        self.ui.actionGenerate_Normalization.setDisabled(False)
        self.ui.actionGenerate_Normalization.setToolTip('Generate a script to normalize data absolutely') 
        self.ui.actionGenerate_Normalization.setStatusTip(self.ui.actionGenerate_Normalization.toolTip())
        self.ui.actionGenerate_Normalization.triggered.connect(self.absolutNormalizationTool)

        self.ui.actionPrediction_Tool.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/predict.png')))
        self.ui.actionPrediction_Tool.setDisabled(False)
        self.ui.actionPrediction_Tool.setToolTip('Predict scan coverage') 
        self.ui.actionPrediction_Tool.setStatusTip(self.ui.actionPrediction_Tool.toolTip())
        self.ui.actionPrediction_Tool.triggered.connect(self.predictionTool)
        self.ui.actionPrediction_Tool.setShortcut("Ctrl+P")

        self.ui.actionTime_Estimate_Tool.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/clock.png')))
        self.ui.actionTime_Estimate_Tool.setDisabled(False)
        self.ui.actionTime_Estimate_Tool.setToolTip('Predict Script time') 
        self.ui.actionTime_Estimate_Tool.setStatusTip(self.ui.actionTime_Estimate_Tool.toolTip())
        self.ui.actionTime_Estimate_Tool.triggered.connect(self.timeEstimate)
        self.ui.actionTime_Estimate_Tool.setShortcut("Ctrl+T")

        self.ui.actionCalculate_Molecular_Weight.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/balance.png')))
        self.ui.actionCalculate_Molecular_Weight.setDisabled(False)
        self.ui.actionCalculate_Molecular_Weight.setToolTip('Calculate Molecular Mass from Chemical Formula') 
        self.ui.actionCalculate_Molecular_Weight.setStatusTip(self.ui.actionCalculate_Molecular_Weight.toolTip())
        self.ui.actionCalculate_Molecular_Weight.triggered.connect(self.molarMassTool)

        self.ui.actionNeutron_Calculations.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/calculator.png')))
        self.ui.actionNeutron_Calculations.setDisabled(False)
        self.ui.actionNeutron_Calculations.setToolTip('Calculate standard neutron quantities') 
        self.ui.actionNeutron_Calculations.setStatusTip(self.ui.actionNeutron_Calculations.toolTip())
        self.ui.actionNeutron_Calculations.triggered.connect(self.neutronCalculationTool)

        self.ui.actionElectronic_Logbook.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/book--pencil.png')))
        self.ui.actionElectronic_Logbook.setToolTip('Generate Electronic Logbook from files') 
        self.ui.actionElectronic_Logbook.setStatusTip(self.ui.actionElectronic_Logbook.toolTip())
        self.ui.actionElectronic_Logbook.triggered.connect(self.electronicLogbookTool)
        self.ui.actionElectronic_Logbook.setShortcut("Ctrl+E")

        self.ui.actionSubtraction_Of_DataSets.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/subtract.png')))
        self.ui.actionSubtraction_Of_DataSets.setToolTip('Perform Subtraction of two DataSets') 
        self.ui.actionSubtraction_Of_DataSets.setStatusTip(self.ui.actionSubtraction_Of_DataSets.toolTip())
        self.ui.actionSubtraction_Of_DataSets.triggered.connect(self.subtractionManager)
        self.ui.actionSubtraction_Of_DataSets.setShortcut("Ctrl+D")

        self.ui.View3D_CurratAxe_button.clicked.connect(self.openBraggListWindow)

    def getProgressBarValue(self):
        return self.ui.progressBar.value

    def addProgressBarValue(self,value):
        currentValue = self.getProgressBarValue()+value
        self.ui.progressBar.setValue(currentValue)
        self.ui.progressBar.value = currentValue
        

    def setProgressBarValue(self,value):
        if not hasattr(self,'ui.progressBar.value'):
            self.ui.progressBar.value = 0
        
        self.ui.progressBar.setValue(value)
        self.ui.progressBar.value = value

    def setProgressBarLabelText(self,text):
        if self.current_timer:
            self.current_timer.stop()
        #self.ui.progressBar_label.setText(text)
        self.ui.progressBar.setText(text)

    def setProgressBarMaximum(self,value):
        self.ui.progressBar.setMaximum(value)

    def resetProgressBar(self):
        self.setProgressBarValue(0)
        self.setProgressBarLabelText('Ready')

    def saveSettingsDialog(self,event):
        res = QtWidgets.QMessageBox.question(self,
                                    "Exit - Save Gui Settings",
                                    "Do you want to save Gui Settings?",
                                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        
        if res == QtWidgets.QMessageBox.Save:
            if self.saveCurrentGui(): # successful saving
                self.closeWindows()
                event.accept()
            else:
                event.ignore()
                return False
        elif res == QtWidgets.QMessageBox.No:
            self.closeWindows()
            event.accept()
            return 1
        else:
            event.ignore()
            return 0

    def quitDialog(self,event):
        res = QtWidgets.QMessageBox.question(self,
                                    "Exit",
                                    "Do you want to exit the Gui?",
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if res == QtWidgets.QMessageBox.Yes:
            self.closeWindows()
            event.accept()
            return 1
        else:
            event.ignore()
            return 0

    def restart(self):
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
        print(status)

    def closeEvent(self, event):
        if self.loadedGuiSettings is None:
            if not self.saveSettingsDialog(event): # The dialog is cancelled
                return
        
        elif np.all([s1==s2 for s1,s2 in zip(self.loadedGuiSettings.values(),self.generateCurrentGuiSettings().values())]):
            if not self.quitDialog(event):
                return

        else:
            if not self.saveSettingsDialog(event): # The dialog is cancelled
                return
        self.isClosing = True
        self.maskingManager.close()
        self.closeWindows()

    @ProgressBarDecoratorArguments(runningText='Closing Windows',completedText='Windows Closed')
    def closeWindows(self):
        if hasattr(self,'windows'):
            for window in self.windows:
                try:
                    plt.close(window)
                except:
                    try:
                        window.close()
                    except:
                        pass
            for figureList in self.figureList:
                figureList.closeAll()
        return True

    def about(self):
        dialog = AboutDialog(self.AppContext.get_resource('About.txt'),version=self.version,icon=QtGui.QIcon(self.AppContext.get_resource('Icons/Own/information-button.png')))
        dialog.exec_()

    def help(self):
        dialog = HelpDialog(self.AppContext.get_resource('Help.txt'),guiWindow = self)
        dialog.exec_()

    def subtractionHelp(self):
        dialog = HelpDialog(self.AppContext.get_resource('SubtractionHelp.txt'),guiWindow = self)
        dialog.exec_()


    def setupStateMachine(self):
        self.stateMachine = StateMachine([empty,partial,raw,converted],self)

    def update(self):
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        

    @ProgressBarDecoratorArguments(runningText='Saving Gui Settings',completedText='Gui Settings Saved',failedText='Cancelled')
    def saveCurrentGui(self): # save data set and files in format DataSetNAME DataFileLocation DataFileLocation:DataSetNAME
        #DataSet = [self.dataSets[I].name for I in range(self.DataSetModel.rowCount(None))]
        
        settingsDict = self.generateCurrentGuiSettings(updateProgressBar=True)
        if not hasattr(self,'loadedSettingsFile'):
            self.loadedSettingsFile = home
        saveSettings,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',self.loadedSettingsFile)

        if saveSettings is None or saveSettings == '':
            return False

        if not saveSettings.split('.')[-1] == 'MJOLNIRGuiSettings':
            saveSettings+='.MJOLNIRGuiSettings'

        if os.path.exists(saveSettings): # if file already exists user has been asked to delete it
            os.remove(saveSettings)
        for key,value in settingsDict.items():
            updateSetting(saveSettings,key,value)
        self.loadedGuiSettings = self.generateCurrentGuiSettings()
        return True


    def generateCurrentGuiSettings(self,updateProgressBar=False):
        saveString = []
        
        if updateProgressBar: self.setProgressBarMaximum(len(self.DataSetModel.dataSets))

        for i,ds in enumerate(self.DataSetModel.dataSets):
            dsDict = {'name':ds.name}
            
            localstring = [df.fileLocation if df.type != 'nxs' else df.original_fileLocation for df in ds]
            dsDict['files']=localstring
            dsDict['binning'] = [None if df.type != 'nxs' else df.binning for df in ds]
            if not ds.background is None:
                dsDict['background'] = ds.background
                dsDict['convertBeforeSubtract'] = ds.convertBeforeSubtract
            if not ds._maskingObject is None:
                dsDict['maskingObject'] = ds._maskingObject
            saveString.append(dsDict)
            if updateProgressBar: self.setProgressBarValue((i+1))

        lineEditString = self.generateCurrentLineEditSettings()
        radioButtonString = self.generateCurrentRadioButtonSettings()
        spinBoxString = self.generateCurrentSpinBoxSettings()
        checkBoxString = self.generateCurrentcheckBoxSettings()
        fileDir = ''
        logbookPreset = self.logbookPreset.copy()
        if hasattr(self,'predictionSettings'):
            predictionSettings  = self.predictionSettings
        else:
            predictionSettings = {}

        infos = self.DataFileInfoModel.currentInfos()
        guiSettings = self.guiSettings()
        returnDict = {'dataSet':saveString, 'lineEdits':lineEditString, 'radioButtons': radioButtonString,'spinBoxes':spinBoxString,
                      'checkBoxes':checkBoxString,'fileDir':fileDir, 'infos':infos, 'guiSettings':guiSettings,
                      'predictionSettings':predictionSettings,'logbookPreset':logbookPreset}
        return returnDict

    def generateCurrentLineEditSettings(self):
        lineEditValueString = {}
        for item in self.lineEdits:
            lineEditValueString[item.objectName()] = item.text()
        return lineEditValueString

    def generateCurrentSpinBoxSettings(self):
        spinBoxValueString = {}
        for item in self.spinBoxes:
            spinBoxValueString[item.objectName()] = item.value()
        return spinBoxValueString

    def generateCurrentcheckBoxSettings(self):
        chechValueString = {}
        for item in self.checkBoxes:
            chechValueString[item.objectName()] = item.isChecked()
        return chechValueString

    def generateCurrentRadioButtonSettings(self):
        radioButtonString = {}
        for item in self.radioButtons:
            radioButtonString[item.objectName()] = item.isChecked()
        return radioButtonString

    def loadFolder(self):
        fileDir = loadSetting(self.settingsFile,'fileDir')
        if not fileDir is None:
            self.setCurrentDirectory(fileDir)


    @ProgressBarDecoratorArguments(runningText='Loading gui settings',completedText='Loading Done',failedText='Cancelled')
    def loadGui(self,presetFileLocation=None):
        
        # Load saveFile
        if not hasattr(self,'loadedSettingsFolder'):
            folder = home
        else:
            folder = self.loadedSettingsFolder
        
        if presetFileLocation is None: # When no file is provided, open file dialogue
            settingsFile,_ = QtWidgets.QFileDialog.getOpenFileName(self,"Open GUI settings file", folder,"Setting (*.MJOLNIRGuiSettings);;All Files (*)")
        else:
            settingsFile = presetFileLocation
        self.update()
        self.loadedSettingsFolder = os.path.dirname(settingsFile)
        self.loadedSettingsFile = settingsFile
        
        if settingsFile is None or settingsFile == '':
            return False
        
        self.setProgressBarLabelText('Deleating Old Data Sets and Files')
        while self.DataSetModel.rowCount(None)>0:
            self.DataSetModel.delete(self.DataSetModel.getCurrentDatasetIndex())
        else:
            self.DataSetModel.layoutChanged.emit()
            self.DataFileModel.updateCurrentDataSetIndex()
        self.update()
        dataSetString = loadSetting(settingsFile,'dataSet')
        if not dataSetString is None:
            totalFiles = np.sum([len(dsDict['files'])+np.sum(1-np.array([d is None for d in dsDict['binning']]))+1 for dsDict in dataSetString])+1
            # Get estimate of total number of data files
            self.setProgressBarMaximum(totalFiles)
            
            self.setProgressBarValue(0)
            logbookPreset = loadSetting(settingsFile,'logbookPreset')
            if not logbookPreset is None:
                self.logbookPreset = logbookPreset
            

            for dsDict in dataSetString:
                DSName = dsDict['name']
                self.setProgressBarLabelText('Loading Data Set \''+DSName+'\'')   
                files = dsDict['files'] # data or foreground data
                if 'background' in dsDict: # Data set is a subtracted set!
                    background = dsDict['background']
                    if len(files)!=0: # If files in dataset, continue
                        dfs = []
                        for dfLocation in files:
                            df = GuiDataFile(dfLocation)
                            self.update()
                            dfs.append(df)
                            self.addProgressBarValue(0.5)
                        dfsBG = []
                        for dfLocation in background:
                            df = GuiDataFile(dfLocation)
                            self.update()
                            dfsBG.append(df)
                            self.addProgressBarValue(0.5)
                        
                        
                        foreground_ds = GuiDataSet(name='fg',dataFiles=dfs)
                        background_ds = GuiDataSet(name='bg',dataFiles=dfsBG)
                        binnings = dsDict['binning']
                        if dsDict['convertBeforeSubtract']:
                            self.setProgressBarLabelText('Converting Data Set \''+DSName+'\'')   
                            for df,binning in zip(foreground_ds,binnings): # Give the correct binning
                                df.binning = binning
                            foreground_ds.convertDataFile(guiWindow=self,setProgressBarMaximum=False,progressUpdate=0.5,printFunction=self.writeToStatus)
                            self.update()
                            for df,binning in zip(background_ds,binnings): # Assume binning is the same across data sets
                                df.binning = binning
                            background_ds.convertDataFile(guiWindow=self,setProgressBarMaximum=False,progressUpdate=0.5,printFunction=self.writeToStatus)
                            self.update()
                            

                        temp = foreground_ds-background_ds
                        
                        ds = GuiDataSet(name=DSName,dataSet=temp)
                        
                        ds.background = background
                        ds.convertBeforeSubtract = dsDict['convertBeforeSubtract']
                        
                        if not ds.convertBeforeSubtract: # Convert after subtraction if needed
                            if not np.any([b is None for b in dsDict['binning']]):
                                self.setProgressBarLabelText('Converting Data Set \''+DSName+'\'')   
                                ds.convertDataFile(guiWindow=self,setProgressBarMaximum=False,printFunction=self.writeToStatus)
                                self.update()
                        if 'maskingObject' in dsDict:
                            maskingObject = dsDict['maskingObject']                        
                            self.setProgressBarLabelText('Applying Mask to \''+DSName+'\'') 
                            ds.mask = maskingObject(ds)
                            ds._maskingObject = maskingObject

                else: # Regular dataset
                        
                    dfs = None
                    if len(files)!=0: # If files in dataset, continue
                        dfs = []
                        for dfLocation in files:
                            df = GuiDataFile(dfLocation)
                            self.update()
                            dfs.append(df)
                            self.addProgressBarValue(1)
                    ds = GuiDataSet(name=DSName,dataFiles=dfs)
                    if 'binning' in dsDict:
                        if not np.any([b is None for b in dsDict['binning']]):
                            binnings = dsDict['binning']
                            for df,binning in zip(ds,binnings):
                                df.binning = binning
                            self.setProgressBarLabelText('Converting Data Set \''+DSName+'\'')     
                            ds.convertDataFile(guiWindow=self,setProgressBarMaximum=False,printFunction=self.writeToStatus)
                            self.update()

                    if 'maskingObject' in dsDict:
                        maskingObject = dsDict['maskingObject']                        
                        ds.mask = maskingObject(ds)
                        ds._maskingObject = maskingObject

                
                self.DataSetModel.append(ds)
                self.DataSetModel.layoutChanged.emit()
                self.update()
                self.addProgressBarValue(1)
        else:
            self.setProgressBarLabelText('')
        DataFileListInfos = loadSetting(settingsFile,'infos')
        if not DataFileListInfos is None:
            self.DataFileInfoModel.infos = DataFileListInfos

        self.loadGuiSettings(file=settingsFile)
        self.loadLineEdits(file=settingsFile)
        self.loadRadioButtons(file=settingsFile)
        self.loadSpinBoxes(file=settingsFile)
        self.loadCheckBoxes(file=settingsFile)
        self.loadPredictionSettings(file=settingsFile)
        self.DataSetModel.layoutChanged.emit()
        self.DataFileInfoModel.layoutChanged.emit()
        self.DataFileModel.updateCurrentDataSetIndex()
        self.update()


        self.loadedGuiSettings = self.generateCurrentGuiSettings()
        return True

    def guiSettings(self):
        boxStates = [b.state for b in self.boxContainers]
        settingsDict = {'boxStates':boxStates,'colormap':self.colormap}
        if not hasattr(self,'BraggListWindow'):
           settingsDict['braggPoints'] = self.braggPoints
        else:
            settingsDict['braggPoints'] = self.BraggListWindow.BraggListModel.getAllData()
        return settingsDict
        
    def loadGuiSettings(self,file=None):
        
        if file is None:
            file = self.settingsFile
        
        guiSettings = loadSetting(file,'guiSettings')
        if not guiSettings is None:
            boxStates = guiSettings['boxStates']
            
            if not boxStates is None:
                for box,value in zip(self.boxContainers,boxStates):
                    try:
                        if box.state != value:
                            box.on_pressed()
                    except AttributeError:
                        pass

            if 'braggPoints' in guiSettings:
                self.braggPoints = guiSettings['braggPoints']
                if hasattr(self,'BraggListWindow'):
                    self.BraggListWindow.BraggListModel.data = self.braggPoints.copy()
                    self.BraggListWindow.BraggListModel.layoutChanged.emit()
            if 'colormap' in guiSettings:
                self.colormap = guiSettings['colormap']
            else:
                self.colormap = 'viridis'
        

    def loadLineEdits(self,file=None):
        if file is None:
            file = self.settingsFile
        lineEditValueString = loadSetting(file,'lineEdits')
        if not lineEditValueString is None:
            if isinstance(lineEditValueString,str):
                print('Please save a new gui state to comply with the new version')
                return
            for item,value in lineEditValueString.items():
                try:
                    getattr(self.ui,item).setText(value)
                except AttributeError:
                    pass

    def loadRadioButtons(self,file=None):
        if file is None:
            file = self.settingsFile
        radioButtonString = loadSetting(file,'radioButtons')
        if not radioButtonString is None:
            if isinstance(radioButtonString,str):
                print('Please save a new gui state to comply with the new version')
                return
            for item,value in radioButtonString.items():
                try:
                    getattr(self.ui,item).setChecked(value)
                except AttributeError:
                    pass

    def loadPredictionSettings(self,file=None):
        if file is None:
            file = self.settingsFile
        predictionSettings = loadSetting(file,'predictionSettings')
        if not predictionSettings is None:
            if isinstance(predictionSettings,str):
                print('Please save a new gui state to comply with the new version')
                return
            self.predictionSettings = predictionSettings

    def loadSpinBoxes(self,file=None):
        if file is None:
            file = self.settingsFile
        spinBoxValueString = loadSetting(file,'spinBoxes')
        if not spinBoxValueString is None:
            if isinstance(spinBoxValueString,str):
                print('Please save a new gui state to comply with the new version')
                return
            for item,value in spinBoxValueString.items():
                try:
                    getattr(self.ui,item).setValue(value)
                except AttributeError:
                    pass
    
    def loadCheckBoxes(self,file=None):
        if file is None:
            file = self.settingsFile
        checkBoxString = loadSetting(file,'checkBoxes')
        if not checkBoxString is None:
            if isinstance(checkBoxString,str):
                print('Please save a new gui state to comply with the new version')
                return
            for item,value in checkBoxString.items():
                try:
                    getattr(self.ui,item).setChecked(value)
                except AttributeError:
                    pass

    def getCurrentDirectory(self):
        return self.currentFolder

    def setCurrentDirectory(self,folder):
        self.currentFolder = folder
        
    def writeToStatus(self,text):
        self.log.append(text)

    def _clearStatus(self):
        self.log.clear()

    @ProgressBarDecoratorArguments(runningText='Clear Log',completedText='Log Cleared')
    def clearStatus(self):
        self._clearStatus()
        return True
    

    def resetProgressBarTimed(self):
        if self.current_timer:
            self.current_timer.stop()
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.resetProgressBar)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(3000)

    #def changeTheme(self,name):
    #    if not name in themes.keys():
    #        raise AttributeError('Theme name not recognized. Got {}, but allowed are: '.format(name),', '.join(themes.keys()))
    #    app = QtWidgets.QApplication.instance()
    #    self.theme = name
    #    themes[name](app)
    #    #palette = app.palette()
    #    #print('Palette:',palette)
    #    #for view in self.views:
    #    #    view.setPalette(palette)


    def settingsDialog(self):
        # Get infos from DataFileInfoModel
        
        dataFileInfoModelPossibleSettings,dataFileInfoModelInitial = self.DataFileInfoModel.settingsDialog()
        # Create a widget holding check boxes for all possible settings
        dFIMLayout = QtWidgets.QVBoxLayout() # Outer most layout
        dFIMLayoutScrollArea = QtWidgets.QScrollArea() # scrollarea layout
        dummyWidget = QtWidgets.QWidget() # Dummy widget to insert layout into scroll area

        dFIMLayout_settings = QtWidgets.QVBoxLayout()
        dFIMTitleLabel = QtWidgets.QLabel(text='DataFile intormation \nSelect infos to be shown for selected file(s)')
        dFIMTitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        # Add title to layout
        dFIMLayout.addWidget(dFIMTitleLabel)

        # make check boxes for all settings
        dFIMcheckBoxes = []
        for setting in dataFileInfoModelPossibleSettings.values():
            checkBox = QtWidgets.QCheckBox()
            dFIMcheckBoxes.append(checkBox)
            name = setting.location
            checkBox.setText(name)
            checkBox.setChecked(setting in dataFileInfoModelInitial)
            dFIMLayout_settings.addWidget(checkBox)
        dummyWidget.setLayout(dFIMLayout_settings)
        dFIMLayoutScrollArea.setWidget(dummyWidget)
        
        dFIMLayout.addWidget(dFIMLayoutScrollArea)
        # Overview: dFIMLayout -> dFIMLayoutScrollArea -> dummyWidget -> dFIMLayout_settings -> checkBox
        #     Type:   layout             widget              widget            layout            widget


        # accept function arguments: self (dialog), layout which was passed in
        def dFIMAcceptFunction(self,layout,possibleSettings=dataFileInfoModelPossibleSettings):
            self.dMFIASettings = []
            for idx,setting in enumerate(possibleSettings.values()): # Loop through all the possible settings
                box = layout.itemAt(1).widget().widget().layout().itemAt(idx).widget() # Skip 0 as it is a QLabel
                if box.isChecked():# If checked add the corresponding setting to list of loaded settings
                    self.dMFIASettings.append(setting.location)


        # Create layout for gui settings
        guiSettingsLayout = QtWidgets.QVBoxLayout()
        labelTitle = QtWidgets.QLabel(text = 'Color map:')

        cmapBox = QtWidgets.QComboBox()
        cmaps = plt.colormaps()
        current = cmaps.index(self.colormap)
        cmapBox.addItems(cmaps)
        cmapBox.setCurrentIndex(current)
        
        guiSettingsLayout.addWidget(labelTitle)
        guiSettingsLayout.addWidget(cmapBox)


        # Create radiobuttons
        
        def guiSettingsAcceptFunction(self,layout,guiWindow=self):
            cmapBox = layout.itemAt(1).widget()
            guiWindow.colormap = cmapBox.currentText()
            
 
        # settings holds a list of possible settings for all setting fields
        layouts = [guiSettingsLayout,dFIMLayout]
        acceptFunctions = [guiSettingsAcceptFunction,dFIMAcceptFunction]
        dialog = settingsBoxDialog(layouts=layouts,acceptFunctions=acceptFunctions)
        dialog.setWindowIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/settings.png')))
        dialog.resize(dialog.sizeHint())
        
        
        
        if dialog.exec_(): # Execute the dialog
            self.DataFileInfoModel.infos = dialog.dMFIASettings # update settings
            self.DataFileInfoModel.layoutChanged.emit()
        else:
            return
            
    def molarMassTool(self):
        molecularCalculationManager = MolecularCalculationManager(parent=None,guiWindow=self)
        self.windows.append(molecularCalculationManager)
        molecularCalculationManager.show()
        

    def neutronCalculationTool(self):
        calculatorManager = CalculatorManager(parent=None,guiWindow=self)
        self.windows.append(calculatorManager)
        calculatorManager.show()

    def absolutNormalizationTool(self):
        absolutNormalizationWindow = NormalizationManager(parent=None,guiWindow=self)
        self.windows.append(absolutNormalizationWindow)
        absolutNormalizationWindow.show()

    def predictionTool(self):
        predictionToolWindow = PredictionToolManager(parent=None,guiWindow=self)
        self.windows.append(predictionToolWindow)
        predictionToolWindow.show()

    def timeEstimate(self):
        TimeEstimateManagerWindow = ScanListManager(parent=None,guiWindow=self)
        self.windows.append(TimeEstimateManagerWindow)
        TimeEstimateManagerWindow.show()

    def electronicLogbookTool(self):
        electronicLogBook = ElectronicLogBookManager(parent=None,guiWindow=self)
        self.windows.append(electronicLogBook)
        electronicLogBook.show()

    def subtractionManager(self):
        subtractionManager = SubtractionManager(parent=None,guiWindow=self)
        self.windows.append(subtractionManager)
        subtractionManager.show()

    def getBraggPoints(self):
        if hasattr(self,'BraggListWindow'):
            return self.BraggListWindow.getData()
        else:
            return self.braggPoints
    

    def openBraggListWindow(self):
        if hasattr(self,'BraggListWindow'): # If a window is open, use it
            if self.BraggListWindow.isVisible(): # if not visible, the window was closed
                getattr(self.BraggListWindow,'raise')()
                self.BraggListWindow.activateWindow()
            else:
                if self.braggPoints is None:
                    bL = []
                else:
                    bL = self.braggPoints.copy()
                self.BraggListWindow = BraggListManager.BraggListManager(BraggList=bL,guiWindow = self)
                self.BraggListWindow.BraggListModel.layoutChanged.connect(self.View3D_changed_CurratAxeList_function)

                #self.braggPoints = self.BraggListWindow.BraggListModel.data
            self.windows.append(self.BraggListWindow)
            self.BraggListWindow.show()

        else:
            if self.braggPoints is None:
                bL = []
            else:
                bL = self.braggPoints.copy()
            self.BraggListWindow = BraggListManager.BraggListManager(BraggList=bL,guiWindow = self)
            self.BraggListWindow.BraggListModel.layoutChanged.connect(self.View3D_changed_CurratAxeList_function)
            self.windows.append(self.BraggListWindow)
            self.BraggListWindow.show()

class settingsBoxDialog(QtWidgets.QDialog):

    def __init__(self, layouts, acceptFunctions, *args, **kwargs):
        super(settingsBoxDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("Settings")
        self.acceptFunctions = acceptFunctions
        self.layouts = layouts

        self.layout = QtWidgets.QVBoxLayout()
        
        for layout in layouts:
            self.layout.addLayout(layout)
        
        
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self): # the accept button has been pressed
        for aFunc,layout in zip(self.acceptFunctions,self.layouts):
            aFunc(self,layout)
        return super(settingsBoxDialog,self).accept()

    def reject(self):
        return super(settingsBoxDialog,self).reject()



def updateSplash(splash,originalTime,updateInterval,padding='\n'*7+20*' '):
    currentTime = datetime.datetime.now()
    points = int(1000.0*(currentTime-originalTime).total_seconds()/updateInterval)+1

    alignment = QtCore.Qt.AlignTop# | QtCore.Qt.AlignHCenter
    splash.showMessage(padding+'Loading MJOLNIRGui'+'.'*points,color=QtGui.QColor(255,255,255),alignment=alignment)
    #QTimer.singleShot(1000, updateSplash(splash,points+1) )
    QtWidgets.QApplication.processEvents()

def main():
    try:
        import AppContextEmulator
    except ImportError:
        from MJOLNIRGui.src.main.python import AppContextEmulator
        

    app = QtWidgets.QApplication(sys.argv) # Passing command line arguments to app

    appEmu = AppContextEmulator.AppContextEmulator(__file__)

    splash = QtWidgets.QSplashScreen(QtGui.QPixmap(appEmu.get_resource('splash.png')))                                    
    splash.show()

    timer = QtCore.QTimer() 

    # adding action to timer 
    updateInterval = 400 # ms
    originalTime = datetime.datetime.now()
    updater = lambda:updateSplash(splash,originalTime=originalTime,updateInterval=updateInterval)
    updater()
    timer.timeout.connect(updater) 

    # update the timer every updateInterval 
    timer.start(updateInterval)
    

    window = MJOLNIRMainWindow(appEmu) # This window has to be closed for app to end
    splash.finish(window)
    window.show()
    timer.stop()

    if len(sys.argv)==2:
        window.loadGui(presetFileLocation=sys.argv[1])

    app.exec_() 

if __name__ == '__main__':
    main()

    