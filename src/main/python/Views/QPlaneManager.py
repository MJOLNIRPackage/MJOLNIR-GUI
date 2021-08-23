import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments, loadUI
    from MJOLNIRGui.src.main.DataModels import MatplotlibFigureList,MatplotlibFigureListDelegate
except ImportError:
    from _tools import ProgressBarDecoratorArguments, loadUI
    from DataModels import MatplotlibFigureList,MatplotlibFigureListDelegate

from os import path
from PyQt5 import QtWidgets, uic
import numpy as np

def QPlane_plot_button_function(self):
    # Make plot
    if not self.stateMachine.requireStateByName('Converted'):
        return False
    ds = self.DataSetModel.getCurrentDataSet()
    if len(ds.convertedFiles)==0:
        self.DataSet_convertData_button_function()        
    
    # Check various plot settings
    if self.ui.QPlane_SelectUnits_RLU_radioButton.isChecked():
        rlu=True
    else:
        rlu=False        

    if self.ui.QPlane_LogScale_checkBox.isChecked():
        log=True
    else:
        log=False          

    EMin=float(self.ui.QPlane_EMin_lineEdit.text())
    EMax=float(self.ui.QPlane_EMax_lineEdit.text())
    xBinTolerance = float(self.ui.QPlane_xBinTolerance_lineEdit.text())           
    yBinTolerance = float(self.ui.QPlane_yBinTolerance_lineEdit.text())           

    Data,Bins,ax = ds.plotQPlane(EMin=EMin, EMax=EMax,xBinTolerance=xBinTolerance,yBinTolerance=yBinTolerance,log=log,rlu=rlu,cmap=self.colormap)
    currentFigure = ax.get_figure()
    self.QPlane=ax   
    
    self.figureListQPlane.append(currentFigure) 
    
    
    currentFigure.colorbar(ax.pmeshs[0])
    currentFigure.set_size_inches(8,6)
    grid = self.ui.QPlane_Grid_checkBox.isChecked()
    ax.grid(grid)
    TitleText=self.ui.QPlane_SetTitle_lineEdit.text()
    if TitleText == '':
        TitleText = self.ui.QPlane_SetTitle_lineEdit.placeholderText()
    CAxisMin=float(self.ui.QPlane_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.QPlane_CAxisMax_lineEdit.text())

    currentFigure.settings = {'QPlane_SelectUnits_RLU_radioButton':rlu,
                    'QPlane_SelectUnits_AA_radioButton': not rlu,
                    'QPlane_Grid_checkBox':grid!=False,
                    'QPlane_LogScale_checkBox':log,
                    #'View3D_CurratAxe_checkBox':plotCurratAxe,
                    'QPlane_xBinTolerance_lineEdit':xBinTolerance,
                    'QPlane_yBinTolerance_lineEdit':yBinTolerance,
                    'QPlane_EMax_lineEdit':EMax,
                    'QPlane_EMin_lineEdit':EMin,
                    'QPlane_SetTitle_lineEdit':TitleText,
                    'QPlane_CAxisMax_lineEdit':CAxisMax,
                    'QPlane_CAxisMin_lineEdit':CAxisMin,
                    'QPlane_SetTitle_lineEdit':TitleText}

    def setClosed(fig):
        fig.closed=True

    closeFunction = lambda event: setClosed(currentFigure)
    currentFigure.canvas.mpl_connect('close_event', closeFunction)
                    
    self.QPlane_setCAxis_button_function()
    self.QPlane_SetTitle_button_function()
    self.windows.append(self.QPlane.get_figure())

    return True
    

def QPlane_setCAxis_button_function(self):
    CAxisMin=float(self.ui.QPlane_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.QPlane_CAxisMax_lineEdit.text())
    currentFigure = self.figureListQPlane.getCurrentFigure()
    if not currentFigure is None:
        currentFigure.gca().set_clim(CAxisMin,CAxisMax)
    
        currentFigure.settings['QPlane_CAxisMax_lineEdit'] = CAxisMax
        currentFigure.settings['QPlane_CAxisMin_lineEdit'] = CAxisMin
    
def QPlane_SetTitle_button_function(self):
    TitleText=self.ui.QPlane_SetTitle_lineEdit.text()        
    if TitleText == '':
        TitleText = self.ui.QPlane_SetTitle_lineEdit.placeholderText()
    
    currentFigure = self.figureListQPlane.getCurrentFigure()
    if not currentFigure is None:
        currentFigure._title = TitleText
        currentFigure.gca().set_title(TitleText)
        currentFigure.settings['QPlane_SetTitle_lineEdit'] = TitleText
    

def QPlane_Grid_checkBox_toggled_function(self):
    currentFigure = self.figureListQPlane.getCurrentFigure()
    if not currentFigure is None:
        grid = self.ui.QPlane_Grid_checkBox.isChecked()
        currentFigure.gca().grid(grid)
        currentFigure.settings['QPlane_Grid_checkBox'] = grid

def QPlane_DataSet_selectionChanged_function(self):
    ds = self.DataSetModel.getCurrentDataSet()
    if not ds is None:
        title = ds.name
    else:
        title = ''
    self.ui.QPlane_SetTitle_lineEdit.setPlaceholderText(title)

def indexChanged(self,index):
    figure = self.figureListQPlane.figures[index]
    if hasattr(figure,'settings'):
        for setting,value in figure.settings.items():
            if 'radio' in setting or 'checkBox' in setting:
                getattr(getattr(self.ui,setting),'setChecked')(value)
            else:
                getattr(getattr(self.ui,setting),'setText')(str(value))


QPlaneManagerBase, QPlaneManagerForm = loadUI('QPlane.ui')

class QPlaneManager(QPlaneManagerBase, QPlaneManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(QPlaneManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initQPlaneManager()

    def initQPlaneManager(self):
        self.guiWindow.QPlane_plot_button_function = lambda: QPlane_plot_button_function(self.guiWindow)
        self.guiWindow.QPlane_setCAxis_button_function = lambda: QPlane_setCAxis_button_function(self.guiWindow)
        self.guiWindow.QPlane_SetTitle_button_function = lambda: QPlane_SetTitle_button_function(self.guiWindow)
        self.guiWindow.QPlane_Grid_checkBox_toggled_function = lambda: QPlane_Grid_checkBox_toggled_function(self.guiWindow)
        self.guiWindow.QPlane_DataSet_selectionChanged_function = lambda: QPlane_DataSet_selectionChanged_function(self.guiWindow)
        self.guiWindow.QPlane_indexChanged = lambda index: indexChanged(self.guiWindow,index)

        for key,value in self.__dict__.items():
            if 'QPlane' in key:
                self.guiWindow.ui.__dict__[key] = value

        self.guiWindow.figureListQPlane = MatplotlibFigureList(combobox=self.QPlane_figureList_comboBox)
        self.guiWindow.figureList.append(self.guiWindow.figureListQPlane)
        self.QPlane_figureList_comboBox.setModel(self.guiWindow.figureListQPlane)

        self.mplListDelegate = MatplotlibFigureListDelegate()

    def setup(self):
        
        self.guiWindow.ui.QPlane_plot_button.clicked.connect(self.guiWindow.QPlane_plot_button_function)
        self.guiWindow.ui.QPlane_setCAxis_button.clicked.connect(self.guiWindow.QPlane_setCAxis_button_function)
        self.guiWindow.ui.QPlane_SetTitle_button.clicked.connect(self.guiWindow.QPlane_SetTitle_button_function)

        self.guiWindow.ui.QPlane_CAxisMax_lineEdit.returnPressed.connect(self.CAxisChanged)
        self.guiWindow.ui.QPlane_CAxisMin_lineEdit.returnPressed.connect(self.CAxisChanged)

        self.guiWindow.ui.QPlane_Grid_checkBox.toggled.connect(self.guiWindow.QPlane_Grid_checkBox_toggled_function)
        self.guiWindow.ui.QPlane_SetTitle_lineEdit.returnPressed.connect(self.TitleChanged)

        self.guiWindow.DataSetSelectionModel.selectionChanged.connect(self.guiWindow.QPlane_DataSet_selectionChanged_function)
        self.guiWindow.DataSetModel.dataChanged.connect(self.guiWindow.QPlane_DataSet_selectionChanged_function)

        self.guiWindow.figureListQPlane.view.currentIndexChanged.connect(self.guiWindow.QPlane_indexChanged)
        self.guiWindow.ui.QPlane_figureList_comboBox.setItemDelegate(self.mplListDelegate)

    def CAxisChanged(self):
        if self.guiWindow.ui.QPlane_setCAxis_button.isEnabled():
            self.guiWindow.QPlane_setCAxis_button_function()

    def TitleChanged(self):
        if self.guiWindow.ui.QPlane_SetTitle_button.isEnabled():
            self.guiWindow.QPlane_SetTitle_button_function()