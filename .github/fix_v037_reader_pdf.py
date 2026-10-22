from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')

style = r'''
<style id="v037-reader-fix">
/* Backdrop must not block the reader when closed. */
#vnextSheetBackdrop{display:none!important;pointer-events:none!important}
#vnextSheetBackdrop.show{display:flex!important;pointer-events:auto!important}

/* PDF gets its own true full-screen viewport. Controls float over it. */
#reader.pdf-mode{position:relative!important;height:100dvh!important;overflow:hidden!important;background:#d9d9d5!important}
#reader.pdf-mode .pdf-wrap{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;padding:0!important;margin:0!important;background:#d9d9d5!important;overflow:auto!important;align-items:center!important;justify-content:flex-start!important}
#reader.pdf-mode .pdf-wrap.active{display:flex!important}
#reader.pdf-mode .pdf-page-surface{flex:0 0 auto!important;margin:auto!important;box-shadow:none!important}
#reader.pdf-mode .reader-head{position:absolute!important;left:0!important;right:0!important;top:0!important;z-index:45!important}
#reader.pdf-mode #readerFooter .vnext-progress-pill{z-index:43!important}
#reader.pdf-mode #readerFooter .vnext-reader-tools{z-index:44!important}
#reader.pdf-mode.chrome-hidden .reader-head,
#reader.pdf-mode.chrome-hidden #readerFooter .vnext-progress-pill,
#reader.pdf-mode.chrome-hidden #readerFooter .vnext-reader-tools{opacity:0!important;visibility:hidden!important;pointer-events:none!important}
</style>
'''
h=h.replace('</head>',style+'\n</head>',1)

# Default PDF mode should behave like an e-reader: crop margins first.
h=h.replace("viewMode:localStorage.getItem('pdfViewMode_v1')||'width'",
            "viewMode:localStorage.getItem('pdfViewMode_v1')||'crop'")
h=h.replace("localStorage.getItem('pdfViewMode_v1')||'width'",
            "localStorage.getItem('pdfViewMode_v1')||'crop'")

# Make page-mode/crop sizing use the whole available viewport.
old="let scale=ww/base.width;if(pdfState.viewMode==='page')scale=Math.min(ww/base.width,wh/base.height);"
new="let scale=ww/base.width;if(pdfState.viewMode==='page')scale=Math.min(ww/base.width,wh/base.height);if(pdfState.viewMode==='crop')scale=Math.max(ww/base.width,Math.min(wh/base.height,ww/base.width*1.35));"
if old in h:
    h=h.replace(old,new,1)

# Ensure opening/closing the custom sheet never leaves an invisible click shield.
h=h.replace("window.vnextCloseSheet=function(){document.getElementById('vnextSheetBackdrop')?.classList.remove('show');",
            "window.vnextCloseSheet=function(){const __b=document.getElementById('vnextSheetBackdrop');if(__b){__b.classList.remove('show');__b.style.display='none'};")
h=h.replace("document.getElementById('vnextSheetBackdrop').classList.add('show');setReaderChromeVisible(true)",
            "const __b=document.getElementById('vnextSheetBackdrop');__b.style.display='flex';__b.classList.add('show');setReaderChromeVisible(true)")

assert '#vnextSheetBackdrop{display:none!important' in h
assert "viewMode:localStorage.getItem('pdfViewMode_v1')||'crop'" in h
assert "if(pdfState.viewMode==='crop')scale=Math.max" in h

p.write_text(h,encoding='utf-8')
print('v0.3.7 reader/PDF interaction fix applied')
