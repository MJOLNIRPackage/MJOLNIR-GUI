import sys
sys.path.append('..')

from os import path

from PyQt5 import uic
from MJOLNIR._tools import DSpacing,ScatteringAngle

# Handles all functionality related to the CalculatorSimpleManager. 

try:
    CalculatorSimpleManagerBase, CalculatorSimpleManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Calculator_Simple.ui"))
except:
    try:
        CalculatorSimpleManagerBase, CalculatorSimpleManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Calculator_Simple.ui"))
    except:
        CalculatorSimpleManagerBase, CalculatorSimpleManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Calculator_Simple.ui"))
# All of this connects the buttons and their functions to the main window.
       

def textChangedA4(manager):
    A4 = manager.a4_spinBox.value()
    E = manager.e_spinBox.value()
    manager.d_spinBox.setValue(DSpacing(A4,Energy=E))
    

def textChangedEnergy(manager):
    E = manager.e_spinBox.value()
    D = manager.d_spinBox.value()
    manager.a4_spinBox.setValue(ScatteringAngle(D,Energy=E))
    

def textChangedD(manager):
    D = manager.d_spinBox.value()
    E = manager.e_spinBox.value()
    manager.a4_spinBox.setValue(ScatteringAngle(D,Energy=E))


def onFocus(self,event,others):
    for o in others:
        try:
            o.valueChanged.disconnect()
        except TypeError: # If no connection to remove
            pass
    self.valueChanged.connect(self.onChangeFunction)
    self.old_focusInEvent(event)




class CalculatorSimpleManager(CalculatorSimpleManagerBase, CalculatorSimpleManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(CalculatorSimpleManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow

        self.initCalculatorSimpleManager()
        
    def initCalculatorSimpleManager(self):    
        self.setup()
        

    def setup(self):
        # Add updating functions to be called when text is changed
        self.a4_spinBox.onChangeFunction = lambda: textChangedA4(self)
        self.e_spinBox.onChangeFunction = lambda: textChangedEnergy(self)
        self.d_spinBox.onChangeFunction = lambda: textChangedD(self)
        
        # Move default focusInEvent
        self.a4_spinBox.old_focusInEvent = self.a4_spinBox.focusInEvent
        self.e_spinBox.old_focusInEvent = self.e_spinBox.focusInEvent
        self.d_spinBox.old_focusInEvent = self.d_spinBox.focusInEvent

        # Update to new 
        self.a4_spinBox.focusInEvent= lambda event: onFocus(self.a4_spinBox,event,[self.e_spinBox,self.d_spinBox])
        self.e_spinBox.focusInEvent = lambda event: onFocus(self.e_spinBox,event,[self.a4_spinBox,self.d_spinBox])
        self.d_spinBox.focusInEvent = lambda event: onFocus(self.d_spinBox,event,[self.a4_spinBox,self.e_spinBox])
        
