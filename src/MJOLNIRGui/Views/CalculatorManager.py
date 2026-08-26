from MJOLNIRGui.Views.CalculatorGeneralManager import CalculatorGeneralManager
from MJOLNIRGui.Views.CalculatorSimpleManager import CalculatorSimpleManager
from MJOLNIRGui.Views.CalculatorAdvancedManager import CalculatorAdvancedManager

from MJOLNIRGui._tools import loadUI


from MJOLNIRGui._qt import QtWidgets,QtGui



CalculatorManagerBase, CalculatorManagerForm = loadUI('Calculator.ui')

# All of this connects the buttons and their functions to the main window.
       


class CalculatorManager(CalculatorManagerBase, CalculatorManagerForm):
    def __init__(self,parent=None,guiWindow=None):

        super(CalculatorManager, self).__init__(parent=parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.setWindowIcon(QtGui.QIcon(self.guiWindow.AppContext.get_resource('Icons/Own/calculator.png')))

        self.nameList = ['General','Simple','Advanced'] 
        self.viewClasses = [CalculatorGeneralManager,CalculatorSimpleManager,CalculatorAdvancedManager]

        self.views = []

        # Find correct layout to insert views
        vlay = self.collapsibleContainer#QtWidgets.QVBoxLayout(self.ui.collapsibleContainer)
        # Insert all views
        self.boxContainers = []
        for name,Type in zip(self.nameList,self.viewClasses):
            self.update()
            box = QtWidgets.QGroupBox(title=name)#box = CollapsibleBox(name,startState=state)
            self.boxContainers.append(box)
            vlay.addWidget(box)
            lay = QtWidgets.QVBoxLayout()
            box.setLayout(lay)

            widget = Type(guiWindow=self.guiWindow)

            self.views.append(widget)
            lay.addWidget(widget)
           
        vlay.addStretch()

    