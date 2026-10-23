from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')

css=r'''
<style id="v043-approved-reader-fix">
/* PDF uses the same approved reader toolbar as EPUB/TXT. */
#reader.pdf-mode .pdf-controls{display:none!important}
#reader.pdf-mode #pdfModePanel{display:none!important}
#reader.pdf-mode .vnext-reader-footer{
  position:absolute!important;left:0!important;right:0!important;bottom:0!important;
  z-index:46!important;display:block!important;background:rgba(247,247,243,.97)!important
}
#reader.pdf-mode .pdf-wrap{
  position:absolute!important;inset:0!important;
  padding:0!important;margin:0!important;overflow:auto!important;
  align-items:center!important;justify-content:flex-start!important;
  background:#d9d9d5!important
}
#reader.pdf-mode .pdf-page-surface{margin:0 auto!important;transform-origin:top center!important}

/* Approved Format sheet from prototype v8. */
.v043-format-row{padding:13px 0;border-bottom:1px solid var(--line)}
.v043-format-row:last-child{border-bottom:0}
.v043-format-label{font-size:12px;font-weight:850;margin-bottom:9px}
.v043-option-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}
.v043-option-grid.crop5{grid-template-columns:repeat(5,1fr)}
.v043-square{
  min-width:0;border:1px solid var(--line);background:var(--paper);border-radius:12px;
  padding:10px 4px 8px;display:flex;flex-direction:column;align-items:center;gap:4px;
  font-size:9px;font-weight:750;color:var(--muted)
}
.v043-square.active{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.v043-square .ico{font-size:20px;line-height:1}
.v043-zoom{display:grid;grid-template-columns:44px 1fr 44px;gap:9px;align-items:center}
.v043-zoom button{border:1px solid var(--line);background:var(--paper);border-radius:11px;font-size:20px}
.v043-zoom-value{text-align:center;font-size:16px;font-weight:850}
.v043-range{width:100%;accent-color:var(--ink)}
.v043-note{font-size:10px;color:var(--muted);line-height:1.4;margin-top:8px}

/* Import review must stay above the app nav and keep actions visible. */
#importOverlay{z-index:220!important;align-items:flex-end!important;padding-bottom:0!important}
#importOverlay>.sheet{
  max-height:calc(100dvh - 20px)!important;height:auto!important;
  overflow:hidden!important;padding-bottom:0!important
}
#importOverlay .sheet-body{flex:1 1 auto!important;min-height:0!important;overflow:auto!important;padding-bottom:18px!important}
#importOverlay .sheet-foot{
  flex:0 0 auto!important;position:relative!important;z-index:2!important;
  background:var(--paper)!important;
  padding:12px 20px calc(18px + env(safe-area-inset-bottom,0px))!important
}
#importOverlay .import-card{margin-bottom:14px!important}
</style>
'''

head_end=h.rfind('</head>')
assert head_end>0
h=h[:head_end]+css+'\n'+h[head_end:]

js=r'''
<script id="v043-approved-reader-js">
(function(){
  const state={
    display:localStorage.getItem('v043Display')||'Single',
    zoom:Number(localStorage.getItem('v043Zoom')||100),
    crop:localStorage.getItem('v043Crop')||'Auto',
    blank:Number(localStorage.getItem('v043Blank')||0)
  };

  function setActive(group,value){
    document.querySelectorAll(group+' [data-v]').forEach(b=>b.classList.toggle('active',b.dataset.v===value));
  }

  function applyPdfZoom(){
    if(!window.pdfState)return;
    const surface=document.getElementById('pdfPageSurface');
    if(!surface)return;
    const auto=Number(surface.dataset.autoCropZoom||1);
    const user=Math.max(.7,Math.min(1.8,state.zoom/100));
    surface.style.transform='scale('+(auto*user)+')';
    surface.style.transformOrigin='top center';
    const wrap=document.getElementById('pdfWrap');
    if(wrap)wrap.style.paddingBottom=Math.max(0,(auto*user-1)*surface.clientHeight+state.blank)+'px';
  }

  window.v043SetDisplay=function(v){
    state.display=v;localStorage.setItem('v043Display',v);setActive('#v043DisplayOptions',v);
    if(window.pdfState){
      const map={Single:'page',Continuous:'scroll',Facing:'page',Horizontal:'width'};
      if(typeof setPdfViewMode==='function')setPdfViewMode(map[v]||'page');
    }else{
      showToast('Page display: '+v);
    }
  };

  window.v043Zoom=function(delta){
    state.zoom=Math.max(70,Math.min(180,state.zoom+delta));
    localStorage.setItem('v043Zoom',String(state.zoom));
    const el=document.getElementById('v043ZoomValue');if(el)el.textContent=state.zoom+'%';
    applyPdfZoom();
  };

  window.v043SetCrop=function(v){
    state.crop=v;localStorage.setItem('v043Crop',v);setActive('#v043CropOptions',v);
    const note=document.getElementById('v043CropNote');
    if(note)note.innerHTML='<b>Selected:</b> '+(v==='Auto'?'Auto crop all margins':v);
    if(window.pdfState){
      if(v==='Auto'){setPdfViewMode('crop')}
      else if(v==='None'){setPdfViewMode('page')}
      else if(v==='Left/Right'){setPdfViewMode('width')}
      else if(v==='Top/Bottom'){setPdfViewMode('page');showToast('Top/Bottom crop')}
      else {showToast('Manual crop: use Zoom to adjust')}
    }
  };

  window.v043SetBlank=function(v){
    state.blank=Number(v)||0;localStorage.setItem('v043Blank',String(state.blank));
    const el=document.getElementById('v043BlankVal');if(el)el.textContent=String(state.blank);
    const wrap=document.getElementById('pdfWrap');if(wrap)wrap.style.paddingBottom=state.blank+'px';
  };

  function formatHtml(){
    return '<div class="v043-format-row"><div class="v043-format-label">Page display</div>'+
      '<div class="v043-option-grid" id="v043DisplayOptions">'+
      ['Single','Continuous','Facing','Horizontal'].map((x,i)=>'<button class="v043-square '+(state.display===x?'active':'')+'" data-v="'+x+'" onclick="v043SetDisplay(\''+x+'\')"><span class="ico">'+['▤','▥','▦','↔'][i]+'</span><span>'+x+'</span></button>').join('')+
      '</div></div>'+
      '<div class="v043-format-row"><div class="v043-format-label">Zoom</div><div class="v043-zoom"><button onclick="v043Zoom(-10)">−</button><div class="v043-zoom-value" id="v043ZoomValue">'+state.zoom+'%</div><button onclick="v043Zoom(10)">＋</button></div></div>'+
      '<div class="v043-format-row"><div class="v043-format-label">Crop</div><div class="v043-option-grid crop5" id="v043CropOptions">'+
      ['None','Top/Bottom','Left/Right','Auto','Manual'].map((x,i)=>'<button class="v043-square '+(state.crop===x?'active':'')+'" data-v="'+x+'" onclick="v043SetCrop(\''+x+'\')"><span class="ico">'+['□','↕','↔','⌗','✥'][i]+'</span><span>'+x+'</span></button>').join('')+
      '</div><div class="v043-note" id="v043CropNote"><b>Selected:</b> '+(state.crop==='Auto'?'Auto crop all margins':state.crop)+'</div></div>'+
      '<div class="v043-format-row"><div class="v043-format-label">Leave blank space</div><input class="v043-range" type="range" min="0" max="40" value="'+state.blank+'" oninput="v043SetBlank(this.value)"><div class="v043-note">Current: <b id="v043BlankVal">'+state.blank+'</b></div></div>';
  }

  window.vnextOpenFormat=function(){
    if(typeof vnextCloseSheet==='function')vnextCloseSheet();
    if(typeof openSheet==='function')openSheet('Format',formatHtml());
  };

  /* Stronger auto crop: detect real content, enlarge it while preserving all content. */
  window.applyAutoCropToPdfSurface=function(canvas,surface){
    try{
      const ctx=canvas.getContext('2d',{willReadFrequently:true}),w=canvas.width,h=canvas.height;
      if(!ctx||w<20||h<20)return;
      const step=Math.max(5,Math.floor(Math.min(w,h)/220)),data=ctx.getImageData(0,0,w,h).data;
      const dark=(x,y)=>{const i=(Math.max(0,Math.min(h-1,y))*w+Math.max(0,Math.min(w-1,x)))*4;return (data[i]+data[i+1]+data[i+2])/3<242};
      let l=0,r=w-1,t=0,b=h-1,hit=false;
      outerL:for(let x=0;x<w;x+=step){for(let y=0;y<h;y+=step){if(dark(x,y)){l=x;hit=true;break outerL}}}
      if(!hit){surface.dataset.autoCropZoom='1';applyPdfZoom();return}
      outerR:for(let x=w-1;x>=0;x-=step){for(let y=0;y<h;y+=step){if(dark(x,y)){r=x;break outerR}}}
      outerT:for(let y=0;y<h;y+=step){for(let x=l;x<=r;x+=step){if(dark(x,y)){t=y;break outerT}}}
      outerB:for(let y=h-1;y>=0;y-=step){for(let x=l;x<=r;x+=step){if(dark(x,y)){b=y;break outerB}}}
      const contentW=Math.max(1,r-l),contentH=Math.max(1,b-t);
      const wrap=document.getElementById('pdfWrap');
      const cssW=Math.max(1,surface.clientWidth),cssH=Math.max(1,surface.clientHeight);
      const wrapW=Math.max(1,wrap?.clientWidth||cssW),wrapH=Math.max(1,(wrap?.clientHeight||cssH)-8);
      const contentCssW=cssW*(contentW/w),contentCssH=cssH*(contentH/h);
      const zoom=Math.max(1,Math.min(1.85,wrapW/contentCssW,wrapH/contentCssH));
      surface.dataset.autoCropZoom=String(zoom);
      applyPdfZoom();
    }catch(e){surface.dataset.autoCropZoom='1';applyPdfZoom()}
  };

  const oldRender=window.renderPdfPage;
  if(typeof oldRender==='function'){
    window.renderPdfPage=async function(){
      const r=await oldRender.apply(this,arguments);
      setTimeout(applyPdfZoom,0);
      return r;
    };
  }

  /* Keep PDF on the same approved toolbar. */
  const oldSync=window.syncPdfModeUI;
  if(typeof oldSync==='function'){
    window.syncPdfModeUI=function(){
      const r=oldSync.apply(this,arguments);
      const panel=document.getElementById('pdfModePanel');if(panel)panel.classList.remove('show');
      return r;
    };
  }

  window.__v043ApprovedReader=true;
})();
</script>
'''
body_end=h.rfind('</body>')
assert body_end>0
h=h[:body_end]+js+'\n'+h[body_end:]

assert 'id="v043-approved-reader-fix"' in h
assert 'id="v043-approved-reader-js"' in h
assert "window.vnextOpenFormat=function()" in h
assert '#reader.pdf-mode .pdf-controls{display:none!important}' in h
assert '#importOverlay{z-index:220!important' in h

p.write_text(h,encoding='utf-8')
print('v0.4.3 approved reader/PDF/import layout patch applied')
