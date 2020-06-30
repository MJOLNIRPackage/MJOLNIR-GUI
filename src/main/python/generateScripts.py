# All functionality behind the menu options of generate scripts.
import numpy as np
from os import path

from PyQt5 import QtWidgets

from MJOLNIR import _tools
try:
    import MJOLNIRGui._tools as _GUItools
    from MJOLNIRGui._tools import ProgressBarDecoratorArguments
except ImportError:
    import _tools as _GUItools
    from _tools import ProgressBarDecoratorArguments


# The general idea is to generate .py code that will load, convert and plot 
# data using the settings of the gui. Each part of the code to be written is 
# handled by different functions. At the end of the code the functions have to 
# be linked to the main window. If more functions are to be written they have 
# to be connected in MJOLNIR_GUI

def startString():
    # Importing the right things
    importString = []

    importString.append('import matplotlib.pyplot as plt')
    importString.append('try:')
    importString.append('    import IPython')
    importString.append('    shell = IPython.get_ipython()')
    importString.append("    shell.enable_matplotlib(gui='qt')")
    importString.append("except:")
    importString.append("    pass\n\n")


    importString.append('from MJOLNIR import _tools')
    importString.append('from MJOLNIR.Data import DataSet')
    
    importString.append('\nimport numpy as np')
    importString.append('from os import path')
    
    return '\n'.join(importString)

def generateFileLoader(dataFiles):
    """Generate a string to be run in order to load the provided data file paths"""
    try:
        dataFiles = np.concatenate(dataFiles)
    except ValueError:
        pass
    
    dataFiles = np.array(dataFiles)
    
    directories = np.array([path.dirname(df) for df in dataFiles])
    
    uniqueDictionaries, indices = np.unique(directories,return_inverse = True)
        
    fileStrings = []
    
    for I, uDict in enumerate(uniqueDictionaries):
        dfs = dataFiles[indices==I]
        names = np.array([path.splitext(path.basename(df))[0] for df in dfs])
        # Find base name and remove extension
        if len(dfs) != 1:
            prefix = path.commonprefix(list(names))
            
            if 'camea' in prefix:
                # Remove all non-zero digits from prefix
                while prefix[-1]!='0' and prefix[-1]!='n':
                    prefix = prefix[:-1]
                year = int(prefix[5:9])
                numbers = np.array([n[len(prefix):] for n in names],dtype=int)
                sortNumbers = np.sort(numbers)
                diff = np.diff(sortNumbers)
                separators = list(np.arange(len(diff))[diff>1]+1) # add one due to diff removing 1 lenght
                groups = []
                if len(separators) == 0:
                    groups.append('-'.join([str(sortNumbers[0]),str(sortNumbers[-1])]))
                else:
                    separators.insert(0,0)
                    separators.append(-1)
                    for start,stop in zip(separators[:-1],separators[1:]):
                        if stop == -1:
                            group = sortNumbers[start:]
                        else:
                            group = sortNumbers[start:stop]
                        if len(group)>2:
                            groups.append('-'.join([str(group[0]),str(group[-1])]))
                        elif len(group)==2:
                            groups.append(','.join(group.astype(str)))
                        else:
                            groups.append(str(group[0]))
                files = ','.join(groups)
            
                fileStrings.append('_tools.fileListGenerator("{:}",r"{:}",{:})'.format(files,uDict,year))
            else:
                fileStrings.append('["'+'",\n"'.join(dfs)+'"]')
        else:
            
            fileStrings.append('["'+dfs[0]+'"]')
            
            
    if len(fileStrings)>1:
        loadString = 'dataFiles = []\n'
        loadString+= 'dataFiles.append('+')\ndataFiles.append('.join(fileStrings)+')\n'
        loadString+= 'dataFiles = np.concatenate(dataFiles)\n'
        
    else:
        loadString = 'dataFiles = '+fileStrings[0]+'\n'
    
    return loadString


def loadDataSet(dataSetName='ds',DataFiles=None):
    """Generate string to be run in order to load a dataset"""
    
    loadString = []
    if DataFiles is None:
        loadString.append('{} = DataSet.DataSet()'.format(dataSetName))
    else:
        loadString.append(generateFileLoader(DataFiles))
        loadString.append('{} = DataSet.DataSet(dataFiles)'.format(dataSetName))

    return '\n'.join(loadString)

def binDataSet(dataSetName='ds',binning=8):
    plotString = []
    if binning is None:
        binString = ''
    else:
        binString = 'binning = {},'.format(binning)
    plotString.append('# Run the converter. This automatically generates nxs-file(s). \n'
                        +'# Binning can be changed with binning argument.')
    plotString.append('{:}.convertDataFile({:}saveFile=False)\n\n'.format(dataSetName,binString))
    
    return '\n'.join(plotString)


# Below here we have the functions for each option in the menu. 
# First the relevant parameters from the GUI are loaded, then the script is 
# generated using helper functions

@ProgressBarDecoratorArguments(runningText='Generating 3D Script',completedText='Script Saved',failedText='Cancelled')
def generate3DScript(self):
    # Check if data has been loaded. Abort if not
    self.stateMachine.run()
    if not self.stateMachine.currentState.name in ['Raw','Converted']:
        _GUItools.dialog(text='It is not possible to generate a script without any data loaded.')
        return False

    # Save the created script
    folder = self.getCurrentDirectory()
    saveFile = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',folder,"Python (*.py)")[0]
    if len(saveFile)==0:
        return False
    if path.splitext(saveFile)[1] !='.py':
        saveFile = path.splitext(saveFile)[0]+'.py'

    # Start loading information from the GUI
    ds = self.DataSetModel.getCurrentDataSet()
    dataSetName = ds.name
    
    dataFiles = [df.original_file.fileLocation if hasattr(df,'original_file') else df.fileLocation for df in ds]

    binning = self.ui.DataSet_binning_comboBox.currentText()
    qx = self.ui.View3D_QXBin_lineEdit.text()
    qy = self.ui.View3D_QYBin_lineEdit.text()
    E = self.ui.View3D_EBin_lineEdit.text()

    CAxisMin = self.ui.View3D_CAxisMin_lineEdit.text()
    CAxisMax = self.ui.View3D_CAxisMax_lineEdit.text()

    log = self.ui.View3D_LogScale_checkBox.isChecked()
    grid = self.ui.View3D_Grid_checkBox.isChecked()

    title = self.ui.View3D_SetTitle_lineEdit.text()

    RLU = self.ui.View3D_SelectUnits_RLU_radioButton.isChecked()

    radioState = [self.ui.View3D_SelectView_QxE_radioButton.isChecked(),
    self.ui.View3D_SelectView_QyE_radioButton.isChecked(),self.ui.View3D_SelectView_QxQy_radioButton.isChecked()]
    selectView = np.arange(3)[radioState]
    selectView = selectView[0]

    # And generate the script
    generateViewer3DScript(saveFile=saveFile,dataFiles=dataFiles,dataSetName=dataSetName, binning=binning, qx=qx, qy=qy, E=E, 
                                RLU=RLU, CAxisMin=CAxisMin, CAxisMax=CAxisMax, log=log, grid=grid,
                                title=title, selectView=selectView)

    return True



def generateViewer3DScript(saveFile,dataSetName,dataFiles,binning = None, 
                           qx=0.05, qy=0.05, E = 0.08, RLU=True, 
                           CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', selectView = 2):
    # The script is generated by appending the various elements, the joining 
    # them with a \n
    saveString = []
    
    saveString.append(startString())
    saveString.append(loadDataSet(dataSetName=dataSetName,DataFiles=dataFiles))
    
    saveString.append(binDataSet(dataSetName=dataSetName,binning=binning))


    saveString.append(plotViewer3D(dataSetName=dataSetName, qx=qx, qy=qy, E=E, 
                                    RLU=RLU, CAxisMin=CAxisMin, CAxisMax=CAxisMax, log=log, grid=grid,
                                    title=title, selectView=selectView))

    saveString = '\n'.join(saveString)
    with open(saveFile,'w') as file:
        file.write(saveString)    



def plotViewer3D(dataSetName='ds', qx=0.05, qy=0.05, E = 0.08, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', selectView = 2):
    # Generate the actual text for the View3D script

    plotString = []

    # Check which arguments have been used in the GUI. If they are unused or 
    # left to their default values we do not want the argumetns to clutter the generated script.
    if RLU == False:
        rluArgument = ',rlu = False'
    else:
        rluArgument = ''
    
    if log == True:
        logArgument = ', log=True'
    else:
        logArgument = ''

    if grid == True:
        gridArgument = ', grid=True'
    else:
        gridArgument = ', grid=False'

    args = rluArgument+logArgument+gridArgument

    plotString.append('# Plotting data quickly in equi-sized voxels can be done by')
    plotString.append('Viewer = {}.View3D({}{})'.format(dataSetName,','.join([str(x) for x in [qx,qy,E]]),args))

    plotString.append("# Above, all data is binned in voxels of size " +str(qx) + "/AA, " + str(qy) +"/AA, and " +str(E) +" meV.\n"\
                        +"# Automatically, data is plotted in reciprocal lattice as provided by the\n"\
                        +"# UB matrix saved in the data file. Alternatively, one can plot in 'raw'\n"\
                        +"# coordinates (orthogonal and in units of 1/AA) by issuing rlu=False above.\n")
    
    plotString.append('Viewer.caxis=({},{})'.format(CAxisMin,CAxisMax))

    plotString.append("# Without any intervention data is usually plotted on a useless colour scale.\n"\
                        +"# This is countered by specifying min and max for colour by the call above.\n"\
                        +"# Alternatively, one can provide this as input to View3D\n")

    if title !='':
        plotString.append('# Set title of plot')
        plotString.append('Viewer.ax.set_title("{}")\n'.format(title))

    if selectView !=2:
        plotString.append('# Set View direction')
        plotString.append('Viewer.setProjection({})\n'.format(selectView))

    plotString.append('plt.show()\n')
        
    return '\n'.join(plotString)


@ProgressBarDecoratorArguments(runningText='Generating QELine Script',completedText='Script Saved',failedText='Cancelled')
def generateQELineScript(self):
    self.stateMachine.run()
    if not self.stateMachine.currentState.name in ['Raw','Converted']:
        _GUItools.dialog(text='It is not possible to generate a script without any data loaded.')
        return False

    folder = self.getCurrentDirectory()
    saveFile = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',folder,"Python (*.py)")[0]
    if len(saveFile)==0:
        return False
    if path.splitext(saveFile)[1] !='.py':
        saveFile = path.splitext(saveFile)[0]+'.py'

    ds = self.DataSetModel.getCurrentDataSet()
    dataSetName = ds.name
    
    dataFiles = [df.original_file.fileLocation if hasattr(df,'original_file') else df.fileLocation for df in ds]

    binning = self.ui.DataSet_binning_comboBox.currentText()
    
    HStart = self.ui.QELine_HStart_lineEdit.text()
    KStart = self.ui.QELine_KStart_lineEdit.text()
    LStart = self.ui.QELine_LStart_lineEdit.text()
    HEnd = self.ui.QELine_HEnd_lineEdit.text()
    KEnd = self.ui.QELine_KEnd_lineEdit.text()
    LEnd = self.ui.QELine_LEnd_lineEdit.text()
    width = self.ui.QELine_Width_lineEdit.text()
    minPixel = self.ui.QELine_MinPixel_lineEdit.text()
    EMin = self.ui.QELine_EMin_lineEdit.text()
    EMax = self.ui.QELine_EMax_lineEdit.text()
    NPoints = self.ui.QELine_NPoints_lineEdit.text()


    CAxisMin = self.ui.QELine_CAxisMin_lineEdit.text()
    CAxisMax = self.ui.QELine_CAxisMax_lineEdit.text()

    log = self.ui.QELine_LogScale_checkBox.isChecked()
    grid = self.ui.QELine_Grid_checkBox.isChecked()

    title = self.ui.QELine_SetTitle_lineEdit.text()

    RLU = self.ui.QELine_SelectUnits_RLU_radioButton.isChecked()
    
    
    generatePlotQELineScript(saveFile=saveFile,dataSetName=dataSetName,dataFiles=dataFiles,binning = binning, 
                                HStart=HStart, KStart=KStart, LStart = LStart, HEnd=HEnd, KEnd=KEnd, LEnd=LEnd, 
                                width=width, minPixel=minPixel, EMin = EMin, EMax=EMax, NPoints=NPoints, RLU=RLU, 
                                CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title)

    return True    

    
def generatePlotQELineScript(saveFile,dataSetName,dataFiles,binning = None, 
                             HStart=-1, KStart=0.0, LStart = -1, HEnd=-1, KEnd=0, LEnd=1,
                             width=0.1, minPixel=0.01, EMin = 0.0, EMax=10, NPoints=101, RLU=True, 
                             CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title=''):
    saveString = []
    
    saveString.append(startString())
    saveString.append(loadDataSet(dataSetName=dataSetName,DataFiles=dataFiles))
    
    saveString.append(binDataSet(dataSetName=dataSetName,binning=binning))

    saveString.append(plotQELineText(dataSetName=dataSetName, HStart=HStart, KStart=KStart, LStart = LStart, HEnd=HEnd, KEnd=KEnd, LEnd=LEnd,
               width=width, minPixel=minPixel, EMin = EMin,EMax=EMax,NPoints=NPoints, RLU=RLU, 
                CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title))

    saveString = '\n'.join(saveString)    
        
    with open(saveFile,'w') as file:
        file.write(saveString)
        

def plotQELineText(dataSetName='ds', HStart=-1, KStart=0.0, LStart = -1, HEnd=-1, KEnd=0, LEnd=1,
               width=0.1, minPixel=0.01, EMin = 0.0,EMax=10,NPoints=101, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title=''):

    plotString = []

    if RLU == False:
        rluArgument = ',rlu = False'
    else:
        rluArgument = ''
    
    if log == True:
        logArgument = ', log=True'
    else:
        logArgument = ''

    args = rluArgument+logArgument

    plotString.append('# Plotting a cut through data in Q and E is done using this code')
    
    
    plotString.append('# First define the positions to be cut through.')
    plotString.append('# The GUI is limited to two Q points, but more can be added below')
    
    plotString.append('Q1 = np.array([' + HStart + ',' + KStart + ',' + LStart + '])')
    plotString.append('Q2 = np.array([' + HEnd + ',' + KEnd + ',' + LEnd + '])')
    
    plotString.append('# Collect them into one array')
    plotString.append('QPoints = np.array([Q1,Q2])')
    
    plotString.append('# Define orthogonal width and minimum pixel size along Q-cut')
    plotString.append('width = ' + width + ' # 1/AA')
    plotString.append('minPixel = ' + minPixel + ' # 1/AA')
    
    plotString.append('# Define energy bins')
    plotString.append('EnergyBins=np.linspace(' + EMin + ',' + EMax + ',' + NPoints +')')  
        
    
    plotString.append('fig = plt.figure(figsize=(14,6))')
    plotString.append('ax = fig.gca()')
    plotString.append("ax,DataLists,Bins,BinCenters,Offsets = \\" )
    plotString.append('        ' + dataSetName + '.plotCutQELine(QPoints=QPoints, width=width, minPixel=minPixel, \\')
    plotString.append('        ' +'ax=ax, EnergyBins=EnergyBins' +args +')')

    plotString.append("# Without any intervention data is usually plotted on a useless colour scale.\n"\
                        +"# This is countered by specifying min and max for colour by the call below.\n"\
                        +"# Alternatively, one can provide this as input to plotCutQELine\n")

    plotString.append('ax.set_clim(' + CAxisMin + ',' + CAxisMax +')')

    if grid == True:
        plotString.append('ax.grid(True,zorder=0,c=\'k\') ')


    if title !='':
        plotString.append('# Set title of plot')
        plotString.append('ax.set_title("{}")\n'.format(title))

    plotString.append('plt.show()\n')
        
    return '\n'.join(plotString)

        

@ProgressBarDecoratorArguments(runningText='Generating QPlane Script',completedText='Script Saved',failedText='Cancelled')
def generateQPlaneScript(self):
    self.stateMachine.run()
    if not self.stateMachine.currentState.name in ['Raw','Converted']:
        _GUItools.dialog(text='It is not possible to generate a script without any data loaded.')
        return False

    folder = self.getCurrentDirectory()
    saveFile = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',folder,"Python (*.py)")[0]
    if len(saveFile)==0:
        return False
    if path.splitext(saveFile)[1] !='.py':
        saveFile = path.splitext(saveFile)[0]+'.py'

    ds = self.DataSetModel.getCurrentDataSet()
    dataSetName = ds.name
    
    dataFiles = [df.original_file.fileLocation if hasattr(df,'original_file') else df.fileLocation for df in ds]

    binning = self.ui.DataSet_binning_comboBox.currentText()
    
    
    
    EMin = self.ui.QPlane_EMin_lineEdit.text()
    EMax = self.ui.QPlane_EMax_lineEdit.text()

    xBinTolerance = self.ui.QPlane_xBinTolerance_lineEdit.text()
    yBinTolerance = self.ui.QPlane_yBinTolerance_lineEdit.text()

    CAxisMin = self.ui.QPlane_CAxisMin_lineEdit.text()
    CAxisMax = self.ui.QPlane_CAxisMax_lineEdit.text()

    log = self.ui.QPlane_LogScale_checkBox.isChecked()
    grid = self.ui.QPlane_Grid_checkBox.isChecked()

    title = self.ui.QPlane_SetTitle_lineEdit.text()

    RLU = self.ui.QPlane_SelectUnits_RLU_radioButton.isChecked()
    
    
    generatePlotQPlaneScript(saveFile,dataSetName,dataFiles,binning = binning, 
                             xBinTolerance=xBinTolerance, yBinTolerance=yBinTolerance,
                             EMin = EMin,EMax=EMax, RLU=RLU, 
                             CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title)

    return True    


def generatePlotQPlaneScript(saveFile,dataSetName,dataFiles,binning = None, 
                             xBinTolerance=0.03, yBinTolerance=0.03,
                             EMin = 0.0,EMax=10, RLU=True, 
                             CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title=''):
    saveString = []
    
    saveString.append(startString())
    saveString.append(loadDataSet(dataSetName=dataSetName,DataFiles=dataFiles))
    
    saveString.append(binDataSet(dataSetName=dataSetName,binning=binning))
    
    saveString.append(plotQPlaneText(dataSetName=dataSetName, xBinTolerance=xBinTolerance, yBinTolerance=yBinTolerance,
                EMin = EMin,EMax=EMax, RLU=RLU, 
                CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title))

    saveString = '\n'.join(saveString)    
        
    with open(saveFile,'w') as file:
        file.write(saveString)


def plotQPlaneText(dataSetName='ds', xBinTolerance=0.03, yBinTolerance=0.03,
                EMin = 0.0,EMax=10, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title=''):

    plotString = []

    if RLU == False:
        rluArgument = ',rlu = False'
    else:
        rluArgument = ''
    
    if log == True:
        logArgument = ', log=True'
    else:
        logArgument = ''

    args = rluArgument+logArgument

    plotString.append('# Plotting a Q plane done using this code')

    plotString.append('EMin = ' + EMin)
    plotString.append('EMax = ' + EMax)
    plotString.append('xBinTolerance = ' + xBinTolerance)
    plotString.append('yBinTolerance = ' + yBinTolerance)
    plotString.append('Data,Bins,ax = '+ dataSetName + '.plotQPlane(EMin=EMin, EMax=EMax,xBinTolerance=xBinTolerance,yBinTolerance=yBinTolerance' + args + ')')

    plotString.append('fig = ax.get_figure() # Extract figure from returned axis')
    plotString.append('fig.colorbar(ax.pmeshs[0]) # Create colorbar from plot\n')

    plotString.append("# Without any intervention data is usually plotted on a useless colour scale.\n"\
                        +"# This is countered by specifying min and max for colour by the call below.\n"\
                        +"# Alternatively, one can provide this as input to plotCutQPlane\n")

    plotString.append('ax.set_clim(' + CAxisMin + ',' + CAxisMax +')')

    if grid == True:
        plotString.append('ax.grid(True,zorder=0,c=\'k\') ')


    if title !='':
        plotString.append('# Set title of plot')
        plotString.append('ax.set_title("{}")\n'.format(title))

    plotString.append('plt.show()\n')
        
    return '\n'.join(plotString)



@ProgressBarDecoratorArguments(runningText='Generating Cut1D Script',completedText='Script Saved',failedText='Cancelled')
def generateCut1DScript(self):
    self.stateMachine.run()
    if not self.stateMachine.currentState.name in ['Raw','Converted']:
        _GUItools.dialog(text='It is not possible to generate a script without any data loaded.')
        return False

    folder = self.getCurrentDirectory()
    saveFile = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',folder,"Python (*.py)")[0]
    if len(saveFile)==0:
        return False
    if path.splitext(saveFile)[1] !='.py':
        saveFile = path.splitext(saveFile)[0]+'.py'

    ds = self.DataSetModel.getCurrentDataSet()
    dataSetName = ds.name
    
    dataFiles = [df.original_file.fileLocation if hasattr(df,'original_file') else df.fileLocation for df in ds]

    binning = self.ui.DataSet_binning_comboBox.currentText()
    
    HStart = self.ui.Cut1D_HStart_lineEdit.text()
    KStart = self.ui.Cut1D_KStart_lineEdit.text()
    LStart = self.ui.Cut1D_LStart_lineEdit.text()
    HEnd = self.ui.Cut1D_HEnd_lineEdit.text()
    KEnd = self.ui.Cut1D_KEnd_lineEdit.text()
    LEnd = self.ui.Cut1D_LEnd_lineEdit.text()
    width = self.ui.Cut1D_Width_lineEdit.text()
    minPixel = self.ui.Cut1D_MinPixel_lineEdit.text()
    EMin = self.ui.Cut1D_EMin_lineEdit.text()
    EMax = self.ui.Cut1D_EMax_lineEdit.text()



    title = self.ui.Cut1D_SetTitle_lineEdit.text()

    
    
    generatePlotCut1DScript(saveFile=saveFile,dataSetName=dataSetName,dataFiles=dataFiles,binning = binning, 
                                HStart=HStart, KStart=KStart, LStart = LStart, HEnd=HEnd, KEnd=KEnd, LEnd=LEnd, 
                                width=width, minPixel=minPixel, EMin = EMin, EMax=EMax,
                                title=title)

    return True    
        
def generatePlotCut1DScript(saveFile,dataSetName,dataFiles,binning = None, 
                             HStart=-1, KStart=0.0, LStart = -1, HEnd=-1, KEnd=0, LEnd=1,
                             width=0.1, minPixel=0.01, EMin = 0.0, EMax=10, RLU=True, 
                             title=''):
    saveString = []
    
    saveString.append(startString())
    saveString.append(loadDataSet(dataSetName=dataSetName,DataFiles=dataFiles))
    
    saveString.append(binDataSet(dataSetName=dataSetName,binning=binning))

    saveString.append(plotCut1DText(dataSetName=dataSetName, HStart=HStart, KStart=KStart, LStart = LStart, HEnd=HEnd, KEnd=KEnd, LEnd=LEnd,
               width=width, minPixel=minPixel, EMin = EMin,EMax=EMax, 
               title=title))

    saveString = '\n'.join(saveString)    
        
    with open(saveFile,'w') as file:
        file.write(saveString)   
        
def plotCut1DText(dataSetName='ds', HStart=-1, KStart=0.0, LStart = -1, HEnd=-1, KEnd=0, LEnd=1,
               width=0.1, minPixel=0.01, EMin = 0.0,EMax=10,
               title=''):

    plotString = []

    plotString.append('# Plotting a 1D cut through data is done using this code')
    
    
    plotString.append('# First define the positions to be cut through.')
    
    plotString.append('Q1 = np.array([' + HStart + ',' + KStart + ',' + LStart + '])')
    plotString.append('Q2 = np.array([' + HEnd + ',' + KEnd + ',' + LEnd + '])')
    
    plotString.append('# Define orthogonal width and minimum pixel size along Q-cut')
    plotString.append('width = ' + width + ' # 1/AA')
    plotString.append('minPixel = ' + minPixel + ' # 1/AA')
    
    plotString.append('# Define energies')
    plotString.append('EMin='+EMin)
    plotString.append('EMax='+EMax)
    
    plotString.append('ax,*_ = ' +dataSetName +'.plotCut1D(q1=Q1,q2=Q2,width=width,minPixel=minPixel,Emin=EMin,Emax=EMax,rlu=True,constantBins=False)')


    if title !='':
        plotString.append('# Set title of plot')
        plotString.append('ax.set_title("{}")\n'.format(title))

    plotString.append('plt.show()\n')
        
    return '\n'.join(plotString)

# Teach the main window how to call the functions in here.
def initGenerateScript(guiWindow):
    guiWindow.generateQELineScript = lambda: generateQELineScript(guiWindow)
    guiWindow.generate3DScript = lambda: generate3DScript(guiWindow)
    guiWindow.generateQPlaneScript = lambda: generateQPlaneScript(guiWindow)
    guiWindow.generateCut1DScript = lambda: generateCut1DScript(guiWindow)

def setupGenerateScript(guiWindow):
    pass