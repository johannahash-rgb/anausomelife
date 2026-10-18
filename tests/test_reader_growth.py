"""Evidence, generated-page and feed regressions; not an accessibility certification."""
import hashlib, importlib.util, re, shutil, tempfile, unittest
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('reader_growth',ROOT/'.github/scripts/reader_growth.py')
growth=importlib.util.module_from_spec(spec);spec.loader.exec_module(growth)

def doc(root,name):return html.fromstring((root/name).read_text())

class ReaderGrowth(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
  paths={'contact.html','blog.html','privacy.html','media/index.html','product-guides.html','sitemap.xml','assets/global-nav.js',*growth.SUMMARIES}
  for href in doc(ROOT,'blog.html').xpath('//ol[contains(@class,"journal-recent-list")]/li//a/@href'):
   p=urlsplit(href).path
   if p.startswith('/') and p.endswith('.html'):paths.add(p.lstrip('/'))
  for name in paths:
   p=cls.root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
  cls.before={name:doc(cls.root,name).xpath('//main//img/@src') for name in growth.SUMMARIES}
  growth.prepare(cls.root)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_three_distinct_evidence_summaries(self):
  for name,info in growth.SUMMARIES.items():
   d=doc(self.root,name);summary=d.xpath('//*[@id="review-summary"]')
   self.assertEqual(len(summary),1)
   self.assertIn(info['kind'],summary[0].text_content())
   self.assertEqual(len(summary[0].xpath('.//dl/div')),3)
   self.assertEqual(d.xpath('//main//img/@src'),self.before[name])
   self.assertFalse(d.xpath('//*[@itemprop="ratingValue"]'))
 def test_no_fabricated_newsletter_or_star_reviews(self):
  d=doc(self.root,'follow.html')
  self.assertFalse(d.xpath('//form|//input[@type="email"]'))
  self.assertEqual(d.xpath('//*[@id="journal-feed-address"]/@value'),[growth.BASE+'/feed.xml'])
  self.assertTrue(d.xpath('//*[@id="copy-journal-feed"][@hidden]'))
  self.assertIn('not automatically a recommendation',doc(self.root,'reviews.html').text_content())
 def test_valid_feed_and_stable_permalinks(self):
  rss=ET.parse(self.root/'feed.xml');items=rss.findall('./channel/item')
  self.assertGreaterEqual(len(items),3)
  self.assertEqual(len({i.findtext('guid') for i in items}),len(items))
  for item in items:
   self.assertEqual(item.findtext('link'),item.findtext('guid'))
   self.assertTrue(item.findtext('link').startswith(growth.BASE+'/'))
   self.assertTrue(item.findtext('title'));self.assertTrue(item.findtext('description'))
   self.assertIsNone(item.find('pubDate'))
  pins=['wayne-newton-flamingo-bucket-list-self-care.html','get-in-the-photograph.html','rangeley-grandparents-field-note.html']
  self.assertEqual([i.findtext('link') for i in items[:3]],[growth.BASE+'/'+p for p in pins])
 def test_idempotent_complete_build(self):
  digest=lambda:{p.relative_to(self.root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
  before=digest();growth.prepare(self.root);self.assertEqual(before,digest())
 def test_new_pages_have_one_heading_unique_ids_and_no_media_topnav(self):
  for name in ['reviews.html','follow.html']:
   d=doc(self.root,name);ids=d.xpath('//*[@id]/@id')
   self.assertEqual(len(ids),len(set(ids)))
   self.assertEqual(len(d.xpath('//h1')),1)
   self.assertFalse(d.xpath('//header//a[contains(@href,"/media/")]'))
   self.assertEqual(len(d.xpath('//link[@type="application/rss+xml"]')),1)
   self.assertTrue(d.xpath('//footer//a[@href="/follow.html"]'))
   for src in d.xpath('//img/@src'):
    self.assertTrue((ROOT/src.lstrip('/')).exists(),src)
 def test_summary_links_and_new_routes_resolve(self):
  for name in ['reviews.html','follow.html',*growth.SUMMARIES]:
   for href in doc(self.root,name).xpath('//main//a/@href'):
    u=urlsplit(href)
    if u.scheme or u.netloc:continue
    rel=u.path.lstrip('/') if u.path else name
    p=self.root/rel
    if p.is_dir():p/='index.html'
    if not p.exists():
     p=ROOT/rel
     if p.is_dir():p/='index.html'
    self.assertTrue(p.exists(),href)
    if u.fragment and p.suffix=='.html':
     # Media growth anchors are inserted by the earlier existing publication stage.
     if rel in {'media/index.html','media/'} and u.fragment=='products':continue
     self.assertTrue(html.fromstring(p.read_text()).xpath('//*[@id=$id]',id=u.fragment),href)
 def test_missing_evidence_fails_before_publishing(self):
  name=next(iter(growth.SUMMARIES));p=self.root/name;source=p.read_text()
  try:
   p.write_text(source.replace(growth.SUMMARIES[name]['evidence'][0],'REMOVED EVIDENCE'))
   with self.assertRaisesRegex(ValueError,'Recheck review evidence'):growth.prepare(self.root)
  finally:p.write_text(source)
 def test_sitemap_and_privacy_controls(self):
  locs=[x.text for x in ET.parse(self.root/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
  for path in ['reviews.html','follow.html']:self.assertEqual(locs.count(growth.BASE+'/'+path),1)
  d=doc(self.root,'privacy.html');self.assertTrue(d.xpath('//*[@id="measurement-controls"][@hidden]'))
  self.assertIn('not currently enabled',d.xpath('//*[@id="measurement-state"]')[0].text_content())

if __name__=='__main__':unittest.main()
