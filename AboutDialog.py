from PyQt5 import QtWidgets, QtGui, QtCore



class AboutDialog(QtWidgets.QDialog):

    def __init__(self, aboutFile, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("About")
        #self.resize(400, 250)

        with open(aboutFile) as f:
            text = '\n'.join([line.replace('\n','') for line in f.readlines()])

        self.about_label = QtWidgets.QLabel(text=text)
        self.about_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse|QtCore.Qt.TextSelectableByKeyboard)
        
        self.about_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.about_label)
        self.setLayout(self.layout)
        self.setMinimumSize(self.sizeHint())