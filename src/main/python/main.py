#from fbs_runtime.application_context.PyQt5 import ApplicationContext
import sys
try:
    from MJOLNIR_GUI import MJOLNIRMainWindow,updateSplash
except ImportError:
    sys.path.append('.')
    try:
        from .MJOLNIR_GUI import MJOLNIRMainWindow,updateSplash
    except ImportError:
        from MJOLNIR_GUI import MJOLNIRMainWindow,updateSplash
    import os
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    
from PyQt5 import QtWidgets, QtGui, QtCore
import datetime

#class AppContext(ApplicationContext):#
#
#    def __init__(self, *args, **kwargs):
#        super(AppContent, self).__init__(*args, **kwargs)
#
#        self.window = mywindow()
#
#    def run(self):
#        self.window.show()
#        return self.app.exec_()

from fbs_runtime.application_context.PyQt5 import ApplicationContext, \
    cached_property


class AppContext(ApplicationContext):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
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
        
        return self.app.exec_()

    @cached_property
    def main_window(self):
        QtWidgets.QApplication.processEvents()
        res = MJOLNIRMainWindow(self)
        self.timer.stop()
        return res # Pass context to the window.

#if __name__ == '__main__':
#    ctx = ApplicationContext()
#    w = mywindow()
#    w.show()
#    exit_code = ctx.app.exec_()      # 2. Invoke appctxt.app.exec_()
#    sys.exit(exit_code)
def main():
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
