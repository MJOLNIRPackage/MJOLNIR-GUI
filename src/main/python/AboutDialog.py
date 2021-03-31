from PyQt5 import QtWidgets, QtGui, QtCore
#from qtmodern.windows import ModernDialog
import MJOLNIR
import sys

class AboutDialog(QtWidgets.QDialog):

    def __init__(self, aboutFile, version, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("About")

        with open(aboutFile) as f:
            text = '\n'.join([line.replace('\n','') for line in f.readlines()])
        text = text.replace('{MJOLNIRGui}',version)
        text = text.replace('{MJOLNIR}',MJOLNIR.__version__)

        pythonVersion = '.'.join([str(x) for x in sys.version_info[:3]])
        text = text.replace('{PythonVersion}',pythonVersion)
        
        self.about_label = QtWidgets.QLabel(text=text)
        self.about_label.setWordWrap(True)
        self.about_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse|QtCore.Qt.TextSelectableByKeyboard)
        
        self.about_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.about_label)
        self.setLayout(self.layout)
        self.setMinimumSize(self.sizeHint())
        self.resize(self.sizeHint())