# All functionality behind the menu options of generate scripts.
import numpy as np
from os import path

from PyQt5 import QtWidgets

from MJOLNIR import _tools
from MJOLNIR.Data import Mask
import inspect
try:
    import MJOLNIRGui.src.main.python._tools as _GUItools
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
except ImportError:
    import _tools as _GUItools
    from _tools import ProgressBarDecoratorArguments


# The general idea is to generate .py code that will load, convert and plot 
# data using the settings of the gui. Each part of the code to be written is 
# handled by different functions. At the end of the code the functions have to 
# be linked to the main window. If more functions are to be written they have 
# to be connected in MJOLNIR_GUI

def startString(ds):
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
    if not ds._maskingObject is None:
        importString.append('from MJOLNIR.Data import DataSet,Mask') 
    else:
        importString.append('from MJOLNIR.Data import DataSet') 
    
    importString.append('\nimport numpy as np')
    importString.append('from os import path')
    
    return '\n'.join(importString)

def generateFileLoader(dataFiles,name='dataFiles'):
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
                diff = np.diff(numbers)
                separators = list(np.arange(len(diff))[np.logical_and(diff!=1,diff!=-1)]+1) # add one due to diff removing 1 lenght
                groups = []
                if len(separators) == 0:
                    groups.append('-'.join([str(numbers[0]),str(numbers[-1])]))
                else:
                    separators.insert(0,0)
                    separators.append(-1)
                    for start,stop in zip(separators[:-1],separators[1:]):
                        if stop == -1:
                            group = numbers[start:]
                        else:
                            group = numbers[start:stop]
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
        loadString = name+' = []\n'
        loadString+= name+'.append('+')\n'+name+'.append('.join(fileStrings)+')\n'
        loadString+= name+' = np.concatenate('+name+')'
        
    else:
        loadString = name+' = '+fileStrings[0]
    
    return loadString


def loadAndBinDataSet(ds=None,DataFiles=None,convertBeforeSubtract=None,backgroundFiles=None,binning=8,mask=None):
    """Generate string to be run in order to load a dataset"""
    

    
    loadString = []

    if binning is None:
        binString = ''
    else:
        binString = 'binning = {},'.format(binning)

    if DataFiles is None:
        loadString.append('{} = DataSet.DataSet()'.format(ds.name))
    else:
        if not backgroundFiles is None: # Dealing with subtracted data set
            loadString.append(generateFileLoader(DataFiles,name = 'foreground'))
            loadString.append('{} = DataSet.DataSet(foreground)'.format('FG'))
            loadString.append(generateFileLoader(backgroundFiles,name = 'background'))
            loadString.append('{} = DataSet.DataSet(background)'.format('BG'))

            if not convertBeforeSubtract: # Subtract first
                loadString.append('{} = FG - BG'.format(ds.name))
                loadString.append('# Run the converter. This automatically generates nxs-file(s). \n'
                                +'# Binning can be changed with binning argument.')
                loadString.append('{:}.convertDataFile({:}saveFile=False)\n\n'.format(ds.name,binString))

            else:
                loadString.append('# Run the converter. This automatically generates nxs-file(s). \n'
                                +'# Binning can be changed with binning argument.')
                
                loadString.append('{:}.convertDataFile({:}saveFile=False)\n\n'.format('FG',binString))
                loadString.append('{:}.convertDataFile({:}saveFile=False)\n\n'.format('BG',binString))
                loadString.append('{} = FG - BG'.format(ds.name))


        else:
            loadString.append(generateFileLoader(DataFiles))
            loadString.append('{} = DataSet.DataSet(dataFiles)'.format(ds.name))

            loadString.append('# Run the converter. This automatically generates nxs-file(s). \n'
                                +'# Binning can be changed with binning argument.')
            loadString.append('{:}.convertDataFile({:}saveFile=False)\n\n'.format(ds.name,binString))

    if not ds._maskingObject is None:
        loadString.append('\n')
        returnStr,totalMaskName = generateMaskStr(ds._maskingObject)
        loadString.append(returnStr)
        loadString.append('')
        loadString.append('{0}.mask = {1}({0}) # Run mask on DataSet'.format(ds.name,totalMaskName))
        loadString.append('')
        loadString.append('')


    
    
    return '\n'.join(loadString)


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
    
    dataFiles = [df.original_fileLocation if hasattr(df,'original_fileLocation') else df.fileLocation for df in ds]
    if not ds.background is None: # Dealing with a subracted dataset
        convertBeforeSubtract = ds.convertBeforeSubtract
        backgroundFiles = ds.background
    else:
        convertBeforeSubtract = None
        backgroundFiles = None

    binning = self.ui.DataSet_binning_comboBox.currentText()
    qx = self.ui.View3D_QXBin_lineEdit.text()
    qy = self.ui.View3D_QYBin_lineEdit.text()
    E = self.ui.View3D_EBin_lineEdit.text()

    CAxisMin = self.ui.View3D_CAxisMin_lineEdit.text()
    CAxisMax = self.ui.View3D_CAxisMax_lineEdit.text()

    customViewer = self.ui.View3D_Mode_Custom_radioButton.isChecked()
    if self.ui.View3D_CurratAxe_checkBox.isChecked():
        CurratAxeBraggList = self.getBraggPoints()
    else:
        CurratAxeBraggList = None

    log = self.ui.View3D_LogScale_checkBox.isChecked()
    grid = self.ui.View3D_Grid_checkBox.isChecked()
    counts = self.ui.View3D_RawCounts_checkBox.isChecked()

    title = self.ui.View3D_SetTitle_lineEdit.text()

    RLU = self.ui.View3D_SelectUnits_RLU_radioButton.isChecked()

    # And generate the script
    generateViewer3DScript(saveFile=saveFile,dataFiles=dataFiles,ds=ds, binning=binning, qx=qx, qy=qy, E=E, 
                                RLU=RLU, CAxisMin=CAxisMin, CAxisMax=CAxisMax, log=log, grid=grid,
                                title=title,customViewer=customViewer,counts=counts,convertBeforeSubtract=convertBeforeSubtract,
                                backgroundFiles=backgroundFiles,cmap=self.colormap,CurratAxeBraggList=CurratAxeBraggList,)

    return True



def generateViewer3DScript(saveFile,ds,dataFiles,binning = None, 
                           qx=0.05, qy=0.05, E = 0.08, RLU=True, 
                           CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', selectView = 2, customViewer=False,counts=False,
                           convertBeforeSubtract=None,backgroundFiles=None,cmap='viridis',CurratAxeBraggList=None):
    # The script is generated by appending the various elements, the joining 
    # them with a \n
    saveString = []
    
    saveString.append(startString(ds=ds))
    saveString.append(loadAndBinDataSet(ds=ds,DataFiles=dataFiles,convertBeforeSubtract=convertBeforeSubtract,backgroundFiles=backgroundFiles,binning=binning))
    

    saveString.append(plotViewer3D(ds=ds, qx=qx, qy=qy, E=E, 
                                    RLU=RLU, CAxisMin=CAxisMin, CAxisMax=CAxisMax, log=log, grid=grid,
                                    title=title, selectView=selectView, customViewer=customViewer,counts=counts,cmap=cmap,CurratAxeBraggList=CurratAxeBraggList))

    saveString = '\n'.join(saveString)
    with open(saveFile,'w') as file:
        file.write(saveString)    



def plotViewer3D(ds, qx=0.05, qy=0.05, E = 0.08, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', selectView = 2, customViewer=False,counts=False,cmap='viridis',CurratAxeBraggList=None):
    # Generate the actual text for the View3D script

    plotString = []

    # Check which arguments have been used in the GUI. If they are unused or 
    # left to their default values we do not want the argumetns to clutter the generated script.
    if RLU == False and customViewer == False:
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

    if customViewer == True:
        sliceArgument = ', customSlicer = True'
    else:
        sliceArgument = ''

    if counts == True and customViewer == False:
        countsArgument = ', counts = True'
    else:
        countsArgument = ''

    if cmap != 'viridis':
        cmapArgument = ', cmap = "'+cmap+'"'
    else:
        cmapArgument = ''

    if not CurratAxeBraggList is None:
        plotString.append('\n# Make list of Bragg peaks used for Currat-Axe spurion calculation\nCurratAxeBraggList = {}\n\n'.format(CurratAxeBraggList))
        CABraggArgument = ', CurratAxeBraggList=CurratAxeBraggList'
    else:
        CABraggArgument = ''

    args = rluArgument+logArgument+gridArgument+sliceArgument+countsArgument+cmapArgument+CABraggArgument

    plotString.append('# Plotting data quickly in equi-sized voxels can be done by')
    plotString.append('Viewer = {}.View3D({}{})'.format(ds.name,','.join([str(x) for x in [qx,qy,E]]),args))

    plotString.append("# Above, all data is binned in voxels of size " +str(qx) + "/AA, " + str(qy) +"/AA, and " +str(E) +" meV.\n"\
                        +"# Automatically, data is plotted in reciprocal lattice as provided by the\n"\
                        +"# UB matrix saved in the data file. When using the custom viewer, only RLU is supported.\n"\
                        +"#Alternatively, one can plot in 'raw' "\
                        +"coordinates (orthogonal and in units of 1/AA)using the standard viewer \n#by issuing rlu=False above.\n")
    
    plotString.append('Viewer.caxis=({},{})'.format(CAxisMin,CAxisMax))

    plotString.append("# Without any intervention data is usually plotted on a useless colour scale.\n"\
                        +"# This is countered by specifying min and max for colour by the call above.\n"\
                        +"# Alternatively, one can provide this as input to View3D\n")

    if title !='':
        plotString.append('# Set title of plot')
        plotString.append('Viewer.set_title("{}")\n'.format(title))

    if selectView !=2 and customViewer==False:
        plotString.append('# Set View direction')
        plotString.append('Viewer.setProjection({})\n'.format(selectView))

    plotString.append('plt.show()\n')
        
    return '\n'.join(plotString)


@ProgressBarDecoratorArguments(runningText='Generating QE Script',completedText='Script Saved',failedText='Cancelled')
def generateQEScript(self):
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
    
    dataFiles = [df.original_fileLocation if hasattr(df,'original_fileLocation') else df.fileLocation for df in ds]
    if not ds.background is None: # Dealing with a subracted dataset
        convertBeforeSubtract = ds.convertBeforeSubtract
        backgroundFiles = ds.background
    else:
        convertBeforeSubtract = None
        backgroundFiles = None

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

    constantBins = self.ui.QELine_ConstantBins_checkBox.isChecked()

    CAxisMin = self.ui.QELine_CAxisMin_lineEdit.text()
    CAxisMax = self.ui.QELine_CAxisMax_lineEdit.text()

    log = self.ui.QELine_LogScale_checkBox.isChecked()
    grid = self.ui.QELine_Grid_checkBox.isChecked()

    title = self.ui.QELine_SetTitle_lineEdit.text()

    RLU = self.ui.QELine_SelectUnits_RLU_radioButton.isChecked()
    
    
    generatePlotQEScript(saveFile=saveFile,ds=ds,dataFiles=dataFiles,binning = binning, 
                                HStart=HStart, KStart=KStart, LStart = LStart, HEnd=HEnd, KEnd=KEnd, LEnd=LEnd, 
                                width=width, minPixel=minPixel, EMin = EMin, EMax=EMax, NPoints=NPoints, RLU=RLU, 
                                CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title, constantBins=constantBins,
                                convertBeforeSubtract=convertBeforeSubtract,backgroundFiles=backgroundFiles,cmap=self.colormap)

    return True    

    
def generatePlotQEScript(saveFile,ds,dataFiles,binning = None, 
                             HStart=-1, KStart=0.0, LStart = -1, HEnd=-1, KEnd=0, LEnd=1,
                             width=0.1, minPixel=0.01, EMin = 0.0, EMax=10, NPoints=101, RLU=True, 
                             CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', constantBins=False,
                             convertBeforeSubtract=None,backgroundFiles=None,cmap='viridis'):
    saveString = []
    
    saveString.append(startString(ds=ds))
    saveString.append(loadAndBinDataSet(ds=ds,DataFiles=dataFiles,convertBeforeSubtract=convertBeforeSubtract,backgroundFiles=backgroundFiles,binning=binning))

    saveString.append(plotQEText(ds=ds, HStart=HStart, KStart=KStart, LStart = LStart, HEnd=HEnd, KEnd=KEnd, LEnd=LEnd,
               width=width, minPixel=minPixel, EMin = EMin,EMax=EMax,NPoints=NPoints, RLU=RLU, 
                CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title, constantBins=constantBins,cmap=cmap))

    saveString = '\n'.join(saveString)    
        
    with open(saveFile,'w') as file:
        file.write(saveString)
        

def plotQEText(ds, HStart=-1, KStart=0.0, LStart = -1, HEnd=-1, KEnd=0, LEnd=1,
               width=0.1, minPixel=0.01, EMin = 0.0,EMax=10,NPoints=101, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', constantBins=False,cmap='viridis'):

    plotString = []

    if RLU == False:
        rluArgument = ',rlu = False'
    else:
        rluArgument = ''
    
    if log == True:
        logArgument = ', log=True'
    else:
        logArgument = ''

    if cmap != 'viridis':
        cmapArgument = ', cmap = "'+cmap+'"'
    else:
        cmapArgument = ''

    args = rluArgument+logArgument+cmapArgument

    plotString.append('# Plotting a cut through data in Q and E is done using this code')
    
    
    plotString.append('# First define the positions to be cut through.')
    plotString.append('# The GUI is limited to two Q points, but more can be added below')
    
    plotString.append('Q1 = np.array([' + HStart + ',' + KStart + ',' + LStart + '])')
    plotString.append('Q2 = np.array([' + HEnd + ',' + KEnd + ',' + LEnd + '])')
    
    plotString.append('# Define orthogonal width and minimum pixel size along Q-cut')
    plotString.append('width = ' + width + ' # 1/AA')
    plotString.append('minPixel = ' + minPixel + ' # 1/AA')
    
    plotString.append('# Define energy bins')
    plotString.append('EnergyBins=np.linspace(' + EMin + ',' + EMax + ',' + NPoints +')')  
        
    
    plotString.append("ax,Data,Bins = \\" )
    plotString.append('        ' + ds.name + '.plotCutQE(q1=Q1, q2=Q2, width=width, minPixel=minPixel, \\')
    plotString.append('        ' +'EnergyBins=EnergyBins' +args +')')

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
    
    dataFiles = [df.original_fileLocation if hasattr(df,'original_fileLocation') else df.fileLocation for df in ds]
    if not ds.background is None: # Dealing with a subracted dataset
        convertBeforeSubtract = ds.convertBeforeSubtract
        backgroundFiles = ds.background
    else:
        convertBeforeSubtract = None
        backgroundFiles = None

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
    
    
    generatePlotQPlaneScript(saveFile,ds,dataFiles,binning = binning, 
                             xBinTolerance=xBinTolerance, yBinTolerance=yBinTolerance,
                             EMin = EMin,EMax=EMax, RLU=RLU, 
                             CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title,
                             convertBeforeSubtract=convertBeforeSubtract,backgroundFiles=backgroundFiles,cmap=self.colormap)

    return True    


def generatePlotQPlaneScript(saveFile,ds,dataFiles,binning = None, 
                             xBinTolerance=0.03, yBinTolerance=0.03,
                             EMin = 0.0,EMax=10, RLU=True, 
                             CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='',
                             convertBeforeSubtract=None,backgroundFiles=None,cmap='viridis'):
    saveString = []
    
    saveString.append(startString(ds=ds))
    saveString.append(loadAndBinDataSet(ds=ds,DataFiles=dataFiles,convertBeforeSubtract=convertBeforeSubtract,backgroundFiles=backgroundFiles,binning=binning))
    
    saveString.append(plotQPlaneText(ds=ds, xBinTolerance=xBinTolerance, yBinTolerance=yBinTolerance,
                EMin = EMin,EMax=EMax, RLU=RLU, 
                CAxisMin = CAxisMin, CAxisMax = CAxisMax, log=log, grid=grid, title=title,cmap=cmap))

    saveString = '\n'.join(saveString)    
        
    with open(saveFile,'w') as file:
        file.write(saveString)


def plotQPlaneText(ds, xBinTolerance=0.03, yBinTolerance=0.03,
                EMin = 0.0,EMax=10, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='',cmap='viridis'):

    plotString = []

    if RLU == False:
        rluArgument = ',rlu = False'
    else:
        rluArgument = ''
    
    if log == True:
        logArgument = ', log=True'
    else:
        logArgument = ''

    if cmap != 'viridis':
        cmapArgument = ', cmap = "'+cmap+'"'
    else:
        cmapArgument = ''
    args = rluArgument+logArgument+cmapArgument

    plotString.append('# Plotting a Q plane done using this code')

    plotString.append('EMin = ' + EMin)
    plotString.append('EMax = ' + EMax)
    plotString.append('xBinTolerance = ' + xBinTolerance)
    plotString.append('yBinTolerance = ' + yBinTolerance)
    plotString.append('Data,Bins,ax = '+ ds.name + '.plotQPlane(EMin=EMin, EMax=EMax,xBinTolerance=xBinTolerance,yBinTolerance=yBinTolerance' + args + ')')

    plotString.append('fig = ax.get_figure() # Extract figure from returned axis')
    plotString.append('fig.colorbar(ax.pmeshs[0]) # Create colorbar from plot\n')

    plotString.append("# Without any intervention data is usually plotted on a useless colour scale.\n"\
                        +"# This is countered by specifying min and max for colour by the call below.\n"\
                        +"# Alternatively, one can provide this as input to plotCutQPlane\n")

    plotString.append('ax.set_clim(' + CAxisMin + ',' + CAxisMax +')')

    if grid == True:
        plotString.append('ax.grid(True,zorder=0) ')


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

    if self.Cut1DModel.rowCount() == 0:
        _GUItools.dialog(text='It is not possible to generate a script without any cuts performed. Please make a cut using the "Generate 1D cut" or Plot 1D cut" buttons.')
        return False

    folder = self.getCurrentDirectory()
    saveFile = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',folder,"Python (*.py)")[0]
    if len(saveFile)==0:
        return False
    if path.splitext(saveFile)[1] !='.py':
        saveFile = path.splitext(saveFile)[0]+'.py'

    ds = self.DataSetModel.getCurrentDataSet()
    
    dataFiles = [df.original_fileLocation if hasattr(df,'original_fileLocation') else df.fileLocation for df in ds]
    if not ds.background is None: # Dealing with a subracted dataset
        convertBeforeSubtract = ds.convertBeforeSubtract
        backgroundFiles = ds.background
    else:
        convertBeforeSubtract = None
        backgroundFiles = None

    binning = self.ui.DataSet_binning_comboBox.currentText()
    
    saveString = []
    saveString.append(startString(ds=ds))
    saveString.append('\n\n')
    saveString.append(loadAndBinDataSet(ds=ds,DataFiles=dataFiles,convertBeforeSubtract=convertBeforeSubtract,backgroundFiles=backgroundFiles,binning=binning))
    self.appendPLTSHOW = False # Flag to keep track of the need for a plt.show() command
    if self.Cut1DModel.rowCount() == 1:
        cut = self.Cut1DModel.dataCuts1D[0]
        saveString.append(plotCut1DText(ds,cut,single=True,self=self))
    else:
        
        for cut in self.Cut1DModel.dataCuts1D:
            saveString.append(plotCut1DText(ds,cut,single=False,self=self))
            saveString.append('\n')

    if self.appendPLTSHOW:
        saveString.append('\nplt.show()')
    saveString.append('\n\n#If a ufit object is needed, add "ufit=True" to the above method calls and change "_data" and "_bins" to "_ufit".')
    with open(saveFile,'w') as file:
        file.write(''.join(saveString))
    return True    
        
        
def plotCut1DText(ds, cut,single=True,self=None):
    title = cut.name.replace(' ','_')
    if cut.parameters['method'].find('cut1DE')>-1: # If the method contains "cut1DE" it is for constant q
        q = cut.parameters['q1']
        EMin,EMax = cut.parameters['EMin'],cut.parameters['EMax']
        rlu,width = cut.parameters['rlu'],cut.parameters['width']
        minPixel = cut.parameters['minPixel']
        constantBins = cut.parameters['constantBins']
        ufit = not cut._ufit is None
        method = cut.parameters['method']

        if cut.parameters['method'].find('plot')>-1:
            returnPars = title+'_ax,'
        else:
            returnPars = ''
        if ufit:
            returnPars+=title+'_cut'
        else:
            returnPars+=title+'_data,'+title+'_bins'

        plotString = []
        if single:
            plotString.append('# Plotting a 1D cut for constant q through data is done using this code')
            plotString.append('# First define the positions to be cut through.')
            
            plotString.append('q = np.array(['+','.join([str(x) for x in q])+ '])')
            
            plotString.append('# Define orthogonal width and minimum pixel size along Q-cut')
            plotString.append('width = ' + str(width) + ' # 1/AA')
            plotString.append('minPixel = ' + str(minPixel) + ' # 1/AA')
            plotString.append('rlu = ' + str(rlu))
            plotString.append('constantBins = ' + str(constantBins))

            plotString.append('# Define energies')
            plotString.append('E1='+str(EMin))
            plotString.append('E2='+str(EMax))
            
            plotString.append(returnPars+' = ' +ds.name +'.'+method+'(E1=E1,E2=E2,q=q,width=width,minPixel=minPixel,rlu=rlu,constantBins=constantBins,ufit='+str(ufit)+')')
        else:
            plotString.append(returnPars+' = ' +ds.name +'.'+method+'(E1={},E2={},q={},width={},minPixel={},rlu={},constantBins={},ufit={})'.format(
            EMin,EMax,'['+','.join([str(x) for x in q])+ ']',width,minPixel,rlu,constantBins,ufit))
        
    else:
        q1,q2 = cut.parameters['q1'], cut.parameters['q2']
        EMin,EMax = cut.parameters['EMin'],cut.parameters['EMax']
        rlu,width = cut.parameters['rlu'],cut.parameters['width']
        minPixel = cut.parameters['minPixel']
        constantBins = cut.parameters['constantBins']
        ufit = not cut._ufit is None
        method = cut.parameters['method']

        plotString = []

        if method.find('plot')>-1:
            returnPars = title+'_ax,'
        else:
            returnPars = ''
        if ufit:
            returnPars+=title+'_cut'
        else:
            returnPars+=title+'_data,'+title+'_bins'

        if single:
            plotString.append('# Plotting a 1D cut through data is done using this code')
            
            
            plotString.append('# First define the positions to be cut through.')
            
            plotString.append('Q1 = np.array(['+','.join([str(x) for x in q1])+ '])')
            plotString.append('Q2 = np.array(['+','.join([str(x) for x in q2])+ '])')
            
            plotString.append('# Define orthogonal width and minimum pixel size along Q-cut')
            plotString.append('width = ' + str(width) + ' # 1/AA')
            plotString.append('minPixel = ' + str(minPixel) + ' # 1/AA')
            plotString.append('rlu = ' + str(rlu))
            plotString.append('constantBins = ' + str(constantBins))

            plotString.append('# Define energies')
            plotString.append('EMin='+str(EMin))
            plotString.append('EMax='+str(EMax))

            plotString.append(returnPars+' = ' +ds.name +'.'+method+'(q1=Q1,q2=Q2,width=width,minPixel=minPixel,Emin=EMin,Emax=EMax,rlu=True,constantBins=constantBins,ufit='+str(ufit)+')')
        else:
            plotString.append(returnPars+' = ' +ds.name +'.'+method+'(q1={},q2={},width={},minPixel={},Emin={},Emax={},rlu={},constantBins={},ufit={})'.format(
                '['+','.join([str(x) for x in q1])+ ']','['+','.join([str(x) for x in q2])+ ']',width,minPixel,EMin,EMax,rlu,constantBins,ufit
            ))

    if method.find('plot')>-1:
        plotString.append('# Set title of plot')
        plotString.append(title+'_ax.set_title("{}")\n'.format(cut.name))
        self.appendPLTSHOW = True

        
    return '\n'.join(plotString)

# Teach the main window how to call the functions in here.
def initGenerateScript(guiWindow):
    guiWindow.generateQEScript = lambda: generateQEScript(guiWindow)
    guiWindow.generate3DScript = lambda: generate3DScript(guiWindow)
    guiWindow.generateQPlaneScript = lambda: generateQPlaneScript(guiWindow)
    guiWindow.generateCut1DScript = lambda: generateCut1DScript(guiWindow)

def setupGenerateScript(guiWindow):
    pass

def generateMaskStr(maskingObject):
    
    def generateMask(mask):
        makeStr = []
        signature = inspect.signature(type(mask).__init__)
        
        paramDict = {}
        maskName = mask.name
        for param in signature.parameters:
            if param == 'self': continue
            paramDict[param] = getattr(mask,param)
            if not isinstance(paramDict[param],(np.ndarray)):
                if isinstance(paramDict[param],(str)):
                    makeStr.append(maskName+'_'+param+' = "'+str(paramDict[param])+'"')
                else:
                    makeStr.append(maskName+'_'+param+' = '+str(paramDict[param]))
            else:
                makeStr.append(maskName+'_'+param+' = np.array('+np.array2string(paramDict[param],separator=',')+')')
            
        makeStr.append('')
        makeStr.append(paramDict['name']+' = Mask.'+type(mask).__name__+'(')
        for idx,key in enumerate(paramDict):
            makeStr.append('\t'+key+' = '+maskName+'_'+key+','*(idx!=len(paramDict)-1)+')'*(idx==len(paramDict)-1))
    
        return '\n'.join(makeStr)
    
    eq,masks = Mask.extract(maskingObject)
    masks.sort(key=lambda mask:mask.name)
    defineMaskStr = ['# Generate individual masks']+[generateMask(mask) for mask in masks]
    totalMaskName = 'totalMask'
    while totalMaskName in [m.name for m in masks]:
        try:
            idx = int(totalMaskName.split('_')[-1])
        except ValueError:
            totalMaskName = totalMaskName+'_1'
        else:
            totalMaskName = totalMaskName[:-(len(str(idx))+1)] + '_' + str(idx+1)
    
    maskStr = '\n\n'.join(['\n\n'.join(defineMaskStr),totalMaskName+' = '+eq])

    return maskStr,totalMaskName