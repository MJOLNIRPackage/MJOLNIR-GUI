try:
    from PyQt6 import QtCore, QtGui, QtWidgets, uic, Qt
    QT_VERSION = 6
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic, Qt
    QT_VERSION = 5

QApplication = QtWidgets.QApplication