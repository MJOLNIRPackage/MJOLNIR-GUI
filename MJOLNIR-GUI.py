

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
        
        
        
        self.ui.DataSet_convertData_button.clicked.connect(self.DataSet_convertData_button_function)
        
        
        
        self.ui.View3D_plot_button.clicked.connect(self.View3D_plot_button_function)
        self.ui.View3D_setCAxis_button.clicked.connect(self.View3D_plot_button_function)
        
        # self.ui.DataSet_binning_comboBox.
        
        
    def DataSet_convertData_button_function(self):
        #The loading should be moved to a different button        
        fileList,_ = QtWidgets.QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","hdf Files (*.hdf);;All Files (*)")
        self.fileList=fileList


        binning=int(self.ui.DataSet_binning_comboBox.currentText())
        ds = GuiDataSet(self.fileList)
        ds.convertDataFile(binning=binning,saveFile=False)
        self.ds=ds
        
    def View3D_plot_button_function(self):

        # Check if we already have data, otherwise convert current data.
        if not hasattr(self, 'fileList'):
            self.DataSet_convertData_button_function()
        
        QXBin=float(self.ui.View3D_QXBin_lineEdit.text())
        QYBin=float(self.ui.View3D_QYBin_lineEdit.text())
        EBin =float(self.ui.View3D_EBin_lineEdit.text())
        self.V = self.ds.View3D(QXBin,QYBin,EBin)
        
        self.View3D_setCAxis_button_function()
        
    def View3D_setCAxis_button_function(self):
        #For some reason this creates a new window when it is clicked. It shouldn't.
        if not hasattr(self, 'V'):
            self.View3D_plot_button_function()
            
        CAxisMin=float(self.ui.View3D_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.View3D_CAxisMax_lineEdit.text())
        self.V.set_clim(CAxisMin,CAxisMax)
        



app = QtWidgets.QApplication([])

application = mywindow()

application.show()

sys.exit(app.exec())
