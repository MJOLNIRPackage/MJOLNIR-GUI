import sys
#sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments,loadUI
    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.python.DataModels import Cut1DModel
    from MJOLNIRGui.src.main.python.MJOLNIR_Data import Gui1DCutObject
except ImportError:
    from DataModels import Cut1DModel
    from MJOLNIR_Data import Gui1DCutObject
    from _tools import ProgressBarDecoratorArguments,loadUI
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets, uic, QtCore, QtGui
import numpy as np
import matplotlib.pyplot as plt

import itertools

def Cut1D_Delete1D_btn_function(self):
    self.Cut1DModel.delete(self.ui.Cut1D_listView.selectedIndexes())
    self.Cut1DModel.layoutChanged.emit()
    self.Cut1DModel.Cut1D_listView.clearSelection()
    self.update1DCutLabels()
    self.stateMachine.run()


def Cut1D_DoubleClick_Selection_function(self,index,*args,**kwargs):
    self.ui.Cut1D_listView.edit(index)

def setupCut1D(self):
    self.ui.Cut1D_plot_button.clicked.connect(self.Cut1D_plot_button_function)
    self.ui.Cut1D_Generate1D_button.clicked.connect(self.Cut1D_Generate1D_button_function)
    self.ui.Cut1D_Delete1D_btn.clicked.connect(self.Delete1D_button_function)
    self.ui.Cut1D_SetTitle_button.clicked.connect(self.Cut1D_SetTitle_button_function)
    
    self.Cut1DModel = Cut1DModel(Cut1D_listView=self.ui.Cut1D_listView)
    self.ui.Cut1D_listView.setModel(self.Cut1DModel)

    self.Cut1DSelectionModel = self.ui.Cut1D_listView.selectionModel()
    self.Cut1DSelectionModel.selectionChanged.connect(self.selected1DCutChanged)
    
    self.ui.Cut1D_listView.doubleClicked.connect(self.Cut1D_DoubleClick_Selection_function)

    def contextMenu(view,event,gui):
        # Generate a context menu that opens on right click
        position = event.globalPos()
        idx = view.selectedIndexes()
        if len(idx)!=0:
            items = [gui.Cut1DModel.item(i) for i in idx]
            if event.type() == QtCore.QEvent.ContextMenu:
                menu = QtWidgets.QMenu()
                
                if len(idx)==1:
                    text = 'Plot cut'
                else:
                    text = 'Plot cuts individually'
                plot = QtWidgets.QAction(text)
                plot.setToolTip(text) 
                plot.setStatusTip(plot.toolTip())
                plot.triggered.connect(lambda: [self.plotItem(it) for it in items])
                plot.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/plot.png')))

                delete = QtWidgets.QAction('Delete')
                delete.setToolTip('Delete cut(s)') 
                delete.setStatusTip(delete.toolTip())
                delete.triggered.connect(lambda: gui.Cut1DModel.delete(idx))
                delete.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/cross-button.png')))

                menu.addAction(plot)
                if len(idx)>1: # multiple cuts selected at once
                    plotTogether = QtWidgets.QAction('Plot Together')
                    plotTogether.setToolTip('Plot cuts together') 
                    plotTogether.setStatusTip(plot.toolTip())
                    plotTogether.triggered.connect(self.Cut1D_cut1DPlotTogether)
                    plotTogether.setIcon(QtGui.QIcon(self.AppContext.get_resource('Icons/Own/plotMany.png')))
                    menu.addAction(plotTogether)
                menu.addAction(delete)
                return menu.exec_(position)

    self.ui.Cut1D_listView.contextMenuEvent = lambda event: contextMenu(self.ui.Cut1D_listView,event,self)

def selected1DCutChanged(self,*args,**kwargs):
    self.update1DCutLabels()


def update1DCutLabels(self):
    cuts = self.Cut1DModel.rowCount()
    if cuts == 0:
        self.ui.Cut1D_Export1D_btn.setEnabled(False)
        self.ui.Cut1D_ExporCSV_radioBtn.setEnabled(False)
        self.ui.Cut1D_ExporUFIT_radioBtn.setEnabled(False)
    else:
        self.ui.Cut1D_Export1D_btn.setEnabled(True)
        self.ui.Cut1D_ExporCSV_radioBtn.setEnabled(True)
        self.ui.Cut1D_ExporUFIT_radioBtn.setEnabled(True)

    indices = self.Cut1DModel.Cut1D_listView.selectedIndexes()
    if len(indices)>1:
        self.ui.Cut1D_plotTogether_btn.setEnabled(True)
    else:
        self.ui.Cut1D_plotTogether_btn.setEnabled(False)

    if not len(indices) == 0: # If index is selected
        self.Cut1D_indexChanged(indices[0])
        self.ui.Cut1D_Delete1D_btn.setEnabled(True)
    else:
        self.ui.Cut1D_Delete1D_btn.setEnabled(False)

def cut1DPlotTogether(self):
    indices = self.Cut1DModel.Cut1D_listView.selectedIndexes()
    #if len(indices) == 0: return
    ax = None
    for idx in indices:
        ax = self.plotItem(self.Cut1DModel.item(idx),ax=ax)
    ax.legend()

def extractCutParameters(self):
    rlu = self.ui.Cut1D_SelectUnits_RLU_radioButton.isChecked()
    cutQ = self.ui.Cut1D_SelectCut_Q_radioButton.isChecked()

    title = self.ui.Cut1D_SetTitle_lineEdit.text()
    
    HStart = self.ui.Cut1D_HStart_lineEdit.text()
    if cutQ: 
        HEnd = self.ui.Cut1D_HEnd_lineEdit.text()
        KEnd = self.ui.Cut1D_KEnd_lineEdit.text()
    else:
        HEnd = KEnd = LEnd = 0.0
    KStart = self.ui.Cut1D_KStart_lineEdit.text()
    
    if rlu:
        LStart = self.ui.Cut1D_LStart_lineEdit.text()
        if cutQ: 
            LEnd = self.ui.Cut1D_LEnd_lineEdit.text()
    else:
        LStart = 0.0

    

    EMax = float(self.ui.Cut1D_EMax_lineEdit.text())
    EMin = float(self.ui.Cut1D_EMin_lineEdit.text())

    width = float(self.ui.Cut1D_Width_lineEdit.text())
    minPixel = float(self.ui.Cut1D_MinPixel_lineEdit.text())

    ds = self.DataSetModel.getCurrentDataSet()
    
    if rlu:
        q1 = np.array([HStart,KStart,LStart],dtype=float)
        q2 = np.array([HEnd,KEnd,LEnd],dtype=float)
    else:
        q1 = np.array([HStart,KStart],dtype=float)
        q2 = np.array([HEnd,KEnd],dtype=float)


    return ds,q1,q2,width,minPixel,EMax,EMin,cutQ,rlu,title

@ProgressBarDecoratorArguments(runningText='Save Cut1D to folder',completedText='Cut1D saved')
def Cut1D_Export1D_btn_function(self):

    asCSV = self.ui.Cut1D_ExporCSV_radioBtn.isChecked()
    saveString = self.ui.Cut1D_ExportName_lineEdit.text()

    if asCSV:
        saveFolder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Save 1D cuts')

        if not saveFolder is None or saveFolder == '':
            
            if not saveString.split('.')[-1] == 'csv':
                saveString = saveString+'.csv'
            if not '#' in saveString: # Require file name to include a #
                saveString=saveString.replace('.csv','_#.csv')
            for cut in self.Cut1DModel.dataCuts1D:
                name = cut.name.replace(' ','_')
                location = path.join(saveFolder,saveString.replace('#',name))
                cut.save(location)
        else:
            return False
    else:
        if not saveString.split('.')[-1] == 'ufit':
            saveString = saveString+'.ufit'
        location,_ = QtWidgets.QFileDialog.getSaveFileName(self,'Save 1D cuts',saveString)
        if location is None or location == '':
            return False
        if not location.split('.')[-1] == 'ufit':
            location = location+'.ufit'
        
        self.Cut1D_Save_To_uFit(location)
        
        


def checker(q1,q2,width,minPixel,EMax,EMin,cutQ):
    """Checker for 1DCuts. Returns False is an error is detected."""
    success = True
    if EMax<EMin:
        _GUItools.dialog(text='1D Cut could not be made. EMax ({}) < EMin ({})!'.format(EMax,EMin))
        success = False
    if width<0:
        _GUItools.dialog(text='1D Cut could not be made. Q width ({}) is negative!'.format(width))
        success = False
    if minPixel<0:
        _GUItools.dialog(text='1D Cut could not be made. Min Pixel ({}) is negative!'.format(minPixel))
        success = False
    return success


@ProgressBarDecoratorArguments(runningText='Plotting Cut1D',completedText='Plotting Done')
def Cut1D_plot_button_function(self):
    self.Cut1D_Generate1D_button_function()

    self.Cut1DModel.dataCuts1D[-1].plot() # Generates ax but does not return it -.-
    ax = plt.gca()
    self.windows.append(ax.get_figure())
    
    self.Cut1D=ax
    return True


@ProgressBarDecoratorArguments(runningText='Cutting Cut1D',completedText='Cutting Done')
def Cut1D_Generate1D_button_function(self):
    if not self.stateMachine.requireStateByName('Converted'):
        return False

    if self.interactiveCut is None:
        ds,q1,q2,width,minPixel,EMax,EMin,cutQ,rlu,title = extractCutParameters(self)
    else:
        ds,q1,q2,width,minPixel,EMax,EMin,cutQ,rlu = self.interactiveCut
        title = None
    if checker(q1,q2,width,minPixel,EMax,EMin,cutQ) is False:
        return False
    try:
        if cutQ:
            pdData,bins = ds.cut1D(q1=q1,q2=q2,width=width,minPixel=minPixel,Emin=EMin,Emax=EMax,rlu=rlu,constantBins=True,ufit=False)
            parameters = {'q1':q1,'q2':q2,'EMin':EMin,'EMax':EMax,'rlu':rlu,'width':width,'constantBins':True,'minPixel':minPixel,'method':'cut1D','dataset':ds}
            
            # add parameters to correct edits, loop through q. If rlu sizes matches otherwise len(q) = 2 and padding with 0.0
            for q,field in itertools.zip_longest(q1,['Cut1D_HStart_lineEdit','Cut1D_KStart_lineEdit','Cut1D_LStart_lineEdit'],fillvalue=0.0):  
                parameters[field] = q
            for q,field in itertools.zip_longest(q2,['Cut1D_HEnd_lineEdit','Cut1D_KEnd_lineEdit','Cut1D_LEnd_lineEdit'],fillvalue=0.0):  
                parameters[field] = q
            
            parameters['Cut1D_EMax_lineEdit'] = parameters['EMax']
            parameters['Cut1D_EMin_lineEdit'] = parameters['EMin']
            parameters['Cut1D_Width_lineEdit'] = width
            parameters['Cut1D_MinPixel_lineEdit'] = minPixel
            parameters['Cut1D_SelectCut_Q_radioButton'] = True
            parameters['Cut1D_SelectCut_E_radioButton'] = False
            parameters['Cut1D_SelectUnits_RLU_radioButton'] = rlu
            parameters['Cut1D_SelectUnits_AA_radioButton'] = not rlu


        else: # else along E
            pdData,bins = ds.cut1DE(E1=EMin,E2=EMax,q=q1,rlu=rlu,width=width,constantBins=True, minPixel = minPixel,ufit=False)
            parameters = {'EMin':EMin,'EMax':EMax,'q1':q1,'q2':None,'rlu':rlu,'width':width,'constantBins':True,'minPixel':minPixel,'method':'cut1DE','dataset':ds}
            
            for q,field in itertools.zip_longest(q1,['Cut1D_HStart_lineEdit','Cut1D_KStart_lineEdit','Cut1D_LStart_lineEdit','Cut1D_HEnd_lineEdit','Cut1D_KEnd_lineEdit','Cut1D_LEnd_lineEdit'],fillvalue=0.0):  
                parameters[field] = q
            
            parameters['Cut1D_EMax_lineEdit'] = parameters['EMax']
            parameters['Cut1D_EMin_lineEdit'] = parameters['EMin']
            parameters['Cut1D_Width_lineEdit'] = width
            parameters['Cut1D_MinPixel_lineEdit'] = minPixel
            parameters['Cut1D_SelectCut_Q_radioButton'] = False
            parameters['Cut1D_SelectCut_E_radioButton'] = True
            parameters['Cut1D_SelectUnits_RLU_radioButton'] = rlu
            parameters['Cut1D_SelectUnits_AA_radioButton'] = not rlu

        # Generate a Gui1DCutObject
        if not hasattr(self,'cutNumber'):
            self.cutNumber = 1
        if title is None or len(title) == 0:
            title = 'Cut {}'.format(self.cutNumber)
        
        parameters['Cut1D_SetTitle_lineEdit'] = title
        gui1DCut = Gui1DCutObject(name=title,parameters=parameters,pdData=pdData,bins=bins)
        


        self.cutNumber+=1
        self.Cut1DModel.append(gui1DCut)
    except AttributeError as e:
        raise e
        #_GUItools.dialog(text='1D Cut could not be made. Check the limits for the cut and try again!')
        return False


def Cut1D_SetTitle_button_function(self):
    TitleText=self.ui.Cut1D_SetTitle_lineEdit.text()        
    if TitleText == '':
            TitleText = self.ui.Cut1D_SetTitle_lineEdit.getPlaceholderText()
    if hasattr(self, 'Cut1D'):
        self.Cut1D.set_title(TitleText)
        fig = self.Cut1D.get_figure()
        fig.canvas.draw()


def Cut1D_toggle_units_function(self):
    if self.ui.Cut1D_SelectUnits_RLU_radioButton.isChecked(): # changed to RLU
        # Change titles
        self.ui.Cut1D_Hlabel.setText('H')
        self.ui.Cut1D_Klabel.setText('K')
        self.ui.Cut1D_Llabel.setText('L')
        self.ui.Cut1D_LStart_lineEdit.setEnabled(True)
        if self.ui.Cut1D_SelectCut_Q_radioButton.isChecked():
            self.ui.Cut1D_LEnd_lineEdit.setEnabled(True)
    else: # Changing to AA
        self.ui.Cut1D_Hlabel.setText('Qx')
        self.ui.Cut1D_Klabel.setText('Qy')
        self.ui.Cut1D_Llabel.setText('N/A')
        self.ui.Cut1D_LStart_lineEdit.setEnabled(False)
        self.ui.Cut1D_LEnd_lineEdit.setEnabled(False)

def Cut1D_toggle_CutDir_function(self):
    if self.ui.Cut1D_SelectCut_Q_radioButton.isChecked(): # changed to Cut along Q
        self.ui.Cut1D_StartLabel.setText('Start')
        self.ui.Cut1D_StopLabel.setText('Stop')
        self.ui.Cut1D_HEnd_lineEdit.setEnabled(True)
        self.ui.Cut1D_KEnd_lineEdit.setEnabled(True)
        self.ui.Cut1D_MinPixel_label.setText('Min Pixel [1/AA]')
        if self.ui.Cut1D_SelectUnits_RLU_radioButton.isChecked(): # If RLU units
            self.ui.Cut1D_LEnd_lineEdit.setEnabled(True)
    else: # Changing to AA
        self.ui.Cut1D_StartLabel.setText('Point')
        self.ui.Cut1D_StopLabel.setText('N/A')
        self.ui.Cut1D_HEnd_lineEdit.setEnabled(False)
        self.ui.Cut1D_KEnd_lineEdit.setEnabled(False)
        self.ui.Cut1D_LEnd_lineEdit.setEnabled(False)
        self.ui.Cut1D_MinPixel_label.setText('Min Pixel [meV]')


#@ProgressBarDecoratorArguments(runningText='Saving to file',completedText='Saving Done')
def Cut1D_Save_To_uFit(self,saveFile):
    from ufit.gui.session import UfitSession
    from ufit.gui.scanitem import ScanDataItem
    if self.Cut1DModel.rowCount() == 0:
        return

    datasets = self.Cut1DModel.dataCuts1D
    for data in datasets:
        data.ufit.meta['title'] = data.name

    self.ufitsaveFile = saveFile
    session = UfitSession()
    session.add_items([ScanDataItem(data.ufit) for data in datasets])

    if saveFile is None or saveFile == '':
        return False

    if not saveFile.split('.')[-1] == 'ufit':
        saveFile+='.ufit'

    session.set_filename(saveFile)
    session.save()


def plotItem(self,item,ax=None):
    #plot the selected Gui1DCutObject into a new window
    if not ax is None:
        fig = ax.get_figure()
        Append = False # Do not append as it is already appended
    else:
        Append = True
    ax = item.plot(ax=ax)
    fig = ax.get_figure()
    fig.tight_layout()
    if Append:
        self.windows.append(fig)
    return ax

#def Cut1D_Cut_SelectionChanged_function(self):
#self.guiWindow.View3D_indexChanged = lambda index: indexChanged(self.guiWindow,index)

def indexChanged(self,index):
    cut1D = self.Cut1DModel.item(index)
    if hasattr(cut1D,'parameters'):
        for setting,value in cut1D.parameters.items():
            if 'radio' in setting or 'checkBox' in setting:
                getattr(getattr(self.ui,setting),'setChecked')(value)
            elif 'lineEdit' in setting:
                getattr(getattr(self.ui,setting),'setText')(str(value))



def Cut1D_DataSet_selectionChanged_function(self):
    ds = self.DataSetModel.getCurrentDataSet()
    if not ds is None:
        title = ds.name
    else:
        title = ''
    self.ui.Cut1D_SetTitle_lineEdit.setPlaceholderText(title)

Cut1DManagerBase, Cut1DManagerForm = loadUI('Cut1D.ui')

class Cut1DManager(Cut1DManagerBase, Cut1DManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(Cut1DManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initCut1DManager()

    def initCut1DManager(self):
        self.guiWindow.interactiveCut = None # Used to pass in interactive cuts
        self.guiWindow.Cut1D_plot_button_function = lambda: Cut1D_plot_button_function(self.guiWindow)
        self.guiWindow.Cut1D_Generate1D_button_function = lambda: Cut1D_Generate1D_button_function(self.guiWindow)
        self.guiWindow.Cut1D_SetTitle_button_function = lambda: Cut1D_SetTitle_button_function(self.guiWindow)
        self.guiWindow.setupCut1D = lambda: setupCut1D(self.guiWindow)
        self.guiWindow.Cut1D_indexChanged = lambda index: indexChanged(self.guiWindow,index)
        self.guiWindow.Cut1D_cut1DPlotTogether = lambda: cut1DPlotTogether(self.guiWindow)
        self.guiWindow.Cut1D_toggle_units_function = lambda: Cut1D_toggle_units_function(self.guiWindow)
        self.guiWindow.Cut1D_toggle_CutDir_function = lambda: Cut1D_toggle_CutDir_function(self.guiWindow)
        self.guiWindow.Cut1D_Save_To_uFit = lambda location: Cut1D_Save_To_uFit(self.guiWindow,location)
        self.guiWindow.Cut1D_DataSet_selectionChanged_function = lambda: Cut1D_DataSet_selectionChanged_function(self.guiWindow)

        self.guiWindow.plotItem = lambda item,ax=None: plotItem(self.guiWindow,item,ax)

        
        self.guiWindow.Cut1D_DoubleClick_Selection_function = lambda index:Cut1D_DoubleClick_Selection_function(self.guiWindow,index)
        self.guiWindow.Delete1D_button_function = lambda:Cut1D_Delete1D_btn_function(self.guiWindow)
        self.guiWindow.selected1DCutChanged = lambda : selected1DCutChanged(self.guiWindow)
        self.guiWindow.update1DCutLabels = lambda:update1DCutLabels(self.guiWindow)
        self.guiWindow.Cut1D_Export1D_btn_function = lambda:Cut1D_Export1D_btn_function(self.guiWindow)
        for key,value in self.__dict__.items():
            if 'Cut1D' in key:
                self.guiWindow.ui.__dict__[key] = value
        
    def setup(self):
        self.guiWindow.setupCut1D()
        self.guiWindow.ui.Cut1D_SelectUnits_RLU_radioButton.toggled.connect(self.guiWindow.Cut1D_toggle_units_function)
        self.guiWindow.ui.Cut1D_SelectCut_Q_radioButton.toggled.connect(self.guiWindow.Cut1D_toggle_CutDir_function)
        
        self.guiWindow.ui.Cut1D_Export1D_btn.clicked.connect(self.guiWindow.Cut1D_Export1D_btn_function)

        self.guiWindow.ui.Cut1D_SetTitle_lineEdit.returnPressed.connect(self.TitleChanged)

        self.guiWindow.DataSetSelectionModel.selectionChanged.connect(self.guiWindow.Cut1D_DataSet_selectionChanged_function)
        self.guiWindow.DataSetModel.dataChanged.connect(self.guiWindow.Cut1D_DataSet_selectionChanged_function)
        self.guiWindow.ui.Cut1D_plotTogether_btn.clicked.connect(self.guiWindow.Cut1D_cut1DPlotTogether)
    
    
    def TitleChanged(self):
        if self.guiWindow.ui.Cut1D_SetTitle_button.isEnabled():
            self.guiWindow.Cut1D_SetTitle_button_function()