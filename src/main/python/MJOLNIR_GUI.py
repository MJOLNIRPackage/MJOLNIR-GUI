try:
    import IPython
    shell = IPython.get_ipython()
    shell.enable_matplotlib(gui='qt')
except:
    pass


from MJOLNIR import _tools # Useful tools useful across MJOLNIR
try:
    import _tools as _guitools
except ImportError:
    import MJOLNIRGui.src.main.python._tools as _guitools
import numpy as np
import matplotlib.pyplot as plt
import sys
import datetime
from time import sleep

from os import path
import os

from MJOLNIR.Data import Mask

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
    from Views.CalculatorManager import CalculatorManager
    from Views.collapsibleBox import CollapsibleBox
    from MJOLNIR_Data import GuiDataFile,GuiDataSet,GuiMask
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
    from MJOLNIRGui.src.main.python.Views.CalculatorManager import CalculatorManager
    from MJOLNIRGui.src.main.python.Views.collapsibleBox import CollapsibleBox
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile,GuiDataSet,GuiMask
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
#DataSet, View3D, QELine, QPlane, Cut1D, Raw1D


class MJOLNIRMainWindow(QtWidgets.QMainWindow):
    mask_changed = QtCore.pyqtSignal()
    state_changed = QtCore.pyqtSignal(str,str,name='stateChanged')
    def __init__(self,AppContext):

        super(MJOLNIRMainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.AppContext = AppContext
        self.version = self.AppContext.build_settings['version']   
        ### Settings saved in .MJOLNIRGuiSettings
        self.settingsFile = path.join(home,'.MJOLNIRGuiSettings')
        self.views = []
        guiSettings = loadSetting(self.settingsFile,'guiSettings')
        
        
        #if guiSettings is None:
        #    self.theme = 'light'
        #else:
        #    if not 'theme' in guiSettings:
        #        self.theme = 'light'
        #    else:
        #        self.theme = guiSettings['theme']
                

        
        self.ui.setupUi(self)
        self.update()

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.AppContext.get_resource('Icons/Own/MJOLNIR.png')))
        self.setWindowIcon(icon)

        # List to hold all views that need to be setup
        self.views = []
        ## Set up DataSetManager
        self.ui.dataSetManager = DataSetManager(self.ui.fixedOpen,self)
        self.update()
        self.views.append(self.ui.dataSetManager)

        # Lists of views in shown order
        self.nameList = ['View3D','QE line','Q plane','1D cuts','1D raw data','Masking'] # 'Normalization'
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
        vlay.addStretch()

        self.maskingManager = MaskManager(self)

        self.windows = [] # Holder for generated plotting windows

        self.dataSets = []

        self.current_timer = None
        
        self.blockItems = [getattr(self.ui,item) for item in self.ui.__dict__ if '_button' in item[-7:]] # Collect all items to block on calls
        self.blockItems.append(self.ui.DataSet_binning_comboBox)

        self.lineEdits = [getattr(self.ui,item) for item in self.ui.__dict__ if '_lineEdit' in item[-9:]] # Collect all lineedits
        self.radioButtons = [getattr(self.ui,item) for item in self.ui.__dict__ if '_radioButton' in item] # Collect all radiobuttons
        self.spinBoxes = [getattr(self.ui,item) for item in self.ui.__dict__ if '_spinBox' in item[-8:]] # Collect all spinboxes
        self.checkBoxes = [getattr(self.ui,item) for item in self.ui.__dict__ if '_checkBox' in item[-9:]] # Collect all checkboxes

        self.update()
        initGenerateScript(self)

        for view in self.views: # Run through all views to set them up
            view.setup()

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

        self.ui.actionSave_GUI_state.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/folder-save.png')))
        self.ui.actionSave_GUI_state.setToolTip('Save current Gui setup') 
        self.ui.actionSave_GUI_state.setStatusTip(self.ui.actionSave_GUI_state.toolTip())
        self.ui.actionSave_GUI_state.triggered.connect(self.saveCurrentGui)
        self.actionSave_GUI_state_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        self.actionSave_GUI_state_shortcut.activated.connect(self.saveCurrentGui)

        self.ui.actionLoad_GUI_state.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/folder--arrow.png')))
        self.ui.actionLoad_GUI_state.setToolTip('Load Gui setup') 
        self.ui.actionLoad_GUI_state.setStatusTip(self.ui.actionLoad_GUI_state.toolTip())
        self.ui.actionLoad_GUI_state.triggered.connect(self.loadGui)
        self.actionLoad_GUI_state_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self)
        self.actionLoad_GUI_state_shortcut.activated.connect(self.loadGui)

        self.ui.actionGenerate_View3d_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-3D.png')))
        self.ui.actionGenerate_View3d_script.setToolTip('Generate 3D Script') 
        self.ui.actionGenerate_View3d_script.setStatusTip(self.ui.actionGenerate_View3d_script.toolTip())
        self.ui.actionGenerate_View3d_script.triggered.connect(self.generate3DScript)

        self.ui.actionGenerate_QELine_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-QE.png')))
        self.ui.actionGenerate_QELine_script.setToolTip('Generate QELine Script') 
        self.ui.actionGenerate_QELine_script.setStatusTip(self.ui.actionGenerate_QELine_script.toolTip())
        self.ui.actionGenerate_QELine_script.triggered.connect(self.generateQELineScript)
        
        self.ui.actionGenerate_QPlane_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-QP.png')))
        self.ui.actionGenerate_QPlane_script.setToolTip('Generate QPlane Script') 
        self.ui.actionGenerate_QPlane_script.setStatusTip(self.ui.actionGenerate_QPlane_script.toolTip())
        self.ui.actionGenerate_QPlane_script.triggered.connect(self.generateQPlaneScript)
        
        self.ui.actionGenerate_1d_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/script-1D.png')))
        self.ui.actionGenerate_1d_script.setToolTip('Generate Cut1D Script') 
        self.ui.actionGenerate_1d_script.setStatusTip(self.ui.actionGenerate_1d_script.toolTip())
        self.ui.actionGenerate_1d_script.triggered.connect(self.generateCut1DScript)
        
        self.ui.actionOpen_mask_gui.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/mask-open.png')))
        self.ui.actionOpen_mask_gui.setDisabled(True)
        self.ui.actionOpen_mask_gui.setToolTip('Open Mask Gui') 
        self.ui.actionOpen_mask_gui.setStatusTip(self.ui.actionOpen_mask_gui.toolTip())
        self.ui.actionOpen_mask_gui.triggered.connect(self.maskingManager.setWindowVisible)
        
        self.ui.actionLoad_mask.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/mask-load.png')))
        self.ui.actionLoad_mask.setDisabled(True)
        self.ui.actionLoad_mask.setToolTip('Load Mask - Not Implemented') 
        self.ui.actionLoad_mask.setStatusTip(self.ui.actionLoad_mask.toolTip())
        #self.ui.actionLoad_mask.triggered.connect(self.maskingManager.getMasks)

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


        self.ui.actionNormalizationWidget.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/ruler.png')))
        self.ui.actionNormalizationWidget.setDisabled(False)
        self.ui.actionNormalizationWidget.setToolTip('Generate a script to normalize data absolutely') 
        self.ui.actionNormalizationWidget.setStatusTip(self.ui.actionNormalizationWidget.toolTip())
        self.ui.actionNormalizationWidget.triggered.connect(self.absolutNormalizationTool)

        self.ui.actionPredictionWidget.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/predict.png')))
        self.ui.actionPredictionWidget.setDisabled(False)
        self.ui.actionPredictionWidget.setToolTip('Predict scan coverage') 
        self.ui.actionPredictionWidget.setStatusTip(self.ui.actionPredictionWidget.toolTip())
        self.ui.actionPredictionWidget.triggered.connect(self.predictionTool)

        self.ui.actionMolecularWeight.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/balance.png')))
        self.ui.actionMolecularWeight.setDisabled(False)
        self.ui.actionMolecularWeight.setToolTip('Calculate Molecular Mass from Chemical Formula') 
        self.ui.actionMolecularWeight.setStatusTip(self.ui.actionMolecularWeight.toolTip())
        self.ui.actionMolecularWeight.triggered.connect(self.molarMassTool)

        self.ui.actionNeutronCalculations.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/calculator.png')))
        self.ui.actionNeutronCalculations.setDisabled(False)
        self.ui.actionNeutronCalculations.setToolTip('Calculate standard neutron quantities') 
        self.ui.actionNeutronCalculations.setStatusTip(self.ui.actionNeutronCalculations.toolTip())
        self.ui.actionNeutronCalculations.triggered.connect(self.neutronCalculationTool)

        self.ui.actionElectronicLogbook.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/book--pencil.png')))
        self.ui.actionElectronicLogbook.setDisabled(True)
        self.ui.actionElectronicLogbook.setToolTip('Generate Electronic Logbook from files') 
        self.ui.actionElectronicLogbook.setStatusTip(self.ui.actionElectronicLogbook.toolTip())
        self.ui.actionElectronicLogbook.triggered.connect(self.electronicLogbookTool)

    def getProgressBarValue(self):
        return self.ui.progressBar.value

    def setProgressBarValue(self,value):
        if not hasattr(self,'ui.progressBar.value'):
            self.ui.progressBar.value = 0
        
        self.ui.progressBar.setValue(value)
        self.ui.progressBar.value = value

    def setProgressBarLabelText(self,text):
        if self.current_timer:
            self.current_timer.stop()
        self.ui.progressBar_label.setText(text)

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
            self.saveCurrentGui()
            self.closeWindows()
            event.accept()
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
        return True

    def about(self):
        dialog = AboutDialog(self.AppContext.get_resource('About.txt'),version=self.version)
        dialog.exec_()

    def help(self):
        dialog = HelpDialog(self.AppContext.get_resource('Help.txt'))
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

        for key,value in settingsDict.items():
            updateSetting(saveSettings,key,value)
        self.loadedGuiSettings = self.generateCurrentGuiSettings()
        return True


    def generateCurrentGuiSettings(self,updateProgressBar=False):
        saveString = []
        
        if updateProgressBar: self.setProgressBarMaximum(len(self.DataSetModel.dataSets))

        for i,ds in enumerate(self.DataSetModel.dataSets):
            dsDict = {'name':ds.name}
            
            localstring = [df.fileLocation if df.type != 'nxs' else df.original_file.fileLocation for df in ds]
            dsDict['files']=localstring
            dsDict['binning'] = [None if df.type != 'nxs' else df.binning for df in ds]
            saveString.append(dsDict)
            if updateProgressBar: self.setProgressBarValue((i+1))

        lineEditString = self.generateCurrentLineEditSettings()
        radioButtonString = self.generateCurrentRadioButtonSettings()
        spinBoxString = self.generateCurrentSpinBoxSettings()
        checkBoxString = self.generateCurrentcheckBoxSettings()
        fileDir = self.getCurrentDirectory()

        infos = self.DataFileInfoModel.currentInfos()
        guiSettings = self.guiSettings()
        
        returnDict = {'dataSet':saveString, 'lineEdits':lineEditString, 'radioButtons': radioButtonString,'spinBoxes':spinBoxString,
                      'checkBoxes':checkBoxString,'fileDir':fileDir, 'infos':infos, 'guiSettings':guiSettings}
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

        totalFiles = np.sum([len(dsDict['files'])+np.sum(1-np.array([d is None for d in dsDict['binning']]))+1 for dsDict in dataSetString])+1
        # Get estimate of total number of data files
        self.setProgressBarMaximum(totalFiles)
        counter = 0


        for dsDict in dataSetString:
            self.setProgressBarLabelText('Loading Data Set')
            DSName = dsDict['name']
            files = dsDict['files']
            dfs = None
            if len(files)!=0: # If files in dataset, continue
                dfs = []
                for dfLocation in files:
                    df = GuiDataFile(dfLocation)
                    self.update()
                    dfs.append(df)
                    counter+=1
                    self.setProgressBarValue(counter)
            if DSName == '':
                continue
            ds = GuiDataSet(name=DSName,dataFiles=dfs)
            if 'binning' in dsDict:
                if not np.any([b is None for b in dsDict['binning']]):
                    binnings = dsDict['binning']
                    for df,binning in zip(ds,binnings):
                        df.binning = binning
                    self.setProgressBarLabelText('Converting Data Set')    
                    ds.convertDataFile(guiWindow=self,setProgressBarMaximum=False)
                    self.update()
            
            self.DataSetModel.append(ds)
            self.DataSetModel.layoutChanged.emit()
            self.update()
            counter+=1
            self.setProgressBarValue(counter)
            
        DataFileListInfos = loadSetting(settingsFile,'infos')
        if not DataFileListInfos is None:
            self.DataFileInfoModel.infos = DataFileListInfos

        self.loadGuiSettings(file=settingsFile)
        self.loadLineEdits(file=settingsFile)
        self.loadRadioButtons(file=settingsFile)
        # self.loadSpinBoxes(file=settingsFile)
        # self.loadCheckBoxes(file=settingsFile)
        self.DataSetModel.layoutChanged.emit()
        self.DataFileInfoModel.layoutChanged.emit()
        self.DataFileModel.updateCurrentDataSetIndex()
        self.update()


        self.loadedGuiSettings = self.generateCurrentGuiSettings()
        return True

    def guiSettings(self):
        boxStates = [b.state for b in self.boxContainers]
        settingsDict = {'boxStates':boxStates}
        return settingsDict
        
    def loadGuiSettings(self,file=None):
        if file is None:
            file = self.settingsFile
        guiSettings = loadSetting(file,'guiSettings')
        boxStates = guiSettings['boxStates']
        
        if not boxStates is None:
            for box,value in zip(self.boxContainers,boxStates):
                try:
                    if box.state != value:
                        box.on_pressed()
                except AttributeError:
                    pass


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
        return self.ui.DataSet_path_lineEdit.text()

    def setCurrentDirectory(self,folder):
        self.currentFolder = folder
        self.ui.DataSet_path_lineEdit.setText(folder)
        

    

    def resetProgressBarTimed(self):
        if self.current_timer:
            self.current_timer.stop()
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.resetProgressBar)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(3000)

    def changeTheme(self,name):
        if not name in themes.keys():
            raise AttributeError('Theme name not recognized. Got {}, but allowed are: '.format(name),', '.join(themes.keys()))
        app = QtWidgets.QApplication.instance()
        self.theme = name
        themes[name](app)
        #palette = app.palette()
        #print('Palette:',palette)
        #for view in self.views:
        #    view.setPalette(palette)


    def settingsDialog(self):
        # Get infos from DataFileInfoModel
        
        dataFileInfoModelPossibleSettings,dataFileInfoModelInitial = self.DataFileInfoModel.settingsDialog()
        # Create a widget holding check boxes for all possible settings

        dFIMLayout = QtWidgets.QVBoxLayout()
        dFIMTitleLabel = QtWidgets.QLabel(text='Select infos to be shown for selected file(s)')
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
            dFIMLayout.addWidget(checkBox)

        # accept function arguments: self (dialog), layout which was passed in
        def dFIMAcceptFunction(self,layout,possibleSettings=dataFileInfoModelPossibleSettings):
            self.dMFIASettings = []
            for idx,setting in enumerate(possibleSettings.values()): # Loop through all the possible settings
                box = layout.itemAt(idx+1).widget() # Skip 0 as it is a QLabel
                if box.isChecked():# If checked add the corresponding setting to list of loaded settings
                    self.dMFIASettings.append(setting.location)


        # Create layout for gui settings
        guiSettingsLayout = QtWidgets.QVBoxLayout()
 

        # Create radiobuttons
        
        def guiSettingsAcceptFunction(self,layout):
            length = layout.count()-1 # first entry is QLabel
            
 
        # settings holds a list of possible settings for all setting fields
        layouts = [guiSettingsLayout,dFIMLayout]
        acceptFunctions = [guiSettingsAcceptFunction,dFIMAcceptFunction]
        dialog = settingsBoxDialog(layouts=layouts,acceptFunctions=acceptFunctions)

        dialog.resize(dialog.sizeHint())
        
        
        
        if dialog.exec_(): # Execute the dialog
            self.DataFileInfoModel.infos = dialog.dMFIASettings # update settings
            self.DataFileInfoModel.layoutChanged.emit()
        else:
            return
            
    def molarMassTool(self):
        molecularCalculationManager = MolecularCalculationManager()
        self.windows.append(molecularCalculationManager)
        molecularCalculationManager.show()
        

    def neutronCalculationTool(self):
        calculatorManager = CalculatorManager()
        self.windows.append(calculatorManager)
        calculatorManager.show()

    def absolutNormalizationTool(self):
        absolutNormalizationWindow = NormalizationManager(parent=None)
        self.windows.append(absolutNormalizationWindow)
        absolutNormalizationWindow.show()

    def predictionTool(self):
        predictionToolWindow = PredictionToolManager(parent=None,guiWindow=self)
        self.windows.append(predictionToolWindow)
        predictionToolWindow.show()

    def electronicLogbookTool(self):
        print('Not Implemeted yet electronicLogbookTool')

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

    