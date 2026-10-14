"""Apply the calendar's benefit-led opening without rebuilding its event controls."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HERO = '''<section class="wrap calendar-heading calendar-entrance" aria-labelledby="calendar-title">
<div class="calendar-value"><p class="eyebrow">Sensory-friendly &amp; accessible events · New England</p>
<h1 id="calendar-title">Find an outing that fits your family.</h1>
<p class="calendar-benefit">Less searching. Fewer surprises. Compare sensory levels, ages, cost, and published access details before you make a plan.</p>
<a class="calendar-primary-action" href="#upcoming">Find my next outing <span aria-hidden="true">↓</span></a>
<p class="calendar-scope">For children, teens &amp; adults · All six New England states</p></div>
<aside class="calendar-start" aria-labelledby="calendar-start-title"><p class="eyebrow">A useful place to start</p><h2 id="calendar-start-title">What matters today?</h2>
<nav aria-label="Start with an event preference">
<a href="/calendar.html?sensory=low#upcoming"><strong>Lower sensory</strong><span>Find a quieter kind of outing <b aria-hidden="true">↗</b></span></a>
<a href="/calendar.html?access=wheelchair-step-free#upcoming"><strong>Wheelchair &amp; step-free options</strong><span>See published access features <b aria-hidden="true">↗</b></span></a>
<a href="/calendar.html?age=teens#upcoming"><strong>Something for teens</strong><span>Start with the right age group <b aria-hidden="true">↗</b></span></a>
<a href="/calendar.html?cost=free#upcoming"><strong>Free admission</strong><span>Check eligibility &amp; booking details <b aria-hidden="true">↗</b></span></a>
</nav></aside></section>'''
MORE = '''<details class="calendar-other-plans" id="more-planning"><summary>More ways to plan a day out</summary><nav class="calendar-jump" aria-label="More planning resources"><a href="#social-active-programs">Dances, hikes &amp; play</a><a href="#free-programs">Free programs</a><a href="#watchlist">Annual watchlist</a><a href="#organizers">More organizers</a><a href="/carolines-cart-new-england.html">Caroline’s Cart directory</a></nav></details>'''

def apply():
    p=ROOT/'calendar.html';s=p.read_text()
    s,n=re.subn(r'<section class="[^"]*calendar-heading[^"]*"[^>]*>.*?</section>',HERO,s,count=1,flags=re.S)
    if n!=1:raise RuntimeError('Expected one calendar entrance')
    s=re.sub(r'<link[^>]*href="/assets/calendar-entrance\.css[^>]*>','',s)
    s=s.replace('</head>','<link rel="stylesheet" href="/assets/calendar-entrance.css?v=20261014-value">\n</head>')
    s=s.replace('<div><p class="eyebrow">Plan the day</p><h2>Upcoming events.</h2></div>','<div><h2>Find events</h2><p class="calendar-filter-caption">Choose a place and date, then add the details that matter to you.</p></div>')
    s=s.replace('More filters <span data-more-count></span><span class="filter-description">Sensory level, holidays, age &amp; access</span>','Sensory, age &amp; access filters <span data-more-count></span><span class="filter-description">Plus holidays &amp; event types</span>')
    s=re.sub(r'<details class="calendar-other-plans".*?</details>','',s,flags=re.S)
    s=s.replace('<aside class="calendar-note">',MORE+'\n<aside class="calendar-note">',1)
    s=re.sub(r'<title>.*?</title>','<title>Find sensory-friendly &amp; accessible New England events | An AUsome Life</title>',s,count=1)
    description='Find New England outings that fit your family. Compare sensory levels, ages, cost, and published accessibility features, with links to the organizers.'
    s=re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*(">)',lambda m:m[1]+description+m[2],s)
    s=re.sub(r'(<meta property="og:title" content=")[^"]*(">)',lambda m:m[1]+'Find a New England outing that fits your family'+m[2],s)
    p.write_text(s)
    print('Updated calendar entrance; existing filters and event views preserved.')

if __name__=='__main__':apply()
