from fbs_runtime.application_context.PyQt5 import ApplicationContext
from MJOLNIR_GUI import mywindow

import sys

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



if __name__ == '__main__':
    ctx = ApplicationContext()
    w = mywindow()
    w.show()
    exit_code = ctx.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
