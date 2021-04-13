import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
    import MJOLNIRGui.src.main.python._tools as _GUItools
except ImportError:
    from _tools import ProgressBarDecoratorArguments
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import numpy as np
from MJOLNIR._tools import calculateMolarMass,symbols,_relative_atomic_masses

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# Handles all functionality related to the MolecularCalculationManager. 

masses = _relative_atomic_masses.split(' ')

class ElementModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, elements=None, view=None, **kwargs):
        super(ElementModel, self).__init__(*args, **kwargs)
        self.view = view
        self.reset(elements)
       
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            column = index.column()
            if column == 0:
                return self.names[index.row()]
            elif column == 1:
                return self.numbers[index.row()]
            elif column == 2:
                return self.masses[index.row()]


    def getData(self,*args,**kwargs):
         return self.data(*args,**kwargs)

    def rowCount(self, index):
        return len(self.names)

    def columnCount(self,index):
        return 3

    def reset(self,elements):
        if elements is None:
            elements = {}
        self.elements = elements
        if len(elements)==0:
            self.names = []
            self.numbers = []
            self.masses = []
        else:
            self.names = list(elements.keys())
            self.numbers = list(elements.values())

            self.masses = [masses[list(symbols).index(name)] for name in self.names]

        self.layoutChanged.emit()
        self.dataChanged.emit(self.index(0,0),self.index(len(self.names),2))

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return ["Element", "Amount", "Mass [g/mol]"][section]


    def flags(self,index):
        return QtCore.Qt.ItemIsSelectable#QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable



def checkValidSampleFormula(self,text,sampleMassL):

    try:
        mass,elements = calculateMolarMass(text,returnElements=True)
        self.setStyleSheet("color: black;")
    except AttributeError as e:
        self.setStyleSheet("color: red;")
        mass = 0
        elements = {}

    if len(text)!=0 and mass==0: # A string was provided but no mass found, typically error in input
        self.setStyleSheet("color: red;")
    elif len(text)==0:
        mass,elements = calculateMolarMass(self.placeholderText(),returnElements=True)

    sampleMassL.setText(sampleMassL.textformat.format(mass))

    self.parent().elementModel.reset(elements)



try:
    MolecularCalculationManagerBase, MolecularCalculationManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"MolecularCalculationManager.ui"))
except:
    try:
        MolecularCalculationManagerBase, MolecularCalculationManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"MolecularCalculationManager.ui"))
    except:
        MolecularCalculationManagerBase, MolecularCalculationManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"MolecularCalculationManager.ui"))
# All of this connects the buttons and their functions to the main window.

class MolecularCalculationManager(MolecularCalculationManagerBase, MolecularCalculationManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(MolecularCalculationManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow


        self.elementModel = ElementModel()
        self.initMolecularCalculationManager()
        
    def initMolecularCalculationManager(self):    
        
        self.setup()
        

    def setup(self):
        sampleFormLE = self.MolecularCalculationManager_sampleFormula_lineEdit
        sampleMassL = self.MolecularCalculationManager_sampleMolarMass_label

        sampleMassL.textformat = "{:.6f} g/mol"

        # Connect the check validater when text is edited
        sampleFormLE.textChanged.connect(lambda text:checkValidSampleFormula(sampleFormLE,text,sampleMassL))
        self.MolecularCalculationManager_molarMass_tableView.setModel(self.elementModel)

        # Call textChanged with empty text to update list view
        sampleFormLE.textChanged.emit('')
        


