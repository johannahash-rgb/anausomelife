import test from 'node:test';
import assert from 'node:assert/strict';
import {createOuting,parseRequest,publicSource,blocked} from '../lib/core.js';
import {makeProvider} from '../lib/provider.js';
import {makeHandler} from '../api/generate.js';
import {reserveAttempt} from '../lib/limits.js';
const input={destination:'L.L.Bean, Freeport, Maine',context:'A quiet break'};
const data={needsClarification:false,choices:[],place:'L.L.Bean, Freeport, Maine',opening:'We are planning a visit. We can keep it short.',steps:['We go together.','We arrive.','We choose one thing.','We can take a break.','We can leave.'],visualFacts:['A large outdoor boot sculpture.'],sources:[{title:'Official place page',url:'https://www.llbean.com/llb/shop/1000001705'}],retrievedUrls:['https://www.llbean.com/llb/shop/1000001705']};
const image='data:image/webp;base64,UklGRgAAAABXRUJQ';
function fake({rejectAt='',ambiguous=false,badSource=false}={}){
 const calls=[];let n=0;
 const hit=label=>{calls.push(label);if(label===rejectAt)throw blocked();};
 return {calls,reserve:async()=>hit('reserve'),provider:{moderate:async(_t,img)=>hit(img?'output moderation':++n===1?'input moderation':'research moderation'),review:async(_t,img)=>hit(img?'output review':n===1?'input review':'research review'),research:async()=>{hit('research');return ambiguous?{needsClarification:true,choices:['A park in Boston','A park in Burlington']}:structuredClone({...data,retrievedUrls:badSource?[]:data.retrievedUrls});},draw:async()=>{hit('draw');return image;}}};
}
test('successful flow researches before drawing and releases only checked output',async()=>{const d=fake();const result=await createOuting(input,d);assert.equal(result.status,'ready');assert.equal(result.image,image);assert.ok(d.calls.indexOf('research')<d.calls.indexOf('draw'));assert.deepEqual(d.calls.slice(-2),['output moderation','output review']);assert.match(result.imageCaption,/not a current/);});
for(const stage of ['reserve','input moderation','input review','research moderation','research review','output moderation','output review'])test('fail closed at '+stage,async()=>{const d=fake({rejectAt:stage});await assert.rejects(createOuting(input,d));assert.equal(d.calls.at(-1),stage);if(!stage.startsWith('output'))assert.ok(!d.calls.includes('draw'));});
test('ambiguity produces choices and never draws',async()=>{const d=fake({ambiguous:true});const r=await createOuting(input,d);assert.equal(r.status,'choose_place');assert.ok(!d.calls.includes('draw'));assert.equal(r.image,undefined);});
test('invented/unretrieved source prevents image cost',async()=>{const d=fake({badSource:true});await assert.rejects(createOuting(input,d),{code:'source_check_failed'});assert.ok(!d.calls.includes('draw'));});
test('no uploads, arbitrary fields or oversized prompts',()=>{assert.throws(()=>parseRequest({...input,image:'private photo'}));assert.throws(()=>parseRequest({destination:'x'.repeat(201)}));assert.throws(()=>parseRequest([]));assert.deepEqual(parseRequest(input),input);});
test('source links reject executable, credential-bearing and local targets',()=>{for(const s of ['javascript:alert(1)','http://example.com','https://127.0.0.1/','https://[::1]/','https://user:secret@example.com/','https://service.internal/'])assert.equal(publicSource(s),null);assert.equal(publicSource('https://www.llbean.com/'),'https://www.llbean.com/');});
test('malformed moderation cannot approve content',async()=>{const provider=makeProvider({},async()=>({ok:true,json:async()=>({results:[]})}));await assert.rejects(provider.moderate('hello'),{code:'unavailable'});});
test('network outage never becomes an approved result',async()=>{const provider=makeProvider({},async()=>{throw Error('timeout');});await assert.rejects(provider.moderate('hello'));});
function response(){return {headers:{},setHeader(k,v){this.headers[k]=v;},status(s){this.code=s;return this;},json(v){this.body=v;return this;},end(){return this;}};}
test('disabled or unconfigured endpoint makes no network calls and reveals no secrets',async()=>{const res=response();await makeHandler({env:{OPENAI_API_KEY:'secret'},fetcher:()=>assert.fail('network called')})({method:'POST',headers:{origin:'https://anausomelife.com'},body:input},res);assert.equal(res.code,503);assert.ok(!JSON.stringify(res.body).includes('secret'));});
test('foreign origin is rejected before generation',async()=>{const res=response();await makeHandler({fetcher:()=>assert.fail('network called')})({method:'POST',headers:{origin:'https://other.example'}},res);assert.equal(res.code,403);});
test('rate limit exhaustion blocks the request; raw IP is not stored',async()=>{let sent;await assert.rejects(reserveAttempt({headers:{'x-vercel-forwarded-for':'192.0.2.10'}},{VERCEL:'1',UPSTASH_REDIS_REST_URL:'https://test.upstash.io',UPSTASH_REDIS_REST_TOKEN:'test',RATE_LIMIT_SECRET:'x'.repeat(32)},async(_url,options)=>{sent=options.body;return {ok:true,json:async()=>({result:0})};}),{code:'rate_limited'});assert.ok(!sent.includes('192.0.2.10'));assert.match(sent,/EVAL/);});
test('missing trusted client address fails closed before counters',async()=>{await assert.rejects(reserveAttempt({headers:{}},{VERCEL:'1'},()=>assert.fail('network called')),{code:'unavailable'});});
