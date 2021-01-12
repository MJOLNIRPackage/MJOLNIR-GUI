import sys
try:
    from StateMachine import State,AllFalseBut,AllTrue,AllFalse,AllTrueBut
except ImportError:
    from .StateMachine import State,AllFalseBut,AllTrue,AllFalse,AllTrueBut



import numpy as np

import platform

platform.system()

if platform.system() == 'Windows':
    markerColor = 'lightblue'
else:
    markerColor = 'palette(Link)'

highlightStyle = "background-color: palette(Link); color: white"
normalStyle = "background-color: palette(midlight)"

## enterStateFunction
def AllEnabled(StateMachine):
    names = [item.objectName() for item in StateMachine.guiWindow.blockItems]
    enabled = np.ones(len(names))
    #enabledNames = ['DataSet_NewDataSet_button',]
    for item,enable in zip(StateMachine.guiWindow.blockItems,enabled):
        item.setEnabled(enable)

    blue = AllFalseBut(['View3D_plot_button','QELine_plot_button','QPlane_plot_button'],enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,blue):
        if enable:
            item.setStyleSheet(highlightStyle)
        else:
            item.setStyleSheet(normalStyle)

def ConvertedEnabled(StateMachine):
    names = [item.objectName() for item in StateMachine.guiWindow.blockItems]
    enabled = np.ones(len(names))
    enabledNames = ['Raw1D_fit_button']
    
    enabled = AllTrueBut(enabledNames,enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,enabled):
        item.setEnabled(enable)

    blue = AllFalseBut(['View3D_plot_button','QELine_plot_button','QPlane_plot_button','Cut1D_plot_button','Cut1D_Generate1D_button'],enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,blue):
        if enable:
            item.setStyleSheet(highlightStyle)
        else:
            item.setStyleSheet(normalStyle)

def RawEnabled(StateMachine):
    names = [item.objectName() for item in StateMachine.guiWindow.blockItems]
    enabled = np.ones(len(names))
    enabledNames = ['DataSet_NewDataSet_button','DataSet_DeleteDataSet_button',
    'DataSet_AddFiles_button','DataSet_DeleteFiles_button','DataSet_convertData_button','DataSet_binning_comboBox',
    'View3D_plot_button','QELine_plot_button','QPlane_plot_button','Raw1D_plot_button','Cut1D_plot_button']
    
    enabled = AllFalseBut(enabledNames,enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,enabled):
        item.setEnabled(enable)

    blue = AllFalseBut(['DataSet_convertData_button','Raw1D_plot_button'],enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,blue):
        if enable:
            item.setStyleSheet(highlightStyle)
        else:
            item.setStyleSheet(normalStyle)


def PartialEnabled(StateMachine):
    names = [item.objectName() for item in StateMachine.guiWindow.blockItems]
    enabled = np.ones(len(names))
    enabledNames = ['DataSet_NewDataSet_button','DataSet_DeleteDataSet_button',
    'DataSet_AddFiles_button',
    'View3D_plot_button','QELine_plot_button','QPlane_plot_button','Raw1D_plot_button','Cut1D_plot_button']
    
    enabled = AllFalseBut(enabledNames,enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,enabled):
        item.setEnabled(enable)

    blue = AllFalseBut(['DataSet_AddFiles_button'],enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,blue):
        if enable:
            item.setStyleSheet(highlightStyle)
        else:
            item.setStyleSheet(normalStyle)
    


def EmptyEnabled(StateMachine):
    names = [item.objectName() for item in StateMachine.guiWindow.blockItems]
    enabled = np.ones(len(names))
    enabledNames = ['DataSet_NewDataSet_button','View3D_plot_button','QELine_plot_button','QPlane_plot_button','Raw1D_plot_button','Cut1D_plot_button']
    
    enabled = AllFalseBut(enabledNames,enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,enabled):
        item.setEnabled(enable)

    blue = AllFalseBut(['DataSet_NewDataSet_button'],enabled,names)
    for item,enable in zip(StateMachine.guiWindow.blockItems,blue):
        if enable:
            item.setStyleSheet(highlightStyle)
        else:
            item.setStyleSheet(normalStyle)
    

## Transition functions

def transitionEmptyPartial(StateMachine): # What is required to transition from empty to partial
    return StateMachine.guiWindow.DataSetModel.rowCount(None)>0

def transitionPartialRaw(StateMachine): # What is required to transition from partial to raw
    count = len(StateMachine.guiWindow.DataSetModel.getCurrentDataSet())
    if not count is None:
        return count>0
    else:
        return False

def transitionRawConverted(StateMachine): # What is required to transition from partial to raw
    ds = StateMachine.guiWindow.DataSetModel.getCurrentDataSet()
    
    if not ds is None:
        val = len(ds.convertedFiles)>0
    else:
        val = False
    
    return val
### Functions to force transition

def forceTransitionEmptyPartial(StateMachine): # add DataSet
    StateMachine.guiWindow.DataSet_NewDataSet_button_function()
    return transitionEmptyPartial(StateMachine)

def forceTransitionPartialRaw(StateMachine): # add DataFile
    StateMachine.guiWindow.DataSet_AddFiles_button_function()
    return transitionPartialRaw(StateMachine)

def forceTansitionRawConverted(StateMachine): # add DataFile
    print(StateMachine.currentState.name)
    StateMachine.guiWindow.convert()
    return True#transitionRawConverted(StateMachine)


### States for state machine

# Allows plotting, fitting and all the fun
converted = State('Converted',nextState=None,enterStateFunction=ConvertedEnabled) 

# Has DataSet, DataFiles but not converded yet
raw = State('Raw',enterStateFunction=RawEnabled,transitionRequirement=transitionRawConverted,
                transitionFunction=forceTansitionRawConverted,nextState=converted)

# Has DataSet but no DataFiles
partial = State('Partial',enterStateFunction=PartialEnabled,transitionRequirement=transitionPartialRaw,
                transitionFunction=forceTransitionPartialRaw,nextState=raw)

# Has no DataSet
empty = State('Empty',enterStateFunction=EmptyEnabled,transitionRequirement=transitionEmptyPartial,
                transitionFunction=forceTransitionEmptyPartial,nextState=partial)
