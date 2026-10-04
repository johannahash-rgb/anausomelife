#!/usr/bin/env python3
"""Keep editorial headlines in one place, without regenerating article content."""
from pathlib import Path
from html import escape, unescape
import re

ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(r'(<h([1-6])\b[^>]*>)(.*?)(</h\2>)', re.S)


def plain(markup):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', markup))).strip()


def key(markup):
    return re.sub(r'\W+', ' ', plain(markup)).strip().casefold()


def clean(source):
    if 'class="ellis-review' not in source:
        return source
    # These lists only restate the headings immediately below them. Keep the
    # separate practical-details jump link and every destination section ID.
    source = re.sub(r'<nav\b[^>]*class="er-story-doors"[^>]*>.*?</nav>', '', source, flags=re.S)
    titles = {re.search(r'\bid="([^"]+)"', m[1])[1]: m[3]
              for m in HEADING.finditer(source) if re.search(r'\bid="([^"]+)"', m[1])}
    if titles.get('er-welcome-title') and key(titles['er-welcome-title']) == key(titles.get('er-story-title', '')):
        # Preserve the old fragment, and name the introduction independently.
        source = re.sub(r'<h2\b[^>]*id="er-welcome-title"[^>]*>.*?</h2>', '<span id="er-welcome-title" hidden></span>', source, flags=re.S)
        source = source.replace('aria-labelledby="er-welcome-title"', 'aria-label="Introduction"')

    # Interactive checklists already have their own short, descriptive kicker.
    # Use that as their accessible heading instead of reprinting story titles.
    source = re.sub(
        r'<p class="er-kicker">([^<]*)</p><h3 id="(guide-panel-heading-\d+)">.*?</h3>',
        lambda m: '<h3 class="er-kicker" id="'+m[2]+'">'+m[1]+'</h3>',
        source, flags=re.S)

    seen = set()
    def headline(match):
        opening, level, text, closing = match.groups()
        identity = re.search(r'\bid="([^"]+)"', opening)
        identity = identity[1] if identity else ''
        normalized = key(text)
        if level in ('1', '2') and normalized in seen:
            if identity in ('er-ferry-title', 'er-access-title'):
                text = 'Arrival &amp; access.'
            elif identity == 'er-visit-title':
                text = 'The short version.'
            elif not identity:
                # The only untitled H2 duplicates are printable venue cards.
                text = escape(plain(text)) + ' visit checklist'
        if level in ('1', '2'):
            seen.add(key(text))
        return opening + text + closing
    source = HEADING.sub(headline, source)

    # The retained practical disclosure must not repeat the introduction title.
    source = re.sub(
        r'(<details id="original-section-2"><summary><span>).*?(</span>)',
        r'\1A simple plan to begin.\2', source, flags=re.S)
    return source


def main():
    changed = 0
    for path in sorted(ROOT.rglob('*.html')):
        if any(part in ('.git', 'content', 'docs', 'tests', 'services', 'generator-api') for part in path.relative_to(ROOT).parts):
            continue
        old = path.read_text()
        new = clean(old)
        if new != old:
            path.write_text(new)
            changed += 1
    print(f'Cleaned repeated headlines on {changed} pages.')


if __name__ == '__main__':
    main()
