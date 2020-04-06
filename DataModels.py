
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt



class DataSetModel(QtCore.QAbstractListModel):
    def __init__(self, *args, dataSets=None, **kwargs):
        super(DataSetModel, self).__init__(*args, **kwargs)
        self.dataSets = dataSets or []
        
    def data(self, index, role):
        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = self.dataSets[index.row()].name
            return text
        
        #if role == Qt.DecorationRole:
        #    status, _ = self.dataSets[index.row()]
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
        return self.dataSets[index.row()]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ds = self.dataSets[index.row()]
        if role == QtCore.Qt.EditRole:
            ds.name = value
            self.dataChanged.emit(index, index)
            return True
            
        return False

    def flags(self,index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable



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


class DataFileModel(QtCore.QAbstractListModel):
    def __init__(self, *args, DataSet_filenames_listView=None,dataSetModel=None,DataSet_DataSets_listView=None, **kwargs):
        super(DataFileModel, self).__init__(*args, **kwargs)
        self.dataSetModel = dataSetModel
        self.DataSet_DataSets_listView = DataSet_DataSets_listView
        self.DataSet_filenames_listView = DataSet_filenames_listView
        
    def data(self, index, role):

        if role == Qt.DisplayRole:
            
            text = self.dataSetModel.item(self.getCurrentDatasetIndex())[index.row()].name
            return text
        
        #if role == Qt.DecorationRole:
        #    status, _ = self.todos[index.row()]
        #    if status:
        #        return tick

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



    def rowCount(self, index):
        
        if self.getCurrentDatasetIndexRow() is None:
            return 0
        try:
            length = len(self.dataSetModel.item(self.getCurrentDatasetIndex()))
            return length
        except IndexError:
            return 0

    def updateCurrentDataSetIndex(self):
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
