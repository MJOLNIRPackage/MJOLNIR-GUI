# MJOLNIR-GUI
This is (going to be) a graphical interface for MJOLNIR: https://github.com/Jakob-Lass/MJOLNIR/


# Install

The app is currently supported on Windows and Ubuntu. For both, installation files are available at https://www.psi.ch/en/sinq/camea/data-treatment.


## Install - apt-get
For Ubuntu users, the package can be install as a stand-alone by

```bash
sudo apt-get install apt-transport-https
    wget -qO - https://fbs.sh/MJOLNIRPackage/MJOLNIRGui/public-key.gpg | sudo apt-key add -
    echo 'deb [arch=amd64] https://fbs.sh/MJOLNIRPackage/MJOLNIRGui/deb stable main' | sudo tee /etc/apt/sources.list.d/mjolnirgui.list
    sudo apt-get update
    sudo apt-get install mjolnirgui
```
If the app has already been installed, then force an immediate update via:
```bash
    sudo apt-get update -o Dir::Etc::sourcelist="/etc/apt/sources.list.d/mjolnirgui.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"
    sudo apt-get install --only-upgrade mjolnirgui
```