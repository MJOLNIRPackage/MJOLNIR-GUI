from PyQt5 import QtCore
from MJOLNIR.Data import DataSet,DataFile,Mask
import numpy as np
#from collections import defaultdict

class GuiDataSet(DataSet.DataSet):
    def __init__(self,dataFiles=None,name='No Name', **kwargs):
        super(GuiDataSet,self).__init__(dataFiles=dataFiles,**kwargs)
        self.name = name
        #self.currentNormalizationSettings = defaultdict(lambda: None) # Holder for newest settings
        #self.normalizationSettings = defaultdict(lambda: None) # Holder for latest used settings
        
    
    def setData(self,column,value):
        if column == 0: self.name = value
        
    def convertDataFile(self,dataFiles=None,guiWindow=None,setProgressBarMaximum=True):
        
        dataFiles = list(self)
        if not guiWindow is None and setProgressBarMaximum:
            guiWindow.setProgressBarMaximum(len(dataFiles)+1)

        convertedFiles = []
        for _,rawfile in enumerate(dataFiles):
            convFile = rawfile.convert()
                
            convertedFiles.append(convFile)
            if not guiWindow is None:
                currentI = guiWindow.getProgressBarValue()
                guiWindow.setProgressBarValue(currentI+1)
            
        self._convertedFiles = []
        self.convertedFiles = convertedFiles    
        
        self._getData()
        if not guiWindow is None:
            guiWindow.setProgressBarValue(len(dataFiles))


    def flags(self):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable

    # def undoAbsolutNormalize(self):
    #     if len(self.convertedFiles)>0: # If there are converted files present, undo normalization
    #         super(GuiDataSet,self).undoAbsolutNormalize()

    #     self.normalizationSettings = {}
    #     print(self.normalizationSettings,self.currentNormalizationSettings)
        
    # def isNormalizable(self): # checks if the current data set can be normalized
    #     # If the current normalization settings are non-zero and equal to previously used values, return -1 to signify an allowance for revert of normalization
    #     if self.currentNormalizationSettings != {} and self.currentNormalizationSettings==self.normalizationSettings:
    #         return -1
    #     if self.currentNormalizationSettings == {}:
    #         return 0
    #     else:
    #         return 1

    # def absolutNormalize(self):
    #     if self.normalizationSettings == self.currentNormalizationSettings:
    #         ## Instead of normalize revert normalization
    #         self.undoAbsolutNormalize()
    #         normalizationParams = self.parent().sampleManager.getSampleInputs()
    #         self.currentNormalizationSettings.update(normalizationParams)
    #         return

    #     self.normalizationSettings.update(self.currentNormalizationSettings)

    #     raise NotImplementedError('Currently not implemented')
    #     sampleMass = self.currentNormalizationSettings['sampleMass_spinBox']
    #     units = self.sampleUnitsPerCell_spinBox
    #     gfactor = self.sampleGFactor_spinBox
    #     chemicalFormula = self.sampleFormula_lineEdit
        
    #     print("Normalized DataSet",sampleMass,units,gfactor,chemicalFormula)

    #     if hasattr(self,'SampleManager_normalizationSampleGroupBox_checkBox'):
    #         if self.SampleManager_normalizationSampleGroupBox_checkBox:
    #             #nMolarMass = self.normalizationSampleMolarMass_spinBox
    #             nChemicalFormula = self.normalizationSampleFormula_lineEdit
    #             nSampleMass = self.normalizationSampleMass_spinBox
    #             nUnits = self.normalizationSampleUnitsPerCell_spinBox
    #             nGfactor = self.normalizationSampleGFactor_spinBox
    #             nMonitor = self.normalizationMonitor_spinBox
    #             nSigma = self.normalizationSampleSigmaInc_spinBox
    #             super(GuiDataSet,self).absolutNormalize(sampleMass=sampleMass,sampleChemicalFormula=chemicalFormula,
    #             formulaUnitsPerUnitCell=units,sampleGFactor=gfactor,correctVanadium=True,vanadiumMass=nSampleMass,vanadiumChemicalFormula=nChemicalFormula,
    #             vanadiumMonitor=nMonitor,vanadiumSigmaIncoherent=nSigma,vanadiumGFactor=nGfactor,vanadiumUnitsPerUnitCell=nUnits)

    #     else:
    #         super(GuiDataSet,self).absolutNormalize(sampleMass=sampleMass,sampleChemicalFormula=chemicalFormula,
    #             formulaUnitsPerUnitCell=units,sampleGFactor=gfactor,correctVanadium=False)
                
class GuiDataFile(DataFile.DataFile):
    def __init__(self,fileLocation, **kwargs):
        super(GuiDataFile,self).__init__(fileLocation=fileLocation,**kwargs)
        binning = 1
        calibrationIndex = list(self.possibleBinnings).index(binning) # Only binning 1 is used for raw plotting
        
        if self.instrument == 'CAMEA':
            EPrDetector = 8 
            detectors = 104
        elif self.type == 'MultiFLEXX':
            EPrDetector = 5
            detectors = 31
        elif self.type == 'FlatCone':
            EPrDetector = 1
            detectors = 31
        else:

            totalDetectors = np.array(self.instrumentCalibrations[calibrationIndex][0].shape[:-1])
            if np.mod(totalDetectors,31)==0: # either MultiFLEXX or FlatCone
                EPrDetector = int(totalDetectors/31)
                detectors = 31
            else: # CAMEA
                EPrDetector = 8 
                detectors = 104
        
        self.maxDetectorSelection = detectors
        self.maxAnalyzerSelection = EPrDetector
        self.detectorSelectionOriginal = self.detectorSelection
        self.analyzerSelectionOriginal = self.analyzerSelection

    def setData(self,column,value):
        if column == 0: self.name = value

    def flags(self):
        return QtCore.Qt.ItemIsEditable

    def convert(self):
        if self.type == 'nxs':
            df = self.original_file
        else:
            df = self
        convertedFile = GuiDataFile(super(GuiDataFile, df).convert(binning = df.binning))
        
        return convertedFile

class Gui1DCutObject(object):
    def __init__(self,name,uFitDataset=None):
        self.name = name
        self.uFitDataset = uFitDataset
    
    def plot(self,*args,**kwargs):
        return self.uFitDataset.plot(*args,**kwargs)

    
class GuiMask(object):
    def __init__(self,name,mask=None):

        self.name = name
        self.mask = mask
