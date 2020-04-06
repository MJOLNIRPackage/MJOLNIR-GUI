from PyQt5 import QtCore
from MJOLNIR.Data import DataSet,DataFile

class GuiDataSet(DataSet.DataSet):
    def __init__(self,dataFiles=None,name='No Name', **kwargs):
        super(GuiDataSet,self).__init__(dataFiles=dataFiles,**kwargs)
        self.name = name
        
    
    def setData(self,column,value):
        if column == 0: self.name = value
        


    def flags(self):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable

class GuiDataFile(DataFile.DataFile):
    def __init__(self,fileLocation, **kwargs):
        super(GuiDataFile,self).__init__(fileLocation=fileLocation,**kwargs)
        
    def setData(self,column,value):
        if column == 0: self.name = value

    def flags(self):
        return QtCore.Qt.ItemIsEditable