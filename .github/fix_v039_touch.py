from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')

css=r'''
<style id="v039-touch-safety">
/* Android/Bigme WebView: interactive controls must accept touch directly. */
button,.nav-btn,.tool,.chip,.iconbtn,.icon-btn,.book-card,.note-card,[role="button"]{
  pointer-events:auto!important;
  touch-action:manipulation!important;
  -webkit-user-select:none;
  user-select:none;
}
/* Hidden fullscreen layers must never steal taps. */
.overlay:not(.show),
.reader-settings-backdrop:not(.show),
#vnextSheetBackdrop:not(.show),
.vnext-sheet-backdrop:not(.show),
#pdfModePanel:not(.show){
  pointer-events:none!important;
}
#vnextSheetBackdrop:not(.show),
.vnext-sheet-backdrop:not(.show),
.reader-settings-backdrop:not(.show){
  display:none!important;
}
</style>
'''
h=h.replace('</head>',css+'\n</head>',1)

js=r'''
<script id="v039-touch-safety-js">
(function(){
  /* Same class of fix that made the earlier Android button build usable:
     convert a real touch-end into exactly one programmatic click. */
  let start=null;
  let suppressClickUntil=0;
  const SEL='button,.nav-btn,.tool,.chip,.iconbtn,.icon-btn,.book-card,.note-card,[role="button"]';

  document.addEventListener('touchstart',function(e){
    if(!e.touches||e.touches.length!==1){start=null;return}
    const t=e.touches[0], el=e.target.closest?.(SEL);
    start=el?{el,x:t.clientX,y:t.clientY,time:Date.now()}:null;
  },{capture:true,passive:true});

  document.addEventListener('touchend',function(e){
    if(!start)return;
    const s=start; start=null;
    const t=e.changedTouches&&e.changedTouches[0];
    if(!t)return;
    if(Math.abs(t.clientX-s.x)>14||Math.abs(t.clientY-s.y)>14||Date.now()-s.time>900)return;
    if(s.el.disabled)return;
    e.preventDefault();
    suppressClickUntil=Date.now()+450;
    /* Do not stop the synthetic click; existing onclick/listeners must receive it. */
    try{s.el.click()}catch(_){}
  },{capture:true,passive:false});

  /* Suppress only the browser's duplicate compatibility click after touch.
     Programmatic .click() has detail===0 and is allowed. */
  document.addEventListener('click',function(e){
    if(Date.now()<suppressClickUntil && e.detail!==0){
      e.preventDefault();
      e.stopImmediatePropagation();
    }
  },true);

  document.addEventListener('touchcancel',function(){start=null},{capture:true,passive:true});

  function clearDeadLayers(){
    document.querySelectorAll('.overlay,.reader-settings-backdrop,#vnextSheetBackdrop,.vnext-sheet-backdrop').forEach(function(el){
      if(!el.classList.contains('show')){
        el.style.pointerEvents='none';
        if(el.id==='vnextSheetBackdrop'||el.classList.contains('vnext-sheet-backdrop')||el.classList.contains('reader-settings-backdrop')){
          el.style.display='none';
        }
      }
    });
  }
  clearDeadLayers();
  window.addEventListener('pageshow',clearDeadLayers);
  document.addEventListener('visibilitychange',function(){if(!document.hidden)clearDeadLayers()});
  window.__myreaderTouchSafetyV039=true;
})();
</script>
'''
h=h.replace('</body>',js+'\n</body>',1)

assert 'id="v039-touch-safety"' in h
assert 'id="v039-touch-safety-js"' in h
assert "s.el.click()" in h
assert "touch-action:manipulation!important" in h
assert "window.__myreaderTouchSafetyV039=true" in h

p.write_text(h,encoding='utf-8')
print('v0.3.9 Android touch safety installed')
