
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt



class DataSetModel(QtCore.QAbstractListModel):
    def __init__(self, *args, dataSets=None, **kwargs):
        super(DataSetModel, self).__init__(*args, **kwargs)
        self.dataSets = dataSets or []
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            text = self.dataSets[index.row()].name
            return text
        
        #if role == Qt.DecorationRole:
        #    status, _ = self.dataSets[index.row()]
        #    if status:
        #        return tick

    def rowCount(self, index):
        return len(self.dataSets)




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
    def __init__(self, *args, dataSets=None, currentDataSetIndex=None,currentDataFileIndex=None, **kwargs):
        super(DataFileModel, self).__init__(*args, **kwargs)
        self.dataSets = dataSets or []
        self.currentDataSetIndex = currentDataSetIndex
        self.currentDataFileIndex = currentDataFileIndex
        
    def data(self, index, role):

        if role == Qt.DisplayRole:
            
            text = self.dataSets[self.currentDataSetIndex][index.row()].name
            return text
        
        #if role == Qt.DecorationRole:
        #    status, _ = self.todos[index.row()]
        #    if status:
        #        return tick

    def rowCount(self, index):
        if self.currentDataSetIndex is None:
            return 0
        return len(self.dataSets[self.currentDataSetIndex])

    def updateCurrentDataSetIndex(self,index):
        self.currentDataSetIndex = index
        
    def updateCurrentDataFileIndex(self,index):
        self.currentDataFileIndex = index
        
