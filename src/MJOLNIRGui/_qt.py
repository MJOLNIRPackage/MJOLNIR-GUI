try:
    from PyQt6 import QtCore, QtGui, QtWidgets, uic
    Qt = QtCore.Qt

    Qt.EditRole                    = Qt.ItemDataRole.EditRole
    Qt.DisplayRole                 = Qt.ItemDataRole.DisplayRole
    Qt.DecorationRole              = Qt.ItemDataRole.DecorationRole

    Qt.ItemIsEditable              = Qt.ItemFlag.ItemIsEditable
    Qt.ItemIsEnabled               = Qt.ItemFlag.ItemIsEnabled
    Qt.ItemIsSelectable            = Qt.ItemFlag.ItemIsSelectable
    Qt.ItemIsDragEnabled           = Qt.ItemFlag.ItemIsDragEnabled
    Qt.ItemIsDropEnabled           = Qt.ItemFlag.ItemIsDropEnabled
    Qt.NoItemFlags                 = Qt.ItemFlag.NoItemFlags

    Qt.AlignCenter                 = Qt.AlignmentFlag.AlignCenter
    Qt.AlignHCenter                = Qt.AlignmentFlag.AlignHCenter
    Qt.AlignTop                    = Qt.AlignmentFlag.AlignTop

    Qt.DownArrow                  = Qt.ArrowType.DownArrow
    Qt.RightArrow                 = Qt.ArrowType.RightArrow

    Qt.ToolButtonTextBesideIcon   = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

    Qt.Horizontal                 = Qt.Orientation.Horizontal

    Qt.ScrollBarAlwaysOff         = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    Qt.ScrollBarAlwaysOn          = Qt.ScrollBarPolicy.ScrollBarAlwaysOn

    Qt.WindowCloseButtonHint      = Qt.WindowType.WindowCloseButtonHint
    Qt.WindowMinMaxButtonsHint    = Qt.WindowType.WindowMinMaxButtonsHint
    Qt.WindowSystemMenuHint       = Qt.WindowType.WindowSystemMenuHint
    Qt.WindowTitleHint            = Qt.WindowType.WindowTitleHint

    Qt.LinksAccessibleByKeyboard  = Qt.TextInteractionFlag.LinksAccessibleByKeyboard
    Qt.LinksAccessibleByMouse     = Qt.TextInteractionFlag.LinksAccessibleByMouse
    Qt.TextSelectableByKeyboard   = Qt.TextInteractionFlag.TextSelectableByKeyboard
    Qt.TextSelectableByMouse      = Qt.TextInteractionFlag.TextSelectableByMouse

    Qt.MoveAction                 = Qt.DropAction.MoveAction
    Qt.IgnoreAction               = Qt.DropAction.IgnoreAction

    Qt.NoPen                      = Qt.PenStyle.NoPen

    QtWidgets.QSizePolicy.Preferred = QtWidgets.QSizePolicy.Policy.Preferred
    QtWidgets.QSizePolicy.Expanding = QtWidgets.QSizePolicy.Policy.Expanding
    QtWidgets.QSizePolicy.Minimum = QtWidgets.QSizePolicy.Policy.Minimum
    QtWidgets.QSizePolicy.Maximum = QtWidgets.QSizePolicy.Policy.Maximum
    QtWidgets.QSizePolicy.Fixed = QtWidgets.QSizePolicy.Policy.Fixed

    QtWidgets.QLayout.SetNoConstraint = (
        QtWidgets.QLayout.SizeConstraint.SetNoConstraint
    )
    QtWidgets.QAction = QtGui.QAction

    QtWidgets.QAbstractItemView.InternalMove = (
        QtWidgets.QAbstractItemView.DragDropMode.InternalMove
    )


    QtWidgets.QDialogButtonBox.Ok = (
        QtWidgets.QDialogButtonBox.StandardButton.Ok
    )

    QtWidgets.QDialogButtonBox.Cancel = (
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )


    QtWidgets.QMessageBox.Save = (
                QtWidgets.QMessageBox.StandardButton.Save
            )

    QtWidgets.QMessageBox.No = (
                QtWidgets.QMessageBox.StandardButton.No
            )

    QtWidgets.QMessageBox.Yes = (
                QtWidgets.QMessageBox.StandardButton.Yes
            )

    QtWidgets.QMessageBox.Ok = (
                QtWidgets.QMessageBox.StandardButton.Ok
            )

    QtWidgets.QMessageBox.Cancel = (
                QtWidgets.QMessageBox.StandardButton.Cancel
            )

    QtWidgets.QMessageBox.Critical = (
                QtWidgets.QMessageBox.Icon.Critical
            )
    
    
    Qt.WindowContextHelpButtonHint = (
        Qt.WindowType.WindowContextHelpButtonHint
    )
    
    QtWidgets.QShortcut = QtGui.QShortcut
    QtGui.QRegExpValidator = QtGui.QRegularExpressionValidator

    FocusOut = QtCore.QEvent.Type.FocusOut

    Qt.Unchecked = Qt.CheckState.Unchecked
    Qt.PartiallyChecked = Qt.CheckState.PartiallyChecked
    Qt.Checked = Qt.CheckState.Checked

    QtWidgets.QFrame.NoFrame = QtWidgets.QFrame.Shape.NoFrame

    QtCore.QEvent.ContextMenu = QtCore.QEvent.Type.ContextMenu

    QtCore.QAbstractAnimation.Forward = (
        QtCore.QAbstractAnimation.Direction.Forward
    )
    QtCore.QAbstractAnimation.Backward = (
        QtCore.QAbstractAnimation.Direction.Backward
    )

    QT_VERSION = 6
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    from PyQt5.QtCore import Qt

    FocusOut = QtCore.QEvent.FocusOut
    Qt.ItemDataRole = object()

    Qt.Checked = QtCore.Qt.Checked
    Qt.Unchecked = QtCore.Qt.Unchecked
    Qt.PartiallyChecked = QtCore.Qt.PartiallyChecked

    QT_VERSION = 5

QApplication = QtWidgets.QApplication