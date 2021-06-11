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
        self.BraggList_add_button.clicked.connect(self.BraggList_add_button_function)
        self.BraggList_delete_button.clicked.connect(self.BraggList_delete_button_function)
        self.BraggList_deleteAll_button.clicked.connect(self.BraggList_deleteAll_button_function)
        
        self.BraggListModel = BraggListModel(braggList_listView=self.BraggList_listView,BraggList=self.initBraggList)
        self.BraggList_listView.setModel(self.BraggListModel)

        self.BraggListSelectionModel = self.BraggList_listView.selectionModel()
        self.BraggListModel.layoutChanged.connect(self.selectedChanged)
        self.BraggListSelectionModel.selectionChanged.connect(self.selectedChanged)
        
    

    def selectedChanged(self,*args,**kwargs):
        if self.BraggListModel.rowCount() == 0:
            self.BraggList_deleteAll_button.setDisabled(True)
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
        self.BraggListModel.data = []
        self.BraggListModel.layoutChanged.emit()


    def extractBraggParamters(self):
        H = self.BraggList_H_spinBox.value()
        K = self.BraggList_K_spinBox.value()
        L = self.BraggList_L_spinBox.value()

        return H,K,L