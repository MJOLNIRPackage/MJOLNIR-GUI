
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from MJOLNIR_Data import GuiDataFile
import numpy as np



class DataSetModel(QtCore.QAbstractListModel):
    def __init__(self, *args, dataSets=None, DataSet_DataSets_listView=None, **kwargs):
        super(DataSetModel, self).__init__(*args, **kwargs)
        self.dataSets = dataSets or []
        self.DataSet_DataSets_listView = DataSet_DataSets_listView
        
    def data(self, index, role):
        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = self.dataSets[index.row()].name
            return text
        
        #if role == Qt.DecorationRole:
        #    status = self.dataSets[index.row()].checked
        #    if status:
        #        return tick

    def getData(self,*args,**kwargs):
        return self.data(*args,**kwargs)

    def rowCount(self, index):
        return len(self.dataSets)

    def append(self,ds):
        self.dataSets.append(ds)
        print("DataSet '{}' was added.".format(ds.name))
        self.layoutChanged.emit()

    def delete(self,index):
        try:
            print("DataSet '{}' was deleted.".format(self.dataSets[index.row()].name))
            del self.dataSets[index.row()]
            self.layoutChanged.emit()
        except:
            pass

    def item(self,index):
        if not index is None:
            return self.dataSets[index.row()]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ds = self.item(index)
        if role == QtCore.Qt.EditRole:
            ds.name = value
            self.dataChanged.emit(index, index)
            return True
            
        return False

    def flags(self,index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def getCurrentDatasetIndex(self):
        indices = self.DataSet_DataSets_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            return self.DataSet_DataSets_listView.selectedIndexes()[0]

    def getCurrentDatasetIndexRow(self):
        currentIndex = self.getCurrentDatafileIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentDataSet(self):
        index = self.getCurrentDatasetIndex()
        return self.item(index)



### Conversion from row call to attribute name

class defaultList(list):
    """Overloading of list object to always return list[0] if entry larger than lengths is called"""
    def __init__(self,*args,**kwargs):
        super(defaultList,self).__init__(*args,**kwargs)

    def __getitem__(self,index):
        if index>len(self)-1:
            return super(defaultList, self).__getitem__(0)
        else:
            return super(defaultList, self).__getitem__(index)

conversionList = defaultList(['name',
                            'ScanCommand'])


class defDict(dict):
    def __init__(self,*args,**kwargs):
        dict.__init__(self, args)
        #super(defDict,self).__init__(*args,**kwargs)


    def __getitem__(self, key):
        if not key in dict.keys(self):
            val = dict.__getitem__(self, 'default')
        else:
            val = dict.__getitem__(self, key)
        
        return val

    def __setitem__(self, key, val):
        
        dict.__setitem__(self, key, val)
    
    

IconDict = defDict()
IconDict['default']=QtGui.QImage('Icons/icons/document.png')
IconDict['hdf']=QtGui.QImage('Icons/Own/HDF_logo_16.png')
IconDict['nxs']=QtGui.QImage('Icons/Own/NXS_logo_16.png')


class DataFileModel(QtCore.QAbstractListModel):
    def __init__(self, *args, DataSet_filenames_listView=None,dataSetModel=None,DataSet_DataSets_listView=None, **kwargs):
        super(DataFileModel, self).__init__(*args, **kwargs)
        self.dataSetModel = dataSetModel
        self.DataSet_DataSets_listView = DataSet_DataSets_listView
        self.DataSet_filenames_listView = DataSet_filenames_listView
        
    def data(self, index, role):

        if role == Qt.DisplayRole or role == Qt.EditRole:
            
            text = self.dataSetModel.item(self.getCurrentDatasetIndex())[index.row()].name
            return text
        
        if role == Qt.DecorationRole:
            t = self.dataSetModel.item(self.getCurrentDatasetIndex())[index.row()].type
            return IconDict[t]


    def getCurrentDatasetIndex(self):
        
        indices = self.DataSet_DataSets_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            return self.DataSet_DataSets_listView.selectedIndexes()[0]

    def getCurrentDatasetIndexRow(self):
        currentIndex = self.getCurrentDatasetIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentDatafileIndex(self):
        indices = self.DataSet_filenames_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            return self.DataSet_filenames_listView.selectedIndexes()[0]

    def getCurrentDatafileIndexRow(self):
        currentIndex = self.getCurrentDatafileIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentDatafile(self):
        indexRow = self.getCurrentDatafileIndexRow()
        if indexRow is None:
            return None
        else:
            ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
            df = ds[indexRow]
            return df


    def rowCount(self, index):
        
        if self.getCurrentDatasetIndexRow() is None:
            return 0
        try:
            length = len(self.dataSetModel.item(self.getCurrentDatasetIndex()))
            return length
        except IndexError:
            return 0

    def updateCurrentDataSetIndex(self):
        self.DataSet_filenames_listView.clearSelection()
        self.layoutChanged.emit()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        df = ds[index.row()]
        
        if role == QtCore.Qt.EditRole:
            df.name = value
            
            return True
            
        return False


    def flags(self,index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def delete(self):
        ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        del ds[self.getCurrentDatafileIndexRow()]
        self.layoutChanged.emit()


    def add(self,files,guiWindow=None):
        if not guiWindow is None:
            guiWindow.setProgressBarMaximum(len(files))
        ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        dfs = []
        for i,f in enumerate(files):
            dfs.append(GuiDataFile(f))
            if not guiWindow is None:
                guiWindow.setProgressBarValue(i+1)
            

        ds.append(dfs)
        self.layoutChanged.emit()