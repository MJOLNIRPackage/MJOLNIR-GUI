import pickle as pickle
import os,traceback
import functools
from PyQt5 import QtCore,QtWidgets

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QCheckBox, QLabel,QApplication
from PyQt5 import uic
import platform
from os import path

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
            try:
                returnval = func(self,*args,**kwargs)
            except Exception:
                err = traceback.format_exc()
                state = self.stateMachine.currentState.name
                errText = 'MJOLNIRGui encountered an error with the following error message:\n\n{}\nMJOLNIRGui was in:{}\n\n'.format(str(err),state)+\
                    'If this is a recurring error, that you believe should be fixed, please  feel free to copy the message and '+\
                    'send it in an email to "MJOLNIRPackage@gmail.com".'
                
                dialog(errText)
                returnval = False

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
    dialog.setStyleSheet("messagebox-text-interaction-flags: 5")
    dialog.setIcon(QtWidgets.QMessageBox.Critical)
    dialog.setText(text)
    dialog.addButton(QtWidgets.QMessageBox.Ok)
    dialog.exec() 

def CenterWidgets(widget, host = None):
    if (host is None):
        host = widget.parentWidget()

    if (not host is None):
        hostRect = host.geometry()
        widget.move(hostRect.center() - widget.rect().center())
    
    else:
        screenGeometry = QApplication.desktop().screenGeometry()
        x = (screenGeometry.width() - widget.width()) / 2
        y = (screenGeometry.height() - widget.height()) / 2
        widget.move(x, y)
    

def loadUI(fileName):
    # print(platform.system().lower(),fileName)
    if platform.system().lower() == 'darwin':
        folder = path.abspath(path.join(path.dirname(__file__),'..','Resources','Views'))
    else: 
        folder = path.join(path.dirname(__file__),'..','..','resources','base','Views')


    try:
    # needed before freezing app
        base,form = uic.loadUiType(path.join(path.dirname(__file__),fileName))
    
    except FileNotFoundError:
        try:
            # needed when running app local through fbs
            base,form = uic.loadUiType(path.abspath(path.join(folder,fileName)))
            
        except FileNotFoundError:
            # needed when running app after pip install
            
            # except FileNotFoundError:
            #     base,form = uic.loadUiType(path.join(folder,fileName))
            try:
                base,form = uic.loadUiType(path.abspath(path.join(path.dirname(__file__),'..','resources','base','Views',fileName)))
                
            except FileNotFoundError:
                base,form = uic.loadUiType(path.abspath(path.join(path.dirname(__file__),'Views',fileName)))
    return base,form
        

class log(list):
    def __init__(self,textBrowser,button,maxLines = 80):
        self.maxLines = maxLines
        self.textBrowser = textBrowser
        self.button = button
        
        self.button.setDisabled(False)
        
    def clear(self):
        while len(self)>0:
            self.pop()

        self.updateTextBrowser()

    def trim(self):
        while len(self)>self.maxLines:
            self.pop()

    def updateTextBrowser(self):
        self.textBrowser.setText('\n'.join(self))
        if len(self) == 0:
            self.button.setDisabled(True)
        else:
            self.button.setDisabled(False)

    def __setitem__(self, key, value):
        super(log, self).__setitem__(key, value)
        self.updateTextBrowser()

    def __delitem__(self, value):
        super(log, self).__delitem__(value)
        self.updateTextBrowser()

    def __add__(self, value):
        super(log, self).__add__(value)
        self.trim()
        self.updateTextBrowser()
        

    def __iadd__(self, value):
        super(log, self).__iadd__(value)
        self.trim()
        self.updateTextBrowser()

    def append(self, value):
        super(log, self).insert(0,value)
        self.trim()
        self.updateTextBrowser()

    def remove(self, value):
        super(log, self).remove(value)
        self.updateTextBrowser()
        
