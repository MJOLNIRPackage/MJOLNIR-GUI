# MJOLNIR-GUI

**MJOLNIR-GUI** is a graphical user interface for [MJOLNIR](https://github.com/MJOLNIRPackage/MJOLNIR), a Python package for data treatment and analysis of multiplexing inelastic neutron spectrometers.

The GUI is designed to make the functionality of MJOLNIR accessible in a user-friendly environment, both for users who are new to scripting and for experienced users who want a convenient way to inspect and process data.

MJOLNIR-GUI provides tools for:

* Converting and inspecting experimental data
* Quickly obtaining an overview of measured datasets
* Visualising data during an experiment
* Inspecting and analysing previously collected data
* Accessing selected MJOLNIR data-treatment functionality without writing Python scripts

Further information about MJOLNIR and data treatment for multiplexing neutron spectrometers can be found on the [CAMEA data-treatment page](https://www.psi.ch/en/sinq/camea/data-treatment).

## Installation

The recommended way to install MJOLNIR-GUI is using `pip` in a dedicated Python environment. This can be created using tools such as [Miniforge](https://github.com/conda-forge/miniforge), `venv`, or another preferred environment manager.

Installing MJOLNIR-GUI automatically installs the required [MJOLNIR](https://github.com/MJOLNIRPackage/MJOLNIR) package.

MJOLNIR-GUI supports both **Qt5** and **Qt6**. Because the Python Qt bindings are mutually exclusive, the desired Qt version must be selected when installing the package.

### Qt5

```bash
pip install "MJOLNIRGui[qt5]"
```

### Qt6

```bash
pip install "MJOLNIRGui[qt6]"
```

After a successful installation, start the GUI from the command line with:

```bash
MJOLNIRGui
```

## Requirements

MJOLNIR-GUI requires:

* Python **3.9 or newer**
* Either **Qt5** or **Qt6**
* MJOLNIR (installed automatically as a dependency)

The required Qt version must be selected during installation using either the `qt5` or `qt6` optional dependency.

## Installation from Git

MJOLNIR-GUI can also be installed directly from the Git repository. This is useful for development, testing new features, or accessing the latest version before it is released through PyPI.

First, clone the repository:

```bash
git clone https://github.com/MJOLNIRPackage/MJOLNIR-GUI.git
cd MJOLNIR-GUI
```

The latest version can then be installed using `pip`. For example, for Qt6:

```bash
pip install ".[qt6]"
```

or, for Qt5:

```bash
pip install ".[qt5]"
```

After installation, start the GUI with:

```bash
MJOLNIRGui
```

## Citing MJOLNIR-GUI

If you use MJOLNIR-GUI for data treatment or analysis in a publication, please cite the MJOLNIR-GUI software and the associated publication.

Citation information, the DOI, and the relevant publication can be found on the [CAMEA data-treatment page](https://www.psi.ch/en/sinq/camea/data-treatment).

## Links

* [MJOLNIR on GitHub](https://github.com/MJOLNIRPackage/MJOLNIR)
* [MJOLNIR-GUI on GitHub](https://github.com/MJOLNIRPackage/MJOLNIR-GUI)
* [CAMEA data treatment](https://www.psi.ch/en/sinq/camea/data-treatment)
