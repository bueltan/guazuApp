[app]

# (str) Title of your application
title = GuazuApp

# (str) Package name
package.name = GuazuApp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts =

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,sqlalchemy,sqlite3,kivy==2.0.0,https://github.com/kivymd/KivyMD/archive/master.zip,pygments,sdl2_ttf==2.0.15,pillow, backoff==1.10.0,plyer==2.0.0,aiohttp==3.7.4, appdirs==1.4.3, async-timeout==3.0.1,attrs==20.3.0,certifi==2019.11.28, chardet==3.0.4,colorama==0.4.3,contextlib2==0.6.0, distlib==0.3.0,distro==1.4.0, docutils==0.17, gql==3.0.0a5, graphql-core==3.1.3, html5lib==1.0.1, idna==2.8,ipaddr==2.2.0,lockfile==0.12.2, msgpack==0.6.2, multidict==4.7.6, packaging==20.3, pep517==0.8.2,progress==1.5, pygments==2.8.1, pyparsing==2.4.6, pytoml==0.1.21, requests==2.25.1,retrying==1.3.3, six==1.14.0, typing-extensions==3.7.4.3,urllib3==1.25.8, webencodings==0.5.1, websockets==8.1, yarl==1.6.3

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait
# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0
# (string) Presplash background color (for new android toolchain)
android.presplash_color = #FFFFFF
# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 28
# (int) Minimum API your APK will support.
android.minapi = 21
# (str) Android NDK version to use
android.ndk = 19b
# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False
# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True
# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D
# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a
[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer
# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = ./bin
