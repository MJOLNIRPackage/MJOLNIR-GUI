from PyQt5 import QtWidgets, QtGui, QtCore
#from qtmodern.windows import ModernDialog
import os

class HelpDialog(QtWidgets.QDialog):

    def __init__(self, helpFile, guiWindow=None,*args, **kwargs):
        super(HelpDialog, self).__init__(*args, **kwargs)
        self.guiWindow = guiWindow
        if not guiWindow is None:
            self.setWindowIcon(QtGui.QIcon(self.guiWindow.AppContext.get_resource('Icons/Own/question-button.png')))
        self.setWindowTitle("Help")
        # Remove the "?" in title
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        
        

        with open(helpFile) as f:
            text = "<br>".join([line.replace('\n','') for line in f.readlines()[1:]])
            startImg = 0
            startStr = '<img src=' # look for this string

            while True:
                startImg = text.find(startStr,startImg+1)
                if startImg == -1:
                    break
                endImg = text.find('>',startImg)
                pathStart = startImg+len(startStr)
                pathNotation = text[startImg+len(startStr)] # either ' or "
                pathEnd = text.find(pathNotation,pathStart+1)
                path = text[pathStart+1:pathEnd]
                path = os.path.join(*path.split('\\'))
                text = text[:pathStart+1] + self.guiWindow.AppContext.get_resource(path) + text[pathEnd:]
            

        self.help_label = QtWidgets.QLabel(text=text)
        self.help_label.setWordWrap(True)
        self.help_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse|QtCore.Qt.TextSelectableByKeyboard|
                                                QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        
        self.help_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.help_label.setOpenExternalLinks(True)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.scroll_layout = QtWidgets.QScrollArea()
        self.scroll_layout.setLineWidth(0)
        self.scroll_layout.setFrameShape(0)
        self.layout.addWidget(self.scroll_layout)
        
        self.scroll_layout.setWidget(self.help_label)
        self.setLayout(self.layout)
        self.setMinimumSize(self.sizeHint())
        # find size of window needed
        width = max(self.help_label.size().width()+50,self.sizeHint().width())
        height = min(self.help_label.size().height(),800)
        
        self.resize(width,height)