import sys
sys.path.append('..')
sys.path.append('.')

try:
    from Views.CalculatorGeneralManager import CalculatorGeneralManager
    from Views.CalculatorSimpleManager import CalculatorSimpleManager
    from Views.CalculatorAdvancedManager import CalculatorAdvancedManager
    from Views.collapsibleBox import CollapsibleBox
except ModuleNotFoundError:
    from MJOLNIRGui.src.main.python.Views.CalculatorGeneralManager import CalculatorGeneralManager
    from MJOLNIRGui.src.main.python.Views.CalculatorSimpleManager import CalculatorSimpleManager
    from MJOLNIRGui.src.main.python.Views.CalculatorAdvancedManager import CalculatorAdvancedManager   
    from MJOLNIRGui.src.main.python.Views.collapsibleBox import CollapsibleBox


from os import path
from PyQt5 import QtWidgets,uic,QtGui,QtCore


try:
    CalculatorManagerBase, CalculatorManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Calculator.ui"))
except:
    try:
        CalculatorManagerBase, CalculatorManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Calculator.ui"))
    except:
        CalculatorManagerBase, CalculatorManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Calculator.ui"))
# All of this connects the buttons and their functions to the main window.
       


class CalculatorManager(CalculatorManagerBase, CalculatorManagerForm):
    def __init__(self):

        super(CalculatorManager, self).__init__()
        self.setupUi(self)

        self.nameList = ['General','Simple','Advanced'] 
        self.viewClasses = [CalculatorGeneralManager,CalculatorSimpleManager,CalculatorAdvancedManager]
        self.startState = [True,True,True] # If extended 

        self.views = []

        # Find correct layout to insert views
        vlay = self.collapsibleContainer#QtWidgets.QVBoxLayout(self.ui.collapsibleContainer)
        # Insert all views
        self.boxContainers = []
        for name,Type,state in zip(self.nameList,self.viewClasses,self.startState):
            self.update()
            box = CollapsibleBox(name,startState=state)
            self.boxContainers.append(box)
            vlay.addWidget(box)
            lay = QtWidgets.QVBoxLayout()

            widget = Type(guiWindow=self)
            #if Type == NormalizationManager: # Get a reference to the sample manager directly in self
            #    self.normalizationManager = widget
            self.views.append(widget)
            lay.addWidget(widget)
           
            box.setContentLayout(lay)
        vlay.addStretch()

    