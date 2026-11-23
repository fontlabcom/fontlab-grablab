# this_file: tests_docs/test_site.py
"""Check the actual generated payload, routes and public source boundaries."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs'
PREFIX = '/fontlab-grablab/'
PAGES = ['index.html', 'installation/index.html', 'capture-bundles/index.html', 'svg-and-icons/index.html', 'development-and-limits/index.html', 'licence/index.html']


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.links = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])

    def handle_data(self, data):
        self.text.append(data)


class SiteTests(unittest.TestCase):
    def test_all_generated_internal_links_and_fragments_resolve(self):
        for path in SITE.rglob('*.html'):
            for link in Page(path.read_text()).links:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = unquote(url.path)
                if target.startswith('/'):
                    self.assertTrue(target.startswith(PREFIX), (path, link))
                    dest = SITE / target.removeprefix(PREFIX)
                else:
                    dest = path.parent / target if target else path
                if dest.is_dir():
                    dest = dest / 'index.html'
                self.assertTrue(dest.is_file(), (path, link, dest))
                self.assertTrue(dest.resolve().is_relative_to(SITE.resolve()), link)
                if url.fragment and dest.suffix == '.html':
                    self.assertIn(unquote(url.fragment), Page(dest.read_text()).ids, (path, link))

    def test_pages_have_fly_assets_fontlab_chrome_local_search_and_correct_canonical(self):
        for route in PAGES:
            page = Page((SITE / route).read_text())
            with self.subTest(route=route):
                asset_paths = [urlsplit(link).path for link in page.links]
                for asset in ('fly.css', 'fly-bridge.js', 'fly.js'):
                    self.assertTrue(any(path.endswith('assets/fly/' + asset) for path in asset_paths), asset)
                menus = [attrs for tag, attrs in page.tags if tag == 'fontlab-menu']
                self.assertEqual(len(menus), 1)
                self.assertEqual(menus[0].get('site-label'), 'GrabLab')
                self.assertEqual(menus[0].get('mobile-menu'), 'materialx')
                self.assertEqual(menus[0].get('mobile-search'), 'materialx')
                self.assertEqual(sum(tag == 'fontlab-footer' for tag, _ in page.tags), 1)
                self.assertEqual([attrs.get('data-md-color-scheme') for tag, attrs in page.tags if tag == 'body'], ['default'])
                search = [attrs for tag, attrs in page.tags if attrs.get('data-md-component') == 'search-query']
                self.assertEqual(len(search), 1)
                self.assertFalse(any(attrs.get('data-md-component') == 'palette' for _, attrs in page.tags))
                canonical = [attrs['href'] for tag, attrs in page.tags if attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, ['https://fontlabcom.github.io/fontlab-grablab/' + route.removesuffix('index.html')])

    def test_search_indexes_every_authored_page(self):
        search = json.loads((SITE / 'search/search_index.json').read_text())
        locations = {row['location'].split('#')[0] for row in search['docs']}
        self.assertEqual(locations, {'', 'svg-and-icons/', 'development-and-limits/', 'licence/', 'installation/', 'capture-bundles/'})
        text = ' '.join(row['text'] for row in search['docs'])
        for term in ('base64', 'png-url', 'svg-url', 'inline-svg'):
            self.assertIn(term, text)

    def test_attribution_downloads_are_exact_and_no_private_payload_is_published(self):
        for name in ('LICENSE',):
            self.assertEqual((ROOT / name).read_bytes(), (SITE / 'assets' / name).read_bytes())
        self.assertTrue((SITE / '.nojekyll').is_file())
        private_markers = (b'/Users/', b'/Volumes/', b'/private/', b'ghp_', b'github_pat_', b'-----BEGIN PRIVATE KEY-----')
        sources = [path.read_bytes() for folder in ('src', 'Scripts', 'glyphs', 'examples') if (ROOT / folder).is_dir() for path in (ROOT / folder).rglob('*.py')]
        for path in SITE.rglob('*'):
            if path.is_file():
                self.assertNotIn('.DS_Store', path.parts)
                self.assertNotIn(path.suffix, ('.py', '.pyi', '.vfpy', '.whl', '.zip'))
                payload = path.read_bytes()
                for marker in private_markers:
                    self.assertFalse(marker in payload, (path, marker))
                for source in sources:
                    if len(source) > 80:
                        self.assertFalse(source in payload, path)

    def test_workflow_builds_every_main_push_and_requalifies_immutable_output(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/docs.yml').read_text())
        events = workflow.get('on', workflow.get(True))
        self.assertEqual(events['push'], {'branches': ['main']})
        self.assertNotIn('concurrency', workflow)
        build = workflow['jobs']['build']
        verify = workflow['jobs']['qualify-generated-output']
        self.assertNotIn('concurrency', build)
        self.assertEqual(verify['needs'], 'build')
        self.assertEqual(build['outputs']['epoch'], '${{ steps.epoch.outputs.value }}')
        for job, epoch in ((build, '${{ steps.epoch.outputs.value }}'), (verify, '${{ needs.build.outputs.epoch }}')):
            build_step = next(s for s in job['steps'] if s.get('run') == 'sh src_docs/build.sh')
            self.assertEqual(build_step['env']['SOURCE_DATE_EPOCH'], epoch)
        self.assertEqual(verify['steps'][0]['with']['ref'], '${{ needs.build.outputs.sha }}')
        self.assertEqual(verify['permissions'], {'contents': 'read'})
        for job in (build, verify):
            runs = '\n'.join(step.get('run', '') for step in job['steps'])
            self.assertIn('sh src_docs/build.sh', runs)
            self.assertIn('--require-hashes -r src_docs/requirements.txt', runs)
        self.assertIn('git diff --exit-code HEAD -- docs', '\n'.join(s.get('run', '') for s in verify['steps']))
        self.assertIn('git ls-files --others -- docs', '\n'.join(s.get('run', '') for s in verify['steps']))
        self.assertFalse(any('publish.sh' in s.get('run', '') for s in verify['steps']))

    def test_private_pages_hold_removes_automatic_request_and_permission(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/docs.yml').read_text())
        self.assertNotIn('pages', workflow['permissions'])
        for name, job in workflow['jobs'].items():
            with self.subTest(job=name):
                self.assertNotIn('pages', job['permissions'])
                commands = '\n'.join(step.get('run', '') for step in job['steps'])
                self.assertNotIn('request-pages.sh', commands)
                self.assertNotIn('/pages/builds', commands)

    def test_complete_normative_readme_contract_and_catalogue_are_preserved(self):
        def canonical(text):
            text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
            text = text.replace('`', '')
            return re.sub(r'\s+', ' ', text).strip()
        readme = (ROOT / 'README.md').read_text()
        body = readme.split('# GrabLab\n', 1)[1]
        authored = '\n'.join(path.read_text() for path in (ROOT / 'src_docs/md').glob('*.md'))
        combined = canonical(authored)
        for section in re.split(r'(?m)^(?=## )', body):
            if section.strip():
                self.assertIn(canonical(section), combined, 'Complete normative README section must survive')
        scripts = sorted((ROOT / 'Scripts/GrabLab').glob('*.py'))
        self.assertEqual([path.name for path in scripts], ['grablab_menu.py', 'grablab_now.py', 'grablab_on_f5_mac.py', 'grablab_on_save.py'])
        installation = (ROOT / 'src_docs/md/installation.md').read_text()
        rendered = re.sub(r'\s+', ' ', ' '.join(Page((SITE / 'installation/index.html').read_text()).text))
        for path in scripts:
            with self.subTest(script=path.name):
                with path.open() as source:
                    header = source.readline().rstrip('\n')
                self.assertTrue(header.startswith('#FLM:'), 'A current script must declare its public menu label')
                label = header.removeprefix('#FLM:').strip()
                self.assertTrue(label, 'A missing public menu label must fail the catalogue check')
                relative = str(path.relative_to(ROOT))
                escaped = label.replace('|', '\\|')
                self.assertIn(f'| `{relative}` | {escaped} |', installation)
                self.assertIn(f'{relative} {label}', rendered)
        with self.subTest(contract='catalogue header'):
            self.assertIn('| Script | Public #FLM menu label |', installation)
        with self.subTest(contract='G2 uv resolution and retained no-uv limitation'):
            development = (ROOT / 'src_docs/md/development-and-limits.md').read_text()
            self.assertIn('The source installer now delegates the complete declared requirements to uv, including versions, markers and extras; the no-uv fallback remains presence-only.', development)
        a = (ROOT / 'src/grablab/grab.py').read_bytes().split(b'# Copyright', 1)[1].split(b'\n\n', 1)[0]
        self.assertEqual((SITE / 'assets/BSD-3-Clause-NOTICE.txt').read_bytes(), b'# Copyright' + a + b'\n')
