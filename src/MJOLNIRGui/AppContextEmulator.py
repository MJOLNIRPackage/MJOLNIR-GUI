import sys,os,json
class AppContextEmulator(object):
    def __init__(self,projectDirectory):
        self.projectDirectory = projectDirectory
        local_os = sys.platform

        if local_os.lower() == 'linux':
            local_os = 'linux'
        elif local_os.lower() == 'win32' or local_os.lower() == 'cygwin':
            local_os = 'windows'
        elif local_os.lower() == 'darwin':
            local_os = 'mac'
        else:
            local_os = 'linux'

        self.os = local_os
        self.resourses = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','resources'))

        self.build_settings = {}
        self.get_build_settings()


    def get_resource(self,path):
        tryPath = os.path.join(self.resourses,'base',path)
        specificPath = os.path.join(self.resourses,self.os,path)
        
        if os.path.exists(specificPath):
            return specificPath
        else:
            return tryPath
            
    def get_build_settings(self):
        self.settingsFolder = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','build','settings'))

        if not hasattr(self,'build_settings'):
            self.build_settings = {}

        baseFile = os.path.join(self.settingsFolder,'base.json')

        with open(baseFile) as f:
            newSettings = json.load(f)
        self.build_settings = {**self.build_settings,**newSettings}

        
        specificFile = os.path.join(self.settingsFolder,self.os+'.json')
        if os.path.exists(specificFile):
            with open(specificFile) as f:
                newSettings = json.load(f)
                self.build_settings = {**self.build_settings,**newSettings}

