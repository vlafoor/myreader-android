from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')
h=re.sub(r'\n?<style id="vnext-viewport-fix">.*?</style>\n?', '\n', h, count=1, flags=re.S)

css=r'''
<style id="v046-library-repair">
#library{position:absolute!important;inset:0!important;display:none;flex-direction:column!important;overflow:hidden!important;background:var(--paper)!important}
#library.active{display:flex!important}
#library>.topbar{position:relative!important;z-index:8!important;display:flex!important;flex:0 0 auto!important;padding:16px 20px 12px!important;background:var(--paper)!important}
#library>.searchbox{position:relative!important;z-index:8!important;display:flex!important;visibility:visible!important;opacity:1!important;flex:0 0 auto!important;margin:0 20px 12px!important;min-height:50px!important}
#library>.chips{position:relative!important;z-index:8!important;display:flex!important;visibility:visible!important;opacity:1!important;flex:0 0 auto!important;min-height:48px!important;padding:0 20px 12px!important}
#library>.scroll{position:relative!important;z-index:6!important;display:block!important;visibility:visible!important;opacity:1!important;flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;padding:0 20px 28px!important;background:var(--paper)!important}
#library .section-label{display:block!important;visibility:visible!important;opacity:1!important}
#library #continueSection{position:relative!important;z-index:7!important}
#library .continue-card{position:relative!important;z-index:7!important;display:flex!important;visibility:visible!important;opacity:1!important;min-height:132px!important}
#library .book-grid{position:relative!important;z-index:7!important;display:grid!important;visibility:visible!important;opacity:1!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:18px 14px!important;padding-bottom:24px!important}
#library .book-card{position:relative!important;display:block!important;visibility:visible!important;opacity:1!important;min-width:0!important;color:var(--ink)!important;overflow:visible!important}
#library .cover-wrap{position:relative!important;display:block!important;visibility:visible!important;opacity:1!important;width:100%!important;height:auto!important;min-height:150px!important;aspect-ratio:2/3!important;border-radius:10px!important;overflow:hidden!important;background:linear-gradient(145deg,#9f8f78,#554c40)!important}
@supports not (aspect-ratio: 2 / 3){#library .cover-wrap{height:190px!important}}
#library .cover-wrap img,#library .cover-placeholder{display:block!important;visibility:visible!important;opacity:1!important;width:100%!important;height:100%!important}
#library .cover-placeholder{display:flex!important}
#library .book-name{display:-webkit-box!important;visibility:visible!important;opacity:1!important;color:var(--ink)!important;margin-top:8px!important;min-height:17px!important}
#library .book-author{display:block!important;visibility:visible!important;opacity:1!important;color:var(--muted)!important;min-height:14px!important}
#library .book-progress{display:block!important;visibility:visible!important;opacity:1!important}
#library .vnext-cover-progress,#library .vnext-cover-format{z-index:9!important}
@media(max-width:430px){#library .book-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:18px 14px!important}#library .cover-wrap{min-height:210px!important}}
@media(max-width:360px){#library>.searchbox{margin-left:14px!important;margin-right:14px!important}#library>.chips{padding-left:14px!important;padding-right:14px!important}#library>.scroll{padding-left:14px!important;padding-right:14px!important}#library .cover-wrap{min-height:180px!important}}
</style>
'''
head=h.find('</head>')
assert head>0
h=h[:head]+css+'\n'+h[head:]

js=r'''
<script id="v046-library-repair-js">
(function(){
  window.v046RepairLibrary=function(){
    const lib=document.getElementById('library');if(!lib)return;
    const sb=document.getElementById('vnextSheetBackdrop');if(sb){sb.classList.remove('show');sb.style.display='none';sb.style.pointerEvents='none'}
    document.getElementById('importOverlay')?.classList.remove('show');
    document.getElementById('bookActionOverlay')?.classList.remove('show');
    document.getElementById('collectionPickerOverlay')?.classList.remove('show');
    document.querySelectorAll('.book-menu-backdrop,.book-menu').forEach(x=>x.classList.remove('show'));
    [lib.querySelector('.searchbox'),lib.querySelector('.chips'),lib.querySelector('.scroll')].forEach(x=>{if(x){x.style.display='';x.style.visibility='';x.style.opacity=''}});
  };
  const oldOpen=window.openScreen;
  window.openScreen=function(id){
    const r=oldOpen.apply(this,arguments);
    if(id==='library'){v046RepairLibrary();setTimeout(()=>{v046RepairLibrary();renderLibrary?.()},0)}
    return r;
  };
  const oldRender=window.renderLibrary;
  if(typeof oldRender==='function'){
    window.renderLibrary=async function(){
      v046RepairLibrary();
      const r=await oldRender.apply(this,arguments);
      const grid=document.getElementById('bookGrid');
      if(grid)grid.querySelectorAll('.book-card').forEach(card=>{
        card.style.display='block';card.style.visibility='visible';card.style.opacity='1';
        const cover=card.querySelector('.cover-wrap');
        if(cover && cover.getBoundingClientRect().height<40)cover.style.height='190px';
      });
      return r;
    };
    try{renderLibrary=window.renderLibrary}catch(_){}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',v046RepairLibrary);else v046RepairLibrary();
})();
</script>
'''
body=h.rfind('</body>')
assert body>0
h=h[:body]+js+'\n'+h[body:]

gpath=Path('app/build.gradle')
g=gpath.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 41',g,count=1)
g=re.sub(r"versionName\s+['\"][^'\"]+['\"]","versionName '0.4.6-library-repair'",g,count=1)
gpath.write_text(g,encoding='utf-8')

assert 'vnext-viewport-fix' not in h
assert 'id="v046-library-repair"' in h
assert 'id="v046-library-repair-js"' in h
assert "#library>.searchbox" in h
assert "#library .cover-wrap" in h
p.write_text(h,encoding='utf-8')
print('v0.4.6 library repair applied')
