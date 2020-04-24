import sys
sys.path.append('..')

from DataModels import DataSetModel,DataFileModel
from MJOLNIR_Data import GuiDataFile,GuiDataSet
from _tools import ProgressBarDecoratorArguments

from os import path
from PyQt5 import QtWidgets
import numpy as np

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

def initDataSetManager(guiWindow):
 
    guiWindow.selectedDataSetChanged = lambda:selectedDataSetChanged(guiWindow)
    guiWindow.selectedDataFileChanged = lambda:selectedDataFileChanged(guiWindow)
    guiWindow.DataSet_NewDataSet_button_function = lambda:DataSet_NewDataSet_button_function(guiWindow)
    guiWindow.DataSet_DeleteDataSet_button_function = lambda:DataSet_DeleteDataSet_button_function(guiWindow)
    guiWindow.DataSet_DeleteFiles_button_function = lambda:DataSet_DeleteFiles_button_function(guiWindow)
    guiWindow.DataSet_DoubleClick_Selection_function = lambda index:DataSet_DoubleClick_Selection_function(guiWindow,index)
    guiWindow.DataFile_DoubleClick_Selection_function = lambda index:DataFile_DoubleClick_Selection_function(guiWindow,index)

    guiWindow.DataSet_AddFiles_button_function = lambda: DataSet_AddFiles_button_function(guiWindow)

    guiWindow.DataSet_convertData_button_function = lambda: DataSet_convertData_button_function(guiWindow)
    guiWindow.convert = lambda: convert(guiWindow)

    guiWindow.setupDataSet_DataFile_labels = lambda: setupDataSet_DataFile_labels(guiWindow)
    guiWindow.updateDataFileLabels = lambda: updateDataFileLabels(guiWindow)

    guiWindow.setupDataSet = lambda:setupDataSet(guiWindow)
    guiWindow.setupDataFile =  lambda:setupDataFile(guiWindow)



def setupDataSetManager(guiWindow):
    guiWindow.setupDataSet() # Setup datasets with buttons and call functions
    guiWindow.setupDataFile() # Setup datafiles      
    guiWindow.setupRaw1DCutSpinBoxes()
    guiWindow.setupDataSet_DataFile_labels()