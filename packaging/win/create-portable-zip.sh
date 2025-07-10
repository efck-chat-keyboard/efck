#!/bin/sh
set -eux

# This script creates a portable ZIP archive for the Windows version of EFCK.
# It assumes that PyInstaller has already been run and the application
# is built in the dist/efck-chat-keyboard directory.

# Navigate to the project root
cd "$(dirname "$0")/../../"

APP_NAME="efck-chat-keyboard"
DIST_DIR="dist"
PORTABLE_DIR_SOURCE="$DIST_DIR/$APP_NAME" # This is the folder created by PyInstaller's COLLECT
TARGET_ZIP_FILE_BASENAME="${APP_NAME}-portable-win"
TARGET_ZIP_FILE="$DIST_DIR/${TARGET_ZIP_FILE_BASENAME}.zip"

# Check if the source directory exists
if [ ! -d "$PORTABLE_DIR_SOURCE" ]; then
    echo "Error: Source directory $PORTABLE_DIR_SOURCE does not exist."
    echo "Please run PyInstaller first (e.g., pyinstaller packaging/pyinstaller.spec from project root)."
    exit 1
fi

echo "Source directory: $(pwd)/$PORTABLE_DIR_SOURCE"
echo "Target ZIP file: $(pwd)/$TARGET_ZIP_FILE"

# Remove old zip file if it exists
rm -f "$TARGET_ZIP_FILE"

# Create the ZIP archive.
# Change directory to the parent of $APP_NAME (i.e., $DIST_DIR)
# so that the archive contains $APP_NAME as the root folder.
# This way, when the user extracts, they get a single folder.
(cd "$DIST_DIR" && zip -r "${TARGET_ZIP_FILE_BASENAME}.zip" "$APP_NAME" -x "*/.DS_Store" "*/__MACOSX")

# To create a zip where contents of $PORTABLE_DIR_SOURCE are at the root of the zip:
# (cd "$PORTABLE_DIR_SOURCE" && zip -r "../${TARGET_ZIP_FILE_BASENAME}.zip" . -x ".DS_Store" "__MACOSX")


echo "Successfully created portable ZIP: $TARGET_ZIP_FILE"
