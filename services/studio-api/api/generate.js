import {createOuting,parseRequest,StudioError,unavailable} from '../lib/core.js';
import {makeProvider} from '../lib/provider.js';
import {configured,reserveAttempt} from '../lib/limits.js';
const origins=new Set(['https://anausomelife.com','https://www.anausomelife.com']);
export function makeHandler({env=process.env,fetcher=fetch}={}){
 return async function handler(req,res){
  res.setHeader('Cache-Control','no-store');res.setHeader('Vary','Origin');res.setHeader('X-Content-Type-Options','nosniff');
  const origin=req.headers.origin;
  if(!origins.has(origin))return res.status(403).json({error:'origin_not_allowed',message:'Open the studio on An AUsome Life.'});
  res.setHeader('Access-Control-Allow-Origin',origin);
  res.setHeader('Access-Control-Allow-Methods','POST, OPTIONS');res.setHeader('Access-Control-Allow-Headers','Content-Type');
  if(req.method==='OPTIONS')return res.status(204).end();
  if(req.method!=='POST')return res.status(405).json({error:'method_not_allowed'});
  try{
   if(!configured(env))throw unavailable();
   if(!/^application\/json(?:;|$)/i.test(req.headers['content-type']||''))throw new StudioError('invalid_request',415,'Use a text-only JSON request.');
   if(Number(req.headers['content-length']||0)>4096)throw new StudioError('too_long',413,'Please shorten the description.');
   let body=req.body;
   if(typeof body==='string'){if(Buffer.byteLength(body)>4096)throw new StudioError('too_long',413,'Please shorten the description.');try{body=JSON.parse(body);}catch{throw new StudioError('invalid_request',400,'Please check the description.');}}
   if(Buffer.byteLength(JSON.stringify(body??null))>4096)throw new StudioError('too_long',413,'Please shorten the description.');
   const input=parseRequest(body);
   const result=await createOuting(input,{provider:makeProvider(env,fetcher),reserve:()=>reserveAttempt(req,env,fetcher)});
   return res.status(200).json(result);
  }catch(error){
   // Provider bodies, credential values, personal prompts and image bytes never enter logs/errors.
   const safe=error instanceof StudioError?error:unavailable();
   if(safe.status===429)res.setHeader('Retry-After','3600');
   return res.status(safe.status).json({error:safe.code,message:safe.message});
  }
 };
}
export default makeHandler();
