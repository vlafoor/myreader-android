from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')

style=r'''
<style id="v038-reader-stability">
/* Header: reserve real space for back + time/battery, title never overlaps them. */
#reader .reader-head{
  display:grid!important;
  grid-template-columns:minmax(138px,auto) minmax(0,1fr) 12px!important;
  align-items:center!important;
  column-gap:8px!important;
  padding:7px 10px!important;
}
#reader .reader-head-left{
  position:static!important;
  left:auto!important;top:auto!important;
  width:auto!important;min-width:0!important;
  height:40px!important;
  display:flex!important;align-items:center!important;gap:7px!important;
  overflow:visible!important;
}
#readerBookTitle{
  width:auto!important;max-width:none!important;min-width:0!important;
  justify-self:stretch!important;text-align:center!important;
  padding:0 4px!important;
}
#readerDeviceInfo{font-size:8px!important;display:flex!important;gap:4px!important}

/* EPUB viewport height is identical with chrome shown or hidden. */
#reader:not(.pdf-mode) .reader-head{
  height:55px!important;min-height:55px!important;max-height:55px!important;
  flex:0 0 55px!important;
}
#reader:not(.pdf-mode).chrome-hidden .reader-head{
  height:55px!important;min-height:55px!important;max-height:55px!important;
  flex:0 0 55px!important;
  padding:7px 10px!important;
}
#reader:not(.pdf-mode) .reader-page,
#reader:not(.pdf-mode).chrome-hidden .reader-page{
  flex:1 1 auto!important;min-height:0!important;
  padding-top:22px!important;padding-bottom:28px!important;
}

/* PDF Fit Page: whole physical page must remain visible, never clipped. */
#reader.pdf-mode .pdf-wrap{
  overflow:auto!important;
  padding:0!important;
  align-items:center!important;
  justify-content:center!important;
}
#reader.pdf-mode .pdf-page-surface{
  transform:none!important;
  transform-origin:center center!important;
  margin:auto!important;
  max-width:100%!important;
}
</style>
'''
h=h.replace('</head>',style+'\n</head>',1)

# One-time migration: old crop preference must not survive this fix.
marker="window.__v038PdfModeMigration"
script=r'''
<script id="v038-reader-fix-js">
window.__v038PdfModeMigration=true;
try{
  if(localStorage.getItem('pdfViewModeMigration_v038')!=='1'){
    localStorage.setItem('pdfViewMode_v1','page');
    localStorage.setItem('pdfViewModeMigration_v038','1');
  }
}catch(e){}

/* Never let auto crop physically zoom the page beyond the viewport. */
window.v038SafePdfSurface=function(surface){
  if(!surface)return;
  surface.style.transform='none';
  surface.style.marginBottom='0px';
  surface.style.clipPath='none';
};
</script>
'''
h=h.replace('</body>',script+'\n</body>',1)

# PDF state default and any fallback default now Fit Page.
h=h.replace("viewMode:localStorage.getItem('pdfViewMode_v1')||'crop'",
            "viewMode:localStorage.getItem('pdfViewMode_v1')||'page'")
h=h.replace("localStorage.getItem('pdfViewMode_v1')||'crop'",
            "localStorage.getItem('pdfViewMode_v1')||'page'")

# Fit page is always a contain calculation. Crop mode no longer pre-zooms before detection.
old="let scale=ww/base.width;if(pdfState.viewMode==='page')scale=Math.min(ww/base.width,wh/base.height);if(pdfState.viewMode==='crop')scale=Math.max(ww/base.width,Math.min(wh/base.height,ww/base.width*1.35));"
new="let scale=ww/base.width;if(pdfState.viewMode==='page'||pdfState.viewMode==='crop')scale=Math.min(ww/base.width,wh/base.height);"
if old not in h:
    raise SystemExit('PDF scale block not found')
h=h.replace(old,new,1)

# Auto crop detector may analyze margins, but must not enlarge/cut the rendered page.
start=h.find('function applyAutoCropToPdfSurface(canvas,surface){')
end=h.find('\n\nfunction toggleReaderNav',start)
if start<0 or end<0:
    raise SystemExit('auto crop function not found')
safe_func="""function applyAutoCropToPdfSurface(canvas,surface){
  /* v0.3.8 safety: preserve the full rendered page. Margin detection can return later
     as a non-destructive viewport option, but must never crop content by scaling. */
  if(!surface)return;
  surface.style.transform='none';
  surface.style.transformOrigin='center center';
  surface.style.marginBottom='0px';
  surface.style.clipPath='none';
}"""
h=h[:start]+safe_func+h[end:]

# Reader tap logic: controls-visible tap only hides controls; it cannot turn a page.
old_click="const r=rp.getBoundingClientRect(),x=e.clientX-r.left;if(x>r.width*.70)nextTextPage();else if(x<r.width*.30)prevTextPage();else toggleReaderChrome()"
new_click="const reader=document.getElementById('reader');if(reader&&!reader.classList.contains('chrome-hidden')){setReaderChromeVisible(false);return}const r=rp.getBoundingClientRect(),x=e.clientX-r.left;if(x>r.width*.80)nextTextPage();else if(x<r.width*.20)prevTextPage();else setReaderChromeVisible(true)"
if old_click not in h:
    raise SystemExit('reader click block not found')
h=h.replace(old_click,new_click,1)

assert 'id="v038-reader-stability"' in h
assert "pdfViewModeMigration_v038" in h
assert "viewMode:localStorage.getItem('pdfViewMode_v1')||'page'" in h
assert "if(pdfState.viewMode==='page'||pdfState.viewMode==='crop')scale=Math.min" in h
assert "if(reader&&!reader.classList.contains('chrome-hidden')){setReaderChromeVisible(false);return}" in h
assert "x>r.width*.80" in h and "x<r.width*.20" in h

p.write_text(h,encoding='utf-8')
print('v0.3.8 stable viewport, header, and PDF fit applied')
