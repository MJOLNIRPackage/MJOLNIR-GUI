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


setup(
    name=settings['app_name'],
    version=settings['version'],
    description=('Neutron Scattering software suite.'),
    long_description=long_description,
    author=settings['author'],
    author_email='lass.jakob@gmail.com',
    url='https://github.com/jakob-lass/MJOLNIR-Gui',
    license='MPL-2.0',
    packages=['MJOLNIRGui','MJOLNIRGui/Views'],
    package_dir={'MJOLNIRGui': 'src/main/python/','MJOLNIRGui/Views': 'src/main/python/Views/'},
    package_data={'MJOLNIRGui': ['main.py','../resources/base/*.png','../resources/base/*.txt','*.py',
    '../icons/*.ico','../icons/base/*','../resources/base/Icons/icons/*','../resources/base/Icons/Own/*','../resources/base/Views/*']},
    entry_points = {
        "console_scripts": ['MJOLNIRGui = MJOLNIRGui.MJOLNIR_GUI:main']
        },
    python_requires='>=3.4,<=3.7',
    install_requires=['MJOLNIR>=1.1.7','PyQt5'],
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6']
    )
