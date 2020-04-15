import pickle as pickle
import os

from os.path import expanduser
settingsFile = expanduser("~") # Use home folder for storing settings file

settingsFile = os.path.join(settingsFile,'.MJOLNIRGuisettings')

def loadSetting(string): # pragma: no cover
    if Exists():
        with open(settingsFile,"rb") as pickle_in:
            loaded_dict = pickle.load(pickle_in)
        if string in loaded_dict:
            returnValue = loaded_dict[string]
        else:
            returnValue = None
        return returnValue
    else:
        return None

def updateSetting(name,value):# pragma: no cover
    if Exists():
        with open(settingsFile,"rb") as pickle_in:
            loaded_dict = pickle.load(pickle_in)
    else:
        loaded_dict = {}
    loaded_dict[name]=value
    with open(settingsFile,"wb") as pickle_out:
        pickle.dump(loaded_dict, pickle_out)

def Exists(file = settingsFile):# pragma: no cover
    return os.path.isfile(settingsFile)