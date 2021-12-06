import sys,os
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import loadUI, dialog
except ImportError:
    from _tools import loadUI, dialog
from os import path
import numpy as np
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from MJOLNIR.Data import DataFile


class customCheckBox(QtWidgets.QCheckBox):
    def __init__(self,*args,name=None,manager=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.stateChanged.connect(lambda state: manager.boxTicked(self,state))
        self.name = name


ElectronicLogBookManagerBase, ElectronicLogBookManagerForm = loadUI('ElectronicLogBookWidget.ui')

class ElectronicLogBookManager(ElectronicLogBookManagerBase, ElectronicLogBookManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(ElectronicLogBookManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.setWindowIcon(QtGui.QIcon(self.guiWindow.AppContext.get_resource('Icons/Own/book--pencil.png')))

        if not hasattr(self.guiWindow,'logbookPreset'):
            self.guiWindow.logbookPreset = []

        self.possibleParameters = DataFile.possibleAttributes
        self.initElectronicLogBookManager()
        self.initialMove()

        if 'saveToFile' in self.guiWindow.logbookPreset:
            self.ElectronicLogBook_savetofile_radioButton.setChecked(True)
        else:
            self.ElectronicLogBook_printinlog_radioButton.setChecked(True)

        self.checkDataSet()

    def initElectronicLogBookManager(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.dummyWidget = QtWidgets.QWidget()

        for par in self.possibleParameters:
            horizontal = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(par)
            tickBox = customCheckBox(name=par,manager=self)
            tickBox.setObjectName(par+'_checkBox')

            if not par in self.guiWindow.logbookPreset:
                checked = False
            else:
                checked = 2
            tickBox.setCheckState(checked)
            setattr(self,par+'_checkBox',tickBox)
            horizontal.addWidget(label)
            horizontal.addWidget(tickBox)
            self.layout.addLayout(horizontal)

        self.dummyWidget.setLayout(self.layout)
        self.parametersLayout.setWidget(self.dummyWidget)
        self.ElectronicLogBook_load_button.clicked.connect(self.load)
        self.ElectronicLogBook_dataset_button.clicked.connect(self.loadFromDataSet)
        self.ElectronicLogBook_savetofile_radioButton.toggled.connect(self.saveToFileChanged)
        self.guiWindow.DataSetModel.layoutChanged.connect(self.checkDataSet)
        
    
    def getPars(self):
        pars = self.guiWindow.logbookPreset
        for aux in ['saveToFile','printToLog']:
            if aux in pars: # remove the auxilliary entries
                del pars[pars.index(aux)]
        if not 'name' in pars:
            pars.insert(0,'name')
        return pars

    def load(self):
        pars = self.getPars()
        folder = self.guiWindow.getCurrentDirectory()
        allowedRawFilesString = 'Raw ('+' '.join(['*.'+str(x) for x in DataFile.supportedRawFormats])+')'
        allowedAllFilesString = 'All Files (*)'
        allowedString = ';;'.join([allowedRawFilesString,allowedAllFilesString])
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Open data Files", folder,allowedString)
        if files is None:
            return False
        if len(files) == 0:
            return False
        
        result = DataFile.shallowRead(files,pars)
        self.returnResult(pars,result)

    def loadFromDataSet(self):
        pars = self.getPars()
        ds = self.guiWindow.DataSetModel.getCurrentDataSet()
        files = [df.fileLocation for df in ds.dataFiles]
        if files is None:
            self.guiWindow.writeToStatus('Selected DataSet is empty')
            dialog('Selected DataSet is empty')
            return False
        if len(files) == 0:
            self.guiWindow.writeToStatus('Selected DataSet is empty')
            dialog('Selected DataSet is empty')
            return False
        
        result = DataFile.shallowRead(files,pars)
        self.returnResult(pars,result)
        
    def beautify(self,pars,result):
        returnString = []
        for fileResult in result:
            localReturnString = []
            for par,res in zip(pars,fileResult):
                if hasattr(res,'shape'):
                    if res.size == 1:
                        try:
                            localReturnString.append(' '+par+': '+str(res[0]))
                        except IndexError: # res = np.array(None) and the above throws an error!
                            localReturnString.append(' '+par+': None')
                    else:
                        try:
                            m = np.min(res)
                            M = np.max(res)
                        except TypeError:
                            localReturnString.append(' '+par+': '+str(res[0]))
                        else:
                            if np.isclose(m,M):
                                localReturnString.append(' '+par+': '+str(res[0]))
                            else:
                                localReturnString.append(' '+par+': [{} - {}]'.format(str(m),str(M)))
                else:
                    localReturnString.append(' '+par+': '+str(res))
            returnString.append(' '.join(localReturnString))

        returnString = '\n'.join([x for x in returnString])

        return returnString

    def returnResult(self,pars,result): # function to return result to user (either file or log)
        result = self.beautify(pars,result)
        if self.ElectronicLogBook_savetofile_radioButton.isChecked():
            saveLocation,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',None,"Text (*.txt)")
            if len(saveLocation) == 0:
                return False
            with open(saveLocation,'w') as f:
                f.writelines(result)
        else:
            self.guiWindow.writeToStatus(result)
        # After successful return, close window
        self.close()

    def checkDataSet(self):
        if self.guiWindow.DataSetModel.getCurrentDatasetIndex() is None:
            self.ElectronicLogBook_dataset_button.setDisabled(True)
        else:
            self.ElectronicLogBook_dataset_button.setDisabled(False)

    def initialMove(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QtCore.QPoint(qtRectangle.center().x(),int(qtRectangle.height()/2.0)+5) # Move widget 5 pixel from top edge
        
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def boxTicked(self,box,state):
        if state: # Going to true
            if not box.name in self.guiWindow.logbookPreset:
                self.guiWindow.logbookPreset.append(box.name)
        else:
            if box.name in self.guiWindow.logbookPreset:
                idx = self.guiWindow.logbookPreset.index(box.name)
                del self.guiWindow.logbookPreset[idx]

    def saveToFileChanged(self,state):
        if state: # changed to true
            if 'printToLog' in self.guiWindow.logbookPreset:
                del self.guiWindow.logbookPreset[self.guiWindow.logbookPreset.index('printToLog')]
            self.guiWindow.logbookPreset.append('saveToFile')
        else:
            if 'saveToFile' in self.guiWindow.logbookPreset:
                del self.guiWindow.logbookPreset[self.guiWindow.logbookPreset.index('saveToFile')]
            self.guiWindow.logbookPreset.append('printToLog')
        
        
        