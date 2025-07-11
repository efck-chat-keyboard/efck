#!/bin/sh
set -eux

# This script creates a portable ZIP archive for the Windows version of EFCK.
# It assumes that PyInstaller has already been run and the application
# is built in the dist/efck-chat-keyboard directory.

APP_NAME="efck-chat-keyboard"
DIST_DIR="dist"
TARGET_ZIP_FILE="${APP_NAME}-portable-win64.zip"

cd "$DIST_DIR"
rm -vf "$TARGET_ZIP_FILE"

# Check if the source directory exists
if [ ! -d "$APP_NAME" ]; then
    echo "Error: Source directory $DIST_DIR/$APP_NAME does not exist."
    echo "Please run PyInstaller first (e.g., pyinstaller packaging/pyinstaller.spec from project root)."
    exit 1
fi >&2

# Create the ZIP archive.
# Change directory to the parent of $APP_NAME (i.e., $DIST_DIR)
# so that the archive contains $APP_NAME as the root folder.
# This way, when the user extracts, they get a single folder.
zip -r "$TARGET_ZIP_FILE" "$APP_NAME"

echo "$DIST_DIR/$TARGET_ZIP_FILE"
