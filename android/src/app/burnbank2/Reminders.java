package app.burnbank2;

import android.Manifest;
import android.app.AlarmManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Build;

import java.util.Calendar;
import java.util.Locale;

/** Three daily reminders (13:00, 18:00, 21:00) showing what has been earned so far. */
public class Reminders {
    static final int[] HOURS = {13, 18, 21};
    static final String CHANNEL = "reminders";
    static final int NOTIFICATION_ID = 7;

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences("burnbank", Context.MODE_PRIVATE);
    }

    static boolean enabled(Context c) {
        return prefs(c).getBoolean("reminders", true);
    }

    static PendingIntent alarmIntent(Context c, int i) {
        Intent in = new Intent(c, ReminderReceiver.class);
        in.setAction("app.burnbank2.REMIND_" + HOURS[i]);
        return PendingIntent.getBroadcast(c, 100 + i, in,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static void schedule(Context c) {
        if (!enabled(c)) { cancel(c); return; }
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        long now = System.currentTimeMillis();
        for (int i = 0; i < HOURS.length; i++) {
            Calendar cal = Calendar.getInstance();
            cal.set(Calendar.HOUR_OF_DAY, HOURS[i]);
            cal.set(Calendar.MINUTE, 0);
            cal.set(Calendar.SECOND, 0);
            cal.set(Calendar.MILLISECOND, 0);
            if (cal.getTimeInMillis() <= now) cal.add(Calendar.DATE, 1);
            am.setInexactRepeating(AlarmManager.RTC_WAKEUP, cal.getTimeInMillis(),
                    AlarmManager.INTERVAL_DAY, alarmIntent(c, i));
        }
    }

    static void cancel(Context c) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        for (int i = 0; i < HOURS.length; i++) am.cancel(alarmIntent(c, i));
    }

    static void show(Context c) {
        if (!enabled(c)) return;
        if (Build.VERSION.SDK_INT >= 33
                && c.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            return;
        }
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;

        int tdee = prefs(c).getInt("tdee", 2400);
        int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
        int earned = Math.round(hour * tdee / 24f);
        String title = "+" + String.format(Locale.US, "%,d", earned) + " kcal earned so far";
        String text = hour + " of 24 hours banked. Open Burnbank to see your balance.";

        Intent open = new Intent(c, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent tap = PendingIntent.getActivity(c, 1, open,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification.Builder b;
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "Reminders", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("Three a day, showing what you have earned so far.");
            nm.createNotificationChannel(ch);
            b = new Notification.Builder(c, CHANNEL);
        } else {
            b = new Notification.Builder(c);
        }
        b.setSmallIcon(R.drawable.ic_notif)
         .setColor(0xFFF6BE2E)
         .setContentTitle(title)
         .setContentText(text)
         .setContentIntent(tap)
         .setAutoCancel(true);
        nm.notify(NOTIFICATION_ID, b.build());
    }
}
