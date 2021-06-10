from re import sub
import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python.DataModels import DataSetModel,SelectionModel,DataFileModel,DataFileInfoModel,subtractionSettings
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile,GuiDataSet
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
except ImportError:
    from DataModels import DataSetModel,SelectionModel,DataFileModel,DataFileInfoModel,subtractionSettings
    from MJOLNIR_Data import GuiDataFile,GuiDataSet
    from _tools import ProgressBarDecoratorArguments


from os import path
from PyQt5 import QtWidgets,uic, QtCore, QtGui
from PyQt5.QtCore import Qt
import numpy as np
def subtractable(file1,file2):
    if file1.type != file2.type:
        return False
    if file1.I.shape != file2.I.shape:
        return False

    floatArrays = ['A3','A4','Ei']
    for param in floatArrays:
        if not np.all(np.isclose(getattr(file1,param),getattr(file2,param))):
            return False

    if not file1.scanParameters == file2.scanParameters:
        return False

    return True

ValidColour =  QtGui.QColor(255, 255, 255, 0)
InvalidColour = QtGui.QColor(255, 0, 0, 120)

class MyDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        #super(MyDelegate,self).__init__(self)
        QtWidgets.QStyledItemDelegate.__init__(self, parent, *args)


    def paint(self, painter, option, index):
        super(MyDelegate,self).paint(painter, option, index)
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

try:
    # needed when freezing app
    SubtractionManagerBase, SubtractionManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Subtraction.ui"))
    
except:
    try:
        # needed when running app local through fbs
        SubtractionManagerBase, SubtractionManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Subtraction.ui"))
        
    except:
        # needed when running app after pip install
        SubtractionManagerBase, SubtractionManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Subtraction.ui"))
        

        
class SubtractionManager(SubtractionManagerBase, SubtractionManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(SubtractionManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initSubtractionManager()

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

        self.Subtraction_dataSet_foreground_comboBox.currentIndexChanged.connect(lambda: self.comboboxChanged(foreground=True))#lambda idx: comboboxChanged(idx,self.Subtraction_dataSet_foreground_comboBox,self.Subtraction_dataSet_background_comboBox))
        self.Subtraction_dataSet_background_comboBox.currentIndexChanged.connect(lambda: self.comboboxChanged(foreground=False))#lambda idx: comboboxChanged(idx,self.Subtraction_dataSet_background_comboBox,self.Subtraction_dataSet_foreground_comboBox))
        
        
        self.DataFileModel_foreground = DataFileModel(self.Subtraction_filenames_foreground_listView,\
            dataSetModel=self.guiWindow.DataSetModel,DataSet_DataSets_listView=self.Subtraction_dataSet_foreground_comboBox,\
                guiWindow = self.guiWindow)

        # Set up model for foreground df view
        self.Subtraction_filenames_foreground_listView.setModel(self.DataFileModel_foreground)
        self.Subtraction_filenames_foreground_listView.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.Subtraction_filenames_foreground_listView.setDragDropOverwriteMode(False)

        dg = MyDelegate()
        self.Subtraction_filenames_foreground_listView.setItemDelegate(dg)
        self.Subtraction_filenames_background_listView.setItemDelegate(dg)
        

        # add selection model for smooth selection when drag/dropping
        self.DataFile_foreground_SelectionModel = SelectionModel(self.DataFileModel_foreground)#self.ui.DataSet_DataSets_listView.selectionModel()
        
        
        self.Subtraction_filenames_foreground_listView.setSelectionModel(self.DataFile_foreground_SelectionModel)
        
        

        # add file information
        self.DataFile_foreground_infoModel = DataFileInfoModel(DataSet_filenames_listView=self.Subtraction_filenames_foreground_listView,dataSetModel=self.guiWindow.DataSetModel,
        DataSet_DataSets_listView=self.Subtraction_dataSet_foreground_comboBox,dataFileModel=self.DataFileModel_foreground,guiWindow=self.guiWindow)
        self.DataFile_foreground_infoModel.infos = [x for x in subtractionSettings.keys()]
        self.Subtraction_fileAttributs_foreground_listView.setModel(self.DataFile_foreground_infoModel)
        
        #self.DataFileModel_foreground.layoutChanged.connect(self.checkDataSetCombability)
        self.DataFileModel_foreground.dragDropFinished.connect(self.DataFile_foreground_SelectionModel.onModelItemsReordered)
        self.DataFile_foreground_SelectionModel.selectionChanged.connect(self.updateDataFileLabels)
        #self.DataFileModel_foreground.layoutChanged.connect(self.updateDataFileLabels)
        


        ##### Repeat above for background
        self.DataFileModel_background = DataFileModel(self.Subtraction_filenames_background_listView,\
            dataSetModel=self.guiWindow.DataSetModel,DataSet_DataSets_listView=self.Subtraction_dataSet_background_comboBox,\
                guiWindow = self.guiWindow)
        #self.DataFileModel_background.layoutChanged.connect(self.checkDataSetCombability)

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
            subtracted_ds.background = [df.original_file.fileLocation for df in background_ds]
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
        
        foregroundFiles = self.DataFileModel_foreground.getData()
        backgroundFiles = self.DataFileModel_background.getData()

        maxlength = np.max([len(foregroundFiles),len(backgroundFiles)])
        checks = []

        for item in foregroundFiles+backgroundFiles:
            item.BGColor = InvalidColour

        for fore,back in zip(foregroundFiles,backgroundFiles):
            check = subtractable(fore,back)
            checks.append(check)
            if check:
                fore.BGColor = ValidColour
                back.BGColor = ValidColour
            else:
                fore.BGColor = InvalidColour
                back.BGColor = InvalidColour

        
        if np.all(checks) and len(checks)==maxlength: # subraction is allowed
            self.Subtraction_generateSubtraction_button.setDisabled(False)
        else:
            self.Subtraction_generateSubtraction_button.setDisabled(True)

        self.DataFileModel_foreground.layoutChanged.emit()
        self.DataFileModel_background.layoutChanged.emit()
        self.guiWindow.DataFileModel.layoutChanged.emit()



