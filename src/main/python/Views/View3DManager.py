import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments,loadUI
    from MJOLNIRGui.src.main.python.Views import BraggListManager
    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.DataModels import MatplotlibFigureList,MatplotlibFigureListDelegate
except ImportError:
    from _tools import ProgressBarDecoratorArguments,loadUI
    from Views import BraggListManager
    import _tools as _GUItools
    from DataModels import MatplotlibFigureList,MatplotlibFigureListDelegate
from os import path
from PyQt5 import QtWidgets,uic
import numpy as np
from MJOLNIR.Data import Viewer3D

# Handles all functionality related to the View3D box. Each button has its own 
# definition, which should be pretty selfexplanatory.

def View3D_setCAxis_button_function(self):
    currentFigure = self.figureListView3D.getCurrentFigure()
    if currentFigure is None:
        self.View3D_plot_button_function()
        currentFigure = self.figureListView3D.getCurrentFigure()
        
    CAxisMin=float(self.ui.View3D_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.View3D_CAxisMax_lineEdit.text())
            
    currentFigure.set_clim(CAxisMin,CAxisMax)
    if hasattr(currentFigure,'settings'):
        currentFigure.settings['View3D_CAxisMax_lineEdit'] = str(CAxisMax)
        currentFigure.settings['View3D_CAxisMin_lineEdit'] = str(CAxisMin)
    

def View3D_SelectView_QxE_radioButton_function(self):
    currentFigure = self.figureListView3D.getCurrentFigure()
    if not currentFigure is None:
        currentFigure.setAxis(1)
        # Redraw the title, then change the viewing plane to render properly
        self.View3D_SetTitle_button_function()
        currentFigure.setPlane(1)
        currentFigure.setPlane(0)
            
def View3D_SelectView_QyE_radioButton_function(self):
    currentFigure = self.figureListView3D.getCurrentFigure()
    if not currentFigure is None:
        currentFigure.setAxis(0)
        # Redraw the title, then change the viewing plane to render properly
        self.View3D_SetTitle_button_function()
        currentFigure.setPlane(1)
        currentFigure.setPlane(0)
    
def View3D_SelectView_QxQy_radioButton_function(self):
    currentFigure = self.figureListView3D.getCurrentFigure()
    if not currentFigure is None:
        currentFigure.setAxis(2)
        # Redraw the title, then change the viewing plane to render properly
        self.View3D_SetTitle_button_function()
        currentFigure.setPlane(1)
        currentFigure.setPlane(0)
    
def View3D_SetTitle_button_function(self):        
    currentFigure = self.figureListView3D.getCurrentFigure()
    if not currentFigure is None:
        TitleText=self.ui.View3D_SetTitle_lineEdit.text()
        if TitleText == '':
            TitleText = self.ui.View3D_SetTitle_lineEdit.placeholderText()
        if isinstance(currentFigure,Viewer3D.Viewer3D):
            currentFigure.ax.set_title(TitleText)
            
            # Get the value of the slider right now, then change it around a bit and put it back to where it was, to render properly
            currentSliderValue=currentFigure.Energy_slider.val
            currentFigure.Energy_slider.set_val(0)
            currentFigure.Energy_slider.set_val(1)
            currentFigure.Energy_slider.set_val(currentSliderValue)
        else:
            currentFigure.parent().window().setWindowTitle(TitleText)

        currentFigure._title = TitleText
        
        idx = self.figureListView3D.getCurrentFigureIndex()
        dummyIdx = self.figureListView3D.index(idx)
        self.figureListView3D.beginInsertRows(dummyIdx,idx,idx+1)
        self.figureListView3D.endInsertRows()
        self.figureListView3D.view.currentTextChanged.emit(TitleText)
        if hasattr(currentFigure,'settings'):
            currentFigure.settings['View3D_SetTitle_lineEdit'] = TitleText
        
                
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
    
    figure = ds.View3D(QXBin,QYBin,EBin,grid=grid,rlu=rlu,log=log,customSlicer=customSlicer,counts=counts,outputFunction=self.writeToStatus,cmap=self.colormap,CurratAxeBraggList=braggList)
    self.figureListView3D.append(figure)
    currentFigure = self.figureListView3D.getCurrentFigure()

    TitleText=self.ui.View3D_SetTitle_lineEdit.text()
    if TitleText == '':
        TitleText = self.ui.View3D_SetTitle_lineEdit.placeholderText()

    CAxisMin=float(self.ui.View3D_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.View3D_CAxisMax_lineEdit.text())

    figure.settings = {'View3D_SelectUnits_RLU_radioButton':rlu,
                       'View3D_SelectUnits_AA_radioButton': not rlu,
                       'View3D_Grid_checkBox':grid!=False,
                       'View3D_LogScale_checkBox':log,
                       'View3D_Mode_Viewer3D_radioButton': not customSlicer,
                       'View3D_Mode_Custom_radioButton': customSlicer,
                       'View3D_RawCounts_checkBox':counts,
                       'View3D_CurratAxe_checkBox':plotCurratAxe,
                       'View3D_QXBin_lineEdit':QXBin,
                       'View3D_QYBin_lineEdit':QYBin,
                       'View3D_EBin_lineEdit':EBin,
                       'View3D_SetTitle_lineEdit':TitleText,
                       'View3D_CAxisMax_lineEdit':CAxisMax,
                       'View3D_CAxisMin_lineEdit':CAxisMin}

    if customSlicer:
        #self.windows.append(currentFigure.parent())
        def setClosed(self,fig):
            self.figureListView3D.close(fig)
            fig.closed=True

        closeFunction = lambda event: setClosed(self,currentFigure)
        currentFigure.parent().closeEvent = closeFunction
    else:
        #self.windows.append(currentFigure.ax.get_figure())
        def setClosed(fig):
            fig.closed=True

        closeFunction = lambda event: setClosed(currentFigure)
        
        currentFigure.ax.get_figure().canvas.mpl_connect('close_event', closeFunction)
    
        # Select the correct view
        if self.ui.View3D_SelectView_QxE_radioButton.isChecked():
            self.View3D_SelectView_QyE_radioButton_function()
        if self.ui.View3D_SelectView_QyE_radioButton.isChecked():
            self.View3D_SelectView_QxE_radioButton_function()
        if self.ui.View3D_SelectView_QxQy_radioButton.isChecked():
            self.View3D_SelectView_QxQy_radioButton_function()

        self.View3D_SetTitle_button_function()
        currentFigure.setPlane(1)
        currentFigure.setPlane(0)

    
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
    currentFigure = self.figureListView3D.getCurrentFigure()
    if not currentFigure is None:
        value = self.ui.View3D_CurratAxe_checkBox.isChecked()
        currentFigure.plotCurratAxe = value
        if hasattr(currentFigure,'settings'):
            currentFigure.settings['View3D_CurratAxe_checkBox'] = value

def View3D_changed_CurratAxeList_function(self):
    currentFigure = self.figureListView3D.getCurrentFigure()
    if not currentFigure is None:
        currentFigure.CurratAxeBraggList = self.getBraggPoints()

        

def View3D_DataSet_selectionChanged_function(self):
    ds = self.DataSetModel.getCurrentDataSet()
    if not ds is None:
        title = ds.name
    else:
        title = ''
    self.ui.View3D_SetTitle_lineEdit.setPlaceholderText(title)
    
def View3D_Grid_checkBox_toggled_function(self):
    currentFigure = self.figureListView3D.getCurrentFigure()
    if not currentFigure is None:
        if self.ui.View3D_Grid_checkBox.isChecked():
            currentFigure.grid = True
            currentFigure.gridZOrder=9
        else:
            currentFigure.grid = False
            currentFigure.gridZOrder=9
        currentFigure.settings['View3D_Grid_checkBox'] = currentFigure.grid!=False
        for ax in currentFigure._axes:
            ax.grid(currentFigure.grid,zorder=currentFigure.gridZOrder)

def indexChanged(self,index):
    figure = self.figureListView3D.figures[index]
    if hasattr(figure,'settings'):
        for setting,value in figure.settings.items():
            if 'radio' in setting or 'checkBox' in setting:
                getattr(getattr(self.ui,setting),'setChecked')(value)
            else:
                getattr(getattr(self.ui,setting),'setText')(str(value))

View3DManagerBase, View3DManagerForm = loadUI('View3D.ui')

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
        self.guiWindow.View3D_indexChanged = lambda index: indexChanged(self.guiWindow,index)

        for key,value in self.__dict__.items():
            if 'View3D' in key:
                self.guiWindow.ui.__dict__[key] = value

        ## Set up figure manager. Is to be initialized between manager initialization but before their setup
        self.guiWindow.figureListView3D = MatplotlibFigureList(combobox=self.View3D_figureList_comboBox)
        self.guiWindow.figureList.append(self.guiWindow.figureListView3D)
        self.View3D_figureList_comboBox.setModel(self.guiWindow.figureListView3D)

        self.mplListDelegate = MatplotlibFigureListDelegate()
        

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
        self.guiWindow.figureListView3D.view.currentIndexChanged.connect(self.guiWindow.View3D_indexChanged)
        self.guiWindow.ui.View3D_figureList_comboBox.setItemDelegate(self.mplListDelegate)

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