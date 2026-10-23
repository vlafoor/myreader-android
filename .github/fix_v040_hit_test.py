from pathlib import Path
import re

# Native: never move the WebView into Android fullscreen/layout-behind-bars mode.
p=Path('app/src/main/java/com/myreader/app/MainActivity.java')
s=p.read_text(encoding='utf-8')

old=r'''    private void applyReaderImmersiveUi() {
        View decor = getWindow().getDecorView();
        if (readerImmersive) {
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
            int sticky = View.SYSTEM_UI_FLAG_LAYOUT_STABLE | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                    View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_FULLSCREEN |
                    View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY;
            decor.setSystemUiVisibility(sticky);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                WindowInsetsController controller = getWindow().getInsetsController();
                if (controller != null) {
                    controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                    controller.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                }
            }
        } else {
            getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                WindowInsetsController controller = getWindow().getInsetsController();
                if (controller != null) controller.show(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
            }
            int flags = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) flags |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            decor.setSystemUiVisibility(flags);
        }
    }'''

new=r'''    private void applyReaderImmersiveUi() {
        // IMPORTANT for Bigme / Android WebView hit testing:
        // Never lay the WebView behind system bars. Older MyReader v0.8 fixed a global
        // "buttons look normal but taps do nothing" bug caused by visual coordinates
        // diverging from WebView hit-test coordinates when fullscreen/insets were applied.
        //
        // Reader "immersive" is now HTML/CSS-only: it hides MyReader's reader chrome,
        // while Android status/navigation bars remain outside the WebView.
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            getWindow().setDecorFitsSystemWindows(true);
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) {
                controller.show(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
            }
        }
        int flags = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            flags |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        }
        getWindow().getDecorView().setSystemUiVisibility(flags);
    }'''

if old not in s:
    raise SystemExit('applyReaderImmersiveUi block not found')
s=s.replace(old,new,1)

# setReaderImmersive can retain state, but applying it never changes WebView coordinates.
# Remove delayed fullscreen re-entry hooks that could re-apply stale flags.
s=s.replace('        if (hasFocus && readerImmersive && webView != null) webView.postDelayed(this::applyReaderImmersiveUi, 60);',
            '        if (hasFocus && webView != null) webView.postDelayed(this::applyReaderImmersiveUi, 60);')
s=s.replace('        if (readerImmersive && webView != null) {\n            webView.postDelayed(this::applyReaderImmersiveUi, 80);\n            webView.postDelayed(() -> webView.evaluateJavascript("if(window.applyReadingBrightness)window.applyReadingBrightness()", null), 120);\n        }',
            '        if (webView != null) {\n            webView.postDelayed(this::applyReaderImmersiveUi, 80);\n            if (readerImmersive) webView.postDelayed(() -> webView.evaluateJavascript("if(window.applyReadingBrightness)window.applyReadingBrightness()", null), 120);\n        }')

p.write_text(s,encoding='utf-8')

# HTML: don't request native fullscreen when opening a book.
hpath=Path('app/src/main/assets/index.html')
h=hpath.read_text(encoding='utf-8')
h=h.replace("try{native()?.setReaderImmersive(true);native()?.setAppBrightness?.(brightnessToNative(settings.brightness))}catch(e){}",
            "try{native()?.setReaderImmersive(false);native()?.setAppBrightness?.(brightnessToNative(settings.brightness))}catch(e){}")
assert "native()?.setReaderImmersive(false);native()?.setAppBrightness" in h
hpath.write_text(h,encoding='utf-8')

print('v0.4.0 native WebView hit-test fix applied')
