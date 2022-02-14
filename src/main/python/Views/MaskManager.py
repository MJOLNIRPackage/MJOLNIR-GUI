import sys,copy
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments, loadUI
    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.python.DataModels import MaskModel
    from MJOLNIRGui.src.main.python.Views import BraggListManager
    #from MJOLNIRGui.src.main.python.MJOLNIR_Data import GuiMask
    
except ImportError:
    from DataModels import MaskModel
    #from MJOLNIR_Data import GuiMask
    from _tools import ProgressBarDecoratorArguments, loadUI
    import _tools as _GUItools
    from Views import BraggListManager
from MJOLNIR.Data import Mask
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import numpy as np
import os
import inspect


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
            maskType = type(mask).__name__
            self.Mask_type_label.setText(maskType)


def parse(string,masks):
    for _ObscureName in masks:
        locals()[_ObscureName.name]=_ObscureName
    return eval(string)


def MaskOnChange(self):
    self.Mask_parse_equation_text_edit_function()
    self.updateMaskLabels()


def Mask_parse_equation_text_edit_function(self):
    AppC = self.AppContext
    string = self.Mask_equation_line_edit.text()
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
            if not isinstance(combinedMask,(Mask.MaskingObject)):
                img = QtGui.QPixmap(AppC.get_resource('Icons/Own/red-led-on.png'))
                self.MaskModel.combinedMask = None
            else:
                img = QtGui.QPixmap(AppC.get_resource('Icons/Own/green-led-on.png'))
                self.MaskModel.combinedMask = combinedMask
    img = img.scaled(QtCore.QSize(16, 16))
    self.Mask_status_label.setPixmap(img)
    self.maskingManager.performButtonChecks()

def Mask_add_button_function(self,oldMask=None):
    mask = self.maskingDialog(oldMask = oldMask)

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


### Define masks and their functions

maskTypes = {
    'Index Mask': 'loadIndexMask',
    'Line Mask': 'loadLineMask',
    'Rectangular Mask': 'loadRectangleMask',
    'Circular Mask': 'loadCircleMask',
    'Currat Axe Mask': 'loadCurratAxeMask',
    '3D Box Mask': 'loadBoxMask',
}

translate = {
    'indexMask': 'Index Mask',
    'lineMask': 'Line Mask',
    'rectangleMask': 'Rectangular Mask',
    'circleMask': 'Circular Mask',
    'CurratAxeMask': 'Currat Axe Mask',
    'boxMask': '3D Box Mask'
}


class maskingDialog(QtWidgets.QWidget):
    coordinates = ['h','k','l','energy','qx','qy','A3','A4']

    def __init__(self,  maskingManager, oldMask = None, *args, **kwargs):
        super(maskingDialog, self).__init__(*args, **kwargs)
        self.maskingManager = maskingManager
        self.MaskModel = self.maskingManager.maskingMainWindow.MaskModel
        self.oldMask = oldMask
        self.setWindowTitle("Masking")
        
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
        if not oldMask is None:
            self.maskNameEdit.setText(oldMask.name)
        self.titleLayout.addWidget(self.maskNameEdit)
        self.mainLayout.addLayout(self.titleLayout)
        self.inputLayoutOverview = QtWidgets.QHBoxLayout()
        self.inputLayoutOverview.setObjectName("inputLayoutOverview")

        self.cornerLayout = QtWidgets.QGridLayout()
        self.cornerLayout.setObjectName("cornerLayout")

        # self.coordinateLabel = QtWidgets.QLabel(self)
        # self.coordinateLabel.setObjectName("coordinateLabel")
        # self.inputLayoutOverview.addWidget(self.coordinateLabel)
        
        self.mainLayout.addLayout(self.inputLayoutOverview)
        self.mainLayout.addLayout(self.cornerLayout)
        self.verticalLayout.addLayout(self.mainLayout)

        self.initiateComboBox(mask=oldMask)
        if not oldMask is None:
            self.loadMaskType(translate[type(oldMask).__name__],oldMask)
        else:
            self.maskTypeComboBox.setCurrentIndex(0)
        
        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        
        
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setShortcut("Ctrl+Return")
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).setShortcut("Esc")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        

        
        self.verticalLayout.addWidget(self.buttonBox)
        self.setLayout(self.verticalLayout)

        self._changingBoxes = False
        

    def maskSelectionChanged(self,text):
        if text == '':
            return
        
        self.clearInputLayout() # Clear layout
        self.clearCornerLayout()
        self.loadMaskType(text)

    def loadMaskType(self,text,mask=None):
        if text in ['']:#self.simpleMaskParameters.keys():
            currentInfoParameters = self.simpleMaskParameters[text]
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
                    if Type is float:
                        inputField = QtWidgets.QDoubleSpinBox()
                    elif Type is int:
                        inputField = QtWidgets.QSpinBox()
                    elif Type is bool:
                        inputField = QtWidgets.QCheckBox()
                    else:
                        raise AttributeError()
                    self.cornerLayout.addWidget(inputField,i,j+1)
                    self.inputFields.append(inputField)

        elif text in maskTypes:
            getattr(self,maskTypes[text])(mask=mask)
            
    def loadIndexMask(self,mask):
        labels = []
        self.widgets = []
        labels.append(QtWidgets.QLabel('Index Start'))
        self.widgets.append(QtWidgets.QSpinBox())
        
        labels.append(QtWidgets.QLabel('Index End'))
        self.widgets.append(QtWidgets.QSpinBox())
        
        labels.append(QtWidgets.QLabel('Axis'))
        axisComboBox=QtWidgets.QComboBox()
        axisComboBox.addItems(list(map(str,range(3))))
        axisComboBox.setCurrentIndex(0)
        self.widgets.append(axisComboBox)

        labels.append(QtWidgets.QLabel('Mask Inside'))
        self.widgets.append(QtWidgets.QCheckBox())

        params = ['start','end','axis','maskInside']
        if not mask is None:
            values = [getattr(mask,p) for p in params]
        else:
            values = [None for p in params]

        for i,(label,widget,value) in enumerate(zip(labels,self.widgets,values)):
            self.cornerLayout.addWidget(label,i,0)
            self.cornerLayout.addWidget(widget,i,1)
            if not value is None:
                if isinstance(widget,(QtWidgets.QSpinBox)):
                    widget.setValue(value)
                elif isinstance(widget,(QtWidgets.QComboBox)):
                    idx = widget.findText(str(value))
                    widget.setCurrentIndex(idx)
                elif isinstance(widget,(QtWidgets.QCheckBox)):
                    widget.setChecked(value)


        def acceptFunction(self):
            inputFields = {}
            inputFields['start'] = self.widgets[0].value()
            inputFields['end'] = self.widgets[1].value()
            inputFields['axis'] = int(self.widgets[2].currentText())
            inputFields['maskInside'] = self.widgets[3].isChecked()
            return inputFields

        self.acceptFunction = lambda: acceptFunction(self)

    def loadLineMask(self,mask):
        labels = []
        self.widgets = []

        labels.append(QtWidgets.QLabel('Coordinate'))
        axisComboBox=QtWidgets.QComboBox()
        axisComboBox.addItems(self.coordinates)
        axisComboBox.setCurrentIndex(0)
        self.widgets.append(axisComboBox)

        labels.append(QtWidgets.QLabel('Start'))
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)
        
        labels.append(QtWidgets.QLabel('End'))
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)
        
        

        labels.append(QtWidgets.QLabel('Mask Inside'))
        self.widgets.append(QtWidgets.QCheckBox())

        params = ['coordinates','start','end','maskInside']
        if not mask is None:
            values = [getattr(mask,p) for p in params]
        else:
            values = [None for p in params]

        for i,(label,widget,value) in enumerate(zip(labels,self.widgets,values)):
            self.cornerLayout.addWidget(label,i,0)
            self.cornerLayout.addWidget(widget,i,1)
            if not value is None:
                if isinstance(widget,(QtWidgets.QSpinBox,QtWidgets.QDoubleSpinBox)):
                    widget.setValue(value)
                elif isinstance(widget,(QtWidgets.QComboBox)):
                    idx = widget.findText(str(value[0]))
                    widget.setCurrentIndex(idx)
                elif isinstance(widget,(QtWidgets.QCheckBox)):
                    widget.setChecked(value)


        def acceptFunction(self):
            inputFields = {}
            inputFields['start'] = self.widgets[1].value()
            inputFields['end'] = self.widgets[2].value()
            inputFields['coordinates'] = [self.widgets[0].currentText()]
            inputFields['maskInside'] = self.widgets[3].isChecked()
            return inputFields

        self.acceptFunction = lambda: acceptFunction(self)

    def loadRectangleMask(self,mask):
        labels = []
        self.widgets = []
        
        
        labels.append(QtWidgets.QLabel('Coordinates'))
        axisComboBox=QtWidgets.QComboBox()
        axisComboBox.addItems(self.coordinates)
        axisComboBox.setCurrentIndex(0)
        self.widgets.append(axisComboBox)
        axisComboBox=QtWidgets.QComboBox()
        axisComboBox.addItems(self.coordinates)
        axisComboBox.setCurrentIndex(1)
        self.widgets.append(axisComboBox)

        labels.append(QtWidgets.QLabel('Corner 1'))
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)
        
        labels.append(QtWidgets.QLabel('Corner 2'))
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)

        self.corner3CheckBox = QtWidgets.QCheckBox()
        self.corner3CheckBox.setText('Corner 3')
        
        def onToggle(value,self):
            
            for spinBox in self.widgets[6:8]:
                if value:
                    spinBox.setDisabled(False)
                else:
                    spinBox.setDisabled(True)
        self.corner3CheckBox.toggled.connect(lambda value: onToggle(value,self))
        
        
        labels.append(self.corner3CheckBox)
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)
        DSBox = QtWidgets.QDoubleSpinBox()
        DSBox.setMaximum(1e6)
        DSBox.setMinimum(-1e6)
        self.widgets.append(DSBox)
        
        self.corner3CheckBox.setChecked(True)
        
        labels.append(QtWidgets.QLabel('Mask Inside'))
        self.widgets.append(QtWidgets.QCheckBox())

        params = ['coordinates','corner1','corner2','corner3','maskInside']
        if not mask is None:
            values = [getattr(mask,p) for p in params]
        else:
            values = [None for p in params]

        for i,(label,value) in enumerate(zip(labels,values)):
            self.cornerLayout.addWidget(label,i,0)
            w1 = self.widgets[2*i]
            self.cornerLayout.addWidget(w1,i,1)
            if len(self.widgets)!=i*2+1:
                w2 = self.widgets[2*i+1]
                self.cornerLayout.addWidget(w2,i,1+1)
            else:
                w2 = None

            if not value is None:
                if isinstance(w1,(QtWidgets.QSpinBox,QtWidgets.QDoubleSpinBox)):
                    w1.setValue(value[0])
                    w2.setValue(value[1])
                elif isinstance(w1,(QtWidgets.QComboBox)):
                    w1.setCurrentIndex(w1.findText(str(value[0])))
                    w1.setCurrentIndex(w2.findText(str(value[1])))
                elif isinstance(w1,(QtWidgets.QCheckBox)):
                    w1.setChecked(value)


        def acceptFunction(self):
            inputFields = {}
            inputFields['coordinates'] = [self.widgets[0].currentText(),self.widgets[1].currentText()]
            inputFields['corner1'] = [self.widgets[2].value(),self.widgets[3].value()]
            inputFields['corner2'] = [self.widgets[4].value(),self.widgets[5].value()]
            if self.corner3CheckBox.isChecked():
                inputFields['corner3'] = [self.widgets[6].value(),self.widgets[7].value()]
            inputFields['maskInside'] = self.widgets[8].isChecked()
            return inputFields

        self.acceptFunction = lambda: acceptFunction(self)
    
    def loadBoxMask(self,mask):
        labels = []
        self.widgets = []
        dimensionality = 3
        def onToggle(value,widgets):
            
            for spinBox in widgets:
                if value:
                    spinBox.setDisabled(False)
                else:
                    spinBox.setDisabled(True)
        
        labels.append(QtWidgets.QLabel('Coordinates'))
        for i in range(dimensionality):
            axisComboBox=QtWidgets.QComboBox()
            axisComboBox.addItems(self.coordinates)
            axisComboBox.setCurrentIndex(i)
            self.widgets.append(axisComboBox)

        labels.append(QtWidgets.QLabel('Corner 1'))
        for _ in range(dimensionality):
            DSBox = QtWidgets.QDoubleSpinBox()
            DSBox.setMaximum(1e6)
            DSBox.setMinimum(-1e6)
            self.widgets.append(DSBox)

        labels.append(QtWidgets.QLabel('Corner 2'))
        for _ in range(dimensionality):
            DSBox = QtWidgets.QDoubleSpinBox()
            DSBox.setMaximum(1e6)
            DSBox.setMinimum(-1e6)
            self.widgets.append(DSBox)
        
        labels.append(QtWidgets.QLabel('Corner 3'))
        for _ in range(dimensionality):
            DSBox = QtWidgets.QDoubleSpinBox()
            DSBox.setMaximum(1e6)
            DSBox.setMinimum(-1e6)
            self.widgets.append(DSBox)

        
        self.corner4CheckBox = QtWidgets.QCheckBox()
        self.corner4CheckBox.setText('Corner 4')
        labels.append(self.corner4CheckBox)

        for _ in range(dimensionality):
            
            DSBox = QtWidgets.QDoubleSpinBox()
            DSBox.setMaximum(1e6)
            DSBox.setMinimum(-1e6)
            self.widgets.append(DSBox)
        widgets = len(self.widgets)
        self.corner4CheckBox.toggled.connect(lambda value: onToggle(value,self.widgets[widgets-dimensionality:widgets]))
        
        self.corner4CheckBox.setChecked(False)
        self.corner4CheckBox.setChecked(True)
        
        labels.append(QtWidgets.QLabel('Mask Inside'))
        self.widgets.append(QtWidgets.QCheckBox())

        params = ['coordinates','corner1','corner2','corner3','corner4','maskInside']
        sizes = [dimensionality,dimensionality,dimensionality,dimensionality,dimensionality,1]
        if not mask is None:
            values = [getattr(mask,p) for p in params]
        else:
            values = [[None]*s for s in sizes]

        for i,(label,value) in enumerate(zip(labels,values)):
            self.cornerLayout.addWidget(label,i,0)

            if isinstance(value,(bool)):
                value = [value]
            elif isinstance(value,(np.ndarray)):
                if np.any(np.isnan(value)):
                    value = [None]*dimensionality
            for j,val in enumerate(value):
                w = self.widgets[i*dimensionality+j]
                self.cornerLayout.addWidget(w,i,j+1)
                if not val is None:
                    if isinstance(w,(QtWidgets.QSpinBox,QtWidgets.QDoubleSpinBox)):
                        w.setValue(val)
                    elif isinstance(w,(QtWidgets.QComboBox)):
                        w.setCurrentIndex(w.findText(str(val)))
                    elif isinstance(w,(QtWidgets.QCheckBox)):
                        w.setChecked(val)

        def acceptFunction(self):
            inputFields = {}
            inputFields['coordinates'] = [x.currentText() for x in self.widgets[:dimensionality]]
            inputFields['corner1'] = [x.value() for x in self.widgets[1*dimensionality:2*dimensionality]]
            inputFields['corner2'] = [x.value() for x in self.widgets[2*dimensionality:3*dimensionality]]
            inputFields['corner3'] = [x.value() for x in self.widgets[3*dimensionality:4*dimensionality]]
            if self.corner4CheckBox.isChecked():
                inputFields['corner4'] = [x.value() for x in self.widgets[4*dimensionality:5*dimensionality]]
            inputFields['maskInside'] = self.widgets[-1].isChecked()
            return inputFields

        self.acceptFunction = lambda: acceptFunction(self)


    def loadCircleMask(self,mask):
        labels = []
        self.widgets = []
        dimensionality = 2
        
        labels.append(QtWidgets.QLabel('Coordinates'))
        for i in range(dimensionality):
            axisComboBox=QtWidgets.QComboBox()
            axisComboBox.addItems(self.coordinates)
            axisComboBox.setCurrentIndex(i)
            self.widgets.append(axisComboBox)

        labels.append(QtWidgets.QLabel('Center'))
        for _ in range(dimensionality):
            DSBox = QtWidgets.QDoubleSpinBox()
            DSBox.setMaximum(1e6)
            DSBox.setMinimum(-1e6)
            self.widgets.append(DSBox)

        labels.append(QtWidgets.QLabel('Radius Point'))
        for _ in range(dimensionality):
            DSBox = QtWidgets.QDoubleSpinBox()
            DSBox.setMaximum(1e6)
            DSBox.setMinimum(-1e6)
            self.widgets.append(DSBox)

        labels.append(QtWidgets.QLabel('Mask Inside'))
        self.widgets.append(QtWidgets.QCheckBox())
        

        params = ['coordinates','center','radiusPoint','maskInside']
        sizes = [dimensionality,dimensionality,dimensionality,1]
        if not mask is None:
            values = [getattr(mask,p).flatten() if hasattr(getattr(mask,p),'flatten') else getattr(mask,p) for p in params]
        else:
            values = [[None]*s for s in sizes]

        for i,(label,value) in enumerate(zip(labels,values)):
            self.cornerLayout.addWidget(label,i,0)

            if isinstance(value,(bool)):
                value = [value]
            elif isinstance(value,(np.ndarray)):
                if np.any(np.isnan(value)):
                    value = [None]*dimensionality
            if i == 3:
                if not hasattr(value,'__len__'): # then it is not [None]
                    value = [value]
            for j,val in enumerate(value):
                if i < 3:
                    index =i*dimensionality+j
                else:
                    index = 2*dimensionality+i-1

                w = self.widgets[index]
                self.cornerLayout.addWidget(w,i,j+1)
                if not val is None:
                    if isinstance(w,(QtWidgets.QSpinBox,QtWidgets.QDoubleSpinBox)):
                        w.setValue(val)
                    elif isinstance(w,(QtWidgets.QComboBox)):
                        w.setCurrentIndex(w.findText(str(val)))
                    elif isinstance(w,(QtWidgets.QCheckBox)):
                        w.setChecked(val)

        def acceptFunction(self):
            inputFields = {}
            inputFields['coordinates'] = [x.currentText() for x in self.widgets[:dimensionality]]
            inputFields['center'] = [x.value() for x in self.widgets[1*dimensionality:2*dimensionality]]
            inputFields['radiusPoint'] = [x.value() for x in self.widgets[2*dimensionality:3*dimensionality]]
            #inputFields['radius'] = self.widgets[3*dimensionality].value()
            inputFields['maskInside'] = self.widgets[-1].isChecked()
            return inputFields

        self.acceptFunction = lambda: acceptFunction(self)

    def loadCurratAxeMask(self,mask):
        if not mask is None:
            braggList = mask.braggPeaks
        else:
            braggList = None
        

        self.BraggListManager = BraggListManager.BraggListManager(parent=self,BraggList=braggList)
        self.cornerLayout.addWidget(self.BraggListManager,0,0)
        ###
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        
        
        self.verticalLayout2 = QtWidgets.QVBoxLayout()
        
        self.verticalLayout2.addWidget(QtWidgets.QLabel('Mask Size'))

        self.buttonGroup = QtWidgets.QButtonGroup(self.verticalLayoutWidget)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.QxQy_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup.addButton(self.QxQy_radioButton)
        
        self.verticalLayout2.addWidget(self.QxQy_radioButton)

        self.RLU_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.buttonGroup.addButton(self.RLU_radioButton)
        self.RLU_radioButton.setChecked(True)

        self.verticalLayout2.addWidget(self.RLU_radioButton)

        self.verticalLayout.addLayout(self.verticalLayout2)

        self.QxQy_radioButton.setText("Qx Qy")
        self.RLU_radioButton.setText("RLU")

        self.gridLayout = QtWidgets.QGridLayout()
        self.BraggList_dH_spinBox = QtWidgets.QDoubleSpinBox(self.verticalLayoutWidget)
        self.BraggList_dH_spinBox.setObjectName(u"BraggList_H_spinBox")
        self.BraggList_dH_spinBox.setDecimals(3)
        self.BraggList_dH_spinBox.setMinimum(0.001)
        self.BraggList_dH_spinBox.setMaximum(99.998999999999995)
        self.BraggList_dH_spinBox.setSingleStep(0.010000000000000)
        self.BraggList_dH_spinBox.setValue(0.100000000000000)

        self.gridLayout.addWidget(self.BraggList_dH_spinBox, 1, 0, 1, 1)

        self.BraggList_dK_spinBox = QtWidgets.QDoubleSpinBox(self.verticalLayoutWidget)
        self.BraggList_dK_spinBox.setObjectName(u"BraggList_K_spinBox")
        self.BraggList_dK_spinBox.setDecimals(3)
        self.BraggList_dK_spinBox.setMinimum(0.001)
        self.BraggList_dK_spinBox.setMaximum(99.998999999999995)
        self.BraggList_dK_spinBox.setSingleStep(0.010000000000000)
        self.BraggList_dK_spinBox.setValue(0.100000000000000)

        self.gridLayout.addWidget(self.BraggList_dK_spinBox, 1, 1, 1, 1)

        self.BraggList_dL_spinBox = QtWidgets.QDoubleSpinBox(self.verticalLayoutWidget)
        self.BraggList_dL_spinBox.setObjectName(u"BraggList_L_spinBox")
        self.BraggList_dL_spinBox.setDecimals(3)
        self.BraggList_dL_spinBox.setMinimum(0.001)
        self.BraggList_dL_spinBox.setMaximum(99.998999999999995)
        self.BraggList_dL_spinBox.setSingleStep(0.010000000000000)
        self.BraggList_dL_spinBox.setValue(0.100000000000000)

        self.gridLayout.addWidget(self.BraggList_dL_spinBox, 1, 2, 1, 1)

        self.BraggListQH_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.BraggListQH_label.setText('dH')
        self.BraggListQH_label.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.BraggListQH_label, 0, 0, 1, 1)

        self.BraggListQK_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.BraggListQK_label.setText('dK')
        self.BraggListQK_label.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.BraggListQK_label, 0, 1, 1, 1)

        self.BraggListQL_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.BraggListQL_label.setText('dL')
        self.BraggListQL_label.setAlignment(QtCore.Qt.AlignCenter)

        self.gridLayout.addWidget(self.BraggListQL_label, 0, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QtWidgets.QVBoxLayout()
        
        self.horizontalLayout.addWidget(QtWidgets.QLabel('Mask Inside'))

        self.MaskInside_checkBox = QtWidgets.QCheckBox()
        if not mask is None:
            self.MaskInside_checkBox.setChecked(mask.maskInside)
        self.horizontalLayout.addWidget(self.MaskInside_checkBox)

        self.cornerLayout.addWidget(self.verticalLayoutWidget,1,0)

        def toggle(self,value): # To be added to QxQy
            if value:
                self.BraggList_dL_spinBox.setDisabled(True)
                self.BraggListQH_label.setText('dqx')
                self.BraggListQK_label.setText('dqx')
                self.BraggListQL_label.setText('')
            else:
                self.BraggList_dL_spinBox.setDisabled(False)
                self.BraggListQH_label.setText('dH')
                self.BraggListQK_label.setText('dK')
                self.BraggListQL_label.setText('dL')
        
        self.QxQy_radioButton.toggled.connect(lambda value: toggle(self,value))
        if not mask is None:
            dqx,dqy, dH, dK, dL = mask.dqx,mask.dqy, mask.dH, mask.dK, mask.dL
            if np.any([x is None for x in [dqx,dqy]]): # Then use dH, dK, dL
                self.BraggList_dH_spinBox.setValue(dH)
                self.BraggList_dK_spinBox.setValue(dK)
                self.BraggList_dL_spinBox.setValue(dL)
            else:
                self.QxQy_radioButton.setChecked(True)
                self.BraggList_dH_spinBox.setValue(dqx)
                self.BraggList_dK_spinBox.setValue(dqy)



        def acceptFunction(self):
            inputFields = {}
            inputFields['braggPeaks'] = self.BraggListManager.BraggListModel.data
            if self.QxQy_radioButton.isChecked():
                inputFields['dqx'] = self.BraggList_dH_spinBox.value()
                inputFields['dqx'] = self.BraggList_dK_spinBox.value()
            else:
                inputFields['dH'] = self.BraggList_dH_spinBox.value()
                inputFields['dK'] = self.BraggList_dK_spinBox.value()
                inputFields['dL'] = self.BraggList_dL_spinBox.value()
            inputFields['maskInside'] = self.MaskInside_checkBox.isChecked()
            return inputFields

        self.acceptFunction = lambda: acceptFunction(self)

        
    def coordinateSelectionChanged(self,id,text):
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
        # coordinates = [box.currentText() for box in self.coordinateComboBoxes]
        MaskType = getattr(Mask,self.maskTypeComboBox.currentText())
        
        maskName = self.maskNameEdit.text()
        if len(maskName) == 0:
            maskName = None
        inputFields = self.acceptFunction()

        self.mask = MaskType(**inputFields,name=maskName)
        if not self.oldMask is None:
            idx = self.MaskModel.getNames().index(self.oldMask.name)
            index = self.MaskModel.index(idx)
            self.MaskModel.delete([index])
        self.MaskModel.append(self.mask)
        self.close()
        #return super(maskingDialog,self).accept()

    def reject(self):
        self.close()

    def initiateComboBox(self,mask=None):
        self.maskTypeComboBox.clear()  # Needed to clear empty input
        names = list(maskTypes.keys())#['indexMask','lineMask','rectangleMask','circleMask','boxMask','CurratAxeMask']#self.simpleMaskParameters.keys()
        for name in names:
            self.maskTypeComboBox.addItem(name)
        if not mask is None:
            self.maskTypeComboBox.setCurrentIndex(names.index(translate[type(mask).__name__]))
        else:
            self.maskTypeComboBox.setCurrentIndex(-1)

        self.maskTypeComboBox.currentTextChanged.connect(self.maskSelectionChanged)

class AnotherWindow(QtWidgets.QWidget):
    """
    Create class to handle second window
    """
    def __init__(self,widget,AppContext,parent,maskingManager):
        super().__init__()
        self.maskingManager = maskingManager
        self.AppContext = AppContext
        layout = QtWidgets.QVBoxLayout()
        
        self.setLayout(layout)
        layout.addWidget(widget)
        self.parent = parent

        self.dialog = None

    # Method to generate masking dialogue
    def maskingDialog(self,oldMask=None):
        self.dialog = maskingDialog(maskingManager=self.maskingManager,oldMask=oldMask)

        if self.dialog.show(): # Execute the dialog
            return None
        
    def closeEvent(self, event):
        if not self.parent.isClosing:
            self.setVisible(False)
            if not self.dialog is None:
                self.dialog.close()
            return
        else:
            if not self.dialog is None:
                self.dialog.close()
            
        
        


MaskManagerBase, MaskManagerForm = loadUI("Mask2.ui")

class MaskManager(MaskManagerBase, MaskManagerForm):
    def __init__(self, parent=None):
        super(MaskManager, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        
        self.maskingMainWindow = AnotherWindow(widget=self,AppContext=self.parent.AppContext,parent=self.parent,maskingManager=self)
        self.maskingMainWindow.setVisible(False)
        self.MaskIsCorrect = False
        self.initMaskManager()
        self.setup()
        self.setupContextMenu()

    def setupContextMenu(self):
        def contextMenu(view,event,self):
            # Generate a context menu that opens on right click
            position = event.globalPos()
            idx = view.selectedIndexes()
            
            if len(idx)!=0:
                mask = view.model().item(idx[0])
                if event.type() == QtCore.QEvent.ContextMenu:
                    menu = QtWidgets.QMenu()
                    edit = QtWidgets.QAction('Edit')
                    edit.setToolTip('Edit Mask') 
                    edit.setStatusTip(edit.toolTip())
                    edit.triggered.connect(lambda: Mask_add_button_function(self.maskingMainWindow,oldMask=mask))
                    edit.setIcon(QtGui.QIcon(self.parent.AppContext.get_resource('Icons/Own/mask-edit.png')))
                    menu.addAction(edit)

                    duplicate = QtWidgets.QAction('Duplicate')
                    duplicate.setToolTip('Duplicate Mask') 
                    duplicate.setStatusTip(duplicate.toolTip())
                    duplicate.triggered.connect(lambda: Mask_duplicate_button_nonBlock_function(self.maskingMainWindow))
                    duplicate.setIcon(QtGui.QIcon(self.parent.AppContext.get_resource('Icons/Own/mask-duplicate.png')))
                    menu.addAction(duplicate)

                    delete = QtWidgets.QAction('Delete')
                    delete.setToolTip('Delete Mask') 
                    delete.setStatusTip(delete.toolTip())
                    delete.triggered.connect(lambda: Mask_delete_button_function(self.maskingMainWindow))
                    delete.setIcon(QtGui.QIcon(self.parent.AppContext.get_resource('Icons/Own/cross-button.png')))
                    menu.addAction(delete)


                    return menu.exec_(position)

        self.maskingMainWindow.MaskModel.Mask_listView.contextMenuEvent = lambda event: contextMenu(self.maskingMainWindow.MaskModel.Mask_listView,event,self)


    def setWindowVisible(self):
        self.maskingMainWindow.setVisible(True)

    def initMaskManager(self):
        self.maskingMainWindow.Mask_add_button_function = lambda: Mask_add_button_function(self.maskingMainWindow)
        self.maskingMainWindow.Mask_duplicate_button_nonBlock_function = lambda: Mask_duplicate_button_nonBlock_function(self.maskingMainWindow)
        self.maskingMainWindow.Mask_parse_equation_text_edit_function = lambda: Mask_parse_equation_text_edit_function(self.maskingMainWindow)
        self.maskingMainWindow.setupMask = lambda: setupMask(self.maskingMainWindow)

        self.maskingMainWindow.Mask_DoubleClick_Selection_function = lambda index:Mask_DoubleClick_Selection_function(self.maskingMainWindow,index)
        self.maskingMainWindow.Mask_delete_button_function = lambda:Mask_delete_button_function(self.maskingMainWindow)
        self.maskingMainWindow.selectedMaskChanged = lambda : selectedMaskChanged(self.maskingMainWindow)
        self.maskingMainWindow.updateMaskLabels = lambda:updateMaskLabels(self.maskingMainWindow)
        self.maskingMainWindow.MaskOnChange = lambda:MaskOnChange(self.maskingMainWindow)
        for key,value in self.__dict__.items():
                if 'Mask' in key:
                    self.maskingMainWindow.__dict__[key] = value

        grey = '<img src="{}" width=16 height=16>'.format(self.parent.AppContext.get_resource('Icons/Own/grey-led-on.png'))
        red = '<img src="{}" width=16 height=16>'.format(self.parent.AppContext.get_resource('Icons/Own/red-led-on.png'))
        green = '<img src="{}" width=16 height=16>'.format(self.parent.AppContext.get_resource('Icons/Own/green-led-on.png'))
        img = QtGui.QPixmap(self.parent.AppContext.get_resource('Icons/Own/grey-led-on.png'))
        img = img.scaled(QtCore.QSize(16, 16))
        self.maskingMainWindow.Mask_status_label.setPixmap(img)
        self.maskingMainWindow.Mask_status_label.setToolTip('<br>'.join([grey+' No mask applied',red+' Wrong masking',green+' Valid masking']))
        
        self.Mask_data_set_combo_box.setModel(self.parent.DataSetModel)
        self.Mask_apply_to_dataset_button.clicked.connect(self.ApplyMaskToDataSet)

        self.parent.DataSetModel.layoutChanged.connect(self.DataSetModelLayoutChanged)

        self.performButtonChecks()
        # def quick(self,state):
        #     print('quick got',state)
        #     if not state is None:
        #         self.parent.mask_changed.emit()
        #self.maskingMainWindow.Mask_apply_checkbox_nonBlock.stateChanged.connect(quick)

        
    def setup(self):
        self.maskingMainWindow.setupMask()
        self.maskingMainWindow.updateMaskLabels()
        self.maskingMainWindow.Mask_delete_button_nonBlock.clicked.connect(self.maskingMainWindow.Mask_delete_button_function)
        self.maskingMainWindow.Mask_delete_button_nonBlock.setShortcut("Del")

        self.maskingMainWindow.Mask_add_button_nonBlock.clicked.connect(self.maskingMainWindow.Mask_add_button_function)
        self.maskingMainWindow.Mask_add_button_nonBlock.setShortcut("Ctrl+N")

        self.maskingMainWindow.Mask_duplicate_button_nonBlock.clicked.connect(self.maskingMainWindow.Mask_duplicate_button_nonBlock_function)
        self.maskingMainWindow.Mask_equation_line_edit.textChanged.connect(self.maskingMainWindow.Mask_parse_equation_text_edit_function)
        self.maskingMainWindow.MaskModel.layoutChanged.connect(self.maskingMainWindow.MaskOnChange)
        self.maskingMainWindow.Mask_save_file_button.clicked.connect(self.save_mask_file)
        self.maskingMainWindow.Mask_save_file_button.setShortcut("Ctrl+S")

        self.maskingMainWindow.Mask_load_file_button.clicked.connect(self.load_mask_file)
        self.maskingMainWindow.Mask_load_file_button.setShortcut("Ctrl+O")

    def getMasks(self):
        if hasattr(self.maskingMainWindow,'MaskModel'):
            return self.maskingMainWindow.MaskModel.combinedMask
        else:
            return None
        
        
    def closeEvent(self, event):
        self.maskingMainWindow.close()


    def DataSetModelLayoutChanged(self):
        if self.parent.DataSetModel.rowCount(None)==0:
            self.Mask_data_set_combo_box.setCurrentIndex(-1)
        else:
            self.Mask_data_set_combo_box.setCurrentIndex(0)

        self.performButtonChecks()
        
    def ApplyMaskToDataSet(self):
        self.parent.resetProgressBar()
        self.parent.setProgressBarMaximum(1)
        self.parent.setProgressBarLabelText('Applying Masking')
        localIdx = self.Mask_data_set_combo_box.currentIndex()
        idx = self.parent.DataSetModel.index(localIdx,0) # Create correct index type for DataSetModel
        ds = self.parent.DataSetModel.data(idx,QtCore.Qt.ItemDataRole) # Get the DataSet in question
        self.parent.setProgressBarLabelText('Applying Masking to "{}"'.format(ds.name))

        
        mask = self.getMasks()
        matrix = mask(ds)
        self.parent.addProgressBarValue(0.75)
        
        ds.mask = matrix
        self.parent.setProgressBarValue(1)
        self.parent.setProgressBarLabelText('Done!')
        self.parent.resetProgressBarTimed()

        ds._maskingObject = mask
        
        self.closeEvent(event=None)

    def performButtonChecks(self):
        self.Mask_apply_to_dataset_button_check()
        self.Mask_save_file_button_check()


    def Mask_apply_to_dataset_button_check(self):
        if self.parent.DataSetModel.rowCount(None)!=0 and self.getMasks() is not None:
            self.Mask_apply_to_dataset_button.setDisabled(False)
        else:
            self.Mask_apply_to_dataset_button.setDisabled(True)

    def Mask_save_file_button_check(self):
        if self.getMasks() is not None:
            self.Mask_save_file_button.setDisabled(False)
        else:
            self.Mask_save_file_button.setDisabled(True)

    def save_mask_file(self):
        mask = self.getMasks()
        saveFile,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')

        if saveFile is None or saveFile == '':
            return False

        if not saveFile.split('.')[-1] == 'mask':
            saveFile+='.mask'

        if os.path.exists(saveFile): # if file already exists user has been asked to delete it
            os.remove(saveFile)
        
        mask.save(saveFile)

    def load_mask_file(self):

        loadFile,_ = QtWidgets.QFileDialog.getOpenFileName(self,"Load Mask", None ,"Mask (*.mask);;All Files (*)")

        if loadFile is None or loadFile == '':
            return False

        mask = Mask.load(loadFile)

        eq,masks = Mask.extract(mask)

        currentNames = self.maskingMainWindow.MaskModel.getNames()
        newNames = [m.name for m in masks]

        overlap = list(set.intersection(set(currentNames),set(newNames)))
        if len(overlap)>0:
            dialog = OverlapDialog(names=overlap)
            result = dialog.exec_()
            if result:
                ### Delete all masks with names in 
                names = list([m.name for m in self.maskingMainWindow.MaskModel.masks])

                idx =  [names.index(name) for name in overlap] # make sure ascending
                index = self.maskingMainWindow.MaskModel.index(-1,0)
                self.maskingMainWindow.MaskModel.Mask_listView.setCurrentIndex(index)
                self.maskingMainWindow.MaskModel.delete([self.maskingMainWindow.MaskModel.index(i,0) for i in idx])
            else:
                return False

        for m in masks:
            self.maskingMainWindow.MaskModel.append(m)

        self.maskingMainWindow.Mask_equation_line_edit.setText(eq)
        return True

        


class OverlapDialog(QtWidgets.QDialog):
    def __init__(self,names,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.names = names
        self.setWindowTitle("Name{:} already in use!".format('s'*(len(names)>1)))

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Loaded mask contains name{0} already in use. \n Overwrite with the loaded mask{0}?".format('s'*(len(names)>1)))
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)