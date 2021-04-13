# MJOLNIR-GUI
This is a graphical interface for the MJOLNIR: https://github.com/MJOLNIRPackage/MJOLNIR/, which deals with multiplexing inelastic neutron spectrometers. MJOLNIRGui is meant to introduce the scripting software in a user-friendly way and to give access to data-overview methods either during an experiment or when inspecting data files. Further information can be found at https://www.psi.ch/en/sinq/camea/data-treatment.

## Citing this package
If you use this software for data treatment, please do cite it using its doi and the article found at https://www.psi.ch/en/sinq/camea/data-treatment.


# Install

There are in total four ways of installing this interface to MJOLNIR

## Using installers

Installers for the app is currently supported on Windows and Ubuntu. For both, installation files are available at https://www.psi.ch/en/sinq/camea/data-treatment. To install, double click the .exe file in windows, or run the .deb file through the system package manager on Ubuntu.


## Anaconda and Pip

The app can be install in an Anaconda environment on all platforms. In order to do this, first the anaconda environment is to be set up

```bash
    conda create --name MJOLNIRGui python=3.6 geos numpy scipy shapely
```

For windows, it is important that the geos and shapely modules are installed through conda instead of pip. Next, the app is installed by

```bash
    conda activate MJOLNIRGui
    pip install MJOLNIRGui
```

This installs the needed packages and creates a command line script to run the app. To run, be sure to be in the right environment and call

```bash
    MJOLNIRGui
```

## Through git

As an alternative to the two above methods, it is possible to clone the git repository og MJOLNIRGui and run it locally. This is done by creating a folder in which to clone and invoke the clone command

```bash
    git clone https://github.com/MJOLNIRPackage/MJOLNIR-GUI.git
    cd MJOLNIR-GUI
```

As was the case for the anaconda and pip method, on Windows the geos and shapely modules need to be installed through anaconda. Further needed packages are fbs PyQt5 PyInstaller==3.4 setuptools<45.0.0, MJOLNIR. With all of these installed navigate to the root directory of the git repository (containing setup.py, src, ...) and call

```bash
    fbs run
```

## Ubunto through the apt-get

You can also add the MJOLNIRGui to be automatically update through the software updater. This is done by

```bash
    sudo apt-get install apt-transport-https
    wget -qO - https://fbs.sh/MJOLNIRPackage/MJOLNIRGui/public-key.gpg | sudo apt-key add -
    echo 'deb [arch=amd64] https://fbs.sh/MJOLNIRPackage/MJOLNIRGui/deb stable main' | sudo tee /etc/apt/sources.list.d/mjolnirgui.list
    sudo apt-get update
    sudo apt-get install mjolnirgui
```

If you already have installed the app, a forced  update can be triggered via:

```bash
    sudo apt-get update -o Dir::Etc::sourcelist="/etc/apt/sources.list.d/mjolnirgui.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"
    sudo apt-get install --only-upgrade mjolnirgui
```

Lastly, your can also install without automatic updates by downloading:

https://fbs.sh/MJOLNIRPackage/MJOLNIRGui/MJOLNIRGui.deb

