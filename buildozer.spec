[app]

# (str) Title of your application
title = Nova AI Asistan

# (str) Package name
package.name = novaai

# (str) Package domain (needed for android/ios packaging)
package.domain = com.novaai

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,ogg

# (str) Application versioning
version = 1.0.0

# Requirements (str)
requirements = python3,kivy==2.3.0,kivymd,requests,google-generativeai

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations (landscape, portrait and all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# Android permissions
android.permissions = INTERNET

# Android API level
android.api = 31

# (int) Minimum API level required
android.minapi = 21

# (str) Android entry point class
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.theme = @android:style/Theme.Material.NoActionBar.Fullscreen

# (list) Android architecture filters
android.archs = armeabi-v7a, arm64-v8a

# (bool) If True, the app will be debuggable
android.debug = False

# (str) Android logcat filter
android.logcat_filters = *:S

# (str) Android manifest placeholders
#android.manifest_placeholders = APP_NAME:Nova AI, APP_PACKAGE:com.novaai

# (bool) Copy application icon to the APK
android.copy_libs = True

# (bool) If True, the app will use the new Android build toolchain
android.new_archs = 1

# (bool) If True, the app will use the new Android build toolchain
android.accept_sdk_license = True

# (bool) If True, the app will use the new Android build toolchain
android.use_gradle = True
