#FLM: GrabLab: Screengrab on Save
from fontlabapp import *
from grablab import Grab

app.ui.menu.file.save_font.qaction.triggered.connect(
    lambda checked=False: Grab().grabAll()  # triggered(bool) passes `checked`
)
