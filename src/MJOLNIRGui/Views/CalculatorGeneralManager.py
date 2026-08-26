import sys
#sys.path.append('..')

from MJOLNIR._tools import EnergyK,WavelengthK,WavelengthEnergy,EnergyWavelength,KEnergy,KWavelength
try:
    from _tools import loadUI
except (ModuleNotFoundError, ImportError):
    from MJOLNIRGui.src.main.python._tools import loadUI

from PyQt5 import QtGui

# Handles all functionality related to the CalculatorGeneralManager. 


CalculatorGeneralManagerBase, CalculatorGeneralManagerForm = loadUI('Calculator_General.ui')

       

def textChangedWavelength(manager):
    wavelength = manager.wavelength_spinBox.value()
    manager.q_spinBox.setValue(KWavelength(wavelength))
    manager.e_spinBox.setValue(EnergyWavelength(wavelength))

def textChangedEnergy(manager):
    E = manager.e_spinBox.value()
    manager.q_spinBox.setValue(KEnergy(E))
    manager.wavelength_spinBox.setValue(WavelengthEnergy(E))

def textChangedK(manager):
    k = manager.q_spinBox.value()
    manager.e_spinBox.setValue(EnergyK(k))
    manager.wavelength_spinBox.setValue(WavelengthK(k))

def onFocus(self,event,others):
    for o in others:
        try:
            o.valueChanged.disconnect()
        except TypeError: # If no connection to remove
            pass
    self.valueChanged.connect(self.onChangeFunction)
    self.old_focusInEvent(event)




class CalculatorGeneralManager(CalculatorGeneralManagerBase, CalculatorGeneralManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(CalculatorGeneralManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.setWindowIcon(QtGui.QIcon(self.guiWindow.AppContext.get_resource('Icons/Own/calculator.png')))

        self.initCalculatorGeneralManager()
        
    def initCalculatorGeneralManager(self):    
        self.setup()
        

    def setup(self):
        # Add updating functions to be called when text is changed
        self.wavelength_spinBox.onChangeFunction = lambda: textChangedWavelength(self)
        self.e_spinBox.onChangeFunction = lambda: textChangedEnergy(self)
        self.q_spinBox.onChangeFunction = lambda: textChangedK(self)
        
        # Move default focusInEvent
        self.wavelength_spinBox.old_focusInEvent = self.wavelength_spinBox.focusInEvent
        self.e_spinBox.old_focusInEvent = self.e_spinBox.focusInEvent
        self.q_spinBox.old_focusInEvent = self.q_spinBox.focusInEvent

        # Update to new 
        self.wavelength_spinBox.focusInEvent= lambda event: onFocus(self.wavelength_spinBox,event,[self.e_spinBox,self.q_spinBox])
        self.e_spinBox.focusInEvent = lambda event: onFocus(self.e_spinBox,event,[self.wavelength_spinBox,self.q_spinBox])
        self.q_spinBox.focusInEvent = lambda event: onFocus(self.q_spinBox,event,[self.wavelength_spinBox,self.e_spinBox])
        
