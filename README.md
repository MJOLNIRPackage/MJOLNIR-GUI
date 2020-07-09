# MJOLNIR-GUI
This is a graphical interface for the MJOLNIR: https://github.com/MJOLNIRPackage/MJOLNIR/, which deals with multiplexing inelastic neutron spectrometers. MJOLNIRGui is meant to introduce the scripting software in a user-friendly way and to give access to data-overview methods either during an experiment or when inspecting data files. Further information can be found at https://www.psi.ch/en/sinq/camea/data-treatment.

## Citing this package
If you use this software for data treatment, please do cite it using its doi and the article found at https://www.psi.ch/en/sinq/camea/data-treatment.


## Installation from Terminal (Linux/MacOS)
In order to install this graphical interface to MJOLNIR, the following packages are needed:
- Python >=3.5
- pip >= 20.1.1
- fbs >= 0.8.6
- MJOLNIR >=1.1.7
- PyQt5 >= 5.15.0
- PyQt5-sip >= 12.8.0
- uFit


Notice, that in order to make installers using fbs, either python 3.5 or 3.6 has to be installed.

### Installation
Currently, the most robust way to install MJOLNIRGui is through the terminal with the following commands (assuming conda is installed)

```shell
conda create --name MJOLNIRGui python=3.6
conda activate MJOLNIRGui
pip install --upgrade pip
pip install MJOLNIR PyQt5 PyQt5-sip fbs ufit qtpy
```

Then change directory to a dedicated folder in which the MJOLNIRGui repository will be cloned
```shell
cd path
git clone https://github.com/MJOLNIRPackage/MJOLNIR-GUI.git
cd MJOLNIR-Gui
```

### Running the Gui
In order to run the gui, it has to be activated through the fbs package

```shell
conda activate MJOLNIRGui
fbs run
```


## Installation from executable (Windows/Linux)
Executables are available for Windows and Linux and they can be found at https://www.psi.ch/en/sinq/camea/data-treatment