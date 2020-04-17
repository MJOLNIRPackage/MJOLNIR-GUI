try:
    import IPython
    shell = IPython.get_ipython()
    shell.enable_matplotlib(gui='qt')
except:
    pass


from MJOLNIR import _tools # Usefull tools useful across MJOLNIR
import numpy as np
import matplotlib.pyplot as plt

from os import path
import os


plt.ion()
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from MJOLNIR_GUI_ui import Ui_MainWindow  
from MJOLNIR_Data import GuiDataFile,GuiDataSet
from DataModels import DataSetModel,DataFileModel
from StateMachine import StateMachine
from GuiStates import empty,partial,raw,converted
from AboutDialog import AboutDialog
from HelpDialog import HelpDialog
from generateScripts import generateViewer3DScript

import sys

import functools

from _tools import loadSetting,updateSetting

from pathlib import Path
home = str(Path.home())

seperator1 = '|'
seperator2 = '*'

####

def ProgressBarDecoratorArguments(runningText='Running',completedText='Completed',failedText='Failed'):

    def ProgressBarDecorator(func):
        @functools.wraps(func)
        def newFunc(self,*args,**kwargs):
            self.setProgressBarValue(0)
            self.setProgressBarLabelText(runningText)
            if len(args) == 1:
                args = ()
            else:
                args = args[1:]
            self.update()
            returnval = func(self,*args,**kwargs)

            self.setProgressBarMaximum(100)
            if returnval is not None:
                if returnval is False:
                    self.setProgressBarValue(0)
                    self.setProgressBarLabelText(failedText)
                    self.resetProgressBarTimed()
                    return returnval
        
            self.setProgressBarValue(100)
            self.setProgressBarLabelText(completedText)
            self.resetProgressBarTimed()
            return returnval
        return newFunc
    return ProgressBarDecorator


# Naming convention: WhereInGui_description_type
# Append _function if it is a function
# E.g.: View3D_plot_button and View3D_plot_button_function

#Headlines so far are:
#DataSet, View3D, QELine, QPlane, Cut1D,



class mywindow(QtWidgets.QMainWindow):

    def __init__(self,AppContext):

        super(mywindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.AppContext = AppContext
        self.settingsFile = path.join(home,'.MJOLNIRGuiSettings')
    
        self.ui.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.AppContext.get_resource('Icons/Own/MJOLNIR.png')))
        self.setWindowIcon(icon)
        
        self.windows = []

        self.dataSets = []

        self.current_timer = None
        
        self.blockItems = [getattr(self.ui,item) for item in self.ui.__dict__ if '_button' in item[-7:]] # Collect all items to block on calls
        self.blockItems.append(self.ui.DataSet_binning_comboBox)

        self.lineEdits = [getattr(self.ui,item) for item in self.ui.__dict__ if '_lineEdit' in item[-9:]] # Collect all items to block on calls

        self.setupDataSet() # Setup datasets with buttons and call functions
        self.setupDataFile() # Setup datafiles        

        self.setupDataSet_DataFile_labels()
        self.setupRaw1DCutSpinBoxes()

        ##############################################################################
        # View3D
        ##############################################################################       
        self.ui.View3D_plot_button.clicked.connect(self.View3D_plot_button_function)
        self.ui.View3D_setCAxis_button.clicked.connect(self.View3D_setCAxis_button_function)
        self.ui.View3D_SetTitle_button.clicked.connect(self.View3D_SetTitle_button_function)
        
        # Radiobutton to select viewing type
        self.ui.View3D_SelectView_QxE_radioButton.clicked.connect(self.View3D_SelectView_QxE_radioButton_function)
        self.ui.View3D_SelectView_QyE_radioButton.clicked.connect(self.View3D_SelectView_QyE_radioButton_function)
        self.ui.View3D_SelectView_QxQy_radioButton.clicked.connect(self.View3D_SelectView_QxQy_radioButton_function)

        ##############################################################################
        # QELine
        ##############################################################################
        self.ui.QELine_plot_button.clicked.connect(self.QELine_plot_button_function)
        self.ui.QELine_setCAxis_button.clicked.connect(self.QELine_setCAxis_button_function)
        self.ui.QELine_SetTitle_button.clicked.connect(self.QELine_SetTitle_button_function)

        ##############################################################################
        # QPlane
        ##############################################################################
        self.ui.QPlane_plot_button.clicked.connect(self.QPlane_plot_button_function)
        self.ui.QPlane_setCAxis_button.clicked.connect(self.QPlane_setCAxis_button_function)
        self.ui.QPlane_SetTitle_button.clicked.connect(self.QPlane_SetTitle_button_function)


        ##############################################################################
        # Raw1Dcut
        ##############################################################################
        self.ui.Raw1D_plot_button.clicked.connect(self.Raw1D_plot_button_function)

        self.setupMenu()
        self.setupStateMachine()
        self.stateMachine.run()

        self.loadFolder() # Load last folder as default 
        self.loadLineEdits()

 
    @ProgressBarDecoratorArguments(runningText='Converting data files',completedText='Convertion Done')
    def DataSet_convertData_button_function(self):    
        #  Should add a check if a data set is selected
        
        if not self.stateMachine.requireStateByName('Raw'):
            return False
        
        return self.convert()
        
        
    def convert(self):
        binning=int(self.ui.DataSet_binning_comboBox.currentText())
        ds = self.DataSetModel.getCurrentDataSet()
        
        try:
            ds.convertDataFile(binning=binning,guiWindow=self)
        except AttributeError as e:
            dialog = QtWidgets.QMessageBox()
            dialog.setIcon(QtWidgets.QMessageBox.Critical)
            dialog.setText('It is not possible to convert data file:')
            
            dialog.setInformativeText(str(e))
            dialog.addButton(QtWidgets.QMessageBox.Ok)
            
            dialog.exec_()
        
        self.DataFileModel.layoutChanged.emit()
        self.stateMachine.run()
        return True
        #self.stateMachine.run()
        #ds.convertDataFile(binning=binning,saveFile=False)
                
    ##############################################################################
    # View3D
    ##############################################################################
        
    def View3D_setCAxis_button_function(self):
        if not hasattr(self, 'V'):
            self.View3D_plot_button_function()
            
        CAxisMin=float(self.ui.View3D_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.View3D_CAxisMax_lineEdit.text())
              
        self.V.caxis=(CAxisMin,CAxisMax)
    
    def View3D_SelectView_QxE_radioButton_function(self):
        if hasattr(self, 'V'):
            self.V.setAxis(1)
            # Redraw the title, then change the viewing plane to render properly
            self.View3D_SetTitle_button_function()
            self.V.setPlane(1)
            self.V.setPlane(0)
                
    def View3D_SelectView_QyE_radioButton_function(self):
        if hasattr(self, 'V'):
            self.V.setAxis(0)
            # Redraw the title, then change the viewing plane to render properly
            self.View3D_SetTitle_button_function()
            self.V.setPlane(1)
            self.V.setPlane(0)
        
    def View3D_SelectView_QxQy_radioButton_function(self):
        if hasattr(self, 'V'):
            self.V.setAxis(2)
            # Redraw the title, then change the viewing plane to render properly
            self.View3D_SetTitle_button_function()
            self.V.setPlane(1)
            self.V.setPlane(0)
        
    def View3D_SetTitle_button_function(self):        
        if hasattr(self, 'V'):
            TitleText=self.ui.View3D_SetTitle_lineEdit.text()        
            self.V.ax.set_title(TitleText)
            
            # Get the value of the slider right now, then change it around a bit and put it back to where it was, to render properly
            currentSliderValue=self.V.Energy_slider.val
            self.V.Energy_slider.set_val(0)
            self.V.Energy_slider.set_val(1)
            self.V.Energy_slider.set_val(currentSliderValue)
                    
    @ProgressBarDecoratorArguments(runningText='Generating View3D',completedText='View3D Generated')                    
    def View3D_plot_button_function(self):
        if not self.stateMachine.requireStateByName('Converted'):
            return False

        # Check if we already have data, otherwise convert current data.
        ds = self.DataSetModel.getCurrentDataSet()
        if len(ds.convertedFiles)==0:
            self.DataSet_convertData_button_function()
        
        QXBin=float(self.ui.View3D_QXBin_lineEdit.text())
        QYBin=float(self.ui.View3D_QYBin_lineEdit.text())
        EBin =float(self.ui.View3D_EBin_lineEdit.text())
        
        if self.ui.View3D_SelectUnits_RLU_radioButton.isChecked():
            rlu=True
            
        if self.ui.View3D_SelectUnits_AA_radioButton.isChecked():
            rlu=False

        if self.ui.View3D_Grid_checkBox.isChecked():
            grid=9
        else:
            grid=False
        
        if self.ui.View3D_LogScale_checkBox.isChecked():
            log=True
        else:
            log=False        
        
        self.V = ds.View3D(QXBin,QYBin,EBin,grid=grid,rlu=rlu,log=log)
        self.windows.append(self.V.ax.get_figure())
        
        # Select the correct view
        if self.ui.View3D_SelectView_QxE_radioButton.isChecked():
            self.View3D_SelectView_QyE_radioButton_function()
        if self.ui.View3D_SelectView_QyE_radioButton.isChecked():
            self.View3D_SelectView_QxE_radioButton_function()
        if self.ui.View3D_SelectView_QxQy_radioButton.isChecked():
            self.View3D_SelectView_QxQy_radioButton_function()
                    
        self.View3D_setCAxis_button_function()        
        self.View3D_SetTitle_button_function()
        self.V.setPlane(1)
        self.V.setPlane(0)
        return True
    ##############################################################################
        # QELine
    ##############################################################################
    @ProgressBarDecoratorArguments(runningText='Generating QELine plot',completedText='QELine plot generated')
    def QELine_plot_button_function(self):    
        # First check if we have data, otherwise convert data
        if not self.stateMachine.requireStateByName('Converted'):
            return False
        
        ds = self.DataSetModel.getCurrentDataSet()
        if len(ds.convertedFiles)==0:
            self.DataSet_convertData_button_function()
            
        # Get the Q points
        HStart=float(self.ui.QELine_HStart_lineEdit.text())
        KStart=float(self.ui.QELine_KStart_lineEdit.text())
        LStart=float(self.ui.QELine_LStart_lineEdit.text())
        
        HEnd=float(self.ui.QELine_HEnd_lineEdit.text())
        KEnd=float(self.ui.QELine_KEnd_lineEdit.text())
        LEnd=float(self.ui.QELine_LEnd_lineEdit.text())
                
        Q1 = np.array([HStart,KStart,LStart])
        Q2 = np.array([HEnd,KEnd,LEnd])
        # Collect them into one array
        QPoints = np.array([Q1,Q2])
        
        # Define orthogonal width and minimum pixel size along Q-cut
        width = float(self.ui.QELine_Width_lineEdit.text())   
        minPixel = float(self.ui.QELine_MinPixel_lineEdit.text()) 
 
        # Define energy bins
        EMin=float(self.ui.QELine_EMin_lineEdit.text())
        EMax=float(self.ui.QELine_EMax_lineEdit.text())
        NPoints=int(self.ui.QELine_NPoints_lineEdit.text())        
        EnergyBins=np.linspace(EMin,EMax,NPoints)

        # Check various plot settings
        if self.ui.QELine_SelectUnits_RLU_radioButton.isChecked():
            rlu=True
        else:
            rlu=False        

        if self.ui.QELine_LogScale_checkBox.isChecked():
            log=True
        else:
            log=False  
            
        if self.ui.QELine_ConstantBins_checkBox.isChecked():
            constantBins=True
        else:
            constantBins=False              
    
        # Make plot
        ax,DataLists,Bins,BinCenters,Offsets = \
        ds.plotCutQELine(QPoints=QPoints, width=width, \
                                     minPixel=minPixel, EnergyBins=EnergyBins,\
                                         rlu=rlu,log=log,constantBins=constantBins)

        # Make some final changes to the plot
        self.QELine=ax    
        fig = self.QELine.get_figure()
        fig.set_size_inches(8,6)

        if self.ui.QELine_Grid_checkBox.isChecked():
            ax.grid(True)
        else:
            ax.grid(False)
        
        self.QELine_setCAxis_button_function()

        self.windows.append(self.QELine.get_figure())
        self.QELine_SetTitle_button_function()

        return True


    def QELine_setCAxis_button_function(self):       
        CAxisMin=float(self.ui.QELine_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.QELine_CAxisMax_lineEdit.text())
        
        self.QELine.set_clim(CAxisMin,CAxisMax)
        fig = self.QELine.get_figure()
        fig.canvas.draw()

    def QELine_SetTitle_button_function(self):
        if hasattr(self, 'QELine'):
            TitleText=self.ui.QELine_SetTitle_lineEdit.text()        
            self.QELine.set_title(TitleText)
            fig = self.QELine.get_figure()
            fig.canvas.draw()

    ##############################################################################
    # QPlane
    ##############################################################################        
    def QPlane_plot_button_function(self):
        # Make plot
        if not self.stateMachine.requireStateByName('Converted'):
            return False
        ds = self.DataSetModel.getCurrentDataSet()
        if len(ds.convertedFiles)==0:
            self.DataSet_convertData_button_function()        
        
        # Check various plot settings
        if self.ui.QELine_SelectUnits_RLU_radioButton.isChecked():
            rlu=True
        else:
            rlu=False        

        if self.ui.QPlane_LogScale_checkBox.isChecked():
            log=True
        else:
            log=False          

        EMin=float(self.ui.QPlane_EMin_lineEdit.text())
        EMax=float(self.ui.QPlane_EMax_lineEdit.text())
        QxWidth = float(self.ui.QPlane_QxWidth_lineEdit.text())           
        QyWidth = float(self.ui.QPlane_QyWidth_lineEdit.text())           

        Data,Bins,ax = ds.plotQPlane(EMin=EMin, EMax=EMax,xBinTolerance=QxWidth,yBinTolerance=QyWidth,log=log,rlu=rlu)
        
        self.QPlane=ax    
        
        fig = self.QPlane.get_figure()
        fig.colorbar(ax.pmeshs[0])
        fig.set_size_inches(8,6)

        if self.ui.QPlane_Grid_checkBox.isChecked():
            ax.grid(True)
        else:
            ax.grid(False)
        
        self.QPlane_setCAxis_button_function()
        self.QPlane_SetTitle_button_function()
        self.windows.append(self.QPlane.get_figure())

        return True
        

    def QPlane_setCAxis_button_function(self):
        CAxisMin=float(self.ui.QPlane_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.QPlane_CAxisMax_lineEdit.text())

        self.QPlane.set_clim(CAxisMin,CAxisMax)
        fig = self.QPlane.get_figure()
        fig.canvas.draw()
        
    def QPlane_SetTitle_button_function(self):
        TitleText=self.ui.QPlane_SetTitle_lineEdit.text()        
        if hasattr(self, 'QPlane'):
            TitleText=self.ui.QPlane_SetTitle_lineEdit.text()        
            self.QPlane.set_title(TitleText)
            fig = self.QPlane.get_figure()
            fig.canvas.draw()
        
    ##############################################################################
    # DataSet
    ##############################################################################   
    def setupDataSet(self): # Set up main features for Gui regarding the dataset widgets
        self.ui.DataSet_convertData_button.clicked.connect(self.DataSet_convertData_button_function)
        self.ui.DataSet_convertData_button.setToolTip('Convert selected Dataset')
        self.ui.DataSet_convertData_button.setStatusTip(self.ui.DataSet_convertData_button.toolTip())

        self.ui.DataSet_NewDataSet_button.clicked.connect(self.DataSet_NewDataSet_button_function)
        self.ui.DataSet_NewDataSet_button.setToolTip('Add new Dataset')
        self.ui.DataSet_NewDataSet_button.setStatusTip(self.ui.DataSet_NewDataSet_button.toolTip())

        self.ui.DataSet_DeleteDataSet_button.clicked.connect(self.DataSet_DeleteDataSet_button_function)
        self.ui.DataSet_DeleteDataSet_button.setToolTip('Delete selected Dataset')
        self.ui.DataSet_DeleteDataSet_button.setStatusTip(self.ui.DataSet_DeleteDataSet_button.toolTip())

        self.ui.DataSet_AddFiles_button.clicked.connect(self.DataSet_AddFiles_button_function)
        self.ui.DataSet_AddFiles_button.setToolTip('Add new Datafiles')
        self.ui.DataSet_AddFiles_button.setStatusTip(self.ui.DataSet_AddFiles_button.toolTip())

        self.DataSetModel = DataSetModel(dataSets=self.dataSets,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView)
        self.ui.DataSet_DataSets_listView.setModel(self.DataSetModel)

        self.DataSetSelectionModel = self.ui.DataSet_DataSets_listView.selectionModel()
        self.DataSetSelectionModel.selectionChanged.connect(self.selectedDataSetChanged)
        
        self.ui.DataSet_DataSets_listView.doubleClicked.connect(self.DataSet_DoubleClick_Selection_function)

    def setupDataFile(self): # Set up main features for Gui regarding the datafile widgets
        self.DataFileModel = DataFileModel(DataSet_filenames_listView=self.ui.DataSet_filenames_listView,dataSetModel=self.DataSetModel,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView,guiWindow=self)
        self.ui.DataSet_filenames_listView.setModel(self.DataFileModel)

        self.DataFileSelectionModel = self.ui.DataSet_filenames_listView.selectionModel()
        self.DataFileSelectionModel.selectionChanged.connect(self.selectedDataFileChanged)
        
        self.ui.DataSet_DeleteFiles_button.clicked.connect(self.DataSet_DeleteFiles_button_function)
        self.ui.DataSet_DeleteFiles_button.setToolTip('Delete selected Datafile')
        self.ui.DataSet_DeleteFiles_button.setStatusTip(self.ui.DataSet_DeleteFiles_button.toolTip())

        self.ui.DataSet_DataSets_listView.doubleClicked.connect(self.DataFile_DoubleClick_Selection_function)

    def selectedDataSetChanged(self,*args,**kwargs):
        self.DataFileModel.updateCurrentDataSetIndex()
        self.selectedDataFileChanged()
        self.stateMachine.run()

    def selectedDataFileChanged(self,*args,**kwargs):
        self.DataFileModel.layoutChanged.emit()
        self.updateDataFileLabels()
        self.stateMachine.run()

    def DataSet_NewDataSet_button_function(self):
        ds = GuiDataSet(name='Added')
        self.DataSetModel.append(ds)
        self.update()
        self.stateMachine.run()

    def DataSet_DeleteDataSet_button_function(self):
        self.DataSetModel.delete(self.ui.DataSet_DataSets_listView.selectedIndexes()[0])
        self.DataFileModel.layoutChanged.emit()
        self.stateMachine.run()
        
    def DataSet_DeleteFiles_button_function(self):
        self.DataFileModel.delete()
        self.stateMachine.run()

    def DataSet_DoubleClick_Selection_function(self,index,*args,**kwargs):
        self.ui.DataSet_DataSets_listView.edit(index)

    def DataFile_DoubleClick_Selection_function(self,index,*args,**kwargs):
        self.ui.DataSet_filenames_listView.edit(index)

    @ProgressBarDecoratorArguments(runningText='Adding Data Files',completedText='Data Files Added')
    def DataSet_AddFiles_button_function(self):
        if not self.stateMachine.requireStateByName('Partial'):
            return False
        
        folder = self.getCurrentDirectory()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Open data Files", folder,"HDF (*.hdf);;NXS (*.nxs);;All Files (*)")
        if self.DataSetModel.getCurrentDatasetIndex() is None: # no dataset is currently selected
            self.DataSet_NewDataSet_button_function()
        self.DataFileModel.add(files,guiWindow=self)

        # Find the folder of the data files, using last data file
        folder = path.dirname(files[-1])
        self.setCurrentDirectory(folder)

        self.update()
        self.stateMachine.run()
        return True

    def setupMenu(self): # Set up all QActions and menus
        self.ui.actionExit.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/cross-button.png')))
        self.ui.actionExit.setToolTip('Exit the application') 
        self.ui.actionExit.setStatusTip(self.ui.actionExit.toolTip())
        self.ui.actionExit.triggered.connect(self.close)

        self.ui.actionAbout.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/information-button.png')))
        self.ui.actionAbout.setToolTip('Show About') 
        self.ui.actionAbout.setStatusTip(self.ui.actionAbout.toolTip())
        self.ui.actionAbout.triggered.connect(self.about)

        self.ui.actionHelp.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/question-button.png')))
        self.ui.actionHelp.setToolTip('Show Help') 
        self.ui.actionHelp.setStatusTip(self.ui.actionHelp.toolTip())
        self.ui.actionHelp.triggered.connect(self.help)


        self.ui.actionSave_GUI_state.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/folder-save.png')))
        self.ui.actionSave_GUI_state.setToolTip('Save current Gui setup') 
        self.ui.actionSave_GUI_state.setStatusTip(self.ui.actionSave_GUI_state.toolTip())
        self.ui.actionSave_GUI_state.triggered.connect(self.saveCurrentGui)

        self.ui.actionLoad_GUI_state.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/folder--arrow.png')))
        self.ui.actionLoad_GUI_state.setToolTip('Load Gui setup') 
        self.ui.actionLoad_GUI_state.setStatusTip(self.ui.actionLoad_GUI_state.toolTip())
        self.ui.actionLoad_GUI_state.triggered.connect(self.loadGui)

        self.ui.actionGenerate_View3d_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/script-3D.png')))
        self.ui.actionGenerate_View3d_script.setToolTip('Generate 3D Script') 
        self.ui.actionGenerate_View3d_script.setStatusTip(self.ui.actionGenerate_View3d_script.toolTip())
        self.ui.actionGenerate_View3d_script.triggered.connect(self.generate3DScript)

        self.ui.actionGenerate_QELine_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/script-QE.png')))
        self.ui.actionGenerate_QELine_script.setDisabled(True)
        self.ui.actionGenerate_QELine_script.setToolTip('Generate QELine Script - Not Implemented') 
        self.ui.actionGenerate_QELine_script.setStatusTip(self.ui.actionGenerate_QELine_script.toolTip())
        

        self.ui.actionGenerate_QPlane_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/script-QP.png')))
        self.ui.actionGenerate_QPlane_script.setDisabled(True)
        self.ui.actionGenerate_QPlane_script.setToolTip('Generate QPlane Script - Not Implemented') 
        self.ui.actionGenerate_QPlane_script.setStatusTip(self.ui.actionGenerate_QPlane_script.toolTip())
        

        self.ui.actionGenerate_1d_script.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/script-1D.png')))
        self.ui.actionGenerate_1d_script.setDisabled(True)
        self.ui.actionGenerate_1d_script.setToolTip('Generate 1D Script - Not Implemented') 
        self.ui.actionGenerate_1d_script.setStatusTip(self.ui.actionGenerate_1d_script.toolTip())
        

        self.ui.actionOpen_mask_gui.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/mask-open.png')))
        self.ui.actionOpen_mask_gui.setDisabled(True)
        self.ui.actionOpen_mask_gui.setToolTip('Open Mask Gui - Not Implemented') 
        self.ui.actionOpen_mask_gui.setStatusTip(self.ui.actionOpen_mask_gui.toolTip())
        

        self.ui.actionLoad_mask.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/icons/mask-load.png')))
        self.ui.actionLoad_mask.setDisabled(True)
        self.ui.actionLoad_mask.setToolTip('Load Mask - Not Implemented') 
        self.ui.actionLoad_mask.setStatusTip(self.ui.actionLoad_mask.toolTip())
        
        
        


    def setupDataSet_DataFile_labels(self): # Set up labels containing information on current data file
        self.DataFileLabels = [self.ui.DataSet_Temperature_label,self.ui.DataSet_MagneticField_label,self.ui.DataSet_SampleName_label,
                    self.ui.DataSet_ScanCommand_label,self.ui.DataSet_ScanType_label,self.ui.DataSet_A3_label,self.ui.DataSet_A4_label]
        self.DataFileLabelEntries = ['temperature','magneticField','sampleName','scanCommand','scanParameters','A3','A4']
        for label in self.DataFileLabels:
            label.defaultText = label.text()
            

    def updateDataFileLabels(self):
        dfs = self.DataFileModel.getCurrentDatafiles()
        if dfs is None:
            for label in self.DataFileLabels:
                label.setText(label.defaultText)
            self.updateRaw1DCutSpinBoxes()
        else:
            temperature = []
            A3 = []
            A4 = []
            magneticField = []
            sampleName = []
            scanCommand = []
            scanParameter = []

            formatString = '{:.2f} [{:.2f}  -  {:.2f}]'

            for df in dfs:
                temperature.append(df.temperature)
                A3.append(df.A3)
                A4.append(df.A4)
                magneticField.append(df.magneticField)

                sampleName.append(df.sample.name)
                scanCommand.append(df.scanCommand)
                scanParameter.append(df.scanParameters)
                
                
            if np.any([temp is None for temp in temperature]):
                temperatureEntry = 'N/A'
            else:
                conTemp = np.concatenate(temperature,axis=0)
                temperatureEntry = formatString.format(np.mean(conTemp),np.min(conTemp),np.max(conTemp))

            if np.any([a3 is None for a3 in A3]):
                A3Entry = 'N/A'
            else:
                conA3 = np.concatenate(A3,axis=0)
                A3Entry = formatString.format(np.mean(conA3),np.min(conA3),np.max(conA3))

            if np.any([a4 is None for a4 in A4]):
                A4Entry = 'N/A'
            else:
                conA4 = np.concatenate(A4,axis=0)
                A4Entry = formatString.format(np.mean(conA4),np.min(conA4),np.max(conA4))

            if np.any([magField is None for magField in magneticField]):
                magneticFieldEntry = 'N/A'
            else:
                conMagField = np.concatenate(magneticField,axis=0)
                magneticFieldEntry = formatString.format(np.mean(conMagField),np.min(conMagField),np.max(conMagField))
            
            sampleNameEntry = list(set(sampleName))[0]
            scanCommandEntry = path.commonprefix(scanCommand)
            scanParameters = list(set(np.array(scanParameter).flatten()))

            scanParametersEntry = ', '.join(scanParameters)

            entries = [temperatureEntry,magneticFieldEntry,sampleNameEntry,scanCommandEntry,scanParametersEntry,A3Entry,A4Entry]

            for label,entry in zip(self.DataFileLabels,entries):
                label.setText(label.defaultText+': '+entry)
        
            self.updateRaw1DCutSpinBoxes()
        
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

        
        ax = ds.plot1D()
        self.windows.append(ax)
        return True
        
    
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


    def closeEvent(self, event):
        res = QtWidgets.QMessageBox.question(self,
                                    "Exit - Save Gui Settings",
                                    "Do you want to save Gui Settings?",
                                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        
        
        if res == QtWidgets.QMessageBox.Save:
            self.saveCurrentGui()
            event.accept()
        elif res == QtWidgets.QMessageBox.No:
            self.saveCurrentFolder()
            event.accept()
        else:
            event.ignore()
            return


        if hasattr(self,'windows'):
            for window in self.windows:
                try:
                    plt.close(window)
                except:
                    pass

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
        
        saveString = []
        
        self.setProgressBarMaximum(len(self.DataSetModel.dataSets))

        for i,ds in enumerate(self.DataSetModel.dataSets):
            dsDict = {'name':ds.name}
            
            localstring = [df.fileLocation if df.type != 'nxs' else df.original_file.fileLocation for df in ds]
            dsDict['files']=localstring
            
            saveString.append(dsDict)
            self.setProgressBarValue((i+1))

        #dataSetString = seperator1.join(saveString)
        
        updateSetting(self.settingsFile,'dataSet',saveString)

        self.saveCurrentFolder()
        self.saveLineEdits()    

    def saveLineEdits(self):
        lineEditValueString = seperator1.join([seperator2.join([item.objectName(),item.text()]) for item in self.lineEdits])
        updateSetting(self.settingsFile,'lineEdits',lineEditValueString)

    def saveCurrentFolder(self):
        fileDir = self.getCurrentDirectory()
        updateSetting(self.settingsFile,'fileDir',fileDir)


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
            
        
        


        self.loadLineEdits()
        self.DataSetModel.layoutChanged.emit()
        self.DataFileModel.updateCurrentDataSetIndex()
        self.update()
        return True


    def loadLineEdits(self):
        lineEditValueString = loadSetting(self.settingsFile,'lineEdits')
        if not lineEditValueString is None:
            for item in lineEditValueString.split(':'):
                try:
                    name,value = item.split(seperator2)
                except:
                    continue
                try:
                    getattr(self.ui,name).setText(value)
                except AttributeError:
                    pass

    def getCurrentDirectory(self):
        return self.ui.DataSet_path_lineEdit.text()

    def setCurrentDirectory(self,folder):
        self.ui.DataSet_path_lineEdit.setText(folder)


    @ProgressBarDecoratorArguments(runningText='Genrating 3D Script',completedText='Script Saved',failedText='Cancelled')
    def generate3DScript(self):
        self.stateMachine.run()
        if not self.stateMachine.currentState.name in ['Raw','Converted']:
            dialog = QtWidgets.QMessageBox()
            dialog.setIcon(QtWidgets.QMessageBox.Critical)
            dialog.setText('It is not possible to generate a script without any data loaded.')
            dialog.addButton(QtWidgets.QMessageBox.Ok)
            dialog.exec() 

            return False

        folder = self.getCurrentDirectory()
        saveFile = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',folder,"Python (*.py)")[0]
        if len(saveFile)!=1:
            return False
        if path.splitext(saveFile)[1] !='.py':
            saveFile = path.splitext(saveFile)[0]+'.py'

        ds = self.DataSetModel.getCurrentDataSet()
        dataSetName = ds.name
        
        dataFiles = [df.original_file.fileLocation if hasattr(df,'original_file') else df.fileLocation for df in ds]

        binning = self.ui.DataSet_binning_comboBox.currentText()
        qx = self.ui.View3D_QXBin_lineEdit.text()
        qy = self.ui.View3D_QYBin_lineEdit.text()
        E = self.ui.View3D_EBin_lineEdit.text()

        CAxisMin = self.ui.View3D_CAxisMin_lineEdit.text()
        CAxisMax = self.ui.View3D_CAxisMax_lineEdit.text()

        log = self.ui.View3D_LogScale_checkBox.isChecked()
        grid = self.ui.View3D_Grid_checkBox.isChecked()

        title = self.ui.View3D_SetTitle_lineEdit.text()

        RLU = self.ui.View3D_SelectUnits_RLU_radioButton.isChecked()

        radioState = [self.ui.View3D_SelectView_QxE_radioButton.isChecked(),
        self.ui.View3D_SelectView_QyE_radioButton.isChecked(),self.ui.View3D_SelectView_QxQy_radioButton.isChecked()]
        selectView = np.arange(3)[radioState]
        selectView = selectView[0]

        generateViewer3DScript(saveFile=saveFile,dataFiles=dataFiles,dataSetName=dataSetName, binning=binning, qx=qx, qy=qy, E=E, 
                                    RLU=RLU, CAxisMin=CAxisMin, CAxisMax=CAxisMax, log=log, grid=grid,
                                    title=title, selectView=selectView)

        return True


    def resetProgressBarTimed(self):
        if self.current_timer:
            self.current_timer.stop()
        self.current_timer = QtCore.QTimer()
        self.current_timer.timeout.connect(self.resetProgressBar)
        self.current_timer.setSingleShot(True)
        self.current_timer.start(3000)


# def run():

    
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    application = mywindow()
    
    application.show()
    
    sys.exit(app.exec_())
