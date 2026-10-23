from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')

# Insert only at the REAL closing head/body, never ambiguous string-template anchors.
head_i=h.rfind('</head>')
body_i=h.rfind('</body>')
assert head_i>0 and body_i>head_i

css=r'''
<style id="v043-approved-reader-fixes">
/* Shared reader chrome for EPUB + PDF. Old PDF controls are retired. */
#pdfControls{display:none!important}
#reader.pdf-mode .vnext-reader-footer{display:block!important}
#reader.pdf-mode .pdf-wrap{
  position:absolute!important;
  left:0!important;right:0!important;
  top:62px!important;bottom:91px!important;
  width:auto!important;height:auto!important;
  padding:0!important;margin:0!important;
  overflow:hidden!important;
  align-items:stretch!important;justify-content:stretch!important;
  background:#d9d9d5!important;
}
#reader.pdf-mode.chrome-hidden .pdf-wrap{top:0!important;bottom:0!important}
#reader.pdf-mode .pdf-page-surface{
  position:absolute!important;
  margin:0!important;
  max-width:none!important;
  max-height:none!important;
  transform-origin:top left!important;
  box-shadow:none!important;
}

/* Approved v8 Format sheet */
.v043-format-body{padding:0 1px}
.v043-format-row{padding:11px 0;border-bottom:1px solid var(--line)}
.v043-format-row:last-child{border-bottom:0}
.v043-format-label{font-size:10px;color:var(--muted);margin-bottom:9px;font-weight:800;text-transform:uppercase;letter-spacing:.1em}
.v043-option-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.v043-option-grid.crop5{grid-template-columns:repeat(5,1fr)}
.v043-square-opt{border:1px solid var(--line);background:#fff;border-radius:11px;min-height:58px;padding:7px 4px;font-size:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;text-align:center;color:var(--ink)}
.v043-square-opt.active{border-color:var(--accent);background:var(--accent-soft);box-shadow:inset 0 0 0 1px var(--accent)}
.v043-crop-ico{width:24px;height:24px;position:relative;border:1px solid #999}
.v043-crop-ico:before,.v043-crop-ico:after{content:"";position:absolute;border-color:var(--ink);border-style:solid}
.v043-crop-none:before{inset:4px;border-width:1px}
.v043-crop-v:before{inset:1px 5px;border-width:1px 0}
.v043-crop-h:before{inset:5px 1px;border-width:0 1px}
.v043-crop-auto:before{inset:4px;border-width:1px}
.v043-crop-auto:after{inset:-3px;border-width:2px;border-color:var(--accent)}
.v043-crop-manual:before{inset:6px 3px 3px 6px;border-width:1px}
.v043-format-note{margin-top:8px;font-size:9px;color:var(--muted);line-height:1.45}
.v043-zoom-row{display:flex;align-items:center;justify-content:space-between;gap:10px}
.v043-zoom-btn{width:39px;height:36px;border:1px solid var(--line);background:#fff;border-radius:10px;font-size:19px;color:var(--ink)}
.v043-zoom-value{font-size:12px;font-weight:800}
.v043-range{width:100%;accent-color:var(--accent)}

/* Import review must never disappear behind bottom navigation/system inset. */
#importOverlay{
  position:fixed!important;
  inset:0!important;
  z-index:220!important;
  align-items:flex-end!important;
  padding:0!important;
}
#importOverlay>.sheet{
  height:min(88dvh,760px)!important;
  max-height:calc(100dvh - 14px)!important;
  min-height:0!important;
  overflow:hidden!important;
  display:flex!important;
  flex-direction:column!important;
  padding-bottom:env(safe-area-inset-bottom,0px)!important;
}
#importOverlay .sheet-head{flex:0 0 auto!important}
#importOverlay #importReviewList{
  flex:1 1 auto!important;
  min-height:0!important;
  overflow-y:auto!important;
  overscroll-behavior:contain!important;
  padding-bottom:24px!important;
}
#importOverlay .sheet-foot{
  flex:0 0 auto!important;
  position:relative!important;
  z-index:3!important;
  background:var(--paper)!important;
  padding-bottom:calc(18px + env(safe-area-inset-bottom,0px))!important;
}
@media(max-width:430px){
  #importOverlay .import-card{grid-template-columns:72px minmax(0,1fr)!important;gap:10px!important}
  #importOverlay .import-cover{width:72px!important}
}
</style>
'''
h=h[:head_i]+css+'\n'+h[head_i:]

# Recompute real body close after head insertion.
body_i=h.rfind('</body>')

js=r'''
<script id="v043-approved-reader-fixes-js">
(function(){
  const state={zoom:Number(localStorage.getItem('v043FormatZoom')||100),blank:Number(localStorage.getItem('v043Blank')||0),display:localStorage.getItem('v043Display')||'Single',crop:localStorage.getItem('v043Crop')||'Auto'};

  function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
  function active(a,b){return a===b?' active':''}

  window.vnextOpenFormat=function(){
    if(typeof vnextCloseSheet==='function')vnextCloseSheet();
    if(typeof ensureSheets==='function')ensureSheets();
    const crop=state.crop;
    const html=`
      <div class="v043-format-body">
        <div class="v043-format-row"><div class="v043-format-label">Page display</div>
          <div class="v043-option-grid" id="v043DisplayOptions">
            <button class="v043-square-opt${active(state.display,'Single')}" onclick="v043SetDisplay('Single')"><span style="font-size:21px">▤</span><span>Single</span></button>
            <button class="v043-square-opt${active(state.display,'Continuous')}" onclick="v043SetDisplay('Continuous')"><span style="font-size:21px">▥</span><span>Continuous</span></button>
            <button class="v043-square-opt${active(state.display,'Facing')}" onclick="v043SetDisplay('Facing')"><span style="font-size:21px">▦</span><span>Facing</span></button>
            <button class="v043-square-opt${active(state.display,'Horizontal')}" onclick="v043SetDisplay('Horizontal')"><span style="font-size:21px">↔</span><span>Horizontal</span></button>
          </div>
        </div>
        <div class="v043-format-row"><div class="v043-format-label">Zoom</div>
          <div class="v043-zoom-row"><button class="v043-zoom-btn" onclick="v043Zoom(-10)">−</button><span class="v043-zoom-value" id="v043ZoomValue">${state.zoom}%</span><button class="v043-zoom-btn" onclick="v043Zoom(10)">＋</button></div>
        </div>
        <div class="v043-format-row"><div class="v043-format-label">Crop</div>
          <div class="v043-option-grid crop5" id="v043CropOptions">
            <button class="v043-square-opt${active(crop,'None')}" onclick="v043SetCrop('None')"><span class="v043-crop-ico v043-crop-none"></span><span>None</span></button>
            <button class="v043-square-opt${active(crop,'Top/Bottom')}" onclick="v043SetCrop('Top/Bottom')"><span class="v043-crop-ico v043-crop-v"></span><span>Top/Bottom</span></button>
            <button class="v043-square-opt${active(crop,'Left/Right')}" onclick="v043SetCrop('Left/Right')"><span class="v043-crop-ico v043-crop-h"></span><span>Left/Right</span></button>
            <button class="v043-square-opt${active(crop,'Auto')}" onclick="v043SetCrop('Auto')"><span class="v043-crop-ico v043-crop-auto"></span><span>Auto</span></button>
            <button class="v043-square-opt${active(crop,'Manual')}" onclick="v043SetCrop('Manual')"><span class="v043-crop-ico v043-crop-manual"></span><span>Manual</span></button>
          </div>
          <div class="v043-format-note" id="v043CropNote"><b>Selected:</b> ${esc(crop==='Auto'?'Auto crop all margins':crop)}.</div>
        </div>
        <div class="v043-format-row"><div class="v043-format-label">Leave blank space</div>
          <input class="v043-range" type="range" min="0" max="20" value="${state.blank}" oninput="v043SetBlank(this.value)">
          <div class="v043-format-note">Current: <b id="v043BlankValue">${state.blank}</b></div>
        </div>
      </div>`;
    openSheet('Format',html);
  };

  function redraw(){
    if(currentBook?.ext==='pdf'&&pdfState&&typeof renderPdfPage==='function')renderPdfPage();
    else if(typeof layoutTextPages==='function')layoutTextPages();
  }
  window.v043SetDisplay=function(v){
    state.display=v;localStorage.setItem('v043Display',v);
    if(currentBook?.ext==='pdf'&&pdfState){
      const map={Single:'page',Continuous:'scroll',Facing:'page',Horizontal:'width'};
      setPdfViewMode(map[v]||'page');
    }
    vnextOpenFormat();
  };
  window.v043Zoom=function(d){
    state.zoom=Math.max(70,Math.min(180,state.zoom+Number(d||0)));localStorage.setItem('v043FormatZoom',String(state.zoom));
    if(currentBook?.ext==='pdf') redraw();
    else{
      const base=Number(settings?.fontSize||18);settings.fontSize=Math.max(14,Math.min(34,base*(1+Number(d||0)/100)));saveSettings?.();applyReaderSettings?.();layoutTextPages?.();
    }
    const el=document.getElementById('v043ZoomValue');if(el)el.textContent=state.zoom+'%';
  };
  window.v043SetCrop=function(v){
    state.crop=v;localStorage.setItem('v043Crop',v);
    if(currentBook?.ext==='pdf'&&pdfState){
      pdfState.viewMode=(v==='None'?'page':'crop');
      localStorage.setItem('pdfViewMode_v1',pdfState.viewMode);
      renderPdfPage();
    }
    vnextOpenFormat();
  };
  window.v043SetBlank=function(v){state.blank=Math.max(0,Math.min(20,Number(v)||0));localStorage.setItem('v043Blank',String(state.blank));const e=document.getElementById('v043BlankValue');if(e)e.textContent=state.blank;document.documentElement.style.setProperty('--v043Blank',state.blank+'px')};

  // PDF and EPUB use the exact same reader footer/tool menu.
  const oldOpenPdf=window.openPdf;
  if(typeof oldOpenPdf==='function'){
    window.openPdf=async function(b){
      const out=await oldOpenPdf(b);
      const footer=document.getElementById('readerFooter'), controls=document.getElementById('pdfControls');
      if(footer)footer.style.display='block';
      if(controls){controls.classList.remove('active');controls.style.display='none'}
      if(pdfState && !localStorage.getItem('v043PdfMigrated')){
        pdfState.viewMode='crop';localStorage.setItem('pdfViewMode_v1','crop');localStorage.setItem('v043Crop','Auto');state.crop='Auto';localStorage.setItem('v043PdfMigrated','1');
        await renderPdfPage();
      }
      return out;
    };
    try{openPdf=window.openPdf}catch(_){}
  }

  // Non-destructive Auto Crop: detect white margins, then position/scale the whole page
  // inside the actual PDF viewport so the cropped content fills the screen.
  window.applyAutoCropToPdfSurface=function(canvas,surface){
    try{
      const wrap=document.getElementById('pdfWrap'); if(!wrap||!canvas||!surface)return;
      const ctx=canvas.getContext('2d',{willReadFrequently:true}),w=canvas.width,h=canvas.height;if(!ctx||w<20||h<20)return;
      const step=Math.max(6,Math.floor(Math.min(w,h)/180)),data=ctx.getImageData(0,0,w,h).data;
      const dark=(x,y)=>{const i=(Math.max(0,Math.min(h-1,y))*w+Math.max(0,Math.min(w-1,x)))*4;return (data[i]+data[i+1]+data[i+2])/3<242};
      let l=0,r=w-1,t=0,b=h-1,hit=false;
      outerL:for(let x=0;x<w;x+=step){for(let y=0;y<h;y+=step){if(dark(x,y)){l=x;hit=true;break outerL}}}
      if(!hit)return;
      outerR:for(let x=w-1;x>=0;x-=step){for(let y=0;y<h;y+=step){if(dark(x,y)){r=x;break outerR}}}
      outerT:for(let y=0;y<h;y+=step){for(let x=0;x<w;x+=step){if(dark(x,y)){t=y;break outerT}}}
      outerB:for(let y=h-1;y>=0;y-=step){for(let x=0;x<w;x+=step){if(dark(x,y)){b=y;break outerB}}}
      let lf=l/w,rf=(w-1-r)/w,tf=t/h,bf=(h-1-b)/h;
      if(state.crop==='Top/Bottom'){lf=rf=0}
      if(state.crop==='Left/Right'){tf=bf=0}
      if(state.crop==='None'){lf=rf=tf=bf=0}
      const W=surface.offsetWidth||parseFloat(surface.style.width)||1,H=surface.offsetHeight||parseFloat(surface.style.height)||1;
      const cropW=Math.max(W*.45,W*(1-lf-rf)),cropH=Math.max(H*.45,H*(1-tf-bf));
      const aw=Math.max(1,wrap.clientWidth-state.blank*2),ah=Math.max(1,wrap.clientHeight-state.blank*2);
      let z=Math.min(aw/cropW,ah/cropH)*(state.zoom/100);
      z=Math.max(.35,Math.min(3.2,z));
      const x=(wrap.clientWidth-cropW*z)/2-(lf*W*z);
      const y=(wrap.clientHeight-cropH*z)/2-(tf*H*z);
      surface.style.left=x+'px';surface.style.top=y+'px';surface.style.transform='scale('+z+')';surface.style.transformOrigin='top left';surface.style.margin='0';
    }catch(e){console.warn('v043 crop unavailable',e)}
  };
  try{applyAutoCropToPdfSurface=window.applyAutoCropToPdfSurface}catch(_){}

  // Center Fit Page/Width too; no giant gray dead zone caused by normal-flow margins.
  const oldRender=window.renderPdfPage;
  if(typeof oldRender==='function'){
    window.renderPdfPage=async function(){
      const out=await oldRender();
      const surface=document.getElementById('pdfPageSurface'),wrap=document.getElementById('pdfWrap');
      if(surface&&wrap&&pdfState&&pdfState.viewMode!=='crop'){
        const W=surface.offsetWidth||parseFloat(surface.style.width)||1,H=surface.offsetHeight||parseFloat(surface.style.height)||1;
        let z=1;
        if(pdfState.viewMode==='page')z=Math.min(wrap.clientWidth/W,wrap.clientHeight/H);
        else if(pdfState.viewMode==='width')z=wrap.clientWidth/W;
        z*=state.zoom/100;
        surface.style.transform='scale('+z+')';surface.style.transformOrigin='top left';
        surface.style.left=Math.max(0,(wrap.clientWidth-W*z)/2)+'px';
        surface.style.top=Math.max(0,(wrap.clientHeight-H*z)/2)+'px';
      }
      const footer=document.getElementById('readerFooter');if(footer)footer.style.display='block';
      const controls=document.getElementById('pdfControls');if(controls)controls.style.display='none';
      if(typeof updateProgressBar==='function')updateProgressBar();
      if(pdfState){const loc=document.getElementById('readerLocation'),pr=document.getElementById('readerProgress');if(loc)loc.textContent='Page '+(pdfState.page+1);if(pr)pr.textContent=(pdfState.page+1)+' / '+pdfState.count+' · '+Math.round((pdfState.page+1)/Math.max(1,pdfState.count)*100)+'%'}
      return out;
    };
    try{renderPdfPage=window.renderPdfPage}catch(_){}
  }

  // Import sheet geometry is asserted by build; no behavioral replacement needed.
  window.__v043ApprovedFix=true;
})();
</script>
'''
h=h[:body_i]+js+'\n'+h[body_i:]

# openPdf in this app is a lexical global; make shared footer visible before old render starts.
h=h.replace("document.getElementById('readerPage').style.display='none';document.getElementById('readerFooter').style.display='none';document.getElementById('pdfWrap').classList.add('active');document.getElementById('pdfControls').classList.add('active');",
            "document.getElementById('readerPage').style.display='none';document.getElementById('readerFooter').style.display='block';document.getElementById('pdfWrap').classList.add('active');document.getElementById('pdfControls').classList.remove('active');")

# Default PDF mode becomes crop for new books.
h=h.replace("viewMode:localStorage.getItem('pdfViewMode_v1')||'width'","viewMode:localStorage.getItem('pdfViewMode_v1')||'crop'")

assert 'id="v043-approved-reader-fixes"' in h
assert 'id="v043-approved-reader-fixes-js"' in h
assert "openSheet('Format',html)" in h
assert 'Page display' in h and 'Leave blank space' in h
assert "#pdfControls{display:none!important}" in h
assert "#importOverlay #importReviewList" in h
assert "viewMode:localStorage.getItem('pdfViewMode_v1')||'crop'" in h

p.write_text(h,encoding='utf-8')
print('v0.4.3 approved PDF/Format/import fixes applied')
