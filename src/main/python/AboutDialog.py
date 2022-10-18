from PyQt5 import QtWidgets, QtGui, QtCore
#from qtmodern.windows import ModernDialog
import MJOLNIR
import sys
import matplotlib

class AboutDialog(QtWidgets.QDialog):

    def __init__(self, aboutFile, version, icon=None, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        if not icon is None:
            self.setWindowIcon(icon)
        self.setWindowTitle("About")
        # Remove the "?" in title
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        with open(aboutFile) as f:
            text = "<br>".join([line.replace('\n','') for line in f.readlines()])

        
        text = text.replace('{MJOLNIRGui}',version)
        text = text.replace('{MJOLNIR}',MJOLNIR.__version__)
        text = text.replace('{MATPLOTLIBVersion}',matplotlib.__version__)


        pythonVersion = '.'.join([str(x) for x in sys.version_info[:3]])
        text = text.replace('{PythonVersion}',pythonVersion)
        
        self.about_label = QtWidgets.QLabel(self)
        self.about_label.setText(text)
        self.about_label.setWordWrap(True)
        self.about_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse|QtCore.Qt.TextSelectableByKeyboard|
                                                 QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        
        self.about_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.about_label.setOpenExternalLinks(True)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.about_label)
        self.setLayout(self.layout)
        self.setMinimumSize(self.sizeHint())
        self.resize(self.sizeHint())