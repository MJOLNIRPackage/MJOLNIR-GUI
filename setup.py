from setuptools import setup
import os
import sys
import json


_here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
 

settings = {'app_name': 'MJOLNIRGui', 
'author': 'MJOLNIRPackage', 
'main_module': 'src/main/python/main.py', 
'version': '1.0.7',
'gpg_name': 'MJOLNIRPackage', 
'hidden_imports': ['cmath'], 
'categories': 'Education;', 
'description': 'Graphical user interface for the MJOLNIR software. Documentation and further information can be found at https://www.psi.ch/en/sinq/camea/data-treatment. Please do cite this package with the DOI and article found at the website.', 
'author_email': 'MJOLNIRPackage@gmail.dk', 
'url': 'https://github.com/MJOLNIRPackage/MJOLNIR-GUI', 
'mac_bundle_identifier': 'ch.psi.MJOLNIRGui'}


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
    install_requires=['pip>=20','PyQt5','MJOLNIR>=1.3.0','ufit>=1.4.0'], 
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        ],
    )
