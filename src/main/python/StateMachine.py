# State machine and corresponding classes to deal with gui movements

import numpy as np

class State(object):
    def __init__(self,name,nextState,enterStateFunction=None,transitionRequirement=None,transitionFunction=None,):
        """Create a state
        Args:
            - name (str): Name of state
            - nextState (State): Next state 
        Kwargs:
            - enterStateFunction (function): Function called by StateMachine as fun(self) (default lambda self: None)
            - transitionRequirement (function): Function returning possibility of transitioning to next state called by StateMachine as fun(self) (default lambda: False) 
            - transitionFunction (function): Function to be called to force transition to next state called by StateMachine as fun(self) (default None -> Raises error)
            
        """
        self.name = name

        if transitionRequirement is None:
            transitionRequirement = lambda self: False
        
        if enterStateFunction is None:
            enterStateFunction = lambda self: None

        self.enterStateFunction = enterStateFunction
        self.transitionRequirement = transitionRequirement
        self.nextState = nextState
        self.transitionFunction = transitionFunction




class StateMachine(object):
    def __init__(self,states,guiWindow=None):

        self.states = states
        self.stateNames = [s.name for s in self.states]
        self.guiWindow = guiWindow
        self.currentState = states[0]

    def run(self):
        """Run the machine until it cannot go any further"""
        self.currentState = self.states[0]
        while self.checkTransitionToNextState() == True: # transition requirement is made
            self.transition()
        
        self.currentState.enterStateFunction(self)
        self.guiWindow.update()
    
    def forceRun(self,checkFunction=lambda self:True):
        """Force machine to run until checkFunction returns True or next state is None"""

        while not (self.currentState.nextState is None) and (not checkFunction(self)):
            if self.checkTransitionToNextState() == False:
                if not self.currentState.transitionFunction(self):
                    return checkFunction(self)
            self.transition()
            
        self.currentState.enterStateFunction(self)
        self.guiWindow.update()
        return checkFunction(self)

    def requireStateByName(self,name):
        """Force run state machine until state with 'name' is reached"""
        #resquestIdx = self.stateNames.index(name)
        #currentIdx = self.states.index(self.currentState)
        #if currentIdx<resquestIdx:
        if not name in self.stateNames:
            raise AttributeError('Wanted name is not in list of state names! These are\n','\n'.join(self.stateNames))
        self.currentState = self.states[0]
        def checkName(self,Name):
            return self.currentState.name == Name

        check = lambda self: checkName(self,name)
        return self.forceRun(check)


    def step(self):
        if self.checkTransitionToNextState():
            self.transition()
            self.currentState.enterStateFunction(self)
            self.guiWindow.update()
            
        
    def transition(self):
        if self.checkTransitionToNextState():
            nextState = self.currentState.nextState
            if nextState is not None:
                self.currentState = nextState
                

    def getCurrentState(self):
        return self.currentState

    def checkTransitionToNextState(self):
        return self.currentState.transitionRequirement(self)

    @property
    def currentState(self):
        return self._currentState

    @currentState.getter
    def currentState(self):
        return self._currentState

    @currentState.setter
    def currentState(self,newState):
        if not isinstance(newState,State):
            raise AttributeError('Provided attribute is not a State')
        self._currentState = newState

        


def AllFalse(Buttons):
    return list(np.zeros_like(Buttons,dtype=bool))

def AllTrue(Buttons):
    return list(np.ones_like(Buttons,dtype=bool))

def AllFalseBut(names,buttons,buttonNames):
    buttons = AllFalse(buttons)
    for name in names:
        idx = buttonNames.index(name)
        buttons[idx] = True
    return buttons

def AllTrueBut(names,buttons,buttonNames):
    buttons = AllTrue(buttons)
    for name in names:
        idx = buttonNames.index(name)
        buttons[idx] = False
    return buttons



if __name__ == '__main__':
    ds = []
    df = []
    cf = []

    def EmptyStateInit(self):
        self.buttons = AllFalseBut(['AddDataset','AddDataFile'],self.buttons,self.buttonNames)

    def PartialStateInit(self):
        self.buttons = AllFalseBut(['AddDataset','AddDataFile'],self.buttons,self.buttonNames)

    def RawStateInit(self):
        self.buttons = AllTrueBut(['Plot'],self.buttons,self.buttonNames)

    def ConvertedStateInit(self):
        self.buttons = AllTrue(self.buttons)


    def ConvertedRequirement(ds,df,cf):
        return np.all([len(ds)!=0,len(df)!=0,len(cf)!=0])

    def RawRequirement(ds,df):
        return np.all([len(ds)!=0,len(df)!=0])

    def PartialRequirement(ds):
        return len(ds)!=0

    def addToList(ds):
        ds.append(0)
    
        

    converted = State('Converted',nextState=None,enterStateFunction=ConvertedStateInit)

    raw = State('Raw',enterStateFunction=RawStateInit,transitionRequirement=lambda:ConvertedRequirement(ds=ds,df=df,cf=cf),
                    transitionFunction=lambda:addToList(cf),nextState=converted)
    partial = State('Partial',enterStateFunction=PartialStateInit,transitionRequirement=lambda:RawRequirement(ds=ds,df=df),
                    transitionFunction=lambda:addToList(df),nextState=raw)

    empty = State('Empty',enterStateFunction=EmptyStateInit,transitionRequirement=lambda:PartialRequirement(ds=ds),
                    transitionFunction=lambda:addToList(ds),nextState=partial)



    SM = StateMachine(empty)