#!/usr/bin/env python

import platform
import os
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

import tools.scripts.system as system

project_directory = os.getcwd()

platform_arg = "android"
configuration_arg = sys.argv[1]
architecture_arg = sys.argv[2]
precision_arg = sys.argv[3]

# ===============================================
# Visual Studio 2022 specific stuff
if architecture_arg == "android": # TODO: Add different android processor platforms? E.g. android_arm32, android_arm64, android_x86_32, android_x86_64?
    architecture_arg = "arm64"

# ===============================================
# Install
return_code = 0
if configuration_arg == "editor":
    return_code = subprocess.call(f"adb install godot/bin/android_editor_builds/android_editor-android-dev.apk", shell=True)
else:
    return_code = subprocess.call(f"adb install bin/android/android_editor_game.apk", shell=True)
    
if return_code != 0:
    sys.exit(f"Error: adb install {platform_arg} {configuration_arg} {architecture_arg} {precision_arg} failed")

# ===============================================
# Run
if configuration_arg == "editor":
    return_code = subprocess.call(f"adb.exe shell monkey -p org.godotengine.editor.v4.dev 1", shell=True)
elif configuration_arg == "editor_game":
    return_code = subprocess.call(f"adb.exe shell monkey -p com.godotprojecttemplate.{system.lib_name}.editor_game 1", shell=True)
else:
    return_code = subprocess.call(f"adb.exe shell monkey -p com.godotprojecttemplate.{system.lib_name} 1", shell=True)

if return_code != 0:
    sys.exit(f"Error: adb.exe shell monkey -p {platform_arg} {configuration_arg} {architecture_arg} {precision_arg} failed")
