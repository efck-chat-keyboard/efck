#!/usr/bin/env bash
# MIT License
#
# Copyright (c) 2020 Paul Zabelin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Snatched from https://github.com/paulz/prepare-macos

set -eux

# Prepare GitHub runner

# Change Local name to avoid name clash causing alert
suffix=$RANDOM
UniqueComputerName="$GITHUB_WORKFLOW-$suffix"
sudo scutil --set LocalHostName "$UniqueComputerName"
sudo scutil --set ComputerName "$UniqueComputerName"

# Close Notification window
sudo killall -KILL UserNotificationCenter || true

# Do not disturb
defaults -currentHost write com.apple.notificationcenterui doNotDisturb -boolean true
defaults -currentHost write com.apple.notificationcenterui doNotDisturbDate -date "`date -u +\"%Y-%m-%d %H:%M:%S +0000\"`"
sudo killall NotificationCenter || true

# Disable firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Close Finder Windows using Apple Script
sudo osascript -e 'tell application "Finder" to close windows'

# Close all windows
sudo osascript -e 'tell application "System Events" to set quitapps to name of every application process whose visible is true and background only is false'
