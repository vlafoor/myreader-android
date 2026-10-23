from pathlib import Path
import re

# --- Native Android WebView fallback tap bridge + fresh page load ---
p=Path('app/src/main/java/com/myreader/app/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Extra imports for touch handling.
if 'import android.view.MotionEvent;' not in s:
    s=s.replace('import android.view.MenuItem;','import android.view.MenuItem;\nimport android.view.MotionEvent;')
if 'import android.util.Log;' not in s:
    s=s.replace('import android.util.Base64;','import android.util.Base64;\nimport android.util.Log;')

# Never restore a stale WebView document after app/package updates.
old_load=r'''        SharedPreferences appState = getSharedPreferences("myreader_app_state", MODE_PRIVATE);
        int currentVersion = 24;
        int lastLoadedVersion = appState.getInt("last_loaded_version", -1);
        boolean appUpdated = lastLoadedVersion != currentVersion;
        if (appUpdated) webView.clearCache(true);
        if (savedInstanceState == null || appUpdated) {
            webView.loadUrl("file:///android_asset/index.html");
        } else if (webView.restoreState(savedInstanceState) == null) {
            webView.loadUrl("file:///android_asset/index.html");
        }
        appState.edit().putInt("last_loaded_version", currentVersion).apply();'''
new_load=r'''        SharedPreferences appState = getSharedPreferences("myreader_app_state", MODE_PRIVATE);
        int currentVersion = BuildConfig.VERSION_CODE;
        int lastLoadedVersion = appState.getInt("last_loaded_version", -1);
        boolean appUpdated = lastLoadedVersion != currentVersion;
        if (appUpdated) webView.clearCache(true);
        // Always create a fresh DOM/JavaScript context. Library/progress/notes live in
        // IndexedDB/localStorage, so restoring WebView snapshots is unnecessary and can
        // resurrect a visually correct page with dead event state after APK updates.
        webView.getSettings().setCacheMode(WebSettings.LOAD_NO_CACHE);
        webView.loadUrl("file:///android_asset/index.html");
        appState.edit().putInt("last_loaded_version", currentVersion).apply();'''
if old_load not in s:
    raise SystemExit('old WebView load block not found')
s=s.replace(old_load,new_load,1)

# Replace ReaderWebView with a native fallback tap bridge.
old_cls=r'''    private class ReaderWebView extends WebView {
        ReaderWebView(Context context) { super(context); }
        @Override public ActionMode startActionMode(ActionMode.Callback callback) { return super.startActionMode(new ReaderActionModeCallback(callback)); }
        @Override public ActionMode startActionMode(ActionMode.Callback callback, int type) { return super.startActionMode(new ReaderActionModeCallback(callback), type); }
    }'''
new_cls=r'''    private class ReaderWebView extends WebView {
        private float tapDownX, tapDownY;
        private long tapDownAt;

        ReaderWebView(Context context) { super(context); }

        @Override
        public boolean onTouchEvent(MotionEvent event) {
            if (event != null) {
                if (event.getActionMasked() == MotionEvent.ACTION_DOWN) {
                    tapDownX = event.getX();
                    tapDownY = event.getY();
                    tapDownAt = System.currentTimeMillis();
                } else if (event.getActionMasked() == MotionEvent.ACTION_UP) {
                    final float upX = event.getX(), upY = event.getY();
                    final long age = System.currentTimeMillis() - tapDownAt;
                    final float slop = 18f * getResources().getDisplayMetrics().density;
                    if (age <= 900 && Math.abs(upX - tapDownX) <= slop && Math.abs(upY - tapDownY) <= slop) {
                        // Let WebView deliver its normal click first. If Bigme/WebView drops
                        // it, run a DOM fallback at the exact visual tap coordinate.
                        postDelayed(() -> {
                            final float density = Math.max(1f, getResources().getDisplayMetrics().density);
                            final float cssX = upX / density;
                            final float cssY = upY / density;
                            String js = "(function(x,y){" +
                                    "var now=Date.now();" +
                                    "if(window.__myreaderLastRealClickAt&&now-window.__myreaderLastRealClickAt<180)return 'native:already-clicked';" +
                                    "var e=document.elementFromPoint(x,y),n=e;" +
                                    "while(n&&n!==document.body){" +
                                    "if(n.matches&&n.matches('button,[onclick],.navitem,.chip,.tool,.book-card,.note-card,[role=button],label')){" +
                                    "try{n.click();window.__myreaderLastRealClickAt=Date.now();return 'native:clicked:'+((n.id||n.className||n.tagName)+'').slice(0,80)}catch(_){return 'native:click-error'}}" +
                                    "n=n.parentElement}" +
                                    "return 'native:no-target:'+((e&&e.tagName)||'none')" +
                                    "})(" + cssX + "," + cssY + ")";
                            evaluateJavascript(js, value -> Log.d("MyReaderTouch", String.valueOf(value)));
                        }, 90);
                    }
                }
            }
            return super.onTouchEvent(event);
        }

        @Override public ActionMode startActionMode(ActionMode.Callback callback) { return super.startActionMode(new ReaderActionModeCallback(callback)); }
        @Override public ActionMode startActionMode(ActionMode.Callback callback, int type) { return super.startActionMode(new ReaderActionModeCallback(callback), type); }
    }'''
if old_cls not in s:
    raise SystemExit('ReaderWebView block not found')
s=s.replace(old_cls,new_cls,1)

# WebView should be inspectable in debug builds and report page readiness.
if 'WebView.setWebContentsDebuggingEnabled(true);' not in s:
    s=s.replace('webView = new ReaderWebView(this);','webView = new ReaderWebView(this);\n        WebView.setWebContentsDebuggingEnabled(true);',1)

p.write_text(s,encoding='utf-8')

# --- HTML: remove the unsuccessful global touch shim and add click telemetry/self-test ---
hpath=Path('app/src/main/assets/index.html')
h=hpath.read_text(encoding='utf-8')

h=re.sub(r'\n?<style id="v039-touch-safety">.*?</style>\n?', '\n', h, flags=re.S)
h=re.sub(r'\n?<script id="v039-touch-safety-js">.*?</script>\n?', '\n', h, flags=re.S)

telemetry=r'''
<script id="v041-functional-guard">
(function(){
  window.__myreaderLastRealClickAt=0;
  document.addEventListener('click',function(){window.__myreaderLastRealClickAt=Date.now()},true);

  window.__runMyReaderFunctionalSelfTest=function(){
    var result={ok:true,steps:[]};
    function check(name,fn){
      try{var v=fn();result.steps.push({name:name,ok:!!v,value:String(v)});if(!v)result.ok=false}
      catch(e){result.steps.push({name:name,ok:false,error:String(e)});result.ok=false}
    }
    var original=document.querySelector('.screen.active')?.id||'library';
    var oldFilter=window.libraryFilter;
    check('openScreen exists',function(){return typeof openScreen==='function'});
    check('setLibraryFilter exists',function(){return typeof setLibraryFilter==='function'});
    check('library->stats',function(){openScreen('stats');return document.getElementById('stats')?.classList.contains('active')});
    check('stats->notes',function(){openScreen('notes');return document.getElementById('notes')?.classList.contains('active')});
    check('notes->settings',function(){openScreen('settings');return document.getElementById('settings')?.classList.contains('active')});
    check('settings->library',function(){openScreen('library');return document.getElementById('library')?.classList.contains('active')});
    check('finished filter',function(){
      var b=[...document.querySelectorAll('#library .chip[data-filter]')].find(x=>x.dataset.filter==='finished');
      if(!b)return false;setLibraryFilter(b);return b.classList.contains('active')&&window.libraryFilter==='finished';
    });
    try{
      var restore=[...document.querySelectorAll('#library .chip[data-filter]')].find(x=>x.dataset.filter===(oldFilter||'all'));
      if(restore)setLibraryFilter(restore);
      openScreen(original);
    }catch(_){}
    window.__myreaderSelfTest=result;
    return result;
  };

  setTimeout(function(){
    try{window.__myreaderSelfTest=window.__runMyReaderFunctionalSelfTest()}
    catch(e){window.__myreaderSelfTest={ok:false,error:String(e)}}
  },350);
})();
</script>
'''
h=h.replace('</body>',telemetry+'\n</body>',1)

assert 'v039-touch-safety' not in h
assert 'id="v041-functional-guard"' in h
assert '__runMyReaderFunctionalSelfTest' in h
hpath.write_text(h,encoding='utf-8')

print('v0.4.1 fresh DOM + native fallback tap + functional self-test applied')
