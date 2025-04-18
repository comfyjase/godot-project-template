#!/usr/bin/env python

import platform
import os
import subprocess
import sys

# Change to project directory if we are not already there
current_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{current_directory}", "game")):
    os.chdir("..")
    os.chdir("..")

project_directory = os.getcwd()

platform_arg = "android"
configuration = sys.argv[1]
architecture = sys.argv[2]
precision = sys.argv[3]

# ===============================================
# Visual Studio 2022 specific stuff
if architecture == "android": # TODO: Add different android processor platforms? E.g. android_arm32, android_arm64, android_x86_32, android_x86_64?
    architecture = "arm64"

# ===============================================
# Install
return_code = 0
if configuration == "editor":
    return_code = subprocess.call(f"adb install godot/bin/android_editor_builds/android_editor-android-dev.apk", shell=True)
else:
    return_code = subprocess.call(f"adb install bin/android/android_editor_game.apk", shell=True)
    
if return_code != 0:
    print(f"Error: adb install {platform_arg} {configuration} {architecture} {precision} failed")
    exit()

# ===============================================
# Run
if configuration == "editor":
    return_code = subprocess.call(f"adb.exe shell monkey -p org.godotengine.editor.v4.dev 1", shell=True)
else:
    # TODO: What is the package name for the game library???
    return_code = subprocess.call(f"adb.exe shell monkey -p com.example.game 1", shell=True)

if return_code != 0:
    print(f"Error: adb.exe shell monkey -p {platform_arg} {configuration} {architecture} {precision} failed")
    exit()
