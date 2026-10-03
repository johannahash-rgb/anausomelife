"""Validate the maintained outing studio; its source of truth is visit-story.html."""
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'visit-story.html'
assert 'data-visit-builder' in p.read_text() and 'visit-request-form' in p.read_text()
print('Outing studio source preserved:',p.name)
