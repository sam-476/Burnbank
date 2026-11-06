package app.burnbank2;

import android.content.Context;
import android.graphics.Color;
import android.webkit.JavascriptInterface;

/** Exposed to the page as window.Burnbank: the two reminder settings, and the page background for the system bars. */
public class Bridge {
    private final Context ctx;
    private final MainActivity act;

    Bridge(MainActivity a) {
        act = a;
        ctx = a.getApplicationContext();
    }

    @JavascriptInterface
    public void setTdee(int tdee) {
        if (tdee < 500 || tdee > 10000) return;
        Reminders.prefs(ctx).edit().putInt("tdee", tdee).apply();
    }

    @JavascriptInterface
    public void setReminders(boolean on) {
        Reminders.prefs(ctx).edit().putBoolean("reminders", on).apply();
        if (on) Reminders.schedule(ctx); else Reminders.cancel(ctx);
    }

    /** Called by the page on load and on every theme change with the theme's background, e.g. "#525252". */
    @JavascriptInterface
    public void setBg(String hex) {
        final int color;
        try {
            if (hex == null) return;
            String h = hex.trim();
            if (!h.startsWith("#") || (h.length() != 7 && h.length() != 4)) return;
            if (h.length() == 4) h = "#" + h.charAt(1) + h.charAt(1) + h.charAt(2) + h.charAt(2) + h.charAt(3) + h.charAt(3);
            color = Color.parseColor(h) | 0xFF000000;
        } catch (IllegalArgumentException e) {
            return;
        }
        Reminders.prefs(ctx).edit().putInt("bg", color).apply();
        act.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                act.applyBars(color);
            }
        });
    }
}
