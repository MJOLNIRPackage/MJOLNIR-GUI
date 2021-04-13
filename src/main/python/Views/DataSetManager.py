import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python.DataModels import DataSetModel,DataFileModel,DataFileInfoModel,settings
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile,GuiDataSet
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
except ImportError:
    from DataModels import DataSetModel,DataFileModel,DataFileInfoModel,settings
    from MJOLNIR_Data import GuiDataFile,GuiDataSet
    from _tools import ProgressBarDecoratorArguments


from os import path
from PyQt5 import QtWidgets,uic, QtCore, QtGui
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

    def deleteFunction(self,gui,idx):
        gui.DataSetModel.delete(idx[0])
        self.DataFileModel.layoutChanged.emit()
        self.stateMachine.run()

    def contextMenu(view,event,gui):
        # Generate a context menu that opens on right click
        position = event.globalPos()
        idx = view.selectedIndexes()
        if len(idx)!=0:
            if event.type() == QtCore.QEvent.ContextMenu:
                menu = QtWidgets.QMenu()
                delete = QtWidgets.QAction('Delete')
                delete.setToolTip('Delete DataSet') 
                delete.setStatusTip(delete.toolTip())
                delete.triggered.connect(lambda: deleteFunction(self,gui,idx))

                menu.addAction(delete)
                return menu.exec_(position)

    self.ui.DataSet_DataSets_listView.contextMenuEvent = lambda event: contextMenu(self.ui.DataSet_DataSets_listView,event,self)

def setupDataFile(self): # Set up main features for Gui regarding the datafile widgets
    self.DataFileModel = DataFileModel(DataSet_filenames_listView=self.ui.DataSet_filenames_listView,dataSetModel=self.DataSetModel,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView,guiWindow=self)
    self.ui.DataSet_filenames_listView.setModel(self.DataFileModel)

    self.DataFileSelectionModel = self.ui.DataSet_filenames_listView.selectionModel()
    self.DataFileSelectionModel.selectionChanged.connect(self.selectedDataFileChanged)
    
    self.ui.DataSet_DeleteFiles_button.clicked.connect(self.DataSet_DeleteFiles_button_function)
    self.ui.DataSet_DeleteFiles_button.setToolTip('Delete selected Datafile')
    self.ui.DataSet_DeleteFiles_button.setStatusTip(self.ui.DataSet_DeleteFiles_button.toolTip())

    self.ui.DataSet_DataSets_listView.doubleClicked.connect(self.DataFile_DoubleClick_Selection_function)

    self.DataFileInfoModel = DataFileInfoModel(DataSet_filenames_listView=self.ui.DataSet_filenames_listView,dataSetModel=self.DataSetModel,
    DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView,dataFileModel=self.DataFileModel,guiWindow=self)
    self.setupDataFileInfoModel()
    self.ui.DataSet_fileAttributs_listView.setModel(self.DataFileInfoModel)

    def contextMenuDataFiles(view,event,gui):
        # Generate a context menu that opens on right click
        position = event.globalPos()
        idx = view.selectedIndexes()
        if len(idx)!=0:
            if event.type() == QtCore.QEvent.ContextMenu:
                menu = QtWidgets.QMenu()
                delete = QtWidgets.QAction('Delete')
                delete.setToolTip('Delete DataSet') 
                delete.setStatusTip(delete.toolTip())
                delete.triggered.connect(self.DataSet_DeleteFiles_button_function)

                menu.addAction(delete)
                return menu.exec_(position)

    self.ui.DataSet_filenames_listView.contextMenuEvent = lambda event: contextMenuDataFiles(self.ui.DataSet_filenames_listView,event,self)
    

def setupDataSet_binning_comboBox(self):
    self.ui.DataSet_binning_comboBox.reset = lambda:DataSet_binning_comboBoxReset(self.ui.DataSet_binning_comboBox)
    self.ui.DataSet_binning_comboBox.reset()
    self.ui.DataSet_binning_comboBox.activated.connect(self.DataSet_binning_comboBox_Changed)

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
    #ds.currentNormalizationSettings.update(normalizationParams)

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
    if len(files)==0:
        return False
    folder = path.dirname(files[-1])
    self.setCurrentDirectory(folder)

    self.update()
    self.stateMachine.run()
    return True

@ProgressBarDecoratorArguments(runningText='Converting data files',completedText='Conversion Done')
def DataSet_convertData_button_function(self):    
    #  Should add a check if a data set is selected
    
    if not self.stateMachine.requireStateByName('Raw'):
        return False
    
    val = self.convert()
    self.DataFileModel.layoutChanged.emit()
    self.DataFileInfoModel.layoutChanged.emit()
    return val
    
    
def convert(self):
    ds = self.DataSetModel.getCurrentDataSet()
    
    try:
        ds.convertDataFile(guiWindow=self)
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
    


def updateDataFileLabels(self):
    self.DataFileInfoModel.layoutChanged.emit()
    self.updateRaw1DCutSpinBoxes()
    self.updateBinningComboBox()

def DataSet_binning_comboBox_Changed(self):
    idx = self.ui.DataSet_binning_comboBox.currentIndex()
    newValue = int(self.ui.DataSet_binning_comboBox.itemText(idx))
    
    dfs = self.DataFileModel.getCurrentDatafiles(raw=True)
    if dfs  is None:
        dfs  = self.DataFileModel.getData() #If all or non are chosen, update all
    
    for df in dfs:
        if newValue == df.binning:
            continue

        df.binning = newValue
    self.updateDataFileLabels()

def updateBinningComboBox(self):
    dfs = self.DataFileModel.getCurrentDatafiles(raw=True)
    self.ui.DataSet_binning_comboBox.reset()
    if dfs is None:
        dfs = self.DataFileModel.getData()
    if len(dfs)==0:
        return
    possibleBinnings = set(dfs[0].possibleBinnings.copy())
    if len(dfs)>1:
        for df in dfs[1:]:
            possibleBinnings = possibleBinnings & set(df.possibleBinnings)

    possibleBinnings = list(np.sort(list(possibleBinnings)))
    self.ui.DataSet_binning_comboBox.addItems([str(b) for b in possibleBinnings])
    binning = dfs[0].binning
    idx = possibleBinnings.index(binning)
    
    self.ui.DataSet_binning_comboBox.setCurrentIndex(idx)

def DataSet_binning_comboBoxReset(self):
    values = self.count()
    for _ in range(values):
        self.removeItem(0)

############### Setup of info panel

def setupDataFileInfoModel(self):
    
    self.DataFileInfoModel.infos = [x for x in settings.keys()]#['sample/name','A3','A4','magneticField','temperature','scanCommand','scanParameters','comment','binning']
    


try:
    # needed when freezing app
    DataSetManagerBase, DataSetManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"loadFile.ui"))
    
except:
    try:
        # needed when running app local through fbs
        DataSetManagerBase, DataSetManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"loadFile.ui"))
        
    except:
        # needed when running app after pip install
        DataSetManagerBase, DataSetManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"loadFile.ui"))
        
        
class DataSetManager(DataSetManagerBase, DataSetManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(DataSetManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initDataSetManager()

    def initDataSetManager(self):
    
        self.guiWindow.selectedDataSetChanged = lambda:selectedDataSetChanged(self.guiWindow)
        self.guiWindow.selectedDataFileChanged = lambda:selectedDataFileChanged(self.guiWindow)
        self.guiWindow.DataSet_NewDataSet_button_function = lambda:DataSet_NewDataSet_button_function(self.guiWindow)
        self.guiWindow.DataSet_DeleteDataSet_button_function = lambda:DataSet_DeleteDataSet_button_function(self.guiWindow)
        self.guiWindow.DataSet_DeleteFiles_button_function = lambda:DataSet_DeleteFiles_button_function(self.guiWindow)
        self.guiWindow.DataSet_DoubleClick_Selection_function = lambda index:DataSet_DoubleClick_Selection_function(self.guiWindow,index)
        self.guiWindow.DataFile_DoubleClick_Selection_function = lambda index:DataFile_DoubleClick_Selection_function(self.guiWindow,index)

        self.guiWindow.DataSet_AddFiles_button_function = lambda: DataSet_AddFiles_button_function(self.guiWindow)

        self.guiWindow.DataSet_convertData_button_function = lambda: DataSet_convertData_button_function(self.guiWindow)
        self.guiWindow.convert = lambda: convert(self.guiWindow)

        self.guiWindow.updateDataFileLabels = lambda: updateDataFileLabels(self.guiWindow)

        self.guiWindow.setupDataSet = lambda:setupDataSet(self.guiWindow)
        self.guiWindow.setupDataFile =  lambda:setupDataFile(self.guiWindow)
        self.guiWindow.setupDataFileInfoModel = lambda:setupDataFileInfoModel(self.guiWindow)
        self.guiWindow.setupDataSet_binning_comboBox = lambda:setupDataSet_binning_comboBox(self.guiWindow)
        self.guiWindow.updateBinningComboBox = lambda: updateBinningComboBox(self.guiWindow)
        self.guiWindow.DataSet_binning_comboBox_Changed = lambda:DataSet_binning_comboBox_Changed(self.guiWindow)
        
        
        for key,value in self.__dict__.items():
            if 'DataSet' in key:
                self.guiWindow.ui.__dict__[key] = value



    def setup(self):
        self.guiWindow.setupDataSet() # Setup datasets with buttons and call functions
        self.guiWindow.setupDataFile() # Setup datafiles      
        self.guiWindow.setupRaw1DCutSpinBoxes()
        self.guiWindow.setupDataSet_binning_comboBox()

        self.guiWindow.mask_changed.connect(self.testCall)

    @QtCore.pyqtSlot()
    def testCall(self):
        mask = self.guiWindow.maskingManager.getMasks()
        print('There was a change to the masking and I received a signal with the new mask ',mask)
        currentDS = self.guiWindow.DataSetModel.getCurrentDataSet()
        if not currentDS is None:
            currentDS.mask = mask