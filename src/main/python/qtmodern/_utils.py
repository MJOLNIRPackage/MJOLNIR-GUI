import sys
from os.path import join, dirname, abspath
import qtpy
import platform

QT_VERSION = tuple(int(v) for v in qtpy.QT_VERSION.split('.'))
""" tuple: Qt version. """

PLATFORM = platform.system()


import sys

sys.path.append('..')

import AppContextEmulator

appEmu = AppContextEmulator.AppContextEmulator(__file__)

