
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

import pickle

import numpy as np
import sys
import warnings

from MJOLNIR import _tools as M_tools
from MJOLNIR.Geometry.Instrument import timeEstimate

import matplotlib.pyplot as plt
try:
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiDataFile
except ImportError:
    from  MJOLNIR_Data import GuiDataFile

from os import path
from collections import namedtuple
try:
    import MJOLNIRGui.src.main.python._tools
except ImportError:
    import _tools

from datetime import datetime, timedelta

class DataSetModel(QtCore.QAbstractListModel):

    dragDropFinished = QtCore.pyqtSignal()

    def __init__(self, *args, dataSets=None, DataSet_DataSets_listView=None,guiWindow=None, **kwargs):
        super(DataSetModel, self).__init__(*args, **kwargs)
        self.dataSets = dataSets or []
        self.DataSet_DataSets_listView = DataSet_DataSets_listView
        self.lastDroppedItems = []
        self.pendingRemoveRowsAfterDrop = False
        self.guiWindow = guiWindow

    def rowForItem(self, item):
        '''
        rowForItem method returns the row corresponding to the passed in item
        or None if no such item exists in the model
        '''
        try:
            row = self.dataSets.index(item)
        except ValueError:
            return None
        return row
        
    def data(self, index, role = Qt.ItemDataRole):
        if index.row()<0 or index.row()>len(self.dataSets)-1:
            return 
        
        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = self.dataSets[index.row()].name
            return text
        if role == Qt.ItemDataRole:
            return self.dataSets[index.row()]
        if role == Qt.DecorationRole:
            if not self.dataSets[index.row()]._maskingObject is None:
                return QtGui.QImage(self.guiWindow.AppContext.get_resource('Icons/Own/mask-open.png'))
            else:
                return None

        #    if status:
        #        return tick

    def getData(self,*args,**kwargs):
        return self.data(*args,**kwargs)

    def rowCount(self, index):
        return len(self.dataSets)

    def insertRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        # inserting 'count' empty rows starting at 'row'
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
        for i in range(0, count):
            self.dataSets.insert(row + i, None)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        # num_rows = self.rowCount(QtCore.QModelIndex())
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
        for i in range(count, 0, -1):
            self.dataSets.pop(row - i + 1)
        self.endRemoveRows()

        if self.pendingRemoveRowsAfterDrop:
            '''
            If we got here, it means this call to removeRows is the automatic
            'cleanup' action after drag-n-drop performed by Qt
            '''
            self.pendingRemoveRowsAfterDrop = False
            self.dragDropFinished.emit()

        return True

    def generateValidName(self,ds):
        name = ds.name
        while name in [DS.name for DS in self.dataSets if not DS is ds]: # name already exists.. This screws up drag/drop
            try:
                idx = int(name.split(' ')[-1])
            except ValueError:
                name = name+' 1'
            else:
                name = name[:-(len(str(idx))+1)] + ' ' + str(idx+1)
        return name

    def append(self,ds):
        ds.name = self.generateValidName(ds)

        if self.rowCount(None)>0:
            numbers = [d.idx for d in self.dataSets]
        else:
            numbers = [-1]
        ds.idx = np.max(numbers)+1
        self.dataSets.append(ds)
        self.selectLastDataSet()
        self.layoutChanged.emit()

    def delete(self,index):
        try:
            del self.dataSets[index.row()]
            self.layoutChanged.emit()
        except:
            pass
        QtWidgets.QApplication.processEvents()
        index = self.getCurrentDatasetIndex()
        
        if index is None:
            self.selectLastDataSet()
        else:
            if index.row()==self.rowCount(None):
                self.selectLastDataSet()
            else:
                idx = self.index(index.row(),0)# Hack to force index changed emit
                self.DataSet_DataSets_listView.setCurrentIndex(self.index(-1,0))
                self.DataSet_DataSets_listView.setCurrentIndex(idx)


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

    def index(self, row, column, parent=None):
        if row < 0 or row >= self.rowCount(None):
            return QtCore.QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction 
        

    def flags(self,index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    def mimeTypes(self):
        return ['mjolnirgui/datasetdragdrop.list']

    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        for index in indexes:
            if index.isValid():
                item = self.data(index, QtCore.Qt.ItemDataRole)
                
        stream << QtCore.QByteArray(str(item.idx).encode('utf-8'))#pickle.dumps(item))
        mimedata.setData('mjolnirgui/datasetdragdrop.list', encoded_data)
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        if action == QtCore.Qt.IgnoreAction:
            return True
        if not data.hasFormat('mjolnirgui/datasetdragdrop.list'):
            return False
        if column > 0:
            return False

        num_rows = self.rowCount(QtCore.QModelIndex())
        if num_rows <= 0:
            return False

        if row < 0:
            if parent.isValid():
                row = parent.row()
            else:
                return False

        encoded_data = data.data('mjolnirgui/datasetdragdrop.list')
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)

        new_items = []
        rows = 0
        while not stream.atEnd():
            item = QtCore.QByteArray()
            stream >> item
            item = int((bytes(item)).decode('utf-8)'))#pickle.loads(item)
            index = [ds.idx for ds in self.dataSets].index(item)
            item = self.dataSets[index]
            new_items.append((item, index))
            rows += 1

        self.lastDroppedItems = []
        for (text, index) in new_items:
            target_row = row
            if index < row:
                target_row += 1
            self.beginInsertRows(QtCore.QModelIndex(), target_row, target_row)
            self.dataSets.insert(target_row, text)
            self.endInsertRows()
            self.lastDroppedItems.append(text)
            row += 1
        self.pendingRemoveRowsAfterDrop = True
        return True

    def getCurrentDatasetIndex(self):
        indices = self.DataSet_DataSets_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            index = indices[0]
            if index.row()<self.rowCount(None):
                return index
            else:
                return None

    def getCurrentDatasetIndexRow(self):
        currentIndex = self.getCurrentDatasetIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentDataSet(self):
        index = self.getCurrentDatasetIndex()
        return self.item(index)

    def selectLastDataSet(self):
        DataSets = self.rowCount(None)
        if DataSets!=0:
            index = self.index(self.rowCount(None)-1,0)
            self.DataSet_DataSets_listView.setCurrentIndex(index)


class SelectionModel(QtCore.QItemSelectionModel):
    """Selection model created from https://github.com/d1vanov/PyQt5-reorderable-list-model/blob/master/reorderable_list_model.py
    When drag/drop is used, selects newly inserted item"""
    def __init__(self, parent=None):
        QtCore.QItemSelectionModel.__init__(self, parent)

    def onModelItemsReordered(self):
        new_selection = QtCore.QItemSelection()
        new_index = QtCore.QModelIndex()
        for item in self.model().lastDroppedItems:
            row = self.model().rowForItem(item)
            if row is None:
                continue
            new_index = self.model().index(row, 0, QtCore.QModelIndex())
            new_selection.select(new_index, new_index)

        self.clearSelection()
        flags = QtCore.QItemSelectionModel.ClearAndSelect | \
                QtCore.QItemSelectionModel.Rows | \
                QtCore.QItemSelectionModel.Current
        self.select(new_selection, flags)
        self.setCurrentIndex(new_index, flags)


class Cut1DModel(QtCore.QAbstractListModel):
    def __init__(self, *args, dataCuts1D=None, Cut1D_listView=None, **kwargs):
        super(Cut1DModel, self).__init__(*args, **kwargs)
        self.dataCuts1D = dataCuts1D or []
        self.Cut1D_listView = Cut1D_listView
        
    def data(self, index, role):
        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = self.dataCuts1D[index.row()].name
            return text
        
    def getData(self,*args,**kwargs):
        return self.data(*args,**kwargs)

    def rowCount(self, index=None):
        return len(self.dataCuts1D)

    def append(self,Cut1D):
        self.dataCuts1D.append(Cut1D)
        self.selectLastCut1D()
        self.layoutChanged.emit()

    def delete(self,index):
        indices = [ind.row() for ind in index] # Extract numeric index, sort decending
        indices.sort(reverse=True)
        for ind in indices:
            try:
                del self.dataCuts1D[ind]
                self.layoutChanged.emit()
            except:
                pass

        QtWidgets.QApplication.processEvents()
        index = self.getCurrentCut1DIndex()
       
        if index is None:
            self.selectLastCut1D()
        else:
            if index.row()==self.rowCount(None):
                self.selectLastCut1D()

    def item(self,index):
        if not index is None:
            return self.dataCuts1D[index.row()]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ds = self.item(index)
        if role == QtCore.Qt.EditRole:
            ds.name = value
            self.dataChanged.emit(index, index)
            return True
           
        return False

    def flags(self,index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def getCurrentCut1DIndex(self):
        indices = self.Cut1D_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            index = indices[0]
            if index.row()<self.rowCount(None):
                return index
            else:
                return None

    def getCurrentCut1DIndexRow(self):
        currentIndex = self.getCurrentCut1DIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentCut1D(self):
        index = self.getCurrentCut1DIndex()
        return self.item(index)

    def selectLastCut1D(self):
        dataCuts1D = self.rowCount(None)
        if dataCuts1D!=0:
            index = self.index(self.rowCount(None)-1,0)
            self.Cut1D_listView.setCurrentIndex(index)


class BraggListModel(QtCore.QAbstractListModel):
    def __init__(self, *args, BraggList=None, braggList_listView=None, **kwargs):
        super(BraggListModel, self).__init__(*args, **kwargs)
        if BraggList is None:
            BraggList = []
        self._data = BraggList 
        self.braggList_listView = braggList_listView
        
    def data(self, index, role):
        if index.row()>=self.rowCount(): return 
        if index.row()<0: return 
        if index.column()>=1: return 
        if index.column()<-1: return 

        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = '\t'.join(map(str,self._data[index.row()]))
            return text
        
    def getData(self,*args,**kwargs):
        return self.data(*args,**kwargs)

    def getAllData(self):
        return self._data

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return 0

    def append(self,BraggPoint):
        self._data.append(BraggPoint)
        self.selectLastBragg()
        self.layoutChanged.emit()

    def deleteAll(self):
        indices = [self.index(i,0) for i in range(self.rowCount())]
        self.delete(indices)

    def delete(self,index):
        indices = [ind.row() for ind in index] # Extract numeric index, sort decending
        indices.sort(reverse=True)
        for ind in indices:
            try:
                del self._data[ind]
                self.layoutChanged.emit()
            except:
                pass

        QtWidgets.QApplication.processEvents()
        #index = self.getCurrentBraggIndex()
       
        #if index is None:
        #    self.selectLastBragg()
        #else:
        #    if index.row()==self.rowCount(None):
        #        self.selectLastBragg()

    def item(self,index):
        if not index is None:
            return self._data[index.row()]

    #def setData(self, index, value, role=QtCore.Qt.EditRole):
    #    ds = self.item(index)
    #    if role == QtCore.Qt.EditRole:
    #        ds.name = value
    #        self.dataChanged.emit(index, index)
    #        return True
    #       
    #    return False

    def flags(self,index):
        return  QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def getCurrentBraggIndex(self):
        indices = self.braggList_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            index = indices[0]
            if index.row()<self.rowCount(None):
                return index
            else:
                return None

    def getCurrentBraggIndexRow(self):
        currentIndex = self.getCurrentBraggIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentBragg(self):
        index = self.getCurrentBraggIndex()
        return self.item(index)

    def selectLastBragg(self):
        bragg = self.rowCount(None)
        if bragg!=0:
            index = self.index(self.rowCount(None)-1,0)
            self.braggList_listView.setCurrentIndex(index)




class ScanListModel(QtCore.QAbstractListModel):
    def __init__(self, *args, scanList=None, scanList_listView=None,startTime=None,current=None, **kwargs):
        super(ScanListModel, self).__init__(*args, **kwargs)
        if scanList is None:
            scanList = []
        self._data = scanList 
        self.scanList_listView = scanList_listView
        if startTime is None:
            startTime = datetime.now()

        self.startTime = startTime
        if current is None:
            current = 1.35
        self.current = current
        
    def data(self, index, role):
        if index.row()>=self.rowCount(): return 
        if index.row()<0: return 
        if index.column()>=1: return 
        if index.column()<-1: return 

        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            offset = self.startTime + timedelta(seconds=np.sum([d.timeEstimate(current=self.current) for d in self._data[:index.row()]]))
            text = self._data[index.row()].toText(current=self.current,offset=offset)
            return text
        
    def timeChanged(self,date,time):
        year,month,day = date.year(),date.month(),date.day()
        hour,minute = time.hour(),time.minute()

        self.startTime = datetime(year,month,day,hour,minute)
        self.layoutChanged.emit()

    def currentChanged(self,value):
        self.current = value
        self.layoutChanged.emit()

    def getData(self,*args,**kwargs):
        return self.data(*args,**kwargs)

    def getAllData(self):
        return self._data

    def rowCount(self, index=None):
        return len(self._data)

    def columnCount(self, index=None):
        return 0

    def append(self,scan):
        self._data.append(scan)
        self.selectLastScan()
        self.layoutChanged.emit()

    def deleteAll(self):
        indices = [self.index(i,0) for i in range(self.rowCount())]
        self.delete(indices)

    def delete(self,index):
        indices = [ind.row() for ind in index] # Extract numeric index, sort decending
        indices.sort(reverse=True)
        for ind in indices:
            try:
                del self._data[ind]
                self.layoutChanged.emit()
            except:
                pass

        QtWidgets.QApplication.processEvents()
        #index = self.getCurrentBraggIndex()
       
        #if index is None:
        #    self.selectLastBragg()
        #else:
        #    if index.row()==self.rowCount(None):
        #        self.selectLastBragg()

    def item(self,index):
        if not index is None:
            return self._data[index.row()]

    #def setData(self, index, value, role=QtCore.Qt.EditRole):
    #    ds = self.item(index)
    #    if role == QtCore.Qt.EditRole:
    #        ds.name = value
    #        self.dataChanged.emit(index, index)
    #        return True
    #       
    #    return False

    def flags(self,index):
        return  QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def getCurrentScanIndex(self):
        indices = self.scanList_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            index = indices[0]
            if index.row()<self.rowCount(None):
                return index
            else:
                return None

    def getCurrentScanIndexRow(self):
        currentIndex = self.getCurrentScanIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentScan(self):
        index = self.getCurrentScanIndex()
        return self.item(index)

    def selectLastScan(self):
        scan = self.rowCount(None)
        if scan!=0:
            index = self.index(self.rowCount(None)-1,0)
            self.scanList_listView.setCurrentIndex(index)



class MaskModel(QtCore.QAbstractListModel):
    def __init__(self, *args, masks=None, Mask_listView=None, guiWindow=None, **kwargs):
        super(MaskModel, self).__init__(*args, **kwargs)
        self.masks = masks or []
        self.Mask_listView = Mask_listView
        self._combinedMask = None
        self.guiWindow = guiWindow

    @property
    def combinedMask(self):
        return self._combinedMask

    @combinedMask.getter
    def combinedMask(self):
        return self._combinedMask

    @combinedMask.setter
    def combinedMask(self,value):
        if not value is self._combinedMask:
            self._combinedMask = value
        
    def data(self, index, role):
        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            text = self.masks[index.row()].name
            return text
        
    def getData(self,*args,**kwargs):
        return self.data(*args,**kwargs)

    def rowCount(self, index=None):
        return len(self.masks)

    def generateValidName(self,ds):
        name = ds.name
        while name in self.getNames(): # name already exists.. This screws up drag/drop
            try:
                idx = int(name.split('_')[-1])
            except ValueError:
                name = name+'_1'
            else:
                name = name[:-(len(str(idx))+1)] + '_' + str(idx+1)
        return name

    def append(self,mask):
        mask.name = self.generateValidName(mask)

        if self.rowCount(None)>0:
            numbers = [d.idx for d in self.masks]
        else:
            numbers = [-1]
        mask.idx = np.max(numbers)+1
        self.masks.append(mask)
        self.selectLastMask()
        self.layoutChanged.emit()

    def delete(self,index):
        indices = [ind.row() for ind in index] # Extract numeric index, sort decending
        indices.sort(reverse=True)
        for ind in indices:
            try:
                del self.masks[ind]
                self.layoutChanged.emit()
            except:
                pass

        QtWidgets.QApplication.processEvents()
        selectIndex = self.getCurrentMaskIndex()
        if selectIndex is None:
            self.selectLastMask()
        else:
            if selectIndex.row()==self.rowCount(None):
                self.selectLastMask()

            else:
                idx = self.index(selectIndex.row(),0)# Hack to force index changed emit
                self.Mask_listView.setCurrentIndex(self.index(-1,0))
                self.Mask_listView.setCurrentIndex(idx)
        self.layoutChanged.emit()

    def item(self,index):   
        if not index is None:
            if not isinstance(index,list):
                try:
                    return self.masks[index.row()]
                except (AttributeError,IndexError):
                    return None
            else:
                index = np.asarray(index)
                if len(index) == 0:
                    return None
                indices = np.array([x.row() for x in index],dtype=int)
                return np.asarray(self.masks)[indices]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        mask = self.item(index)
        if role == QtCore.Qt.EditRole:
            mask.name = value
            self.dataChanged.emit(index, index)
            return True
           
        return False
    
    def getNames(self):
        return [m.name for m in self.masks]

    def flags(self,index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def getCurrentMaskIndex(self):
        indices = self.Mask_listView.selectedIndexes()
        
        if len(indices)==0:
            return None
        else:
            index = indices[0]
            if index.row()<self.rowCount(None):
                return index
            else:
                return None

    def getCurrentMaskIndexRow(self):
        currentIndex = self.getCurrentMaskIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getMask(self):
        index = self.getCurrentMaskIndex()
        return self.item(index)

    def selectLastMask(self):
        
        if len(self.masks)>0:
            index = self.index(len(self.masks)-1,0)
        else:
            index = self.index(-1,0)
        self.Mask_listView.setCurrentIndex(index)
        



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
    
    
class DummyIndexClass(object):
    def __init__(self,row):
        self._row = row

    def row(self):
        return self._row



class DataFileModel(QtCore.QAbstractListModel):

    dragDropFinished = QtCore.pyqtSignal()

    def __init__(self,DataSet_filenames_listView=None,dataSetModel=None,DataSet_DataSets_listView=None,guiWindow=None, **kwargs):
        super(DataFileModel, self).__init__(**kwargs)
        self.dataSetModel = dataSetModel
        self.DataSet_DataSets_listView = DataSet_DataSets_listView
        self.DataSet_filenames_listView = DataSet_filenames_listView
        self.guiWindow = guiWindow
        self.lastDroppedItems = []
        self.pendingRemoveRowsAfterDrop = False

        self.IconDict = defDict()
        self.IconDict['default']=QtGui.QImage(self.guiWindow.AppContext.get_resource('Icons/Own/document.png'))
        self.IconDict['hdf']=QtGui.QImage(self.guiWindow.AppContext.get_resource('Icons/Own/HDF_logo_16.png'))
        self.IconDict['nxs']=QtGui.QImage(self.guiWindow.AppContext.get_resource('Icons/Own/NXS_logo_16.png'))

    def rowForItem(self, item):
        '''
        rowForItem method returns the row corresponding to the passed in item
        or None if no such item exists in the model
        '''
        try:
            row = list(self.dataSetModel.item(self.getCurrentDatasetIndex())).index(item)
        except ValueError:
            return None
        return row
        
    def data(self, index, role=Qt.ItemDataRole):
        try:
            ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        except AttributeError:
            return None
        
        ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        row = index.row()
        if row>= len(ds):
            return None

        if role == Qt.DisplayRole or role == Qt.EditRole:
            
            text = ds[row].name
            return text
        
        if role == Qt.DecorationRole:
            t = ds[row].type
            return self.IconDict[t]

        if role == Qt.ItemDataRole:
            return ds[row]

    def insertRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        # inserting 'count' empty rows starting at 'row'
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
        for i in range(0, count):
            self.dataSetModel.item(self.getCurrentDatasetIndex()).insert(row + i, None)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        # num_rows = self.rowCount(QtCore.QModelIndex())
        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
        for i in range(count, 0, -1):
             self.dataSetModel.item(self.getCurrentDatasetIndex()).pop(row - i + 1)
        self.endRemoveRows()

        if self.pendingRemoveRowsAfterDrop:
            '''
            If we got here, it means this call to removeRows is the automatic
            'cleanup' action after drag-n-drop performed by Qt
            '''
            self.pendingRemoveRowsAfterDrop = False
            self.dragDropFinished.emit()

        return True

    def index(self, row, column, parent=None):
        if row < 0 or row >= self.rowCount(None):
            return QtCore.QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction 

    def getCurrentDatasetIndex(self):
        if hasattr(self.DataSet_DataSets_listView,'selectedIndexes'): # If DataSet_DataSets_listView is listView
            indices = self.DataSet_DataSets_listView.selectedIndexes()
            
            if indices is None:
                return None
            else:
                if len(indices)==0:
                    return None
                else:
                    return indices[0]
        else: # If it is a combo box, needed for subrtaction manager. Mimic a proper index
            return DummyIndexClass(self.DataSet_DataSets_listView.currentIndex())

    def getCurrentDatasetIndexRow(self):
        currentIndex = self.getCurrentDatasetIndex()
        if currentIndex is None:
            return None
        else:
            return currentIndex.row()

    def getCurrentDatafileIndexs(self):
        indices = self.DataSet_filenames_listView.selectedIndexes()
        
        if indices is None:
            return None
        else:
            idxs = self.DataSet_filenames_listView.selectedIndexes()
            
            if np.all([idx.row()<self.rowCount(None) for idx in idxs]):
                return idxs
            else:
                return None

    def getCurrentDatafileIndexRows(self):
        currentIndeces = self.getCurrentDatafileIndexs()
        if currentIndeces is None:
            return None
        else:
            return [idx.row() for idx in currentIndeces]

    def getCurrentDatafiles(self,raw=False):
        """return current selected data files. If raw is true, return only raw."""
        indexRows = self.getCurrentDatafileIndexRows()
        if indexRows is None:
            return None
        if len(indexRows)==0:
            return None
        if np.any([idx is None for idx in indexRows]):
            return None
        else:
            ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
            dfs = [ds[idx] for idx in indexRows]
            return dfs

    def getData(self,raw = False):
        """Return all data files in dataset independent of selection. If raw is true, return only raw."""
        ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        if ds is None:
            return []
        if len(ds) == 0:
            return []
        if raw:
            dfs = [df if not df.type == 'nxs' else GuiDataFile(df.original_fileLocation) for df in ds]
        else:
            dfs = [df for df in ds]
        
        return dfs

    def getCurrentDataSet(self):
        return self.dataSetModel.item(self.getCurrentDatasetIndex())

    def rowCount(self, index):
        try:
            ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        except IndexError:
            return 0
        if ds is None:
            return 0
        else:
            return len(ds)
        
    def selectFirstDataFile(self):
        Files = self.rowCount(None)
        if Files!=0:
            index = self.index(0,0)
            self.DataSet_filenames_listView.setCurrentIndex(index)
        else:
            self.DataSet_filenames_listView.clearSelection()

    def updateCurrentDataSetIndex(self):
        self.selectFirstDataFile()
        self.layoutChanged.emit()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        df = ds[index.row()]
        
        if role == QtCore.Qt.EditRole:
            df.name = value
            
            return True
            
        return False


    def flags(self,index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDropEnabled
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        #return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def delete(self,idx=None):
        if idx is None:
            ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        else:
            ds = self.dataSetModel.item(idx)
        indices = np.array(self.getCurrentDatafileIndexRows())
        if np.all([row<len(ds) for row in indices]):
            for idx in indices:
                df = ds[idx]
                if df.type == 'nxs': #i.e. converted
                    del ds._dataFiles[idx]
                del ds[idx]
                indices-=1
            if not self.pendingRemoveRowsAfterDrop:
                self.layoutChanged.emit()
            self.guiWindow.updateDataFileLabels()


    def add(self,files,guiWindow=None):
        ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        dfs = []
        binning = None
        if len(ds)>0: # non-empty dataset
            if ds[0].type=='nxs': # Converted dataset
                binning = ds[0].binning

        if not guiWindow is None:
            if binning is None: # length is simply number of files
                length = len(files)
            else:
                length = 2*len(files) # both raw and converted
            guiWindow.setProgressBarMaximum(length)
            printFunction = guiWindow.writeToStatus
        else:
            printFunction = None
        
        for i,f in enumerate(files):
            newFile = GuiDataFile(f)
            dfs.append(newFile)
            if not guiWindow is None:
                guiWindow.setProgressBarValue(i+1)
            if not binning is None:
                convFile = newFile.convert(binning=binning,printFunction=printFunction)
                dfs.append(convFile)
                if not guiWindow is None:
                    guiWindow.setProgressBarValue(i+1)
            

        ds.append(dfs)
        if not self.pendingRemoveRowsAfterDrop:
            self.layoutChanged.emit()
        guiWindow.updateDataFileLabels()


    def mimeTypes(self):
        return ['mjolnirgui/datafiledragdrop.list']

    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        items = []
        for index in indexes:
            if index.isValid():
                item = self.data(index, QtCore.Qt.ItemDataRole)
                items.append(item)
                
        for item in items:
            stream << QtCore.QByteArray(str(item.idx).encode('utf-8'))#pickle.dumps(item))
        mimedata.setData('mjolnirgui/datafiledragdrop.list', encoded_data)
        return mimedata

    def dropMimeData(self, data, action, row, column, parent):
        if action == QtCore.Qt.IgnoreAction:
            return True
        if not data.hasFormat('mjolnirgui/datafiledragdrop.list'):
            return False
        if column > 0:
            return False

        num_rows = self.rowCount(QtCore.QModelIndex())
        if num_rows <= 0:
            return False

        if row < 0:
            if parent.isValid():
                row = parent.row()
            else:
                return False

        encoded_data = data.data('mjolnirgui/datafiledragdrop.list')
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)

        new_items = []
        rows = 0
        while not stream.atEnd():
            item = QtCore.QByteArray()
            stream >> item
            item = int(bytes(item).decode('utf-8'))#pickle.loads(item)
            index = [df.idx for df in self.dataSetModel.item(self.getCurrentDatasetIndex())].index(item)

            item = self.dataSetModel.item(self.getCurrentDatasetIndex())[index]
            new_items.append((item, index))
            rows += 1

        self.lastDroppedItems = []
        for (text, index) in new_items:
            target_row = row
            if index < row:
                target_row += 1
            self.beginInsertRows(QtCore.QModelIndex(), target_row, target_row)
            self.dataSetModel.item(self.getCurrentDatasetIndex()).insert(target_row, text)
            self.endInsertRows()
            self.lastDroppedItems.append(text)
            row += 1
        self.pendingRemoveRowsAfterDrop = True
        return True


def getAttribute(obj,location):
    if not '/' in location:
        return getattr(obj,location)
    
    splitLocation = location.split('/')
    newLocation = '/'.join(splitLocation[1:])
    newObj = getattr(obj,splitLocation[0])
    return getAttribute(newObj,newLocation)


def formatValueArray(array, formatString = '{:.2f} [{:.2f}  -  {:.2f}]'):
    """Format array to string using mean, min, max"""
    try:
        array = np.concatenate(array)
    except ValueError:
        return 'N/A'
    mean = np.mean(array)
    max_ = np.max(array)
    min_ = np.min(array)

    return formatString.format(mean,min_,max_)

def formatValueArrayDirection(array, formatString = '{:.2f} [{:.2f}  -  {:.2f}]'):
    """Format array to string using mean, min, max as well as direction (for A3)"""
    try:
        array = np.concatenate(array)
    except ValueError:
        return 'N/A'
    mean = np.mean(array)
    max_ = np.max(array)
    min_ = np.min(array)
    diff = np.diff(array.flatten())
    if np.all(diff>0):
        direction = ' Scan dir: +'
    elif np.all(diff<0):
        direction = ' Scan dir: -'
    else:
        direction = ''


    return formatString.format(mean,min_,max_)+direction

def formatTextArray(array):
    """Return string only if all entries are equal"""
    if len(array)==1:
        return array[0].strip()
        
    if np.all([array[0]==a for a in array]):
        return array[0].strip()
    else:
        return 'Multiple Values'

def formatTextArrayAdder(array):
    """Return list of all values"""
    array = np.array(array).flatten()
    if len(array)==1:
        return array[0]
    
    Set = set(array) # Set only conains one of each
    return ', '.join([str(s) for s in Set])


def formatVector(array):
    a = np.array(array,dtype=float)
    if len(a.shape)==1: # only one input
        return M_tools.generateLabel(a)
    else:
        if a.shape[1]>1: # more than one array
            if np.all([np.equal(a[0],x) for x in a[1:]]): # all equal to a[0]
                return M_tools.generateLabel(a[0])
            else:
                return 'N/A'
        else:
            return M_tools.generateLabel(a)


def formatRaw(array):
    if len(array) == 1:
        return str(array[0])
    return str(array)


Info = namedtuple('Info','location baseText formatter')
name = Info('sample/name','Sample: ',formatTextArray)
title = Info('title','Title: ',formatTextArray)
projectionVector1 = Info('sample/projectionVector1','Projection 1: ',formatVector)
projectionVector2 = Info('sample/projectionVector2','Projection 2: ',formatVector)
A3 = Info('A3','A3 [deg]: ',formatValueArrayDirection)
tt = Info('twotheta','2θ [deg]: ',formatValueArray)
magneticField = Info('magneticField','Magnetic Field [B]: ',formatValueArray)
temperature = Info('temperature','Temperature [K]: ',formatValueArray)
scanCommand = Info('scanCommand','Command: ',formatTextArray)
scanSteps = Info('scanSteps','Scan steps: ',formatRaw)
scanParameters = Info('scanParameters','Parameter: ',formatTextArrayAdder)
comment = Info('comment','Comment: ',formatTextArray)
binning = Info('binning','Binning: ',formatRaw)
Ei = Info('Ei','Ei [meV]: ',formatValueArray)
countingTime = Info('Time', 'Step time [s]: ',formatValueArray)
startTime = Info('startTime', 'Start time: ', formatTextArrayAdder)
endTime = Info('endTime', 'End time: ', formatTextArrayAdder)

settings = {'sample/name':name,'title':title,'sample/projectionVector1':projectionVector1,'sample/projectionVector2':projectionVector2,'Ei':Ei, 'A3':A3,'twotheta':tt, 'magneticField':magneticField,'temperature':temperature,
            'comment':comment, 'binning':binning,'scanCommand':scanCommand, 'scanSteps':scanSteps, 'scanParameters':scanParameters,
            'Time':countingTime,'startTime':startTime, 'endTime':endTime}

subtractionSettings = {'sample/name':name,'title':title,'sample/projectionVector1':projectionVector1,'sample/projectionVector2':projectionVector2,'Ei':Ei, 'A3':A3,'twotheta':tt, 'magneticField':magneticField,'temperature':temperature, 'scanCommand':scanCommand, 'scanSteps':scanSteps, 'scanParameters':scanParameters}

class DataFileInfoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, DataSet_filenames_listView=None,dataSetModel=None,DataSet_DataSets_listView=None,dataFileModel=None,guiWindow=None, **kwargs):
        super(DataFileInfoModel, self).__init__(*args, **kwargs)
        self.dataSetModel = dataSetModel
        self.dataFileModel = dataFileModel
        self.DataSet_DataSets_listView = DataSet_DataSets_listView
        self.DataSet_filenames_listView = DataSet_filenames_listView
        self.guiWindow = guiWindow
        self.possibleSettings = settings
        self.infos = []

        
    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            dfs = self.dataFileModel.getCurrentDatafiles()
            I = index.row()
            info = self.infos[I]
            if not dfs is None:
                
                if len(dfs)==1:
                    data = [getAttribute(dfs[0],info.location)]
                else:
                    data =[getAttribute(df,info.location) for df in dfs]
                return info.baseText+info.formatter(data)
            else:
                return info.baseText
        elif role == Qt.ItemDataRole:
            I = index.row()
            info = self.infos[I]
            dfs = self.dataFileModel.getCurrentDatafiles()
            if not dfs is None:
                df = dfs[0]
            else:
                return True
            
            if hasattr(df,info.location+'_check'):
                return getattr(df,info.location+'_check')
            else:
                return True


        
        
    def rowCount(self,index):
        return len(self.infos)

    @property
    def infos(self):
        return self._infos

    @infos.setter
    def infos(self, newSettings):
        newSettings = np.array(newSettings)
        inside = np.array([I in self.possibleSettings.keys() for I in newSettings],dtype=bool)
        if not np.all(inside):
            outside = np.array(1-inside,dtype=bool)
            warnings.warn('Wanted setting(s) {} not found. Allowed are {}'.format(newSettings[outside],settings.keys()))
        self._infos = [settings[I] for I in newSettings[inside]]


    def possibleInfos(self):
        return [key for key in self.possibleSettings]


    def currentInfos(self):
        return [setting.location for setting in self.infos]
        
    def settingsDialog(self):
        return self.possibleSettings,self.infos

ValidColour =  QtGui.QColor(255, 255, 255, 0)
InvalidColour = QtGui.QColor(255, 0, 0, 120)
class MatplotlibFigureListDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        """Delegate colouring the background of data files with the BG colour given by df.BGColor, default is ValidColor"""
        QtWidgets.QStyledItemDelegate.__init__(self, parent, *args)


    def paint(self, painter, option, index):
        super(MatplotlibFigureListDelegate,self).paint(painter, option, index)
        if True:
            
            figure = index.model().data(index,Qt.ItemDataRole)
            #print(figure._title,option._state)
            painter.save()
            painter.setPen(QtGui.QPen(Qt.NoPen))
            if not hasattr(figure,'closed'):
                c = ValidColour
            elif figure.closed: # If figure is closed, color the backgroud red
                c = InvalidColour
            else:
                c = ValidColour
            painter.setBrush(QtGui.QBrush(c))

            # Draw the background rectangle            
            painter.drawRect(option.rect)
            painter.restore()

class MatplotlibFigureList(QtCore.QAbstractListModel):
    def __init__(self, *args, combobox=None, **kwargs):
        super(MatplotlibFigureList, self).__init__(*args, **kwargs)
        self.figures = []
        
        self.view = combobox
        
    
    def setup(self):
        self.view.setModel(self)

    def data(self, index, role):
        if role == Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if hasattr(self.figures[index.row()],'_title'):
                text = self.figures[index.row()]._title
            else:
                text = 'NoTitle...'
            return text

        if role == Qt.ItemDataRole:
            return self.figures[index.row()]

    def getData(self,*args,**kwargs):
        return self.data(*args,**kwargs)

    def rowCount(self, index=None):
        return len(self.figures)
        

    def append(self,figure):
        if not hasattr(figure,'closed'):
            figure.closed = False
        self.figures.append(figure)

        self.selectLastFigure()
        self.layoutChanged.emit()

    
    #def delete(self,index):
    #    indices = [ind.row() for ind in index] # Extract numeric index, sort decending
    #    indices.sort(reverse=True)
    #    for ind in indices:
    #        try:
    #            del self.figures[ind]
    #            self.layoutChanged.emit()
    #        except:
    #            pass

    #    QtWidgets.QApplication.processEvents()
    #    index = self.getCurrentFigureIndex()
    #   
    #    if index is None:
    #        self.selectLastCut1D()
    #    else:
    #        if index.row()==self.rowCount(None):
    #            self.selectLastFigure()

    #def item(self,index,figureType=None):
    #    if not index is None:
    #        return self.figure[index.row()]

    def flags(self,index):
        #figure = self.figures[index.row()]
        #if figure.closed:
        #    return QtCore.Qt.ItemIsSelectable
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled #QtCore.Qt.ItemIsEditable  | 

    def getCurrentFigureIndex(self):
        index = self.view.currentIndex()
        if index is None:
            return None
        else:
            if index<self.rowCount(None):
                return index
            else:
                return None
        
    def getCurrentFigure(self):
        index = self.view.currentIndex()
        if index is None:
            return None
        else:
            if index<self.rowCount(None) and index>-1:
                return self.figures[index]
            else:
                return None

    #def getCurrentCut1DIndexRow(self):
    #    currentIndex = self.getCurrentCut1DIndex()
    #    if currentIndex is None:
    #        return None
    #    else:
    #        return currentIndex.row()

    #def getCurrentCut1D(self):
    #    index = self.getCurrentCut1DIndex()
    #    return self.item(index)

    def selectLastFigure(self):
        figures = self.rowCount(None)
        if figures!=0:
            index = self.index(self.rowCount(None)-1,0)
            self.view.setCurrentIndex(index.row())

    def closeAll(self):
        for fig in self.figures:
            self.close(fig)

    def close(self,figure):
        if hasattr(figure,'ax'):
            plt.close(figure.ax.get_figure())
            figure.closed = True
        else:
            try:
                plt.close(figure)
                figure.closed = True
            except:
                figure.parent().close()
                figure.closed = True
        self.layoutChanged.emit()
        #del figure

def formatLongInt(value):
    returnFormat = '{:d}'
    string = returnFormat.format(value)
    stringRemaining = string[::-1]
    newString = []
    
    while len(stringRemaining)>2:
        newString.append(stringRemaining[:3][::-1])
        stringRemaining = stringRemaining[3:]
    
    if len(stringRemaining)>0:
        padded = stringRemaining+' '*(3-len(stringRemaining))
        newString.append(padded[::-1])
    return ' '.join(newString[::-1])


class Scan(object):
    def __init__(self,Ei1,Ei2=None,s2t=None,A3Start=None,A3StepSize=None,A3Steps=None,monitor=None):

        self.Ei1 = Ei1
        self.Ei2 = Ei2
        self.s2t1 = s2t
        self.s2t2 = s2t+4
        self.A3Start = A3Start
        self.A3StepSize = A3StepSize
        self.A3Steps = A3Steps
        self.A3Stop = A3Start+A3StepSize*(A3Steps-1)
        self.monitorValue = monitor


    def timeEstimate(self,current=1.3):
        time = 0
        for e,stt in zip([self.Ei1,self.Ei1,self.Ei2,self.Ei2],[self.s2t1,self.s2t2,self.s2t2,self.s2t1]):
            if e is None:
                continue
            time += timeEstimate([e],self.monitorValue,self.A3Steps,A4s=1,current=current)
        return time

    @property
    def Ei(self):
        returnFormat = '{:.2f}'
        returnString = []
        for e in [self.Ei1,self.Ei2]:
            if e is None: continue
            returnString.append(returnFormat.format(e))
            
        return ', '.join(returnString)

    @property
    def s2t(self):
        returnFormat = '{:.2f}'
        returnString = []
        for s2t in [self.s2t1,self.s2t2]:
            if s2t is None: continue
            returnString.append(returnFormat.format(s2t))
            
        return ', '.join(returnString)

    @property
    def A3(self):
        returnFormat = '{:.1f}'
        returnString = []
        for s2t in [self.A3Start,self.A3StepSize,self.A3Stop]:
            returnString.append(returnFormat.format(s2t))
        returnString = '['+':'.join(returnString)+']'+'({:})'.format(self.A3Steps)
        return returnString

    @property
    def Monitor(self):
        return formatLongInt(self.monitorValue)
    
    
    def Time(self,current=None):
        return '{:.2f}'.format(self.timeEstimate(current=current)/(60*60))

    def timeDelta(self,current=None):
        return timedelta(seconds=self.timeEstimate(current=current))
   
    def finishTime(self,current=None,offset=datetime.now()):
        return '{:%A %H:%M}'.format(self.timeDelta(current=current)+offset)
    
    def toText(self,current=None,offset=datetime.now()):
        return ' | '.join([f'{st : ^20}' for st in [self.Ei,self.s2t,self.A3,self.Monitor,self.Time(current=current),self.finishTime(current=current,offset=offset)]])