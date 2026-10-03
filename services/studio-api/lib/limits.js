import {createHmac} from 'node:crypto';
import {isIP} from 'node:net';
import {StudioError,unavailable} from './core.js';
export const REQUIRED=['OPENAI_API_KEY','STUDIO_TEXT_MODEL','STUDIO_IMAGE_MODEL','UPSTASH_REDIS_REST_URL','UPSTASH_REDIS_REST_TOKEN','RATE_LIMIT_SECRET'];
export function configured(env){
  return env.STUDIO_ENABLED==='true'&&env.VERCEL==='1'&&REQUIRED.every(k=>typeof env[k]==='string'&&env[k].trim())&&env.RATE_LIMIT_SECRET.length>=32;
}
// One atomic operation across instances: global and per-network counters expire automatically.
export const reservationScript=`
local daily=tonumber(redis.call('GET',KEYS[1]) or '0')
local hourly=tonumber(redis.call('GET',KEYS[2]) or '0')
if daily>=10 or hourly>=3 then return 0 end
redis.call('INCR',KEYS[1]); redis.call('EXPIRE',KEYS[1],172800)
redis.call('INCR',KEYS[2]); redis.call('EXPIRE',KEYS[2],7200)
return 1`;
export async function reserveAttempt(req,env,fetcher=fetch,now=new Date()){
  const ip=req.headers['x-vercel-forwarded-for'];
  if(env.VERCEL!=='1'||typeof ip!=='string'||!isIP(ip.trim()))throw unavailable();
  const endpoint=new URL(env.UPSTASH_REDIS_REST_URL);
  if(endpoint.protocol!=='https:'||!endpoint.hostname.endsWith('.upstash.io')||endpoint.username||endpoint.password||endpoint.port||endpoint.pathname!=='/'||endpoint.search)throw unavailable();
  const day=now.toISOString().slice(0,10),hour=now.toISOString().slice(0,13);
  const network=createHmac('sha256',env.RATE_LIMIT_SECRET).update(day+'|'+ip.trim()).digest('hex');
  const r=await fetcher(endpoint.href,{method:'POST',headers:{Authorization:'Bearer '+env.UPSTASH_REDIS_REST_TOKEN,'Content-Type':'application/json'},body:JSON.stringify(['EVAL',reservationScript,2,'aal:daily:'+day,'aal:hour:'+hour+':'+network]),signal:AbortSignal.timeout(5000)});
  if(!r.ok)throw unavailable();const value=await r.json();if(value.error||![0,1].includes(value.result))throw unavailable();
  if(value.result===0)throw new StudioError('rate_limited',429,'The studio has reached its current limit. You can still use the editable planner.');
}
