import sys

from matplotlib.pyplot import polar
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments,loadUI
    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.python.DataModels import MatplotlibFigureList,MatplotlibFigureListDelegate
except ImportError:
    from _tools import ProgressBarDecoratorArguments,loadUI
    import _tools as _GUItools
    from DataModels import MatplotlibFigureList,MatplotlibFigureListDelegate
from os import path
from PyQt5 import QtWidgets, uic
import numpy as np
from MJOLNIR.Data.DraggableShapes import extractCut1DPropertiesRectanglePerpendicular,extractCut1DPropertiesRectangleHorizontal, extractCut1DPropertiesRectangleVertical


@ProgressBarDecoratorArguments(runningText='Generating QELine plot',completedText='QELine plot generated')
def QELine_plot_button_function(self):    
    # First check if we have data, otherwise convert data
    if not self.stateMachine.requireStateByName('Converted'):
        return False
    
    ds = self.DataSetModel.getCurrentDataSet()
    if len(ds.convertedFiles)==0:
        self.DataSet_convertData_button_function()
        
    rlu = self.ui.QELine_SelectUnits_RLU_radioButton.isChecked()
    # Get the Q points
    HStart=float(self.ui.QELine_HStart_lineEdit.text())
    KStart=float(self.ui.QELine_KStart_lineEdit.text())
    
    HEnd=float(self.ui.QELine_HEnd_lineEdit.text())
    KEnd=float(self.ui.QELine_KEnd_lineEdit.text())
    if rlu:
        LStart=float(self.ui.QELine_LStart_lineEdit.text())
        LEnd=float(self.ui.QELine_LEnd_lineEdit.text())
    
            
    if rlu:
        Q1 = np.array([HStart,KStart,LStart])
        Q2 = np.array([HEnd,KEnd,LEnd])
    else:
        Q1 = np.array([HStart,KStart])
        Q2 = np.array([HEnd,KEnd])
   
    # Collect them into one array
    QPoints = np.array([Q1,Q2])
    
    # Define orthogonal width and minimum pixel size along Q-cut
    width = float(self.ui.QELine_Width_lineEdit.text())   
    minPixel = float(self.ui.QELine_MinPixel_lineEdit.text()) 

    # Define energy bins
    EMin=float(self.ui.QELine_EMin_lineEdit.text())
    EMax=float(self.ui.QELine_EMax_lineEdit.text())
    NPoints=int(self.ui.QELine_NPoints_lineEdit.text())       
    dE = (EMax-EMin)/(NPoints+1)
    #EnergyBins=np.linspace(EMin,EMax,NPoints)

    # Check various plot settings

    if self.ui.QELine_LogScale_checkBox.isChecked():
        log=True
    else:
        log=False  
        
    if self.ui.QELine_ConstantBins_checkBox.isChecked():
        constantBins=True
    else:
        constantBins=False              

    cut1DrectanglePerpendicularLocal = lambda viewer,dr:cut1DrectanglePerpendicular(self,viewer,dr)
    cut1DFunctionRectangleHorizontalLocal = lambda viewer,dr:cut1DFunctionRectangleHorizontal(self,viewer,dr)
    cut1DFunctionRectangleVerticalLocal = lambda viewer,dr: cut1DFunctionRectangleVertical(self,viewer,dr)
    #try:
    # Make plot
    ax,Data,bins = \
    ds.plotCutQE(q1=QPoints[0],q2=QPoints[1], width=width, \
                                    minPixel=minPixel, EMin=EMin,EMax=EMax,dE = dE,\
                                    rlu=rlu,cmap=self.colormap,cut1DFunctionRectanglePerpendicular=cut1DrectanglePerpendicularLocal,
                                    cut1DFunctionRectangleHorizontal=cut1DFunctionRectangleHorizontalLocal,
                                    cut1DFunctionRectangleVertical = cut1DFunctionRectangleVerticalLocal,
                                    outputFunction=self.writeToStatus) # log!constantBins=constantBins,

    currentFigure = ax.get_figure()
    self.figureListQELine.append(currentFigure)

    grid = self.ui.QELine_Grid_checkBox.isChecked()
    
    TitleText=self.ui.QELine_SetTitle_lineEdit.text()
    if TitleText == '':
        TitleText = self.ui.QELine_SetTitle_lineEdit.placeholderText()
    CAxisMin=float(self.ui.QELine_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.QELine_CAxisMax_lineEdit.text())

    currentFigure.settings = {'QELine_SelectUnits_RLU_radioButton':rlu,
                    'QELine_SelectUnits_AA_radioButton': not rlu,
                    'QELine_Grid_checkBox':grid!=False,
                    'QELine_LogScale_checkBox':log,
                    'QELine_ConstantBins_checkBox':constantBins,
                    #'View3D_CurratAxe_checkBox':plotCurratAxe,
                    'QELine_HStart_lineEdit':HStart,
                    'QELine_KStart_lineEdit':KStart,
                    'QELine_LStart_lineEdit':LStart,
                    'QELine_HEnd_lineEdit':HEnd,
                    'QELine_KEnd_lineEdit':KEnd,
                    'QELine_LEnd_lineEdit':LEnd,
                    'QELine_Width_lineEdit':width,
                    'QELine_MinPixel_lineEdit':minPixel,
                    'QELine_EMax_lineEdit':EMax,
                    'QELine_EMin_lineEdit':EMin,
                    'QELine_NPoints_lineEdit':NPoints,
                    'QELine_SetTitle_lineEdit':TitleText,
                    'QELine_CAxisMax_lineEdit':CAxisMax,
                    'QELine_CAxisMin_lineEdit':CAxisMin}

    def setClosed(fig):
        fig.closed=True

    closeFunction = lambda event: setClosed(currentFigure)
    currentFigure.canvas.mpl_connect('close_event', closeFunction)
    # Make some final changes to the plot
    self.QELine=ax    
    
    currentFigure.set_size_inches(8,6)

    if self.ui.QELine_Grid_checkBox.isChecked():
        ax.grid(True)
    else:
        ax.grid(False)
    self.QELine_setCAxis_button_function()
    self.QELine_SetTitle_button_function()

    return True
    #except:
    #    _GUItools.dialog(text='QELine cut could not be made. Check the limits for the cut and try again!')
    #    return False

def QELine_Grid_checkBox_toggled_function(self):
    currentFigure = self.figureListQELine.getCurrentFigure()
    if not currentFigure is None:
        grid = self.ui.QELine_Grid_checkBox.isChecked()
        currentFigure.gca().grid(grid)
        currentFigure.settings['QELine_Grid_checkBox'] = grid!=False
        

        
def QELine_toggle_units_function(self):
    if self.ui.QELine_SelectUnits_RLU_radioButton.isChecked(): # changed to RLU
        # Change titles
        self.ui.QELine_HLabel.setText('H')
        self.ui.QELine_KLabel.setText('K')
        self.ui.QELine_LLabel.setText('L')
        self.ui.QELine_LStart_lineEdit.setEnabled(True)
        self.ui.QELine_LEnd_lineEdit.setEnabled(True)
    else: # Changing to AA
        self.ui.QELine_HLabel.setText('Qx')
        self.ui.QELine_KLabel.setText('Qy')
        self.ui.QELine_LLabel.setText('N/A')
        self.ui.QELine_LStart_lineEdit.setEnabled(False)
        self.ui.QELine_LEnd_lineEdit.setEnabled(False)

def QELine_setCAxis_button_function(self):       
    CAxisMin=float(self.ui.QELine_CAxisMin_lineEdit.text())
    CAxisMax=float(self.ui.QELine_CAxisMax_lineEdit.text())
    currentFigure = self.figureListQELine.getCurrentFigure()
    if not currentFigure is None:
        currentFigure.gca().set_clim(CAxisMin,CAxisMax)
        currentFigure.settings['QELine_CAxisMax_lineEdit'] = CAxisMax
        currentFigure.settings['QELine_CAxisMin_lineEdit'] =CAxisMin
        currentFigure.canvas.draw()

def QELine_SetTitle_button_function(self):
    currentFigure = self.figureListQELine.getCurrentFigure()
    if not currentFigure is None:
        TitleText=self.ui.QELine_SetTitle_lineEdit.text()
        if TitleText == '':
            TitleText = self.ui.QELine_SetTitle_lineEdit.placeholderText()
        currentFigure.gca().set_title(TitleText)
        currentFigure._title=TitleText
        currentFigure.settings['QELine_SetTitle_lineEdit'] = TitleText
        currentFigure.canvas.draw()

def QELine_DataSet_selectionChanged_function(self):
    ds = self.DataSetModel.getCurrentDataSet()
    if not ds is None:
        title = ds.name
    else:
        title = ''
    self.ui.QELine_SetTitle_lineEdit.setPlaceholderText(title)

def indexChanged(self,index):
    figure = self.figureListQELine.figures[index]
    if hasattr(figure,'settings'):
        for setting,value in figure.settings.items():
            if 'radio' in setting or 'checkBox' in setting:
                getattr(getattr(self.ui,setting),'setChecked')(value)
            else:
                getattr(getattr(self.ui,setting),'setText')(str(value))
    if not figure is None:
        self.ui.QELine_figureToCSV_pushButton.setEnabled(True)
    else:
        
        self.ui.QELine_figureToCSV_pushButton.setEnabled(False)

@ProgressBarDecoratorArguments(runningText='Save QELine to csv',completedText='QELine saved')
def saveToCSV(self):
    figure = self.figureListQELine.getCurrentFigure()
    ax = figure.gca()
    title = ax.title.get_text()
    location,_ = QtWidgets.QFileDialog.getSaveFileName(self,'Save QELine',str(title)+'.csv','CSV (*.csv)')
    if location is None or location == '':
        return False
    if not location.split('.')[-1] == 'csv':
        location = location+'.csv'
    
    ax.to_csv(location)
    return True

def cut1DrectanglePerpendicular(self,ax,dr):
    # If there is no sample, i.e. 1/AA plot
    if hasattr(ax,'sample'):
        sample = ax.sample
    else:
        sample = None

    # Extract the parameters
    rounding = 4 # Round to 4 digits
    parameters = extractCut1DPropertiesRectanglePerpendicular(dr.rect,sample)

    offset = ax.calculatePosition(parameters['center'][0]).T[0]#ax.convertPlotAxisReal(parameters['center'][0]).T[0]
    
    del parameters['center'] # remove the 'center' as it is not allowed in plotCut1D

    # transform the orthogonal vector if needed 
    if not sample is None:
        orthogonalVector = sample.calculateQxQyToHKL(*ax.orthovec)
    else:
        orthogonalVector = ax.orthovec
    
    # find actual offset along current cut
    offset -= np.dot(orthogonalVector,offset)*orthogonalVector/np.dot(orthogonalVector.T,orthogonalVector)
    
    parameters['q1'] = [np.round(x,rounding) for x in ax.minOrthoPosition+offset]
    parameters['q2'] = [np.round(x,rounding) for x in ax.maxOrthoPosition+offset]

    parameters['minPixel'] = np.round(ax.minPixel,rounding)

    
    # Order of parameters needed is: ds,q1,q2,width,minPixel,EMax,EMin,cutQ,rlu
    self.interactiveCut = [ax.ds,parameters['q1'],parameters['q2'],
                           np.round(parameters['width'],rounding),parameters['minPixel'],np.round(parameters['Emax'],rounding),np.round(parameters['Emin'],rounding),True,parameters['rlu']]
    
    # Perform the cut and plot it
    self.Cut1D_plot_button_function()
    # Reset the interactiveCut flag
    self.interactiveCut = None

def cut1DFunctionRectangleHorizontal(self,ax,dr):
    rounding = 4
    if hasattr(ax,'sample'):
        sample = ax.sample
    else:
        sample = None
    parameters = extractCut1DPropertiesRectangleHorizontal(dr.rect,sample)

    # Convert center point into actual position in Q
    parameters['q1'] = [np.round(x,rounding) for x in ax.calculatePosition(parameters['q1'][0])]#ax.convertPlotAxisReal(parameters['q1'][0]).T[0]]
    parameters['q2'] = [np.round(x,rounding) for x in ax.calculatePosition(parameters['q2'][0])]#ax.convertPlotAxisReal(parameters['q2'][0]).T[0]]
    
    parameters['minPixel'] = np.round(ax.minPixel,rounding)
    parameters['width'] = np.round(ax.width,rounding)

    #Order of parameters needed is: ds,q1,q2,width,minPixel,EMax,EMin,cutQ,rlu
    self.interactiveCut = [ax.ds,parameters['q1'],parameters['q2'],
                           parameters['width'],parameters['minPixel'],np.round(parameters['Emax'],rounding),np.round(parameters['Emin'],rounding),True,parameters['rlu']]
    
    # Perform the cut and plot it
    self.Cut1D_plot_button_function()
    # Reset the interactiveCut flag
    self.interactiveCut = None

def cut1DFunctionRectangleVertical(self,ax,dr):
    rounding = 4
    if hasattr(ax,'sample'):
        sample = ax.sample
    else:
        sample = None
    parameters = extractCut1DPropertiesRectangleVertical(dr.rect,sample)
    
    # Convert center point into actual position in Q
    parameters['q'] = [np.round(x,rounding) for x in ax.calculatePosition(parameters['q']).T]#ax.convertPlotAxisReal(parameters['q']).T[0]]
    
    parameters['minPixel'] = np.round(ax.minPixel,rounding)
    parameters['width'] = np.round(ax.width,rounding)
    self.interactiveCut = [ax.ds,parameters['q'],None,
                           parameters['width'],parameters['minPixel'],np.round(parameters['E2'],rounding),np.round(parameters['E1'],rounding),False,parameters['rlu']]
    
    # Perform the cut and plot it
    self.Cut1D_plot_button_function()
    # Reset the interactiveCut flag
    self.interactiveCut = None

QELineManagerBase, QELineManagerForm = loadUI('QELine.ui')

class QELineManager(QELineManagerBase, QELineManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(QELineManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initQELineManager()

    def initQELineManager(self):
        self.guiWindow.QELine_plot_button_function = lambda: QELine_plot_button_function(self.guiWindow)
        self.guiWindow.QELine_setCAxis_button_function = lambda: QELine_setCAxis_button_function(self.guiWindow)
        self.guiWindow.QELine_SetTitle_button_function = lambda: QELine_SetTitle_button_function(self.guiWindow)
        self.guiWindow.QELine_toggle_units_function = lambda: QELine_toggle_units_function(self.guiWindow)
        self.guiWindow.QELine_DataSet_selectionChanged_function = lambda: QELine_DataSet_selectionChanged_function(self.guiWindow)
        self.guiWindow.QELine_Grid_checkBox_toggled_function = lambda: QELine_Grid_checkBox_toggled_function(self.guiWindow)
        self.guiWindow.QELine_indexChanged = lambda index: indexChanged(self.guiWindow,index)
        self.guiWindow.QELine_saveToCSV = lambda: saveToCSV(self.guiWindow)

        for key,value in self.__dict__.items():
            if 'QELine' in key:
                self.guiWindow.ui.__dict__[key] = value

        ## Set up figure manager. Is to be initialized between manager initialization but before their setup
        self.guiWindow.figureListQELine = MatplotlibFigureList(combobox=self.QELine_figureList_comboBox)
        self.guiWindow.figureList.append(self.guiWindow.figureListQELine)
        self.QELine_figureList_comboBox.setModel(self.guiWindow.figureListQELine)

        self.mplListDelegate = MatplotlibFigureListDelegate()

    def setup(self):
        
        self.guiWindow.ui.QELine_plot_button.clicked.connect(self.guiWindow.QELine_plot_button_function)
        self.guiWindow.ui.QELine_setCAxis_button.clicked.connect(self.guiWindow.QELine_setCAxis_button_function)
        self.guiWindow.ui.QELine_SetTitle_button.clicked.connect(self.guiWindow.QELine_SetTitle_button_function)
        self.guiWindow.ui.QELine_SelectUnits_RLU_radioButton.toggled.connect(self.guiWindow.QELine_toggle_units_function)

        self.guiWindow.ui.QELine_CAxisMax_lineEdit.returnPressed.connect(self.CAxisChanged)
        self.guiWindow.ui.QELine_CAxisMin_lineEdit.returnPressed.connect(self.CAxisChanged)
        self.guiWindow.ui.QELine_Grid_checkBox.toggled.connect(self.guiWindow.QELine_Grid_checkBox_toggled_function)
        self.guiWindow.ui.QELine_SetTitle_lineEdit.returnPressed.connect(self.TitleChanged)

        self.guiWindow.DataSetSelectionModel.selectionChanged.connect(self.guiWindow.QELine_DataSet_selectionChanged_function)
        self.guiWindow.DataSetModel.dataChanged.connect(self.guiWindow.QELine_DataSet_selectionChanged_function)

        self.guiWindow.figureListQELine.view.currentIndexChanged.connect(self.guiWindow.QELine_indexChanged)
        self.guiWindow.ui.QELine_figureList_comboBox.setItemDelegate(self.mplListDelegate)

        self.guiWindow.ui.QELine_figureToCSV_pushButton.clicked.connect(self.guiWindow.QELine_saveToCSV)

    def CAxisChanged(self):
        if self.guiWindow.ui.QELine_setCAxis_button.isEnabled():
            self.guiWindow.QELine_setCAxis_button_function()

    def TitleChanged(self):
        if self.guiWindow.ui.QELine_SetTitle_button.isEnabled():
            self.guiWindow.QELine_SetTitle_button_function()
