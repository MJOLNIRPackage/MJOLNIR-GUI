#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:31:10 2019

@author: lass
"""

import sys,os,json

# update to new version in base.json
settingsFile = os.path.join('src','build','settings','base.json')



with open(settingsFile) as jsonFile:
    settings = json.load(jsonFile)

if len(sys.argv)>1:
    version = sys.argv[1]
else:
    currentVersion = settings['version'].split('.')
    updatedVersion = [x if i<len(currentVersion)-1 else str(int(x)+1) for i,x in enumerate(currentVersion)]
    version = '.'.join(updatedVersion)

print('Updating version from {} to {}'.format(settings['version'],version))


settings['version'] = version

with open(settingsFile,'w') as jsonFile:
    json.dump(settings,jsonFile,indent=4)
    

