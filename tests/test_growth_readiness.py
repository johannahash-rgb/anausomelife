#!/usr/bin/env python3
"""Regression tests for public editorial inquiry routes and metadata."""
import importlib.util
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from lxml import html

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('growth',ROOT/'.github/scripts/growth_readiness.py')
growth=importlib.util.module_from_spec(spec);spec.loader.exec_module(growth)

class GrowthReadinessTests(unittest.TestCase):
    def test_owned_blocks_are_idempotent(self):
        source='<main><section id="testing"><h2>Keep this</h2></section></main>'
        output=growth.owned(source,'products',growth.PRODUCTS,growth.before_section('testing'))
        self.assertEqual(output,growth.owned(output,'products',growth.PRODUCTS,growth.before_section('testing')))
        self.assertIn('<h2>Keep this</h2>',output)

    def test_missing_anchor_fails_safely(self):
        with self.assertRaises(ValueError):
            growth.owned('<main></main>','products',growth.PRODUCTS,growth.before_section('testing'))

    def test_metadata_fills_omissions_without_overwriting(self):
        source='<html><head><title>A guide</title><meta name="description" content="A useful guide"><link rel="canonical" href="https://anausomelife.com/example.html"><meta property="og:image" content="https://anausomelife.com/assets/original.webp"></head><body><main></main></body></html>'
        result=growth.add_metadata(source,'example.html')
        doc=html.fromstring(result)
        self.assertEqual(doc.xpath('//meta[@property="og:image"]/@content'),['https://anausomelife.com/assets/original.webp'])
        self.assertEqual(doc.xpath('//meta[@name="twitter:image"]/@content'),['https://anausomelife.com/assets/original.webp'])
        self.assertEqual(result,growth.add_metadata(result,'example.html'))

    def test_noindex_is_not_promoted(self):
        source='<html><head><title>Preview</title><meta name="robots" content="noindex,nofollow"></head><body><main></main></body></html>'
        self.assertEqual(source,growth.add_metadata(source,'preview-example.html'))

    def test_footer_keeps_media_out_of_header(self):
        source='<header><nav><a href="/blog.html">Journal</a></nav></header><footer><nav><a href="/media/">Media Kit &amp; partnerships</a></nav></footer>'
        output=growth.finish_footer(source)
        doc=html.fromstring(output)
        self.assertFalse(doc.xpath('//header//a[contains(@href,"/media/")]'))
        self.assertEqual(len(doc.xpath('//footer//a[@href="/media/#press-desk"]')),1)
        self.assertEqual(output,growth.finish_footer(output))

    def test_contact_is_a_local_draft_not_a_submission(self):
        doc=html.fromstring(growth.CONTACT)
        form=doc.xpath('//form')[0]
        self.assertEqual(form.get('onsubmit'),'return false')
        self.assertIsNone(form.get('action'))
        self.assertEqual(len(doc.xpath('//button[@id="inquiry-prepare"][@type="button"][@hidden]')),1)
        self.assertEqual(len(doc.xpath('//div[@id="inquiry-output"][@hidden]')),1)
        self.assertTrue(doc.xpath('//noscript'))
        for field in doc.xpath('//input|//select|//textarea'):
            self.assertTrue(doc.xpath('//label[@for=$field]',field=field.get('id')))

    def test_no_duplicate_template_ids(self):
        doc=html.fromstring('<main>'+growth.PRODUCTS+growth.PRESS_DESK+growth.CONTACT+'</main>')
        ids=doc.xpath('//*[@id]/@id')
        self.assertEqual(len(ids),len(set(ids)))

    def test_new_internal_destinations_exist(self):
        # Source fixtures may be tested in an overlay, but CI must use a checkout.
        if not (ROOT/'media/index.html').exists():
            self.skipTest('Run this link test against a repository checkout')
        for content in [growth.PRODUCTS,growth.PRESS_DESK,growth.CONTACT,growth.PRESS_CALLOUT,growth.CONTACT_ROUTES,growth.PRODUCT_NOTES]:
            doc=html.fromstring(content)
            for href in doc.xpath('//a/@href'):
                parts=urlsplit(href)
                if parts.scheme or parts.netloc or not parts.path:continue
                path=ROOT/parts.path.lstrip('/')
                if path.is_dir():path/= 'index.html'
                self.assertTrue(path.is_file(),href)

if __name__=='__main__':unittest.main()
