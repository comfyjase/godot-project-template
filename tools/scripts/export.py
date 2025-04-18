#!/usr/bin/env python

import datetime
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

platform_arg = sys.argv[1]
configuration = sys.argv[2]
architecture = sys.argv[3]
precision = sys.argv[4]

# ===============================================
# Visual Studio 2022 specific stuff
if platform_arg == "Win32" or platform_arg == "x64":
    platform_arg = "windows"

if architecture == "Win32":
    architecture = "x86_32"
elif architecture == "x64" or architecture == "linux":
    architecture = "x86_64"
elif architecture == "web":
    architecture = "wasm32"
elif architecture == "android": # TODO: Add different android processor platforms? E.g. android_arm32, android_arm64, android_x86_32, android_x86_64?
    architecture = "arm64"
    
using_wsl = (platform.system() == "Windows") and (platform_arg == "linux")

# ===============================================
# Export
latest_git_commit_id = subprocess.check_output("git rev-parse --short HEAD").decode('ascii').strip()

os.chdir(os.path.join("godot", "bin"))

build_suffix = ""
if platform_arg == "windows":
    build_suffix = ".exe"
elif platform_arg == "macos":
    build_suffix = ".dmg"
elif platform_arg == "linux":
    build_suffix = ""
elif platform_arg == "web":
    build_suffix = ".html"
elif platform_arg == "android":
    build_suffix = ".apk"
elif platform_arg == "ios":
    build_suffix = ".zip"

build_file_name_and_type = ""

if platform_arg == "web":
    build_file_name_and_type = f"index{build_suffix}"
else:
    current_date_time_stamp = datetime.datetime.now()
    date_time_stamp = f"{current_date_time_stamp.year}{current_date_time_stamp.month}{current_date_time_stamp.day}_{current_date_time_stamp.hour}{current_date_time_stamp.minute}{current_date_time_stamp.second}"
    build_file_name_and_type = f"game_{platform_arg}_{configuration}_{date_time_stamp}_{latest_git_commit_id}{build_suffix}"
    print(f"Build Name: {build_file_name_and_type}", flush=True)

export_command_type = ""
if configuration in ["editor", "editor_game", "template_debug"]:
    export_command_type = "debug"
else:
    export_command_type = "release"

godot_binary_file_name = ""
if platform.system() == "Windows":
    godot_binary_file_name = f"godot.windows.editor.dev.x86_64.exe"
elif platform.system() == "Darwin":
    godot_binary_file_name = f"godot.macos.editor.dev.universal"
elif platform.system() == "Linux":
    godot_binary_file_name = f"godot.linuxbsd.editor.dev.x86_64"

if not os.path.exists(godot_binary_file_name):
    print(f"Error: godot editor {godot_binary_file_name} doesn't exist yet, please build the godot editor for your OS platform first before attempting to export.")
    exit()

export_command = f"{godot_binary_file_name} --path {os.path.join(project_directory, "game")} --headless --export-{export_command_type} \"{platform_arg} {configuration} {architecture} {precision}\" \"{os.path.join(project_directory, "bin", platform_arg, build_file_name_and_type)}\""
return_code = subprocess.call(export_command, shell=True)
if return_code != 0:
    print(f"Error: Failed to export game for {platform_arg} {configuration} {architecture} {precision} from godot binary {godot_binary_file_name}")
    exit()
    
print("Done")
