[app]
title = BalsamMobile
package.name = balsam
package.domain = org.awab

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1

requirements = python3,kivy==2.1.0,kivymd,arabic_reshaper,python-bidi,pillow

orientation = portrait

android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# مهم جداً
android.api = 33
android.minapi = 21

# إضافات مهمة للاستقرار
android.ndk = 25b
android.sdk = 33

# تحسين البناء
log_level = 2
