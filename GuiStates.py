from StateMachine import State,AllFalseBut,AllTrue,AllFalse,AllTrueBut

import numpy as np



## enterStateFunction
def AllEnabled(StateMachine):
    names = [item.objectName for item in StateMachine.guiWindow.blockItems]
    enabled = np.ones(len(names))
    #enabledNames = ['DataSet_NewDataSet_button',]
    for item,enable in zip(StateMachine.guiWindow.blockItems,enabled):
        item.setEnabled(enable)


## Transition functions

def transitionEmptyPartial(StateMachine): # What is required to transition from empty to partial
    return StateMachine.guiWindow.DataSetModel.rowCount(None)>0

def transitionPartialRaw(StateMachine): # What is required to transition from partial to raw
    count = StateMachine.guiWindow.DataFileModel.rowCount(None)
    if not count is None:
        return count>0 and transitionEmptyPartial(StateMachine)
    else:
        return False

def transitionRawConverted(StateMachine): # What is required to transition from partial to raw
    ds = StateMachine.guiWindow.DataSetModel.getCurrentDataSet()
    if not ds is None:
        return len(ds.convertedFiles)>0
    else:
        return False

### Functions to force transition

def forceTransitionEmptyPartial(StateMachine): # add DataSet
    StateMachine.guiWindow.DataSet_NewDataSet_button_function()

def forceTransitionPartialRaw(StateMachine): # add DataFile
    StateMachine.guiWindow.DataSet_AddFiles_button_function()

def forceTansitionRawConverted(StateMachine): # add DataFile
    StateMachine.guiWindow.DataSet_convertData_button_function()




### States for state machine

# Allows plotting, fitting and all the fun
converted = State('Converted',nextState=None,enterStateFunction=AllEnabled) 

# Has DataSet, DataFiles but not converded yet
raw = State('Raw',enterStateFunction=AllEnabled,transitionRequirement=transitionRawConverted,
                transitionFunction=forceTansitionRawConverted,nextState=converted)

# Has DataSet but no DataFiles
partial = State('Partial',enterStateFunction=AllEnabled,transitionRequirement=transitionPartialRaw,
                transitionFunction=forceTransitionPartialRaw,nextState=raw)

# Has no DataSet
empty = State('Empty',enterStateFunction=AllEnabled,transitionRequirement=transitionEmptyPartial,
                transitionFunction=forceTransitionEmptyPartial,nextState=partial)