

try:
    import IPython
    shell = IPython.get_ipython()
    shell.enable_matplotlib(gui='qt')
except:
    pass


from MJOLNIR import _tools # Usefull tools useful across MJOLNIR
import numpy as np
import matplotlib.pyplot as plt

from os import path


plt.ion()


from PyQt5 import QtWidgets, QtCore, QtGui

from MJOLNIR_GUI_ui import Ui_MainWindow  
from MJOLNIR_Data import GuiDataFile,GuiDataSet
from DataModels import DataSetModel,DataFileModel
import sys




# Naming convention: WhereInGui_description_type
# Append _function if it is a function
# E.g.: View3D_plot_button and View3D_plot_button_function

#Headlines so far are:
#DataSet, View3D, QELine, QPlane, Cut1D,



class mywindow(QtWidgets.QMainWindow):

    def __init__(self):

        super(mywindow, self).__init__()

        self.ui = Ui_MainWindow()
    
        self.ui.setupUi(self)
        
        self.currentDataSetIndex = 0

        self.dataSets = []
        

        self.setupDataSet() # Setup datasets with buttons and call functions
        self.setupDataFile() # Setup datafiles
        
        
        ##############################################################################
        # View3D
        ##############################################################################       
        self.ui.View3D_plot_button.clicked.connect(self.View3D_plot_button_function)
        self.ui.View3D_setCAxis_button.clicked.connect(self.View3D_setCAxis_button_function)
        self.ui.View3D_SetTitle_button.clicked.connect(self.View3D_SetTitle_button_function)
        
        # Radiobutton to select viewing type
        self.ui.View3D_SelectView_QxE_radioButton.clicked.connect(self.View3D_SelectView_QxE_radioButton_function)
        self.ui.View3D_SelectView_QyE_radioButton.clicked.connect(self.View3D_SelectView_QyE_radioButton_function)
        self.ui.View3D_SelectView_QxQy_radioButton.clicked.connect(self.View3D_SelectView_QxQy_radioButton_function)

        ##############################################################################
        # QELine
        ##############################################################################
        self.ui.QELine_plot_button.clicked.connect(self.QELine_plot_button_function)
        self.ui.QELine_setCAxis_button.clicked.connect(self.QELine_setCAxis_button_function)
        self.ui.QELine_SetTitle_button.clicked.connect(self.QELine_SetTitle_button_function)

        ##############################################################################
        # QPlane
        ##############################################################################
        self.ui.QPlane_plot_button.clicked.connect(self.QPlane_plot_button_function)
        self.ui.QPlane_setCAxis_button.clicked.connect(self.QPlane_setCAxis_button_function)
        self.ui.QPlane_SetTitle_button.clicked.connect(self.QPlane_SetTitle_button_function)
        
        

    def DataSet_convertData_button_function(self):
        #  Should add a check if a data set is selected
            
        binning=int(self.ui.DataSet_binning_comboBox.currentText())
        ds = self.DataSetModel.getCurrentDataSet()
        ds.convertDataFile(binning=binning,saveFile=False)
        
        
        ##############################################################################
        # View3D
        ##############################################################################
        
    def View3D_setCAxis_button_function(self):
        if not hasattr(self, 'V'):
            self.View3D_plot_button_function()
            
        CAxisMin=float(self.ui.View3D_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.View3D_CAxisMax_lineEdit.text())
              
        self.V.caxis=(CAxisMin,CAxisMax)
    
    def View3D_SelectView_QxE_radioButton_function(self):
        if hasattr(self, 'V'):
            self.V.setAxis(1)
            # Redraw the title, then change the viewing plane to render properly
            self.View3D_SetTitle_button_function()
            self.V.setPlane(1)
            self.V.setPlane(0)
                
    def View3D_SelectView_QyE_radioButton_function(self):
        if hasattr(self, 'V'):
            self.V.setAxis(0)
            # Redraw the title, then change the viewing plane to render properly
            self.View3D_SetTitle_button_function()
            self.V.setPlane(1)
            self.V.setPlane(0)
        
    def View3D_SelectView_QxQy_radioButton_function(self):
        if hasattr(self, 'V'):
            self.V.setAxis(2)
            # Redraw the title, then change the viewing plane to render properly
            self.View3D_SetTitle_button_function()
            self.V.setPlane(1)
            self.V.setPlane(0)
        
    def View3D_SetTitle_button_function(self):        
        if hasattr(self, 'V'):
            TitleText=self.ui.View3D_SetTitle_lineEdit.text()        
            self.V.ax.set_title(TitleText)
            
            # Get the value of the slider right now, then change it around a bit and put it back to where it was, to render properly
            currentSliderValue=self.V.Energy_slider.val
            self.V.Energy_slider.set_val(0)
            self.V.Energy_slider.set_val(1)
            self.V.Energy_slider.set_val(currentSliderValue)
                    
    def View3D_plot_button_function(self):

        # Check if we already have data, otherwise convert current data.
        ds = self.DataSetModel.getCurrentDataSet()
        if len(ds.convertedFiles)==0:
            self.DataSet_convertData_button_function()
        
        QXBin=float(self.ui.View3D_QXBin_lineEdit.text())
        QYBin=float(self.ui.View3D_QYBin_lineEdit.text())
        EBin =float(self.ui.View3D_EBin_lineEdit.text())
        
        self.V = ds.View3D(QXBin,QYBin,EBin)
        
        # Select the correct view
        if self.ui.View3D_SelectView_QxE_radioButton.isChecked():
            self.View3D_SelectView_QyE_radioButton_function()
        if self.ui.View3D_SelectView_QyE_radioButton.isChecked():
            self.View3D_SelectView_QxE_radioButton_function()
        if self.ui.View3D_SelectView_QxQy_radioButton.isChecked():
            self.View3D_SelectView_QxQy_radioButton_function()
            
        
        self.View3D_setCAxis_button_function()        
        self.View3D_SetTitle_button_function()
        self.V.setPlane(1)
        self.V.setPlane(0)
        
        ##############################################################################
        # QELine
        ##############################################################################
    def QELine_plot_button_function(self):
        print('This button has not been implemented yet')

    def QELine_setCAxis_button_function(self):
        
        CAxisMin=float(self.ui.QELine_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.QELine_CAxisMax_lineEdit.text())
        
        # self.V.set_clim(CAxisMin,CAxisMax)
        
        print('This button has not been implemented yet')

    def QELine_SetTitle_button_function(self):
        TitleText=self.ui.QELine_SetTitle_lineEdit.text()        
        print('This button has not been implemented yet')


        ##############################################################################
        # QPlane
        ##############################################################################        
    def QPlane_plot_button_function(self):
        print('This button has not been implemented yet')

    def QPlane_setCAxis_button_function(self):
        print('This button has not been implemented yet')        
        CAxisMin=float(self.ui.QPlane_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.QPlane_CAxisMax_lineEdit.text())

    def QPlane_SetTitle_button_function(self):
        TitleText=self.ui.QPlane_SetTitle_lineEdit.text()        
        print('This button has not been implemented yet')
        

    def setupDataSet(self): # Set up main features for Gui regarding the dataset widgets
        self.ui.DataSet_convertData_button.clicked.connect(self.DataSet_convertData_button_function)
        self.ui.DataSet_NewDataSet_button.clicked.connect(self.DataSet_NewDataSet_button_function)
        self.ui.DataSet_DeleteDataSet_button.clicked.connect(self.DataSet_DeleteDataSet_button_function)
        self.ui.DataSet_AddFiles_button.clicked.connect(self.DataSet_AddFiles_button_function)

        self.DataSetModel = DataSetModel(dataSets=self.dataSets,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView)
        self.ui.DataSet_DataSets_listView.setModel(self.DataSetModel)

        self.ui.DataSet_DataSets_listView.clicked.connect(self.selectedDataSetChanged)
        self.ui.DataSet_DataSets_listView.doubleClicked.connect(self.DataSet_DoubleClick_Selection_function)

    def setupDataFile(self): # Set up main features for Gui regarding the datafile widgets
        self.DataFileModel = DataFileModel(DataSet_filenames_listView=self.ui.DataSet_filenames_listView,dataSetModel=self.DataSetModel,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView)
        self.ui.DataSet_filenames_listView.setModel(self.DataFileModel)
        self.ui.DataSet_filenames_listView.clicked.connect(self.selectedDataFileChanged)
        self.ui.DataSet_DeleteFiles_button.clicked.connect(self.DataSet_DeleteFiles_button_function)

        self.ui.DataSet_DataSets_listView.doubleClicked.connect(self.DataFile_DoubleClick_Selection_function)


    @property
    def currentDataFileIndex(self):
        return self._currentDataFileIndex

    @currentDataFileIndex.getter
    def currentDataFileIndex(self):
        return self._currentDataFileIndex

    @currentDataFileIndex.setter
    def currentDataFileIndex(self,index):
        self._currentDataFileIndex = index

    @property
    def currentDataSetIndex(self):
        return self._currentDataSetIndex

    @currentDataSetIndex.getter
    def currentDataSetIndex(self):
        return self._currentDataSetIndex

    @currentDataSetIndex.setter
    def currentDataSetIndex(self,index):
        self._currentDataSetIndex = index

    def selectedDataSetChanged(self,*args,**kwargs):
        self.DataFileModel.updateCurrentDataSetIndex()

    def selectedDataFileChanged(self,*args,**kwargs):
        self.DataFileModel.layoutChanged.emit()

    def DataSet_NewDataSet_button_function(self):
        ds = GuiDataSet(name='Added')
        self.DataSetModel.append(ds)
        index = self.DataSetModel.index(self.DataSetModel.rowCount(None)-1,0)
        self.DataSetModel.DataSet_DataSets_listView.setCurrentIndex(index)

    def DataSet_DeleteDataSet_button_function(self):
        self.DataSetModel.delete(self.ui.DataSet_DataSets_listView.selectedIndexes()[0])
        
    def DataSet_DeleteFiles_button_function(self):
        self.DataFileModel.delete()

    def DataSet_DoubleClick_Selection_function(self,index,*args,**kwargs):
        self.ui.DataSet_DataSets_listView.edit(index)

    def DataFile_DoubleClick_Selection_function(self,index,*args,**kwargs):
        self.ui.DataSet_filenames_listView.edit(index)

    def DataSet_AddFiles_button_function(self):
        currentFolder = self.ui.DataSet_path_lineEdit.text()
        if path.exists(currentFolder):
            folder=currentFolder
        else:
            folder = ""
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", folder,"HDF (*.hdf);;All Files (*)")
        if self.DataSetModel.getCurrentDatasetIndex() is None: # no dataset is currently selected
            self.DataSet_NewDataSet_button_function()
        self.DataFileModel.add(files)
        

# def run():
    
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    application = mywindow()
    
    application.show()
    
    sys.exit(app.exec_())

# run()