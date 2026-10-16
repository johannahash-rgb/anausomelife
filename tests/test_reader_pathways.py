"""Check reader routes against actual pages, assets and existing page behavior."""
import importlib.util
import json
from pathlib import Path
import unittest
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pathways',ROOT/'.github/scripts/reader_pathways.py')
pathways=importlib.util.module_from_spec(spec);spec.loader.exec_module(pathways)
CATEGORIES={row['url']:row.get('category','') for row in json.loads((ROOT/'data/library.json').read_text())}

def publish(name):
    return pathways.apply_to_page((ROOT/name).read_text(),name,CATEGORIES)

def with_class(doc,name):
    return doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," '+name+' ")]')

class ReadingPaths(unittest.TestCase):
    def test_recommendations_exist_and_never_point_back_to_current_page(self):
        for item in pathways.CARDS.values():
            for key in ('url','image'):
                target=ROOT/item[key].lstrip('/')
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.is_file(),item[key])
        for page in ROOT.rglob('*.html'):
            relative=page.relative_to(ROOT).as_posix()
            if any(part.startswith('.') or part in {'docs','assets','content','tests'} for part in page.parts):continue
            group=pathways.group_for(relative,CATEGORIES)
            urls=[row['url'] for row in pathways.selected_cards(relative,group)]
            self.assertEqual(len(urls),len(set(urls)),relative)
            self.assertNotIn(pathways.page_url(relative),urls,relative)

    def test_role_guides_lead_to_relevant_real_stories_and_support(self):
        cases={'maternal-role.html':'/get-in-the-photograph.html',
               'grandparent-role.html':'/rangeley-grandparents-field-note.html',
               'respite-partner-role.html':'/wayne-newton-flamingo-bucket-list-self-care.html',
               'family-planning-toolkit.html':'/october-ice-cream-dairy-joy-weston.html'}
        for name,story in cases.items():
            doc=html.fromstring(publish(name));links=with_class(doc,'reader-next-card')
            self.assertEqual(len(links),3,name)
            self.assertEqual(links[0].get('href'),story,name)
            self.assertIn('/family-roles.html',with_class(doc,'reader-exits')[0].xpath('.//a/@href'))
            self.assertFalse(with_class(doc,'er-related'),name)

    def test_handpicked_recommendations_are_kept_without_a_second_card_grid(self):
        for name in ('favorite-places/book-barn-niantic.html','guides/prepare-for-an-iep-meeting.html','october-ice-cream-dairy-joy-weston.html'):
            before=html.fromstring((ROOT/name).read_text());after=html.fromstring(publish(name))
            old=[e for e in before.iter() if pathways.has_class(e,pathways.RELATED)]
            new=[e for e in after.iter() if pathways.has_class(e,pathways.RELATED)]
            self.assertEqual([e.text_content() for e in old],[e.text_content() for e in new])
            self.assertEqual([e.xpath('.//a/@href') for e in old],[e.xpath('.//a/@href') for e in new])
            self.assertFalse(with_class(after,'reader-next-card'))
            self.assertEqual(len(with_class(after,'reader-exits')),1)

    def test_forms_scripts_and_existing_fragment_destinations_survive(self):
        for name in ('maternal-role.html','family-planning-toolkit.html','communication-card-generator.html','visit-story.html','energy-is-an-access-resource.html'):
            before=html.fromstring((ROOT/name).read_text());after=html.fromstring(publish(name))
            self.assertTrue(set(before.xpath('//*[@id]/@id')).issubset(after.xpath('//*[@id]/@id')),name)
            for selector in ('//input','//textarea','//select','//button','//script'):
                def elements(doc):
                    return [(dict(e.attrib),e.text) for e in doc.xpath(selector)]
                self.assertEqual(elements(before),elements(after),(name,selector))

    def test_repeated_publication_is_stable(self):
        for name in ('family-roles.html','maternal-role.html','guides/prepare-for-an-iep-meeting.html','family-planning-toolkit.html','media/index.html'):
            once=publish(name);twice=pathways.apply_to_page(once,name,CATEGORIES)
            self.assertEqual(once,twice,name)
            doc=html.fromstring(twice)
            self.assertEqual(len(with_class(doc,'reader-next')),1,name)
            self.assertEqual(len(doc.xpath('//link[contains(@href,"reader-pathways.css")]')),1,name)

    def test_policies_and_nonreader_documents_stay_focused(self):
        self.assertFalse(with_class(html.fromstring(publish('privacy.html')),'reader-next'))
        source='<html><head><script src="/assets/global-nav.js"></script></head><body><main><h1>Print sheet</h1></main></body></html>'
        for name in ('index.html','downloads/sheet.html','content/home-entrance.html'):
            self.assertEqual(pathways.apply_to_page(source,name,{}),source)
        for meta in ('<meta name="robots" content="noindex">','<meta http-equiv="Refresh" content="0;url=/">'):
            page=source.replace('<head>','<head>'+meta)
            self.assertEqual(pathways.apply_to_page(page,'preview.html',{}),page)

    def test_hub_preserves_known_anchors_and_starts_with_tasks(self):
        doc=html.fromstring((ROOT/'family-roles.html').read_text())
        ids=doc.xpath('//*[@id]/@id')
        for anchor in ('choose','paternal','principles','others','handover','caregiver-time','prompt'):
            self.assertIn(anchor,ids)
        self.assertEqual(len(ids),len(set(ids)))
        self.assertLess(ids.index('practical'),ids.index('choose'))
        self.assertLess(ids.index('caregiver-time'),ids.index('choose'))
        self.assertEqual(doc.xpath('//h1/text()'),['Family & caregiver support'])

if __name__=='__main__':unittest.main()
