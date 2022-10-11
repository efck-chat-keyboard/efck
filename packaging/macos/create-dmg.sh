#!/bin/sh
set -eux

# Depends on create-dmg, such as:
# $ brew install create-dmg


cd "$(dirname "$0")/../.."
DIST="dist"
ICON="$(find "$DIST" -name '*.icns' | head -n1)"
APP="$(find "$DIST" -type d -name '*.app' -maxdepth 1)"
APP_NAME="$(basename "$APP" .app)"
DMG_ROOT="$DIST/dmg"
TARGET="$DIST/$APP_NAME.dmg"

mkdir -p "$DMG_ROOT" && trap "rm -r '$DMG_ROOT'" EXIT
cp -R "$APP" "$DMG_ROOT"
rm -f "$TARGET"

create-dmg \
    --volname "$APP_NAME" \
    --volicon "$ICON" \
    --background "$(dirname "$0")/dmg-bg.png" \
    --icon "$APP_NAME.app" 150 150 \
    --app-drop-link 490 150 \
    --window-size 640 330 \
    --window-pos 200 200 \
    --icon-size 128 \
    "$TARGET" \
    "$DMG_ROOT"
