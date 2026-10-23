from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')
ref=Path('.github/reference/MyReader-Full-vNext-Prototype-v8.html').read_text(encoding='utf-8')
for marker in [
    '.reader-top{height:55px',
    '.reader-progress{position:absolute',
    '.reader-tools{position:absolute',
    '.sheet{position:absolute',
    '.format-row{padding:11px 0'
]:
    assert marker in ref, 'Approved prototype marker missing: '+marker

css=r'''
<style id="v044-approved-prototype-shell">
/* Approved v8 reader geometry — shared by EPUB and PDF. */
#reader{position:relative!important;overflow:hidden!important}
#reader .reader-head{
  flex:0 0 55px!important;height:55px!important;min-height:55px!important;max-height:55px!important;
  padding:7px 11px!important;border-bottom:1px solid var(--line)!important;background:var(--paper)!important;
  opacity:1;visibility:visible;transform:none!important
}
#reader .reader-head-left{height:40px!important;display:flex!important;align-items:center!important;gap:7px!important}
#reader .reader-head .bookhead{font:700 13px Georgia,serif!important;max-width:58%!important}
#reader.chrome-hidden .reader-head{
  flex-basis:55px!important;height:55px!important;min-height:55px!important;max-height:55px!important;
  padding:7px 11px!important;opacity:0!important;visibility:hidden!important;pointer-events:none!important
}
#readerFooter.vnext-reader-footer{
  flex:0 0 101px!important;height:101px!important;min-height:101px!important;
  padding:0!important;border:0!important;background:var(--paper)!important;position:relative!important
}
#readerFooter .vnext-progress-pill{
  position:absolute!important;left:11px!important;right:11px!important;top:0!important;height:32px!important;
  border:1px solid var(--line)!important;border-radius:12px!important;background:rgba(251,250,246,.97)!important;
  display:flex!important;align-items:center!important;gap:8px!important;padding:8px 9px!important;
  font:9px Inter,system-ui,sans-serif!important;color:var(--muted)!important
}
#readerFooter .vnext-progress-line{flex:1!important;height:4px!important}
#readerFooter .vnext-reader-tools{
  position:absolute!important;left:0!important;right:0!important;bottom:0!important;height:69px!important;
  background:var(--paper)!important;border-top:1px solid var(--line)!important;
  display:grid!important;grid-template-columns:repeat(6,1fr)!important
}
#readerFooter .vnext-reader-tools button{
  border:0!important;background:transparent!important;display:flex!important;flex-direction:column!important;
  align-items:center!important;justify-content:center!important;gap:3px!important;
  font-size:7px!important;color:var(--muted)!important;padding:0!important
}
#readerFooter .vnext-reader-tools button span{font-size:18px!important;line-height:1!important;color:var(--ink)!important}
#reader.chrome-hidden #readerFooter{flex-basis:101px!important;height:101px!important;min-height:101px!important}
#reader.chrome-hidden #readerFooter .vnext-progress-pill,
#reader.chrome-hidden #readerFooter .vnext-reader-tools{opacity:0!important;visibility:hidden!important;pointer-events:none!important}

/* Stable reading viewport. Hiding controls never changes pagination or PDF scale. */
#reader .reader-page{padding-top:22px!important;padding-bottom:28px!important}
#reader.chrome-hidden .reader-page{padding-top:22px!important;padding-bottom:28px!important}
#reader.pdf-mode .pdf-wrap{
  position:absolute!important;left:0!important;right:0!important;top:55px!important;bottom:101px!important;
  width:auto!important;height:auto!important;margin:0!important;padding:0!important;overflow:auto!important;
  display:none;align-items:center!important;justify-content:center!important;background:#d9d9d5!important
}
#reader.pdf-mode .pdf-wrap.active{display:flex!important}
#reader.pdf-mode.chrome-hidden .pdf-wrap{top:55px!important;bottom:101px!important}
#reader.pdf-mode .pdf-page-surface{margin:auto!important;box-shadow:none!important}

/* One approved v8 sheet style for every reader tool. */
#vnextSheetBackdrop{
  position:absolute!important;inset:0!important;z-index:68!important;background:rgba(30,32,29,.24)!important;
  display:none!important;align-items:flex-end!important;pointer-events:none!important
}
#vnextSheetBackdrop.show{display:flex!important;pointer-events:auto!important}
#vnextSheetBackdrop .vnext-sheet{
  position:relative!important;left:auto!important;right:auto!important;bottom:auto!important;width:100%!important;
  z-index:70!important;background:var(--paper)!important;border-top:1px solid var(--line)!important;
  border-radius:20px 20px 0 0!important;box-shadow:0 -16px 35px rgba(0,0,0,.14)!important;
  transform:none!important;transition:none!important;max-height:72vh!important;overflow:auto!important
}
#vnextSheetBackdrop .vnext-sheet-head{
  position:sticky!important;top:0!important;z-index:2!important;background:var(--paper)!important;
  display:flex!important;align-items:center!important;justify-content:space-between!important;
  padding:13px 15px 10px!important;border-bottom:1px solid var(--line)!important
}
#vnextSheetBackdrop .vnext-sheet-head b{font-size:14px!important}
#vnextSheetBackdrop .vnext-sheet-close{
  width:30px!important;height:30px!important;border:1px solid var(--line)!important;border-radius:10px!important;
  background:var(--paper)!important;font-size:17px!important
}
#vnextSheetBody{padding:10px 15px 18px!important}
.v44-format-row{padding:11px 0;border-bottom:1px solid var(--line)}
.v44-format-row:last-child{border-bottom:0}
.v44-format-label{font-size:10px;color:var(--muted);margin-bottom:9px;font-weight:800;text-transform:uppercase;letter-spacing:.1em}
.v44-option-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.v44-option-grid.crop5{grid-template-columns:repeat(5,1fr)}
.v44-square-opt{
  border:1px solid var(--line);background:#fff;border-radius:11px;min-height:58px;padding:7px 4px;
  font-size:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;text-align:center
}
.v44-square-opt.active{border-color:var(--accent);background:var(--accent-soft);box-shadow:inset 0 0 0 1px var(--accent)}
.v44-square-opt .ico{font-size:21px;line-height:1}
.v44-zoom-row{display:flex;align-items:center;justify-content:space-between;gap:10px}
.v44-zoom-btn{width:39px;height:36px;border:1px solid var(--line);background:#fff;border-radius:10px;font-size:19px}
.v44-zoom-value{font-size:12px;font-weight:800}
.v44-range{width:100%;accent-color:var(--accent)}
.v44-note{margin-top:8px;font-size:9px;color:var(--muted);line-height:1.45}
.v44-theme-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.v44-theme{border:0;background:transparent;display:grid;place-items:center;gap:5px;font-size:8px}
.v44-theme i{width:34px;height:34px;border:1px solid var(--line);border-radius:50%;display:block}
.v44-theme.active i{outline:2px solid var(--ink);outline-offset:2px}

/* Settings/import: no artificial blank/crop. */
#settings .settings-scroll{flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;padding:0 20px 26px!important}
.bottomnav{position:relative!important;left:auto!important;right:auto!important;bottom:auto!important;flex:0 0 70px!important}
#importOverlay{position:absolute!important;inset:0!important;align-items:flex-end!important}
#importOverlay .sheet{max-height:calc(100dvh - 8px)!important;height:auto!important;min-height:0!important;overflow:hidden!important}
#importOverlay .sheet-body{flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;padding-bottom:16px!important}
#importOverlay .sheet-foot{flex:0 0 auto!important;position:sticky!important;bottom:0!important;background:var(--paper)!important;z-index:3!important}

/* Old separate PDF panel and old Reading Appearance panel are not used from the reader toolbar. */
#pdfModePanel{display:none!important}
</style>
'''
head=h.find('</head>')
assert head>0
h=h[:head]+css+'\n'+h[head:]

js=r'''
<script id="v044-approved-prototype-shell-js">
(function(){
  function esc(v){return String(v==null?'':v).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function active(cls,val){return cls===val?' active':''}
  function markActive(group,val){
    document.querySelectorAll(group+' [data-v44]').forEach(function(b){b.classList.toggle('active',b.dataset.v44===String(val))})
  }

  window.v44PdfDisplay=function(mode){
    if(!window.pdfState)return;
    setPdfViewMode(mode);
    markActive('#v44PdfDisplay',mode);
  };
  window.v44PdfZoom=function(delta){
    if(!window.pdfState)return;
    if(!Number.isFinite(pdfState.zoom))pdfState.zoom=Number(localStorage.getItem('pdfZoom_v2')||1);
    pdfState.zoom=Math.max(.65,Math.min(2.4,pdfState.zoom+Number(delta||0)));
    localStorage.setItem('pdfZoom_v2',String(pdfState.zoom));
    var z=document.getElementById('v44PdfZoomValue');if(z)z.textContent=Math.round(pdfState.zoom*100)+'%';
    renderPdfPage();
  };
  window.v44PdfCrop=function(mode){
    if(!window.pdfState)return;
    if(!pdfState.cropMode)pdfState.cropMode='auto';
    pdfState.cropMode=mode;localStorage.setItem('pdfCropMode_v2',mode);
    if(mode==='none')setPdfViewMode('page');else setPdfViewMode('crop');
    markActive('#v44PdfCrop',mode);
  };
  window.v44PdfBlank=function(v){
    if(!window.pdfState)return;
    pdfState.margin=Math.max(0,Math.min(48,Number(v)||0));
    localStorage.setItem('pdfMargin_v2',String(pdfState.margin));
    var x=document.getElementById('v44PdfBlankVal');if(x)x.textContent=String(pdfState.margin);
    renderPdfPage();
  };
  window.v44PdfRotate=function(){
    if(!window.pdfState)return;
    pdfState.rotation=((Number(pdfState.rotation||0)+90)%360);
    localStorage.setItem('pdfRotation_v2',String(pdfState.rotation));
    renderPdfPage();
  };

  window.v44EpubSize=function(v){setReaderFontSize(v)};
  window.v44EpubLine=function(v){setReaderLineValue(v)};
  window.v44EpubMargin=function(v){setReaderMarginValue(v)};
  window.v44EpubBrightness=function(v){setReaderBrightness(v)};
  window.v44EpubStrength=function(v){setTextStrength(v)};
  window.v44Theme=function(v){
    var fake=document.createElement('button');fake.dataset.v=v;setTheme(fake);
    markActive('#v44Themes',v);
  };

  function pdfFormat(){
    var view=(pdfState&&pdfState.viewMode)||localStorage.getItem('pdfViewMode_v1')||'page';
    var crop=(pdfState&&pdfState.cropMode)||localStorage.getItem('pdfCropMode_v2')||'auto';
    var zoom=Math.round(((pdfState&&pdfState.zoom)||Number(localStorage.getItem('pdfZoom_v2')||1))*100);
    var blank=(pdfState&&Number(pdfState.margin))||Number(localStorage.getItem('pdfMargin_v2')||0);
    return '<div class="v44-format-row"><div class="v44-format-label">Page display</div>'+
      '<div class="v44-option-grid" id="v44PdfDisplay">'+
      '<button class="v44-square-opt'+active(view,'page')+'" data-v44="page" onclick="v44PdfDisplay(\'page\')"><span class="ico">▤</span><span>Single</span></button>'+
      '<button class="v44-square-opt'+active(view,'scroll')+'" data-v44="scroll" onclick="v44PdfDisplay(\'scroll\')"><span class="ico">▥</span><span>Continuous</span></button>'+
      '<button class="v44-square-opt'+active(view,'width')+'" data-v44="width" onclick="v44PdfDisplay(\'width\')"><span class="ico">↔</span><span>Fit width</span></button>'+
      '<button class="v44-square-opt'+active(view,'crop')+'" data-v44="crop" onclick="v44PdfDisplay(\'crop\')"><span class="ico">⌗</span><span>Auto fit</span></button>'+
      '</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Zoom</div><div class="v44-zoom-row"><button class="v44-zoom-btn" onclick="v44PdfZoom(-.1)">−</button><span class="v44-zoom-value" id="v44PdfZoomValue">'+zoom+'%</span><button class="v44-zoom-btn" onclick="v44PdfZoom(.1)">＋</button></div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Crop</div><div class="v44-option-grid crop5" id="v44PdfCrop">'+
      '<button class="v44-square-opt'+active(crop,'none')+'" data-v44="none" onclick="v44PdfCrop(\'none\')"><span class="ico">□</span><span>None</span></button>'+
      '<button class="v44-square-opt'+active(crop,'tb')+'" data-v44="tb" onclick="v44PdfCrop(\'tb\')"><span class="ico">↕</span><span>Top/Bottom</span></button>'+
      '<button class="v44-square-opt'+active(crop,'lr')+'" data-v44="lr" onclick="v44PdfCrop(\'lr\')"><span class="ico">↔</span><span>Left/Right</span></button>'+
      '<button class="v44-square-opt'+active(crop,'auto')+'" data-v44="auto" onclick="v44PdfCrop(\'auto\')"><span class="ico">⌗</span><span>Auto</span></button>'+
      '<button class="v44-square-opt'+active(crop,'manual')+'" data-v44="manual" onclick="v44PdfCrop(\'manual\')"><span class="ico">✥</span><span>Manual</span></button>'+
      '</div><div class="v44-note">Auto trims blank margins but preserves a safety edge around page content.</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Leave blank space</div><input class="v44-range" type="range" min="0" max="48" step="2" value="'+blank+'" oninput="v44PdfBlank(this.value)"><div class="v44-note">Current: <b id="v44PdfBlankVal">'+blank+'</b> px</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Rotation</div><button class="v44-square-opt" onclick="v44PdfRotate()"><span class="ico">↻</span><span>Rotate 90°</span></button></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Text</div><div class="v44-note">Long-press text in normal PDFs to select, copy, highlight or add a note. Scanned pages can use OCR from Navigate.</div></div>';
  }

  function epubFormat(){
    var font=Number(settings.font||20),line=Number(settings.line||1.72),margin=Number(settings.margin||28),bright=Number(settings.brightness||55),strength=Number(settings.textStrength||22),theme=settings.theme||'paper';
    return '<div class="v44-format-row"><div class="v44-format-label">Font</div><div class="v44-note">'+esc(settings.fontFamily||'Literata')+'</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Text size</div><input class="v44-range" type="range" min="14" max="34" step="1" value="'+font+'" oninput="v44EpubSize(this.value)"></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Line spacing</div><input class="v44-range" type="range" min="1.3" max="2.1" step=".05" value="'+line+'" oninput="v44EpubLine(this.value)"></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Margins</div><input class="v44-range" type="range" min="12" max="48" step="2" value="'+margin+'" oninput="v44EpubMargin(this.value)"></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Theme</div><div class="v44-theme-grid" id="v44Themes">'+
      '<button class="v44-theme'+active(theme,'paper')+'" data-v44="paper" onclick="v44Theme(\'paper\')"><i style="background:#f2f0ea"></i><span>Paper</span></button>'+
      '<button class="v44-theme'+active(theme,'warm')+'" data-v44="warm" onclick="v44Theme(\'warm\')"><i style="background:#efe1ca"></i><span>Warm</span></button>'+
      '<button class="v44-theme'+active(theme,'amber')+'" data-v44="amber" onclick="v44Theme(\'amber\')"><i style="background:#e7cca2"></i><span>Amber</span></button>'+
      '<button class="v44-theme'+active(theme,'eink')+'" data-v44="eink" onclick="v44Theme(\'eink\')"><i style="background:#e5e5e0"></i><span>E-ink</span></button>'+
      '<button class="v44-theme'+active(theme,'night')+'" data-v44="night" onclick="v44Theme(\'night\')"><i style="background:#171714"></i><span>Night</span></button>'+
      '</div></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Brightness</div><input class="v44-range" type="range" min="0" max="100" step="1" value="'+bright+'" oninput="v44EpubBrightness(this.value)"></div>'+
      '<div class="v44-format-row"><div class="v44-format-label">Text strength</div><input class="v44-range" type="range" min="0" max="100" step="1" value="'+strength+'" oninput="v44EpubStrength(this.value)"></div>';
  }

  window.vnextOpenFormat=function(){
    vnextCloseSheet();
    openSheet('Format',currentBook&&currentBook.ext==='pdf'?pdfFormat():epubFormat());
  };

  var oldNavigate=window.vnextOpenNavigate;
  window.vnextOpenNavigate=function(){
    if(currentBook&&currentBook.ext==='pdf'){
      var html='<div class="v44-format-row"><div class="v44-format-label">Go to page</div><div class="vnext-go-row"><input id="vnextGoInput" type="number" min="1" max="'+pdfState.count+'" value="'+(pdfState.page+1)+'" inputmode="numeric"><button onclick="vnextGoPage()">Go</button></div></div>'+
        '<div class="v44-format-row"><div class="v44-format-label">PDF text</div><button class="v44-square-opt" onclick="vnextCloseSheet();showToast(\'Long-press text to select/copy\')"><span class="ico">Aa</span><span>Select text</span></button></div>';
      openSheet('Navigate',html);
    }else oldNavigate();
  };

  function aliasReader(){
    var r=document.getElementById('reader');if(r)r.classList.add('reader-screen');
    var head=r&&r.querySelector('.reader-head');if(head)head.classList.add('reader-top');
    var page=r&&r.querySelector('.reader-page');if(page)page.classList.add('reader-body');
    var prog=r&&r.querySelector('.vnext-progress-pill');if(prog)prog.classList.add('reader-progress');
    var tools=r&&r.querySelector('.vnext-reader-tools');if(tools){tools.classList.add('reader-tools');tools.querySelectorAll('button').forEach(function(b){b.classList.add('tool')})}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',aliasReader);else aliasReader();
})();
</script>
'''
body=h.rfind('</body>')
assert body>0
h=h[:body]+js+'\n'+h[body:]

# Smaller base APK: unbundled OCR, ARM64 only.
gpath=Path('app/build.gradle')
g=gpath.read_text(encoding='utf-8')
g=g.replace("implementation 'com.google.mlkit:text-recognition:16.0.1'","implementation 'com.google.android.gms:play-services-mlkit-text-recognition:19.0.1'")
if "abiFilters 'arm64-v8a'" not in g:
    g=g.replace("targetSdk 34","targetSdk 34\n        ndk { abiFilters 'arm64-v8a' }",1)
g=re.sub(r'versionCode\s+\d+','versionCode 39',g,count=1)
g=re.sub(r"versionName\s+['\"][^'\"]+['\"]","versionName '0.4.4-approved-v8'",g,count=1)
gpath.write_text(g,encoding='utf-8')

# Final guards.
assert 'id="v044-approved-prototype-shell"' in h
assert 'id="v044-approved-prototype-shell-js"' in h
assert 'window.vnextOpenFormat=function()' in h
assert 'Page display' in h and 'Leave blank space' in h
assert '#readerFooter .vnext-reader-tools' in h
assert '#settings .settings-scroll' in h and 'padding:0 20px 26px!important' in h
assert "play-services-mlkit-text-recognition:19.0.1" in g
assert "abiFilters 'arm64-v8a'" in g
p.write_text(h,encoding='utf-8')
print('v0.4.4 approved prototype shell applied')
