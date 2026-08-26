
from MJOLNIRGui.MJOLNIR_GUI import MJOLNIRMainWindow,updateSplash
    
from MJOLNIRGui._qt import QtWidgets, QtGui, QtCore
import datetime
from functools import cached_property

from pathlib import Path

RESOURCE_DIR = Path(__file__).parent / "resources"

class AppContext():
    def __init__(self,*args,**kwargs):
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self.splash = QtWidgets.QSplashScreen(QtGui.QPixmap(self.get_resource('splash.png')))                                    
        
        self.splash.show()
        
        self.timer = QtCore.QTimer() 
        
        updateInterval = 400 # ms
        originalTime = datetime.datetime.now()
        
        updater = lambda:updateSplash(self.splash,originalTime=originalTime,updateInterval=updateInterval)
        updater()
        
        
        self.timer.timeout.connect(updater) 
        self.timer.setInterval(updateInterval)
        self.timer.start()
        QtWidgets.QApplication.processEvents()

        

    def run(self):
        
        QtWidgets.QApplication.processEvents()
        self.splash.finish(self.main_window)
        self.main_window.show()

        if len(sys.argv)==2:
            self.main_window.loadGui(presetFileLocation=sys.argv[1])
        return self.app.exec_()

    @cached_property
    def main_window(self):
        QtWidgets.QApplication.processEvents()
        res = MJOLNIRMainWindow(self)
        self.timer.stop()
        return res # Pass context to the window.

    def get_resource(self, resource_name):
        return str(RESOURCE_DIR / resource_name)

def main():
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)

if __name__ == '__main__':
    import os
    os.environ["QT_LOGGING_RULES"] = "*.debug=false"
    main()
