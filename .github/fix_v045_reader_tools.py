from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')

css=r'''
<style id="v045-reader-tool-fix">
/* Hard geometry: reader content in the middle, controls always at the bottom. */
#reader{position:relative!important;display:block!important;height:100%!important;min-height:0!important;overflow:hidden!important}
#reader .reader-head{
  position:absolute!important;left:0!important;right:0!important;top:0!important;z-index:55!important;
  height:55px!important;min-height:55px!important;max-height:55px!important
}
#reader .reader-page{
  position:absolute!important;left:0!important;right:0!important;top:55px!important;bottom:101px!important;
  width:auto!important;height:auto!important;min-height:0!important;overflow:hidden!important
}
#reader.pdf-mode .reader-page{display:none!important}
#reader.pdf-mode .pdf-wrap{
  position:absolute!important;left:0!important;right:0!important;top:55px!important;bottom:101px!important;
  width:auto!important;height:auto!important;min-height:0!important;z-index:2!important
}
#readerFooter.vnext-reader-footer{
  position:absolute!important;left:0!important;right:0!important;bottom:0!important;top:auto!important;
  z-index:56!important;width:100%!important;height:101px!important;min-height:101px!important;
  flex:none!important;margin:0!important;padding:0!important;background:var(--paper)!important
}
#readerFooter .vnext-progress-pill{top:0!important;left:11px!important;right:11px!important}
#readerFooter .vnext-reader-tools{bottom:0!important;left:0!important;right:0!important;height:69px!important}
#reader.chrome-hidden .reader-head{position:absolute!important;top:0!important;height:55px!important}
#reader.chrome-hidden .reader-page{top:55px!important;bottom:101px!important}
#reader.pdf-mode.chrome-hidden .pdf-wrap{top:55px!important;bottom:101px!important}
#reader.chrome-hidden #readerFooter{position:absolute!important;bottom:0!important;height:101px!important;min-height:101px!important}

/* Reader sheets are interactive and sit above the fixed bottom controls. */
#vnextSheetBackdrop{z-index:100!important}
#vnextSheetBackdrop.show{display:flex!important;pointer-events:auto!important}
#vnextSheetBackdrop .vnext-sheet{z-index:101!important;pointer-events:auto!important;max-height:76dvh!important}
#vnextSheetBackdrop button,#vnextSheetBackdrop input,#vnextSheetBackdrop select{
  pointer-events:auto!important;touch-action:manipulation!important
}
.v45-control{display:grid;grid-template-columns:38px minmax(0,1fr) 38px;align-items:center;gap:9px}
.v45-control button{height:36px;border:1px solid var(--line);border-radius:10px;background:#fff;font-size:18px}
.v45-control input[type=range]{width:100%;accent-color:var(--accent)}
.v45-select{width:100%;height:39px;border:1px solid var(--line);border-radius:10px;background:#fff;padding:0 10px}
.v45-toc-list{display:grid;gap:6px}
.v45-toc-item{border:1px solid var(--line);background:#fff;border-radius:11px;padding:10px 11px;text-align:left;font-size:11px;line-height:1.35}
.v45-empty{padding:18px 4px;color:var(--muted);font-size:11px;line-height:1.5}
.v45-theme-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:7px}
.v45-theme{border:0;background:transparent;display:grid;place-items:center;gap:5px;font-size:8px}
.v45-theme i{width:32px;height:32px;border:1px solid var(--line);border-radius:50%}
.v45-theme.active i{outline:2px solid var(--ink);outline-offset:2px}
</style>
'''
head=h.find('</head>')
assert head>0
h=h[:head]+css+'\n'+h[head:]

# Static button route correction.
h=h.replace('<button onclick="toggleReaderNav()"><span>☰</span>Contents</button>',
            '<button onclick="v045OpenContents()"><span>☰</span>Contents</button>',1)

js=r'''
<script id="v045-reader-tool-fix-js">
(function(){
  function sheet(title,body){openSheet(title,body)}
  function esc45(v){return escapeHtml(String(v==null?'':v))}
  function currentExt(){return currentBook&&currentBook.ext||''}

  window.v045OpenContents=async function(){
    if(!currentBook)return;
    if(currentExt()==='pdf'){
      sheet('Contents','<div id="v45PdfToc" class="v45-empty">Loading PDF contents…</div>');
      const host=document.getElementById('v45PdfToc');
      try{
        const doc=pdfState&&pdfState.doc;
        if(!doc||typeof doc.getOutline!=='function'){
          host.className='v45-empty';host.innerHTML='<b>No table of contents</b><br>This PDF does not expose an outline.';
          return;
        }
        const outline=await doc.getOutline();
        if(!outline||!outline.length){
          host.className='v45-empty';host.innerHTML='<b>No table of contents</b><br>This PDF does not contain outline/bookmark metadata. Use Navigate for page numbers.';
          return;
        }
        const rows=[];
        async function walk(items,depth){
          for(const item of items||[]){
            let dest=item.dest;
            try{
              if(typeof dest==='string')dest=await doc.getDestination(dest);
              if(dest&&dest[0]){
                const idx=await doc.getPageIndex(dest[0]);
                rows.push({title:item.title||('Page '+(idx+1)),page:idx,depth:depth});
              }
            }catch(_){}
            if(item.items&&item.items.length)await walk(item.items,depth+1);
          }
        }
        await walk(outline,0);
        window.__v045TocRows=rows;
        host.className='v45-toc-list';
        host.innerHTML=rows.length?rows.map((r,i)=>'<button class="v45-toc-item" style="padding-left:'+(11+r.depth*13)+'px" onclick="v045JumpPdfToc('+i+')">'+esc45(r.title)+'<span style="float:right;color:var(--muted)">'+(r.page+1)+'</span></button>').join(''):'<div class="v45-empty"><b>No usable table of contents</b><br>Use Navigate for page numbers.</div>';
      }catch(e){
        host.className='v45-empty';host.textContent='Could not read this PDF table of contents.';
      }
      return;
    }
    if(epubState&&epubState.chapters&&epubState.chapters.length){
      sheet('Contents','<div class="v45-toc-list">'+epubState.chapters.map((c,i)=>'<button class="v45-toc-item" onclick="showEpubChapter('+i+');vnextCloseSheet()">'+esc45(c.title||('Chapter '+(i+1)))+'</button>').join('')+'</div>');
      return;
    }
    sheet('Contents','<div class="v45-empty"><b>No table of contents</b><br>This book does not provide chapter metadata.</div>');
  };
  window.v045JumpPdfToc=async function(i){
    const r=(window.__v045TocRows||[])[i];if(!r||!pdfState)return;
    pdfState.page=Math.max(0,Math.min(pdfState.count-1,r.page));vnextCloseSheet();await renderPdfPage();
  };

  function rangeRow(label,min,max,step,value,minus,plus,oninput){
    return '<div class="v44-format-row"><div class="v44-format-label">'+label+'</div><div class="v45-control">'+
      '<button onclick="'+minus+'">−</button><input type="range" min="'+min+'" max="'+max+'" step="'+step+'" value="'+value+'" oninput="'+oninput+';this.dispatchEvent(new Event(\'change\'))" onchange="'+oninput+'"><button onclick="'+plus+'">＋</button></div></div>';
  }

  window.v045EpubStep=function(key,delta){
    if(key==='font')setReaderFontSize(Number(settings.font||20)+delta);
    if(key==='line')setReaderLineValue(Number(settings.line||1.72)+delta);
    if(key==='margin')setReaderMarginValue(Number(settings.margin||28)+delta);
    if(key==='brightness')setReaderBrightness(Number(settings.brightness||55)+delta);
    if(key==='strength')setTextStrength(Number(settings.textStrength||22)+delta);
    vnextOpenFormat();
  };
  window.v045SetFont=function(v){setReaderFontFamily(v);vnextOpenFormat()};
  window.v045Theme=function(v){const b=document.createElement('button');b.dataset.v=v;setTheme(b);vnextOpenFormat()};

  function epubFormat45(){
    const theme=settings.theme||'paper';
    return '<div class="v44-format-row"><div class="v44-format-label">Font</div><select class="v45-select" onchange="v045SetFont(this.value)">'+
      ['Literata','Georgia','Bookerly','Arial','system'].map(x=>'<option value="'+x+'" '+((settings.fontFamily||'Literata')===x?'selected':'')+'>'+x+'</option>').join('')+'</select></div>'+
      rangeRow('Text size',14,34,1,settings.font||20,"v045EpubStep('font',-1)","v045EpubStep('font',1)","setReaderFontSize(this.value)")+
      rangeRow('Line spacing',1.3,2.1,.05,settings.line||1.72,"v045EpubStep('line',-.05)","v045EpubStep('line',.05)","setReaderLineValue(this.value)")+
      rangeRow('Margins',12,48,2,settings.margin||28,"v045EpubStep('margin',-2)","v045EpubStep('margin',2)","setReaderMarginValue(this.value)")+
      '<div class="v44-format-row"><div class="v44-format-label">Theme</div><div class="v45-theme-grid">'+
      [['paper','#f2f0ea','Paper'],['warm','#efe1ca','Warm'],['amber','#e7cca2','Amber'],['eink','#e5e5e0','E-ink'],['night','#171714','Night']].map(t=>'<button class="v45-theme '+(theme===t[0]?'active':'')+'" onclick="v045Theme(\''+t[0]+'\')"><i style="background:'+t[1]+'"></i><span>'+t[2]+'</span></button>').join('')+
      '</div></div>'+
      rangeRow('Brightness',0,100,1,settings.brightness||55,"v045EpubStep('brightness',-5)","v045EpubStep('brightness',5)","setReaderBrightness(this.value)")+
      rangeRow('Text strength',0,100,1,settings.textStrength||22,"v045EpubStep('strength',-5)","v045EpubStep('strength',5)","setTextStrength(this.value)");
  }

  function pdfFormat45(){
    const view=pdfState&&pdfState.viewMode||'page',crop=pdfState&&pdfState.cropMode||'auto';
    const zoom=Math.round((pdfState&&pdfState.zoom||1)*100),blank=Number(pdfState&&pdfState.margin||0);
    const opt=(mode,icon,label)=>'<button class="v44-square-opt '+(view===mode?'active':'')+'" onclick="setPdfViewMode(\''+mode+'\');vnextOpenFormat()"><span class="ico">'+icon+'</span><span>'+label+'</span></button>';
    const cr=(mode,icon,label)=>'<button class="v44-square-opt '+(crop===mode?'active':'')+'" onclick="v44PdfCrop(\''+mode+'\');vnextOpenFormat()"><span class="ico">'+icon+'</span><span>'+label+'</span></button>';
    return '<div class="v44-format-row"><div class="v44-format-label">Page display</div><div class="v44-option-grid" id="v45PdfDisplay">'+
      opt('page','▤','Single')+opt('scroll','▥','Continuous')+opt('width','↔','Fit width')+opt('crop','⌗','Auto fit')+'</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Zoom</div><div class="v45-control"><button onclick="v44PdfZoom(-.1);vnextOpenFormat()">−</button><div style="text-align:center;font-weight:800">'+zoom+'%</div><button onclick="v44PdfZoom(.1);vnextOpenFormat()">＋</button></div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Crop</div><div class="v44-option-grid crop5">'+
      cr('none','□','None')+cr('tb','↕','Top/Bottom')+cr('lr','↔','Left/Right')+cr('auto','⌗','Auto')+cr('manual','✥','Manual')+'</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Leave blank space</div><input class="v44-range" type="range" min="0" max="48" step="2" value="'+blank+'" oninput="v44PdfBlank(this.value)" onchange="v44PdfBlank(this.value)"><div class="v44-note">Current: '+blank+' px</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Rotation</div><button class="v44-square-opt" onclick="v44PdfRotate();vnextOpenFormat()"><span class="ico">↻</span><span>Rotate 90°</span></button></div>';
  }

  window.vnextOpenFormat=function(){
    sheet('Format',currentExt()==='pdf'?pdfFormat45():epubFormat45());
  };

  /* Navigate alone owns Go to page. */
  window.vnextOpenNavigate=function(){
    let value=1,max=1;
    if(currentExt()==='pdf'&&pdfState){value=pdfState.page+1;max=pdfState.count}
    else{value=(textPageState&&textPageState.page||0)+1;max=Math.max(1,textPageState&&textPageState.count||1)}
    sheet('Navigate','<div class="v44-format-row"><div class="v44-format-label">Go to page</div><div class="vnext-go-row"><input id="vnextGoInput" type="number" min="1" max="'+max+'" value="'+value+'" inputmode="numeric"><button onclick="vnextGoPage()">Go</button></div><div class="v44-note">Page 1 – '+max+'</div></div>');
  };

  function wire(){
    const tools=document.querySelectorAll('#readerFooter .vnext-reader-tools button');
    if(tools[0])tools[0].onclick=v045OpenContents;
    if(tools[2])tools[2].onclick=vnextOpenFormat;
    if(tools[4])tools[4].onclick=vnextOpenNavigate;
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',wire);else wire();
})();
</script>
'''
body=h.rfind('</body>')
assert body>0
h=h[:body]+js+'\n'+h[body:]

# Version
gpath=Path('app/build.gradle')
g=gpath.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 40',g,count=1)
g=re.sub(r"versionName\s+['\"][^'\"]+['\"]","versionName '0.4.5-reader-tools'",g,count=1)
gpath.write_text(g,encoding='utf-8')

# Guards
assert 'onclick="v045OpenContents()"' in h
assert 'window.vnextOpenFormat=function()' in h
assert 'window.v045OpenContents=async function()' in h
assert 'No table of contents' in h
assert 'Navigate alone owns Go to page' in h
assert '#readerFooter.vnext-reader-footer' in h
assert 'position:absolute!important;left:0!important;right:0!important;bottom:0!important' in h
p.write_text(h,encoding='utf-8')
print('v0.4.5 reader tools fixed')
