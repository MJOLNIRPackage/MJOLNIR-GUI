# -*- coding: utf-8 -*-
"""
Spyder Editor

Script to copy all dependencies into the MJOLNIRGui folder to prepare for pip
installation
"""

import os, shutil
def copytree(src, dst, symlinks=False, ignore=None, remove=None):
    if remove is None:
        remove = []
    for item in os.listdir(src):
        if os.path.split(item)[-1] in remove:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
            print('Copying folder {} to {}'.format(s,d))
        else:
            shutil.copy2(s, d)
            print('Copying file {} to {}'.format(s,d))


delCommand = 'del'

local = os.path.dirname(__file__)

targetDir = os.path.join(local,'MJOLNIRGui','src')


if not os.path.exists(targetDir):
    os.system("mkdir {}".format(targetDir))

# If the build folder exists also delete the main folder
if os.path.exists(targetDir):
    shutil.rmtree(targetDir)

# Do not include the installer or sign folders
removeList = ['installer','sign']

copytree(os.path.join(local,'src'),targetDir,remove=removeList)

# Remove secret json file (Currently not present)
secretFile = os.path.join(targetDir,'build','settings','secret.json')
if os.path.exists(secretFile):
    os.remove(os.path.join(targetDir,'build','settings','secret.json'))

