# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MJOLNIR_GUI_ui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(631, 886)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.DataSet_convertData_button = QtWidgets.QPushButton(self.centralwidget)
        self.DataSet_convertData_button.setGeometry(QtCore.QRect(300, 240, 75, 23))
        self.DataSet_convertData_button.setObjectName("DataSet_convertData_button")
        self.DataSet_binning_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.DataSet_binning_comboBox.setGeometry(QtCore.QRect(300, 210, 69, 22))
        self.DataSet_binning_comboBox.setObjectName("DataSet_binning_comboBox")
        self.DataSet_binning_comboBox.addItem("")
        self.DataSet_binning_comboBox.addItem("")
        self.DataSet_binning_comboBox.addItem("")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(300, 190, 71, 16))
        self.label.setObjectName("label")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(20, 290, 176, 41))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)
        self.View3D_QYBin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.View3D_QYBin_lineEdit.setObjectName("View3D_QYBin_lineEdit")
        self.gridLayout.addWidget(self.View3D_QYBin_lineEdit, 0, 1, 1, 1)
        self.View3D_QXBin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.View3D_QXBin_lineEdit.setObjectName("View3D_QXBin_lineEdit")
        self.gridLayout.addWidget(self.View3D_QXBin_lineEdit, 0, 0, 1, 1)
        self.View3D_EBin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.View3D_EBin_lineEdit.setObjectName("View3D_EBin_lineEdit")
        self.gridLayout.addWidget(self.View3D_EBin_lineEdit, 0, 2, 1, 1)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(210, 280, 114, 48))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.View3D_CAxisMin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.View3D_CAxisMin_lineEdit.setObjectName("View3D_CAxisMin_lineEdit")
        self.gridLayout_2.addWidget(self.View3D_CAxisMin_lineEdit, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)
        self.View3D_CAxisMax_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_2)
        self.View3D_CAxisMax_lineEdit.setObjectName("View3D_CAxisMax_lineEdit")
        self.gridLayout_2.addWidget(self.View3D_CAxisMax_lineEdit, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 0, 1, 1)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(340, 280, 61, 84))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.View3D_SelectView_QxE_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.View3D_SelectView_QxE_radioButton.setObjectName("View3D_SelectView_QxE_radioButton")
        self.verticalLayout.addWidget(self.View3D_SelectView_QxE_radioButton)
        self.View3D_SelectView_QyE_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.View3D_SelectView_QyE_radioButton.setObjectName("View3D_SelectView_QyE_radioButton")
        self.verticalLayout.addWidget(self.View3D_SelectView_QyE_radioButton)
        self.View3D_SelectView_QxQy_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.View3D_SelectView_QxQy_radioButton.setChecked(True)
        self.View3D_SelectView_QxQy_radioButton.setObjectName("View3D_SelectView_QxQy_radioButton")
        self.verticalLayout.addWidget(self.View3D_SelectView_QxQy_radioButton)
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(70, 260, 61, 28))
        self.label_8.setObjectName("label_8")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(410, 280, 51, 61))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.View3D_SelectUnits_RLU_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget_2)
        self.View3D_SelectUnits_RLU_radioButton.setChecked(True)
        self.View3D_SelectUnits_RLU_radioButton.setObjectName("View3D_SelectUnits_RLU_radioButton")
        self.verticalLayout_2.addWidget(self.View3D_SelectUnits_RLU_radioButton)
        self.View3D_SelectUnits_AA_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget_2)
        self.View3D_SelectUnits_AA_radioButton.setObjectName("View3D_SelectUnits_AA_radioButton")
        self.verticalLayout_2.addWidget(self.View3D_SelectUnits_AA_radioButton)
        self.label_9 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_2.addWidget(self.label_9)
        self.DataSet_NewDataSet_button = QtWidgets.QPushButton(self.centralwidget)
        self.DataSet_NewDataSet_button.setGeometry(QtCore.QRect(10, 50, 75, 23))
        self.DataSet_NewDataSet_button.setObjectName("DataSet_NewDataSet_button")
        self.DataSet_DeleteDataSet_button = QtWidgets.QPushButton(self.centralwidget)
        self.DataSet_DeleteDataSet_button.setGeometry(QtCore.QRect(10, 80, 91, 23))
        self.DataSet_DeleteDataSet_button.setObjectName("DataSet_DeleteDataSet_button")
        self.DataSet_AddFiles_button = QtWidgets.QPushButton(self.centralwidget)
        self.DataSet_AddFiles_button.setGeometry(QtCore.QRect(130, 20, 111, 23))
        self.DataSet_AddFiles_button.setObjectName("DataSet_AddFiles_button")
        self.DataSet_DeleteFiles_button = QtWidgets.QPushButton(self.centralwidget)
        self.DataSet_DeleteFiles_button.setGeometry(QtCore.QRect(130, 50, 131, 23))
        self.DataSet_DeleteFiles_button.setObjectName("DataSet_DeleteFiles_button")
        self.View3D_SetTitle_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.View3D_SetTitle_lineEdit.setGeometry(QtCore.QRect(480, 280, 113, 20))
        self.View3D_SetTitle_lineEdit.setText("")
        self.View3D_SetTitle_lineEdit.setObjectName("View3D_SetTitle_lineEdit")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(0, 260, 621, 111))
        self.groupBox.setObjectName("groupBox")
        self.View3D_LogScale_checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.View3D_LogScale_checkBox.setGeometry(QtCore.QRect(420, 90, 70, 17))
        self.View3D_LogScale_checkBox.setObjectName("View3D_LogScale_checkBox")
        self.View3D_SetTitle_button = QtWidgets.QPushButton(self.groupBox)
        self.View3D_SetTitle_button.setGeometry(QtCore.QRect(500, 40, 75, 23))
        self.View3D_SetTitle_button.setObjectName("View3D_SetTitle_button")
        self.View3D_setCAxis_button = QtWidgets.QPushButton(self.groupBox)
        self.View3D_setCAxis_button.setGeometry(QtCore.QRect(220, 70, 75, 23))
        self.View3D_setCAxis_button.setObjectName("View3D_setCAxis_button")
        self.View3D_plot_button = QtWidgets.QPushButton(self.groupBox)
        self.View3D_plot_button.setGeometry(QtCore.QRect(500, 80, 75, 23))
        self.View3D_plot_button.setObjectName("View3D_plot_button")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(0, 370, 621, 181))
        self.groupBox_2.setObjectName("groupBox_2")
        self.QELine_plot_button = QtWidgets.QPushButton(self.groupBox_2)
        self.QELine_plot_button.setGeometry(QtCore.QRect(540, 150, 75, 23))
        self.QELine_plot_button.setObjectName("QELine_plot_button")
        self.QELine_ConstantBin_checkBox = QtWidgets.QCheckBox(self.groupBox_2)
        self.QELine_ConstantBin_checkBox.setGeometry(QtCore.QRect(340, 140, 91, 21))
        self.QELine_ConstantBin_checkBox.setObjectName("QELine_ConstantBin_checkBox")
        self.View3D_setCAxis_button_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.View3D_setCAxis_button_2.setGeometry(QtCore.QRect(370, 60, 75, 23))
        self.View3D_setCAxis_button_2.setObjectName("View3D_setCAxis_button_2")
        self.QELine_SetTitle_lineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.QELine_SetTitle_lineEdit.setGeometry(QtCore.QRect(490, 20, 113, 20))
        self.QELine_SetTitle_lineEdit.setText("")
        self.QELine_SetTitle_lineEdit.setObjectName("QELine_SetTitle_lineEdit")
        self.QELine_SetTitle_button = QtWidgets.QPushButton(self.groupBox_2)
        self.QELine_SetTitle_button.setGeometry(QtCore.QRect(490, 40, 75, 23))
        self.QELine_SetTitle_button.setObjectName("QELine_SetTitle_button")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.groupBox_2)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(50, 10, 229, 71))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_20 = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.label_20.setObjectName("label_20")
        self.gridLayout_4.addWidget(self.label_20, 1, 0, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.label_21.setObjectName("label_21")
        self.gridLayout_4.addWidget(self.label_21, 3, 0, 1, 1)
        self.QELine_HStart_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.QELine_HStart_lineEdit.setObjectName("QELine_HStart_lineEdit")
        self.gridLayout_4.addWidget(self.QELine_HStart_lineEdit, 1, 1, 1, 1)
        self.QELine_KStart_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.QELine_KStart_lineEdit.setObjectName("QELine_KStart_lineEdit")
        self.gridLayout_4.addWidget(self.QELine_KStart_lineEdit, 1, 2, 1, 1)
        self.QELine_LStart_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.QELine_LStart_lineEdit.setObjectName("QELine_LStart_lineEdit")
        self.gridLayout_4.addWidget(self.QELine_LStart_lineEdit, 1, 3, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.label_18.setObjectName("label_18")
        self.gridLayout_4.addWidget(self.label_18, 0, 1, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.label_19.setObjectName("label_19")
        self.gridLayout_4.addWidget(self.label_19, 0, 2, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.gridLayoutWidget_4)
        self.label_17.setObjectName("label_17")
        self.gridLayout_4.addWidget(self.label_17, 0, 3, 1, 1)
        self.QELine_HEnd_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.QELine_HEnd_lineEdit.setObjectName("QELine_HEnd_lineEdit")
        self.gridLayout_4.addWidget(self.QELine_HEnd_lineEdit, 3, 1, 1, 1)
        self.QELine_KEnd_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.QELine_KEnd_lineEdit.setObjectName("QELine_KEnd_lineEdit")
        self.gridLayout_4.addWidget(self.QELine_KEnd_lineEdit, 3, 2, 1, 1)
        self.QELine_LEnd_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_4)
        self.QELine_LEnd_lineEdit.setObjectName("QELine_LEnd_lineEdit")
        self.gridLayout_4.addWidget(self.QELine_LEnd_lineEdit, 3, 3, 1, 1)
        self.gridLayoutWidget_8 = QtWidgets.QWidget(self.groupBox_2)
        self.gridLayoutWidget_8.setGeometry(QtCore.QRect(50, 90, 216, 41))
        self.gridLayoutWidget_8.setObjectName("gridLayoutWidget_8")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.gridLayoutWidget_8)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_31 = QtWidgets.QLabel(self.gridLayoutWidget_8)
        self.label_31.setObjectName("label_31")
        self.gridLayout_8.addWidget(self.label_31, 1, 0, 1, 1)
        self.QELine_EMin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_8)
        self.QELine_EMin_lineEdit.setObjectName("QELine_EMin_lineEdit")
        self.gridLayout_8.addWidget(self.QELine_EMin_lineEdit, 1, 1, 1, 1)
        self.QELine_NPoints_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_8)
        self.QELine_NPoints_lineEdit.setObjectName("QELine_NPoints_lineEdit")
        self.gridLayout_8.addWidget(self.QELine_NPoints_lineEdit, 1, 3, 1, 1)
        self.QELine_Emax_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_8)
        self.QELine_Emax_lineEdit.setObjectName("QELine_Emax_lineEdit")
        self.gridLayout_8.addWidget(self.QELine_Emax_lineEdit, 1, 2, 1, 1)
        self.label_32 = QtWidgets.QLabel(self.gridLayoutWidget_8)
        self.label_32.setAlignment(QtCore.Qt.AlignCenter)
        self.label_32.setObjectName("label_32")
        self.gridLayout_8.addWidget(self.label_32, 0, 1, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.gridLayoutWidget_8)
        self.label_33.setObjectName("label_33")
        self.gridLayout_8.addWidget(self.label_33, 0, 2, 1, 1)
        self.label_34 = QtWidgets.QLabel(self.gridLayoutWidget_8)
        self.label_34.setObjectName("label_34")
        self.gridLayout_8.addWidget(self.label_34, 0, 3, 1, 1)
        self.gridLayoutWidget_9 = QtWidgets.QWidget(self.groupBox_2)
        self.gridLayoutWidget_9.setGeometry(QtCore.QRect(50, 140, 216, 22))
        self.gridLayoutWidget_9.setObjectName("gridLayoutWidget_9")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.gridLayoutWidget_9)
        self.gridLayout_9.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.label_36 = QtWidgets.QLabel(self.gridLayoutWidget_9)
        self.label_36.setObjectName("label_36")
        self.gridLayout_9.addWidget(self.label_36, 0, 0, 1, 1)
        self.QELine_Width_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_9)
        self.QELine_Width_lineEdit.setObjectName("QELine_Width_lineEdit")
        self.gridLayout_9.addWidget(self.QELine_Width_lineEdit, 0, 1, 1, 1)
        self.QELine_MinPixel_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_9)
        self.QELine_MinPixel_lineEdit.setObjectName("QELine_MinPixel_lineEdit")
        self.gridLayout_9.addWidget(self.QELine_MinPixel_lineEdit, 0, 3, 1, 1)
        self.label_37 = QtWidgets.QLabel(self.gridLayoutWidget_9)
        self.label_37.setObjectName("label_37")
        self.gridLayout_9.addWidget(self.label_37, 0, 2, 1, 1)
        self.QELine_LogScale_checkBox = QtWidgets.QCheckBox(self.groupBox_2)
        self.QELine_LogScale_checkBox.setGeometry(QtCore.QRect(340, 120, 70, 17))
        self.QELine_LogScale_checkBox.setObjectName("QELine_LogScale_checkBox")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.groupBox_2)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(480, 70, 51, 61))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.QELine_SelectUnits_RLU_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget_3)
        self.QELine_SelectUnits_RLU_radioButton.setChecked(True)
        self.QELine_SelectUnits_RLU_radioButton.setObjectName("QELine_SelectUnits_RLU_radioButton")
        self.verticalLayout_3.addWidget(self.QELine_SelectUnits_RLU_radioButton)
        self.QELine_SelectUnits_AA_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget_3)
        self.QELine_SelectUnits_AA_radioButton.setObjectName("QELine_SelectUnits_AA_radioButton")
        self.verticalLayout_3.addWidget(self.QELine_SelectUnits_AA_radioButton)
        self.label_15 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        self.label_15.setObjectName("label_15")
        self.verticalLayout_3.addWidget(self.label_15)
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.groupBox_2)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(360, 10, 114, 48))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.QELine_CAxisMin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.QELine_CAxisMin_lineEdit.setObjectName("QELine_CAxisMin_lineEdit")
        self.gridLayout_3.addWidget(self.QELine_CAxisMin_lineEdit, 0, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_16.setObjectName("label_16")
        self.gridLayout_3.addWidget(self.label_16, 1, 0, 1, 1)
        self.QELine_CAxisMax_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_3)
        self.QELine_CAxisMax_lineEdit.setObjectName("QELine_CAxisMax_lineEdit")
        self.gridLayout_3.addWidget(self.QELine_CAxisMax_lineEdit, 1, 1, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_22.setObjectName("label_22")
        self.gridLayout_3.addWidget(self.label_22, 0, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 720, 621, 131))
        self.groupBox_3.setObjectName("groupBox_3")
        self.pushButton_13 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_13.setGeometry(QtCore.QRect(10, 20, 75, 23))
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_14 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_14.setGeometry(QtCore.QRect(10, 80, 75, 23))
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_5.setGeometry(QtCore.QRect(10, 50, 75, 23))
        self.pushButton_5.setObjectName("pushButton_5")
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_5.setGeometry(QtCore.QRect(0, 560, 621, 161))
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayoutWidget_10 = QtWidgets.QWidget(self.groupBox_5)
        self.gridLayoutWidget_10.setGeometry(QtCore.QRect(50, 20, 156, 41))
        self.gridLayoutWidget_10.setObjectName("gridLayoutWidget_10")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.gridLayoutWidget_10)
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.label_35 = QtWidgets.QLabel(self.gridLayoutWidget_10)
        self.label_35.setObjectName("label_35")
        self.gridLayout_10.addWidget(self.label_35, 1, 0, 1, 1)
        self.QPlane_EMin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_10)
        self.QPlane_EMin_lineEdit.setObjectName("QPlane_EMin_lineEdit")
        self.gridLayout_10.addWidget(self.QPlane_EMin_lineEdit, 1, 1, 1, 1)
        self.QPlane_EMin_lineEdit_2 = QtWidgets.QLineEdit(self.gridLayoutWidget_10)
        self.QPlane_EMin_lineEdit_2.setObjectName("QPlane_EMin_lineEdit_2")
        self.gridLayout_10.addWidget(self.QPlane_EMin_lineEdit_2, 1, 2, 1, 1)
        self.label_38 = QtWidgets.QLabel(self.gridLayoutWidget_10)
        self.label_38.setAlignment(QtCore.Qt.AlignCenter)
        self.label_38.setObjectName("label_38")
        self.gridLayout_10.addWidget(self.label_38, 0, 1, 1, 1)
        self.label_39 = QtWidgets.QLabel(self.gridLayoutWidget_10)
        self.label_39.setObjectName("label_39")
        self.gridLayout_10.addWidget(self.label_39, 0, 2, 1, 1)
        self.gridLayoutWidget_11 = QtWidgets.QWidget(self.groupBox_5)
        self.gridLayoutWidget_11.setGeometry(QtCore.QRect(50, 70, 111, 48))
        self.gridLayoutWidget_11.setObjectName("gridLayoutWidget_11")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.gridLayoutWidget_11)
        self.gridLayout_11.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.label_41 = QtWidgets.QLabel(self.gridLayoutWidget_11)
        self.label_41.setObjectName("label_41")
        self.gridLayout_11.addWidget(self.label_41, 0, 0, 1, 1)
        self.QPlane_QxWidth_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_11)
        self.QPlane_QxWidth_lineEdit.setObjectName("QPlane_QxWidth_lineEdit")
        self.gridLayout_11.addWidget(self.QPlane_QxWidth_lineEdit, 0, 1, 1, 1)
        self.label_42 = QtWidgets.QLabel(self.gridLayoutWidget_11)
        self.label_42.setObjectName("label_42")
        self.gridLayout_11.addWidget(self.label_42, 1, 0, 1, 1)
        self.QPlane_QyWidth_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_11)
        self.QPlane_QyWidth_lineEdit.setObjectName("QPlane_QyWidth_lineEdit")
        self.gridLayout_11.addWidget(self.QPlane_QyWidth_lineEdit, 1, 1, 1, 1)
        self.QPlane_SetTitle_button = QtWidgets.QPushButton(self.groupBox_5)
        self.QPlane_SetTitle_button.setGeometry(QtCore.QRect(490, 60, 75, 23))
        self.QPlane_SetTitle_button.setObjectName("QPlane_SetTitle_button")
        self.QPlane_SetTitle_lineEdit = QtWidgets.QLineEdit(self.groupBox_5)
        self.QPlane_SetTitle_lineEdit.setGeometry(QtCore.QRect(490, 30, 113, 20))
        self.QPlane_SetTitle_lineEdit.setText("")
        self.QPlane_SetTitle_lineEdit.setObjectName("QPlane_SetTitle_lineEdit")
        self.QPlane_LogScale_checkBox = QtWidgets.QCheckBox(self.groupBox_5)
        self.QPlane_LogScale_checkBox.setGeometry(QtCore.QRect(290, 110, 70, 17))
        self.QPlane_LogScale_checkBox.setObjectName("QPlane_LogScale_checkBox")
        self.QPlane_plot_button = QtWidgets.QPushButton(self.groupBox_5)
        self.QPlane_plot_button.setGeometry(QtCore.QRect(540, 130, 75, 23))
        self.QPlane_plot_button.setObjectName("QPlane_plot_button")
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.groupBox_5)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(220, 90, 51, 61))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.QPlane_SelectUnits_RLU_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget_4)
        self.QPlane_SelectUnits_RLU_radioButton.setChecked(True)
        self.QPlane_SelectUnits_RLU_radioButton.setObjectName("QPlane_SelectUnits_RLU_radioButton")
        self.verticalLayout_4.addWidget(self.QPlane_SelectUnits_RLU_radioButton)
        self.QPlane_SelectUnits_AA_radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget_4)
        self.QPlane_SelectUnits_AA_radioButton.setObjectName("QPlane_SelectUnits_AA_radioButton")
        self.verticalLayout_4.addWidget(self.QPlane_SelectUnits_AA_radioButton)
        self.label_23 = QtWidgets.QLabel(self.verticalLayoutWidget_4)
        self.label_23.setObjectName("label_23")
        self.verticalLayout_4.addWidget(self.label_23)
        self.gridLayoutWidget_5 = QtWidgets.QWidget(self.groupBox_5)
        self.gridLayoutWidget_5.setGeometry(QtCore.QRect(310, 20, 114, 48))
        self.gridLayoutWidget_5.setObjectName("gridLayoutWidget_5")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.gridLayoutWidget_5)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.QPlane_CAxisMin_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_5)
        self.QPlane_CAxisMin_lineEdit.setObjectName("QPlane_CAxisMin_lineEdit")
        self.gridLayout_5.addWidget(self.QPlane_CAxisMin_lineEdit, 0, 1, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.gridLayoutWidget_5)
        self.label_24.setObjectName("label_24")
        self.gridLayout_5.addWidget(self.label_24, 1, 0, 1, 1)
        self.QPlane_CAxisMax_lineEdit = QtWidgets.QLineEdit(self.gridLayoutWidget_5)
        self.QPlane_CAxisMax_lineEdit.setObjectName("QPlane_CAxisMax_lineEdit")
        self.gridLayout_5.addWidget(self.QPlane_CAxisMax_lineEdit, 1, 1, 1, 1)
        self.label_25 = QtWidgets.QLabel(self.gridLayoutWidget_5)
        self.label_25.setObjectName("label_25")
        self.gridLayout_5.addWidget(self.label_25, 0, 0, 1, 1)
        self.QPlane_setCAxis_button = QtWidgets.QPushButton(self.groupBox_5)
        self.QPlane_setCAxis_button.setGeometry(QtCore.QRect(330, 70, 75, 23))
        self.QPlane_setCAxis_button.setObjectName("QPlane_setCAxis_button")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(410, 80, 71, 16))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(410, 100, 81, 16))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(410, 120, 71, 16))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(410, 140, 81, 16))
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(410, 160, 81, 16))
        self.label_14.setObjectName("label_14")
        self.DataSet_path_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.DataSet_path_lineEdit.setGeometry(QtCore.QRect(130, 80, 221, 20))
        self.DataSet_path_lineEdit.setObjectName("DataSet_path_lineEdit")
        self.DataSet_filenames_listView = QtWidgets.QListView(self.centralwidget)
        self.DataSet_filenames_listView.setGeometry(QtCore.QRect(130, 110, 161, 151))
        self.DataSet_filenames_listView.setObjectName("DataSet_filenames_listView")
        self.DataSet_DataSets_listView = QtWidgets.QListView(self.centralwidget)
        self.DataSet_DataSets_listView.setGeometry(QtCore.QRect(10, 110, 111, 151))
        self.DataSet_DataSets_listView.setObjectName("DataSet_DataSets_listView")
        self.groupBox_3.raise_()
        self.groupBox_5.raise_()
        self.groupBox_2.raise_()
        self.groupBox.raise_()
        self.DataSet_convertData_button.raise_()
        self.DataSet_binning_comboBox.raise_()
        self.label.raise_()
        self.gridLayoutWidget.raise_()
        self.gridLayoutWidget_2.raise_()
        self.verticalLayoutWidget.raise_()
        self.label_8.raise_()
        self.verticalLayoutWidget_2.raise_()
        self.DataSet_NewDataSet_button.raise_()
        self.DataSet_DeleteDataSet_button.raise_()
        self.DataSet_AddFiles_button.raise_()
        self.DataSet_DeleteFiles_button.raise_()
        self.View3D_SetTitle_lineEdit.raise_()
        self.label_10.raise_()
        self.label_11.raise_()
        self.label_12.raise_()
        self.label_13.raise_()
        self.label_14.raise_()
        self.DataSet_path_lineEdit.raise_()
        self.DataSet_filenames_listView.raise_()
        self.DataSet_DataSets_listView.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 631, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuMask = QtWidgets.QMenu(self.menubar)
        self.menuMask.setObjectName("menuMask")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen_mask_gui = QtWidgets.QAction(MainWindow)
        self.actionOpen_mask_gui.setObjectName("actionOpen_mask_gui")
        self.actionLoad_mask = QtWidgets.QAction(MainWindow)
        self.actionLoad_mask.setObjectName("actionLoad_mask")
        self.actionGenerate_View3d_script = QtWidgets.QAction(MainWindow)
        self.actionGenerate_View3d_script.setObjectName("actionGenerate_View3d_script")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionGenerate_View3d_script)
        self.menuMask.addAction(self.actionOpen_mask_gui)
        self.menuMask.addAction(self.actionLoad_mask)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuMask.menuAction())

        self.retranslateUi(MainWindow)
        self.DataSet_binning_comboBox.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.DataSet_convertData_button.setText(_translate("MainWindow", "Convert Data"))
        self.DataSet_binning_comboBox.setToolTip(_translate("MainWindow", "Binning"))
        self.DataSet_binning_comboBox.setCurrentText(_translate("MainWindow", "8"))
        self.DataSet_binning_comboBox.setItemText(0, _translate("MainWindow", "1"))
        self.DataSet_binning_comboBox.setItemText(1, _translate("MainWindow", "3"))
        self.DataSet_binning_comboBox.setItemText(2, _translate("MainWindow", "8"))
        self.label.setText(_translate("MainWindow", "Select binning"))
        self.label_4.setText(_translate("MainWindow", "E"))
        self.label_2.setText(_translate("MainWindow", "Qx"))
        self.label_3.setText(_translate("MainWindow", "Qy"))
        self.View3D_QYBin_lineEdit.setText(_translate("MainWindow", "0.05"))
        self.View3D_QXBin_lineEdit.setText(_translate("MainWindow", "0.05"))
        self.View3D_EBin_lineEdit.setText(_translate("MainWindow", "0.05"))
        self.View3D_CAxisMin_lineEdit.setText(_translate("MainWindow", "0"))
        self.label_6.setText(_translate("MainWindow", "C axis max"))
        self.View3D_CAxisMax_lineEdit.setText(_translate("MainWindow", "5e-6"))
        self.label_5.setText(_translate("MainWindow", "C axis min"))
        self.View3D_SelectView_QxE_radioButton.setText(_translate("MainWindow", "Qx E"))
        self.View3D_SelectView_QyE_radioButton.setText(_translate("MainWindow", "Qy E"))
        self.View3D_SelectView_QxQy_radioButton.setText(_translate("MainWindow", "Qx Qy"))
        self.label_7.setText(_translate("MainWindow", "Select view"))
        self.label_8.setText(_translate("MainWindow", "View3d bins"))
        self.View3D_SelectUnits_RLU_radioButton.setText(_translate("MainWindow", "RLU"))
        self.View3D_SelectUnits_AA_radioButton.setText(_translate("MainWindow", "AA-1"))
        self.label_9.setText(_translate("MainWindow", "Units"))
        self.DataSet_NewDataSet_button.setText(_translate("MainWindow", "New data set"))
        self.DataSet_DeleteDataSet_button.setText(_translate("MainWindow", "Delete data set"))
        self.DataSet_AddFiles_button.setText(_translate("MainWindow", "Add files to data set"))
        self.DataSet_DeleteFiles_button.setText(_translate("MainWindow", "Delete files from data set"))
        self.groupBox.setTitle(_translate("MainWindow", "View 3d"))
        self.View3D_LogScale_checkBox.setText(_translate("MainWindow", "Log scale"))
        self.View3D_SetTitle_button.setText(_translate("MainWindow", "Set title"))
        self.View3D_setCAxis_button.setText(_translate("MainWindow", "Set c axis"))
        self.View3D_plot_button.setText(_translate("MainWindow", "Plot View3D"))
        self.groupBox_2.setTitle(_translate("MainWindow", "QE line"))
        self.QELine_plot_button.setText(_translate("MainWindow", "Plot 2d cut"))
        self.QELine_ConstantBin_checkBox.setText(_translate("MainWindow", "Constant bins"))
        self.View3D_setCAxis_button_2.setText(_translate("MainWindow", "Set c axis"))
        self.QELine_SetTitle_button.setText(_translate("MainWindow", "Set title"))
        self.label_20.setText(_translate("MainWindow", "Start"))
        self.label_21.setText(_translate("MainWindow", "End"))
        self.QELine_HStart_lineEdit.setText(_translate("MainWindow", "0"))
        self.QELine_KStart_lineEdit.setText(_translate("MainWindow", "0"))
        self.QELine_LStart_lineEdit.setText(_translate("MainWindow", "0"))
        self.label_18.setText(_translate("MainWindow", "H"))
        self.label_19.setText(_translate("MainWindow", "K"))
        self.label_17.setText(_translate("MainWindow", "L"))
        self.QELine_HEnd_lineEdit.setText(_translate("MainWindow", "1"))
        self.QELine_KEnd_lineEdit.setText(_translate("MainWindow", "0"))
        self.QELine_LEnd_lineEdit.setText(_translate("MainWindow", "0"))
        self.label_31.setText(_translate("MainWindow", "Energy"))
        self.label_32.setText(_translate("MainWindow", "Min"))
        self.label_33.setText(_translate("MainWindow", "Max"))
        self.label_34.setText(_translate("MainWindow", "N points"))
        self.label_36.setText(_translate("MainWindow", "Width"))
        self.QELine_Width_lineEdit.setText(_translate("MainWindow", "0.1"))
        self.QELine_MinPixel_lineEdit.setText(_translate("MainWindow", "0.03"))
        self.label_37.setText(_translate("MainWindow", "Min pixel"))
        self.QELine_LogScale_checkBox.setText(_translate("MainWindow", "Log scale"))
        self.QELine_SelectUnits_RLU_radioButton.setText(_translate("MainWindow", "RLU"))
        self.QELine_SelectUnits_AA_radioButton.setText(_translate("MainWindow", "AA-1"))
        self.label_15.setText(_translate("MainWindow", "Units"))
        self.QELine_CAxisMin_lineEdit.setText(_translate("MainWindow", "0"))
        self.label_16.setText(_translate("MainWindow", "C axis max"))
        self.QELine_CAxisMax_lineEdit.setText(_translate("MainWindow", "5e-6"))
        self.label_22.setText(_translate("MainWindow", "C axis min"))
        self.groupBox_3.setTitle(_translate("MainWindow", "1d stuff"))
        self.pushButton_13.setText(_translate("MainWindow", "Simple plot"))
        self.pushButton_14.setText(_translate("MainWindow", "Make cut"))
        self.pushButton_5.setText(_translate("MainWindow", "Make fit"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Q plane"))
        self.label_35.setText(_translate("MainWindow", "Energy"))
        self.QPlane_EMin_lineEdit.setText(_translate("MainWindow", "1"))
        self.QPlane_EMin_lineEdit_2.setText(_translate("MainWindow", "2"))
        self.label_38.setText(_translate("MainWindow", "Min"))
        self.label_39.setText(_translate("MainWindow", "Max"))
        self.label_41.setText(_translate("MainWindow", "Qx width"))
        self.QPlane_QxWidth_lineEdit.setText(_translate("MainWindow", "0.03"))
        self.label_42.setText(_translate("MainWindow", "Qy width"))
        self.QPlane_QyWidth_lineEdit.setText(_translate("MainWindow", "0.03"))
        self.QPlane_SetTitle_button.setText(_translate("MainWindow", "Set title"))
        self.QPlane_LogScale_checkBox.setText(_translate("MainWindow", "Log scale"))
        self.QPlane_plot_button.setText(_translate("MainWindow", "Plot Q plane"))
        self.QPlane_SelectUnits_RLU_radioButton.setText(_translate("MainWindow", "RLU"))
        self.QPlane_SelectUnits_AA_radioButton.setText(_translate("MainWindow", "AA-1"))
        self.label_23.setText(_translate("MainWindow", "Units"))
        self.QPlane_CAxisMin_lineEdit.setText(_translate("MainWindow", "0"))
        self.label_24.setText(_translate("MainWindow", "C axis max"))
        self.QPlane_CAxisMax_lineEdit.setText(_translate("MainWindow", "5e-6"))
        self.label_25.setText(_translate("MainWindow", "C axis min"))
        self.QPlane_setCAxis_button.setText(_translate("MainWindow", "Set c axis"))
        self.label_10.setText(_translate("MainWindow", "Temperature"))
        self.label_11.setText(_translate("MainWindow", "Magnetic field"))
        self.label_12.setText(_translate("MainWindow", "Sample name"))
        self.label_13.setText(_translate("MainWindow", "Scan command"))
        self.label_14.setText(_translate("MainWindow", "Type of scan"))
        self.DataSet_path_lineEdit.setText(_translate("MainWindow", "Path/To/Current/Directory/"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuMask.setTitle(_translate("MainWindow", "Mask"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionOpen_mask_gui.setText(_translate("MainWindow", "Open mask gui"))
        self.actionLoad_mask.setText(_translate("MainWindow", "Load mask"))
        self.actionGenerate_View3d_script.setText(_translate("MainWindow", "Generate View3d script"))
