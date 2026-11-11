/* Regression checks for the presenter-controlled playback contract. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const harness=fs.readFileSync(path.join(__dirname,'verify_context_nugget.cjs'),'utf8').split('const ids=')[0];
for(const kind of ['laundry','topiary']){
 let source=harness.replace("'interactive/context_nugget'",`'interactive/inbox_${kind}'`).replace('const context=vm.createContext({document:doc,window:win});',"win.location={search:''};const context=vm.createContext({document:doc,window:win,URLSearchParams});");
 source+=`
 loaded();assert.equal(run('index'),-1);assert.equal(run('mode'),'holding');
 assert.equal(run('beats.length'),6);
 for(let i=0;i<6;i++){
  run('advance()');assert.equal(run('index'),i);
  const generation=run('generation');run('advance()');assert.equal(run('generation'),generation);
  loaded();assert.equal(run('mode'),'playing');run('advance()');assert.equal(run('index'),i);
  video.emit('ended');loaded();assert.equal(run('mode'),'holding');assert.equal(video.loop,true);
  video.emit('ended');assert.equal(run('index'),i,'native holds never auto-advance');
 }
 assert.equal(els['#next'].disabled,true);run('advance()');assert.equal(run('index'),5);
 run('previous()');loaded();assert.equal(run('index'),4);run('replay()');loaded();assert.equal(run('index'),4);
 run('selectStep(3)');const stale=video.onloadeddata;run('selectStep(1)');stale();assert.equal(run('mode'),'loading');loaded();assert.equal(run('index'),1);
 video.onerror();assert.equal(run('mode'),'error');run('replay()');loaded();assert.equal(run('mode'),'playing');
 run('ready()');loaded();assert.equal(run('index'),-1);assert.equal(run('mode'),'holding');
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
 for(const beat of manifest.beats)for(const key of ['src','hold','poster'])assert(fs.existsSync(path.resolve(root,beat[key])),beat.id+' missing '+key);
 `;
 vm.runInNewContext(source,{require,console,URLSearchParams,__dirname});
 console.log(`PASS ${kind}: six actions, manual holds, final stop, replay/back/jump, loading guards, error/retry, local media.`);
}
