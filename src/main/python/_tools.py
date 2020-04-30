import pickle as pickle
import os
import functools
from PyQt5 import QtCore,QtWidgets

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QCheckBox, QLabel


def ProgressBarDecoratorArguments(runningText='Running',completedText='Completed',failedText='Failed'):

    def ProgressBarDecorator(func):
        @functools.wraps(func)
        def newFunc(self,*args,**kwargs):
            self.setProgressBarValue(0)
            self.setProgressBarLabelText(runningText)
            if len(args) == 1:
                args = ()
            else:
                args = args[1:]
            self.update()
            returnval = func(self,*args,**kwargs)

            self.setProgressBarMaximum(100)
            if returnval is not None:
                if returnval is False:
                    self.setProgressBarValue(0)
                    self.setProgressBarLabelText(failedText)
                    self.resetProgressBarTimed()
                    return returnval
        
            self.setProgressBarValue(100)
            self.setProgressBarLabelText(completedText)
            self.resetProgressBarTimed()
            return returnval
        return newFunc
    return ProgressBarDecorator


def loadSetting(settingsFile,string): # pragma: no cover
    if Exists(settingsFile):
        with open(settingsFile,"rb") as pickle_in:
            loaded_dict = pickle.load(pickle_in)
        if string in loaded_dict:
            returnValue = loaded_dict[string]
        else:
            returnValue = None
        return returnValue
    else:
        return None

def updateSetting(settingsFile, name,value):# pragma: no cover
    if Exists(settingsFile):
        with open(settingsFile,"rb") as pickle_in:
            loaded_dict = pickle.load(pickle_in)
    else:
        loaded_dict = {}
    loaded_dict[name]=value
    with open(settingsFile,"wb") as pickle_out:
        pickle.dump(loaded_dict, pickle_out,protocol=pickle.HIGHEST_PROTOCOL)

def Exists(settingsFile):# pragma: no cover
    return os.path.isfile(settingsFile)

def dialog(text):
    dialog = QtWidgets.QMessageBox()
    dialog.setIcon(QtWidgets.QMessageBox.Critical)
    dialog.setText(text)
    dialog.addButton(QtWidgets.QMessageBox.Ok)
    dialog.exec() 


class CheckBoxDialog(QDialog):

    def __init__(self, possibleSettings, currentSettings, *args, **kwargs):
        super(CheckBoxDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("Settings")
        self.possibleSettings = possibleSettings

        self.layout = QVBoxLayout()

        self.titleLabel = QLabel(text='Select infos to be shown for selected file(s)')
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(self.titleLabel)
        self.checkBoxes = []
        for setting in self.possibleSettings.values():
            checkBox = QCheckBox()
            self.checkBoxes.append(checkBox)
            name = setting.location
            checkBox.setText(name)
            checkBox.setChecked(setting in currentSettings)
            self.layout.addWidget(checkBox)
        
        
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def accept(self): # the accept button has been pressed
        
        self.newSettings = []
        for box,setting in zip(self.checkBoxes,self.possibleSettings.values()):
            if box.isChecked():
                self.newSettings.append(setting.location)

        super(CheckBoxDialog,self).accept()