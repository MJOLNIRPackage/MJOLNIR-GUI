# -*- coding: utf-8 -*-
"""
Spyder Editor

Script to copy all dependencies into the MJOLNIRGui folder to prepare for pip
installation
"""

import os

local = os.path.dirname(__file__)

targetDir = os.path.join(local,'MJOLNIRGui')

if False:
    
    settingsDir = os.path.join('src','build','settings','*')
    settingsDirName = 'settings'
    
    iconsDir = os.path.join('src','main','icons','*')
    iconsDirName = 'icons'
    
    fileDir = os.path.join('src','main','python','*')
    fileDirName = ''
    
    resourceDir = os.path.join('src','main','resources','*')
    resourceDirName = 'resources'
    # Resulting structure 
    # copy:
    #   settingsDir -> targetDir+settingsDirName
    #   iconsDir -> targetDir+iconsDirName
    #   fileDir -> targetDir+fileDirName
    #   settingsDir -> targetDir+settingsDirName


if not os.path.exists(targetDir):
    os.system("mkdir {}".format(targetDir))

# for path,name in zip([settingsDir,iconsDir,fileDir,resourceDir],[settingsDirName,iconsDirName,fileDirName,resourceDirName]):
#     target = os.path.join(local,targetDir,name)
#     if not os.path.exists(target):
#         os.system("mkdir {}".format(target))
#     os.system("cp -rf {} {}".format(path,target))

os.system("cp -rf {} {}".format(os.path.join(local,'src'),targetDir))
os.system("cp -f {} {}".format(os.path.join(local,'src','main','python','main.py'),os.path.join(targetDir,'main.py')))



os.system('rm '+os.path.join(targetDir,'src','build','settings','secret.json'))
os.system('rm -rf '+os.path.join(targetDir,'src','installer'))
os.system('rm -rf '+os.path.join(targetDir,'src','sign'))