from re import sub
import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python.DataModels import DataSetModel,SelectionModel,DataFileModel,DataFileInfoModel,subtractionSettings
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile,GuiDataSet
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments,loadUI
    from MJOLNIRGui.src.main.python.HelpDialog import HelpDialog
except ImportError:
    from DataModels import DataSetModel,SelectionModel,DataFileModel,DataFileInfoModel,subtractionSettings
    from MJOLNIR_Data import GuiDataFile,GuiDataSet
    from _tools import ProgressBarDecoratorArguments,loadUI
    from HelpDialog import HelpDialog


from os import path
from PyQt5 import QtWidgets,uic, QtCore, QtGui
from PyQt5.QtCore import Qt
import numpy as np
def subtractable(file1,file2,A3Precision=0.1,twothetaPrecision=0.1,EiPrecision=0.1):
    checked = {}
    checked['type'] = file1.type == file2.type
    checked['scanSteps'] = file1.I.shape == file2.I.shape
    if not file1.A3.shape ==  file2.A3.shape:
        checked['A3'] = False
    else:
        checked['A3'] = np.all(np.isclose(file1.A3,file2.A3,atol=A3Precision))
    checked['twotheta'] = np.all(np.isclose(file1.twotheta,file2.twotheta,atol=twothetaPrecision))
    checked['Ei'] = np.all(np.isclose(file1.Ei,file2.Ei,atol=EiPrecision))
    checked['scanParameters'] = file1.scanParameters == file2.scanParameters
    return checked

ValidColour =  QtGui.QColor(255, 255, 255, 0)
InvalidColour = QtGui.QColor(255, 0, 0, 120)

class DataSetDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        """Delegate colouring the background of data files with the BG colour given by df.BGColor, default is ValidColor"""
        QtWidgets.QStyledItemDelegate.__init__(self, parent, *args)


    def paint(self, painter, option, index):
        super(DataSetDelegate,self).paint(painter, option, index)
        if True:
            df = index.model().data(index,Qt.ItemDataRole)
            painter.save()
            painter.setPen(QtGui.QPen(Qt.NoPen))
            
            if not hasattr(df,'BGColor'): # No BG color given, assume Valid
                c = ValidColour
            else:
                c = df.BGColor
            painter.setBrush(QtGui.QBrush(c))

            # Draw the background rectangle            
            painter.drawRect(option.rect)
            painter.restore()

class DataFileDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        """Delegate colouring the background of data file properties depending on whether they match or not"""
        QtWidgets.QStyledItemDelegate.__init__(self, parent, *args)


    def paint(self, painter, option, index):
        super(DataFileDelegate,self).paint(painter, option, index)
        
        dataPropertyCheck = index.model().data(index,role=Qt.ItemDataRole)
    
        painter.save()
        painter.setPen(QtGui.QPen(Qt.NoPen))
        
        if dataPropertyCheck: # Check is successful
            c = ValidColour
        else:
            c = InvalidColour
        painter.setBrush(QtGui.QBrush(c))

        # Draw the background rectangle            
        painter.drawRect(option.rect)
        painter.restore()

SubtractionManagerBase, SubtractionManagerForm = loadUI('Subtraction.ui')



class SubtractionManager(SubtractionManagerBase, SubtractionManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(SubtractionManager, self).__init__(parent,QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint | \
            QtCore.Qt.WindowMinMaxButtonsHint )
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.setWindowIcon(QtGui.QIcon(self.guiWindow.AppContext.get_resource('Icons/Own/subtract.png')))
        self.initSubtractionManager()
        #self.guiWindow.subtractionHelp()

    def accept(self):
        if not self.Subtraction_generateSubtraction_button.isDisabled():
            self.Subtraction_generateSubtraction_button.clicked.emit()
            super(SubtractionManager,self).accept()
        
    

    def initSubtractionManager(self):

        self.Subtraction_dataSet_foreground_comboBox.setModel(self.guiWindow.DataSetModel)
        self.Subtraction_dataSet_background_comboBox.setModel(self.guiWindow.DataSetModel)

       
        self.Subtraction_dataSet_foreground_comboBox.oldIdx = -1
        self.Subtraction_dataSet_background_comboBox.oldIdx = -1

        if self.guiWindow.DataSetModel.rowCount(None)>1:
            self.Subtraction_dataSet_foreground_comboBox.setCurrentIndex(0)
            self.Subtraction_dataSet_foreground_comboBox.oldIdx = 0
            self.Subtraction_dataSet_background_comboBox.setCurrentIndex(1)
            self.Subtraction_dataSet_background_comboBox.oldIdx = 1

        self.Subtraction_dataSet_foreground_comboBox.currentIndexChanged.connect(lambda: self.comboboxChanged(foreground=True))
        self.Subtraction_dataSet_background_comboBox.currentIndexChanged.connect(lambda: self.comboboxChanged(foreground=False))
        
        
        self.DataFileModel_foreground = DataFileModel(self.Subtraction_filenames_foreground_listView,\
            dataSetModel=self.guiWindow.DataSetModel,DataSet_DataSets_listView=self.Subtraction_dataSet_foreground_comboBox,\
                guiWindow = self.guiWindow)

        # Set up model for foreground df view
        self.Subtraction_filenames_foreground_listView.setModel(self.DataFileModel_foreground)
        self.Subtraction_filenames_foreground_listView.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.Subtraction_filenames_foreground_listView.setDragDropOverwriteMode(False)

        dataSetDelegate = DataSetDelegate() # Painter for DataSet comparison
        dataFileDelegate = DataFileDelegate() # Painter for properties of data files

        self.Subtraction_filenames_foreground_listView.setItemDelegate(dataSetDelegate)
        self.Subtraction_filenames_background_listView.setItemDelegate(dataSetDelegate)

        self.Subtraction_fileAttributs_foreground_listView.setItemDelegate(dataFileDelegate)
        self.Subtraction_fileAttributs_background_listView.setItemDelegate(dataFileDelegate)
        

        # add selection model for smooth selection when drag/dropping
        self.DataFile_foreground_SelectionModel = SelectionModel(self.DataFileModel_foreground)
        
        
        self.Subtraction_filenames_foreground_listView.setSelectionModel(self.DataFile_foreground_SelectionModel)
        
        

        # add file information
        self.DataFile_foreground_infoModel = DataFileInfoModel(DataSet_filenames_listView=self.Subtraction_filenames_foreground_listView,dataSetModel=self.guiWindow.DataSetModel,
        DataSet_DataSets_listView=self.Subtraction_dataSet_foreground_comboBox,dataFileModel=self.DataFileModel_foreground,guiWindow=self.guiWindow)
        self.DataFile_foreground_infoModel.infos = [x for x in subtractionSettings.keys()]
        
        self.Subtraction_fileAttributs_foreground_listView.setModel(self.DataFile_foreground_infoModel)

        self.DataFileModel_foreground.dragDropFinished.connect(self.DataFile_foreground_SelectionModel.onModelItemsReordered)
        self.DataFile_foreground_SelectionModel.selectionChanged.connect(self.updateDataFileLabels)
        


        ##### Repeat above for background
        self.DataFileModel_background = DataFileModel(self.Subtraction_filenames_background_listView,\
            dataSetModel=self.guiWindow.DataSetModel,DataSet_DataSets_listView=self.Subtraction_dataSet_background_comboBox,\
                guiWindow = self.guiWindow)

        # Set up model for background df view
        self.Subtraction_filenames_background_listView.setModel(self.DataFileModel_background)
        self.Subtraction_filenames_background_listView.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.Subtraction_filenames_background_listView.setDragDropOverwriteMode(False)

        # add selection model for smooth selection when drag/dropping
        self.DataFile_background_SelectionModel = SelectionModel(self.DataFileModel_background)#self.ui.DataSet_DataSets_listView.selectionModel()
        self.DataFileModel_background.dragDropFinished.connect(self.DataFile_background_SelectionModel.onModelItemsReordered)
        self.DataFile_background_SelectionModel.selectionChanged.connect(self.updateDataFileLabels)
        self.Subtraction_filenames_background_listView.setSelectionModel(self.DataFile_background_SelectionModel)
        self.DataFileModel_foreground.dragDropFinished.connect(self.updateDataFileLabels)

        

        # add file information
        self.DataFile_background_infoModel = DataFileInfoModel(DataSet_filenames_listView=self.Subtraction_filenames_background_listView,dataSetModel=self.guiWindow.DataSetModel,
        DataSet_DataSets_listView=self.Subtraction_dataSet_background_comboBox,dataFileModel=self.DataFileModel_background,guiWindow=self.guiWindow)
        self.DataFile_background_infoModel.infos = [x for x in subtractionSettings.keys()]
        self.Subtraction_fileAttributs_background_listView.setModel(self.DataFile_background_infoModel)

        # Connect generation button with method
        self.Subtraction_generateSubtraction_button.clicked.connect(self.generateSubtracted)

        # Check DataSetName on finish editing
        self.Subtraction_dataSet_name_lineEdit.editingFinished.connect(self.checkDataSetName)
        # Call once to update naming from default
        self.checkDataSetName()
        self.checkDataSetCombability()

    def comboboxChanged(self,foreground=True):
        if foreground:
            self.DataFileModel_foreground.updateCurrentDataSetIndex()
        else:
            self.DataFileModel_background.updateCurrentDataSetIndex()
        self.updateDataFileLabels()


    def updateDataFileLabels(self):
        self.DataFile_foreground_infoModel.layoutChanged.emit()
        self.DataFile_background_infoModel.layoutChanged.emit()
        self.checkDataSetCombability()

    def generateSubtracted(self):
        foreground_ds = self.DataFileModel_foreground.getCurrentDataSet()
        background_ds = self.DataFileModel_background.getCurrentDataSet()
        
        temp = foreground_ds-background_ds
        subtracted_ds = GuiDataSet(dataSet=temp,name=self.Subtraction_dataSet_name_lineEdit.text())

        if background_ds[0].type == 'nxs': # If first file is converted
            subtracted_ds.background = [df.fileLocation for df in background_ds]
            subtracted_ds.convertBeforeSubtract = True
        else:    
            subtracted_ds.background = [df.fileLocation for df in background_ds]
            subtracted_ds.convertBeforeSubtract = False
        
        self.guiWindow.DataSetModel.append(subtracted_ds)
        self.close()
        

    def checkDataSetName(self):
        """If no name is given, simply return "subtracted" """
        if self.Subtraction_dataSet_name_lineEdit.text().strip() == '':
            self.Subtraction_dataSet_name_lineEdit.setText('Subtracted')

    def checkDataSetCombability(self,*args,**kwargs):
        if self.DataFileModel_foreground.rowCount(None)==0 or self.DataFileModel_foreground.rowCount(None)==0:
            self.Subtraction_generateSubtraction_button.setDisabled(True)
            self.DataFileModel_foreground.layoutChanged.emit()
            self.DataFileModel_background.layoutChanged.emit()
            self.guiWindow.DataFileModel.layoutChanged.emit()
            return

        foregroundFiles = self.DataFileModel_foreground.getData()
        backgroundFiles = self.DataFileModel_background.getData()

        maxlength = np.max([len(foregroundFiles),len(backgroundFiles)])
        checks = [] # Check of combability 
        for item in foregroundFiles+backgroundFiles:
            item.BGColor = InvalidColour

        for fore,back in zip(foregroundFiles,backgroundFiles):
            check = subtractable(fore,back)
            totalCheck = np.all([v for v in check.values()])
            checks.append(totalCheck)
            
            if totalCheck:
                fore.BGColor = ValidColour
                back.BGColor = ValidColour
            else:
                fore.BGColor = InvalidColour
                back.BGColor = InvalidColour

            for key,value in check.items():
                setattr(fore,key+'_check',value)
                setattr(back,key+'_check',value)

        # Check if selected datasets are converted
        subtracted = np.any([not X.dataSetModel.item(X.getCurrentDatasetIndex()).background is None for X in [self.DataFileModel_foreground,self.DataFileModel_background]])
        
        if np.all(checks) and len(checks)==maxlength and not subtracted: # subraction is allowed
            self.Subtraction_generateSubtraction_button.setDisabled(False)
        else:
            self.Subtraction_generateSubtraction_button.setDisabled(True)

        self.DataFileModel_foreground.layoutChanged.emit()
        self.DataFileModel_background.layoutChanged.emit()
        self.guiWindow.DataFileModel.layoutChanged.emit()

