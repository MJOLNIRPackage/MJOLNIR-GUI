#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:31:10 2019

@author: lass
"""

import sys,os,json

# update to new version in base.json
settingsDir = os.path.join('src','build','settings')
installFile = 'setup.py'
guiFile = os.path.join('src','main','python','MJOLNIR_Gui.py')

settingsFiles = os.listdir(settingsDir)

settings = {}

for f in settingsFiles:
    file = os.path.join(settingsDir,f)
    with open(file) as json_file:
        _settings = json.load(json_file)
        for item,val in _settings.items():
            settings[item] = val

if len(sys.argv)>1:
    version = sys.argv[1]
else:
    currentVersion = settings['version'].split('.')
    updatedVersion = [x if i<len(currentVersion)-1 else str(int(x)+1) for i,x in enumerate(currentVersion)]
    version = '.'.join(updatedVersion)

print('Updating version from {} to {}'.format(settings['version'],version))


settings['version'] = version

with open(os.path.join('src','build','settings','base.json'),'w') as jsonFile:
    json.dump(settings,jsonFile,indent=4)
    
with open(installFile) as f:
    text = f.readlines()
    startLine = -1
    for i,line in enumerate(text):
        if 'settings = ' in line:
            startLine = i
        if startLine > 0 and  "'}" in line:
            endLine = i+1

del settings['gpg_key']
settingsStr = ['settings = '+str(settings).replace(', ',', \n')+'\n']

finalText = text[:startLine]+settingsStr+text[endLine:]

with open(guiFile) as f:
    text = f.readlines()
    startLine = -1
    for i,line in enumerate(text):
        if 'version = ' in line:
            versionLine = i
            break
        

text[versionLine] = "version = '{}'\n".format(version) 

with open(guiFile,'w') as f:
    f.writelines(text)
