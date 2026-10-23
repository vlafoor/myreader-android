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
  const finishedOk=finished.classList.contains('active');
  mark('Finished filter click',finishedOk);
  if(!finishedOk) throw new Error('Finished button click did not activate');

  const all=[...d.querySelectorAll('#library .chip[data-filter]')].find(x=>x.dataset.filter==='all');
  if(!all) throw new Error('Missing All filter');
  all.click();
  const allOk=all.classList.contains('active');
  mark('All filter click',allOk);
  if(!allOk) throw new Error('All button click did not activate');

  await sleep(700);


  // Library visual recovery: seed real IndexedDB rows and verify visible card structure.
  await w.addOne({title:'Visible EPUB',author:'Author One',ext:'epub',progress:.16,addedAt:2,cover:''});
  await w.addOne({title:'Visible PDF',author:'Author Two',ext:'pdf',progress:.04,addedAt:1,cover:''});
  w.openScreen('library');
  await w.renderLibrary();
  await sleep(120);
  const search=d.querySelector('#library>.searchbox');
  const chips=d.querySelector('#library>.chips');
  if(!search || !chips) throw new Error('Library search/filter structure missing');
  const searchStyle=w.getComputedStyle(search),chipsStyle=w.getComputedStyle(chips);
  if(searchStyle.display==='none'||searchStyle.visibility==='hidden'||searchStyle.opacity==='0') throw new Error('Library search hidden');
  if(chipsStyle.display==='none'||chipsStyle.visibility==='hidden'||chipsStyle.opacity==='0') throw new Error('Library filters hidden');
  const cards=[...d.querySelectorAll('#bookGrid .book-card')];
  if(cards.length<2) throw new Error('Library book cards did not render');
  for(const card of cards.slice(0,2)){
    const cover=card.querySelector('.cover-wrap'),name=card.querySelector('.book-name'),author=card.querySelector('.book-author');
    if(!cover||!name||!author) throw new Error('Library card content missing');
    for(const el of [cover,name,author]){
      const st=w.getComputedStyle(el);
      if(st.display==='none'||st.visibility==='hidden'||st.opacity==='0') throw new Error('Library card content hidden: '+el.className);
    }
    if(!name.textContent.trim()) throw new Error('Library title empty');
  }
  console.log('MYREADER_LIBRARY_VISUAL_SMOKE_TEST_PASS');

  // Reader toolbar routing + functional Format checks.
  w.eval("currentBook={ext:'pdf',title:'Test PDF'}; pdfState={page:12,count:308,doc:null,viewMode:'page',cropMode:'auto',zoom:1,margin:0};");
  await w.v045OpenContents();
  await sleep(40);
  let sheetTitle=d.getElementById('vnextSheetTitle')?.textContent||'';
  let sheetBody=d.getElementById('vnextSheetBody')?.textContent||'';
  if(sheetTitle!=='Contents') throw new Error('PDF Contents did not open Contents sheet');
  if(/Go to page/i.test(sheetBody)) throw new Error('PDF Contents incorrectly routed to Go to page');

  w.vnextOpenNavigate();
  await sleep(20);
  sheetTitle=d.getElementById('vnextSheetTitle')?.textContent||'';
  sheetBody=d.getElementById('vnextSheetBody')?.textContent||'';
  if(sheetTitle!=='Navigate' || !/Go to page/i.test(sheetBody)) throw new Error('Navigate does not own Go to page');

  w.vnextOpenFormat();
  await sleep(20);
  sheetTitle=d.getElementById('vnextSheetTitle')?.textContent||'';
  sheetBody=d.getElementById('vnextSheetBody')?.textContent||'';
  if(sheetTitle!=='Format' || !/Page display/i.test(sheetBody) || !/Crop/i.test(sheetBody)) throw new Error('PDF Format options missing');

  w.eval("currentBook={ext:'epub',title:'Test EPUB'}; epubState={index:0,chapters:[{title:'Chapter One'}]};");
  const oldFont=Number(w.eval('settings.font'));
  w.vnextOpenFormat();
  await sleep(20);
  sheetBody=d.getElementById('vnextSheetBody')?.textContent||'';
  if(!/Text size/i.test(sheetBody) || !/Line spacing/i.test(sheetBody) || !/Margins/i.test(sheetBody)) throw new Error('EPUB Format options missing');
  w.v045EpubStep('font',1);
  await sleep(20);
  const newFont=Number(w.eval('settings.font'));
  if(!(newFont>oldFont)) throw new Error('EPUB Format control did not change font setting');

  console.log('MYREADER_READER_TOOL_SMOKE_TEST_PASS');

  // Library card rendering gate: real card contents must exist, not badges-only shells.
  await w.addOne({title:'Visible EPUB Book',author:'Author One',cover:'',ext:'epub',addedAt:Date.now()+1,progress:.16,finished:false,bookmark:false});
  await w.addOne({title:'Visible PDF Book',author:'Author Two',cover:'',ext:'pdf',addedAt:Date.now()+2,progress:.04,finished:false,bookmark:false});
  await w.renderLibrary();
  await sleep(80);
  const libraryCards=[...d.querySelectorAll('#bookGrid .book-card')];
  if(libraryCards.length<2) throw new Error('Library did not render book cards');
  const cardText=libraryCards.map(c=>c.textContent||'').join(' | ');
  if(!/Visible EPUB Book/.test(cardText)||!/Visible PDF Book/.test(cardText)) throw new Error('Library book titles are missing');
  if(!/Author One/.test(cardText)||!/Author Two/.test(cardText)) throw new Error('Library authors are missing');
  for(const c of libraryCards.slice(0,2)){
    if(!c.querySelector('.cover-wrap')) throw new Error('Library cover wrapper missing');
    if(!c.querySelector('.cover-placeholder, .cover-wrap img')) throw new Error('Library visible cover/placeholder missing');
    if(!c.querySelector('.book-name')) throw new Error('Library book-name element missing');
    if(!c.querySelector('.book-author')) throw new Error('Library book-author element missing');
    if(!c.querySelector('.vnext-cover-format')) throw new Error('Library format badge missing');
  }
  const htmlFinal=d.documentElement.innerHTML;
  if(!htmlFinal.includes('v046-library-repair')) throw new Error('Library repair CSS missing from final DOM');
  console.log('MYREADER_LIBRARY_RENDER_SMOKE_TEST_PASS');


  if(errors.length) console.log('JSDOM_WARNINGS',JSON.stringify(errors.slice(0,10)));
  console.log('MYREADER_UI_SMOKE_TEST_PASS');
  console.log(JSON.stringify(result));
  process.exit(0);
})().catch(e=>{console.error(e.stack||e);process.exit(1)});
