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


def Mask_DoubleClick_Selection_function(self,index,*args,**kwargs):
    self.ui.Mask_listView.edit(index)

def setupMask(self):
    
    self.MaskModel = MaskModel(Mask_listView=self.ui.Mask_listView)
    self.ui.Mask_listView.setModel(self.MaskModel)
    self.MaskModel.dataChanged.connect(self.MaskModel.layoutChanged.emit)

    self.MaskSelectionModel = self.ui.Mask_listView.selectionModel()
    self.MaskSelectionModel.selectionChanged.connect(self.selectedMaskChanged)
    
    self.ui.Mask_listView.doubleClicked.connect(self.Mask_DoubleClick_Selection_function)


def selectedMaskChanged(self,*args,**kwargs):
    self.updateMaskLabels()


def updateMaskLabels(self):
    masks = self.MaskModel.rowCount()
    if masks == 0:
        self.ui.Mask_delete_button_nonBlock.setEnabled(False)
    else:
        self.ui.Mask_delete_button_nonBlock.setEnabled(True)
    selected = self.ui.Mask_listView.selectedIndexes()
    if len(np.asarray(selected))==0 or masks==0:
        self.ui.Mask_duplicate_button_nonBlock.setEnabled(False)
        self.ui.Mask_type_label.setText('')
    else:
        self.ui.Mask_duplicate_button_nonBlock.setEnabled(True)
        if len(np.asarray(selected))>1:
            self.ui.Mask_type_label.setText('Multiple')
        else:
            mask = self.MaskModel.item(np.asarray(selected)[0])
            maskType = type(mask.mask).__name__
            self.ui.Mask_type_label.setText(maskType)


def parse(string,masks):
    for _ObscureName in masks:
        locals()[_ObscureName.name]=_ObscureName.mask
    return eval(string)


def MaskOnChange(self):
    self.Mask_parse_equation_text_edit_function()
    self.updateMaskLabels()


def Mask_parse_equation_text_edit_function(self):
    AppC = self.AppContext
    string = self.ui.Mask_equation_text_edit.toPlainText()
    string = string.replace('\n','')
    string = string.strip()
    if len(string)==0:
        if hasattr(self,'combinedMask'):
            del self.combinedMask
        img = QtGui.QPixmap(AppC.get_resource('Icons/Own/grey-led-on.png'))
    else:
        try:
            combinedMask = parse(string,masks=self.MaskModel.masks)
        except (NameError,AttributeError,SyntaxError,TypeError):
            img = QtGui.QPixmap(AppC.get_resource('Icons/Own/red-led-on.png'))
        else:
            img = QtGui.QPixmap(AppC.get_resource('Icons/Own/green-led-on.png'))
            self.combinedMask = combinedMask
    img = img.scaled(QtCore.QSize(16, 16))
    self.ui.Mask_status_label.setPixmap(img)
    #print(self.combinedMask,self)
    

#def extractCutParameters(self):
#    HStart = self.ui.Cut1D_HStart_lineEdit.text()
#    HEnd = self.ui.Cut1D_HEnd_lineEdit.text()
#    KStart = self.ui.Cut1D_KStart_lineEdit.text()
#    KEnd = self.ui.Cut1D_KEnd_lineEdit.text()
#    LStart = self.ui.Cut1D_LStart_lineEdit.text()
#    LEnd = self.ui.Cut1D_LEnd_lineEdit.text()

#    EMax = float(self.ui.Cut1D_EMax_lineEdit.text())
#    EMin = float(self.ui.Cut1D_EMin_lineEdit.text())

#    width = float(self.ui.Cut1D_Width_lineEdit.text())
#    minPixel = float(self.ui.Cut1D_MinPixel_lineEdit.text())

#    ds = self.DataSetModel.getCurrentDataSet()
#    rlu = self.ui.Cut1D_SelectUnits_RLU_radioButton.isChecked()
#    if rlu:
#        q1 = np.array([HStart,KStart,LStart],dtype=float)
#        q2 = np.array([HEnd,KEnd,LEnd],dtype=float)
#    else:
#        q1 = np.array([HStart,KStart],dtype=float)
#        q2 = np.array([HEnd,KEnd],dtype=float)

#    cutQ = self.ui.Cut1D_SelectCut_Q_radioButton.isChecked()

#    return ds,q1,q2,width,minPixel,EMax,EMin,cutQ,rlu



#@ProgressBarDecoratorArguments(runningText='Cutting Cut1D',completedText='Cutting Done')
#def Cut1D_Generate1D_button_function(self):
#    if not self.stateMachine.requireStateByName('Converted'):
#        return False
#
#    ds,q1,q2,width,minPixel,EMax,EMin,cutQ,rlu = extractCutParameters(self)
#    if checker(q1,q2,width,minPixel,EMax,EMin,cutQ) is False:
#        return False
#    try:
#        if cutQ:
#            ufitObject = ds.cut1D(q1=q1,q2=q2,width=width,minPixel=minPixel,Emin=EMin,Emax=EMax,rlu=rlu,constantBins=False,ufit=True)
#            parameters = ['q1','q2','width','minPixel','Emin','Emax','rlu','constantBins','method']
#            values = [q1,q2,width,minPixel,EMin,EMax,rlu,False,'cut1D']
#        else: # else along E
#            ufitObject = ds.cut1DE(E1=EMin,E2=EMax,q=q1,rlu=rlu,width=width, minPixel = minPixel,ufit=True)
#            parameters = ['E1','E2','q','rlu','width','minPixel','method']
#            values = [EMin,EMax,q1,rlu,width,minPixel,'cut1DE']
#        
#        # Generate a Gui1DCutObject
#        if not hasattr(self,'cutNumber'):
#            self.cutNumber = 1
#        gui1DCut = Gui1DCutObject(name='Cut {}'.format(self.cutNumber),uFitDataset=ufitObject)
#        for par,val in zip(parameters,values):
#            setattr(gui1DCut,par,val)
#        gui1DCut.parameters = parameters
#        self.cutNumber+=1
#        self.Cut1DModel.append(gui1DCut)
#    except AttributeError as e:
#        raise e
#        #_GUItools.dialog(text='1D Cut could not be made. Check the limits for the cut and try again!')
#        return False


#def Cut1D_toggle_units_function(self):
#    if self.ui.Cut1D_SelectUnits_RLU_radioButton.isChecked(): # changed to RLU
#        # Change titles
#        self.ui.Cut1D_Hlabel.setText('H')
#        self.ui.Cut1D_Klabel.setText('K')
#        self.ui.Cut1D_Llabel.setText('L')
#        self.ui.Cut1D_LStart_lineEdit.setEnabled(True)
#        self.ui.Cut1D_LEnd_lineEdit.setEnabled(True)
#    else: # Changing to AA
#        self.ui.Cut1D_Hlabel.setText('Qx')
#        self.ui.Cut1D_Klabel.setText('Qy')
#        self.ui.Cut1D_Llabel.setText('N/A')
#        self.ui.Cut1D_LStart_lineEdit.setEnabled(False)
#        self.ui.Cut1D_LEnd_lineEdit.setEnabled(False)

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



def Mask_add_button_function(self):
    mask = self.maskingDialog(objInfo)

    print(mask)
    if mask is None:
        return
    else:
        self.MaskModel.append(mask)


def Mask_delete_button_function(self):
    self.MaskModel.delete(self.ui.Mask_listView.selectedIndexes())
    self.updateMaskLabels()
    self.MaskModel.layoutChanged.emit()
    self.updateMaskLabels()
    

def Mask_duplicate_button_nonBlock_function(self):
    self.MaskModel.layoutChanged.emit()
    items = self.MaskModel.item(self.ui.Mask_listView.selectedIndexes())
    if items is None:
        return
    items = np.asarray(items)
    for item in items:
        newItem = copy.deepcopy(item)
        #name = newItem.name
        #number=2
        #updateNumber = False
        #if name.find('(')>-1: # name has the format xxx(iii)
        #    try:
        #        number = int(name[name.find('(')+1:-1])
        #        updateNumber = True
        #    except:
        #        pass
        #if updateNumber:
        #    preName = name.split('(')[0]
        #    
        #    newItem.name = preName+'({})'.format(number+1)
        #else:
        #    newItem.name+='({})'.format(number)
        self.MaskModel.append(newItem)
    
    self.updateMaskLabels()
    self.MaskModel.layoutChanged.emit()



#def focusOutEvent(self, event):
#    AppC = self.parent().guiWindow.AppContext
#    if self.parse() == True:
#        img = QtGui.QPixmap(AppC.get_resource('Icons/Own/green-led-on.png'))
#    elif hasattr(self.parent().guiWindow,'combinedMask'):
#        img = QtGui.QPixmap(AppC.get_resource('Icons/Own/red-led-on.png'))
#    else:
#        img = QtGui.QPixmap(AppC.get_resource('Icons/Own/grey-led-on.png'))
#    img = img.scaled(QtCore.QSize(16, 16))
#    self.parent().guiWindow.ui.Mask_status_label.setPixmap(img)
#    self._focusOutEvent(event)

try:
    MaskManagerBase, MaskManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"Mask.ui"))
except:
    try:
        MaskManagerBase, MaskManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"Mask.ui"))
    except:
        MaskManagerBase, MaskManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"Mask.ui"))
class MaskManager(MaskManagerBase, MaskManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(MaskManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initMaskManager()

    def initMaskManager(self):
        #self.guiWindow.Mask_plot_button_function = lambda: Mask_plot_button_function(self.guiWindow)
        self.guiWindow.Mask_add_button_function = lambda: Mask_add_button_function(self.guiWindow)
        self.guiWindow.Mask_duplicate_button_nonBlock_function = lambda: Mask_duplicate_button_nonBlock_function(self.guiWindow)
        self.guiWindow.Mask_parse_equation_text_edit_function = lambda: Mask_parse_equation_text_edit_function(self.guiWindow)
        #self.guiWindow.Cut1D_SetTitle_button_function = lambda: Cut1D_SetTitle_button_function(self.guiWindow)
        self.guiWindow.setupMask = lambda: setupMask(self.guiWindow)
        #self.guiWindow.Cut1D_toggle_units_function = lambda: Cut1D_toggle_units_function(self.guiWindow)
        #self.guiWindow.Cut1D_Save_To_uFit = lambda: Cut1D_Save_To_uFit(self.guiWindow)

        #self.guiWindow.plotItem = lambda item: plotItem(self.guiWindow,item)

        
        self.guiWindow.Mask_DoubleClick_Selection_function = lambda index:Mask_DoubleClick_Selection_function(self.guiWindow,index)
        self.guiWindow.Mask_delete_button_function = lambda:Mask_delete_button_function(self.guiWindow)
        self.guiWindow.selectedMaskChanged = lambda : selectedMaskChanged(self.guiWindow)
        self.guiWindow.updateMaskLabels = lambda:updateMaskLabels(self.guiWindow)
        self.guiWindow.MaskOnChange = lambda:MaskOnChange(self.guiWindow)
        for key,value in self.__dict__.items():
                if 'Mask' in key:
                    self.guiWindow.ui.__dict__[key] = value

        #self.guiWindow.ui.Mask_equation_text_edit._focusOutEvent = self.guiWindow.ui.Mask_equation_text_edit.focusOutEvent
        #self.guiWindow.ui.Mask_equation_text_edit.parse = self.guiWindow.Mask_parse_equation_text_edit_function
        #self.guiWindow.ui.Mask_equation_text_edit.focusOutEvent = lambda event: focusOutEvent(self.guiWindow.ui.Mask_equation_text_edit,event)

        grey = '<img src="{}" width=16 height=16>'.format(self.guiWindow.AppContext.get_resource('Icons/Own/grey-led-on.png'))
        red = '<img src="{}" width=16 height=16>'.format(self.guiWindow.AppContext.get_resource('Icons/Own/red-led-on.png'))
        green = '<img src="{}" width=16 height=16>'.format(self.guiWindow.AppContext.get_resource('Icons/Own/green-led-on.png'))
        img = QtGui.QPixmap(self.guiWindow.AppContext.get_resource('Icons/Own/grey-led-on.png'))
        img = img.scaled(QtCore.QSize(16, 16))
        self.guiWindow.ui.Mask_status_label.setPixmap(img)
        self.guiWindow.ui.Mask_status_label.setToolTip('<br>'.join([grey+' no mask applied.',red+' wrong masking.',green+' correct masking.']))

        
    def setup(self):
        self.guiWindow.setupMask()
        self.guiWindow.updateMaskLabels()
        #self.guiWindow.ui.Mask_SelectUnits_RLU_radioButton.toggled.connect(self.guiWindow.Mask_toggle_units_function)
        #self.guiWindow.ui.Mask_fit_button.clicked.connect(self.guiWindow.Mask_Save_To_uFit)
        self.guiWindow.ui.Mask_delete_button_nonBlock.clicked.connect(self.guiWindow.Mask_delete_button_function)
        self.guiWindow.ui.Mask_add_button_nonBlock.clicked.connect(self.guiWindow.Mask_add_button_function)
        self.guiWindow.ui.Mask_duplicate_button_nonBlock.clicked.connect(self.guiWindow.Mask_duplicate_button_nonBlock_function)
        self.guiWindow.ui.Mask_equation_text_edit.textChanged.connect(self.guiWindow.Mask_parse_equation_text_edit_function)
        self.guiWindow.MaskModel.layoutChanged.connect(self.guiWindow.MaskOnChange)
        
    