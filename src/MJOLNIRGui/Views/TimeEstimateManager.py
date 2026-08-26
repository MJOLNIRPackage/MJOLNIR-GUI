import sys
sys.path.append('..')

try:
#    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.python.DataModels import ScanListModel,Scan
    from MJOLNIRGui.src.main.python._tools import loadUI
except ImportError:
    from DataModels import ScanListModel
    from _tools import loadUI
#    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import numpy as np
from datetime import datetime


ScanListManagerBase, ScanListManagerForm = loadUI('scanListWidget.ui')

class ScanListManager(ScanListManagerBase, ScanListManagerForm):
    def __init__(self, parent=None, guiWindow=None,scanList=None):
        super(ScanListManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initScanList = scanList
        self.initScanListManager()
        self.selectedChanged()

    def initScanListManager(self):
        # set multiple shortcuts for add_button
        for sequence in ("Ctrl+Enter", "Ctrl+Return",):
            shorcut = QtWidgets.QShortcut(sequence, self.ScanList_add_button)
            shorcut.activated.connect(self.ScanList_add_button_function)

        self.ScanList_add_button.clicked.connect(self.ScanList_add_button_function)
        self.ScanList_add_button.setShortcut("Ctrl+Return")
        self.ScanList_delete_button.clicked.connect(self.ScanList_delete_button_function)
        self.ScanList_delete_button.setShortcut("Delete")
        self.ScanList_deleteAll_button.clicked.connect(self.ScanList_deleteAll_button_function)
        self.ScanList_deleteAll_button.setShortcut("Ctrl+Delete")
        
        now = datetime.now()
        self.ScanList_startDate_dateTimeEdit.setDate(now)
        self.ScanList_startDate_dateTimeEdit.setTime(now.time())


        self.ScanListModel = ScanListModel(scanList_listView=self.ScanList_listView,scanList=self.initScanList,startTime=now)
        self.ScanList_listView.setModel(self.ScanListModel)

        self.ScanListSelectionModel = self.ScanList_listView.selectionModel()
        self.ScanListModel.layoutChanged.connect(self.selectedChanged)
        self.ScanListSelectionModel.selectionChanged.connect(self.selectedChanged)


        self.ScanList_s2t1_spinBox_valueChanged_function = lambda: fixS2t2(self.ScanList_s2t2_spinBox,self.ScanList_s2t1_spinBox)
        self.ScanList_s2t1_spinBox.valueChanged.connect(self.ScanList_s2t1_spinBox_valueChanged_function)

        self.ScanList_Ei1_spinBox._previousValue = self.ScanList_Ei1_spinBox.value()

        self.ScanList_Ei1_spinBox_valueChanged_function = lambda: updateEi2(self.ScanList_Ei2_spinBox,self.ScanList_Ei1_spinBox)
        self.ScanList_Ei1_spinBox.valueChanged.connect(self.ScanList_Ei1_spinBox_valueChanged_function)

        self.ScanList_startDate_dateTimeEdit_changed_function = lambda: self.ScanListModel.timeChanged(self.ScanList_startDate_dateTimeEdit.date(),self.ScanList_startDate_dateTimeEdit.time())
        self.ScanList_startDate_dateTimeEdit.dateChanged.connect(self.ScanList_startDate_dateTimeEdit_changed_function)
        self.ScanList_startDate_dateTimeEdit.timeChanged.connect(self.ScanList_startDate_dateTimeEdit_changed_function)

        self.ScanList_current_doubleSpinBox_changed_function = lambda: self.ScanListModel.currentChanged(self.ScanList_current_doubleSpinBox.value())
        self.ScanList_current_doubleSpinBox.valueChanged.connect(self.ScanList_current_doubleSpinBox_changed_function)


        self.setup()

   

    def setup(self):
        def deleteFunction(self,idx):
            self.ScanListModel.delete(idx)

        def contextMenu(view,event,gui):
            # Generate a context menu that opens on right click
            position = event.globalPos()
            idx = view.selectedIndexes()
            if len(idx)!=0:
                if event.type() == QtCore.QEvent.ContextMenu:
                    menu = QtWidgets.QMenu()
                    delete = QtWidgets.QAction('Delete')
                    delete.setToolTip('Delete DataSet') 
                    delete.setStatusTip(delete.toolTip())
                    delete.triggered.connect(lambda: deleteFunction(self,idx))
                    delete.setIcon(QtGui.QIcon(self.guiWindow.AppContext.get_resource('Icons/Own/cross-button.png')))
                    menu.addAction(delete)
            return menu.exec_(position)
        self.ScanList_listView.contextMenuEvent = lambda event: contextMenu(self.ScanList_listView,event,self)
        
    def closeEvent(self, event): # Function called on close event for the window
        self.guiWindow.braggPoints = self.getData()

    def selectedChanged(self,*args,**kwargs):
        if self.ScanListModel.rowCount() == 0:
            self.ScanList_deleteAll_button.setDisabled(True)
            self.ScanList_listView.clearSelection()
        else:
            self.ScanList_deleteAll_button.setDisabled(False)

        if len(self.ScanList_listView.selectedIndexes()) == 0:
            self.ScanList_delete_button.setDisabled(True)
        else:
            self.ScanList_delete_button.setDisabled(False)


        s = self.ScanListModel.getCurrentScan()

        self.setScan(s)

    
    
    def ScanList_delete_button_function(self):
        self.ScanListModel.delete(self.ScanList_listView.selectedIndexes())
        self.ScanListModel.layoutChanged.emit()

    def ScanList_add_button_function(self):
        s = self.extractScan()
        self.ScanListModel.append(s)

    def ScanList_deleteAll_button_function(self):
        self.ScanListModel.deleteAll()
        self.ScanListModel.layoutChanged.emit()

    def getData(self):
        data = self.ScanListModel.getAllData()
        if len(data) == 0:
            return None
        return data


    def extractScan(self):
        Ei1 = self.ScanList_Ei1_spinBox.value()
        Ei2 = self.ScanList_Ei2_spinBox.value()
        s2t1 = self.ScanList_s2t1_spinBox.value()
        
        A3Start = self.ScanList_a3start_spinBox.value()
        A3StepSize = self.ScanList_a3stepsize_spinBox.value()
        A3Steps = self.ScanList_a3steps_spinBox.value()

        Monitor = self.ScanList_monitor_spinBox.value()

        return Scan(Ei1=Ei1,Ei2=Ei2,s2t=s2t1,A3Start=A3Start,A3StepSize=A3StepSize,A3Steps=A3Steps,monitor=Monitor)
    
    def setScan(self,s):
        if s is None:
            return
        
        Ei1 = s.Ei1
        Ei2 = s.Ei2
        s2t1 = s.s2t1
        s2t2 = s.s2t2
        A3Start = s.A3Start
        A3StepSize = s.A3StepSize
        A3Steps = s.A3Steps
        A3Stop = s.A3Stop
        monitor = s.monitorValue


        self.ScanList_Ei1_spinBox.setValue(Ei1)
        self.ScanList_Ei2_spinBox.setValue(Ei2)
        self.ScanList_s2t1_spinBox.setValue(s2t1)
        
        self.ScanList_a3start_spinBox.setValue(A3Start)
        self.ScanList_a3stepsize_spinBox.setValue(A3StepSize)
        self.ScanList_a3steps_spinBox.setValue(A3Steps)
        self.ScanList_monitor_spinBox.setValue(monitor)

        
def fixS2t2(s2t1_spinBox,s2t2_spinBox):
    s2t1_spinBox.setValue(s2t2_spinBox.value()+4.0)

def updateEi2(Ei2_spinBox,Ei1_spinBox):
    delta = Ei1_spinBox.value()-Ei1_spinBox._previousValue
    Ei1_spinBox._previousValue = Ei1_spinBox.value()
    Ei2_spinBox.setValue(Ei2_spinBox.value()+delta)