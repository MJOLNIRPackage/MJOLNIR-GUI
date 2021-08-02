from PyQt5 import QtWidgets, QtGui, QtCore
#from qtmodern.windows import ModernDialog


class HelpDialog(QtWidgets.QDialog):

    def __init__(self, helpFile, icon=None,*args, **kwargs):
        super(HelpDialog, self).__init__(*args, **kwargs)
        if not icon is None:
            self.setWindowIcon(icon)
        self.setWindowTitle("Help")
        #self.resize(400, 250)

        with open(helpFile) as f:
            text = "<br>".join([line.replace('\n','') for line in f.readlines()[1:]])

        self.help_label = QtWidgets.QLabel(text=text)
        self.help_label.setWordWrap(True)
        self.help_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse|QtCore.Qt.TextSelectableByKeyboard|
                                                QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        
        self.help_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.help_label.setOpenExternalLinks(True)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.help_label)
        self.setLayout(self.layout)
        self.setMinimumSize(self.sizeHint())
        self.resize(self.sizeHint())