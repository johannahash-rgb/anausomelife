#!/usr/bin/env python3
"""Build the expanded glossary: static reading first, optional browser tools second."""
import argparse, html, importlib.util, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
legacy=module('glossary_v1_data',HERE/'glossary_v1_data.py')
art=module('glossary_icons',HERE/'glossary_icons.py')
CATS=['Identity & support','Communication','Sensory & regulation','Behavior & learning','IEP & school','Rights & safety','Daily care & health','Adult life & services','People & professional roles']
SHORT=['Autism & support','Communication','Sensory & regulation','Behavior & learning','IEP & school','Rights & safety','Daily care & health','Adult life & services','Who does what?']
FLAGS={'Profound autism':'Debated term','Gestalt language processing (GLP)':'Evidence developing','ABA — Applied Behavior Analysis':'Approaches debated','Demand avoidance / PDA':'Debated term','Monotropism':'Theory','Double empathy problem':'Theory','Autistic burnout':'Research developing','Autistic inertia':'Research developing','Communication authorship, FC & RPM':'Evidence caution','Massachusetts N1 & N2 notices':'Massachusetts','Massachusetts transition: age 14 & Chapter 688':'Massachusetts'}
PRON={'Interoception':'in-ter-oh-SEP-shun','Proprioception':'proh-pree-oh-SEP-shun','Aphasia':'uh-FAY-zhuh','Apraxia of speech / Childhood Apraxia of Speech (CAS)':'uh-PRAK-see-uh','Dysarthria':'dis-AR-three-uh','Echolalia':'ek-oh-LAY-lee-uh','Dysphagia / swallowing difficulty':'dis-FAY-juh','Alexithymia':'ay-lek-sih-THY-mee-uh'}
esc=lambda x:html.escape(str(x),quote=True)
slug=legacy.slug

def load_sources(root):
    result={}
    for line in (root/'assets/glossary-v2-sources.txt').read_text().splitlines():
        if not line.strip():continue
        key,label,url,kind=line.split('|')
        if not url.startswith('https://'):raise ValueError('Source needs HTTPS')
        result[key]={'label':label,'url':url,'kind':kind}
    return result

def revise(terms,sources):
    by={t['term']:t for t in terms}
    def patch(prefix,**values):
        matches=[t for t in terms if t['term'].startswith(prefix)]
        if len(matches)!=1:raise ValueError('Ambiguous revision '+prefix)
        matches[0].update(values)
    patch('Autism /',plain='A lifelong developmental disability that can affect communication, sensory experience, interests and everyday support needs.')
    patch('Apraxia of speech',plain='Difficulty planning the movements needed to say speech sounds and words.',detail='Apraxia of speech concerns movement planning or programming, not simply weak speech muscles. Childhood apraxia of speech (CAS) is the developmental motor-speech diagnosis. A person may also have language, learning or other motor difficulties; the diagnosis does not tell us their exact understanding. An SLP with motor-speech expertise assesses the pattern over time.',note='Limited or inconsistent speech alone does not establish apraxia. AAC can be used alongside speech support; communication should not wait for a definitive motor-speech diagnosis.',do='Ask which evidence supports the diagnosis, whether language and motor execution were assessed separately, and what communication access is available now.')
    patch('Aphasia',plain='An acquired language difficulty caused by a brain condition or injury.',detail='Aphasia can affect understanding, speaking, reading and writing. It is different from difficulty planning speech movements (apraxia) or executing them (dysarthria), though they can co-occur. Older records sometimes use developmental aphasia or dysphasia differently; ask the clinician what the term means in that record.',note='Being autistic or nonspeaking does not by itself mean a person has aphasia. Sudden new trouble speaking or understanding, especially with weakness or facial droop, can be an emergency: call emergency services.',do='Ask whether the report describes an acquired change in language, a developmental language difficulty, a motor-speech disorder or a combination.')
    patch('Dysarthria',plain='Difficulty making speech movements because of neurological problems with strength, coordination, speed or control.',do='Ask about the speech movements involved, what makes communication clearer and which AAC or other support helps unfamiliar listeners understand.')
    patch('AAC —',plain='Ways to communicate alongside speech or instead of it.',detail='AAC includes unaided methods such as gestures and signs, and aided methods such as boards, books, writing and speech-generating devices. It can be used all the time or only when speech is difficult. There is no age, IQ or speech test someone must pass before AAC is considered. The selection method, vocabulary and partner support need to fit the person.',do='Check that the person can reach and use their communication throughout the day. Include no, stop, help, pain, questions, opinions and social connection—not just requests for objects.')
    patch('Multimodal communication',do='Make a short communication note showing the person’s reliable words, gestures, signs and AAC methods. Ask every supporter to respond to their meaning, not demand a preferred format.')
    patch('Intellectual disability',note='Intellectual disability involves both intellectual and adaptive limitations. Assessment must account for language, sensory, motor and cultural access. Do not assume either typical cognition or intellectual disability from speech ability alone.',do='Ask what each score measures, whether the response method was accessible, and what practical supports the whole assessment indicates.')
    patch('Age-respectful',plain='Respecting someone’s actual age, privacy and choices while giving the help they need.',detail='A teen or adult may need simple explanations or hands-on personal care without being treated as a small child. Age-respectful support also means respecting genuine interests: enjoying a children’s film, toy or song is not a reason to shame someone or remove a preferred activity.',do='Offer accessible choices across a range of interests. Use the person’s preferred name, protect privacy and never describe a whole person as having a single “mental age”.',note='The goal is dignity and choice—not policing harmless interests to make someone look their age.')
    patch('Interoception',plain='Noticing and making sense of signals from inside your body.',detail='These signals can relate to hunger, thirst, pain, toileting, temperature, breathing and emotional arousal. People can experience them faintly, strongly or in ways that are hard to identify. Interoception is different from intraverbal, a behavior-analysis term about responding in conversation.',do='Combine predictable drinks, meals, rest and toileting opportunities with the person’s own signals and clinical advice. Make body and pain vocabulary accessible without forcing an answer.',note='Not every autistic person experiences the same differences. A body-awareness explanation must not replace assessment of persistent pain, dehydration or new symptoms.')
    patch('Meltdown',plain='An intense response to overwhelm that can make communication and self-control much harder.',why='During escalating distress, safety, reduced pressure and recovery matter more than obtaining an explanation or teaching a lesson.',detail='Sensory input, pain, uncertainty, communication breakdown, fatigue or other demands can contribute. Visible behavior does not reliably reveal someone’s intent. Avoid simplistic comparisons in which every tantrum is manipulation and every meltdown has one cause.',do='Reduce unnecessary words, demands and sensory input; offer space and familiar support while following the person’s safety plan. Review triggers and medical concerns after recovery.')
    patch('Reinforcement',plain='When what happens after an action makes that action more likely next time.',detail='This is part of ordinary learning for everyone, not something unique to autism. A warm reply can make you more likely to text a friend again. Getting useful help can make asking for help worthwhile. A consequence counts as reinforcement because of its effect over time—not just because an adult intended it as a reward.',look='You put on headphones and the room becomes more comfortable, so you use them again. A person chooses music on AAC, music plays, and that way of asking becomes useful. These are everyday examples, not proof of the function in an individual case.',do='Ask what skill is being supported, whether the outcome is meaningful to the person and whether the skill works outside practice. Never make basic care or communication access conditional on compliance.')
    patch('Positive reinforcement',look='A person requests music; music is added; the person becomes more likely to use that request. Positive means adding something, not morally good.',do='Observe what the person actually enjoys and how the consequence affects future behavior. Do not assume praise, touch or public attention is welcome.')
    patch('Negative reinforcement',do='Ask what is being removed and which response becomes more likely. Reducing painful input can be an accommodation as well as part of a learning process; do not create distress to make relief a bargaining tool.')
    patch('Consent',plain='Freely agreeing to a specific decision with the information, support and legal capacity needed.',detail='Consent rules differ across health care, education, research and other settings. Needing communication support is not the same as lacking decision-making capacity. A legally authorized representative may have authority for some decisions, but the person’s own wishes and participation still matter.',do='Explain the choice in an accessible way, allow time, check understanding and make refusal possible. Clarify who has authority for this specific decision.',note='Silence, freezing or outward compliance is not automatic agreement. Necessary care and emergencies can involve different legal and ethical duties; use the relevant clinical plan and qualified advice, not a blanket rule.')
    patch('Assent',plain='A person’s own indication that they are willing to take part, even when someone else gives legal permission.',detail='Assent should be actively noticed and checked throughout an activity, not assumed from the absence of a protest. Communication can include speech, AAC, gestures and consistent actions. A person may agree to one part and reject another, or change their mind.',do='Write down the person’s usual yes, no, stop and break signals. When signals are unclear, pause and check where possible rather than interpret distress as cooperation.',note='Assent does not replace legally required consent. Immediate danger and essential health care may require action despite objection; seek the least restrictive workable support, explanation and review.')
    patch('FAPE —',detail='Under IDEA, the educational program must be designed to enable progress appropriate in light of the individual child’s circumstances. The Supreme Court’s Endrew F. standard is not satisfied by merely trivial progress. Goals should be appropriately ambitious; substantial support needs do not justify an empty or unchallenging program.',sources=[{'label':'IDEA: FAPE, section 300.17','url':'https://sites.ed.gov/idea/regs/b/a/300.17','kind':'U.S. federal rule'},sources['endrew']],do='Ask how present levels, challenging goals, specially designed instruction and related services fit together, and what data will trigger a change if progress is inadequate.')
    patch('IEP —',plain='A written special-education plan for a student who is eligible under IDEA.',do='Read the goals and service details together. Check who provides each support, how often, for how long, where, when it starts and how progress will be reported.')
    patch('Level 3',sources=[{'label':'CDC: diagnostic criteria and support-level language','url':'https://www.cdc.gov/autism/hcp/diagnosis/index.html','kind':'Clinical guidance'}])
    patch('Seizure action plan',note='Call emergency services when a seizure lasts longer than five minutes, or sooner if the prescribed plan says so; also for a first seizure, breathing difficulty, a seizure in water, injury or repeated seizures without recovery. Follow the individualized rescue plan; do not put objects in the mouth or hold the person down.')
    patch('BCBA & RBT',sources=[sources['bacb'],sources['rbt']])
    patch('Reward vs.',do='Notice the effect over time and ask about current preferences. Basic care and access should remain available whether or not a reward is effective.')
    # Corrections to older aliases and source labels are confined to this glossary.
    for t in terms:
        for s in t['sources']:
            if 'PMC13083756' in s['url']:s.update(sources['affirming'])
        t['flag']=FLAGS.get(t['term'],'')
    return terms

def load(root):
    sources=load_sources(root)
    terms=legacy.load_terms(root)
    for t in terms:t['detail']=t['plain']
    for n in range(1,5):
        path=root/'assets'/f'glossary-v2-expansion-{n}.txt'
        for i,line in enumerate(path.read_text().splitlines(),1):
            if not line.strip():continue
            row=[v.strip() for v in line.split('||')]
            if len(row)!=12:raise ValueError(f'{path}:{i}: expected 12 fields, got {len(row)}')
            name,cat,plain,detail,why,look,action,ask,note,keys,related,icon=row
            terms.append(dict(term=name,cat=cat,plain=plain,detail=detail,why=why,look=look,do=action,ask=ask,note=note,sources=[sources[k] for k in keys.split(';')],related=related.split(';'),icon_key=icon))
    revise(terms,sources)
    if len(terms)<180 or len({t['term'] for t in terms})!=len(terms):raise ValueError('Missing or duplicate glossary entries')
    for t in terms:
        if t['cat'] not in CATS:raise ValueError(t['cat'])
        t['id']=slug(t['term']);t['art']=art.draw(art.spec_for(t),t['term'])
        for field in ('plain','why','look','ask','sources'):
            if not t.get(field):raise ValueError('Missing '+field+' for '+t['term'])
    return sorted(terms,key=lambda t:t['term'].casefold())

def render(root,terms):
    names={t['term']:t for t in terms}
    aliases=dict(legacy.ALIASES)
    aliases.update({'HCBS':'HCBS / Medicaid waiver','FCT':'Functional Communication Training (FCT)','Dysphagia':'Dysphagia / swallowing difficulty','DLD':'Developmental language disorder (DLD)','PDA':'Demand avoidance / PDA','SLP':'Speech-language pathologist (SLP)','OT':'Occupational therapy (OT)','PT':'Physical therapy (PT)','BCBA':'BCBA & RBT','RBT':'BCBA & RBT','DSP':'Direct support professional (DSP)','504':'Section 504 plan','SDM':'Supported decision-making','N1':'Massachusetts N1 & N2 notices','N2':'Massachusetts N1 & N2 notices','688':'Massachusetts transition: age 14 & Chapter 688','nonverbal':'Nonspeaking / cannot rely on speech alone','multiple modality communication':'Multimodal communication'})
    def resolve(q):
        q=aliases.get(q,q)
        if q in names:return names[q]
        found=[t for t in terms if t['term'].casefold().startswith(q.casefold())]
        return found[0] if len(found)==1 else None
    def link(q,label=None):
        t=resolve(q)
        return '<a href="#'+t['id']+'">'+esc(label or q)+'</a>' if t else ''
    def card(t):
        name=t['term'];target=t['id'];aka=[a for a,v in aliases.items() if v==name]
        flag='<span class="cg-status">'+esc(t['flag'])+'</span>' if t['flag'] else ''
        pron='<p class="cg-pron">Say it: '+esc(PRON[name])+'</p>' if name in PRON else ''
        detail='<section class="cg-depth"><h3>A little more meaning</h3><p>'+esc(t['detail'])+'</p></section>' if t.get('detail') and t['detail']!=t['plain'] else ''
        action='<section class="cg-action"><h3>One useful next step</h3><p>'+esc(t['do'])+'</p></section>' if t.get('do') else ''
        note='<section class="cg-caution"><h3>Keep in mind</h3><p>'+esc(t['note'])+'</p></section>' if t.get('note') else ''
        sources=''.join('<li><span>'+esc(s.get('kind','Further reading'))+'</span><a href="'+esc(s['url'])+'" target="_blank" rel="noopener noreferrer">'+esc(s['label'])+' <span aria-hidden="true">↗</span><span class="cg-sr"> (opens in a new tab)</span></a></li>' for s in t['sources'])
        related=''.join(link(q) for q in t.get('related',[]) if resolve(q) and resolve(q)['id']!=target)
        return f'''<details class="cg-term" id="{target}" data-name="{esc(name)}" data-category="{esc(t['cat'])}" data-aliases="{esc(' | '.join(aka))}"><summary>{t['art']}<span class="cg-summary-copy"><span class="cg-term-meta">{esc(t['cat'])} {flag}</span><h2>{esc(name)}</h2><span class="cg-preview">{esc(t['plain'])}</span></span><span class="cg-plus" aria-hidden="true">+</span></summary><div class="cg-body">{pron}{detail}<section><h3>Why this helps a caregiver</h3><p>{esc(t['why'])}</p></section><section class="cg-depth cg-example"><h3>An everyday example</h3><p>{esc(t['look'])}</p></section>{action}<section class="cg-question"><h3>A question you can use</h3><blockquote>{esc(t['ask'])}</blockquote><button type="button" data-copy-question data-js>Copy this question</button></section>{note}<div class="cg-term-actions" data-js><button type="button" data-save="{target}" aria-pressed="false">Save this term</button><button type="button" data-copy-link="{target}">Copy definition link</button></div><section class="cg-sources"><h3>Read further</h3><ul>{sources}</ul></section><nav class="cg-related" aria-label="Related to {esc(name)}">{related}</nav><a class="cg-permalink" href="#{target}">Link to this definition ↗</a></div></details>'''
    cards='\n'.join(card(t) for t in terms)
    counts={c:sum(t['cat']==c for t in terms) for c in CATS}
    opts='<option value="All">Every topic</option>'+''.join('<option value="'+esc(c)+'">'+esc(s)+' ('+str(counts[c])+')</option>' for c,s in zip(CATS,SHORT))
    topics=''.join('<button type="button" data-topic="'+esc(c)+'" aria-pressed="false"><span>'+esc(s)+'</span><span>'+str(counts[c])+'</span></button>' for c,s in zip(CATS,SHORT))
    letters=''.join('<button type="button" data-letter="'+l+'" aria-pressed="false">'+l+'</button>' for l in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    pairs=[('Speech vs. language vs. communication','AAC','Speech is one method. Communication is the wider goal.'),('Aphasia','Apraxia of speech','Aphasia concerns language; apraxia of speech concerns planning speech movements.'),('Consent','Assent','Legal permission and the person’s own willingness are related, but not interchangeable.'),('Positive reinforcement','Negative reinforcement','Adding and removing—not good and bad. Both increase the relevant behavior.'),('Accommodations','Modifications','Changing access and changing the learning expectation are different questions.'),('Interoception','Intraverbal','Internal body signals versus responding in conversation. Similar-sounding words, different meanings.')]
    compare=''.join('<article><h3>'+esc(a)+' <span> / </span>'+esc(b)+'</h3><p>'+esc(text)+'</p><nav>'+link(a,'Read '+a)+link(b,'Read '+b)+'</nav></article>' for a,b,text in pairs)
    n=len(terms)
    return f'''<main id="main" class="cg-root cg-v2"><div class="cg-wrap"><nav class="cg-crumb" aria-label="Breadcrumb"><a href="/family-roles.html">Family &amp; caregiver support</a><span>/</span><span>The glossary</span></nav><section class="cg-hero"><div><p class="cg-eyebrow">For family, friends &amp; support teams</p><h1>A little clarity.<br>A lot more understanding.</h1><p class="cg-dek">The caregiver’s glossary to high-support and profound autism. <strong>{n} terms</strong>, explained without making you learn a second language.</p><p class="cg-reassure">You do not need to learn every word. Find the one you need today.</p></div><aside class="cg-start"><p class="cg-eyebrow">Not sure where to start?</p><h2>Start with real life.</h2><nav aria-label="Browse by situation" data-js><button data-route="school">I’m preparing for an IEP meeting <span>↗</span></button><button data-route="communication">I want to understand communication <span>↗</span></button><button data-route="distress">Something feels harder today <span>↗</span></button><button data-route="adult">We’re planning care or adult life <span>↗</span></button></nav><p>Short definitions first. Examples, questions and source links inside.</p></aside></section></div><section class="cg-search-tools" id="cg-search-tools" aria-label="Find a term" data-js><div class="cg-wrap"><div class="cg-search-row"><div class="cg-search-field"><label for="cg-search">What word or situation are you looking for?</label><div><input id="cg-search" type="search" autocomplete="off" placeholder="Try AAC, body signals, school says no…" aria-controls="cg-grid"><button type="button" id="cg-clear" aria-label="Clear search and filters">Reset</button></div></div><div class="cg-topic-select"><label for="cg-topic">Topic</label><select id="cg-topic">{opts}</select></div><details class="cg-tools"><summary>Reading tools</summary><div><button data-tool="open">Open shown definitions</button><button data-tool="close">Close definitions</button><button data-tool="all">Show every matching term</button><button data-tool="print">Print matching definitions</button><button data-tool="questions">Print my saved questions</button><button id="cg-size" aria-pressed="false">Larger text</button></div></details></div><div class="cg-reading-row"><div class="cg-view" role="group" aria-label="Detail level"><button data-depth="quick" aria-pressed="true">Quick read</button><button data-depth="full" aria-pressed="false">Full explanations</button></div><button id="cg-saved" aria-pressed="false">Saved here <span id="cg-saved-count">0</span></button><button id="cg-compare">Often mixed up ↗</button></div></div></section><div class="cg-wrap cg-workspace"><aside class="cg-sidebar" data-js><p class="cg-eyebrow">Browse the guide</p><button class="cg-all" data-topic="All" aria-pressed="true">Every topic <span>{n}</span></button><nav aria-label="Topics">{topics}</nav><details class="cg-values"><summary>Our starting point</summary><p>Dignity is not earned through speech, independence or compliance. We respect communication, preferences and genuine support needs together.</p><p>Autistic and disability-led perspectives sit alongside clinical evidence and applicable law. Debated labels are marked, not presented as universal truth.</p><a href="/language.html">Our language approach ↗</a></details><p class="cg-local">Saved terms stay in this browser only. No account or personal care notes are needed.</p></aside><section class="cg-results" aria-label="Glossary definitions"><div class="cg-resultbar"><h2 id="cg-count" role="status" aria-live="polite">{n} terms to explore</h2><button type="button" id="cg-reset-path" hidden data-js>Clear this view</button></div><nav class="cg-alphabet" aria-label="Filter by initial letter" data-js><button data-letter="" aria-pressed="true">All</button>{letters}</nav><p class="cg-path-note" id="cg-path-note" hidden></p><div class="cg-empty" id="cg-empty" hidden><h2>Let’s try another way.</h2><p>No terms match these filters. Try a shorter word or clear the topic.</p><div id="cg-suggestions"></div><button type="button" data-tool="reset">Clear all filters</button></div><noscript><p>Search and saving need JavaScript, but every definition below is readable without it. Use your browser’s Find command or open a term.</p></noscript><div class="cg-grid" id="cg-grid"><!-- GLOSSARY:START -->{cards}<!-- GLOSSARY:END --></div><div class="cg-load" data-js><button type="button" id="cg-more">Show more terms</button><span id="cg-shown"></span></div></section></div><div class="cg-wrap"><section class="cg-closing"><div><p class="cg-eyebrow">Take this into the meeting</p><h2>“What does that mean<br>for this person?”</h2></div><div><p>A definition is a starting point. Ask what was observed, what support is needed and who is responsible for making it happen.</p><p>Every entry includes a question you can use. Save the useful ones and print them together.</p><a href="/caregiver-handover-guide.html">Make a clearer caregiver handoff ↗</a></div></section><details class="cg-editorial"><summary>About the sources, language and limits of this guide</summary><p>This is an editorial reference from An AUsome Life, not an individualized assessment, legal opinion or professionally certified clinical resource. Updated October 20, 2026. Source labels distinguish law, clinical guidance, technical research and lived-experience perspectives.</p><p>Some technical and historical sources use older language. Linking them for a definition does not endorse every practice or recommendation on their sites. No theory explains every autistic person, and findings from speaking adults should not automatically be generalized to people with profound support needs.</p><p>U.S. federal education rules are a baseline; state requirements differ. Massachusetts entries are explicitly marked. New or serious health changes need appropriate medical assessment, not a glossary label. In immediate danger, contact local emergency services and follow the person’s current emergency plan.</p><p>We use autistic person by default and respect individual preference. Age-respectful care does not mean taking away harmless interests. A need for extensive assistance and a right to meaningful choice can both be true.</p></details></div><dialog id="cg-comparison" aria-labelledby="cg-comparison-title"><div class="cg-dialog-head"><h2 id="cg-comparison-title">Often mixed up.</h2><button type="button" id="cg-comparison-close" autofocus>Close</button></div><p>These distinctions help you ask a more useful question.</p>{compare}</dialog><div id="cg-toast" class="cg-toast" role="status" aria-live="polite"></div></main>'''

def build(root):
    root=Path(root);page=root/'caregiver-glossary.html'
    if not page.exists():return
    terms=load(root);source=page.read_text()
    content=render(root,terms)
    if len(re.findall(r'<main\b',source))!=1:raise ValueError('Expected one main')
    source=re.sub(r'<main\b.*?</main>',lambda m:content,source,count=1,flags=re.S)
    source=re.sub(r'(/assets/caregiver-glossary\.(?:css|js))(?:\?[^"\s<>]+)?',r'\1?v=20261020-expanded-v2',source)
    source=re.sub(r'104 plain-English terms',str(len(terms))+' plain-English terms',source)
    source=source.replace('"dateModified":"2026-10-19"','"dateModified":"2026-10-20"')
    page.write_text(source,encoding='utf-8')
    hub=root/'family-roles.html'
    if hub.exists():
        text=hub.read_text()
        text=re.sub(r'104 plain-English terms',str(len(terms))+' plain-English terms',text)
        if 'href="/caregiver-glossary.html"' not in text:
            anchor='<h2 id="practical-title">What would help today?</h2>'
            if anchor not in text:raise ValueError('Caregiver hub anchor changed')
            text=text.replace(anchor,anchor+'<p class="care-more-story"><a href="/caregiver-glossary.html">The expanded caregiver’s glossary</a> — '+str(len(terms))+' terms, everyday examples and questions for your next meeting.</p>',1)
        hub.write_text(text)
    plain=' '.join(' '.join(str(t.get(k,'')) for k in ('term','plain','detail','why','look','do','ask','note')) for t in terms)
    report={'entries':len(terms),'words':len(plain.split()),'unique_names':len({t['term'] for t in terms}),'unique_icons':len({art.spec_for(t) for t in terms}),'categories':{c:sum(t['cat']==c for t in terms) for c in CATS},'sources_per_entry':all(t['sources'] for t in terms),'version':'20261020-expanded-v2'}
    (root/'assets/glossary-v2-build-report.json').write_text(json.dumps(report,indent=2))
    if report['unique_icons']!=len(terms):raise ValueError('Repeated icon compositions; review semantic mapping')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));build(p.parse_args().root)
