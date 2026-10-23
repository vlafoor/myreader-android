const fs=require('fs');
const path=require('path');
const {JSDOM, VirtualConsole}=require('jsdom');
const {indexedDB, IDBKeyRange}=require('fake-indexeddb');

let html=fs.readFileSync('app/src/main/assets/index.html','utf8');
// External reader libraries are irrelevant for navigation smoke tests and may require browser-only APIs.
html=html.replace(/<script\s+src="[^"]+"[^>]*>[\s\S]*?<\/script>/gi,'');

const errors=[];
const vc=new VirtualConsole();
vc.on('jsdomError',e=>errors.push(String(e)));
vc.on('error',e=>errors.push(String(e)));

const dom=new JSDOM(html,{
  url:'https://myreader.test/',
  runScripts:'dangerously',
  pretendToBeVisual:true,
  virtualConsole:vc,
  beforeParse(w){
    w.indexedDB=indexedDB;
    w.IDBKeyRange=IDBKeyRange;
    w.matchMedia=()=>({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
    w.requestAnimationFrame=(cb)=>setTimeout(()=>cb(Date.now()),0);
    w.cancelAnimationFrame=(id)=>clearTimeout(id);
    w.ResizeObserver=class{observe(){} unobserve(){} disconnect(){}};
    w.IntersectionObserver=class{observe(){} unobserve(){} disconnect(){}};
    w.alert=()=>{};
    w.confirm=()=>true;
    w.NativeReader={
      getBatteryPercent:()=>50,
      getLocalTime:()=>'12:00',
      setReaderImmersive:()=>{},
      setAppBrightness:()=>{},
      getPdfPageCount:()=>1,
      renderPdfPage:()=>null
    };
  }
});

function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
(async()=>{
  await sleep(900);
  const w=dom.window,d=w.document;
  const required=['library','stats','notes','settings'];
  for(const id of required){
    if(!d.getElementById(id)) throw new Error('Missing screen '+id);
  }
  if(typeof w.openScreen!=='function') throw new Error('openScreen is not callable');
  if(typeof w.setLibraryFilter!=='function') throw new Error('setLibraryFilter is not callable');

  const result={ok:true,steps:[]};
  const mark=(name,ok)=>{result.steps.push({name,ok});if(!ok)result.ok=false};

  // Verify actual clickable elements, not helper-only functions.
  const clickAndExpect=(label,id)=>{
    const activeScreen=d.querySelector('.screen.active');
    const btn=[...(activeScreen?.querySelectorAll('.navitem')||[])].find(x=>x.textContent.includes(label));
    if(!btn) throw new Error('Missing nav button '+label);
    btn.click();
    const ok=d.getElementById(id).classList.contains('active');
    mark(label+' nav click',ok);
    if(!ok) throw new Error(label+' click did not activate '+id);
  };
  clickAndExpect('Stats','stats');
  clickAndExpect('Notes','notes');
  clickAndExpect('Settings','settings');
  clickAndExpect('Library','library');

  const finished=[...d.querySelectorAll('#library .chip[data-filter]')].find(x=>x.dataset.filter==='finished');
  if(!finished) throw new Error('Missing Finished filter');
  finished.click();
  const finishedOk=finished.classList.contains('active') && w.libraryFilter==='finished';
  mark('Finished filter click',finishedOk);
  if(!finishedOk) throw new Error('Finished button click did not activate');

  const all=[...d.querySelectorAll('#library .chip[data-filter]')].find(x=>x.dataset.filter==='all');
  if(!all) throw new Error('Missing All filter');
  all.click();
  const allOk=all.classList.contains('active') && w.libraryFilter==='all';
  mark('All filter click',allOk);
  if(!allOk) throw new Error('All button click did not activate');

  if(errors.length) console.log('JSDOM_WARNINGS',JSON.stringify(errors.slice(0,10)));
  console.log('MYREADER_UI_SMOKE_TEST_PASS');
  console.log(JSON.stringify(result));
  dom.window.close();
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
