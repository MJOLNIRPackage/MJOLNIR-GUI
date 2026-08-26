import pytest
from MJOLNIRGui._qt import QApplication

@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def gui_window(qapp):
    from MJOLNIRGui.main import AppContext

    context = AppContext()
    window = context.main_window

    yield context, window

    context.timer.stop()
    window.deleteLater()
    context.splash.deleteLater()

from MJOLNIRGui.Views.BraggListManager import BraggListManager
from MJOLNIRGui.Views.CalculatorAdvancedManager import CalculatorAdvancedManager
from MJOLNIRGui.Views.CalculatorSimpleManager import CalculatorSimpleManager
from MJOLNIRGui.Views.Cut1DManager import Cut1DManager
from MJOLNIRGui.Views.DataSetManager import DataSetManager
from MJOLNIRGui.Views.QELineManager import QELineManager
from MJOLNIRGui.Views.QPlaneManager import QPlaneManager
from MJOLNIRGui.Views.Raw1DManager import Raw1DManager
from MJOLNIRGui.Views.View3DManager import View3DManager
from MJOLNIRGui.Views.TimeEstimateManager import ScanListManager
from MJOLNIRGui.Views.CalculatorManager import CalculatorManager
from MJOLNIRGui.Views.CalculatorGeneralManager import CalculatorGeneralManager
from MJOLNIRGui.Views.ElectronicLogBookManager import ElectronicLogBookManager
from MJOLNIRGui.Views.MolecularCalculationManager import MolecularCalculationManager
from MJOLNIRGui.Views.NormalizationManager import NormalizationManager
from MJOLNIRGui.Views.PredictionToolManager import PredictionToolManager
from MJOLNIRGui.Views.SubtractionManager import SubtractionManager
from MJOLNIRGui.Views.MaskManager import MaskManager



@pytest.mark.gui
@pytest.mark.qt5
@pytest.mark.parametrize("manager", [
    BraggListManager,
    CalculatorAdvancedManager,
    CalculatorSimpleManager,
    ScanListManager,
])
def test_manager_construction_simple(qapp, manager):
    widget = manager()
    assert widget is not None
    widget.deleteLater()


@pytest.mark.gui
@pytest.mark.qt5
@pytest.mark.parametrize("manager", [
    Cut1DManager,
    DataSetManager,
    QELineManager,
    QPlaneManager,
    Raw1DManager,
    View3DManager,
])
def test_manager_construction(qapp, manager, gui_window):
    context, gui_window = gui_window
    _manager = manager(guiWindow=gui_window)

    assert _manager is not None
    _manager.deleteLater()


@pytest.mark.gui
@pytest.mark.qt5
@pytest.mark.parametrize("manager", [
    CalculatorManager,
    CalculatorGeneralManager,
    ElectronicLogBookManager,
    MolecularCalculationManager,
    NormalizationManager,
    PredictionToolManager,
    SubtractionManager,
])
def test_manager_construction_dependent(gui_window, manager):
    context, window = gui_window

    widget = manager(guiWindow=window)

    assert widget is not None
    widget.deleteLater()

@pytest.mark.gui
@pytest.mark.qt5
def test_mask_manager(gui_window):
    context, window = gui_window

    manager = MaskManager(parent=window)

    assert manager is not None

    manager.deleteLater()