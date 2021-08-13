import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments,loadUI
    from MJOLNIRGui.src.main.python.Views import BraggListManager
    import MJOLNIRGui.src.main.python._tools as _GUItools
except ImportError:
    from _tools import ProgressBarDecoratorArguments,loadUI
    from Views import BraggListManager
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets,uic
import numpy as np
from MJOLNIR.Data import Viewer3D

# Handles all functionality related to the View3D box. Each button has its own 
# definition, which should be pretty selfexplanatory.

def View3D_setCAxis_button_function(self):
    if not hasattr(self, 'V'):
        self.View3D_plot_button_function()
        
    CAxisMin=float(self.ui.View3D_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.View3D_CAxisMax_lineEdit.text())
            
    self.V.set_clim(CAxisMin,CAxisMax)

def View3D_SelectView_QxE_radioButton_function(self):
    if hasattr(self, 'V'):
        self.V.setAxis(1)
        # Redraw the title, then change the viewing plane to render properly
        self.View3D_SetTitle_button_function()
        self.V.setPlane(1)
        self.V.setPlane(0)
            
def View3D_SelectView_QyE_radioButton_function(self):
    if hasattr(self, 'V'):
        self.V.setAxis(0)
        # Redraw the title, then change the viewing plane to render properly
        self.View3D_SetTitle_button_function()
        self.V.setPlane(1)
        self.V.setPlane(0)
    
def View3D_SelectView_QxQy_radioButton_function(self):
    if hasattr(self, 'V'):
        self.V.setAxis(2)
        # Redraw the title, then change the viewing plane to render properly
        self.View3D_SetTitle_button_function()
        self.V.setPlane(1)
        self.V.setPlane(0)
    
def View3D_SetTitle_button_function(self):        
    if hasattr(self, 'V'):
        TitleText=self.ui.View3D_SetTitle_lineEdit.text()
        if TitleText == '':
            TitleText = self.ui.View3D_SetTitle_lineEdit.placeholderText()
        if isinstance(self.V,Viewer3D.Viewer3D):
            self.V.ax.set_title(TitleText)
            
            # Get the value of the slider right now, then change it around a bit and put it back to where it was, to render properly
            currentSliderValue=self.V.Energy_slider.val
            self.V.Energy_slider.set_val(0)
            self.V.Energy_slider.set_val(1)
            self.V.Energy_slider.set_val(currentSliderValue)
        else:
            self.V.parent().window().setWindowTitle(TitleText)
                
@ProgressBarDecoratorArguments(runningText='Generating View3D',completedText='View3D Generated')                    
def View3D_plot_button_function(self):
    if not self.stateMachine.requireStateByName('Converted'):
        return False

    # Check if we already have data, otherwise convert current data.
    ds = self.DataSetModel.getCurrentDataSet()
    if len(ds.convertedFiles)==0:
        self.DataSet_convertData_button_function()

    # Extract all the information from the GUI
    QXBin=float(self.ui.View3D_QXBin_lineEdit.text())
    QYBin=float(self.ui.View3D_QYBin_lineEdit.text())
    EBin =float(self.ui.View3D_EBin_lineEdit.text())
    
    if self.ui.View3D_SelectUnits_RLU_radioButton.isChecked():
        rlu=True
        
    if self.ui.View3D_SelectUnits_AA_radioButton.isChecked():
        rlu=False

    if self.ui.View3D_Grid_checkBox.isChecked():
        grid=9
    else:
        grid=False
    
    log = self.ui.View3D_LogScale_checkBox.isChecked()
    customSlicer = not self.ui.View3D_Mode_Viewer3D_radioButton.isChecked()
    counts = self.ui.View3D_RawCounts_checkBox.isChecked()
    plotCurratAxe = self.ui.View3D_CurratAxe_checkBox.isChecked()
    if plotCurratAxe:
        braggList = self.getBraggPoints()
    else:
        braggList = None
    
    self.V = ds.View3D(QXBin,QYBin,EBin,grid=grid,rlu=rlu,log=log,customSlicer=customSlicer,counts=counts,outputFunction=self.writeToStatus,cmap=self.colormap,CurratAxeBraggList=braggList)

    if customSlicer:
        self.windows.append(self.V.parent())
        
    else:
        self.windows.append(self.V.ax.get_figure())
    
        # Select the correct view
        if self.ui.View3D_SelectView_QxE_radioButton.isChecked():
            self.View3D_SelectView_QyE_radioButton_function()
        if self.ui.View3D_SelectView_QyE_radioButton.isChecked():
            self.View3D_SelectView_QxE_radioButton_function()
        if self.ui.View3D_SelectView_QxQy_radioButton.isChecked():
            self.View3D_SelectView_QxQy_radioButton_function()

        self.View3D_SetTitle_button_function()
        self.V.setPlane(1)
        self.V.setPlane(0)

    self.View3D_setCAxis_button_function()      
    
    
    return True
    #except:
    #    _GUItools.dialog(text='View3D plot could not be made. Check the input parameters and try again!')
    #    return False        
    
def View3D_toggle_mode_function(self):
    if self.ui.View3D_Mode_Viewer3D_radioButton.isChecked(): # changed to Viewer3D
        # Change titles
        self.ui.View3D_SelectView_QxQy_radioButton.setEnabled(True)
        self.ui.View3D_SelectView_QxE_radioButton.setEnabled(True)
        self.ui.View3D_SelectView_QyE_radioButton.setEnabled(True)
        self.ui.View3D_Grid_checkBox.setEnabled(True)

        self.ui.View3D_SelectUnits_RLU_radioButton.setEnabled(True)
        self.ui.View3D_SelectUnits_AA_radioButton.setEnabled(True)

    else: # Changing to AA
        self.ui.View3D_SelectView_QxQy_radioButton.setEnabled(False)
        self.ui.View3D_SelectView_QxE_radioButton.setEnabled(False)
        self.ui.View3D_SelectView_QyE_radioButton.setEnabled(False)
        self.ui.View3D_Grid_checkBox.setEnabled(False)

        self.ui.View3D_SelectUnits_RLU_radioButton.setEnabled(False)
        self.ui.View3D_SelectUnits_AA_radioButton.setEnabled(False)
        
def View3D_toggle_plotCurratAxe_function(self):
    if hasattr(self,'V'):
        self.V.plotCurratAxe = self.ui.View3D_CurratAxe_checkBox.isChecked()

def View3D_changed_CurratAxeList_function(self):
    if hasattr(self,'V'):
        self.V.CurratAxeBraggList = self.getBraggPoints()

def View3D_DataSet_selectionChanged_function(self):
    ds = self.DataSetModel.getCurrentDataSet()
    if not ds is None:
        title = ds.name
    else:
        title = ''
    self.ui.View3D_SetTitle_lineEdit.setPlaceholderText(title)
    
def View3D_Grid_checkBox_toggled_function(self):
    if hasattr(self,'V'):
        if self.ui.View3D_Grid_checkBox.isChecked():
            self.V.grid = True
            self.V.gridZOrder=9
        else:
            self.V.grid = False
            self.V.gridZOrder=9
        for ax in self.V._axes:
            ax.grid(self.V.grid,zorder=self.V.gridZOrder)
# if platform.system() == 'Darwin':
#     folder = path.abspath(path.join(path.dirname(__file__),'..','..','Resources','Views'))
# else: 
#     folder = path.join(path.dirname(__file__),'..','..','resources','base','Views')

# try:
#     View3DManagerBase, View3DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"View3D.ui"))
# except:
#     View3DManagerBase, View3DManagerForm = uic.loadUiType(path.join(folder,"View3D.ui"))



View3DManagerBase, View3DManagerForm = loadUI('View3D.ui')

# try:
#     View3DManagerBase, View3DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"View3D.ui"))
# except:
#     try:
#         View3DManagerBase, View3DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"View3D.ui"))
#     except:
#         View3DManagerBase, View3DManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"View3D.ui"))
# All of this connects the buttons and their functions to the main window.

class View3DManager(View3DManagerBase, View3DManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(View3DManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initView3DManager()
        
    def initView3DManager(self):    
        self.guiWindow.View3D_setCAxis_button_function = lambda:View3D_setCAxis_button_function(self.guiWindow)
        self.guiWindow.View3D_SelectView_QxE_radioButton_function = lambda:View3D_SelectView_QxE_radioButton_function(self.guiWindow)
        self.guiWindow.View3D_SelectView_QyE_radioButton_function = lambda:View3D_SelectView_QyE_radioButton_function(self.guiWindow)
        self.guiWindow.View3D_SelectView_QxQy_radioButton_function = lambda:View3D_SelectView_QxQy_radioButton_function(self.guiWindow)
        self.guiWindow.View3D_SetTitle_button_function = lambda:View3D_SetTitle_button_function(self.guiWindow)
        self.guiWindow.View3D_plot_button_function = lambda:View3D_plot_button_function(self.guiWindow)
        self.guiWindow.View3D_toggle_mode_function = lambda: View3D_toggle_mode_function(self.guiWindow)
        self.guiWindow.View3D_toggle_plotCurratAxe_function = lambda: View3D_toggle_plotCurratAxe_function(self.guiWindow)
        self.guiWindow.View3D_changed_CurratAxeList_function = lambda: View3D_changed_CurratAxeList_function(self.guiWindow)
        self.guiWindow.View3D_DataSet_selectionChanged_function = lambda: View3D_DataSet_selectionChanged_function(self.guiWindow)
        self.guiWindow.View3D_Grid_checkBox_toggled_function = lambda: View3D_Grid_checkBox_toggled_function(self.guiWindow)

        for key,value in self.__dict__.items():
            if 'View3D' in key:
                self.guiWindow.ui.__dict__[key] = value

    def setup(self):
        self.guiWindow.ui.View3D_plot_button.clicked.connect(self.guiWindow.View3D_plot_button_function)
        self.guiWindow.ui.View3D_setCAxis_button.clicked.connect(self.guiWindow.View3D_setCAxis_button_function)
        self.guiWindow.ui.View3D_SetTitle_button.clicked.connect(self.guiWindow.View3D_SetTitle_button_function)

        self.guiWindow.ui.View3D_SetTitle_lineEdit.returnPressed.connect(self.titleEnterPressed)
        self.guiWindow.ui.View3D_CAxisMax_lineEdit.returnPressed.connect(self.CAxisChanged)
        self.guiWindow.ui.View3D_CAxisMin_lineEdit.returnPressed.connect(self.CAxisChanged)
        
        # Radiobutton to select viewing type
        self.guiWindow.ui.View3D_SelectView_QxE_radioButton.clicked.connect(self.guiWindow.View3D_SelectView_QxE_radioButton_function)
        self.guiWindow.ui.View3D_SelectView_QyE_radioButton.clicked.connect(self.guiWindow.View3D_SelectView_QyE_radioButton_function)
        self.guiWindow.ui.View3D_SelectView_QxQy_radioButton.clicked.connect(self.guiWindow.View3D_SelectView_QxQy_radioButton_function)
        self.guiWindow.ui.View3D_Mode_Viewer3D_radioButton.toggled.connect(self.guiWindow.View3D_toggle_mode_function)
        self.guiWindow.ui.View3D_CurratAxe_checkBox.toggled.connect(self.guiWindow.View3D_toggle_plotCurratAxe_function)
        self.guiWindow.ui.View3D_Grid_checkBox.toggled.connect(self.guiWindow.View3D_Grid_checkBox_toggled_function)

        self.guiWindow.DataSetSelectionModel.selectionChanged.connect(self.guiWindow.View3D_DataSet_selectionChanged_function)
        self.guiWindow.DataSetModel.dataChanged.connect(self.guiWindow.View3D_DataSet_selectionChanged_function)
        
        

    def titleEnterPressed(self):
        if self.guiWindow.ui.View3D_SetTitle_button.isEnabled():
            self.guiWindow.View3D_SetTitle_button_function()

    def CAxisChanged(self):
        if self.guiWindow.ui.View3D_setCAxis_button.isEnabled():
            self.guiWindow.View3D_setCAxis_button_function()

    def curratAxeList(self):
        if hasattr(self,'BraggListWindow'): # If a window is open, use it
            self.braggPoints = self.BraggListWindow.BraggListModel.data
        else:
            self.BraggListWindow = BraggListManager.BraggListManager(BraggList=self.braggPoints)
            self.guiWindow.windows.append(self.BraggListWindow)
            self.BraggListWindow.show()