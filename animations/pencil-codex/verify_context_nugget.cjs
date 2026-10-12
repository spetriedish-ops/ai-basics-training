const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.join(__dirname,'interactive/context_nugget');
class Element{
 constructor(){this.children=[];this.dataset={};this.listeners={};this.hidden=false;this.paused=true;this.readyState=4;}
 append(e){this.children.push(e);}setAttribute(k,v){this[k]=v;}
 addEventListener(k,f){this.listeners[k]=f;}emit(k,e={}){this.listeners[k]?.(e);}
 pause(){this.paused=true;}play(){this.paused=false;return Promise.resolve();}load(){}
 getContext(){return {drawImage(){}};}closest(){return null;}
}
const selectors=['video','canvas','#poster','.status','#next','#jump','#previous','#pause','#cue','#note','.screen','#replay','#fullscreen','#run-of-show'];
const els=Object.fromEntries(selectors.map(k=>[k,new Element()]));
const win=new Element(),doc={querySelector:k=>els[k],querySelectorAll:()=>els['#run-of-show'].children.map(x=>x.children[0]),createElement:()=>new Element(),body:{classList:{toggle(){}}}};
const context=vm.createContext({document:doc,window:win});
vm.runInContext(fs.readFileSync(path.join(root,'sequence.js'),'utf8'),context);
vm.runInContext(fs.readFileSync(path.join(root,'player.js'),'utf8'),context);
const run=s=>vm.runInContext(s,context),video=els.video;
const loaded=()=>video.onloadeddata?.();
const ids=Array.from(run('beats.map(b=>b.id)'));
assert.equal(ids.length,27);assert.equal(ids[0],'recap');assert.equal(ids[1],'context');assert.equal(ids[2],'crumple');
assert.equal(ids.indexOf('coins'),ids.indexOf('dory')+1);
assert.equal(run('index'),-1);assert.equal(run('mode'),'ready');
for(let i=0;i<ids.length;i++){
 run('advance()');assert.equal(run('index'),i,ids[i]);
 const token=run('generation');run('advance()');assert.equal(run('generation'),token,'double clicks cannot skip while loading');
 loaded();
 if(run('Boolean(beats[index].src)')){
  assert.equal(run('mode'),'playing');run('advance()');assert.equal(run('index'),i,'action must finish before next');
  video.emit('ended');loaded();
 }
 assert.equal(run('mode'),'holding');assert.equal(run('index'),i);
 if(run('Boolean(beats[index].hold)'))assert.equal(video.loop,true);
 video.emit('ended');assert.equal(run('index'),i,'hold never advances itself');
}
assert.equal(els['#next'].disabled,true);run('advance()');assert.equal(run('index'),26);
run('previous()');loaded();assert.equal(run('index'),25);run('replay()');loaded();assert.equal(run('index'),25);
run('selectStep(23)');const stale=video.onloadeddata;run('selectStep(2)');stale();assert.equal(run('mode'),'loading');loaded();assert.equal(run('index'),2);
video.emit('ended');assert.equal(run('mode'),'holding');assert.equal(els['#poster'].hidden,false);
run('selectStep(0)');video.onerror();assert.equal(run('mode'),'error');run('replay()');loaded();assert.equal(run('mode'),'playing');
run('ready()');assert.equal(run('index'),-1);assert.equal(video.hidden,true);
const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
for(const beat of manifest.beats)for(const key of ['src','hold','poster'])if(beat[key])assert(fs.existsSync(path.resolve(root,beat[key])),`${beat.id} missing ${key}`);
console.log('PASS: all 27 beats, correct finale order, manual/native holds, blank-paper hold, final stop, back/replay/jump, double-click guards, stale loads, error/retry, all local media.');
