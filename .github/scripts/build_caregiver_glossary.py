#!/usr/bin/env python3
"""Compatibility entry point and final integration for the glossary edition."""
import argparse, importlib.util, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('glossary_v2',HERE/'glossary_v2.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
_original_revise=core.revise

def reviewed_revise(terms,sources):
    terms=_original_revise(terms,sources)
    advocacy={'label':'ASAN: For Whose Benefit? (includes Easy Read and Plain Language)','url':'https://autisticadvocacy.org/policy/briefs/intervention-ethics/','kind':'Autistic-led critique'}
    for term in terms:
        if term['term'] in ('ABA — Applied Behavior Analysis','Social validity','Neurodiversity-affirming practice'):
            term['sources'].append(dict(advocacy))
        if term['term']=='Gestalt language processing (GLP)':
            term['sources'].extend([
                {'label':'Lorang and colleagues: GLP/NLA—concerns and common ground','url':'https://pubs.asha.org/doi/10.1044/2025_PERSP-25-00055','kind':'Research-informed critique'},
                {'label':'Blanc and colleagues: the proposed NLA framework','url':'https://pubs.asha.org/doi/10.1044/2023_PERSP-23-00098','kind':'Proponents’ viewpoint; not proof of effectiveness'}])
        if term['term']=='Massachusetts N1 & N2 notices':
            term['sources'].append({'label':'Massachusetts DESE: Notice of School District Refusal to Act','url':'https://www.doe.mass.edu/specialeducation/iep/refusal-to-act/','kind':'Massachusetts official form'})
        if term['term'] in ('Supported decision-making','Autonomy & self-determination'):
            term['sources'].append({'label':'ASAN: self-determination and the right to make choices','url':'https://autisticadvocacy.org/self-determination/','kind':'Autistic-led rights guidance'})
    additions=[
        dict(term='Multilingual communication & AAC',cat='Communication',
             plain='Communication support that includes the languages a person uses with family and community.',
             detail='AAC assessment should consider the person’s languages, vocabulary, communication partners and cultural context. A system that works only in English may leave someone unable to participate with important people in their life.',
             why='A family should not have to choose between communication access and their home language.',
             look='A person uses one language with a grandparent and another at school. Their communication board or device needs useful vocabulary and partner support for both settings.',
             do='Tell the SLP which languages matter, who uses them and when. Ask about multilingual vocabulary, switching languages and trained interpretation for assessment or meetings.',
             ask='How will this communication system help me communicate with my family in the languages we actually use?',
             note='Knowing more than one language is not itself a communication disorder. A translated word list alone does not establish that a system is accessible or culturally appropriate.',
             sources=[{'label':'ASHA: Multilingual service delivery','url':'https://www.asha.org/practice-portal/professional-issues/multilingual-service-delivery/','kind':'Professional guidance'},{'label':'ASHA: Augmentative and alternative communication','url':'https://www.asha.org/practice-portal/professional-issues/augmentative-and-alternative-communication/','kind':'Clinical guidance'}],related=['AAC','Communication partner','Multimodal communication']),
        dict(term='Plain language & Easy Read',cat='Identity & support',
             plain='Two ways to make information easier to understand. They are related, but not identical.',
             detail='Plain language uses familiar words, clear organization and direct explanations. Easy Read typically adds shorter text, generous spacing and pictures that support each idea. A page is not necessarily Easy Read just because it has pictures or a larger-text button.',
             why='People need usable information to take part in decisions about their lives.',
             look='A service sends a long care document. The person asks for a short explanation, relevant pictures and time to discuss one decision at a time.',
             do='Ask what format the person prefers. Check understanding without turning the conversation into a test, and offer another explanation when needed.',
             ask='Can you explain the choices in a format I can understand and give me time to ask questions?',
             note='This glossary uses plain-language explanations; it is not a validated Easy Read edition. Pictures and simplified wording should support access without replacing important details.',
             sources=[{'label':'ASAN: Plain Language Resources','url':'https://autisticadvocacy.org/resources/','kind':'Autistic-led accessible resources'}],related=['Supported decision-making','Communication Bill of Rights']),
        dict(term='Self-advocacy & supported self-advocacy',cat='Rights & safety',
             plain='Expressing what matters to you and having help to do that when you need it.',
             detail='Self-advocacy can include speech, AAC, gestures, signs, choosing between options or clearly refusing. Supporters can help someone understand choices and communicate a view without substituting their own preference. Advocacy is not reserved for people who can speak, read or manage a meeting independently.',
             why='A caregiver’s knowledge matters, and the disabled person’s own preferences also need a reliable way into decisions.',
             look='Before a planning meeting, someone reviews accessible choices with a trusted supporter. During the meeting, the team addresses them directly and waits for their response.',
             do='Ask the person how they want to participate. Record what they expressed, what was observed and what a supporter is interpreting as separate information.',
             ask='What support would let me have more say in this decision?',
             note='An interpretation of behavior is not automatically a confirmed statement of the person’s wishes. Be transparent about uncertainty and keep offering accessible ways to agree, disagree or change course.',
             sources=[{'label':'ASAN: What we believe','url':'https://autisticadvocacy.org/about-asan/what-we-believe/','kind':'Autistic-led rights perspective'},{'label':'NJC: Communication Bill of Rights, third edition','url':'https://www.asha.org/njc/communication-bill-of-rights/','kind':'Communication rights guidance'}],related=['Assent','Autonomy & self-determination','Supported decision-making'])
    ]
    for item in additions:
        item['flag']=''
        terms.append(item)
    for term in terms:
        if term['term']=='Disability justice & intersectionality':
            term['do']='Ask whose access needs are being missed: people of color, LGBTQ+ people, multilingual families, people with intellectual disabilities and people with fewer financial resources. Offer concrete participation supports, and avoid asking one person to represent everyone.'
            term['sources'].append({'label':'ASAN: Civil rights are disability rights','url':'https://autisticadvocacy.org/about-asan/solidarity/','kind':'Autistic-led rights perspective'})

    autistic_sources={
        'asan':{'label':'ASAN: What we believe','url':'https://autisticadvocacy.org/about-asan/what-we-believe/','kind':'Autistic-led rights perspective'},
        'profound':{'label':'ASAN: The “profound autism” label hurts autistic people — Plain Language toolkit','url':'https://autisticadvocacy.org/the-profound-autism-label-hurts-autistic-people/','kind':'Autistic-led critique of the label'},
        'listen':{'label':'CommunicationFIRST: LISTEN — made by and with nonspeaking autistic people','url':'https://communicationfirst.org/listen/','kind':'Nonspeaking autistic perspectives'},
        'meetings':{'label':'CommunicationFIRST: Meeting tips by AAC users','url':'https://communicationfirst.org/best-practices-for-online-meetings/','kind':'AAC-user-authored access guidance'},
        'sartac':{'label':'SARTAC: Self-advocacy and the intellectual-disability rights movement','url':'https://selfadvocacyinfo.org/self-advocacy/','kind':'Self-advocacy resource'},
        'inclusion':{'label':'Listen Include Respect: Supporting self-advocacy','url':'https://www.listenincluderespect.com/supporting-self-advocacy','kind':'Inclusive participation guidance'},
        'actually':{'label':'Reframing Autism: Learn from #ActuallyAutistic voices','url':'https://reframingautism.org.au/service/i-am-an-ally/','kind':'Autistic-led community guidance'},
        'rights':{'label':'NJC: Communication Bill of Rights','url':'https://www.asha.org/njc/communication-bill-of-rights/','kind':'Communication rights guidance'}
    }
    new_rows=[
      ('Actually Autistic / #ActuallyAutistic','Identity & support','A phrase and hashtag used to foreground autistic people’s own experiences.',
       'It helps readers find accounts from autistic people rather than only commentary about them. Autistic people differ in communication, cognition, culture and support needs; one account cannot stand in for everyone.',
       'First-person perspectives can reveal barriers a supporter has not noticed.',
       'A family reads an autistic person’s explanation of sensory distress, then checks what helps their own family member.',
       'Seek a range of autistic perspectives, including nonspeaking contributors and people with intellectual disabilities. Keep the individual’s own needs central.',
       'Whose first-person experiences are missing from what we are reading?',
       'A hashtag is not a professional credential or proof that a claim is accurate. Nobody owes public disclosure or a personal story to deserve respect.',
       ['actually'],['Self-advocacy & supported self-advocacy','High support needs']),
      ('Autistic-led advocacy','Rights & safety','Advocacy in which autistic people help set the priorities and hold meaningful decision-making power.',
       'Consultation is useful, but leadership also concerns who decides, who is paid and whose disagreement can change the outcome. Families and professionals can contribute without replacing autistic leadership.',
       'A service can praise inclusion while making every decision without its users.',
       'A provider gives autistic advisers accessible proposals, preparation time and a real role in choosing changes.',
       'Ask how people with extensive support needs are included, what support is funded and what changed because of their input.',
       'Which decisions can autistic participants actually influence?',
       'This glossary is a family-publication resource informed by linked autistic-led work. It has not been reviewed or endorsed by those organizations, and it does not claim to speak for autistic people.',
       ['asan','inclusion'],['Nothing about us without us','Supported participation & accessible meetings']),
      ('Nothing about us without us','Rights & safety','People affected by a decision should have a meaningful part in making it.',
       'In autism advocacy, this means involving autistic people in decisions about autism. Extensive support needs call for better access and support, rather than automatic exclusion.',
       'Being discussed is different from being included.',
       'A planning team asks the person’s preferences before agreeing on a new daily routine.',
       'Offer accessible information and a way to respond before the decision is settled. Explain what changed after listening.',
       'How will my views affect this decision?',
       'Participation need not involve a public meeting, speech or agreeing with the group. A person can choose privacy or decline to participate.',
       ['asan'],['Autistic-led advocacy','Person-centered planning']),
      ('Interdependence','Adult life & services','People supporting one another, including when someone needs extensive or lifelong assistance.',
       'Autonomy concerns having a say in life; independence concerns doing things without assistance. Someone can need help with every personal-care task and still have preferences about how that help happens.',
       'Progress can include better support and greater choice without a reduction in care hours.',
       'A person needs hands-on dressing support and chooses the comfortable shirt, the helper or the order of the routine.',
       'Write goals for comfort, relationships, participation and influence alongside any skill goals. Keep essential assistance available.',
       'What would give me more choice while keeping the help I need?',
       'Needing support is not a failure. Family and paid supporters also need sustainable staffing, training, rest and backup.',
       ['asan','sartac'],['Autonomy & self-determination','High support needs','Quality of life']),
      ('Supported participation & accessible meetings','Rights & safety','Changing the format and providing assistance so someone can take part in a decision.',
       'Options include advance questions, pictures or objects, shorter sessions, quiet space, a trusted supporter, AAC and responses outside the meeting. Access should match the individual, rather than require everyone to use the same format.',
       'Fast conversation can exclude someone even when they are physically present.',
       'A team sends choices ahead of time and pauses while an AAC user finishes a message.',
       'Ask about access before the meeting. Address the person directly and record their contribution separately from a supporter’s interpretation.',
       'Can we change the format so I can take part?',
       'An AAC user’s account does not establish that every nonspeaking person has the same skills or support needs. Offer options and check what works.',
       ['meetings','inclusion'],['Processing time / latency','Self-advocacy & supported self-advocacy','Plain language & Easy Read']),
      ('Dissent / saying no','Rights & safety','Expressing disagreement, refusal or a wish to stop.',
       'Dissent may be expressed through speech, AAC, gesture or actions. A changed expression or movement is a reason to check what is happening, rather than assume either agreement or a specific meaning.',
       'A useful communication system must make disagreement possible.',
       'Someone pushes an activity away. A supporter pauses, checks discomfort and offers a break or another way to participate.',
       'Make stop, no, help and break available. Document how supporters respond and how uncertainty is checked.',
       'What happens when I say no?',
       'Essential care and immediate safety can involve difficult decisions. Use appropriate clinical guidance, explain what is happening and seek the least restrictive workable approach. Silence alone is not assent.',
       ['rights'],['Assent','Consent','Functional noncompliance / safe refusal'])
    ]
    for name,cat,plain,detail,why,look,action,ask,note,keys,related in new_rows:
        terms.append(dict(term=name,cat=cat,plain=plain,detail=detail,why=why,look=look,do=action,ask=ask,note=note,sources=[dict(autistic_sources[k]) for k in keys],related=related,flag=''))
    changes={
      'High support needs':('Name the actual help needed: communication access, personal care, health support, supervision and staffing. Also record choices, relationships and interests. Needing round-the-clock assistance does not remove someone’s right to influence daily life.',['asan','sartac']),
      'Profound autism':('Read the proposed research definition alongside autistic-led objections. Describe the person’s actual communication, intellectual disability, health and daily support needs rather than treating the label as a complete profile.',['profound']),
      'Presume competence':('Offer age-respectful communication and learning access without making someone prove worthiness first. Recognize genuine intellectual disability and teach at an accessible pace; dignity does not depend on hidden academic abilities.',['listen']),
      'Inclusion':('Check whether the person can choose, communicate, rest, form relationships and participate meaningfully. Fund the personal care, transport, sensory and staffing supports needed for access.',['inclusion']),
      'Stimming':('Protect harmless stimming and make regulation supports available. If an action causes injury, investigate pain, distress and safer options rather than making looking less autistic the objective.',['actually']),
      'Person-centered planning':('Ask what the person enjoys, avoids and wants to change using accessible options. Identify who will make their preferences happen, including when lifelong hands-on assistance is needed.',['inclusion']),
      'Social validity':('Review whose goals are being served. Include the autistic person’s comfort, refusal, preferences and relationships; a quieter or more compliant person is not automatically better supported.',['asan']),
      'Self-advocacy & supported self-advocacy':('Include everyday decisions as well as formal advocacy. Offer access to peers and self-advocacy groups with suitable support, without requiring a person to represent others or disclose private experiences.',['sartac','inclusion']),
      'Quality of life':('Review personally meaningful comfort, enjoyment, relationships and influence. Separate the person’s own report, observed patterns and supporter judgments; explain disagreements instead of collapsing them into one score.',['sartac'])
    }
    for term in terms:
        if term['term'] in changes:
            term['do'],keys=changes[term['term']]
            existing={source['url'] for source in term['sources']}
            term['sources'].extend(dict(autistic_sources[k]) for k in keys if autistic_sources[k]['url'] not in existing)
        if term['term']=='Profound autism':
            term['note']='Debated term. ASAN argues that the label can reinforce segregation and mistaken assumptions about people with intellectual and communication disabilities. Supporters argue that it makes persistent, intensive support needs visible. Disagreement about a label must not become a reason to withhold care, communication access or community inclusion.'
    return terms
core.revise=reviewed_revise
_base_icon=core.art.spec_for
_voice_icons={'Actually Autistic / #ActuallyAutistic':'person,dialogue,book','Autistic-led advocacy':'people,speech,checklist','Nothing about us without us':'people,document,support','Interdependence':'home,people,linked','Supported participation & accessible meetings':'calendar,device,people','Dissent / saying no':'speech,pause,person'}
core.art.spec_for=lambda term: _voice_icons[term['term']] if term['term'] in _voice_icons else _base_icon(term)

CSS='''/* Final glossary integration: native no-JS reading and unobscured headings. */
.cg-root:not(.cg-enhanced) .cg-workspace{display:block}
.cg-root:not(.cg-enhanced) .cg-start nav{display:none!important}
.cg-tools>summary{display:flex;align-items:center;justify-content:center;gap:8px;white-space:nowrap}
.cg-tools>summary::after{display:inline!important;position:static!important;font-size:12px;margin:0!important}
.cg-term{scroll-margin-top:calc(var(--cg-toolbar-height,180px) + 18px)}
.cg-sidebar{top:calc(var(--cg-toolbar-height,160px) + 20px)}
.cg-mobile-start{display:none}
@media(max-width:760px){
.cg-root .cg-start{display:none}
.cg-root .cg-mobile-start{display:block;margin-top:18px;border:1px solid var(--cg-line);border-radius:12px;background:var(--cg-soft);padding:0 15px;font-size:14px}
.cg-mobile-start>summary{min-height:48px;padding:12px 0;font-weight:700}
.cg-mobile-start nav{display:grid;gap:4px;padding-bottom:12px}
.cg-mobile-start nav button{display:flex;justify-content:space-between;gap:10px;background:transparent;border:0;border-top:1px solid var(--cg-line);font-size:14px;border-radius:0;padding:11px 0}
.cg-root .cg-reading-row #cg-compare{display:none}
.cg-tools>summary{min-height:44px;font-size:13px}
.cg-tools>div{top:51px}
.cg-term{scroll-margin-top:calc(var(--cg-toolbar-height,205px) + 18px)}
}
@media print{.cg-mobile-start{display:none!important}}
'''
JS='''/* Final glossary toolbar measurements and compact mobile menu. */
(()=>{const root=document.querySelector('.cg-v2.cg-enhanced');if(!root)return;
const toolbar=root.querySelector('#cg-search-tools');
const measure=()=>{if(toolbar)root.style.setProperty('--cg-toolbar-height',Math.ceil(toolbar.getBoundingClientRect().height)+'px');};
measure();if(typeof ResizeObserver==='function')new ResizeObserver(measure).observe(toolbar);else window.addEventListener('resize',measure);
root.querySelectorAll('[data-tool="compare"]').forEach(button=>button.addEventListener('click',()=>root.querySelector('#cg-compare').click()));
})();
'''

def build(root):
    root=Path(root);core.build(root)
    page=root/'caregiver-glossary.html'
    if not page.exists():return
    text=page.read_text()
    text=text.replace('<button data-tool="questions">Print my saved questions</button>','<button data-tool="questions">Print my saved questions</button><button data-tool="compare">Often mixed-up terms</button>',1)
    aside=re.search(r'<aside class="cg-start">(.*?)</aside>',text,re.S)
    if aside:
        nav=re.search(r'<nav[^>]*data-js>(.*?)</nav>',aside[1],re.S)
        if nav:
            mobile='<details class="cg-mobile-start" data-js><summary>Not sure? Browse by situation</summary><nav aria-label="Situations on a small screen">'+nav[1]+'</nav></details>'
            marker='<p class="cg-reassure">You do not need to learn every word. Find the one you need today.</p>'
            text=text.replace(marker,marker+mobile,1)
    text=text.replace('<section class="cg-closing">', '<section class="cg-closing" id="autistic-self-advocacy" aria-labelledby="autistic-self-advocacy-title"><div><p class="cg-eyebrow">Autistic perspectives · meaningful participation</p><h2 id="autistic-self-advocacy-title">A say in your own life.</h2></div><div><p>Needing extensive or lifelong help does not make someone less entitled to communication, belonging, privacy or choice. Self-advocacy can happen in small everyday decisions and with substantial support.</p><p>Begin with the person: offer accessible choices; make no, stop and help usable; allow processing time; and distinguish what they communicated from what someone else interpreted. When preferences are unclear, keep checking. Do not invent a first-person account on their behalf.</p><p>Autistic people with intellectual disabilities and nonspeaking autistic people belong in autism advocacy. Families bring important knowledge, while the person’s own experience deserves a direct route into decisions. No single advocate represents everybody, and no one needs to be a public advocate to deserve rights.</p><p>Start with <a href="#term-self-advocacy-supported-self-advocacy">supported self-advocacy</a>, <a href="#term-dissent-saying-no">saying no</a>, <a href="#term-supported-participation-accessible-meetings">accessible meetings</a> and <a href="#term-interdependence">interdependence</a>.</p><p><a href="https://communicationfirst.org/listen/">LISTEN: a film made by and with nonspeaking autistic people</a> offers first-person perspectives. Its full version addresses restraint; shorter and audio-described options and transcripts are available. <a href="https://selfadvocacyinfo.org/self-advocacy/">SARTAC introduces the intellectual-disability self-advocacy movement</a>. <a href="https://autisticadvocacy.org/the-profound-autism-label-hurts-autistic-people/">ASAN’s Plain Language toolkit explains its objections to “profound autism”</a>; the glossary also explains why some researchers and families use the term.</p><p>This is an editorial guide informed by these resources, not an autistic-authored testimony or a claim of endorsement. Listening to autistic people includes listening when their perspectives challenge our assumptions.</p></div></section>'+'<section class="cg-closing">',1)
    text=text.replace('<p class="cg-reassure">', '<p><a href="#autistic-self-advocacy">Autistic perspectives and self-advocacy with extensive support needs ↗</a></p><p class="cg-reassure">',1)
    text=text.replace('Updated October 20, 2026.', 'Updated October 21, 2026.')
    text=text.replace('We use autistic person by default and respect individual preference.', 'This guide welcomes disabled readers, family members, paid supporters and professionals. We use autistic person by default and respect individual preference. Language, race, income, gender and family structure can affect access; nobody should have to use the perfect vocabulary to ask for help.')
    text=text.replace('20261020-expanded-v2','20261021-inclusive-v3')
    page.write_text(text,encoding='utf-8')
    for path,addition,marker in [(root/'assets/caregiver-glossary.css',CSS,'/* Final glossary integration:'),(root/'assets/caregiver-glossary.js',JS,'/* Final glossary toolbar measurements')]:
        source=path.read_text()
        if marker not in source:path.write_text(source+'\n'+addition,encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('.'))
    build(parser.parse_args().root)
