from setuptools import setup
import os
import sys
import json

_here = os.path.abspath(os.path.dirname(__file__))

settingsFile = os.path.join(_here,'src','build','settings','base.json')

with open(settingsFile) as jsonFile:
    settings = json.load(jsonFile)



if sys.version_info[0] < 3:
    with open(os.path.join(_here, 'README.md')) as f:
        long_description = f.read()
else:
    with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
pythonPath = os.path.join('lib','python{}.{}'.format(*sys.version_info[:2]),'site-packages','MJOLNIR')

setup(
    name=settings['app_name'],
    version=settings['version'],
    description=('Neutron Scattering software suite.'),
    long_description=long_description,
    author=settings['author'],
    author_email='lass.jakob@gmail.com',
    url='https://github.com/jakob-lass/MJOLNIR-Gui',
    license='MPL-2.0',
    #data_files = [('src/main/python/',['src/main/python/main.py'])],#os.path.join(pythonPath, 'src','main','resources','base','*')],#,((os.path.join(pythonPath),['MJOLNIR/CalibrationFlatCone.csv'])),((os.path.join(pythonPath),['MJOLNIR/CalibrationMultiFLEXX.csv']))],#,(pythonPath+'/CommandLineScripts/',['MJOLNIR/CommandLineScripts/.settings'])],
    packages=['MJOLNIRGui'],
    package_dir={'MJOLNIRGui': '.'},
    package_data={'MJOLNIRGui': ['MJOLNIRGui/src/main/python/main.py','MJOLNIRGui/src/main/resources/base/*.png','MJOLNIRGui/src/main/resources/base/*.txt','MJOLNIRGui/*.py',
    'MJOLNIRGui/src/build/settings/base.json','MJOLNIRGui/src/main/icons/*.ico','MJOLNIRGui/src/main/icons/base/*','MJOLNIRGui/src/main/resources/base/Icons/icons/*','MJOLNIRGui/src/main/resources/base/Icons/Own/*']},
    #scripts=['MJOLNIR/CommandLineScripts/MJOLNIRCalibrationInspector','MJOLNIR/CommandLineScripts/MJOLNIRHistory','MJOLNIR/CommandLineScripts/MJOLNIRConvert',
    #'MJOLNIR/CommandLineScripts/MJOLNIR3DView'],
    entry_points = {
        "console_scripts": ['MJOLNIRGui = MJOLNIRGui.MJOLNIRGui.main:main']
        },
    python_requires='>=3.4,<=3.7',
    install_requires=['fbs','MJOLNIR>=1.1.7','PyQt5'],
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Information Analysis',
#        'Programming Language :: Python :: 2.7',
#        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6']
#        'Programming Language :: Python :: 3.7'],
    )