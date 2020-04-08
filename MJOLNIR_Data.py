from PyQt5 import QtCore
from MJOLNIR.Data import DataSet,DataFile

class GuiDataSet(DataSet.DataSet):
    def __init__(self,dataFiles=None,name='No Name', **kwargs):
        super(GuiDataSet,self).__init__(dataFiles=dataFiles,**kwargs)
        self.name = name
        
    
    def setData(self,column,value):
        if column == 0: self.name = value
        
    def convertDataFile(self,dataFiles=None,binning=None,guiWindow=None):
        
        dataFiles = self.dataFiles
        if not guiWindow is None:
            guiWindow.setProgressBarMaximum(len(dataFiles)+1)

        convertedFiles = []
        for i,rawfile in enumerate(dataFiles):
            convFile = rawfile.convert(binning)
                
            convertedFiles.append(convFile)
            guiWindow.setProgressBarValue(i+1)
            
        self._convertedFiles = []
        self.convertedFiles = convertedFiles    
        self._getData()
        guiWindow.setProgressBarValue(len(dataFiles))


    def flags(self):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable

class GuiDataFile(DataFile.DataFile):
    def __init__(self,fileLocation, **kwargs):
        super(GuiDataFile,self).__init__(fileLocation=fileLocation,**kwargs)

    def setData(self,column,value):
        if column == 0: self.name = value

    def flags(self):
        return QtCore.Qt.ItemIsEditable

    def convert(self,*args,**kwargs):
        convertedFile = super(GuiDataFile, self).convert(*args, **kwargs)
        self.converted = True
        self.name = '.'.join(self.name.split('.')[:-1])+'.nxs'

        return convertedFile