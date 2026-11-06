#FLM: GrabLab: Screengrab Main Menu
import importlib
import grablab
importlib.reload(grablab)

grab = grablab.Grab()
grab.newGrab()
grabbed = grab.grabMainMenu()
