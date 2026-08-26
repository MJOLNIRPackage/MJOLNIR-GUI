#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 11:54:33 2021

@author: Jakob Lass

Tool to replace makefile in order to fully port development to windows
"""

import argparse
from ntpath import join

import os,glob, shutil

from MJOLNIR.Data.DataSet import OxfordList

possibleArguments = ['wheel', 'upload', 'version','cleanpip','clean','installer']

parser = argparse.ArgumentParser(description="Make tool replacing linux Makefile.")
parser.add_argument("task", nargs='?', default='help', type=str, help="Type of task to be performed. Possible tasks are: {}. Run without argument to see help menu.".format(OxfordList(possibleArguments)))
parser.add_argument("version", nargs='?',default=None, type=str, help="Version number to be created. Default is previous plus 1, i.e. x.y.z -> x.y.z+1")

def callHelp(parser=parser):
    parser.print_help()



def makeWheel():
    os.system("python preparePIP.py")
    os.system("python setup.py sdist")
    os.system("python setup.py bdist_wheel")

def getLatestBuild():
    list_of_files = glob.glob(os.path.join('dist','*')) # * means all if need specific format then *.csv
    return max(list_of_files, key=os.path.getctime)

def getCurrentVersion():
    string  = getLatestBuild()
    versionList = string.split('-')[1].split('.')[:-2]
    if 'post' in versionList[-1]:
        versionList[-1] = versionList[-1].replace('post','')
        adder = 'post'
    else:
        adder = ''
    version = [int(x) for x in versionList]
    
    if adder != '':
        version[-1]=adder+str(version[-1]+1)
    else:
        version[-1]+=1
    return '.'.join([str(x) for x in version])

def uploadPyPi(server='pypiMJOLNIRPackage'):
    build = getLatestBuild()
    print('Uploading ' + str(build) + ' to '+server)
    os.system('twine upload {} -r {}'.format(build,server))


def upload():
    uploadPyPi()

def update(version):
    os.system('python Update.py '+version)

def cleanPIP():
    try:
        shutil.rmtree(r'C:\Users\lass_j\Documents\Software\MJOLNIR-GUI\MJOLNIRGui\src')
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

args = parser.parse_args()


if args.task == '' or args.task.lower() == 'help':
    callHelp()

elif args.task.lower() == 'wheel':
    makeWheel()

elif args.task.lower() == 'upload':
    upload()

elif args.task.lower() == 'version':
    if args.version is None:
        version = getCurrentVersion()
    else:
        version = args.version
    print('Creating version '+version)
    update(version=version)
    
    addFiles = ['setup.py',
                os.path.join('src','build','settings','base.json'),
                os.path.join('src','main','python','MJOLNIR_GUI.py')
                ]
    os.system("git add {}".format(' '.join(addFiles)))
    os.system('git commit -m "Update version"')
    os.system('git tag -a {0} -m "{0}"'.format(version))
    makeWheel()
    os.system("git push")
    os.system("git push --tags")
    


elif args.task.lower() == 'clean':
    os.system('fbs clean')
    cleanPIP()

elif args.task.lower() == 'cleanpip':
    cleanPIP()

elif args.task.lower() == 'installer':
    os.system('fbs freeze --debug')
    os.system('fbs installer')

else:
    print('Provided argument not understood. Received',args.task,'\n\n')
    callHelp()