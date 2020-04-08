

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


from PyQt5 import QtWidgets, QtCore, QtGui, Qt

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
        

        self.dataSets = []
        
        self.setupDataSet() # Setup datasets with buttons and call functions
        self.setupDataFile() # Setup datafiles        
        

        self.setupDataSet_DataFile_labels()

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
        
        
        self.setupMenu()

 
        
    def DataSet_convertData_button_function(self):
        #  Should add a check if a data set is selected
            
        binning=int(self.ui.DataSet_binning_comboBox.currentText())
        ds = self.DataSetModel.getCurrentDataSet()
        try:
            ds.convertDataFile(binning=binning,saveFile=False)
        except AttributeError as e:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical,title='Error')
            msg.setText("Error")
            msg.setInformativeText(str(e))
            msg.resize(300,200)
            msg.exec_()

        self.DataFileModel.layoutChanged.emit()
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
        
        if self.ui.View3D_SelectUnits_RLU_radioButton.isChecked():
            rlu=True
            
        if self.ui.View3D_SelectUnits_AA_radioButton.isChecked():
            rlu=False

        if self.ui.View3D_Grid_checkBox.isChecked():
            grid=9
        else:
            grid=False
        
        if self.ui.View3D_LogScale_checkBox.isChecked():
            log=True
        else:
            log=False        
        
        self.V = ds.View3D(QXBin,QYBin,EBin,grid=grid,rlu=rlu,log=log)
        
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
        
        HStart=float(self.ui.QELine_HStart_lineEdit.text())
        KStart=float(self.ui.QELine_KStart_lineEdit.text())
        LStart=float(self.ui.QELine_LStart_lineEdit.text())
        
        HEnd=float(self.ui.QELine_HEnd_lineEdit.text())
        KEnd=float(self.ui.QELine_KEnd_lineEdit.text())
        LEnd=float(self.ui.QELine_LEnd_lineEdit.text())
        
        
        Q1 = np.array([HStart,KStart,LStart])
        Q2 = np.array([HEnd,KEnd,LEnd])
        # Collect them into one array
        QPoints = np.array([Q1,Q2])
        
        # Define orthogonal width and minimum pixel size along Q-cut
        width = float(self.ui.QELine_Width_lineEdit.text())   # 1/AA
        minPixel = float(self.ui.QELine_MinPixel_lineEdit.text()) # 1/AA
        
        EMin=float(self.ui.QELine_EMin_lineEdit.text())
        EMax=float(self.ui.QELine_EMax_lineEdit.text())
        NPoints=int(self.ui.QELine_NPoints_lineEdit.text())
        
        # Define energy bins
        EnergyBins=np.linspace(EMin,EMax,NPoints)

        
        # fig = plt.figure(figsize=(8,6))
        # ax = fig.gca()
        # ax,DataLists,Bins,BinCenters,Offsets = \
        # ds.plotCutQELine(QPoints=QPoints, width=width, minPixel=minPixel, \
        #       ax=ax, EnergyBins=EnergyBins)
        # ax.set_clim(0,10e-8)       
        
        
        if self.ui.QELine_SelectUnits_RLU_radioButton.isChecked():
            rlu=True
            
        if self.ui.QELine_SelectUnits_AA_radioButton.isChecked():
            rlu=False        
    
        ds = self.DataSetModel.getCurrentDataSet()
        if len(ds.convertedFiles)==0:
            self.DataSet_convertData_button_function()
            
        self.QELine=ds.plotCutQELine(QPoints=QPoints, width=width, \
                                     minPixel=minPixel, EnergyBins=EnergyBins,\
                                         rlu=rlu)
    
        
        self.QELine_setCAxis_button_function()
        
        

    def QELine_setCAxis_button_function(self):
        
        CAxisMin=float(self.ui.QELine_CAxisMin_lineEdit.text())
        CAxisMax=float(self.ui.QELine_CAxisMax_lineEdit.text())
        
        self.QELine.caxis=(CAxisMin,CAxisMax)




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
        self.ui.DataSet_convertData_button.setToolTip('Convert selected Dataset')
        self.ui.DataSet_convertData_button.setStatusTip(self.ui.DataSet_convertData_button.toolTip())

        self.ui.DataSet_NewDataSet_button.clicked.connect(self.DataSet_NewDataSet_button_function)
        self.ui.DataSet_NewDataSet_button.setToolTip('Add new Dataset')
        self.ui.DataSet_NewDataSet_button.setStatusTip(self.ui.DataSet_NewDataSet_button.toolTip())

        self.ui.DataSet_DeleteDataSet_button.clicked.connect(self.DataSet_DeleteDataSet_button_function)
        self.ui.DataSet_DeleteDataSet_button.setToolTip('Delete selected Dataset')
        self.ui.DataSet_DeleteDataSet_button.setStatusTip(self.ui.DataSet_DeleteDataSet_button.toolTip())

        self.ui.DataSet_AddFiles_button.clicked.connect(self.DataSet_AddFiles_button_function)
        self.ui.DataSet_AddFiles_button.setToolTip('Add new Datafiles')
        self.ui.DataSet_AddFiles_button.setStatusTip(self.ui.DataSet_AddFiles_button.toolTip())

        self.DataSetModel = DataSetModel(dataSets=self.dataSets,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView)
        self.ui.DataSet_DataSets_listView.setModel(self.DataSetModel)

        self.DataSetSelectionModel = self.ui.DataSet_DataSets_listView.selectionModel()
        self.DataSetSelectionModel.selectionChanged.connect(self.selectedDataSetChanged)

        
        self.ui.DataSet_DataSets_listView.doubleClicked.connect(self.DataSet_DoubleClick_Selection_function)

    def setupDataFile(self): # Set up main features for Gui regarding the datafile widgets
        self.DataFileModel = DataFileModel(DataSet_filenames_listView=self.ui.DataSet_filenames_listView,dataSetModel=self.DataSetModel,DataSet_DataSets_listView=self.ui.DataSet_DataSets_listView)
        self.ui.DataSet_filenames_listView.setModel(self.DataFileModel)

        
        self.DataFileSelectionModel = self.ui.DataSet_filenames_listView.selectionModel()
        self.DataFileSelectionModel.selectionChanged.connect(self.selectedDataFileChanged)
        
        self.ui.DataSet_DeleteFiles_button.clicked.connect(self.DataSet_DeleteFiles_button_function)
        self.ui.DataSet_DeleteFiles_button.setToolTip('Delete selected Datafile')
        self.ui.DataSet_DeleteFiles_button.setStatusTip(self.ui.DataSet_DeleteFiles_button.toolTip())

        self.ui.DataSet_DataSets_listView.doubleClicked.connect(self.DataFile_DoubleClick_Selection_function)



    def selectedDataSetChanged(self,*args,**kwargs):
        self.DataFileModel.updateCurrentDataSetIndex()
        self.selectedDataFileChanged()

    def selectedDataFileChanged(self,*args,**kwargs):
        self.DataFileModel.layoutChanged.emit()
        self.updateDataFileLabels()

    def DataSet_NewDataSet_button_function(self):
        ds = GuiDataSet(name='Added')
        self.DataSetModel.append(ds)
        index = self.DataSetModel.index(self.DataSetModel.rowCount(None)-1,0)
        self.DataSetModel.DataSet_DataSets_listView.setCurrentIndex(index)

    def DataSet_DeleteDataSet_button_function(self):
        self.DataSetModel.delete(self.ui.DataSet_DataSets_listView.selectedIndexes()[0])
        self.DataFileModel.layoutChanged.emit()
        
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
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Open data Files", folder,"HDF (*.hdf);;NXS (*.nxs);;All Files (*)")
        if self.DataSetModel.getCurrentDatasetIndex() is None: # no dataset is currently selected
            self.DataSet_NewDataSet_button_function()
        self.DataFileModel.add(files)

    def setupMenu(self): # Set up all QActions and menus
        self.ui.actionExit.setIcon(QtGui.QIcon('Icons/icons/cross-button.png'))
        self.ui.actionExit.setToolTip('Exit the application') 
        self.ui.actionExit.triggered.connect(self.close)


    def setupDataSet_DataFile_labels(self): # Set up labels containing information on current data file
        self.DataFileLabels = [self.ui.DataSet_Temperature_label,self.ui.DataSet_MagneticField_label,self.ui.DataSet_SampleName_label,
                    self.ui.DataSet_ScanCommand_label,self.ui.DataSet_ScanType_label]
        self.DataFileLabelEntries = ['temperature','magneticField','sampleName','scanCommand','scanParameters']
        for label in self.DataFileLabels:
            label.defaultText = label.text()
            

    def updateDataFileLabels(self):
        index = self.DataFileModel.getCurrentDatafileIndex()
        if index is None:
            for label in self.DataFileLabels:
                label.setText(label.defaultText)
        else:
            df = self.DataFileModel.getCurrentDatafile()
            temperature = df.temperature
            if temperature is None:
                temperatureEntry = 'N/A'
            else:
                temperatureEntry = '{:.2f} [{:.2f} - {:.2f}]'.format(np.mean(temperature),np.min(temperature),np.max(temperature))

            magneticField = df.magneticField
            if magneticField is None:
                magneticFieldEntry = 'N/A'
            else:
                magneticFieldEntry = '{:.2f} [{:.2f} - {:.2f}]'.format(np.mean(magneticField,np.min(magneticField),np.max(magneticField)))

            sampleNameEntry = df.sample.name
            scanCommandEntry = df.scanCommand
            scanParameters = df.scanParameters
            scanParametersEntry = ', '.join(scanParameters)
            
            entries = [temperatureEntry,magneticFieldEntry,sampleNameEntry,scanCommandEntry,scanParametersEntry,scanParametersEntry]

            for label,entry in zip(self.DataFileLabels,entries):
                label.setText(label.defaultText+': '+entry)
            


# def run():
    
if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    application = mywindow()
    
    application.show()
    
    sys.exit(app.exec_())

# run()