import sys
sys.path.append('..')

try:
    from MJOLNIRGui.src.main.python._tools import ProgressBarDecoratorArguments
    import MJOLNIRGui.src.main.python._tools as _GUItools
except ImportError:
    from _tools import ProgressBarDecoratorArguments
    import _tools as _GUItools
from os import path
from PyQt5 import QtWidgets,uic,QtGui,QtCore
import numpy as np
from MJOLNIR._tools import calculateMolarMass
import pyperclip

# Handles all functionality related to the NormalizationManager. 

def sampleFormRadioButtonChange(self,state,formLE,massSB): # Function for radio button on form. If set enable LineEdit of form, disable mass SB or reverse
    formLE.setDisabled(not state)
    massSB.setDisabled(state)
    # If state is switched to chemical formula use string in field
    if state: 
        checkValidSampleNormalization(formLE,None,massSB)


# def updateToDataSet(self,formName,event):
#     ds = self.guiWindow.DataSetModel.getCurrentDataSet()
#     attribute = getattr(self.guiWindow.ui,'NormalizationManager_'+formName)
#     if not ds is None: # Only when there is a data set
#         if formName.find('_lineEdit')>0:
#             value=attribute.text().strip()
#             if value == '': # Use standard text instead
#                 value = attribute.placeholderText().strip()
#             print(value)
#         elif formName.find('_spinBox')>0:
#             value=attribute.value()
#         elif formName.find('_checkBox')>0:
#             value=attribute.isChecked()
#         else:
#             value = None
#     ds.currentNormalizationSettings[formName] = value
    
#     attribute.focusOutEvent_old(event)

def checkValidSampleNormalization(self,event,massSB):
    string = self.text()
    try:
        mass = calculateMolarMass(string)
        self.setStyleSheet("color: black;")
    except AttributeError as e:
        self.setStyleSheet("color: red;")
        _GUItools.dialog('When parsing "{}" following error occured:\n'.format(string)+str(e))
        if not event is None:
            self.focusOutEvent_old2(event)
        return None

    if len(string)!=0 and mass==0: # A string was provided but no mass found, typically error in input
        self.setStyleSheet("color: red;")
        _GUItools.dialog('When parsing "{}" no mass was found. Please format the chemical formula correctly, e.g. MnF2'.format(string))
    elif len(string)==0:
        mass = calculateMolarMass(self.placeholderText())
        massSB.setValue(mass)
    else:
        massSB.setValue(mass)
    if not event is None:
        self.focusOutEvent_old2(event)


try:
    NormalizationManagerBase, NormalizationManagerForm = uic.loadUiType(path.join(path.dirname(__file__),"NormalizationManager.ui"))
except:
    try:
        NormalizationManagerBase, NormalizationManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','..','resources','base','Views',"NormalizationManager.ui"))
    except:
        NormalizationManagerBase, NormalizationManagerForm = uic.loadUiType(path.join(path.dirname(__file__),'..','resources','base','Views',"NormalizationManager.ui"))
# All of this connects the buttons and their functions to the main window.

class NormalizationManager(NormalizationManagerBase, NormalizationManagerForm):
    def __init__(self, parent=None, guiWindow=None):
        super(NormalizationManager, self).__init__(parent)
        self.setupUi(self)
        self.guiWindow = guiWindow
        self.initNormalizationManager()
        
    def initNormalizationManager(self):    
        self.sampleGroupBox = self.NormalizationManager_sampleGroupBox_checkBox
        self.nSampleGroupBox = self.NormalizationManager_normalizationSampleGroupBox_checkBox
        self.normalizationButton= self.NormalizationManager_applyNormalization_btn
        self.setup()
        

    def setup(self):
        # # Connect update of value in field with corresponding value in dataset
        # # As this cannot be done in a loop, everything is written out

        # self.NormalizationManager_sampleFormula_lineEdit.focusOutEvent_old = self.NormalizationManager_sampleFormula_lineEdit.focusOutEvent
        # self.NormalizationManager_sampleFormula_lineEdit.focusOutEvent = lambda event: updateToDataSet(self,'sampleFormula_lineEdit',event)

        # self.NormalizationManager_sampleMolarMass_spinBox.focusOutEvent_old = self.NormalizationManager_sampleMolarMass_spinBox.focusOutEvent
        # self.NormalizationManager_sampleMolarMass_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'sampleMolarMass_spinBox',event)

        # self.NormalizationManager_sampleMass_spinBox.focusOutEvent_old = self.NormalizationManager_sampleMass_spinBox.focusOutEvent
        # self.NormalizationManager_sampleMass_spinBox.focusOutEvent= lambda event: updateToDataSet(self,'sampleMass_spinBox',event)

        # self.NormalizationManager_sampleUnitsPerCell_spinBox.focusOutEvent_old = self.NormalizationManager_sampleUnitsPerCell_spinBox.focusOutEvent
        # self.NormalizationManager_sampleUnitsPerCell_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'sampleUnitsPerCell_spinBox',event)

        # self.NormalizationManager_sampleGFactor_spinBox.focusOutEvent_old = self.NormalizationManager_sampleGFactor_spinBox.focusOutEvent
        # self.NormalizationManager_sampleGFactor_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'sampleGFactor_spinBox',event)


        # self.NormalizationManager_normalizationSampleMolarMass_spinBox.focusOutEvent_old = self.NormalizationManager_normalizationSampleMolarMass_spinBox.focusOutEvent
        # self.NormalizationManager_normalizationSampleMolarMass_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'normalizationSampleMolarMass_spinBox',event)

        # self.NormalizationManager_normalizationSampleMass_spinBox.focusOutEvent_old = self.NormalizationManager_normalizationSampleMass_spinBox.focusOutEvent
        # self.NormalizationManager_normalizationSampleMass_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'normalizationSampleMass_spinBox',event)

        # self.NormalizationManager_normalizationSampleUnitsPerCell_spinBox.focusOutEvent_old = self.NormalizationManager_normalizationSampleUnitsPerCell_spinBox.focusOutEvent
        # self.NormalizationManager_normalizationSampleUnitsPerCell_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'normalizationSampleUnitsPerCell_spinBox',event)

        # self.NormalizationManager_normalizationSampleGFactor_spinBox.focusOutEvent_old = self.NormalizationManager_normalizationSampleGFactor_spinBox.focusOutEvent
        # self.NormalizationManager_normalizationSampleGFactor_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'normalizationSampleGFactor_spinBox',event)

        # self.NormalizationManager_normalizationMonitor_spinBox.focusOutEvent_old = self.NormalizationManager_normalizationMonitor_spinBox.focusOutEvent
        # self.NormalizationManager_normalizationMonitor_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'normalizationMonitor_spinBox',event)

        # self.NormalizationManager_normalizationSampleSigmaInc_spinBox.focusOutEvent_old = self.NormalizationManager_normalizationSampleSigmaInc_spinBox.focusOutEvent
        # self.NormalizationManager_normalizationSampleSigmaInc_spinBox.focusOutEvent = lambda event: updateToDataSet(self,'normalizationSampleSigmaInc_spinBox',event)

        # self.NormalizationManager_normalizationSampleFormula_lineEdit.focusOutEvent_old = self.NormalizationManager_normalizationSampleFormula_lineEdit.focusOutEvent
        # self.NormalizationManager_normalizationSampleFormula_lineEdit.focusOutEvent = lambda event: updateToDataSet(self,'normalizationSampleFormula_lineEdit',event)
        
        
        self.sampleGroupBox.clicked.connect(lambda event: self.checkNormalizable(event))
        self.nSampleGroupBox.clicked.connect(lambda event: self.checkNormalizable(event))



        #self.normalizationCheckBox.focusOutEvent_old = lambda event: None
        #self.normalizationCheckBox.clicked.connect(lambda event: updateToDataSet(self,'applyNormalization_checkBox',event))
        



        lostFocus = QtGui.QFocusEvent(QtGui.QEnterEvent.FocusOut) # Event used for return pressed functionality
        ## Shorten naming
        sampleFormLE = self.NormalizationManager_sampleFormula_lineEdit
        sampleMassSB = self.NormalizationManager_sampleMolarMass_spinBox
        sampleFormRB = self.NormalizationManager_sampleFormula_radioButton
        # Rename old focusOutEvent to be used in checkValidSample function
        sampleFormLE.focusOutEvent_old2 = sampleFormLE.focusOutEvent
        # Connect the check validater when focus is lost or enter is pressed
        sampleFormLE.focusOutEvent= lambda event:checkValidSampleNormalization(sampleFormLE,event,sampleMassSB)
        sampleFormLE.returnPressed.connect(lambda: checkValidSampleNormalization(sampleFormLE,lostFocus,sampleMassSB))
        

        # Repeat for normalization fields/buttons
        nSsampleFormLE = self.NormalizationManager_normalizationSampleFormula_lineEdit
        nSampleMassSB = self.NormalizationManager_normalizationSampleMolarMass_spinBox
        nSampleFormRB = self.NormalizationManager_normalizationSampleFormula_radioButton

        nSsampleFormLE.focusOutEvent_old2 = nSsampleFormLE.focusOutEvent
        nSsampleFormLE.focusOutEvent = lambda event:checkValidSampleNormalization(nSsampleFormLE,event,nSampleMassSB)
        nSsampleFormLE.returnPressed.connect(lambda: checkValidSampleNormalization(nSsampleFormLE,lostFocus,nSampleMassSB))
        
        
        # Change enabled fields when radio buttons are activated
        sampleFormRB.toggled.connect(lambda state:sampleFormRadioButtonChange(sampleFormRB,state,formLE=sampleFormLE,massSB=sampleMassSB))
        nSampleFormRB.toggled.connect(lambda state:sampleFormRadioButtonChange(nSampleFormRB,state,formLE=nSsampleFormLE,massSB=nSampleMassSB))

        normalizationButton = self.NormalizationManager_applyNormalization_btn

        normalizationButton.clicked.connect(self.saveNormalization)


        # Enable normalizationButton only when sampleGroupBox is checked ###when either sampleGroupBox or nSampleGroupBox is activated
        #self.sampleGroupBox.clicked.connect(lambda event: groupBoxCheckChanged(self.sampleGroupBox,event,normalizationButton,[self.sampleGroupBox,self.nSampleGroupBox]))
        #self.nSampleGroupBox.clicked.connect(lambda event: groupBoxCheckChanged(self.nSampleGroupBox,event,normalizationButton,[self.sampleGroupBox,self.nSampleGroupBox]))


        # Without a dataset active, set the check boxes disabled
        self.sampleGroupBox.setDisabled(False)
        self.nSampleGroupBox.setDisabled(False)

        #normalizationButton.updateChecked = (lambda state: autoEnable(normalizationButton,state))
        #normalizationButton.toggled.connect(normalizationButton.updateChecked)

        
    def getSampleFormNames(self,sample=True):

        # All line edit forms, spinboxes
        lEFormNames = ['sampleFormula_lineEdit']
        sBFormNames = ['sampleMolarMass_spinBox','sampleMass_spinBox','sampleUnitsPerCell_spinBox','sampleGFactor_spinBox']
        cBFormNames = []
        if sample is False: # Change names to fit to normalization sample
            lEFormNames = [x.replace('sample','normalizationSample') for x in lEFormNames]
            sBFormNames = [x.replace('sample','normalizationSample') for x in sBFormNames]

            sBFormNames.append('normalizationMonitor_spinBox')
            sBFormNames.append('normalizationSampleSigmaInc_spinBox')
        return lEFormNames,sBFormNames,cBFormNames

    def getSampleDict(self,sample=True): # If sample is false, get info from normalization sample
        lEFormNames,sBFormNames, cBFormNames = self.getSampleFormNames(sample)
        sampleDict = {}
        # add values to sampleDict
        for lE in lEFormNames:
            value = getattr(self,'NormalizationManager_'+lE).text().strip()
            if value is None or value=='':
                value = getattr(self,'NormalizationManager_'+lE).placeholderText().strip()
            sampleDict[lE] = value
        
        for sB in sBFormNames:
            sampleDict[sB] = getattr(self,'NormalizationManager_'+sB).value()

        for cB in cBFormNames:
            sampleDict[cB] = getattr(self,'NormalizationManager_'+cB).isChecked()

        #print(sampleDict)
        return sampleDict

    def getSampleInputs(self): # Get all inputs from the fields under sample
        
        
        sampleDict = {}
        # Check if renormalization is applied at all
        #apply = self.normalizationCheckBox.isChecked()
        #sampleDict['applyNormalization_checkBox'] = apply
        sampleDict['sampleGroupBox_checkBox'] = self.sampleGroupBox.isChecked()
        sampleDict['normalizationSampleGroupBox_checkBox'] = self.nSampleGroupBox.isChecked()
        sampleDict.update(self.getSampleDict())
        sampleDict.update(self.getSampleDict(sample=False))

        return sampleDict

    def getActiveNormalization(self):
        sampleDict = {}
        sampleDict['sampleGroupBox_checkBox'] = self.sampleGroupBox.isChecked()
        sampleDict['normalizationSampleGroupBox_checkBox'] = self.nSampleGroupBox.isChecked()


    def saveNormalization(self):
        #print('Hmm I should save this....')
        inputs = self.getSampleInputs()

        returnString = []
        arguments = []

        if inputs['sampleGroupBox_checkBox']: # The sample check box has been choosen
            returnString.append('# Write values for sample normalization\n')
            # Figure out if chemical formula or molar mass is to be used
            if self.NormalizationManager_sampleFormula_radioButton.isChecked(): # if true chemcial formula is to be used
                sampleFormula = inputs['sampleFormula_lineEdit']
                sampleMolarMass = None
                returnString.append('sampleFormula = "'+sampleFormula+'"')
                arguments.append('sampleFormula = sampleFormula')
            else:
                sampleFormula = None
                sampleMolarMass = inputs['sampleMolarMass_spinBox']
                returnString.append('sampleMolarMass = '+str(sampleMolarMass)+' # g/mol')
                arguments.append('sampleMolarMass = sampleMolarMass')
            sampleMass = inputs['sampleMass_spinBox']
            sampleUnitsPerCell = inputs['sampleUnitsPerCell_spinBox']
            sampleGFactor = inputs['sampleGFactor_spinBox']

            returnString.append('sampleMass = '+str(sampleMass)+' # g')
            arguments.append('sampleMass = sampleMass')
            returnString.append('sampleUnitsPerCell = '+str(sampleUnitsPerCell))
            arguments.append('formulaUnitsPerUnitCell = sampleUnitsPerCell')
            returnString.append('sampleGFactor = '+str(sampleGFactor))
            arguments.append('sampleGFactor = sampleGFactor')

            returnString.append('')

        if inputs['normalizationSampleGroupBox_checkBox']: # 
            

            if self.NormalizationManager_normalizationSampleFormula_radioButton.isChecked(): # if true chemcial formula is to be used
                nSampleFormula = inputs['normalizationSampleFormula_lineEdit']
                nSampleMolarMass = None
                returnString.append('normalizationSampleFormula = "'+nSampleFormula+'"')
                arguments.append('vanadiumChemicalFormula = normalizationSampleFormula')
            else:
                nSampleFormula = None
                nSampleMolarMass = inputs['normalizationSampleMolarMass_spinBox']
                returnString.append('normalizationSampleMolarMass = '+str(nSampleMolarMass)+' # g/mol')
                arguments.append('vanadiumMolarMass = normalizationSampleMolarMass')

            nSampleMass = inputs['normalizationSampleMass_spinBox']
            nSampleUnitsPerCell = inputs['sampleUnitsPerCell_spinBox']
            nSampleGFactor = inputs['sampleGFactor_spinBox']
            nSampleMonitor = inputs['normalizationMonitor_spinBox']
            nSampleSigma = inputs['normalizationSampleSigmaInc_spinBox']

            returnString.append('normalizationSampleMass = '+str(nSampleMass)+' # g')
            arguments.append('vanadiumMass = normalizationSampleMass')
            returnString.append('normalizationSampleUnitsPerCell = '+str(nSampleUnitsPerCell))
            arguments.append('vanadiumUnitsPerUnitCell = normalizationSampleUnitsPerCell')
            returnString.append('normalizationSampleGFactor = '+str(nSampleGFactor))
            arguments.append('vanadiumGFactor = normalizationSampleGFactor')
            returnString.append('normalizationSampleMonitor = '+str(nSampleMonitor)+' # Neutron counts in monitor/scan step')
            arguments.append('vanadiumMonitor = normalizationSampleMonitor')
            returnString.append('sigma = '+str(nSampleSigma)+' # Incoherent scattering in Barns')
            arguments.append('vanadiumSigmaIncoherent = sigma')
            returnString.append('')

        else:
            arguments.append('correctVanadium = False')

        args = ''
        arguments.reverse()
        while len(arguments)>0:
           line = ''
           while(len(line)<65) and len(arguments)>0:
               line+=arguments.pop()+', '
           args+=line+'\n'
            
        # Add only to -3 as the last two characters will be ', \n'
        returnString.append('ds.absolutNormalize('+args[:-3]+')')
        #print(arguments)

        pyperclip.copy('\n'.join(returnString))

        self.normalizationButton.setStyleSheet("color: green;")
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.resetApplyButton)
        self.timer.start(1000)
            
            

    def resetApplyButton(self):
        self.normalizationButton.setStyleSheet("color: black;")

    #

    # def updateCurrentDataSetIndex(self):
    #     ds = self.guiWindow.DataSetModel.getCurrentDataSet()
    #     if ds is None:
    #         self.sampleGroupBox.setDisabled(True)
    #         self.nSampleGroupBox.setDisabled(True)
    #     elif len(ds.convertedFiles)==0:
    #         self.sampleGroupBox.setDisabled(True)
    #         self.nSampleGroupBox.setDisabled(True)
    #     else:
    #         self.sampleGroupBox.setDisabled(False)
    #         self.nSampleGroupBox.setDisabled(False)

    #         self.sampleGroupBox.setChecked(bool(ds.currentNormalizationSettings['sampleGroupBox_checkBox']))
    #         self.nSampleGroupBox.setChecked(bool(ds.currentNormalizationSettings['normalizationSampleGroupBox_checkBox']))
            
    #         for sample in [True,False]:
    #             lEFormNames, sBFormNames, cBFormNames = self.getSampleFormNames(sample=sample)
    #             for lE in lEFormNames:
    #                 getattr(self.guiWindow.ui,'NormalizationManager_'+lE).setText(str(ds.currentNormalizationSettings[lE]))
    #             for sB in sBFormNames:
    #                 getattr(self.guiWindow.ui,'NormalizationManager_'+sB).setValue(float(ds.currentNormalizationSettings[sB]))
    #             for cB in cBFormNames:
    #                 getattr(self.guiWindow.ui,'NormalizationManager_'+cB).setChecked(bool(ds.currentNormalizationSettings[cB]))
    
    #     self.checkNormalizable()

    def checkNormalizable(self,event=None):
    #     ds = self.guiWindow.DataSetModel.getCurrentDataSet()
    #     if ds is None:
    #         self.normalizationButton.setText('Apply Normalization')
    #         self.normalizationButton.setDisabled(True)
    #         return None
        
        
    #     ds.currentNormalizationSettings['sampleGroupBox_checkBox'] = self.sampleGroupBox.isChecked()
    #     ds.currentNormalizationSettings['normalizationSampleGroupBox_checkBox'] = self.nSampleGroupBox.isChecked()

    #     normalizable = ds.isNormalizable()
        checkBoxes = [self.sampleGroupBox,self.nSampleGroupBox]
        allowed = np.any([cB.isChecked() for cB in checkBoxes])# and self.guiWindow.stateMachine.getCurrentState().name == 'Converted'
        if allowed == 0:
            self.normalizationButton.setText('Copy to Clipboard')
            self.normalizationButton.setDisabled(True)
            return None
        else:
    #     # If this point is reached, the data set can be normalized or reverted
    # 
    #     if normalizable == -1: # already normalized and has same settings as before
    #         self.normalizationButton.setText('Revert Normalization')
    #         self.normalizationButton.setDisabled(False)
    #     elif normalizable == 1: 
            self.normalizationButton.setText('Copy to Clipboard')
            self.normalizationButton.setDisabled(False)
        

    # def applyNormalization(self):
    #     self.guiWindow.DataSetModel.applyNormalization()
        
    #     self.checkNormalizable()
