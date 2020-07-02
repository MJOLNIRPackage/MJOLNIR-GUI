
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

import numpy as np
import sys
import warnings

from MJOLNIR import _tools as M_tools

try:
    from MJOLNIRGui.MJOLNIR_Data import GuiDataFile
except ImportError:
    from  MJOLNIR_Data import GuiDataFile

from os import path
from collections import namedtuple
try:
    import MJOLNIRGui._tools
except ImportError:
    import _tools

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
    
    




class DataFileModel(QtCore.QAbstractListModel):
    def __init__(self, *args, DataSet_filenames_listView=None,dataSetModel=None,DataSet_DataSets_listView=None,guiWindow=None, **kwargs):
        super(DataFileModel, self).__init__(*args, **kwargs)
        self.dataSetModel = dataSetModel
        self.DataSet_DataSets_listView = DataSet_DataSets_listView
        self.DataSet_filenames_listView = DataSet_filenames_listView
        self.guiWindow = guiWindow

        self.IconDict = defDict()
        self.IconDict['default']=QtGui.QImage(self.guiWindow.AppContext.get_resource('Icons/Own/document.png'))
        self.IconDict['hdf']=QtGui.QImage(self.guiWindow.AppContext.get_resource('Icons/Own/HDF_logo_16.png'))
        self.IconDict['nxs']=QtGui.QImage(self.guiWindow.AppContext.get_resource('Icons/Own/NXS_logo_16.png'))
        
    def data(self, index, role):

        if role == Qt.DisplayRole or role == Qt.EditRole:
            
            text = self.dataSetModel.item(self.getCurrentDatasetIndex())[index.row()].name
            return text
        
        if role == Qt.DecorationRole:
            t = self.dataSetModel.item(self.getCurrentDatasetIndex())[index.row()].type
            return self.IconDict[t]


    def getCurrentDatasetIndex(self):
        
        index = self.dataSetModel.getCurrentDatasetIndex()
        
        if index is None:
            return None
        else:
            return index

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
            if raw:
                dfs = [ds[idx] if not ds[idx].type == 'nxs' else ds[idx].original_file for idx in indexRows]
            else:
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
            dfs = [df if not df.type == 'nxs' else df.original_file for df in ds]
        else:
            dfs = [df for df in ds]
        
        return dfs

    def rowCount(self, index):
        ds = self.dataSetModel.getCurrentDataSet()
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
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def delete(self,idx=None):
        print(idx)
        if idx is None:
            ds = self.dataSetModel.item(self.getCurrentDatasetIndex())
        else:
            ds = self.dataSetModel.item(idx)
        indices = np.array(self.getCurrentDatafileIndexRows())
        if np.all([row<len(ds) for row in indices]):
            for idx in indices:
                del ds[idx]
                indices-=1
            self.layoutChanged.emit()
            self.guiWindow.updateDataFileLabels()


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
        guiWindow.updateDataFileLabels()


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
projectionVector1 = Info('sample/projectionVector1','Projection 1: ',formatVector)
projectionVector2 = Info('sample/projectionVector2','Projection 2: ',formatVector)
A3 = Info('A3','A3 [deg]: ',formatValueArray)
A4 = Info('A4','A4 [deg]: ',formatValueArray)
magneticField = Info('magneticField','Mag [B]: ',formatValueArray)
temperature = Info('temperature','Temperature [K]: ',formatValueArray)
scanCommand = Info('scanCommand','Command: ',formatTextArray)
scanSteps = Info('scanSteps','Scan steps: ',formatRaw)
scanParameters = Info('scanParameters','Parameter: ',formatTextArrayAdder)
comment = Info('comment','Comment: ',formatTextArray)
binning = Info('binning','Binning: ',formatRaw)
Ei = Info('Ei','Ei [meV]: ',formatValueArray)
countingTime = Info('Time', 'Scan step time [s]: ',formatValueArray)
startTime = Info('startTime', 'Start time: ', formatTextArrayAdder)
endTime = Info('endTime', 'End time: ', formatTextArrayAdder)

settings = {'sample/name':name,'sample/projectionVector1':projectionVector1,'sample/projectionVector2':projectionVector2,'Ei':Ei, 'A3':A3,'A4':A4, 'magneticField':magneticField,'temperature':temperature,
            'scanCommand':scanCommand, 'scanSteps':scanSteps, 'scanParameters':scanParameters, 'comment':comment, 'binning':binning,
            'Time':countingTime,'startTime':startTime, 'endTime':endTime}

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


