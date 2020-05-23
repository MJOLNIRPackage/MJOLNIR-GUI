import sys
import os
class AppContextEmulator(object):
    def __init__(self,projectDirectory):
        self.projectDirectory = projectDirectory
        local_os = sys.platform

        if local_os.lower() == 'linux':
            local_os = 'linux'
        elif local_os.lower() == 'win32' or local_os.lower() == 'cygwin':
            local_os = 'windows'
        elif local_os.lower() == 'darwin':
            local_os = 'max'
        else:
            local_os = 'linux'

        self.os = local_os
        self.resourses = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','resources'))


    def get_resource(self,path):
        tryPath = os.path.join(self.resourses,'base',path)
        specificPath = os.path.join(self.resourses,self.os,path)
        
        if os.path.exists(specificPath):
            return specificPath
        else:
            return tryPath
            