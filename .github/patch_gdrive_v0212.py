from pathlib import Path
import re

root=Path('app')
htmlp=root/'src/main/assets/index.html'
javap=root/'src/main/java/com/myreader/app/MainActivity.java'
gradlep=root/'build.gradle'

g=gradlep.read_text(encoding='utf-8')
if 'play-services-auth' not in g:
    g += "\n\ndependencies {\n    implementation 'com.google.android.gms:play-services-auth:21.5.0'\n}\n"
g=re.sub(r'versionCode\s+\d+', 'versionCode 20', g)
g=re.sub(r"versionName\s+['\"][^'\"]+['\"]", "versionName '0.2.12'", g)
gradlep.write_text(g,encoding='utf-8')

j=javap.read_text(encoding='utf-8')
imports='''\nimport android.app.PendingIntent;\nimport android.webkit.JavascriptInterface;\nimport com.google.android.gms.auth.api.identity.AuthorizationClient;\nimport com.google.android.gms.auth.api.identity.AuthorizationRequest;\nimport com.google.android.gms.auth.api.identity.AuthorizationResult;\nimport com.google.android.gms.auth.api.identity.Identity;\nimport com.google.android.gms.common.api.Scope;\nimport java.io.BufferedReader;\nimport java.io.InputStreamReader;\nimport java.io.OutputStream;\nimport java.net.HttpURLConnection;\nimport java.net.URL;\nimport java.nio.charset.StandardCharsets;\nimport java.util.Arrays;\n'''
if 'AuthorizationClient' not in j:
    idx=j.index('public class MainActivity')
    j=j[:idx]+imports+'\n'+j[idx:]

class_anchor='public class MainActivity extends Activity {'
if class_anchor not in j:
    raise SystemExit('MainActivity class anchor not found')
fields='''\n    private static final int DRIVE_AUTH_REQUEST = 2001;\n    private static final String DRIVE_APPDATA_SCOPE = "https://www.googleapis.com/auth/drive.appdata";\n    private static final String DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file";\n    private AuthorizationClient driveAuthorizationClient;\n    private volatile String driveAccessToken;\n'''
if 'DRIVE_AUTH_REQUEST' not in j:
    j=j.replace(class_anchor,class_anchor+fields,1)

if 'Identity.getAuthorizationClient(this)' not in j:
    anchor='setContentView(webView);'
    if anchor not in j: raise SystemExit('setContentView anchor not found')
    j=j.replace(anchor,anchor+'\n        driveAuthorizationClient = Identity.getAuthorizationClient(this);',1)

if 'new DriveSyncBridge()' not in j:
    matches=list(re.finditer(r'webView\.addJavascriptInterface\([^;]+;',j))
    if matches:
        pos=matches[-1].end()
        j=j[:pos]+'\n        webView.addJavascriptInterface(new DriveSyncBridge(), "DriveSync");'+j[pos:]
    else:
        anchor='webView.setWebViewClient(new WebViewClient());'
        if anchor not in j: raise SystemExit('WebView anchor not found')
        j=j.replace(anchor,anchor+'\n        webView.addJavascriptInterface(new DriveSyncBridge(), "DriveSync");',1)

if 'requestCode == DRIVE_AUTH_REQUEST' not in j:
    m=re.search(r'(protected void onActivityResult\s*\([^)]*\)\s*\{)',j)
    if not m: raise SystemExit('onActivityResult not found')
    inject='''\n        if (requestCode == DRIVE_AUTH_REQUEST) {\n            if (resultCode == RESULT_OK && data != null) {\n                try {\n                    AuthorizationResult result = driveAuthorizationClient.getAuthorizationResultFromIntent(data);\n                    acceptDriveAuthorization(result);\n                } catch (Exception e) {\n                    notifyDriveAuth(false, "Google Drive authorization failed: " + e.getMessage());\n                }\n            } else {\n                notifyDriveAuth(false, "Google Drive connection cancelled");\n            }\n            return;\n        }\n'''
    j=j[:m.end()]+inject+j[m.end():]

bridge=r'''\n\n    private AuthorizationRequest driveAuthorizationRequest() {\n        return AuthorizationRequest.builder()\n                .setRequestedScopes(Arrays.asList(\n                        new Scope(DRIVE_APPDATA_SCOPE),\n                        new Scope(DRIVE_FILE_SCOPE)))\n                .build();\n    }\n\n    private void acceptDriveAuthorization(AuthorizationResult result) {\n        if (result == null || result.getAccessToken() == null || result.getAccessToken().isEmpty()) {\n            notifyDriveAuth(false, "No Google Drive access token returned");\n            return;\n        }\n        driveAccessToken = result.getAccessToken();\n        notifyDriveAuth(true, "Google Drive connected");\n    }\n\n    private void notifyDriveAuth(boolean ok, String message) {\n        final String js = "window.onNativeDriveAuth && window.onNativeDriveAuth(" + ok + "," + org.json.JSONObject.quote(message == null ? "" : message) + ");";\n        runOnUiThread(() -> webView.evaluateJavascript(js, null));\n    }\n\n    private void notifyDriveSync(boolean ok, String message) {\n        final String js = "window.onNativeDriveSync && window.onNativeDriveSync(" + ok + "," + org.json.JSONObject.quote(message == null ? "" : message) + ");";\n        runOnUiThread(() -> webView.evaluateJavascript(js, null));\n    }\n\n    private class DriveSyncBridge {\n        @JavascriptInterface\n        public void connectGoogleDrive() {\n            runOnUiThread(() -> {\n                if (driveAuthorizationClient == null) {\n                    driveAuthorizationClient = Identity.getAuthorizationClient(MainActivity.this);\n                }\n                driveAuthorizationClient.authorize(driveAuthorizationRequest())\n                        .addOnSuccessListener(result -> {\n                            if (result.hasResolution()) {\n                                PendingIntent pi = result.getPendingIntent();\n                                if (pi == null) {\n                                    notifyDriveAuth(false, "Google authorization needs a resolution but returned no intent");\n                                    return;\n                                }\n                                try {\n                                    startIntentSenderForResult(pi.getIntentSender(), DRIVE_AUTH_REQUEST, null, 0, 0, 0);\n                                } catch (Exception e) {\n                                    notifyDriveAuth(false, "Could not open Google authorization: " + e.getMessage());\n                                }\n                            } else {\n                                acceptDriveAuthorization(result);\n                            }\n                        })\n                        .addOnFailureListener(e -> notifyDriveAuth(false, "Google Drive authorization failed: " + e.getMessage()));\n            });\n        }\n\n        @JavascriptInterface\n        public void disconnectGoogleDrive() {\n            driveAccessToken = null;\n            notifyDriveAuth(false, "Disconnected");\n        }\n\n        @JavascriptInterface\n        public boolean isGoogleDriveConnected() {\n            return driveAccessToken != null && !driveAccessToken.isEmpty();\n        }\n\n        @JavascriptInterface\n        public void syncGoogleDrive(String payloadJson) {\n            final String token = driveAccessToken;\n            if (token == null || token.isEmpty()) {\n                notifyDriveSync(false, "Connect Google Drive first");\n                return;\n            }\n            final String payload = payloadJson == null ? "{}" : payloadJson;\n            new Thread(() -> {\n                try {\n                    uploadDriveSnapshot(token, payload);\n                    notifyDriveSync(true, "Google Drive sync complete");\n                } catch (Exception e) {\n                    notifyDriveSync(false, "Sync failed: " + e.getMessage());\n                }\n            }, "MyReaderDriveSync").start();\n        }\n    }\n\n    private void uploadDriveSnapshot(String token, String payloadJson) throws Exception {\n        String boundary = "myreader_" + System.currentTimeMillis();\n        String metadata = "{\\\"name\\\":\\\"myreader-sync.json\\\",\\\"parents\\\":[\\\"appDataFolder\\\"]}";\n        byte[] body = ("--" + boundary + "\\r\\n" +\n                "Content-Type: application/json; charset=UTF-8\\r\\n\\r\\n" + metadata + "\\r\\n" +\n                "--" + boundary + "\\r\\n" +\n                "Content-Type: application/json; charset=UTF-8\\r\\n\\r\\n" + payloadJson + "\\r\\n" +\n                "--" + boundary + "--\\r\\n").getBytes(StandardCharsets.UTF_8);\n        URL url = new URL("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name");\n        HttpURLConnection c = (HttpURLConnection) url.openConnection();\n        c.setRequestMethod("POST");\n        c.setDoOutput(true);\n        c.setConnectTimeout(15000);\n        c.setReadTimeout(20000);\n        c.setRequestProperty("Authorization", "Bearer " + token);\n        c.setRequestProperty("Content-Type", "multipart/related; boundary=" + boundary);\n        try (OutputStream os = c.getOutputStream()) { os.write(body); }\n        int code = c.getResponseCode();\n        if (code < 200 || code >= 300) {\n            BufferedReader br = new BufferedReader(new InputStreamReader(c.getErrorStream() != null ? c.getErrorStream() : c.getInputStream(), StandardCharsets.UTF_8));\n            StringBuilder sb = new StringBuilder(); String line; while ((line = br.readLine()) != null) sb.append(line);\n            throw new Exception("Drive API " + code + ": " + sb);\n        }\n        c.disconnect();\n    }\n'''
if 'private class DriveSyncBridge' not in j:
    pos=j.rfind('\n}')
    if pos<0: raise SystemExit('class closing brace not found')
    j=j[:pos]+bridge+j[pos:]
javap.write_text(j,encoding='utf-8')

s=htmlp.read_text(encoding='utf-8')
css='''\n<style id="gdrive-sync-v0212">\n.drive-sync-card{border:1px solid var(--line);background:var(--card);border-radius:16px;overflow:hidden;margin:0 0 14px}.drive-sync-row{display:flex;align-items:center;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line)}.drive-sync-row:last-child{border-bottom:0}.drive-sync-copy{flex:1;min-width:0}.drive-sync-copy b{display:block;font-size:12px}.drive-sync-copy small{display:block;font-size:10px;color:var(--muted);margin-top:3px}.drive-sync-btn{border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:9px;padding:8px 10px;font-size:10px;font-weight:800}.drive-sync-btn.primary{background:var(--ink);color:var(--paper)}.drive-sync-status{font-size:9px;border:1px solid var(--line);border-radius:999px;padding:5px 7px;color:var(--muted)}\n</style>\n'''
if 'gdrive-sync-v0212' not in s:
    s=s.replace('</head>',css+'</head>',1)

section='''\n      <div class="settings-group" id="googleDriveSyncSettings">\n        <div class="group-title">Google Drive Sync</div>\n        <div class="drive-sync-card">\n          <div class="drive-sync-row"><span>☁</span><span class="drive-sync-copy"><b>Google Drive</b><small id="driveSyncSubtitle">Not connected</small></span><span id="driveSyncStatus" class="drive-sync-status">Offline</span><button id="driveConnectBtn" class="drive-sync-btn" onclick="connectDriveNative()">Connect</button></div>\n          <div class="drive-sync-row"><span>↺</span><span class="drive-sync-copy"><b>Library sync</b><small>Progress, notes, highlights, collections, and reader settings</small></span><button class="drive-sync-btn primary" onclick="syncDriveNative()">Sync now</button></div>\n        </div>\n      </div>\n'''
if 'id="googleDriveSyncSettings"' not in s:
    marker='<div class="settings-group">\n        <div class="group-title">Language tools</div>'
    if marker in s:
        s=s.replace(marker,section+marker,1)
    else:
        idx=s.find('<div class="settings-group">', s.find('id="settings"'))
        if idx<0: raise SystemExit('settings UI anchor not found')
        s=s[:idx]+section+s[idx:]

js=r'''\n<script id="gdrive-sync-bridge-js">\nfunction driveNative(){return window.DriveSync||null}\nfunction driveUi(connected,message){\n  const st=document.getElementById('driveSyncStatus'),sub=document.getElementById('driveSyncSubtitle'),btn=document.getElementById('driveConnectBtn');\n  if(st){st.textContent=connected?'Connected':'Offline'}\n  if(sub){sub.textContent=message|| (connected?'Google Drive connected':'Not connected')}\n  if(btn){btn.textContent=connected?'Disconnect':'Connect';btn.onclick=connected?disconnectDriveNative:connectDriveNative}\n}\nfunction connectDriveNative(){const n=driveNative();if(!n){showToast?.('Google Drive requires the Android app');return}try{n.connectGoogleDrive()}catch(e){showToast?.('Could not open Google Drive login')}}\nfunction disconnectDriveNative(){const n=driveNative();try{n?.disconnectGoogleDrive()}catch(e){}driveUi(false,'Disconnected')}\nfunction onNativeDriveAuth(ok,message){driveUi(!!ok,message);if(typeof showToast==='function')showToast(message|| (ok?'Connected':'Connection failed'))}\nfunction makeDriveSnapshot(){return JSON.stringify({version:1,updatedAt:new Date().toISOString(),settings:typeof settings==='object'?settings:{},annotations:typeof annotations==='function'?annotations():[],lastOpenedBook:localStorage.getItem('lastOpenedBook_v4')||null})}\nfunction syncDriveNative(){const n=driveNative();if(!n){showToast?.('Google Drive requires the Android app');return}try{n.syncGoogleDrive(makeDriveSnapshot())}catch(e){showToast?.('Sync could not start')}}\nfunction onNativeDriveSync(ok,message){if(typeof showToast==='function')showToast(message|| (ok?'Sync complete':'Sync failed'));if(ok)localStorage.setItem('driveLastSync_v1',new Date().toISOString())}\nwindow.addEventListener('DOMContentLoaded',()=>{try{driveUi(!!driveNative()?.isGoogleDriveConnected(),driveNative()?.isGoogleDriveConnected()?'Google Drive connected':'Not connected')}catch(e){driveUi(false,'Not connected')}});\n</script>\n'''
if 'gdrive-sync-bridge-js' not in s:
    s=s.replace('</body>',js+'</body>',1)
htmlp.write_text(s,encoding='utf-8')
print('Google Drive v0.2.12 patch applied')
