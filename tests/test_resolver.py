import base64
import json
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup
from resolver import Client, known_wrapper, link_record, parse_options

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests' / 'fixtures'

class ResolverTests(unittest.TestCase):
    def test_spider_real_editions(self):
        r = parse_options((FIXTURES/'spider.html').read_text(encoding='utf-8'), 'https://dlpsgame.com/marvels-spider-man-ps4-pkg/')
        self.assertEqual(len(r['options']), 7)
        first = r['options'][0]
        self.assertEqual(first['cusa'], ['CUSA11993'])
        self.assertEqual(first['version'], '1.19')
        self.assertEqual(first['components'][0]['links'][0]['url'], 'https://downloadgameps3.net/archives/19078')
        self.assertEqual(r['options'][3]['edition'], 'CUSA11995 – EUR (v1.17)')
        urls=[l['url'] for o in r['options'] for c in o['components'] for l in c['links']]
        self.assertFalse(any('/18667' in u or '/38700' in u or '/38600' in u for u in urls))

    def test_ragnarok_real_editions(self):
        r = parse_options((FIXTURES/'ragnarok.html').read_text(encoding='utf-8'), 'https://dlpsgame.com/god-of-war-ragnarok-ps4-pkg/')
        self.assertEqual(len(r['options']), 6)
        self.assertEqual(r['options'][0]['cusa'], ['CUSA34386'])
        self.assertEqual(r['options'][0]['components'][0]['links'][0]['url'], 'https://downloadgameps3.net/archives/22662')

    def test_wrapper_and_invalid_payload(self):
        target='https://downloadgameps3.net/archives/19078'
        encoded=base64.b64encode(target.encode()).decode()
        self.assertEqual(known_wrapper('https://clk.sh/full?url='+encoded)[0], target)
        self.assertIsNone(known_wrapper('https://clk.sh/full?url=INVALIDO')[1])
        h='<div class="su-spoiler"><div class="su-spoiler-title">Link Download</div><div class="secure-data" data-payload="???"></div></div>'
        option=parse_options(h,'https://example.com/')['options'][0]
        self.assertTrue(option['evidence']['errors'])
        self.assertEqual(option['components'], [])

    def test_parts_are_explicit_not_guessed(self):
        html='<p><a href="https://mediafire.com/file/x/game.part02.rar">Part 02</a><a href="https://mediafire.com/file/y/game.part01.rar">Part 01</a><a href="https://1fichier.com/?opaque">1File</a></p>'
        s=BeautifulSoup(html,'html.parser')
        self.assertEqual([link_record(a,'https://example.com/')['part'] for a in s.select('a')], [2,1,None])

    def test_redirects_and_captcha(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=Client(cache=tmp,max_redirects=2)
            c.one=lambda u:dict(url=u,status=302,location=u,body='',cached=False,fetched_at=0)
            self.assertIn('Loop',c.trace('https://example.com/a')['error'])
            c.one=lambda u:dict(url=u,status=302,location=u+'a',body='',cached=False,fetched_at=0)
            self.assertIn('Limite',c.trace('https://example.com/a')['error'])
            c.one=lambda u:dict(url=u,status=200,location=None,body='<p>Please click on below captcha box to proceed.</p>',cached=False,fetched_at=0)
            self.assertIn('CAPTCHA',c.trace('https://example.com/a')['error'])

    def test_no_hosting_request_or_conditional_js_guess(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=Client(cache=tmp)
            c.one=lambda u:self.fail('Uma hospedagem foi requisitada')
            self.assertIn('stopped',c.trace('https://1fichier.com/?abc'))
            c.one=lambda u:dict(url=u,status=200,location=None,body='<script>if(false){location="https://example.com/b";}</script>',cached=False,fetched_at=0)
            self.assertEqual(c.trace('https://example.com/a')['final_url'], 'https://example.com/a')

    def test_manifest_versions_and_portability(self):
        m=json.loads((ROOT/'downloads-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(m['platform'],'windows-x64')
        self.assertEqual(len([i for i in m['files'] if i['kind']=='python']),1)
        for i in m['files']:
            self.assertRegex(i['sha256'],r'^[0-9a-f]{64}$')
            self.assertGreater(i['size'],0)
            self.assertEqual(Path(i['filename']).name,i['filename'])
            if i['kind']=='wheel':self.assertTrue(i['filename'].endswith('-none-any.whl'))

if __name__ == '__main__':unittest.main(verbosity=2)
