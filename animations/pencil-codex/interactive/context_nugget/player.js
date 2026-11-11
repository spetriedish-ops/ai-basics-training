/* One presenter-controlled sequence, using each scene's native hold loop. */
const video=document.querySelector('video'),canvas=document.querySelector('canvas'),poster=document.querySelector('#poster');
const status=document.querySelector('.status'),nextButton=document.querySelector('#next'),jump=document.querySelector('#jump');
let index=-1,mode='ready',generation=0;
const beats=sequence.beats;
function url(path){return path+'?v='+sequence.version;}
function update(){
  const beat=beats[index],busy=mode==='loading'||mode==='playing';
  status.textContent=index<0?'Ready for the opening':`${index+1} / ${beats.length} · ${beat.label} · ${mode==='holding'?'holding':mode==='playing'?'playing':mode==='error'?'could not load':'loading'}`;
  nextButton.disabled=busy||index===beats.length-1;
  nextButton.textContent=index<0?'Start the mind map →':index===beats.length-1?'Walkthrough complete':`Next: ${beats[index+1].label} →`;
  document.querySelector('#previous').disabled=index<0;
  document.querySelector('#pause').disabled=index<0||mode==='loading'||mode==='error'||(mode==='holding'&&!beat?.hold);
  document.querySelector('#pause').textContent=video.paused?'Play':'Pause';
  document.querySelector('#cue').textContent=beat?.cue||'Start when ready to read “So far in this series…” The opening draws the previously covered harness branches; Context has its own next click.';
  const note=document.querySelector('#note');note.textContent=beat?.note||'';note.hidden=!beat?.note;
  jump.value=String(index);
  document.querySelectorAll('[data-step]').forEach(b=>b.setAttribute('aria-current',Number(b.dataset.step)===index?'true':'false'));
}
function play(){video.play().then(update).catch(()=>{status.textContent='Press Play to start this beat';document.querySelector('#pause').disabled=false;});}
function preserveFrame(){
  if(!video.hidden&&video.readyState>=2){
    try{canvas.getContext('2d').drawImage(video,0,0,1920,1080);canvas.hidden=false;poster.hidden=true;}catch{/* Keep the existing poster if a frame is not yet available. */}
  }
  video.hidden=true;
}
function load(src,loop=false){
  preserveFrame();video.pause();mode='loading';const token=++generation;video.loop=loop;
  video.onloadeddata=()=>{if(token!==generation)return;video.hidden=false;canvas.hidden=true;poster.hidden=true;mode=loop?'holding':'playing';update();play();};
  video.onerror=()=>{if(token!==generation)return;mode='error';update();status.textContent='This clip could not load. Replay to retry, or choose another beat.';};
  video.src=url(src);video.load();update();
}
function ready(){
  ++generation;video.onloadeddata=null;video.onerror=null;video.pause();video.hidden=true;canvas.hidden=true;poster.src=url(sequence.ready);poster.alt='The mind map is ready to draw';poster.hidden=false;index=-1;mode='ready';update();
}
function hold(){
  const beat=beats[index];
  if(beat.hold){load(beat.hold,true);return;}
  ++generation;video.onloadeddata=null;video.pause();video.hidden=true;canvas.hidden=true;poster.src=url(beat.poster);poster.alt=beat.label+' — holding';poster.hidden=false;mode='holding';update();
}
function selectStep(value){
  if(value<0){ready();return;}
  index=Math.max(0,Math.min(beats.length-1,value));
  const beat=beats[index];
  if(beat.src)load(beat.src);else hold();
}
function advance(){if(mode==='ready'||mode==='holding'||mode==='error'){if(index<beats.length-1)selectStep(index+1);}}
function previous(){selectStep(index-1);}
function replay(){selectStep(Math.max(0,index));}
function pause(){if(index<0){advance();return;}if(mode==='loading'||mode==='error'||(mode==='holding'&&!beats[index].hold))return;video.paused?play():video.pause();update();}
video.addEventListener('ended',()=>{if(mode==='playing'&&!video.loop)hold();});
document.querySelector('.screen').addEventListener('click',advance);
nextButton.onclick=advance;document.querySelector('#previous').onclick=previous;document.querySelector('#replay').onclick=replay;document.querySelector('#pause').onclick=pause;
jump.onchange=()=>selectStep(Number(jump.value));
function fullscreen(){if(document.fullscreenElement)document.exitFullscreen();else document.querySelector('.screen').requestFullscreen().catch(()=>{});}
document.querySelector('#fullscreen').onclick=fullscreen;
window.addEventListener('keydown',e=>{
  if(e.target.closest('select,input,textarea')||e.altKey||e.ctrlKey||e.metaKey)return;
  if(e.key===' '&&e.target.closest('button,summary'))return;
  if(e.repeat&&[' ','ArrowRight','ArrowLeft'].includes(e.key))return;
  if(e.key==='ArrowRight'){e.preventDefault();advance();}
  else if(e.key==='ArrowLeft'){e.preventDefault();previous();}
  else if(e.key===' '){e.preventDefault();mode==='holding'||mode==='ready'?advance():pause();}
  else if(e.key.toLowerCase()==='r')replay();
  else if(e.key.toLowerCase()==='h')document.body.classList.toggle('recording');
  else if(e.key.toLowerCase()==='f')fullscreen();
});
let section;
beats.forEach((beat,i)=>{
  if(section?.label!==beat.section){section=document.createElement('optgroup');section.label=beat.section;jump.append(section);}
  const option=document.createElement('option');option.value=String(i);option.textContent=`${i+1}. ${beat.label}`;section.append(option);
  const item=document.createElement('li'),button=document.createElement('button');button.dataset.step=String(i);button.textContent=beat.label;button.onclick=()=>selectStep(i);item.append(button);
  if(beat.note){const note=document.createElement('small');note.textContent='Narration hold';item.append(note);}
  document.querySelector('#run-of-show').append(item);
});
ready();
