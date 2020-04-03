

try:
    import IPython
    shell = IPython.get_ipython()
    shell.enable_matplotlib(gui='qt')
except:
    pass

from MJOLNIR.Data import DataSet,DataFile
from MJOLNIR import _tools # Usefull tools useful across MJOLNIR
import numpy as np
import matplotlib.pyplot as plt

plt.ion()


from PyQt5 import QtWidgets

from MJOLNIR_GUI_ui import Ui_MainWindow  

import sys




# Naming convention: WhereInGui_description_type
# Append _function if it is a function
# E.g.: View3D_plot_button and View3D_plot_button_function

#Headlines so far are:
#DataSet, View3D, QELine, QPlane, Cut1D,

class GuiDataSet(DataSet.DataSet):
    def __init__(self,dataFiles=None, **kwargs):
        print('Got datafiles:\n',dataFiles)
        super(GuiDataSet,self).__init__(dataFiles=dataFiles,**kwargs)


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
        
        fileList,_ = QtWidgets.QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","hdf Files (*.hdf);;All Files (*)")
        
        ds = GuiDataSet(fileList)
        ds.convertDataFile(binning=8,saveFile=False)
        V = ds.View3D(0.02,0.02,0.1)
        V.caxis = (0,1e-6)
        

app = QtWidgets.QApplication([])

application = mywindow()

application.show()

sys.exit(app.exec())
