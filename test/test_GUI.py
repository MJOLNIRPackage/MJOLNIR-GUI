from pathlib import Path
import pytest
from MJOLNIRGui._qt import uic

@pytest.mark.gui
def test_import():
    import MJOLNIRGui
    from MJOLNIRGui import MJOLNIR_GUI

import MJOLNIRGui

@pytest.mark.qt5
@pytest.mark.gui
def test_ui_files_load():
    view_dir = Path(MJOLNIRGui.__file__).parent / "Views"
    print(f"Testing UI files in {view_dir}")
    for ui_file in view_dir.glob("*.ui"):
        print(str(ui_file))
        base, form = uic.loadUiType(str(ui_file))
        assert base is not None
        assert form is not None
