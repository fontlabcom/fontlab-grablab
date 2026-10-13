# this_file: examples/native_smoke.py
"""Run inside FontLab against installed packages; clean temporary capture files."""
from pathlib import Path
from tempfile import TemporaryDirectory
from fontlabapp import Application
from fontlabapp.application.preflib import PrefLib
from grablab import Grab
from PythonQt import QtGui

app = Application(with_ui=True, with_preflib=False)
widget = QtGui.QWidget()
try:
    with TemporaryDirectory() as directory:
        app.paths.appPrefLibPath = Path(directory) / 'prefs.json'
        app.preflib = PrefLib(app)
        capture = Grab(application=app, folder_base=Path(directory))
        capture.newGrab()
        widget.resize(80, 60)
        paths = capture.grabWidget(widget, 'test', 'hidden', 'Smoke widget')
        assert len(paths) == 2 and all(path.is_file() for path in paths)
        print('Native PNG and SVG passed')
finally:
    widget.deleteLater()
