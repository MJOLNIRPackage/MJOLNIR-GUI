
from MJOLNIR import _tools
import numpy as np
from os import path


def startString():
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


def plotViewer3D(dataSetName='ds',binning = None, qx=0.05, qy=0.05, E = 0.08, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', selectView = 2):

    plotString = []

    if binning is None:
        binString = ''
    else:
        binString = 'binning = {},'.format(binning)
    plotString.append('# Run the converter. This automatically generates nxs-file(s). \n'
                        +'# Binning can be changed with binning argument.')
    plotString.append('{:}.convertDataFile({:}saveFile=False)\n\n'.format(dataSetName,binString))

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

    plotString.append("# Above, all data is binned in voxels of size 0.03/AA, 0.03/AA, and 0.05 meV.\n"\
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
        

def generateViewer3DScript(saveFile,dataSetName,dataFiles,binning = None, qx=0.05, qy=0.05, E = 0.08, RLU=True, 
                CAxisMin = 0, CAxisMax = 1e-5, log=False, grid=True, title='', selectView = 2):
    saveString = []
    
    saveString.append(startString())
    saveString.append(loadDataSet(dataSetName=dataSetName,DataFiles=dataFiles))


    saveString.append(plotViewer3D(dataSetName=dataSetName, binning=binning, qx=qx, qy=qy, E=E, 
                                    RLU=RLU, CAxisMin=CAxisMin, CAxisMax=CAxisMax, log=log, grid=grid,
                                    title=title, selectView=selectView))

    saveString = '\n'.join(saveString)
    
    
    with open(saveFile,'w') as file:
        file.write(saveString)

