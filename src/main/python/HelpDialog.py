from PyQt5 import QtWidgets, QtGui, QtCore
#from qtmodern.windows import ModernDialog


class HelpDialog(QtWidgets.QDialog):

    def __init__(self, helpFile, *args, **kwargs):
        super(HelpDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("Help")
        #self.resize(400, 250)

        with open(helpFile) as f:
            text = '\n'.join([line.replace('\n','') for line in f.readlines()])

        self.help_label = QtWidgets.QLabel(text=text)
        self.help_label.setWordWrap(True)
        self.help_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse|QtCore.Qt.TextSelectableByKeyboard)
        
        self.help_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.help_label)
        self.setLayout(self.layout)
        self.setMinimumSize(self.sizeHint())
        self.resize(self.sizeHint())