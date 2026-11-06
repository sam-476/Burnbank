#!/bin/bash
# Burnbank v2 APK build (package app.burnbank2). Needs: JDK (javac/jar/keytool), python3 + Pillow, and tools/ as described in the handover.
set -euo pipefail
cd "$(dirname "$0")"
export JAVA_TOOL_OPTIONS=
T=tools
AAPT2=$T/prebuilt/linux/aapt2_64
ANDROID_JAR=$T/android.jar
APKSIGNER=$T/node_modules/@postar/apktool-node/lib/apksigner.jar
JAR2DEX=$T/dex2jar/dex-tools-v2.4/d2j-jar2dex.sh
PKG=app/burnbank2
VCODE=1
VNAME=2.0

rm -rf build && mkdir -p build/gen build/classes
python3 make_icons.py
python3 make_asset.py

$AAPT2 compile --dir android/res -o build/res.zip
$AAPT2 link -o build/base.apk \
  --manifest android/AndroidManifest.xml \
  -I "$ANDROID_JAR" \
  --java build/gen \
  -A android/assets \
  --min-sdk-version 24 --target-sdk-version 34 \
  --version-code $VCODE --version-name $VNAME \
  build/res.zip

javac --release 8 -Xlint:-options -g:none -cp "$ANDROID_JAR" -d build/classes \
  build/gen/$PKG/R.java android/src/$PKG/*.java
(cd build/classes && jar cf ../app.jar .)
chmod +x "$JAR2DEX" $T/dex2jar/dex-tools-v2.4/d2j_invoke.sh
"$JAR2DEX" build/app.jar -o build/classes.dex
python3 assemble.py build/base.apk build/classes.dex build/aligned.apk

# Signing key: generated once, kept in keys/ (never inside the APK). A fresh key means v2 cannot install over v1 by accident.
if [ ! -f keys/burnbank2.jks ]; then
  mkdir -p keys
  PASS=$(head -c 24 /dev/urandom | base64 | tr -d '/+=' | head -c 20)
  echo -n "$PASS" > keys/password.txt
  keytool -genkeypair -alias burnbank2 -keyalg RSA -keysize 2048 -validity 10950 \
    -dname "CN=Burnbank" -keystore keys/burnbank2.jks -storepass "$PASS" -keypass "$PASS" >/dev/null 2>&1
fi
PASS=$(cat keys/password.txt)
java -jar "$APKSIGNER" sign --ks keys/burnbank2.jks --ks-key-alias burnbank2 \
  --ks-pass "pass:$PASS" --key-pass "pass:$PASS" \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out Burnbank.apk build/aligned.apk
java -jar "$APKSIGNER" verify --verbose --print-certs Burnbank.apk
ls -la Burnbank.apk
