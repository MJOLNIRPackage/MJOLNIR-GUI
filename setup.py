from setuptools import setup
import os
import sys
import json


_here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


settingsDir = os.path.join(os.path.dirname(__file__),'MJOLNIRGui','src','build','settings')
settingsFiles = os.listdir(settingsDir)

settings = {}

for f in settingsFiles:
    file = os.path.join(settingsDir,f)
    with open(file) as json_file:
        _settings = json.load(json_file)
        for item,val in _settings.items():
            settings[item] = val



home = os.path.join(_here,'MJOLNIRGui')
packages = [x[0] for x in os.walk(home) if x[0][-1]!='_']

packages = [os.path.relpath(p,_here) for p in packages]


setup(
    name=settings['app_name'],
    version=settings['version'],
    description=('Neutron Scattering software suite.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=settings['author'],
    author_email=settings['author_email'],
    url=settings['url'],
    license='MPL-2.0',
    packages=packages,
    package_data={'': ['*']},
    include_package_data=True,
    entry_points = {
        "console_scripts": ['MJOLNIRGui = MJOLNIRGui.src.main.python.MJOLNIR_GUI:main']
        },
    python_requires='>=3.5',
    install_requires=['pip>=20','sip>=5.3','PyQt5-sip','PyQt5','MJOLNIR>=1.1.18','ufit>=1.4.0'], 
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        ],
    )
