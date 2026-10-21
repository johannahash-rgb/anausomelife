"""Term-specific editorial SVG illustrations. No category-level fallback or emoji.
Reusable drawing primitives are combined intentionally for each term; they are
illustrations beside written labels, never a replacement for accessible language.
"""
import html

P = {
'person':'<circle cx="16" cy="8" r="4"/><path d="M8 28v-8a8 8 0 0 1 16 0v8M12 28v-6m8 6v-6"/>',
'people':'<circle cx="10" cy="9" r="3.5"/><circle cx="23" cy="11" r="3.5"/><path d="M3 27v-6a7 7 0 0 1 14 0v6m2-8a6 6 0 0 1 10 5v3"/>',
'support':'<circle cx="16" cy="16" r="4"/><circle cx="5" cy="5" r="2"/><circle cx="27" cy="5" r="2"/><circle cx="16" cy="29" r="2"/><path d="m8 8 5 5m11-5-5 5m-3 7v6"/>',
'speech':'<path d="M6 4h20a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3H13l-7 5v-5a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3Z"/><path d="M9 11h14M9 16h10"/>',
'blank':'<path d="M6 4h20a3 3 0 0 1 3 3v14a3 3 0 0 1-3 3H13l-7 5v-5a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3Z"/>',
'dialogue':'<path d="M3 4h19v13H10l-5 4v-4H3Zm10 19h10l5 5v-5h2V12h-4"/><path d="M8 9h9"/>',
'device':'<rect x="5" y="2" width="22" height="28" rx="3"/><rect x="9" y="6" width="5" height="5" rx="1"/><rect x="18" y="6" width="5" height="5" rx="1"/><rect x="9" y="15" width="5" height="5" rx="1"/><rect x="18" y="15" width="5" height="5" rx="1"/><path d="M13 26h6"/>',
'grid':'<rect x="3" y="4" width="26" height="24" rx="2"/><path d="M3 12h26M3 20h26M12 4v24M21 4v24"/>',
'book':'<path d="M16 7C12 3 6 3 2 5v23c5-2 10-2 14 1 4-3 9-3 14-1V5c-4-2-10-2-14 2Zm0 0v22"/><path d="M6 11h6M6 16h6M20 11h6M20 16h6"/>',
'document':'<path d="M6 2h14l7 7v21H6Zm14 0v8h7M10 16h13M10 21h13M10 26h8"/>',
'checklist':'<rect x="5" y="4" width="22" height="26" rx="2"/><path d="M11 4V2h10v2M9 12l2 2 3-4m3 2h6M9 21l2 2 3-4m3 2h6"/>',
'calendar':'<rect x="3" y="6" width="26" height="24" rx="3"/><path d="M3 13h26M10 2v8M22 2v8M9 19h3m6 0h4M9 25h3m6 0h4"/>',
'clock':'<circle cx="16" cy="17" r="12"/><path d="M16 9v8l6 4M12 2h8"/>',
'arrow':'<path d="M3 16h25m-8-8 8 8-8 8"/>',
'switch':'<path d="M3 9h24l-5-5m5 5-5 5M29 23H5l5-5m-5 5 5 5"/>',
'route':'<circle cx="5" cy="26" r="3"/><circle cx="27" cy="5" r="3"/><path d="M8 26h10c11 0 11-12 0-12H9c-6 0-6-9 0-9h15"/>',
'paths':'<path d="M3 27 16 14 29 4M16 14 9 4m7 10 13 13M3 27h6m-6 0v-6"/>',
'dots':'<circle cx="5" cy="7" r="2"/><circle cx="16" cy="16" r="2"/><circle cx="27" cy="25" r="2"/><path stroke-dasharray="2 3" d="m7 9 7 5m4 4 7 5"/>',
'steps':'<path d="M2 29h8v-8h8v-8h8V4h4"/><path d="m4 16 9-9m-9 0h9v9"/>',
'hand':'<path d="M11 18V7c0-4 4-4 4 0v8-11c0-4 4-4 4 0v11-8c0-4 4-4 4 0v10-4c0-4 4-4 4 0v9c0 7-4 9-9 9-6 0-7-4-10-8l-5-7c-2-3 1-6 4-3l4 4Z"/>',
'ear':'<path d="M8 12c0-13 21-13 21 0 0 8-9 7-10 13-1 8-11 7-11 0M13 12c0-6 10-6 10 0 0 4-6 4-6 8"/>',
'eye':'<path d="M2 16c8-14 20-14 28 0-8 14-20 14-28 0Z"/><circle cx="16" cy="16" r="5"/>',
'wave':'<path d="M2 17h5l4-10 6 21 5-15 3 4h5"/>',
'body':'<circle cx="16" cy="5" r="3"/><path d="M9 12c-4 3-5 9-5 15m19-15c4 3 5 9 5 15M9 12v18m14-18v18M9 12c4 2 10 2 14 0"/>',
'heart':'<path d="M16 29 4 17C-5 5 10-4 16 7c6-11 21-2 12 10Z"/>',
'cup':'<path d="M4 6h19v15c0 10-19 10-19 0Zm19 3h4c7 0 7 11-4 11M3 31h23"/>',
'drop':'<path d="M16 2C12 10 4 15 4 22a12 12 0 0 0 24 0c0-7-8-12-12-20Z"/><path d="M9 22c0 4 3 6 6 6"/>',
'stomach':'<path d="M13 2v10c0 8-8 3-9 10-1 9 12 10 20 4 8-7 5-19-2-18-4 1-4 4-5 0V2"/>',
'plate':'<circle cx="17" cy="16" r="10"/><circle cx="17" cy="16" r="6"/><path d="M2 2v9m4-9v9m-4-5h4M4 11v19M30 2v28"/>',
'chair':'<path d="M8 3h15v15H8Zm-3 15h22v7H5Zm3 7v6m16-6v6"/>',
'shirt':'<path d="m10 3-8 5 4 8 5-3v17h15V13l4 3 2-8-9-5c-3 5-9 5-13 0Z"/>',
'home':'<path d="m1 14 15-12 15 12M5 11v19h22V11M12 30V19h8v11"/>',
'community':'<path d="M2 30V15h9v15m2 0V4h9v26m2 0V11h7v19M1 30h31M16 10h3m-3 6h3m-3 6h3"/>',
'door':'<path d="M6 30V2h20v28M10 29V5l13 3v19Zm8-12h1"/>',
'boundary':'<path d="M7 3H2v26h5M25 3h5v26h-5M7 16h18m-14-4-4 4 4 4m10-8 4 4-4 4"/>',
'shield':'<path d="M16 2 29 7v10c0 7-6 12-13 15C9 29 3 24 3 17V7Z"/>',
'lock':'<rect x="5" y="13" width="22" height="17" rx="3"/><path d="M10 13V8a6 6 0 0 1 12 0v5M16 19v6"/>',
'check':'<path d="m4 16 8 8L29 5"/>',
'plus':'<path d="M16 3v26M3 16h26"/>',
'minus':'<path d="M3 16h26"/>',
'pause':'<path d="M10 3v26M23 3v26"/>',
'magnify':'<circle cx="13" cy="13" r="10"/><path d="m21 21 10 10"/>',
'chart':'<path d="M3 2v27h28M7 22l7-9 6 4 9-13"/>',
'measure':'<path d="M3 26h27M7 22V7m6 15V12m6 10V3m6 19V9"/>',
'cycle':'<path d="M27 11C21-1 4 2 3 15M27 4v7h-7M5 23c8 12 24 3 24-6M5 30v-7h7"/>',
'open-cycle':'<path d="M26 10C18-2 3 5 3 17c0 9 10 14 18 10M26 3v7h-7"/><path stroke-dasharray="2 3" d="M26 25c4-4 5-8 3-12"/>',
'infinity':'<path d="M16 16c-6-12-15-11-15 0s9 12 15 0 15-11 15 0-9 12-15 0Z"/>',
'ramp':'<path d="M2 28h28V8ZM5 19 25 5m-8 0h8v8"/>',
'headphones':'<path d="M3 19V14a13 13 0 0 1 26 0v5M3 15h6v14H3Zm20 0h6v14h-6Z"/>',
'swing':'<path d="M3 31 9 2h14l7 29M12 3v20m8-20V3M8 23h16v5H8Z"/>',
'balance':'<path d="M2 25c10 8 20 8 29 0M16 4v19m-9-2 9-7 9 7"/><circle cx="16" cy="3" r="2"/>',
'sun':'<circle cx="16" cy="16" r="7"/><path d="M16 1v4m0 22v4M1 16h4m22 0h4M5 5l3 3m16 16 3 3M5 27l3-3M24 8l3-3"/>',
'moon':'<path d="M23 3C5-3-5 20 10 29c9 5 19-1 20-10C14 27 6 11 23 3Z"/>',
'leaf':'<path d="M4 29c-6-19 5-23 25-26 0 21-9 29-25 26Zm0 0L24 8M12 20v-9m0 9h10"/>',
'envelope':'<rect x="2" y="5" width="28" height="23" rx="2"/><path d="m2 7 14 12L30 7"/>',
'pen':'<path d="m5 24 17-21 7 6L12 29l-9 2Zm0 0 7 5M20 5l7 6"/>',
'scales':'<path d="M16 2v28M8 30h16M3 8h26M8 8l-6 12h12Zm17 0-6 12h12Z"/>',
'bus':'<rect x="3" y="2" width="26" height="26" rx="4"/><path d="M6 8h20v10H6ZM7 28v3m18-3v3M8 23h1m14 0h1"/>',
'bed':'<path d="M2 5v26M2 15h23c6 0 6 6 6 6v10M2 24h29"/><rect x="5" y="9" width="8" height="6" rx="2"/>',
'linked':'<rect x="2" y="7" width="18" height="10" rx="5" transform="rotate(-30 11 12)"/><rect x="12" y="16" width="18" height="10" rx="5" transform="rotate(-30 21 21)"/>',
'flag':'<path d="M5 31V3h23l-6 6 6 6H5"/>',
'focus':'<circle cx="16" cy="16" r="11"/><circle cx="16" cy="16" r="4"/><path d="M16 1v4m0 22v4M1 16h4m22 0h4"/>',
'gift':'<rect x="3" y="12" width="26" height="7"/><path d="M5 19v12h22V19M16 12v19M16 12C-1 12 3-5 12 5Zm0 0c17 0 13-17 4-7Z"/>',
'plant':'<path d="M16 29V14M16 19C2 19 1 7 1 7c14 0 15 7 15 12Zm0-5C29 14 31 2 31 2 19 2 16 7 16 14ZM6 30h20"/>',
'question':'<path d="M10 10c-1-10 17-10 15 0-1 5-9 5-9 12"/><circle cx="16" cy="29" r="1"/>',
'letters':'<path d="m2 28 7-23 7 23M5 18h9M22 5v23h6M22 16h5M22 5h6"/>',
'notice':'<rect x="4" y="3" width="24" height="27" rx="2"/><path d="M16 8v10M9 25h14"/><circle cx="16" cy="21" r=".7"/>',
'bridge':'<path d="M1 24h30M4 24V7m24 17V7M4 8c7 12 17 12 24 0M10 24V15m6 9v-5m6 5v-9"/>',
'withdraw':'<path d="M28 16H3m8-8-8 8 8 8M29 2v28"/>',
'health':'<rect x="2" y="8" width="28" height="23" rx="3"/><path d="M10 8V2h12v6M16 14v11m-5-5h10"/>',
'fork':'<path d="M16 30V15M16 15 4 3m0 8V3h8m4 12L28 3m-8 0h8v8"/>',
'object':'<path d="m3 10 13-7 13 7v15l-13 6-13-6Zm0 0 13 7 13-7M16 17v14"/>',
'handed':'<path d="M2 23h8l5-4h13c4 0 4 4 0 5l-12 6H2M10 12h16m-5-5 5 5-5 5"/>',
'brain':'<path d="M16 5C9-3 2 6 6 11-9 21 5 34 15 27M16 5c7-8 14 1 10 6 15 10 1 23-9 16M16 5v23M6 11l6 3m14-3-6 3M6 24l6-4m14 4-6-4"/>',
}

def draw(spec, title):
    a,b,label=(spec.split(',')+['',''])[:3]
    if a not in P or (b and b not in P):
        raise ValueError('Unknown icon composition: '+spec)
    main='<g transform="translate(7 6) scale(1.45)">'+P[a]+'</g>'
    badge=''
    if b:
        badge='<rect x="34" y="34" width="29" height="29" rx="10" fill="#edf1e9" stroke="#d1ddd2"/><g transform="translate(39 39) scale(.60)" stroke="#486655">'+P[b]+'</g>'
    if label:
        badge+='<rect x="0" y="47" width="'+str(max(20,len(label)*6+8))+'" height="17" rx="5" fill="#fbf8f1" stroke="none"/><text x="4" y="59" fill="#173c4c" stroke="none" font-family="Arial,sans-serif" font-size="10" font-weight="700">'+html.escape(label)+'</text>'
    return '<svg class="cg-art" viewBox="0 0 64 66" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false"><title>'+html.escape(title)+'</title><path d="M4 19C5 3 42-2 54 11s10 31-2 43S-1 51 4 19" fill="#edf1e9"/><g fill="none" stroke="#173c4c" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'+main+badge+'</g></svg>'

# The first field matches an existing entry prefix; every existing term is mapped.
OLD = '''Autism /|infinity,person
High support|person,support
Profound|person,clock
Level 3|support,document,3
Neurodiversity /|paths,infinity
Identity-first|document,person,ID
Intellectual|book,steps
Adaptive|person,checklist
ADLs|shirt,hand
IADLs|home,checklist
Presume|book,door
Autonomy|person,fork
Ableism|ramp,boundary
Age-respectful|person,shield
Speech vs.|speech,letters
Multimodal|dialogue,device
AAC —|device,speech,AAC
Aided &|device,hand
Speech-generating|device,wave,SGD
Core &|grid,plant
Aided language|device,people
Communication partner|people,dialogue
Access method|device,focus
Eye gaze|eye,device
Receptive|ear,speech
Expressive|speech,arrow
Nonspeaking|hand,speech
Unreliable|speech,clock
Minimally|speech,device
Apraxia|dots,speech
Aphasia|letters,dialogue
Dysarthria|speech,wave
Echolalia|speech,cycle
Scripting|book,speech
Gestalt|linked,speech,GLP
Processing time|clock,speech
Functional communication|speech,door
Yes/no|dialogue,fork
Sensory processing|ear,eye
Sensory overload|wave,headphones
Interoception|body,heart
Proprioception|body,measure
Vestibular|balance,swing
Sensory seeking|headphones,switch
Stimming|hand,cycle
Co-regulation|people,wave
Self-regulation|person,wave
Meltdown|wave,shield
Shutdown|person,pause
Motor planning|dots,body
Behavior|person,magnify
Antecedent|route,document,ABC
Reinforcement|cycle,plus
Positive reinforcement|plus,cycle
Negative reinforcement|minus,cycle
Natural reinforcement|plant,cycle
Punishment|chart,minus
Extinction (|open-cycle,question
Function of|magnify,route
FBA|magnify,checklist,FBA
BIP /|checklist,paths,BIP
Replacement|fork,check
Prompting|hand,arrow
Prompt fading|dots,arrow
Generalization|bridge,community
ABA —|chart,person,ABA
PBIS|community,checklist,PBIS
IDEA —|scales,book,IDEA
IEP —|document,person,IEP
FAPE —|book,shield,FAPE
LRE —|door,people,LRE
Placement|community,paths
Inclusion|people,door
Special education|book,pen
Related services|health,book
Supplementary|book,plus
Accommodations|ramp,book
Modifications|book,switch
PLAAFP|measure,document
Annual goals|flag,calendar
Progress monitoring|chart,calendar
Evaluation|magnify,book
Reevaluation|magnify,cycle
IEE —|magnify,people,IEE
Prior Written|envelope,notice,PWN
Procedural|shield,document
Parent participation|people,pen
IEP Team|people,document,IEP
Parental consent|pen,document
Assistive technology|device,ramp,AT
ESY|calendar,sun,ESY
Transition services|bridge,book
Manifestation|scales,question,MDR
Transportation|bus,support
School nursing|health,community
Consent|pen,check
Assent|hand,check
Functional noncompliance|hand,shield
Elopement|door,route
Restraint|boundary,hand
Seclusion|door,boundary
Safety plan|shield,checklist
Communication under|speech,shield
Pain communication|body,speech'''
NEW = '''access-ramp|ramp,person
barrier-ramp|boundary,ramp
intersecting-paths|paths,people
choice-path|fork,person
two-perspectives|dialogue,people
face-and-dialogue|person,dialogue
energy-and-rest|bed,pause
feelings-and-words|heart,question
focused-attention|focus,paths
start-and-switch|pause,switch
demand-and-choice|checklist,fork
supported-route|route,support
decision-with-support|fork,support
decision-options|fork,question
legal-scope|scales,boundary
person-and-plan|person,document
rights-and-dialogue|shield,speech
 aac-expanded|device,plus
paper-communication|grid,document
repair-dialogue|dialogue,switch
tactile-symbols|object,hand
picture-exchange|grid,handed
authorship|pen,person
many-modes|dialogue,hand
request|speech,cup
comment-on-object|speech,object
question-answer|dialogue,question
echoed-sound|wave,cycle
speech-professional|speech,health
daily-activity-tools|shirt,checklist
mobility-support|body,support
supervision-team|people,checklist
support-companion|people,support
classroom-support|people,book
steps|steps,checklist
gradual-steps|steps,plant
linked-steps|steps,linked
message-to-help|speech,support
person-and-outcomes|person,chart
predictable-safe-space|home,shield
504-document|document,ramp,504
access-and-dialogue|ramp,speech
find-and-assess|magnify,person
local-state-agencies|community,linked
service-calendar|calendar,people
starting-measure|measure,flag
goal-milestones|route,flag
assessment-paths|book,fork
family-notes|people,notice
document-edit|document,pen
plan-and-check|document,check
restore-learning|book,cycle
private-records|document,lock
mediated-dialogue|dialogue,scales
hearing-documents|scales,document
complaint-letter|envelope,pen
rights-transition|shield,bridge
notice-pair|envelope,switch,N1/N2
school-to-adult|book,home,MA
learning-options|book,paths,UDL
seizure-wave|wave,health
seizure-plan|checklist,wave
swallowing-path|body,drop
food-and-comfort|plate,heart
nonfood-safety|object,shield
bowel-comfort|stomach,health
sleep-and-clock|bed,clock
privacy-and-care|shirt,lock
toilet-access|chair,drop
care-and-pause|people,pause
home-and-community|home,community
coordinated-services|support,calendar
support-plan|checklist,person
home-with-support|home,support
shared-place|community,people
care-transition|health,bridge
handover|handed,document
life-areas|heart,community
injury-and-care|body,health
space-and-quiet|headphones,withdraw
movement-change|body,pause
parallel-care|health,linked
reward-and-result|gift,chart
accessible-choices|fork,ramp
alternative-path|fork,cycle
change-and-review|open-cycle,magnify
organize-actions|checklist,steps
language-development|letters,plant'''

def spec_for(term):
    inclusive={'Multilingual communication & AAC':'device,dialogue,home','Plain language & Easy Read':'book,document,magnify','Self-advocacy & supported self-advocacy':'person,speech,support'}
    if term['term'] in inclusive:return inclusive[term['term']]

    if term.get('icon_key'):
        table=dict(line.strip().split('|',1) for line in NEW.splitlines() if line.strip())
        return table[term['icon_key']]
    for line in OLD.splitlines():
        prefix,spec=line.split('|',1)
        if term['term'].startswith(prefix):return spec
    raise ValueError('Missing term-specific illustration: '+term['term'])
