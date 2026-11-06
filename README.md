# Burnbank 2.0

A calorie balance that ticks up every hour. Start the day at 0, earn your daily number hour by hour, food takes from it, exercise gives back. Midnight banks the day. No account, no server, no scale.

Single-file web app with an Android wrapper. Everything stays on the device.

## Files

| Path | What it is |
|---|---|
| `burnbank.html` | The whole app in one file (no libraries, no network). |
| `docs/index.html` | The same app as a complete page, ready to host as a website (GitHub Pages: Settings → Pages → source `main` / `docs`). |
| `android/` | Android wrapper: WebView + three daily reminders. Package `app.burnbank2`, versionName 2.0. |
| `build.sh` | Builds and signs `Burnbank.apk`. Tools it needs are listed at the top of the script. |
| `make_asset.py` | Turns `burnbank.html` into `android/assets/index.html`. |
| `make_icons.py` | Launcher PNGs for older launchers (the adaptive icon is in `android/res/`). |
| `assemble.py` | Adds `classes.dex` to aapt2's output, 4-byte aligned (replaces zipalign). |
| `test_app.py` | End-to-end tests (Playwright): `python3 test_app.py` |
| `shoot_themes.py` | Theme preview sheets. |
| `make_v1_backup.py`, `v1_backup.json` | A real backup from Burnbank 1.1, used by the restore tests. |

The signing key is not in this repository and never should be. Keep it with its password, outside the app.
