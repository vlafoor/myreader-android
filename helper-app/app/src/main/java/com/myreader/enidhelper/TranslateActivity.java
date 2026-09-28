package com.myreader.enidhelper;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.os.Bundle;
import android.text.Html;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.Space;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TranslateActivity extends Activity {
    private static final String PREFS = "enid_cache_v1";
    private static final String API_BASE = "https://api.mymemory.translated.net/get";
    private static final int MAX_BYTES = 500;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    private TextView wordView;
    private TextView resultView;
    private TextView statusView;
    private ProgressBar progress;
    private Button copyButton;

    private String selectedText = "";
    private String currentTranslation = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();

        selectedText = extractText(getIntent());
        if (selectedText == null) selectedText = "";
        selectedText = normalizeDisplay(selectedText);

        if (selectedText.isEmpty()) {
            wordView.setText("Tidak ada teks");
            resultView.setText("Pilih kata Inggris di xReader lalu pilih Add EN→ID atau Share → Add EN→ID.");
            statusView.setText("");
            return;
        }

        wordView.setText(selectedText);
        lookup(selectedText);
    }

    private void buildUi() {
        int pad = dp(22);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(pad, dp(18), pad, dp(18));
        root.setBackgroundColor(Color.WHITE);

        TextView title = new TextView(this);
        title.setText("EN → ID");
        title.setTextSize(16);
        title.setTextColor(Color.DKGRAY);
        title.setGravity(Gravity.START);
        root.addView(title, matchWrap());

        wordView = new TextView(this);
        wordView.setTextSize(26);
        wordView.setTextColor(Color.BLACK);
        wordView.setPadding(0, dp(18), 0, dp(12));
        wordView.setTextIsSelectable(true);
        root.addView(wordView, matchWrap());

        progress = new ProgressBar(this);
        progress.setIndeterminate(true);
        progress.setVisibility(ProgressBar.GONE);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(dp(28), dp(28));
        p.gravity = Gravity.START;
        root.addView(progress, p);

        resultView = new TextView(this);
        resultView.setTextSize(22);
        resultView.setTextColor(Color.BLACK);
        resultView.setLineSpacing(0, 1.15f);
        resultView.setTextIsSelectable(true);
        resultView.setPadding(0, dp(8), 0, dp(8));
        root.addView(resultView, matchWrap());

        statusView = new TextView(this);
        statusView.setTextSize(14);
        statusView.setTextColor(Color.DKGRAY);
        statusView.setPadding(0, dp(4), 0, dp(14));
        root.addView(statusView, matchWrap());

        Space spacer = new Space(this);
        root.addView(spacer, new LinearLayout.LayoutParams(1, 0, 1f));

        LinearLayout buttons = new LinearLayout(this);
        buttons.setOrientation(LinearLayout.HORIZONTAL);
        buttons.setGravity(Gravity.END);

        copyButton = new Button(this);
        copyButton.setText("Copy");
        copyButton.setEnabled(false);
        copyButton.setOnClickListener(v -> copyResult());
        buttons.addView(copyButton);

        Button closeButton = new Button(this);
        closeButton.setText("Close");
        closeButton.setOnClickListener(v -> finish());
        buttons.addView(closeButton);

        root.addView(buttons, matchWrap());
        setContentView(root);
    }

    private void lookup(String text) {
        String key = normalizeKey(text);
        SharedPreferences prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        String cached = prefs.getString(key, null);

        if (cached != null && !cached.isBlank()) {
            showResult(cached, "Tersimpan offline • internet tidak dipakai");
            return;
        }

        if (!hasInternet()) {
            showError("Belum tersimpan. Sambungkan internet sekali untuk kata ini.");
            return;
        }

        if (text.getBytes(StandardCharsets.UTF_8).length > MAX_BYTES) {
            showError("Teks terlalu panjang. Pilih satu kata atau frasa pendek.");
            return;
        }

        progress.setVisibility(ProgressBar.VISIBLE);
        resultView.setText("Mencari arti…");
        statusView.setText("Online sekali, lalu otomatis disimpan untuk offline.");

        executor.execute(() -> {
            try {
                String translation = fetchTranslation(text);
                if (translation == null || translation.isBlank()) {
                    throw new Exception("Terjemahan kosong");
                }

                translation = cleanTranslation(translation);
                getSharedPreferences(PREFS, MODE_PRIVATE)
                        .edit()
                        .putString(key, translation)
                        .apply();

                String finalTranslation = translation;
                runOnUiThread(() -> {
                    progress.setVisibility(ProgressBar.GONE);
                    showResult(finalTranslation, "Baru diunduh • otomatis tersimpan offline");
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    progress.setVisibility(ProgressBar.GONE);
                    showError("Gagal mencari arti online. Coba lagi saat internet stabil.");
                });
            }
        });
    }

    private String fetchTranslation(String text) throws Exception {
        String q = URLEncoder.encode(text, StandardCharsets.UTF_8.name());
        String pair = URLEncoder.encode("en|id", StandardCharsets.UTF_8.name());
        String url = API_BASE + "?q=" + q + "&langpair=" + pair + "&mt=1";

        HttpURLConnection conn = (HttpURLConnection) new java.net.URL(url).openConnection();
        conn.setConnectTimeout(8000);
        conn.setReadTimeout(10000);
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Accept", "application/json");
        conn.setRequestProperty("User-Agent", "EN-ID-Dictionary-Helper/0.1");

        int code = conn.getResponseCode();
        InputStream stream = code >= 200 && code < 300 ? conn.getInputStream() : conn.getErrorStream();
        String body = readAll(stream);
        conn.disconnect();

        if (code < 200 || code >= 300) {
            throw new Exception("HTTP " + code);
        }

        JSONObject root = new JSONObject(body);
        int status = root.optInt("responseStatus", 200);
        if (status != 200) {
            throw new Exception(root.optString("responseDetails", "API error"));
        }

        JSONObject data = root.optJSONObject("responseData");
        if (data == null) return null;
        return data.optString("translatedText", "");
    }

    private String readAll(InputStream stream) throws Exception {
        if (stream == null) return "";
        BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) sb.append(line);
        reader.close();
        return sb.toString();
    }

    private String cleanTranslation(String raw) {
        String decoded = Html.fromHtml(raw, Html.FROM_HTML_MODE_LEGACY).toString().trim();
        return decoded.replaceAll("\\s+", " ");
    }

    private void showResult(String translation, String status) {
        currentTranslation = translation;
        resultView.setText(translation);
        statusView.setText(status);
        copyButton.setEnabled(true);
    }

    private void showError(String message) {
        currentTranslation = "";
        resultView.setText(message);
        statusView.setText("");
        copyButton.setEnabled(false);
    }

    private void copyResult() {
        if (currentTranslation.isEmpty()) return;
        ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        cm.setPrimaryClip(ClipData.newPlainText("EN-ID translation", currentTranslation));
        Toast.makeText(this, "Arti disalin", Toast.LENGTH_SHORT).show();
    }

    private boolean hasInternet() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        Network network = cm.getActiveNetwork();
        if (network == null) return false;
        NetworkCapabilities caps = cm.getNetworkCapabilities(network);
        return caps != null && caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
    }

    private String extractText(Intent intent) {
        if (intent == null) return "";
        String action = intent.getAction();

        if (Intent.ACTION_PROCESS_TEXT.equals(action)) {
            CharSequence cs = intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT);
            return cs == null ? "" : cs.toString();
        }

        if (Intent.ACTION_SEND.equals(action)) {
            CharSequence cs = intent.getCharSequenceExtra(Intent.EXTRA_TEXT);
            return cs == null ? "" : cs.toString();
        }

        return "";
    }

    private String normalizeDisplay(String text) {
        String t = text == null ? "" : text.trim().replaceAll("\\s+", " ");
        if (t.length() > 500) t = t.substring(0, 500);
        return t;
    }

    private String normalizeKey(String text) {
        return normalizeDisplay(text).toLowerCase(Locale.ROOT);
    }

    private LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
    }

    private int dp(int value) {
        float d = getResources().getDisplayMetrics().density;
        return Math.round(value * d);
    }

    @Override
    protected void onDestroy() {
        executor.shutdownNow();
        super.onDestroy();
    }
}
