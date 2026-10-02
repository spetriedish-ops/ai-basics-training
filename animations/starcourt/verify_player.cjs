const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('animations/starcourt/interactive/index.html','utf8');
class Element {
  constructor(){this.children=[];this.dataset={};this.attributes={};this.currentTime=0;this.listeners={};}
  append(b){this.children.push(b);}
  replaceChildren(){this.children=[];}
  setAttribute(k,v){this.attributes[k]=v;}
  addEventListener(k,f){this.listeners[k]=f;}
  pause(){}
  play(){return Promise.resolve();}
  load(){this.currentTime=0;this.onloadedmetadata?.();}
}
const nodes = Object.fromEntries(['video','.status','.beats','.scenes','#next','#download','#still','#narration-cue','#play-all','#fullscreen','.screen'].map(k=>[k,new Element()]));
const document={body:{dataset:{}},querySelector:k=>nodes[k],querySelectorAll:k=>k==='[data-beat]'?nodes['.beats'].children.filter(b=>b.dataset.beat!==undefined):nodes['.scenes'].children,createElement:()=>new Element()};
const context=vm.createContext({document,window:{addEventListener(){}},console});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
const run=s=>vm.runInContext(s,context);
const expect=(id,beat)=>{assert.equal(run('scene().id'),id);assert.equal(run('currentBeat()'),beat);};
// Standard Next must enter the directory and return to the three-option map.
run("selectScene(scenes.findIndex(s=>s.id==='route_mcp'));next()");expect('mcp_directory',0);
run('next();next();next();next()');expect('route_cli',0);
run('next()');expect('cli_terminal',0);
run('next();next();next();next()');expect('route_api',0);
// Reproduce Next during a full preview's final beat, before the ended event.
run("selectScene(scenes.findIndex(s=>s.id==='mcp_directory'));full();video.currentTime=33;label()");
assert.match(nodes['#next'].textContent,/Map: CLI/);
run('next()');expect('route_cli',0);
run("selectScene(scenes.findIndex(s=>s.id==='cli_terminal'));full();video.currentTime=34;next()");expect('route_api',0);
// Next during a middle preview beat advances from the visible action.
run("selectScene(scenes.findIndex(s=>s.id==='mcp_directory'));full();video.currentTime=16;next()");expect('mcp_directory',3);
// The numbered controls now have explicit pivots on both sides of the close-up.
run("selectScene(scenes.findIndex(s=>s.id==='route_mcp'))");
assert.match(nodes['.beats'].children.at(-1).textContent,/MCP directory/);
nodes['.beats'].children.at(-1).onclick();expect('mcp_directory',0);
assert.match(nodes['.beats'].children.at(-1).textContent,/Map: CLI/);
nodes['.beats'].children.at(-1).onclick();expect('route_cli',0);
// Section preview keeps its bounded final hold and Next pivots afterward.
run("selectScene(scenes.findIndex(s=>s.id==='route_mcp'));full();hold()");
assert.equal(nodes.video.src,'holds/03.mp4');assert.equal(nodes.video.loop,true);
run('next()');expect('mcp_directory',0);
console.log('PASS: Next, mid-preview advancement, numbered pivots, and bounded map holds.');
