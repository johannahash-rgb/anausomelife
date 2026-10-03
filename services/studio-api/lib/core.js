import { randomUUID } from 'node:crypto';
import { isIP } from 'node:net';
export class StudioError extends Error {
  constructor(code,status,message){super(message);this.code=code;this.status=status;}
}
export const unavailable=()=>new StudioError('unavailable',503,'The picture studio is unavailable right now. Your existing plan is still yours.');
export const blocked=()=>new StudioError('content_not_supported',422,'Please choose a family-friendly public place or an everyday activity.');
export function parseRequest(body){
  if(!body || typeof body!=='object' || Array.isArray(body) || Object.keys(body).some(k=>!['destination','context'].includes(k)))throw new StudioError('invalid_request',400,'Describe a place and, if helpful, its town.');
  const {destination,context=''}=body;
  if(typeof destination!=='string'||typeof context!=='string'||!destination.trim()||destination.length>200||context.length>500||/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(destination+context))throw new StudioError('invalid_request',400,'Use a short place name and up to 500 characters of context.');
  return {destination:destination.trim(),context:context.trim()};
}
export function publicSource(value){
  try{const u=new URL(value);if(u.protocol!=='https:'||u.username||u.password||u.port||isIP(u.hostname)||!u.hostname.includes('.')||/(^|\.)(localhost|local|internal|test|invalid)$/.test(u.hostname))return null;return u.href;}catch{return null;}
}
const short=(s,n)=>typeof s==='string'&&s.trim().length>0&&s.length<=n;
export function validateResearch(data){
  if(!data||typeof data.needsClarification!=='boolean'||!Array.isArray(data.choices)||data.choices.length>4)throw unavailable();
  if(data.needsClarification){if(!data.choices.length||!data.choices.every(s=>short(s,150)))throw unavailable();return {needsClarification:true,choices:data.choices};}
  if(!short(data.place,160)||!short(data.opening,600)||!Array.isArray(data.steps)||data.steps.length!==5||!data.steps.every(s=>short(s,240))||!Array.isArray(data.visualFacts)||!data.visualFacts.length||data.visualFacts.length>5||!data.visualFacts.every(s=>short(s,300))||!Array.isArray(data.sources)||!data.sources.length||data.sources.length>5)throw unavailable();
  const visited=new Set((data.retrievedUrls||[]).map(publicSource).filter(Boolean));
  const sources=data.sources.map(s=>({title:s?.title,url:publicSource(s?.url)}));
  if(!sources.every(s=>short(s.title,180)&&s.url&&visited.has(s.url)))throw new StudioError('source_check_failed',503,'We could not confirm that place. Add its town or use the editable planner.');
  return {needsClarification:false,place:data.place,opening:data.opening,steps:data.steps,visualFacts:data.visualFacts,sources};
}
export async function createOuting(input,{provider,reserve,now=()=>new Date()}){
  // Atomic counters run before any billable provider calls. No retries are automatic.
  await reserve();
  const request=JSON.stringify(input);
  await provider.moderate(request);
  await provider.review(request);
  const research=validateResearch(await provider.research(input));
  await provider.moderate(JSON.stringify(research));
  await provider.review(JSON.stringify(research));
  if(research.needsClarification)return {status:'choose_place',choices:research.choices};
  const image=await provider.draw(research);
  if(typeof image!=='string'||!/^data:image\/webp;base64,[A-Za-z0-9+/]+=*$/.test(image)||image.length>3500000)throw unavailable();
  const bytes=Buffer.from(image.split(',')[1],'base64');
  if(bytes.toString('ascii',0,4)!=='RIFF'||bytes.toString('ascii',8,12)!=='WEBP')throw unavailable();
  // No partial images or story results are released before both output checks finish.
  await provider.moderate(JSON.stringify(research),image);
  await provider.review(JSON.stringify(research),image);
  return {status:'ready',id:randomUUID(),place:research.place,opening:research.opening,steps:research.steps,image,sources:research.sources,retrievedAt:now().toISOString(),imageCaption:'AI-created editorial interpretation, not a current venue or entrance photograph. Check the official source before visiting.'};
}
