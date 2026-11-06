#FLM: GrabLab: Screengrab on F5/F6 Mac

from fontlabapp import *
from grablab import Grab
from fontlabapp.hotkey import HotkeyManager
import os, time

def set_timestamp():
    os.environ["GRABLAB"] = str(time.time())

def get_timestamp():
    return float(os.environ.get("GRABLAB", 0))

def grab_start_all():
    delay = 2
    if get_timestamp() <= time.time() - delay:
        w = app.qapp.activeModalWidget()
        if w:
            grab = Grab()
            grab.newGrab()
            grab.grabWidget(w, "d", w.className().lower())
            grab.grabScreens([0])
        else:
            Grab().grabAll()
        set_timestamp()
    return False

def grab_start_canvas():
    delay = 2
    if get_timestamp() <= time.time() - delay:
        grab = Grab()
        grab.newGrab()
        grab.grabCanvas()
        set_timestamp()
    return False

def grab_stop():
    set_timestamp()
    return False


hotkey = HotkeyManager()
set_timestamp()
hotkey.on("F5", grab_start_all, grab_stop)
hotkey.on("F6", grab_start_canvas, grab_stop)
hotkey.run()
