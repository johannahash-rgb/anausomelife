"""Publish the maintained homepage fragment with its scoped visual layer."""
import argparse
from pathlib import Path

from lxml import etree, html


def prepare(root):
    page = root / 'index.html'
    content = root / 'content/home-entrance.html'
    if not page.exists() or not content.exists():
        return

    doc = html.document_fromstring(page.read_text(encoding='utf-8'))
    main = doc.xpath('//main')[0]
    main.clear()
    main.set('id', 'main')
    for node in html.fragments_fromstring(content.read_text(encoding='utf-8')):
        main.append(node)

    # Keep one scoped visual layer and no competing, automatic story replacement.
    for node in doc.xpath('//link[contains(@href,"/assets/homepage.css")]'):
        node.getparent().remove(node)
    etree.SubElement(
        doc.xpath('//head')[0], 'link', rel='stylesheet',
        href='/assets/homepage.css?v=20261026-home-v1',
    )
    for node in doc.xpath('//script[contains(@src,"/assets/home-dynamic.js")]'):
        node.getparent().remove(node)
    page.write_text(
        html.tostring(doc, encoding='unicode', method='html', doctype='<!doctype html>') + '\n',
        encoding='utf-8',
    )
    print('Prepared the maintained homepage')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    prepare(parser.parse_args().root.resolve())
