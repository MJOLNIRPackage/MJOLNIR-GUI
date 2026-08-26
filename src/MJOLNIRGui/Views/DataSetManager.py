import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python.DataModels import DataSetModel,SelectionModel,DataFileModel,DataFileInfoModel,settings
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile,GuiDataSet
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments,loadUI
except ImportError:
    from DataModels import DataSetModel,SelectionModel,DataFileModel,DataFileInfoModel,settings
    from MJOLNIR_Data import GuiDataFile,GuiDataSet
    from _tools import ProgressBarDecoratorArguments,loadUI

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.Qt import QApplication
from MJOLNIR.Data import DataFile
import numpy as np
from os import path

def setupDataSet(self): # Set up main features for Gui regarding the dataset widgets
    self.ui.DataSet_convertData_button.clicked.connect(self.DataSet_convertData_button_function)
    self.ui.DataSet_convertData_button.setToolTip('Convert selected Dataset')
    self.ui.DataSet_convertData_button.setStatusTip(self.ui.DataSet_convertData_button.toolTip())

    self.ui.DataSet_NewDataSet_button.clicked.connect(self.DataSet_NewDataSet_button_function)
    self.ui.DataSet_NewDataSet_button.setShortcut("Ctrl+N")
    self.ui.DataSet_NewDataSet_button.setToolTip('Add new Dataset')
    self.ui.DataSet_NewDataSet_button.setStatusTip(self.ui.DataSet_NewDataSet_button.toolTip())

    self.ui.DataSet_DeleteDataSet_button.clicked.connect(self.DataSet_DeleteDataSet_button_function)
    self.ui.DataSet_DeleteDataSet_button.setToolTip('Delete selected Dataset')
    self.ui.DataSet_DeleteDataSet_button.setStatusTip(self.ui.DataSet_DeleteDataSet_button.toolTip())

    self.ui.DataSet_AddFiles_button.clicked.connect(self.DataSet_AddFiles_button_function)
    self.ui.DataSet_AddFiles_button.setShortcut("Ctrl+F")
    self.ui.DataSet_AddFiles_button.setToolTip('Add new Datafiles')
    self.ui.DataSet_AddFiles_button.setStatusTip(self.ui.DataSet_AddFiles_button.toolTip())

    self.DataSetModel = DataSetModel(dataSets=self.dataSets,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView,guiWindow=self)
    self.ui.DataSet_DataSets_listView.setModel(self.DataSetModel)
    self.ui.DataSet_DataSets_listView.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
    self.ui.DataSet_DataSets_listView.setDragDropOverwriteMode(False)

    self.DataSetSelectionModel = SelectionModel(self.DataSetModel)#self.ui.DataSet_DataSets_listView.selectionModel()
    self.DataSetModel.dragDropFinished.connect(self.DataSetSelectionModel.onModelItemsReordered)
    self.DataSetSelectionModel.selectionChanged.connect(self.selectedDataSetChanged)
    self.ui.DataSet_DataSets_listView.setSelectionModel(self.DataSetSelectionModel)
    
    def checkUpdatedName(self,index,*args):
        ds = self.model().data(index)
        suggestedName = self.model().generateValidName(ds)
        if not suggestedName == ds.name:
            ds.name = suggestedName
            self.model().layoutChanged.emit()

    self.ui.DataSet_DataSets_listView.dataChanged = checkUpdatedName

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
                delete.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/cross-button.png')))
                menu.addAction(delete)

                ds = gui.DataSetModel.data(idx[0],role = QtCore.Qt.ItemDataRole)
                if len(ds)>0:
                    currentDS = gui.DataSetModel.data(idx[0],role = QtCore.Qt.ItemDataRole)
                    if len(currentDS)!=0: # If it contains data files
                        if currentDS[0].instrument=='CAMEA': ## Only CAMEA data can be recallibrated
                            recalibrate = QtWidgets.QAction('Update Calibration')
                            recalibrate.setToolTip("Update calibration file(s)")
                            recalibrate.setStatusTip(recalibrate.toolTip())
                            recalibrate.triggered.connect(lambda: gui.DataSet_recalibrateFunction(gui,idx))
                            recalibrate.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/blue-document-resize.png')))
                            
                            menu.addAction(recalibrate)

                        sort = QtWidgets.QAction('Auto Sort')
                        sort.setToolTip("Sort data files according to ascending Ei, abs(2theta), scan dir, A3")
                        sort.setStatusTip(sort.toolTip())
                        def sorting(ds,gui):
                            ds.autoSort()
                            gui.DataSetModel.layoutChanged.emit()
                            gui.DataFileModel.layoutChanged.emit()
                        sort.triggered.connect(lambda: sorting(ds,gui))
                        sort.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/arrow-circle-double-135.png')))
                        
                        menu.addAction(sort)
                    if not ds._maskingObject is None: # A masking has been performed!
                        removeMasking = QtWidgets.QAction('Remove Masking')
                        removeMasking.setToolTip("Remove masking from dataset")
                        def removeMaskingFunction(gui,ds):
                            ds.removeMasking()
                            gui.DataSetModel.layoutChanged.emit()
                        removeMasking.setStatusTip(removeMasking.toolTip())
                        removeMasking.triggered.connect(lambda: removeMaskingFunction(gui,ds))
                        removeMasking.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/mask-cross.png')))
                        menu.addAction(removeMasking)

                return menu.exec_(position)

    self.ui.DataSet_DataSets_listView.contextMenuEvent = lambda event: contextMenu(self.ui.DataSet_DataSets_listView,event,self)

def setupDataFile(self): # Set up main features for Gui regarding the datafile widgets
    self.DataFileModel = DataFileModel(DataSet_filenames_listView=self.ui.DataSet_filenames_listView,dataSetModel=self.DataSetModel,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView,guiWindow=self)
    self.ui.DataSet_filenames_listView.setModel(self.DataFileModel)

    self.ui.DataSet_filenames_listView.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
    self.ui.DataSet_filenames_listView.setDragDropOverwriteMode(False)

    #self.DataFileSelectionModel = self.ui.DataSet_filenames_listView.selectionModel()
    self.DataFileSelectionModel = SelectionModel(self.DataFileModel)#self.ui.DataSet_DataSets_listView.selectionModel()
    self.DataFileModel.dragDropFinished.connect(self.DataFileSelectionModel.onModelItemsReordered)
    self.DataFileSelectionModel.selectionChanged.connect(self.selectedDataFileChanged)
    self.ui.DataSet_filenames_listView.setSelectionModel(self.DataFileSelectionModel)
    
    self.ui.DataSet_DeleteFiles_button.clicked.connect(self.DataSet_DeleteFiles_button_function)
    self.ui.DataSet_DeleteFiles_button.setToolTip('Delete selected Datafile')
    self.ui.DataSet_DeleteFiles_button.setStatusTip(self.ui.DataSet_DeleteFiles_button.toolTip())

    

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
                delete.setToolTip('Delete DataFile') 
                delete.setStatusTip(delete.toolTip())
                delete.triggered.connect(self.DataSet_DeleteFiles_button_function)
                delete.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/cross-button.png')))

                menu.addAction(delete)
                return menu.exec_(position)

    def dragEnterEvent(self, gui, event):
        gui.stateMachine.requireStateByName('Partial')
        if event.mimeData().hasUrls():
            # returns (path and file name, '.'+extension)
            check = [path.splitext(u.toLocalFile())[1][1:] in DataFile.supportedRawFormats for u in event.mimeData().urls()]
            if np.all(check):
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, gui, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        gui._tempFiles = files
        gui.DataSet_AddFiles_Decorated()
        

    self.ui.DataSet_filenames_listView.dragEnterEvent = lambda event: dragEnterEvent(self.ui.DataSet_filenames_listView.dragEnterEvent,self,event)
    self.ui.DataSet_filenames_listView.dropEvent = lambda event: dropEvent(self.ui.DataSet_filenames_listView.dragEnterEvent,self,event)

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
    idx = self.DataSetModel.getCurrentDatasetIndex()
    self.ui.DataSet_DataSets_listView.edit(idx)
    self.update()
    self.stateMachine.run()

def DataSet_DeleteDataSet_button_function(self):
    idx = self.ui.DataSet_DataSets_listView.selectedIndexes()[0]
    self.DataSetModel.delete(idx)
    self.DataSetModel.layoutChanged.emit()
    self.DataFileModel.layoutChanged.emit()
    self.stateMachine.run()
    
def DataSet_DeleteFiles_button_function(self):
    self.DataFileModel.delete()
    self.stateMachine.run()

@ProgressBarDecoratorArguments(runningText='Adding Data Files',completedText='Data Files Added')
def DataSet_AddFiles_button_function(self):
    if not self.stateMachine.requireStateByName('Partial'):
        return False
    folder = self.currentFolder
    ## generate string for raw, converted, and all files
    allowedRawFilesString = 'Raw ('+' '.join(['*.'+str(x) for x in DataFile.supportedRawFormats])+')'
    allowedConvertedFilesString = 'Converted ('+' '.join(['*.'+str(x) for x in DataFile.supportedConvertedFormats])+')'
    allowedAllFilesString = 'All Files (*)'
    
    allowedString = ';;'.join([allowedRawFilesString,allowedConvertedFilesString,allowedAllFilesString])
    files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Open data Files", folder,allowedString)
    return self.DataSet_AddFiles(files)

def DataSet_AddFiles(self,files):
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
def DataSet_AddFiles_Decorated(self):
    return self.DataSet_AddFiles(self._tempFiles)

@ProgressBarDecoratorArguments(runningText='Converting data files',completedText='Conversion Done')
def DataSet_convertData_button_function(self):    
    #  Should add a check if a data set is selected
    if not self.stateMachine.requireStateByName('Raw'):
        return False
    
    val = self.convert()
    self.DataFileModel.layoutChanged.emit()
    self.DataFileInfoModel.layoutChanged.emit()
    return val
    

def recalibrateFunction(gui,idx):
    folder = gui.currentFolder
    calibrationFiles, _ = QtWidgets.QFileDialog.getOpenFileNames(gui,"Open Calibration File(s)", folder,"calbiration (*.calib);;All Files (*)")
    
    # Find the folder of the data files, using last data file
    if len(calibrationFiles)==0:
        return False
    folder = path.dirname(calibrationFiles[-1])
    gui.setCurrentDirectory(folder)

    ds = gui.DataSetModel.data(idx[0],role = QtCore.Qt.ItemDataRole)
    
    length = len(ds)+1 # Files + 1 for loading of calibration files
    gui.setProgressBarMaximum(length)
    progress = 0
    gui.setProgressBarValue(progress)
    gui.setProgressBarLabelText('Loading calibration file'+'s'*(len(calibrationFiles)>1))
    ds.updateCalibration(calibrationFiles,overwrite=True)
    progress += 1
    gui.setProgressBarValue(progress)

    files = []
    dataSetName = ds.name
    gui.setProgressBarLabelText('Updating calibration')
    for d in ds:
        files.append(d.fileLocation)
        d.saveHDF(d.fileLocation)
        progress += 1
        gui.setProgressBarValue(progress)

    gui.DataSetModel.delete(idx[0])

    ds = GuiDataSet(name=dataSetName)
    gui.setProgressBarLabelText('Reloading data file'+'s'*(len(files)>1))
    gui.DataSetModel.append(ds)
    gui.DataFileModel.add(files,guiWindow=gui)
    gui.setProgressBarLabelText('Calibration Updated')
    gui.update()
    gui.resetProgressBarTimed()
    return True
    
def convert(self):
    ds = self.DataSetModel.getCurrentDataSet()
    idx = self.ui.DataSet_binning_comboBox.currentIndex()
    binning = int(self.ui.DataSet_binning_comboBox.itemText(idx))
    try:
        ds.convertDataFile(guiWindow=self,printFunction=self.writeToStatus,deleteOnConvert=True,binning=binning)
    except AttributeError as e:
        dialog = QtWidgets.QMessageBox()
        dialog.setIcon(QtWidgets.QMessageBox.Critical)
        dialog.setText('It is not possible to convert data file:')
        
        dialog.setInformativeText(str(e))
        dialog.addButton(QtWidgets.QMessageBox.Ok)
        
        dialog.exec_()
    
    self.DataSetModel.layoutChanged.emit()
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

def DataSet_DataFileInfo_copy(self,idx,clipboard=True):
    """Copy text in currently selected item to either clipboard or log"""
    
    text = self.DataFileInfoModel.data(idx,QtCore.Qt.DisplayRole)
    if clipboard:
        QApplication.clipboard().setText(text)
    else:
        self.writeToStatus(text)
    
def DataSet_DataFileInfo_remove(self,idx):
    currentInfos = self.DataFileInfoModel.infos
    del currentInfos[idx.row()]
    self.DataFileInfoModel.layoutChanged.emit()
    

def setupDataFileInfoModel(self):
    
    self.DataFileInfoModel.infos = [x for x in settings.keys()]#['sample/name','A3','A4','magneticField','temperature','scanCommand','scanParameters','comment','binning']
    def contextMenuDataFilesInfo(view,event,gui):
        # Generate a context menu that opens on right click
        
        position = event.globalPos()
        idx = view.currentIndex()
        if idx is None:
            return
        if idx.row()>=self.DataFileInfoModel.rowCount(None):
            return
    
        if event.type() == QtCore.QEvent.ContextMenu:
            menu = QtWidgets.QMenu()
            copyCB = QtWidgets.QAction('Copy to clipboard')
            copyCB.setToolTip('Copy Current information to clipboard') 
            copyCB.setStatusTip(copyCB.toolTip())
            copyCB.triggered.connect(lambda: self.DataSet_DataFileInfo_copy(idx,clipboard=True))

            copyLog = QtWidgets.QAction('Copy to log')
            copyLog.setToolTip('Copy Current information to log') 
            copyLog.setStatusTip(copyLog.toolTip())
            copyLog.triggered.connect(lambda: self.DataSet_DataFileInfo_copy(idx,clipboard=False))

            currentInfo = self.DataFileInfoModel.infos[idx.row()].baseText.split(':')[0] # base text has ': ' at the end
            removeInfo = QtWidgets.QAction("Remove '{}'".format(currentInfo))
            removeInfo.setToolTip("Remove '{}' from overview".format(currentInfo)) 
            removeInfo.setStatusTip(removeInfo.toolTip())
            removeInfo.triggered.connect(lambda: self.DataSet_DataFileInfo_remove(idx))

            

            menu.addAction(copyCB)
            menu.addAction(copyLog)
            menu.addAction(removeInfo)
            return menu.exec_(position)
    self.ui.DataSet_fileAttributs_listView.contextMenuEvent = lambda event: contextMenuDataFilesInfo(self.ui.DataSet_fileAttributs_listView,event,self)


DataSetManagerBase, DataSetManagerForm = loadUI('loadFile.ui')
       
        
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

        self.guiWindow.DataSet_AddFiles_button_function = lambda: DataSet_AddFiles_button_function(self.guiWindow)
        self.guiWindow.DataSet_AddFiles = lambda files: DataSet_AddFiles(self.guiWindow,files)
        self.guiWindow.DataSet_recalibrateFunction = lambda gui,idx: recalibrateFunction(gui,idx=idx)
        self.guiWindow.DataSet_AddFiles_Decorated = lambda : DataSet_AddFiles_Decorated(self.guiWindow)

        self.guiWindow.DataSet_convertData_button_function = lambda: DataSet_convertData_button_function(self.guiWindow)
        self.guiWindow.convert = lambda: convert(self.guiWindow)

        self.guiWindow.updateDataFileLabels = lambda: updateDataFileLabels(self.guiWindow)

        self.guiWindow.setupDataSet = lambda:setupDataSet(self.guiWindow)
        self.guiWindow.setupDataFile =  lambda:setupDataFile(self.guiWindow)
        self.guiWindow.setupDataFileInfoModel = lambda:setupDataFileInfoModel(self.guiWindow)
        self.guiWindow.DataSet_DataFileInfo_copy = lambda idx,clipboard:DataSet_DataFileInfo_copy(self.guiWindow,idx,clipboard)
        self.guiWindow.DataSet_DataFileInfo_remove = lambda idx: DataSet_DataFileInfo_remove(self.guiWindow, idx)
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