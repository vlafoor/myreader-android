from pathlib import Path
import re

p=Path('app/src/main/assets/index.html')
h=p.read_text(encoding='utf-8')

css=r'''
<style id="v046-library-recovery">
/* Library is isolated from reader layout patches. */
#library.screen{
  display:none;position:absolute!important;inset:0!important;
  flex-direction:column!important;background:var(--paper)!important;
  overflow:hidden!important;padding:0!important
}
#library.screen.active{display:flex!important}
#library>.topbar{
  position:relative!important;inset:auto!important;display:flex!important;
  flex:0 0 auto!important;visibility:visible!important;opacity:1!important;
  padding:16px 20px 12px!important;background:var(--paper)!important
}
#library>.searchbox{
  display:flex!important;visibility:visible!important;opacity:1!important;
  flex:0 0 auto!important;min-height:52px!important;margin:0 20px 12px!important;
  border:1px solid var(--line)!important;background:var(--card)!important
}
#library>.chips{
  display:flex!important;visibility:visible!important;opacity:1!important;
  flex:0 0 auto!important;min-height:48px!important;padding:0 20px 12px!important
}
#library>.chips .chip{display:block!important;visibility:visible!important;opacity:1!important}
#libraryScroll{
  display:block!important;visibility:visible!important;opacity:1!important;
  flex:1 1 auto!important;min-height:0!important;height:auto!important;
  overflow-y:auto!important;overflow-x:hidden!important;padding:0 20px 28px!important;
  position:relative!important
}
#libraryScroll .section-label{
  display:block!important;visibility:visible!important;opacity:1!important;color:var(--muted)!important
}
#continueSection{visibility:visible!important;opacity:1!important}
#continueCard,.continue-card,.continue-info,.continue-info h3,.continue-info p{
  visibility:visible!important;opacity:1!important
}
#bookGrid.book-grid{
  display:grid!important;visibility:visible!important;opacity:1!important;
  grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:18px 14px!important;padding-bottom:24px!important
}
#bookGrid .book-card{
  display:block!important;position:relative!important;min-width:0!important;
  visibility:visible!important;opacity:1!important;color:var(--ink)!important
}
#bookGrid .cover-wrap{
  display:block!important;position:relative!important;width:100%!important;
  height:calc((100vw - 68px)/3 * 1.5)!important;
  min-height:120px!important;max-height:290px!important;
  border-radius:10px!important;overflow:hidden!important;
  background:linear-gradient(145deg,#9f8f78,#554c40)!important;
  box-shadow:0 5px 14px rgba(0,0,0,.10)!important;
  visibility:visible!important;opacity:1!important
}
#bookGrid .cover-wrap>img{
  display:block!important;position:absolute!important;inset:0!important;
  width:100%!important;height:100%!important;object-fit:cover!important;
  visibility:visible!important;opacity:1!important
}
#bookGrid .cover-placeholder{
  display:flex!important;position:absolute!important;inset:0!important;
  align-items:center!important;justify-content:center!important;text-align:center!important;
  padding:10px!important;color:#fff!important;visibility:visible!important;opacity:1!important
}
#bookGrid .book-name{
  display:-webkit-box!important;visibility:visible!important;opacity:1!important;
  color:var(--ink)!important;font:700 14px/1.22 Georgia,serif!important;
  margin-top:8px!important;-webkit-line-clamp:3!important;-webkit-box-orient:vertical!important;
  overflow:hidden!important;min-height:17px!important
}
#bookGrid .book-author{
  display:block!important;visibility:visible!important;opacity:1!important;
  color:var(--muted)!important;font-size:11px!important;margin-top:4px!important;
  white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important
}
#bookGrid .book-progress{
  display:block!important;visibility:visible!important;opacity:1!important;
  height:3px!important;background:#e7dfd1!important;border-radius:99px!important;margin-top:7px!important
}
#bookGrid .book-progress>i{display:block!important;height:100%!important;background:var(--accent)!important}
#library>.bottomnav{
  position:relative!important;left:auto!important;right:auto!important;bottom:auto!important;
  display:flex!important;visibility:visible!important;opacity:1!important;flex:0 0 70px!important
}
@media(max-width:420px){
  #bookGrid.book-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  #bookGrid .cover-wrap{height:calc((100vw - 54px)/2 * 1.5)!important;max-height:330px!important}
}
</style>
'''
head=h.find('</head>'); assert head>0
h=h[:head]+css+'\n'+h[head:]

js=r'''
<script id="v046-library-recovery-js">
(function(){
  function fallbackCover(img){
    const wrap=img&&img.closest('.cover-wrap,.mini-cover');
    if(!wrap)return;
    const card=img.closest('.book-card');
    const title=card?.querySelector('.book-name')?.textContent||'BOOK';
    img.remove();
    if(!wrap.querySelector('.cover-placeholder')){
      const d=document.createElement('div');d.className='cover-placeholder';
      d.innerHTML=title.split(/\s+/).slice(0,5).map(escapeHtml).join('<br>');
      wrap.insertBefore(d,wrap.firstChild);
    }
  }
  window.__v046FallbackCover=fallbackCover;

  const oldRender=window.renderLibrary;
  window.renderLibrary=async function(){
    await oldRender();
    const scroll=document.getElementById('libraryScroll');
    if(scroll && !Number.isFinite(scroll.scrollTop))scroll.scrollTop=0;
    document.querySelectorAll('#bookGrid .cover-wrap img').forEach(function(img){
      img.onerror=function(){fallbackCover(img)};
      if(img.complete && (!img.naturalWidth || !img.naturalHeight))fallbackCover(img);
    });
  };
  try{renderLibrary=window.renderLibrary}catch(_){}
})();
</script>
'''
body=h.rfind('</body>'); assert body>0
h=h[:body]+js+'\n'+h[body:]

gpath=Path('app/build.gradle')
g=gpath.read_text(encoding='utf-8')
g=re.sub(r'versionCode\s+\d+','versionCode 41',g,count=1)
g=re.sub(r"versionName\s+['\"][^'\"]+['\"]","versionName '0.4.6-library-recovery'",g,count=1)
gpath.write_text(g,encoding='utf-8')

assert 'id="v046-library-recovery"' in h
assert 'id="v046-library-recovery-js"' in h
assert '#library>.searchbox' in h
assert '#bookGrid .book-name' in h
assert '__v046FallbackCover' in h
p.write_text(h,encoding='utf-8')
print('v0.4.6 library recovery applied')
