"""Content and behavior contracts for the shared reading simplification."""
import importlib.util
import json
from pathlib import Path
import unittest
from lxml import html
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('simplicity',ROOT/'.github/scripts/page_simplicity.py')
simplicity=importlib.util.module_from_spec(spec);spec.loader.exec_module(simplicity)

def controls(doc):
    return sorted((n.tag,tuple(sorted(n.attrib.items())),n.text or '') for n in doc.xpath('//input|//select|//textarea|//button'))

class ReadingSimplicity(unittest.TestCase):
    def test_every_page_preserves_content_destinations_and_controls(self):
        for row in json.loads((ROOT/'data/page-directory.json').read_text()):
            with self.subTest(page=row['path']):
                doc=html.document_fromstring((ROOT/row['path']).read_text())
                ids=set(doc.xpath('//*[@id]/@id'));before=controls(doc)
                hrefs=set(doc.xpath('//main//a/@href'))
                simplicity.apply(doc,row['path'])
                self.assertTrue(ids.issubset(set(doc.xpath('//*[@id]/@id'))))
                self.assertEqual(len(doc.xpath('//*[@id]/@id')),len(set(doc.xpath('//*[@id]/@id'))))
                self.assertEqual(before,controls(doc))
                self.assertEqual(len(doc.xpath('//main//h1')),1)
                self.assertFalse(doc.xpath('//main//h1/ancestor::details'))
                # A one-link contents bar may be removed; its anchor still exists.
                missing=hrefs-set(doc.xpath('//main//a/@href'))
                self.assertTrue(all(h.startswith('#') and h[1:] in ids for h in missing),missing)

    def test_repeated_simplification_is_stable(self):
        for name in ['at-home.html','caregiver-handover-guide.html','library.html','little-black-book.html','calendar.html','family-planning-toolkit.html','communication-notes.html','picture-card-library.html','blog.html','media/index.html']:
            doc=html.document_fromstring((ROOT/name).read_text());simplicity.apply(doc,name)
            first=html.tostring(doc)
            simplicity.apply(doc,name)
            self.assertEqual(first,html.tostring(doc),name)

    def test_essential_content_is_not_inside_optional_tools(self):
        for name in ['privacy.html','accessibility.html','disclosure.html','contact.html','media/index.html']:
            doc=html.document_fromstring((ROOT/name).read_text());simplicity.apply(doc,name)
            self.assertFalse(doc.xpath('//main//form/ancestor::details[@data-reading-ease]'))
            self.assertFalse(doc.xpath('//*[@id="brands"]/ancestor::details'))
            self.assertTrue(doc.xpath('//main//p[not(ancestor::details)]'))

    def test_replaced_generated_section_leaves_no_empty_disclosure(self):
        doc=html.document_fromstring('<html><head></head><body><main><h1>Story</h1><details data-reading-ease="exits"><summary>More places to explore</summary></details><div class="reader-next reader-next--compact"><a href="/blog.html">Journal</a></div></main></body></html>')
        simplicity.apply(doc,'example.html')
        self.assertEqual(len(doc.xpath('//details[@data-reading-ease="exits"]')),1)
        self.assertTrue(doc.xpath('//details[@data-reading-ease="exits"]//a'))

if __name__=='__main__':unittest.main()
