# this_file: tests/test_capture.py
"""Capture regressions using bounded native surface doubles; host smoke is separate."""
import importlib
import sys
import types
from pathlib import Path

import pytest


@pytest.fixture
def grab(monkeypatch, tmp_path):
    import fontlabapp
    fakefl = types.ModuleType('fontlab')
    fakefl.CurrentFont = lambda: None
    monkeypatch.setitem(sys.modules, 'fontlab', fakefl)
    monkeypatch.setitem(vars(fontlabapp), 'Application', type('Application', (), {}))
    for name, members in {'PythonQt.QtGui': ['QMessageBox', 'QMenu'], 'PythonQt.QtSvg': ['QSvgGenerator'], 'PythonQt.Qt': ['QBuffer']}.items():
        module = types.ModuleType(name)
        for member in members: setattr(module, member, type(member, (), {}))
        monkeypatch.setitem(sys.modules, name, module)
    module = importlib.import_module('grablab.grab')
    instance = module.Grab.__new__(module.Grab)
    instance.app = types.SimpleNamespace(pref=types.SimpleNamespace(developerOpenGL=True, editorOutlineThickness=3, editorFocus=True, generalDarkGlyph=True), ws=types.SimpleNamespace(updateActiveViewport=lambda: None))
    instance.pref = types.SimpleNamespace(naming_prefix='fl_', grab_png=True, grab_svg=False)
    instance.timestamp = 'test'
    instance.grab_suffix = ''
    instance.grab_folder = tmp_path
    instance.dark = ''
    return instance


def test_failed_image_save_does_not_report_existing_file(grab, tmp_path):
    image = types.SimpleNamespace(width=lambda: 2, height=lambda: 3, dotsPerMeterX=lambda: 1, dotsPerMeterY=lambda: 1, devicePixelRatio=lambda: 1, setDotsPerMeterX=lambda value: None, setDotsPerMeterY=lambda value: None, setText=lambda key,value: None, save=lambda path: False)
    path = tmp_path / 'capture.png'
    stale = tmp_path / 'capture_2x3.png'
    stale.write_bytes(b'stale')
    assert grab.getPixmapPNG(types.SimpleNamespace(toImage=lambda: image), path) is None
    assert stale.read_bytes() == b'stale'


def test_many_filename_collisions_do_not_recurse(grab):
    for number in range(1100):
        suffix = '_' + str(number) if number else ''
        (grab.grab_folder / f'fl_name_test{suffix}.png').touch()
    assert grab.getGrabPath('name', 'png').name == 'fl_name_test_1100.png'


def test_nested_menu_returns_all_artifacts(grab, monkeypatch):
    child = types.SimpleNamespace(actions=lambda: [])
    action = types.SimpleNamespace(isVisible=lambda: True, menu=lambda: child, text='Child')
    parent = types.SimpleNamespace(actions=lambda: [action])
    monkeypatch.setattr(grab, 'grabWidget', lambda widget, kind, text, descriptor: [Path(text + '.png')])
    assert grab.grabMenu(parent, 'parent') == [Path('parent.png'), Path('parent_child.png')]


def test_actual_capture_path_restores_preferences_after_exception(grab, monkeypatch):
    before = vars(grab.app.pref).copy()
    def fail(widget, kind, name, descriptor=''):
        assert grab.app.pref.developerOpenGL is False
        assert grab.app.pref.editorOutlineThickness == 1
        grab.app.pref.generalDarkGlyph = False
        raise RuntimeError('save failure')
    monkeypatch.setattr(grab, 'grabWidgetPNG', fail)
    with pytest.raises(RuntimeError, match='save failure'):
        grab.grabWidget(object(), 'test', 'test')
    assert vars(grab.app.pref) == before


def test_alternative_canvas_failure_restores_view_and_dark_preference(grab, monkeypatch):
    state = {'alternative': False}
    def trigger():
        state['alternative'] = not state['alternative']
    grab.app.ui = types.SimpleNamespace(menu=types.SimpleNamespace(view=types.SimpleNamespace(alternative_view=types.SimpleNamespace(trigger=trigger))))
    grab.pref.grab_svg = True
    grab.pref.grab_pdf = False
    before = vars(grab.app.pref).copy()
    def export(path, **kwargs):
        if state['alternative']:
            raise RuntimeError('alternative export failure')
        return path
    monkeypatch.setattr(grab, 'getCanvasSVG', export)
    with pytest.raises(RuntimeError, match='alternative export failure'):
        grab.grabCanvas()
    assert not state['alternative'], 'alternative view toggle must be paired on failure'
    assert vars(grab.app.pref) == before


def test_svg_metadata_is_added_without_existing_elements(grab, tmp_path):
    import xml.etree.ElementTree as ET
    path = tmp_path / 'widget.svg'
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60"><g font-family=".AppleSystemUIFont" stroke-width="1"/></svg>')
    grab.optimizeSVG(path, title='Title', description='Description')
    root = ET.parse(path).getroot()
    assert root.attrib['width'] == '80' and root.attrib['height'] == '60'
    assert root.find('{http://www.w3.org/2000/svg}title').text == 'Title'
    assert root.find('{http://www.w3.org/2000/svg}desc').text == 'Description'
    group = root.find('{http://www.w3.org/2000/svg}g')
    assert group.attrib == {'font-family': 'system-ui', 'stroke-width': '0.75'}
