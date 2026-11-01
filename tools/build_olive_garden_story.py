"""Publish the owner's approved October 2026 dinner story and exact-file resources."""
from pathlib import Path
import hashlib, html, json, re, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent
PAGE = 'olive-garden-rigatoni-choice-board.html'
URL = 'https://anausomelife.com/' + PAGE
TITLE = 'We made our son a choice board. Then we answered for him.'
DEK = 'At Olive Garden, James reminded us that communication access isn’t the same as being heard—and that changing your mind is part of having a choice.'
ALT = 'James looks toward the camera at Olive Garden, with his blue AAC communication device in front of him.'
ASSET = ROOT / 'assets/olive-garden'
ASSET.mkdir(exist_ok=True)
photos = [('IMG_9761.jpeg','james-with-aac.jpeg'),('IMG_9784(1).jpeg','james-reading-menu.jpeg')]
for source, target in photos:
    shutil.copyfile(SOURCE / 'upload' / source, ASSET / target)
board = 'downloads/pasta-shape-choice-board.png'
shutil.copyfile(SOURCE / 'generated_images/exec-b5206e4b-a377-485a-8d84-226b12df71cc.png', ROOT / board)

# Original code-native typography, separate from all documentary photographs.
outputs = []
for kind, height in [('feed',1350),('story',1920)]:
    im = Image.new('RGB',(1080,height),'#f7f4ec')
    d = ImageDraw.Draw(im)
    offset = 0 if kind == 'feed' else 260
    def text(line,y,size=38,bold=False,color='#173c4c'):
        font=ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',size)
        assert d.textbbox((0,0),line,font=font)[2] < 920, line
        d.text((80,y+offset),line,font=font,fill=color)
    d.line((80,100+offset,1000,100+offset),fill='#244b3e',width=3)
    text('A DINNER AT OLIVE GARDEN',145,30,True,'#244b3e')
    text('James wanted',270,76,True)
    text('rigatoni.',365,88,True)
    text('His parents',510,64)
    text('stand corrected.',595,64)
    text('Room to choose.',765,38,False,'#244b3e')
    text('Time to change his mind.',825,38,False,'#244b3e')
    text('A free pasta picture choice board.',925,33)
    text('Read the story & get the board:',1030,30)
    text('anausomelife.com/olive-garden/',1080,34,True)
    text('An AUsome Life / @anausomelife',1175,29)
    path = f'downloads/olive-garden-social-{kind}.png'
    im.save(ROOT/path)
    outputs.append({'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'dimensions':[1080,height]})

def figure(file,alt,caption,eager=False):
    with Image.open(ROOT/file) as img: w,h=img.size
    return f'<figure class="og-photo"><img src="/{file}" alt="{html.escape(alt,quote=True)}" width="{w}" height="{h}" loading="{"eager" if eager else "lazy"}" decoding="async"><figcaption>{caption}</figcaption></figure>'

story = []

sample=(ROOT/'congdons-doughnuts-wells-maine.html').read_text()
masthead=re.search(r'<header class="mag-masthead">.*?</header>',sample,re.S)[0]
footer=re.search(r'<footer class="mag-footer">.*?</footer>',sample,re.S)[0].replace('<a href="/congdons-choice-board.html">Doughnut choice board</a>','<a href="/picture-card-library.html">Picture cards</a>')
css='''.og-photo{margin:24px auto;max-width:620px}.og-photo img{display:block;width:100%;height:auto;object-fit:contain}.og-photo figcaption{font:italic .95rem/1.5 Georgia,serif;color:#52635d;margin-top:10px}.fn-cover{align-items:center}.fn-story a{text-decoration:underline}.og-download{display:inline-block;background:#244b3e;color:white!important;padding:14px 20px;margin:10px 0}.aal-story-share{margin-top:40px;padding-top:25px;border-top:1px solid #9caa98}.aal-share-copy-text{white-space:pre-line;overflow-wrap:anywhere}.aal-story-actions{display:flex;flex-wrap:wrap;gap:12px}.aal-story-share textarea{width:100%;min-height:100px}.aal-story-share button{padding:12px}.aal-story-share [hidden]{display:none!important}details{margin:18px 0}summary{cursor:pointer;padding:12px 0}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #244b3e;outline-offset:4px}@media(max-width:700px){.fn-cover{display:block}}'''
head=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{TITLE} | An AUsome Life</title><meta name="description" content="{DEK}"><link rel="canonical" href="{URL}"><link rel="icon" href="/favicon.ico">'''
for name in ['site','magazine','editorial','illustrated-navigation','family-field-notes']:
    head+=f'<link rel="stylesheet" href="/assets/{name}.css">'
head+=f'<style>{css}</style><script src="/assets/global-nav.js?v=20261021-glossary-links" data-aal-global-nav="true" defer></script><meta property="article:published_time" content="2026-10-25"><script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@type':'BlogPosting','headline':TITLE,'description':DEK,'datePublished':'2026-10-25','dateModified':'2026-11-01','image':['https://anausomelife.com/assets/olive-garden/james-with-aac.jpeg'],'author':{'@type':'Organization','name':'An AUsome Life'},'mainEntityOfPage':URL})+'</script></head>'
body=f'''<body class="magazine-shell fn-page"><a class="skip" href="#main">Skip to content</a><div class="edition-line"><span>New England &amp; the everyday</span><span>A family-life field guide</span></div>{masthead}<main id="main"><nav class="wrap fn-breadcrumb" aria-label="Breadcrumb"><a href="/blog.html">The journal</a> / Dining together</nav><header class="wrap fn-cover"><div class="fn-cover-copy"><p class="fn-kicker">Olive Garden · Dinner &amp; communication</p><h1>{TITLE}</h1><p class="fn-dek">{DEK}</p><p class="fn-byline"><time datetime="2026-10-25">October 25, 2026</time> · An AUsome Life</p><a href="#choice-board">Get the free pasta choice board ↓</a></div>{figure('assets/olive-garden/james-with-aac.jpeg',ALT,'James, with his AAC at the table.',True)}</header><article class="fn-story" id="story">'''
body+=r'''<p><strong>James chose angel hair. Then he changed his mind.</strong></p>
<p>That should have been completely unremarkable. People change their minds in restaurants every day.</p>
<p>But James is disabled and uses AAC, and sometimes the people who love him most—including us—can become so accustomed to helping that we forget something important: <strong>helping can become speaking for him.</strong></p>
<p>At Olive Garden, we had made James a simple pasta choice board on my phone. His familiar AAC was there, too.</p>
<p>He chose angel hair. So we ordered angel hair.</p>
<p>And then James became frustrated.</p>
<p>At first, we were trying to figure out what was wrong. But James knew what was wrong.</p>
<p><strong>He wanted rigatoni.</strong></p>
<p>His answer had changed.</p>
<p>The problem wasn’t that James couldn’t make a choice. He had made one.</p>
<p>The problem wasn’t that he couldn’t communicate. He was communicating.</p>
<p><strong>The problem was that we had already decided his first answer was the final answer and moved on.</strong></p>
<p>When we stopped, gave him the board again and actually left room for his response, he showed us what he wanted.</p>
<p>Rigatoni.</p>
<p>And this time, James showed the server himself.</p>
<p>He ordered his own dinner.</p>
<p>I was enormously proud of him.</p>
<p>I was also uncomfortable with myself.</p>
<h2>A choice board doesn’t create autonomy</h2>
<p>We made the choice board because we wanted James to have more control over his dinner.</p>
<p>And then we answered for him anyway.</p>
<p>That contradiction has stayed with me.</p>
<p>It is very easy, especially as a parent or caregiver, to believe that because we’ve provided an accommodation, we’ve provided autonomy.</p>
<p><strong>Those aren’t the same thing.</strong></p>
<p>A communication device can be sitting right in front of someone while everyone else talks around them.</p>
<p>A picture board can offer four beautiful choices while another person still decides which answer counts.</p>
<p>A child can communicate clearly and still be unheard because the adults nearby are moving faster than he is.</p>
<p>We love James completely.</p>
<p>And we can love James completely while still having parenting habits—and ableism—to unlearn.</p>
<p>That is uncomfortable to write.</p>
<p>It is also true.</p>
<h2>“I changed my mind” is communication, too</h2>
<p>There is another part of this that sounds small but isn’t: <strong>James was allowed to change his mind.</strong></p>
<p>His first answer wasn’t wrong. He wanted angel hair when he chose angel hair. Then he wanted rigatoni.</p>
<p>Communication isn’t a test where the first answer gets recorded and everyone moves on.</p>
<p>Choice has to include yes. No. Something else. Help me. And: <strong>I changed my mind.</strong></p>
<p>For people who communicate differently, I think we sometimes unintentionally demand a level of consistency we would never expect from ourselves.</p>
<p>I can look at a menu, order one thing, notice something else and say, “Actually, can I change that?”</p>
<p>James deserves exactly the same freedom.</p>
<p><strong>His right to choose includes his right to change his mind.</strong></p>
<h2>The bigger lesson wasn’t about pasta</h2>
<p>What James did that night was bigger than choosing rigatoni.</p>
<p>He objected. He persisted. He made us realize we had misunderstood him.</p>
<p>And when we finally gave him the space, <strong>he made sure the person who actually needed his answer—the server—got it from him.</strong></p>
<p>That’s self-advocacy.</p>
<p>Not perfectly packaged. Not necessarily quiet. Not always convenient.</p>
<p>Sometimes self-advocacy looks like frustration because the people around you haven’t understood the first several ways you’ve tried to tell them something.</p>
<p>Our job isn’t simply to give James tools to communicate.</p>
<p><strong>Our job is to become better communication partners.</strong></p>
<p>That means slowing down. Waiting. Not jumping in because we can answer faster. Letting him show the server. Checking again. Accepting “no.” Accepting a different answer.</p>
<p>And remembering that communication belongs to the person communicating—not to the person interpreting it.</p>
<h2>And we’re still figuring things out</h2>
<p>Pasta is concrete. A picture of rigatoni looks like rigatoni.</p>
<p>Other communication needs are much harder. We are still trying to find better ways for James to communicate things like frustration, discomfort and more abstract emotions in ways that are actually meaningful to him.</p>
<p>We don’t have that solved.</p>
<p>But this dinner reminded me that the answer isn’t only to keep building better tools for James.</p>
<p><strong>We have to keep becoming better listeners, too.</strong></p>
<h2>One lovely moment before dinner</h2>
<p>There was another part of the evening I don’t want to forget.</p>
<p>While we waited, James connected with another disabled teenager over <em>Lilo &amp; Stitch</em>. They explored his AAC together.</p>
<p>A new friend before dinner.</p>
<p>It was one of those small moments that can make an ordinary family outing feel especially good.</p>
<figure class="og-photo"><img src="/assets/olive-garden/james-reading-menu.jpeg" alt="James looks at the pasta menu with his blue AAC device beside him." width="1152" height="1536" loading="lazy" decoding="async"><figcaption>His menu. His choice.</figcaption></figure>
<section id="choice-board" aria-labelledby="board-title"><h2 id="board-title">The pasta choice board</h2><p>I use ChatGPT on my phone to make quick, concrete choice boards for James while we’re out. We’ve done this with <a href="/ai-ice-cream-choice-board-rancatores-lexington.html">ice cream at Ranc’s</a>, too.</p><a class="og-download" href="/downloads/pasta-shape-choice-board.png" download>Download the pasta choice board (PNG)</a><figure class="og-photo"><img src="/downloads/pasta-shape-choice-board.png" alt="Picture choice board with four large labeled generated food illustrations: fettuccine, spaghetti, angel hair, and rigatoni." width="1254" height="1254" loading="lazy" decoding="async"><figcaption>Fettuccine, spaghetti, angel hair, rigatoni.</figcaption></figure><p>It is an independent visual aid with AI-generated food illustrations, based on the options we saw during our visit. It is not an official Olive Garden menu, so check current choices with your server.</p><p>Keep familiar AAC available alongside any temporary board—including ways to say <strong>no</strong>, <strong>help</strong>, or <strong>something else</strong>.</p><p>A board can make the choices visible.</p><p><strong>But the board can’t do the most important part for us. We still have to wait for the answer.</strong></p></section>
<h2>A few practical Olive Garden notes from our family</h2>
<p>We like Olive Garden because the food is familiar and we’ve generally found the service quick and friendly.</p>
<ul><li><strong>Join the waitlist online</strong> before arriving, then check in with the host.</li><li><strong>Ask about bar-area tables</strong> if that setup works better for your family; we’ve enjoyed them on other visits.</li><li><strong>Pay at the table</strong> when you’re ready to leave.</li></ul>
<p><a href="https://www.olivegarden.com/app" target="_blank" rel="noopener noreferrer">Olive Garden’s waitlist instructions</a> · Availability and wait times vary; these are simply our family’s experiences.</p>
<p>But the thing I’ll remember from this particular dinner has nothing to do with the waitlist.</p>
<p>James wanted rigatoni.</p>
<p>He told us.</p>
<p><strong>We just needed to stop answering long enough to hear him.</strong></p>'''

sharealt='Cream graphic headed A dinner at Olive Garden. Navy text reads: James wanted rigatoni. His parents stand corrected. Room to choose. Time to change his mind. A free pasta picture choice board. Read the story and get the board at anausomelife.com/olive-garden/. Credit: An AUsome Life / @anausomelife.'
caption=f'We made James a choice board—and then realized we were still answering for him. Our Olive Garden dinner became a lesson about AAC, autonomy, changing your mind, and the work of becoming better listeners.\nRead the story and get the board: {URL}\nCredit: An AUsome Life / @anausomelife'
body+=f'''<section class="aal-story-share" id="share-this-story" aria-labelledby="aal-share-title" data-share-summary="A family dinner about AAC, autonomy, and leaving room for the answer."><h2 id="aal-share-title">Share the story and the resource</h2><div class="aal-story-actions"><button type="button" data-share-native hidden>Share story</button><button type="button" data-copy-link hidden>Copy story link</button><button type="button" data-copy-caption hidden>Copy suggested caption &amp; credit</button><a href="{URL}">Open the story</a></div><p class="aal-share-status" role="status"></p><div data-share-fallback hidden><label for="og-share-copy">Select and copy this text</label><textarea id="og-share-copy" readonly></textarea></div><details class="aal-share-package"><summary>Sharing graphics, captions and image descriptions</summary>'''
for output in outputs:
    name='Feed' if 'feed' in output['path'] else 'Story'
    body+=figure(output['path'],sharealt,f'{name} graphic · {output["dimensions"][0]} × {output["dimensions"][1]} pixels')+f'<a href="/{output["path"]}" download>Download the {name.lower()} graphic</a>'
body+=f'''<p class="aal-share-permission">You may share only these two named graphics—olive-garden-social-feed.png and olive-garden-social-story.png—unchanged in organic social posts or Stories, with An AUsome Life / @anausomelife credit and a link to this story. This permission does not cover family photographs, other site content, edits or paid advertising.</p><h3>A suggested caption</h3><p class="aal-share-copy-text" data-share-caption>{html.escape(caption)}</p><h3>A short Story caption</h3><p class="aal-share-copy-text" id="og-short-caption">Room to choose—and change your mind. An Olive Garden family dinner and free pasta choice board from An AUsome Life / @anausomelife.\n{URL}</p><button type="button" data-copy-share-text="og-short-caption" hidden>Copy Story caption</button><h3>Image description</h3><p id="og-graphic-alt">{html.escape(sharealt)}</p><button type="button" data-copy-share-text="og-graphic-alt" hidden>Copy image description</button><p>Created independently by An AUsome Life. These resources are not official Olive Garden materials or a statement of endorsement. <a data-reuse-link href="/media/#sharing">Ask about specific image use.</a></p></details></section></article><nav class="wrap fn-related" aria-label="Related stories"><a href="/congdons-doughnuts-wells-maine.html">A doughnut stop and another picture choice board →</a><p><a href="/blog.html">Back to the journal →</a></p></nav></main>{footer}<script src="/assets/site.js" defer></script><script src="/assets/story-share.js?v=20261025" defer></script></body></html>'''
(ROOT/PAGE).write_text(head+body)
(ROOT/'olive-garden').mkdir(exist_ok=True)
(ROOT/'olive-garden/index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Olive Garden story | An AUsome Life</title><meta http-equiv="refresh" content="0; url=/{PAGE}"><link rel="canonical" href="{URL}"></head><body><p><a href="/{PAGE}">Read the Olive Garden story and get the choice board.</a></p></body></html>')

blog=(ROOT/'blog.html').read_text()
card=f'''<li><article class="journal-recent-story"><a class="journal-recent-link" href="/{PAGE}" aria-labelledby="recent-story-olive"><figure class="journal-recent-photo"><img src="/assets/olive-garden/james-with-aac.jpeg" alt="{ALT}" width="1152" height="1536" loading="lazy" style="object-fit:contain"></figure><div class="journal-recent-copy"><p class="journal-recent-place">Olive Garden · Dinner &amp; communication</p><h3 id="recent-story-olive">{TITLE}</h3><p class="journal-recent-description">James changed his mind about pasta. We learned that giving him a communication tool was not the same as leaving enough room for his answer.</p><span class="journal-recent-read">Read the story →</span></div></a></article></li>'''
if PAGE not in blog:
    marker='<li><article class="journal-recent-story"><a class="journal-recent-link" href="/snowshoeing-with-james-right-outside-home.html"'
    assert marker in blog
    blog=blog.replace(marker,card+'\n'+marker,1)
    (ROOT/'blog.html').write_text(blog)
record={'created':'2026-10-25','canonical_story':URL,'authorization_basis':'Owner supplied family photographs, dictated and refined firsthand account, then explicitly instructed Post. Standing direction authorizes original share graphics.','sources':[{'source':s,'output':'assets/olive-garden/'+t,'basis':'Owner-provided original family photograph; editorial publication only, preserved byte-for-byte.'} for s,t in photos], 'choice_board':{'path':board,'source':'Earlier image-generation output in this conversation, created at owner request during the visit.','disclosure':'AI-generated generic food illustrations; not official menu or photographs of restaurant dishes.','intended_use':'Free personal communication resource; no venue endorsement.'},'scoped_organic_sharing_intent':{'assets_only':[x['path'] for x in outputs],'permitted_intended_use':'The two original typographic graphics only: unchanged organic social sharing with credit and story link.','scope_limits':'No family photo reuse, paid media, edits or blanket archive license.'},'outputs':outputs,'brand_accounts':{'status':'No brand tagging; no profile assumed or used.'},'validation':{'reviewed':'2026-10-25','visual_review':'Pending final inspection of exported assets and page.'}}
(ROOT/'docs/olive-garden-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
registry=ROOT/'docs/story-sharing-approvals.json'
data=json.loads(registry.read_text());data['packages'][PAGE]={'provenance':'docs/olive-garden-provenance.json','reviewed':'2026-10-25'};registry.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
registry=ROOT/'docs/social-preview-selections.json'
data=json.loads(registry.read_text())
with Image.open(ASSET/'james-with-aac.jpeg') as im: w,h=im.size
data['pages'][PAGE]={'image':'/assets/olive-garden/james-with-aac.jpeg','alt':ALT,'width':w,'height':h,'mime':'image/jpeg','sha256':hashlib.sha256((ASSET/'james-with-aac.jpeg').read_bytes()).hexdigest(),'card':'summary_large_image','type':'article','kind':'original-family-photograph','provenance':['docs/olive-garden-provenance.json'],'selection_reason':'Owner-selected original family photograph, unchanged; specific editorial page preview, no third-party download rights.'}
registry.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print('Created story, journal card, two original photos, board, two sharing graphics and provenance.')
