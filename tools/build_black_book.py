from build_magazine import ROOT,page,write,E,image
import json
from pathlib import Path
items=[
('rococo','Rococo Ice Cream','Kennebunk, Maine','One very good scoop, with the location and practical details checked before the drive.','https://rococoicecream.com/','/favorite-places-rococo-kennebunk.html'),
('llbean','L.L.Bean','Freeport, Maine','The flagship can be the whole stop. A wander, a look around and room to keep it brief.','https://www.llbean.com/llb/shop/1000001705','/favorite-places-llbean-freeport.html'),
('book-barn','The Book Barn','Niantic, Connecticut','Books, gardens and the kind of browsing that can become the outing.','https://www.bookbarnniantic.com/','/favorite-places-book-barn-niantic.html'),
('lifetime','Life Time','Burlington, Massachusetts','Pool time with the actual family-swim block and changing details checked first.','https://www.lifetime.life/locations/ma/burlington.html','/favorite-places-lifetime-burlington.html'),
('wegmans','Wegmans','Burlington, Massachusetts','Groceries and prepared food in one useful stop. Sometimes practical is the whole point.','https://www.wegmans.com/stores/burlington-ma','/favorite-places/wegmans-burlington.html'),
('rancatores','Rancatore’s','Lexington, Massachusetts','A local treat stop that does not need to become an elaborate day out.','https://www.rancs.com/','/favorite-places-rancatores-lexington.html'),
('lacascias','LaCascia’s Bakery & Deli','Burlington, Massachusetts','Lunch, pastry or something to take home. The next meal counts as good planning.','https://www.lacascias.com/','/favorite-places/lacascias-burlington.html'),
('wilson-farm','Wilson Farm','Lexington, Massachusetts','Food for home, a little New England atmosphere and an easy stopping point.','https://www.wilsonfarm.com/v2.0/home.php','/favorite-places-wilson-farm.html')]
logos={}
f=ROOT/'content/business-logos.json'
if f.exists():logos=json.loads(f.read_text())
body='<section class="library-heading wrap"><p class="eyebrow">The places & businesses in our published field notes</p><h1>The little<br>black book.</h1><p class="article-dek">Good places to keep in reach.</p><p class="quiet-copy">A small address book drawn from Favorite Places. Each entry leads to the full story and the business’s own current information. Buying something alone does not make it a recommendation.</p></section><section class="wrap business-grid">'
for key,title,loc,desc,url,guide in items:
 logo=logos.get(key,{});src=logo.get('asset')
 body+='<article class="business-card">'+('<div class="business-logo">'+image(src,title+' logo')+'</div>' if src else '')+f'<p class="entry-meta">{E(loc)}</p><h2>{E(title)}</h2><p>{E(desc)}</p><div class="business-links"><a href="{guide}">Read the field notes →</a><a href="{url}">Official site ↗</a></div></article>'
body+='</section><aside class="wrap directory-note"><p>Names and logos identify the businesses discussed. Inclusion does not imply a partnership or endorsement by the business. See the relevant story and our <a href="/disclosure.html">disclosure policy</a> for how paid work, gifts and affiliate links are identified.</p><p>Looking for products rather than places? Start with <a href="/things-weve-bought.html">things we have bought</a> and <a href="/how-we-choose.html">how we choose</a>; ownership and a recommendation are different facts.</p></aside>'
write('little-black-book.html',page('The little black book','Businesses featured in our published New England field notes, with practical guides and official links.','/little-black-book.html',body,'business-page'))
