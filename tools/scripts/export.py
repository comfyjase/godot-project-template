#!/usr/bin/env python

import datetime
import os
import subprocess
import sys

# Change to project directory if we are not already there
current_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{current_directory}", "game")):
    os.chdir("..")
    os.chdir("..")

project_directory = os.getcwd()

platform = sys.argv[1]          # e.g. windows/mac/linux
configuration = sys.argv[2]
target = sys.argv[3]            # e.g. android/ios

# ===============================================
# Visual Studio 2022 specific stuff
if platform == "Win32" or platform == "x64":
    platform = "windows"

if architecture == "Win32":
    architecture = "x86_32"
elif architecture == "x64":
    architecture = "x86_64"

using_wsl = "wsl" in configuration
if using_wsl:
    if architecture == "x86_32":
        print(f"Error: Running 32 bit app with WSL 64 bit is unsupported, please choose x64 instead of x86 in the platform dropdown")
        exit()
    platform = "linux"
    configuration = configuration.replace("wsl_", "")

# ===============================================
# Export
latest_git_commit_id = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

os.chdir(os.path.join("godot", "bin"))

build_suffix = ""
if target == "windows":
    build_suffix = ".exe"
elif target = "macos":
    build_suffix = ".dmg"
elif target == "linux":
    build_suffix = ""   
elif target == "web":
    build_suffix = ".zip"
elif target = "android":
    build_suffix = ".apk"
elif target = "ios":
    build_suffix = ".zip"

current_date_time_stamp = datetime.datetime.now()
date_time_stamp = f"{current_date_time_stamp.year}{current_date_time_stamp.month}{current_date_time_stamp.day}_{current_date_time_stamp.hour}{current_date_time_stamp.minute}{current_date_time_stamp.second}"
build_file_name_and_type = f"game_{target}_{configuration}_{date_time_stamp}_{latest_git_commit_id}{build_suffix}"
print(f"Build Name: {build_file_name_and_type}", flush=True)

export_command_type = "debug"
if configuration == "template_debug":
    export_command_type = "debug"
    if not os.path.exists(os.path.join(f"{project_directory}", "game", "bin", f"{target}", f"libgame.{target}.template_debug.dev.*")):
        print(f"Error: libgame.{target}.template_debug.dev.* files are missing, please build project for {target} {configuration}")
        exit()
else:
    export_command_type = "release"
    if not os.path.exists(os.path.join(f"{project_directory}", "game", "bin", f"{target}", f"libgame.{target}.template_release.*")):
        print(f"Error: libgame.{target}.template_release.* files are missing, please build project for {target} {configuration}")
        exit()

godot_binary_file_name = ""
if platform == "windows":
    godot_binary_file_name = f"godot.{platform}.editor.dev.x86_64.exe"
elif platform == "macos":
    godot_binary_file_name = f"godot.macos.editor.dev.universal"
elif platform == "linux":
    godot_binary_file_name = f"godot.linux.editor.dev.TODO"

return_code = subprocess.call(f"{godot_binary_file_name} --path {os.path.join({project_directory}, "game")} --headless --export-{export_command_type} \"{target} {configuration}\" \"{os.path.join({project_directory}, "bin", {target}, {build_file_name_and_type})}\"", shell=True)
print(f"Done ")
