import {configured} from '../lib/limits.js';
export default function handler(_req,res){
 res.setHeader('Cache-Control','no-store');
 res.status(200).json({service:'anausomelife-studio-api',configured:configured(process.env),release:'candidate'});
}
