from pathlib import Path
import re
root=Path('.')
htmlp=root/'app/src/main/assets/index.html'
javap=root/'app/src/main/java/com/myreader/app/MainActivity.java'
gradlep=root/'app/build.gradle'
s=htmlp.read_text()

s=s.replace('--reader-font:20px; --reader-line:1.72; --reader-margin:28px;', '--reader-font:20px; --reader-line:1.72; --reader-margin:28px; --reader-weight:430;')
insert_after="html[data-theme=eink]{--bg:#e8e5da;--paper:#efede4;--card:#f3f1e9;--ink:#252522;--muted:#6d6b63;--line:#cfccc1;--accent:#56544c;--shadow:0 8px 22px rgba(0,0,0,.06)}"
if 'data-theme=ivory' not in s:
    s=s.replace(insert_after, insert_after+"\nhtml[data-theme=ivory]{--bg:#f1eee4;--paper:#f8f4e9;--card:#fcf8ee;--ink:#282621;--muted:#716d65;--line:#d9d4c8;--accent:#635c50;--shadow:0 8px 22px rgba(40,35,25,.06)}\nhtml[data-theme=stone]{--bg:#deded8;--paper:#e8e7e0;--card:#eeede7;--ink:#242421;--muted:#676760;--line:#c6c5bd;--accent:#55544e;--shadow:0 6px 18px rgba(0,0,0,.05)}\nhtml[data-theme=sepia]{--bg:#e6d7bd;--paper:#eddcc1;--card:#f3e4ca;--ink:#30271f;--muted:#756655;--line:#cfba9b;--accent:#70573f;--shadow:0 8px 22px rgba(75,48,20,.07)}")
s=s.replace('color:var(--reader-ink,#2b2925);background:var(--reader-bg,#f7f1e5);user-select:text;', 'color:var(--reader-ink,#2b2925);background:var(--reader-bg,#f7f1e5);font-weight:var(--reader-weight,430);text-rendering:optimizeLegibility;-webkit-font-smoothing:antialiased;user-select:text;')
footer_rule='.reader-footer{flex:0 0 46px;padding:8px 16px 13px;display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;gap:10px;font-size:11px;color:var(--muted);background:var(--reader-bg,#f7f1e5)}'
if '.reader-dimmer{' not in s:
    s=s.replace(footer_rule, footer_rule+"\n.reader-dimmer{position:absolute;inset:0;z-index:15;pointer-events:none;background:#000;opacity:0;transition:opacity .05s linear}.reader-gesture-hud{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:80;display:none;min-width:132px;text-align:center;padding:12px 16px;border-radius:16px;background:rgba(25,25,23,.88);color:#fff;font-size:13px;font-weight:750;box-shadow:0 10px 30px rgba(0,0,0,.28)}.reader-gesture-hud.show{display:block}")
needle="html[data-theme=night] .reader-page,html[data-theme=night] .reader-head,html[data-theme=night] .reader-footer,html[data-theme=night] .pdf-wrap{--reader-bg:#171714;--reader-ink:#eee9df}"
if 'html[data-theme=ivory] #reader' not in s:
    s=s.replace(needle, needle+"\nhtml[data-theme=ivory] #reader,html[data-theme=ivory] .reader-page,html[data-theme=ivory] .reader-head,html[data-theme=ivory] .reader-footer{--reader-bg:#f8f4e9;--reader-ink:#282621}\nhtml[data-theme=stone] #reader,html[data-theme=stone] .reader-page,html[data-theme=stone] .reader-head,html[data-theme=stone] .reader-footer{--reader-bg:#e8e7e0;--reader-ink:#242421}\nhtml[data-theme=sepia] #reader,html[data-theme=sepia] .reader-page,html[data-theme=sepia] .reader-head,html[data-theme=sepia] .reader-footer{--reader-bg:#eddcc1;--reader-ink:#30271f}")
s=s.replace('id="settingsBrightnessRange" type="range" min="5" max="100"', 'id="settingsBrightnessRange" type="range" min="1" max="100"')
s=s.replace('id="readerBrightnessRange" type="range" min="5" max="100"', 'id="readerBrightnessRange" type="range" min="1" max="100"')
old='<button data-v="paper" onclick="setTheme(this)">Paper</button><button data-v="warm" onclick="setTheme(this)">Warm</button><button data-v="amber" onclick="setTheme(this)">Amber</button><button data-v="eink" onclick="setTheme(this)">E-ink</button><button data-v="white" onclick="setTheme(this)">White</button><button data-v="night" onclick="setTheme(this)">Night</button>'
new='<button data-v="paper" onclick="setTheme(this)">Paper</button><button data-v="ivory" onclick="setTheme(this)">Ivory</button><button data-v="warm" onclick="setTheme(this)">Warm</button><button data-v="sepia" onclick="setTheme(this)">Sepia</button><button data-v="amber" onclick="setTheme(this)">Amber</button><button data-v="stone" onclick="setTheme(this)">Stone</button><button data-v="eink" onclick="setTheme(this)">E-ink</button><button data-v="white" onclick="setTheme(this)">White</button><button data-v="night" onclick="setTheme(this)">Night</button>'
s=s.replace(old,new)

brightness_block='<div class="setting-inline" style="display:block"><span>Brightness</span><div class="brightness-row"><span>☾</span><input id="readerBrightnessRange" type="range" min="1" max="100" step="1" oninput="setReaderBrightness(this.value)"><span>☀</span><span id="readerBrightnessValue" class="brightness-value">100%</span></div></div>'
if 'readerClarityRange' not in s:
    s=s.replace(brightness_block, brightness_block+'<div class="setting-inline" style="display:block"><span>Text clarity</span><div class="brightness-row"><span>Aa</span><input id="readerClarityRange" type="range" min="0" max="100" step="1" oninput="setTextClarity(this.value)"><span><b>Aa</b></span><span id="readerClarityValue" class="brightness-value">30%</span></div></div>')
if 'id="readerDimmer"' not in s:
    s=s.replace('<div id="readerFooter" class="reader-footer"><span id="readerLocation"></span><span id="readerDeviceInfo"></span><span id="readerProgress"></span></div>', '<div id="readerFooter" class="reader-footer"><span id="readerLocation"></span><span id="readerDeviceInfo"></span><span id="readerProgress"></span></div><div id="readerDimmer" class="reader-dimmer"></div><div id="readerGestureHud" class="reader-gesture-hud"></div>')
s=s.replace("document.getElementById('readerFooter').style.display='flex'", "document.getElementById('readerFooter').style.display='grid'")

pat=re.compile(r"function loadSettings\(\)\{.*?function syncSettingsUI\(\)\{.*?\}\nasync function resetLibrary", re.S)
m=pat.search(s)
if not m: raise SystemExit('settings block not found')
newblock=r'''function loadSettings(){
  let old={};try{old=JSON.parse(localStorage.getItem('readerSettings_v4')||'{}')}catch(e){}
  let fresh={};try{fresh=JSON.parse(localStorage.getItem('readerSettings_v5')||'{}')}catch(e){}
  const migrated=!localStorage.getItem('readerSettings_v5');
  settings={font:fresh.font||old.font||20,line:fresh.line||old.line||1.72,margin:fresh.margin||old.margin||28,theme:fresh.theme||old.theme||'ivory',awake:!!(fresh.awake??old.awake),brightness:migrated?42:Math.max(1,Math.min(100,Number(fresh.brightness||42))),clarity:migrated?28:Math.max(0,Math.min(100,Number(fresh.clarity??28)))};
  localStorage.setItem('readerSettings_v5',JSON.stringify(settings));applyReaderSettings()
}
function saveSettings(){localStorage.setItem('readerSettings_v5',JSON.stringify(settings));applyReaderSettings();syncSettingsUI()}
function applyReaderSettings(){const oldCount=Math.max(1,textPageState.count||1),oldPage=Math.max(0,textPageState.page||0),oldFrac=oldCount>1?oldPage/(oldCount-1):0;document.documentElement.style.setProperty('--reader-font',settings.font+'px');document.documentElement.style.setProperty('--reader-line',String(settings.line));document.documentElement.style.setProperty('--reader-margin',settings.margin+'px');document.documentElement.style.setProperty('--reader-weight',String(Math.round(400+settings.clarity*2.2)));document.documentElement.dataset.theme=settings.theme;const r=document.getElementById('reader'),themes={paper:['#f7f1e5','#2b2925'],ivory:['#f8f4e9','#282621'],warm:['#f5ead5','#2c2821'],sepia:['#eddcc1','#30271f'],amber:['#f0ddbd','#30271f'],stone:['#e8e7e0','#242421'],eink:['#efede4','#252522'],white:['#ffffff','#202020'],night:['#171714','#eee9df']},pair=themes[settings.theme]||themes.ivory;r.style.setProperty('--reader-bg',pair[0]);r.style.setProperty('--reader-ink',pair[1]);try{native()?.setKeepScreenOn(settings.awake);native()?.setSystemTheme(settings.theme==='night'?'night':settings.theme==='white'?'white':'paper')}catch(e){}applyReadingBrightness();if(currentBook&&currentBook.ext!=='pdf'&&document.getElementById('reader')?.classList.contains('active'))setTimeout(()=>{const p=document.getElementById('readerPage');p.scrollLeft=0;const count=pageCountForReader();const target=Math.round(oldFrac*Math.max(0,count-1));textPageState.count=count;textPageState.page=Math.max(0,Math.min(count-1,target));p.scrollLeft=textPageState.page*p.clientWidth;updateReaderProgress()},80)}
function changeFont(d){settings.font=Math.max(14,Math.min(34,settings.font+d));saveSettings()}
function setLineHeight(btn){settings.line=Number(btn.dataset.v);saveSettings()}
function setReaderMargin(btn){settings.margin=Number(btn.dataset.v);saveSettings()}
function setReaderBrightness(value,persist=true){settings.brightness=Math.max(1,Math.min(100,Number(value)||42));if(persist)localStorage.setItem('readerSettings_v5',JSON.stringify(settings));syncSettingsUI();applyReadingBrightness()}
function setTextClarity(value,persist=true){settings.clarity=Math.max(0,Math.min(100,Number(value)||0));document.documentElement.style.setProperty('--reader-weight',String(Math.round(400+settings.clarity*2.2)));if(persist)localStorage.setItem('readerSettings_v5',JSON.stringify(settings));syncSettingsUI()}
function applyReadingBrightness(){const r=document.getElementById('reader');if(!r?.classList.contains('active'))return;const pct=Math.max(1,Math.min(100,Number(settings.brightness)||42)),curve=Math.max(.01,Math.pow(pct/100,2.15));let usedNative=false;try{if(native()&&typeof native().setAppBrightness==='function'){native().setAppBrightness(curve);usedNative=true}}catch(e){}r.style.filter=usedNative?'none':`brightness(${Math.max(.08,pct/100)})`;const dim=document.getElementById('readerDimmer');if(dim)dim.style.opacity=String(pct<22?Math.min(.52,(22-pct)/21*.52):0)}
function resetAppBrightness(){try{if(native()&&typeof native().setAppBrightness==='function')native().setAppBrightness(-1)}catch(e){}const r=document.getElementById('reader');if(r)r.style.filter='none';const d=document.getElementById('readerDimmer');if(d)d.style.opacity='0'}
function setTheme(btn){settings.theme=btn.dataset.v;saveSettings()}
function toggleAwake(){settings.awake=!settings.awake;saveSettings()}
function syncSettingsUI(){document.getElementById('awakeToggle')?.classList.toggle('on',settings.awake);document.querySelectorAll('#lineSeg button').forEach(b=>b.classList.toggle('active',Number(b.dataset.v)===Number(settings.line)));document.querySelectorAll('#marginSeg button').forEach(b=>b.classList.toggle('active',Number(b.dataset.v)===Number(settings.margin)));document.querySelectorAll('#themeSeg button,#readerSettings [data-v]').forEach(b=>{if(['paper','ivory','warm','sepia','amber','stone','eink','white','night'].includes(b.dataset.v))b.classList.toggle('active',b.dataset.v===settings.theme)});for(const id of ['readerBrightnessRange','settingsBrightnessRange']){const el=document.getElementById(id);if(el)el.value=String(settings.brightness)}for(const id of ['readerBrightnessValue','settingsBrightnessValue']){const el=document.getElementById(id);if(el)el.textContent=settings.brightness+'%'}const cr=document.getElementById('readerClarityRange');if(cr)cr.value=String(settings.clarity);const cv=document.getElementById('readerClarityValue');if(cv)cv.textContent=settings.clarity+'%'}

let edgeGesture=null,edgeGestureConsumedUntil=0,edgeHudTimer=null;
function showEdgeHud(text){const h=document.getElementById('readerGestureHud');if(!h)return;h.textContent=text;h.classList.add('show');clearTimeout(edgeHudTimer);edgeHudTimer=setTimeout(()=>h.classList.remove('show'),650)}
function initReaderEdgeGestures(){const p=document.getElementById('readerPage');if(!p||p.dataset.edgeGestures)return;p.dataset.edgeGestures='1';p.addEventListener('pointerdown',e=>{if(!currentBook||currentBook.ext==='pdf'||e.pointerType==='mouse'&&e.button!==0)return;const r=p.getBoundingClientRect(),x=e.clientX-r.left;if(x<r.width*.17)edgeGesture={kind:'brightness',startY:e.clientY,start:Number(settings.brightness),active:false,pid:e.pointerId};else if(x>r.width*.83)edgeGesture={kind:'clarity',startY:e.clientY,start:Number(settings.clarity),active:false,pid:e.pointerId};else edgeGesture=null},{passive:true});p.addEventListener('pointermove',e=>{if(!edgeGesture||edgeGesture.pid!==e.pointerId)return;const dy=edgeGesture.startY-e.clientY;if(!edgeGesture.active&&Math.abs(dy)>12){edgeGesture.active=true;try{p.setPointerCapture(e.pointerId)}catch(_){}}if(!edgeGesture.active)return;e.preventDefault();const delta=dy/Math.max(220,p.clientHeight)*115;if(edgeGesture.kind==='brightness'){setReaderBrightness(edgeGesture.start+delta,false);showEdgeHud('☀  Brightness '+Math.round(settings.brightness)+'%')}else{setTextClarity(edgeGesture.start+delta,false);showEdgeHud('Aa  Text clarity '+Math.round(settings.clarity)+'%')}},{passive:false});const done=e=>{if(!edgeGesture)return;if(edgeGesture.active){edgeGestureConsumedUntil=Date.now()+350;localStorage.setItem('readerSettings_v5',JSON.stringify(settings));e.preventDefault()}edgeGesture=null};p.addEventListener('pointerup',done,{passive:false});p.addEventListener('pointercancel',done,{passive:false})}
async function resetLibrary'''
s=s[:m.start()]+newblock+s[m.end():]
s=s.replace("rp.addEventListener('click',e=>{if(!currentBook||currentBook.ext==='pdf')return;", "rp.addEventListener('click',e=>{if(Date.now()<edgeGestureConsumedUntil)return;if(!currentBook||currentBook.ext==='pdf')return;")
s=s.replace("window.addEventListener('DOMContentLoaded',()=>{loadSettings();", "window.addEventListener('DOMContentLoaded',()=>{loadSettings();initReaderEdgeGestures();")
htmlp.write_text(s)

j=javap.read_text()
if 'public void setAppBrightness(double value)' not in j:
    anchor='        @JavascriptInterface\n        public int getBatteryLevel() {'
    method='''        @JavascriptInterface
        public void setAppBrightness(double value) {
            runOnUiThread(() -> {
                android.view.WindowManager.LayoutParams lp = getWindow().getAttributes();
                if (value < 0) lp.screenBrightness = android.view.WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_NONE;
                else lp.screenBrightness = (float)Math.max(0.01, Math.min(1.0, value));
                getWindow().setAttributes(lp);
            });
        }

'''
    j=j.replace(anchor,method+anchor)
javap.write_text(j)

g=gradlep.read_text().replace('versionCode 12','versionCode 13').replace("versionName '0.12.0'","versionName '0.13.0'")
gradlep.write_text(g)
