

import IPython
shell = IPython.get_ipython()
shell.enable_matplotlib(gui='qt')

from MJOLNIR.Data import DataSet
from MJOLNIR import _tools # Usefull tools useful across MJOLNIR
import numpy as np
import matplotlib.pyplot as plt

plt.ion()


from PyQt5 import QtWidgets

from MJOLNIRGui_ui2 import Ui_MainWindow  

import sys

class mywindow(QtWidgets.QMainWindow):

    def __init__(self):

        super(mywindow, self).__init__()

        self.ui = Ui_MainWindow()
    
        self.ui.setupUi(self)
        
        
        self.ui.pushButton_12.clicked.connect(self.testTitle)
        
        self.ui.View3D_plot_button.clicked.connect(self.View3D_plot_button_function)
        
        
    def testTitle(self):
        
        print("It's working!")
    def View3D_plot_button_function(self):
        
        

        numbers = '493-500' # String of data numbers


        fileList = _tools.fileListGenerator(numbers,'C:/Users/jacobsen_h/Dropbox/MJOLINRfun/rawdata/',2018) # Create file list from 2018 in specified folder
        ds = DataSet.DataSet(fileList)
        ds.convertDataFile(binning=8,saveFile=False)
        V = ds.View3D(0.02,0.02,0.1)
        V.caxis = (0,1e-6)
        

app = QtWidgets.QApplication([])

application = mywindow()

application.show()

sys.exit(app.exec())