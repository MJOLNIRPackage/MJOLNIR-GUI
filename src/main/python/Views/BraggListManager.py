import sys
sys.path.append('..')

try:
#    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.python.DataModels import BraggListModel
    from MJOLNIRGui.src.main.python._tools import loadUI
except ImportError:
    from DataModels import BraggListModel
    from _tools import loadUI
#    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import numpy as np



BraggListManagerBase, BraggListManagerForm = loadUI('braggListWidget.ui')

class BraggListManager(BraggListManagerBase, BraggListManagerForm):
    def __init__(self, parent=None, guiWindow=None,BraggList=None):
        super(BraggListManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initBraggList = BraggList
        self.initBraggListManager()
        self.selectedChanged()

    def initBraggListManager(self):
        # set multiple shortcuts for add_button
        for sequence in ("Ctrl+Enter", "Ctrl+Return",):
            shorcut = QtWidgets.QShortcut(sequence, self.BraggList_add_button)
            shorcut.activated.connect(self.BraggList_add_button_function)

        self.BraggList_delete_button.clicked.connect(self.BraggList_delete_button_function)
        self.BraggList_delete_button.setShortcut("Delete")
        self.BraggList_deleteAll_button.clicked.connect(self.BraggList_deleteAll_button_function)
        self.BraggList_deleteAll_button.setShortcut("Ctrl+Delete")

        self.BraggListModel = BraggListModel(braggList_listView=self.BraggList_listView,BraggList=self.initBraggList)
        self.BraggList_listView.setModel(self.BraggListModel)

        self.BraggListSelectionModel = self.BraggList_listView.selectionModel()
        self.BraggListModel.layoutChanged.connect(self.selectedChanged)
        self.BraggListSelectionModel.selectionChanged.connect(self.selectedChanged)
        
    def closeEvent(self, event): # Function called on close event for the window
        self.guiWindow.braggPoints = self.getData()

    def selectedChanged(self,*args,**kwargs):
        if self.BraggListModel.rowCount() == 0:
            self.BraggList_deleteAll_button.setDisabled(True)
            self.BraggList_listView.clearSelection()
        else:
            self.BraggList_deleteAll_button.setDisabled(False)

        if len(self.BraggList_listView.selectedIndexes()) == 0:
            self.BraggList_delete_button.setDisabled(True)
        else:
            self.BraggList_delete_button.setDisabled(False)
    
    
    def BraggList_delete_button_function(self):
        self.BraggListModel.delete(self.BraggList_listView.selectedIndexes())
        self.BraggListModel.layoutChanged.emit()

    def BraggList_add_button_function(self):
        HKL = self.extractBraggParamters()
        self.BraggListModel.append(HKL)

    def BraggList_deleteAll_button_function(self):
        self.BraggListModel.deleteAll()
        self.BraggListModel.layoutChanged.emit()

    def getData(self):
        data = self.BraggListModel.getAllData()
        if len(data) == 0:
            return None
        return data


    def extractBraggParamters(self):
        H = self.BraggList_H_spinBox.value()
        K = self.BraggList_K_spinBox.value()
        L = self.BraggList_L_spinBox.value()

        return H,K,L