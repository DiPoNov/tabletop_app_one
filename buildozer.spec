[app]

# (str) Title of your application
title = Десятый Сталинский Удар

# (str) Package name
package.name = stalingame

# (str) Package domain (needed for android/ios packaging)
package.domain = org.wiseplat

# (str) Source code where the main.py live
source.dir = .

# (str) Main source file
source.main = main.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, docs, .github

# (str) Application version
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.0,kivymd,pillow,openssl,requests

# (str) Icon of the application
icon.filename = icon.png

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 23

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Java classes to add as activities to the manifest
# android.add_activities = com.example.ExampleActivity

# (bool) Indicate whether the screen should stay on
android.wakelock = False

# (str) The Android arch to build for
android.arch = arm64-v8a

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) Presplash background color
android.presplash_color = #FFFFFF

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use
p4a.branch = master

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

#
# Buildozer specific
#

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = .buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = bin
