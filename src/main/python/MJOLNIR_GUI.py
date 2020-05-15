try:
    import IPython
    shell = IPython.get_ipython()
    shell.enable_matplotlib(gui='qt')
except:
    pass


from MJOLNIR import _tools # Useful tools useful across MJOLNIR
import numpy as np
import matplotlib.pyplot as plt
import sys

from os import path
import os


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
    from Views.Raw1DManager import Raw1DManager
    from Views.collapsibleBox import CollapsibleBox
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
    from .Views.main import Ui_MainWindow
    from .Views.DataSetManager import DataSetManager
    from .Views.View3DManager import View3DManager
    from .Views.QELineManager import QELineManager
    from .Views.QPlaneManager import QPlaneManager
    from .Views.Cut1DManager import Cut1DManager
    from .Views.Raw1DManager import Raw1DManager
    from .Views.Raw1DManager import Raw1DManager
    from .Views.collapsibleBox import CollapsibleBox
    from .MJOLNIR_Data import GuiDataFile,GuiDataSet
    from .DataModels import DataSetModel,DataFileModel
    from .StateMachine import StateMachine
    from .GuiStates import empty,partial,raw,converted
    from .AboutDialog import AboutDialog
    from .HelpDialog import HelpDialog
    from .generateScripts import initGenerateScript,setupGenerateScript
    from ._tools import loadSetting,updateSetting,ProgressBarDecoratorArguments

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

    def __init__(self,AppContext):

        super(MJOLNIRMainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.AppContext = AppContext
        self.settingsFile = path.join(home,'.MJOLNIRGuiSettings')
    
        self.ui.setupUi(self)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.AppContext.get_resource('Icons/Own/MJOLNIR.png')))
        self.setWindowIcon(icon)

        # List to hold all views that need to be setup
        self.views = []
        ## Set up DataSetManager
        self.ui.dataSetManager = DataSetManager(self.ui.fixedOpen,self)
        
        self.views.append(self.ui.dataSetManager)

        # Lists of views in shown order
        self.nameList = ['View3D','QE line','Q plane','1D cuts','1D raw data']
        self.viewClasses = [View3DManager,QELineManager,QPlaneManager,Cut1DManager,Raw1DManager]#[View3D,View3D,View3D,Cut1D,Raw1D]
        self.startState = [True,False,False,False,True] # If not collapsed

        # Find correct layout to insert views
        vlay = QtWidgets.QVBoxLayout(self.ui.collapsibleContainer)
        # Insert all views
        for name,Type,state in zip(self.nameList,self.viewClasses,self.startState):
            box = CollapsibleBox(name,startState=state)
            vlay.addWidget(box)
            lay = QtWidgets.QVBoxLayout()

            widget = Type(guiWindow=self)
            self.views.append(widget)
            lay.addWidget(widget)
           
            box.setContentLayout(lay)
        vlay.addStretch()

        self.windows = [] # Holder for generated plotting windows

        self.dataSets = []

        self.current_timer = None
        
        self.blockItems = [getattr(self.ui,item) for item in self.ui.__dict__ if '_button' in item[-7:]] # Collect all items to block on calls
        self.blockItems.append(self.ui.DataSet_binning_comboBox)

        self.lineEdits = [getattr(self.ui,item) for item in self.ui.__dict__ if '_lineEdit' in item[-9:]] # Collect all items to block on calls
        

        initGenerateScript(self)

        for view in self.views: # Run through all views to set them up
            view.setup()

        setupGenerateScript(self)

        self.setupMenu()
        self.setupStateMachine()
        self.stateMachine.run()

        self.loadFolder() # Load last folder as default 
        self.loadedGuiSettings = None

 
    

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

        self.ui.actionLoad_GUI_state.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/folder--arrow.png')))
        self.ui.actionLoad_GUI_state.setToolTip('Load Gui setup') 
        self.ui.actionLoad_GUI_state.setStatusTip(self.ui.actionLoad_GUI_state.toolTip())
        self.ui.actionLoad_GUI_state.triggered.connect(self.loadGui)

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
        self.ui.actionOpen_mask_gui.setToolTip('Open Mask Gui - Not Implemented') 
        self.ui.actionOpen_mask_gui.setStatusTip(self.ui.actionOpen_mask_gui.toolTip())
        
        self.ui.actionLoad_mask.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/mask-load.png')))
        self.ui.actionLoad_mask.setDisabled(True)
        self.ui.actionLoad_mask.setToolTip('Load Mask - Not Implemented') 
        self.ui.actionLoad_mask.setStatusTip(self.ui.actionLoad_mask.toolTip())

        self.ui.actionSettings.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/settings.png')))
        self.ui.actionSettings.setDisabled(False)
        self.ui.actionSettings.setToolTip('Change View Settings') 
        self.ui.actionSettings.setStatusTip(self.ui.actionSettings.toolTip())
        self.ui.actionSettings.triggered.connect(self.DataFileInfoModel.changeInfos)

        
        self.ui.actionClose_Windows.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/CloseWindows.png')))
        self.ui.actionClose_Windows.setDisabled(False)
        self.ui.actionClose_Windows.setToolTip('Close All Plotting Windows') 
        self.ui.actionClose_Windows.setStatusTip(self.ui.actionClose_Windows.toolTip())
        self.ui.actionClose_Windows.triggered.connect(self.closeWindows)
        
    def setProgressBarValue(self,value):
        self.ui.progressBar.setValue(value)

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
            event.accept()
        elif res == QtWidgets.QMessageBox.No:
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
            event.accept()
            return 1
        else:
            event.ignore()
            return 0

    def closeEvent(self, event):

        if self.loadedGuiSettings is None:
            if not self.saveSettingsDialog(event): # The dialog is cancelled
                return
        
        elif np.all([s1==s2 for s1,s2 in zip(self.loadedGuiSettings,self.generateCurrentGuiSettings())]):
            if not self.quitDialog(event):
                return

        else:
            if not self.saveSettingsDialog(event): # The dialog is cancelled
                return

        self.closeWindows()

    @ProgressBarDecoratorArguments(runningText='Closing Windowa',completedText='Windows Closed')
    def closeWindows(self):
        if hasattr(self,'windows'):
            for window in self.windows:
                try:
                    plt.close(window)
                except:
                    pass
        return True

    def about(self):
        dialog = AboutDialog(self.AppContext.get_resource('About.txt'))
        dialog.exec_()

    def help(self):
        dialog = HelpDialog(self.AppContext.get_resource('Help.txt'))
        dialog.exec_()


    def setupStateMachine(self):
        self.stateMachine = StateMachine([empty,partial,raw,converted],self)

    def update(self):
        QtWidgets.QApplication.processEvents()

    @ProgressBarDecoratorArguments(runningText='Saving Gui Settings',completedText='Gui Settings Saved')
    def saveCurrentGui(self): # save data set and files in format DataSetNAME DataFileLocation DataFileLocation:DataSetNAME
        #DataSet = [self.dataSets[I].name for I in range(self.DataSetModel.rowCount(None))]
        
        saveString,lineEditString,fileDir,infos = self.generateCurrentGuiSettings(True)
        
        updateSetting(self.settingsFile,'dataSet',saveString)
        updateSetting(self.settingsFile,'lineEdits',lineEditString)
        updateSetting(self.settingsFile,'fileDir',fileDir)
        updateSetting(self.settingsFile,'infos',infos)
        return True


    def generateCurrentGuiSettings(self,updateProgressBar=False):
        saveString = []
        
        if updateProgressBar: self.setProgressBarMaximum(len(self.DataSetModel.dataSets))

        for i,ds in enumerate(self.DataSetModel.dataSets):
            dsDict = {'name':ds.name}
            
            localstring = [df.fileLocation if df.type != 'nxs' else df.original_file.fileLocation for df in ds]
            dsDict['files']=localstring
            
            saveString.append(dsDict)
            if updateProgressBar: self.setProgressBarValue((i+1))

        lineEditString = self.generateCurrentLineEditSettings()
        fileDir = self.getCurrentDirectory()

        infos = self.DataFileInfoModel.currentInfos()

        return saveString, lineEditString, fileDir, infos

    def generateCurrentLineEditSettings(self):
        lineEditValueString = {}
        for item in self.lineEdits:
            lineEditValueString[item.objectName()] = item.text()
        return lineEditValueString


    def loadFolder(self):
        fileDir = loadSetting(self.settingsFile,'fileDir')
        if not fileDir is None:
            self.setCurrentDirectory(fileDir)


    @ProgressBarDecoratorArguments(runningText='Loading gui settings',completedText='Loading Done')
    def loadGui(self):
        self.setProgressBarLabelText('Deleating Old Data Sets and Files')
        while self.DataSetModel.rowCount(None)>0:
            self.DataSetModel.delete(self.DataSetModel.getCurrentDatasetIndex())
        else:
            self.DataSetModel.layoutChanged.emit()
            self.DataFileModel.updateCurrentDataSetIndex()
            self.update()
        
        dataSetString = loadSetting(self.settingsFile,'dataSet')
        totalFiles = np.sum([len(dsDict['files'])+1 for dsDict in dataSetString])+1
        # Get estimate of total number of data files
        self.setProgressBarMaximum(totalFiles)
        counter = 0

        self.setProgressBarLabelText('Loading Data Sets and Files')
        for dsDict in dataSetString:
            DSName = dsDict['name']
            files = dsDict['files']
            dfs = None
            if len(files)!=0: # If files in dataset, continue
                dfs = []
                for dfLocation in files:
                    df = GuiDataFile(dfLocation)
                    dfs.append(df)
                    counter+=1
                    self.setProgressBarValue(counter)
            if DSName == '':
                continue
            ds = GuiDataSet(name=DSName,dataFiles=dfs)
            self.DataSetModel.append(ds)
            counter+=1
            self.setProgressBarValue(counter)
            
        DataFileListInfos = loadSetting(self.settingsFile,'infos')
        if not DataFileListInfos is None:
            self.DataFileInfoModel.infos = DataFileListInfos

        self.loadLineEdits()
        self.DataSetModel.layoutChanged.emit()
        self.DataFileInfoModel.layoutChanged.emit()
        self.DataFileModel.updateCurrentDataSetIndex()
        self.update()


        self.loadedGuiSettings = self.generateCurrentGuiSettings()
        return True


    def loadLineEdits(self):
        lineEditValueString = loadSetting(self.settingsFile,'lineEdits')
        if not lineEditValueString is None:
            if isinstance(lineEditValueString,str):
                print('Please save a new gui state to comply with the new version')
                return
            for item,value in lineEditValueString.items():
                try:
                    getattr(self.ui,item).setText(value)
                except AttributeError:
                    pass

    def getCurrentDirectory(self):
        return self.ui.DataSet_path_lineEdit.text()

    def setCurrentDirectory(self,folder):
        self.ui.DataSet_path_lineEdit.setText(folder)
        

    

    def resetProgressBarTimed(self):
        if self.current_timer:
            self.current_timer.stop()
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.resetProgressBar)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(3000)

def main():
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv) # Passing command line arguments to app

    class AppContextEmulator(object):
        def __init__(self,projectDirectory):
            self.projectDirectory = projectDirectory
            local_os = sys.platform

            if local_os.lower() == 'linux':
                local_os = 'linux'
            elif local_os.lower() == 'win32' or local_os.lower() == 'cygwin':
                local_os = 'windows'
            elif local_os.lower() == 'darwin':
                local_os = 'max'
            else:
                local_os = 'linux'

            self.os = local_os
            self.resourses = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','resources'))


        def get_resource(self,path):
            tryPath = os.path.join(self.resourses,'base',path)
            
            if os.path.exists(tryPath):
                return tryPath
            else:
                return os.path.join(self.resourses,self.os,path)
            
            

    appEmu = AppContextEmulator(__file__)

    window = MJOLNIRMainWindow(appEmu) # This window has to be closed for app to end
    window.show()

    app.exec_() 

if __name__ == '__main__':
    main()

    