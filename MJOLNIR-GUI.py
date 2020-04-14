

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


plt.ion()


from PyQt5 import QtWidgets, QtCore, QtGui, Qt

from MJOLNIR_GUI_ui import Ui_MainWindow  
from MJOLNIR_Data import GuiDataFile,GuiDataSet
from DataModels import DataSetModel,DataFileModel
from StateMachine import StateMachine
from GuiStates import empty,partial,raw,converted
from AboutDialog import AboutDialog
import sys

import functools

from _tools import loadSetting,updateSetting



####

def ProgressBarDecoratorArguments(runningText='Running',completedText='Completed',failedText='Failed',delayInSeconds=3):

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
                    return returnval
        
            self.setProgressBarValue(100)
            self.setProgressBarLabelText(completedText)
            QtCore.QTimer.singleShot(int(delayInSeconds*1000), self.resetProgressBar)
            return returnval
        return newFunc
    return ProgressBarDecorator


# Naming convention: WhereInGui_description_type
# Append _function if it is a function
# E.g.: View3D_plot_button and View3D_plot_button_function

#Headlines so far are:
#DataSet, View3D, QELine, QPlane, Cut1D,



class mywindow(QtWidgets.QMainWindow):

    def __init__(self):

        super(mywindow, self).__init__()

        self.ui = Ui_MainWindow()
    
        self.ui.setupUi(self)
        
        self.windows = []

        self.dataSets = []
        
        self.blockItems = [getattr(self.ui,item) for item in self.ui.__dict__ if '_button' in item[-7:]] # Collect all items to block on calls
        self.blockItems.append(self.ui.DataSet_binning_comboBox)
        self.setupDataSet() # Setup datasets with buttons and call functions
        self.setupDataFile() # Setup datafiles        

        self.setupDataSet_DataFile_labels()

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
        
        
        self.setupMenu()
        self.setupStateMachine()
        self.stateMachine.run()

        self.loadFolder() # Load last folder as default 

 
    @ProgressBarDecoratorArguments(runningText='Converting data files',completedText='Convertion Done')
    def DataSet_convertData_button_function(self):    
        #  Should add a check if a data set is selected
        if not self.stateMachine.requireStateByName('raw'):
            return False
        self.convert()

    def convert(self):
        binning=int(self.ui.DataSet_binning_comboBox.currentText())
        ds = self.DataSetModel.getCurrentDataSet()
        try:
            ds.convertDataFile(binning=binning,guiWindow=self)
        except AttributeError as e:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical,title='Error')
            msg.setText("Error")
            msg.setInformativeText(str(e))
            msg.resize(300,200)
            msg.exec_()

        self.DataFileModel.layoutChanged.emit()
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
    # Menu options
    #############################################################################   
    # def Menu_File_GenerateView3D_function(self):
        # f=fopen("View3D_script.py","w+")
        # f.write()
        
        
        
        
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
        
        currentFolder = self.ui.DataSet_path_lineEdit.text()
        if path.exists(currentFolder):
            folder=currentFolder
        else:
            folder = ""
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Open data Files", folder,"HDF (*.hdf);;NXS (*.nxs);;All Files (*)")
        if self.DataSetModel.getCurrentDatasetIndex() is None: # no dataset is currently selected
            self.DataSet_NewDataSet_button_function()
        self.DataFileModel.add(files,guiWindow=self)

        # Find the folder of the data files, using last data file
        folder = path.dirname(files[-1])
        self.setCurrentDirectory(folder)

        self.update()
        self.stateMachine.run()

    def setupMenu(self): # Set up all QActions and menus
        self.ui.actionExit.setIcon(QtGui.QIcon('Icons/icons/cross-button.png'))
        self.ui.actionExit.setToolTip('Exit the application') 
        self.ui.actionExit.triggered.connect(self.close)

        self.ui.actionAbout.setIcon(QtGui.QIcon('Icons/icons/question.png'))
        self.ui.actionAbout.setToolTip('Show About') 
        self.ui.actionAbout.triggered.connect(self.about)


        self.ui.actionSave_GUI_state.setIcon(QtGui.QIcon('Icons/icons/folder-save.png'))
        self.ui.actionSave_GUI_state.setToolTip('Save current Gui setup') 
        self.ui.actionSave_GUI_state.triggered.connect(self.saveCurrentGui)

        self.ui.actionLoad_GUI_state.setIcon(QtGui.QIcon('Icons/icons/folder--arrow.png'))
        self.ui.actionLoad_GUI_state.setToolTip('Load Gui setup') 
        self.ui.actionLoad_GUI_state.triggered.connect(self.loadGui)

        self.ui.actionGenerate_View3d_script.setIcon(QtGui.QIcon('Icons/icons/script-3D.png'))
        self.ui.actionGenerate_View3d_script.setToolTip('Generate 3D Script') 

        self.ui.actionGenerate_QELine_script.setIcon(QtGui.QIcon('Icons/icons/script-QE.png'))
        self.ui.actionGenerate_QELine_script.setToolTip('Generate QELine Script') 

        self.ui.actionGenerate_QPlane_script.setIcon(QtGui.QIcon('Icons/icons/script-QP.png'))
        self.ui.actionGenerate_QPlane_script.setToolTip('Generate QPlane Script') 

        self.ui.actionGenerate_1d_script.setIcon(QtGui.QIcon('Icons/icons/script-1D.png'))
        self.ui.actionGenerate_1d_script.setToolTip('Generate 3D Script') 

        self.ui.actionOpen_mask_gui.setIcon(QtGui.QIcon('Icons/icons/mask-open.png'))
        self.ui.actionOpen_mask_gui.setToolTip('Open Mask Gui') 

        self.ui.actionLoad_mask.setIcon(QtGui.QIcon('Icons/icons/mask-load.png'))
        self.ui.actionLoad_mask.setToolTip('Load Mask') 
        
        


    def setupDataSet_DataFile_labels(self): # Set up labels containing information on current data file
        self.DataFileLabels = [self.ui.DataSet_Temperature_label,self.ui.DataSet_MagneticField_label,self.ui.DataSet_SampleName_label,
                    self.ui.DataSet_ScanCommand_label,self.ui.DataSet_ScanType_label]
        self.DataFileLabelEntries = ['temperature','magneticField','sampleName','scanCommand','scanParameters']
        for label in self.DataFileLabels:
            label.defaultText = label.text()
            

    def updateDataFileLabels(self):
        df = self.DataFileModel.getCurrentDatafile()
        if df is None:
            for label in self.DataFileLabels:
                label.setText(label.defaultText)
        else:
            temperature = df.temperature
            if temperature is None:
                temperatureEntry = 'N/A'
            else:
                temperatureEntry = '{:.2f} [{:.2f} - {:.2f}]'.format(np.mean(temperature),np.min(temperature),np.max(temperature))

            magneticField = df.magneticField
            if magneticField is None:
                magneticFieldEntry = 'N/A'
            else:
                magneticFieldEntry = '{:.2f} [{:.2f} - {:.2f}]'.format(np.mean(magneticField,np.min(magneticField),np.max(magneticField)))

            sampleNameEntry = df.sample.name
            scanCommandEntry = df.scanCommand
            scanParameters = df.scanParameters
            scanParametersEntry = ', '.join(scanParameters)
            
            entries = [temperatureEntry,magneticFieldEntry,sampleNameEntry,scanCommandEntry,scanParametersEntry,scanParametersEntry]

            for label,entry in zip(self.DataFileLabels,entries):
                label.setText(label.defaultText+': '+entry)
            
    def setProgressBarValue(self,value):
        self.ui.progressBar.setValue(value)

    def setProgressBarLabelText(self,text):
        self.ui.progressBar_label.setText(text)

    def setProgressBarMaximum(self,value):
        self.ui.progressBar.setMaximum(value)

    def resetProgressBar(self):
        self.setProgressBarValue(0)
        self.setProgressBarLabelText('Ready')


    def closeEvent(self, event):
        
        if hasattr(self,'windows'):
            for window in self.windows:
                try:
                    plt.close(window)
                except:
                    pass
        
        if self.DataSetModel.rowCount(None)>0: # If no data, save only folder
            self.saveCurrentGui()
        else:
            self.saveCurrentFolder()

    def about(self):
        dialog = AboutDialog('About.txt')
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
            localstring = [df.fileLocation for df in ds]
            localstring.insert(0,ds.name)
            saveString.append(' '.join(localstring))
            self.setProgressBarValue((i+1))

        dataSetString = ':'.join(saveString)
        
        updateSetting('dataSet',dataSetString)

        self.saveCurrentFolder()

    def saveCurrentFolder(self):
        fileDir = self.getCurrentDirectory()
        updateSetting('fileDir',fileDir)


    def loadFolder(self):
        fileDir = loadSetting('fileDir')
        if not fileDir is None:
            self.setCurrentDirectory(fileDir)


    @ProgressBarDecoratorArguments(runningText='Loading gui settings',completedText='Loading Done')
    def loadGui(self):
        dataSetString = loadSetting('dataSet')
        
        
        lines = dataSetString.split(':')
        totalFiles = len(dataSetString.split(' ')) # Get estimate of total number of data files
        self.setProgressBarMaximum(totalFiles)
        counter = 0

        for line in lines:
            
            DSName,*files = line.split(' ')
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
            
        
        self.loadFolder()
        pass

    def getCurrentDirectory(self):
        return self.ui.DataSet_path_lineEdit.text()

    def setCurrentDirectory(self,folder):
        self.ui.DataSet_path_lineEdit.setText(folder)


# def run():

    
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    application = mywindow()
    
    application.show()
    
    sys.exit(app.exec_())
