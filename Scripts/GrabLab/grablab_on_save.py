#FLM: GrabLab: Screengrab on Save
# this_file: Scripts/GrabLab/grablab_on_save.py
from fly.ap import *
from grablab import Grab

app.ui.menu.file.save_font.qaction.triggered.connect(
    lambda checked=False: Grab().grabAll()  # triggered(bool) passes `checked`
)
