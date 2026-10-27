"""Validate the published navigation graph and overlapping reader collections."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
def document(path):return html.fromstring((ROOT/path).read_text())

class SiteExperience(unittest.TestCase):
    def test_missing_page_has_clear_recovery_and_is_not_indexed(self):
        doc=document('404.html')
        self.assertEqual(len(doc.xpath('//*[@data-site-header]')),1)
        self.assertEqual(len(doc.xpath('//*[@data-site-footer]')),1)
        self.assertTrue(doc.xpath('//meta[@name="robots" and @content="noindex"]'))
        self.assertTrue(doc.xpath('//main//a[@href="/library.html#library-search"]'))
        self.assertNotIn('/404.html',{r['url'] for r in json.loads((ROOT/'data/page-directory.json').read_text())})

    def test_every_canonical_page_is_in_library_and_sitemap(self):
        rows=json.loads((ROOT/'data/page-directory.json').read_text())
        urls={row['url'] for row in rows}
        self.assertEqual(len(urls),len(rows))
        library=document('library.html')
        self.assertEqual(set(library.xpath('//*[@id="library-results"]//article/@data-url')),urls)
        sitemap=document('site-map.html')
        self.assertTrue((urls-{'/site-map.html'}).issubset(set(sitemap.xpath('//main//a/@href'))))
        for row in rows:
            doc=document(row['path'])
            self.assertEqual(len(doc.xpath('//*[@data-site-header]')),1,row['url'])
            self.assertEqual(len(doc.xpath('//*[@data-site-footer]')),1,row['url'])
            self.assertEqual(len(doc.xpath('//h1')),1,row['url'])
            self.assertFalse(doc.xpath('//header[@data-site-header]//a[contains(@href,"/media/")]'))
            self.assertEqual(len(doc.xpath('//*[@id]/@id')),len(set(doc.xpath('//*[@id]/@id'))),row['url'])

    def test_categories_are_multiple_and_linked_from_stories(self):
        config=json.loads((ROOT/'data/journal-taxonomy.json').read_text())
        rows={r['url']:r for r in json.loads((ROOT/'data/page-directory.json').read_text())}
        self.assertIn('self-care',config['entries']['/menauhant-beach-the-art-of-letting-go.html']['topics'])
        self.assertIn('photo-essays',config['entries']['/menauhant-beach-the-art-of-letting-go.html']['formats'])
        self.assertIn('reflections',config['entries']['/menauhant-beach-the-art-of-letting-go.html']['formats'])
        for url,item in config['entries'].items():
            self.assertIn(url,rows)
            self.assertTrue(set(item['topics']).issubset(config['topics']))
            self.assertTrue(set(item['formats']).issubset(config['formats']))
            doc=document(rows[url]['path'])
            self.assertEqual(len(doc.xpath('//nav[@data-article-collection="journal"]')),1,url)
        doc=document('blog.html');cards=doc.xpath('//ol[@class="journal-recent-list"]/li')
        self.assertEqual(len(cards),len(config['entries']))
        self.assertEqual([c.get('data-url') for c in cards[:3]],['/wayne-newton-flamingo-bucket-list-self-care.html','/get-in-the-photograph.html','/rangeley-grandparents-field-note.html'])
        self.assertTrue(all(not c.get('hidden') for c in cards),'No-JS readers can access every story')

    def test_caregiver_roles_and_needs_are_independent(self):
        config=json.loads((ROOT/'data/caregiver-taxonomy.json').read_text())
        self.assertEqual(config['entries']['/grandparent-role.html']['roles'],['grandparents'])
        self.assertEqual(config['entries']['/caregiver-handover-guide.html']['roles'],[])
        self.assertIn('shared-care',config['entries']['/caregiver-handover-guide.html']['topics'])
        doc=document('family-roles.html')
        self.assertEqual(len(doc.xpath('//*[@data-collection="support"]')),1)
        self.assertEqual(len(doc.xpath('//*[@data-collection-card]')),len(config['entries']))
        for anchor in ['choose','practical','caregiver-time','principles','others','handover','prompt']:
            self.assertEqual(len(doc.xpath('//*[@id=$id]',id=anchor)),1)

    def test_michaels_stories_have_distinct_journal_and_caregiver_routes(self):
        journal=json.loads((ROOT/'data/journal-taxonomy.json').read_text())
        care=json.loads((ROOT/'data/caregiver-taxonomy.json').read_text())
        food='/kohinoor-indian-restaurant-mashpee.html'
        beach='/menauhant-beach-the-art-of-letting-go.html'
        for url in [food,beach]:
            self.assertIn('paternal-insights',journal['entries'][url]['topics'])
            self.assertIn('places',journal['entries'][url]['topics'])
            self.assertEqual(care['entries'][url]['roles'],['fathers'])
            self.assertIn('paternal-insights',care['entries'][url]['topics'])
            self.assertIn('outings',care['entries'][url]['topics'])
            for page in ['blog.html','family-roles.html']:
                cards=document(page).xpath('//*[@data-collection-card and @data-url=$url]',url=url)
                self.assertEqual(len(cards),1)
                self.assertIn('Michael, James’s dad',cards[0].text_content())
            self.assertTrue(document('paternal-role.html').xpath('//*[@id="paternal-insights"]//a[@href=$url]',url=url))
        self.assertIn('ausome-heat',journal['entries'][food]['topics'])
        self.assertIn('food',journal['entries'][food]['topics'])
        self.assertNotIn('ausome-heat',journal['entries'][beach]['topics'])
        self.assertNotIn('food',journal['entries'][beach]['topics'])
        self.assertIn('nature',journal['entries'][beach]['topics'])
        self.assertIn('reflections',journal['entries'][beach]['formats'])
        self.assertNotIn('paternal-insights',journal['entries']['/what-i-understood-at-the-beach.html']['topics'])

    def test_michaels_places_are_in_the_existing_directory_and_search(self):
        places={row['url']:row for row in json.loads((ROOT/'data/places.json').read_text())}
        search={row['url']:row for row in json.loads((ROOT/'data/site-index.json').read_text())}
        doc=document('favorite-places.html')
        for url,kind in [('/kohinoor-indian-restaurant-mashpee.html','food'),('/menauhant-beach-the-art-of-letting-go.html','outdoors')]:
            self.assertIn('Cape Cod',places[url]['location'])
            rows=doc.xpath('//*[@data-place-kind][.//h2/a[@href=$url]]',url=url)
            self.assertEqual(len(rows),1)
            self.assertIn(kind,rows[0].get('data-place-kind').split())
            self.assertIn('Paternal insights',search[url]['search'])
            self.assertIn('Michael, James’s dad',search[url]['search'])

    def test_all_navigation_targets_and_art_exist(self):
        config=json.loads((ROOT/'data/site-structure.json').read_text())
        for chapter in config['chapters']:
            for label,url,art in chapter['links']:
                u=urlsplit(url);target=ROOT/u.path.lstrip('/')
                if target.is_dir():target/='index.html'
                self.assertTrue(target.is_file(),url)
                if u.fragment:self.assertTrue(html.fromstring(target.read_text()).xpath('//*[@id=$id]',id=u.fragment),url)
                self.assertTrue((ROOT/'assets/navigation-watercolors'/f'{art}-128.webp').is_file())

if __name__=='__main__':unittest.main()
