import sys,copy
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.python.DataModels import MaskModel
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiMask
    
except ImportError:
    from DataModels import MaskModel
    from MJOLNIR_Data import GuiMask
    from _tools import ProgressBarDecoratorArguments
    import _tools as _GUItools
from MJOLNIR.Data.Mask import MaskingObject
from os import path
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import numpy as np

from MJOLNIR.Data import Mask
import inspect

# Manually created for masking
objInfo =  {'indexMask': [('start', [float], 1, False),
  ('end', [float], 1, False),
  ('axis', [int], 1, True),
  ('maskInside', [bool], 1, True)],
 'lineMask': [('start', [float], 1, False),
  ('end', [float], 1, False),
  ('maskInside', [bool], 1, True)],
 'circleMask': [('center', [float, float], 2, False),
  ('radiusPoint', [float, float], 2, True),
  ('radius', [float, float], 2, True),
  ('maskInside', [bool], 1, True)],
 'rectangleMask': [('corner1', [float, float], 2, False),
  ('corner2', [float, float], 2, False),
  ('corner3', [float, float], 2, True),
  ('maskInside', [bool], 1, True)],
 'boxMask': [('corner1', [float, float, float], 3, False),
  ('corner2', [float, float, float], 3, False),
  ('corner3', [float, float, float], 3, False),
  ('corner4', [float, float, float], 3, True),
  ('maskInside', [bool], 1, True)]}


def Mask_DoubleClick_Selection_function(self,index,*args,**kwargs):
    self.Mask_listView.edit(index)

def setupMask(self):
    
    self.MaskModel = MaskModel(Mask_listView=self.Mask_listView,guiWindow=self.parent)
    self.Mask_listView.setModel(self.MaskModel)
    self.MaskModel.dataChanged.connect(self.MaskModel.layoutChanged.emit)

    self.MaskSelectionModel = self.Mask_listView.selectionModel()
    self.MaskSelectionModel.selectionChanged.connect(self.selectedMaskChanged)
    
    self.Mask_listView.doubleClicked.connect(self.Mask_DoubleClick_Selection_function)


def selectedMaskChanged(self,*args,**kwargs):
    self.updateMaskLabels()


def updateMaskLabels(self):
    masks = self.MaskModel.rowCount()
    if masks == 0:
        self.Mask_delete_button_nonBlock.setEnabled(False)
    else:
        self.Mask_delete_button_nonBlock.setEnabled(True)
    selected = self.Mask_listView.selectedIndexes()
    if len(np.asarray(selected))==0 or masks==0:
        self.Mask_duplicate_button_nonBlock.setEnabled(False)
        self.Mask_type_label.setText('')
    else:
        self.Mask_duplicate_button_nonBlock.setEnabled(True)
        if len(np.asarray(selected))>1:
            self.Mask_type_label.setText('Multiple')
        else:
            mask = self.MaskModel.item(np.asarray(selected)[0])
            maskType = type(mask.mask).__name__
            self.Mask_type_label.setText(maskType)


def parse(string,masks):
    for _ObscureName in masks:
        locals()[_ObscureName.name]=_ObscureName.mask
    return eval(string)


def MaskOnChange(self):
    self.Mask_parse_equation_text_edit_function()
    self.updateMaskLabels()


def Mask_parse_equation_text_edit_function(self):
    AppC = self.AppContext
    string = self.Mask_equation_text_edit.toPlainText()
    string = string.replace('\n','')
    string = string.strip()
    if len(string)==0:
        if hasattr(self.MaskModel,'combinedMask'):
            self.MaskModel.combinedMask = None
        img = QtGui.QPixmap(AppC.get_resource('Icons/Own/grey-led-on.png'))
    else:
        try:    
            combinedMask = parse(string,masks=self.MaskModel.masks)
        except (NameError,AttributeError,SyntaxError,TypeError):
            img = QtGui.QPixmap(AppC.get_resource('Icons/Own/red-led-on.png'))
            self.MaskModel.combinedMask = None
        else:
            img = QtGui.QPixmap(AppC.get_resource('Icons/Own/green-led-on.png'))
            self.MaskModel.combinedMask = combinedMask
    img = img.scaled(QtCore.QSize(16, 16))
    self.Mask_status_label.setPixmap(img)

def Mask_add_button_function(self):
    mask = self.maskingDialog(objInfo)

    if mask is None:
        return
    else:
        self.MaskModel.append(mask)


def Mask_delete_button_function(self):
    self.MaskModel.delete(self.Mask_listView.selectedIndexes())
    self.updateMaskLabels()
    self.MaskModel.layoutChanged.emit()
    self.updateMaskLabels()
    

def Mask_duplicate_button_nonBlock_function(self):
    self.MaskModel.layoutChanged.emit()
    items = self.MaskModel.item(self.Mask_listView.selectedIndexes())
    if items is None:
        return
    items = np.asarray(items)
    for item in items:
        newItem = copy.deepcopy(item)
        self.MaskModel.append(newItem)
    
    self.updateMaskLabels()
    self.MaskModel.layoutChanged.emit()

class maskingDialog(QtWidgets.QDialog):
    coordinates = ['h','k','l','energy','qx','qy','A3','A4']

    def __init__(self, maskInfoObject, *args, **kwargs):
        super(maskingDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("Masking")
        
        self.maskInfoObject = maskInfoObject  

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.titleLayout = QtWidgets.QHBoxLayout()
        self.titleLayout.setObjectName("titleLayout")
        self.maskTypeComboBox = QtWidgets.QComboBox(self)
        self.maskTypeComboBox.setObjectName("maskTypeComboBox")
        self.maskTypeComboBox.addItem("")
        self.maskTypeComboBox.addItem("")
        self.titleLayout.addWidget(self.maskTypeComboBox)
        self.maskNameEdit = QtWidgets.QLineEdit(self)
        self.maskNameEdit.setObjectName("maskNameEdit")
        self.titleLayout.addWidget(self.maskNameEdit)
        self.mainLayout.addLayout(self.titleLayout)
        self.inputLayoutOverview = QtWidgets.QHBoxLayout()
        self.inputLayoutOverview.setObjectName("inputLayoutOverview")

        self.cornerLayout = QtWidgets.QGridLayout()
        self.cornerLayout.setObjectName("cornerLayout")

        self.coordinateLabel = QtWidgets.QLabel(self)
        self.coordinateLabel.setObjectName("coordinateLabel")
        self.inputLayoutOverview.addWidget(self.coordinateLabel)
        
        self.mainLayout.addLayout(self.inputLayoutOverview)
        self.mainLayout.addLayout(self.cornerLayout)
        
        self.verticalLayout.addLayout(self.mainLayout)

        self.initiateComboBox()
        
        
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        

        
        self.verticalLayout.addWidget(self.buttonBox)
        self.setLayout(self.verticalLayout)

        self._changingBoxes = False

    def maskSelectionChanged(self,text):
        if text == '':
            return
        currentInfoParameters = self.maskInfoObject[text]
        self.clearInputLayout() # Clear layout
        self.clearCornerLayout()

        dimensionality = currentInfoParameters[0][2]
        
        self.coordinateLabel = QtWidgets.QLabel('Coordinates: ')
        self.inputLayoutOverview.addWidget(self.coordinateLabel)
        self.coordinateComboBoxes = []
        for i in range(dimensionality):
            box = QtWidgets.QComboBox(self)
            box.setObjectName("coordinateBox"+str(i))
            self.inputLayoutOverview.addWidget(box)
            for coord in self.coordinates:
                box.addItem(coord)
            
            self.coordinateComboBoxes.append(box)
        self.labels = [item[0] for item in currentInfoParameters]
        
        self.inputFields = []
        for i,label in enumerate(self.labels):
            localLabel = QtWidgets.QLabel(label)
            self.cornerLayout.addWidget(localLabel,i,0)
            for j,Type in enumerate(currentInfoParameters[i][1]):
                if Type in [float,int]:
                    inputField = QtWidgets.QLineEdit('')
                elif Type is bool:
                    inputField = QtWidgets.QCheckBox()
                else:
                    raise AttributeError()
                self.cornerLayout.addWidget(inputField,i,j+1)
                self.inputFields.append(inputField)

        
        
    def coordinateSelectonChanged(self,id,text):
        if self._changingBoxes or text == '': # If already changing the boxes through updating of items
            return
        print('Id {} changed to {}'.format(id,text))
        self._changingBoxes = True # Start changing the boxes
        totalCoordinates = self.coordinates.copy()
        currentCoordinates = [box.currentText() for box in self.coordinateComboBoxes]
        for box,prevCoord,ownCoord in zip(self.coordinateComboBoxes[1:],currentCoordinates,currentCoordinates[1:]):
            box.clear()
            totalCoordinates.remove(prevCoord)
            box.addItems(totalCoordinates)

        self._changingBoxes = False
            
        

    def clearInputLayout(self):
        for i in reversed(range(self.inputLayoutOverview.count())): 
            self.inputLayoutOverview.itemAt(i).widget().setParent(None)
    
    def clearCornerLayout(self):
        for i in reversed(range(self.cornerLayout.count())): 
            self.cornerLayout.itemAt(i).widget().setParent(None)

    def accept(self): # the accept button has been pressed
        coordinates = [box.currentText() for box in self.coordinateComboBoxes]
        MaskType = getattr(Mask,self.maskTypeComboBox.currentText())
        
        inputFields = {}
        for label,field in zip(self.labels, self.inputFields):
            value = field.text()
            if value == '':
                continue
            else:
                inputFields[label] = float(value)

        mask = MaskType(**inputFields,coordinates=coordinates)

        maskName = self.maskNameEdit.text()
        self.mask = GuiMask(maskName,mask)
        return super(maskingDialog,self).accept()

    def reject(self):
        return super(maskingDialog,self).reject()

    def initiateComboBox(self):
        self.maskTypeComboBox.currentTextChanged.connect(self.maskSelectionChanged)
        self.maskTypeComboBox.clear()  # Needed to clear empty input
        names = self.maskInfoObject.keys()
        for name in names:
            self.maskTypeComboBox.addItem(name)

class AnotherWindow(QtWidgets.QWidget):
    """
    Create class to handle second window
    """
    def __init__(self,widget,AppContext,parent):
        super().__init__()
        
        self.AppContext = AppContext
        layout = QtWidgets.QVBoxLayout()
        
        self.setLayout(layout)
        layout.addWidget(widget)
        self.parent = parent

    # Method to generate masking dialogue
    def maskingDialog(self,objInfo):
        dialog = maskingDialog(objInfo)

        if dialog.exec_(): # Execute the dialog
            return dialog.mask
        else:
            return None
        


try:
    MaskManagerBase, MaskManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Mask.ui"))
except:
    try:
        MaskManagerBase, MaskManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Mask.ui"))
    except:
        MaskManagerBase, MaskManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Mask.ui"))
class MaskManager(MaskManagerBase, MaskManagerForm):
    def __init__(self, parent=None):
        super(MaskManager, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        
        self.tester = AnotherWindow(widget=self,AppContext=self.parent.AppContext,parent=self.parent)
        self.tester.setVisible(False)
        self.initMaskManager()
        self.setup()


    def setWindowVisible(self):
        self.tester.setVisible(True)

    def initMaskManager(self):
        self.tester.Mask_add_button_function = lambda: Mask_add_button_function(self.tester)
        self.tester.Mask_duplicate_button_nonBlock_function = lambda: Mask_duplicate_button_nonBlock_function(self.tester)
        self.tester.Mask_parse_equation_text_edit_function = lambda: Mask_parse_equation_text_edit_function(self.tester)
        self.tester.setupMask = lambda: setupMask(self.tester)

        self.tester.Mask_DoubleClick_Selection_function = lambda index:Mask_DoubleClick_Selection_function(self.tester,index)
        self.tester.Mask_delete_button_function = lambda:Mask_delete_button_function(self.tester)
        self.tester.selectedMaskChanged = lambda : selectedMaskChanged(self.tester)
        self.tester.updateMaskLabels = lambda:updateMaskLabels(self.tester)
        self.tester.MaskOnChange = lambda:MaskOnChange(self.tester)
        for key,value in self.__dict__.items():
                if 'Mask' in key:
                    self.tester.__dict__[key] = value

        grey = '<img src="{}" width=16 height=16>'.format(self.parent.AppContext.get_resource('Icons/Own/grey-led-on.png'))
        red = '<img src="{}" width=16 height=16>'.format(self.parent.AppContext.get_resource('Icons/Own/red-led-on.png'))
        green = '<img src="{}" width=16 height=16>'.format(self.parent.AppContext.get_resource('Icons/Own/green-led-on.png'))
        img = QtGui.QPixmap(self.parent.AppContext.get_resource('Icons/Own/grey-led-on.png'))
        img = img.scaled(QtCore.QSize(16, 16))
        self.tester.Mask_status_label.setPixmap(img)
        self.tester.Mask_status_label.setToolTip('<br>'.join([grey+' no mask applied.',red+' wrong masking.',green+' correct masking.']))

        self.tester.Mask_apply_checkbox_nonBlock.stateChanged.connect(self.parent.mask_changed.emit)

        
    def setup(self):
        self.tester.setupMask()
        self.tester.updateMaskLabels()
        self.tester.Mask_delete_button_nonBlock.clicked.connect(self.tester.Mask_delete_button_function)
        self.tester.Mask_add_button_nonBlock.clicked.connect(self.tester.Mask_add_button_function)
        self.tester.Mask_duplicate_button_nonBlock.clicked.connect(self.tester.Mask_duplicate_button_nonBlock_function)
        self.tester.Mask_equation_text_edit.textChanged.connect(self.tester.Mask_parse_equation_text_edit_function)
        self.tester.MaskModel.layoutChanged.connect(self.tester.MaskOnChange)

    def getMasks(self):
        if self.tester.Mask_apply_checkbox_nonBlock.isChecked():
            mask = self.tester.MaskModel.combinedMask
        else:
            mask = None

        return mask
        
        

        
    