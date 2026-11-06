package app.burnbank2;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.view.WindowInsetsController;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    static final int DEFAULT_BG = 0xFF525252; // the Dark theme's background; the page updates it via Bridge.setBg

    private WebView web;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setTextZoom(100);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return true; // the app never navigates anywhere
            }

            @Override
            @SuppressWarnings("deprecation")
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return true;
            }
        });
        web.addJavascriptInterface(new Bridge(this), "Burnbank");
        setContentView(web);
        applyBars(Reminders.prefs(this).getInt("bg", DEFAULT_BG)); // last theme's colour, so there is no flash
        web.loadUrl("file:///android_asset/index.html");

        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
        }
        Reminders.schedule(this);
    }

    /** Paint the window, the WebView and both system bars in the theme's background; pick dark or light bar icons to match. */
    @SuppressWarnings("deprecation")
    void applyBars(int color) {
        Window w = getWindow();
        if (w == null) return;
        w.setBackgroundDrawable(new ColorDrawable(color));
        w.setStatusBarColor(color);
        w.setNavigationBarColor(color);
        if (web != null) web.setBackgroundColor(color);
        boolean light = luminance(color) > 0.5;
        View decor = w.getDecorView();
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController c = decor.getWindowInsetsController();
            if (c != null) {
                int mask = WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(light ? mask : 0, mask);
            }
        } else {
            int f = decor.getSystemUiVisibility();
            f = light ? (f | View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR) : (f & ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
            if (Build.VERSION.SDK_INT >= 26) {
                f = light ? (f | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR) : (f & ~View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
            }
            decor.setSystemUiVisibility(f);
        }
    }

    /** Relative luminance (WCAG), 0 = black, 1 = white. */
    static double luminance(int color) {
        double r = chan(Color.red(color)), g = chan(Color.green(color)), b = chan(Color.blue(color));
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }

    private static double chan(int v) {
        double c = v / 255.0;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.evaluateJavascript("document.dispatchEvent(new Event('visibilitychange'))", null);
    }

    @Override
    protected void onDestroy() {
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
