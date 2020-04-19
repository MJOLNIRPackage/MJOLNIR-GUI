#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:31:10 2019

@author: lass
"""

import sys,os,json

version = sys.argv[1]

# update to new version in base.json
settingsFile = os.path.join('src','build','settings','base.json')

with open(settingsFile) as jsonFile:
    settings = json.load(jsonFile)

settings['version'] = version



