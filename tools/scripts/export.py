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
is_ci = False
if len(sys.argv) == 6:
    is_ci = sys.argv[5]

# ===============================================
# Visual Studio 2022 specific stuff
if platform_arg == "Win32" or platform_arg == "x64":
    platform_arg = "windows"

if platform_arg == architecture:
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
    
library_suffix = ""
if platform_arg == "windows":
    library_suffix = ".dll"
elif platform_arg == "macos":
    library_suffix = ".dylib"
elif platform_arg == "linux":
    library_suffix = ".so"
elif platform_arg == "web":
    library_suffix = ".wasm"
elif platform_arg == "android":
    library_suffix = ".so"
elif platform_arg == "ios":
    library_suffix = ".so"

build_file_name_and_type = ""

if platform_arg == "web":
    build_file_name_and_type = f"index{build_suffix}"
elif platform_arg == "android" and configuration == "editor_game":
    build_file_name_and_type = f"android_{configuration}{build_suffix}"
else:
    current_date_time_stamp = datetime.datetime.now()
    date_time_stamp = f"{current_date_time_stamp.year}.{current_date_time_stamp.month}.{current_date_time_stamp.day}_{current_date_time_stamp.hour}.{current_date_time_stamp.minute}.{current_date_time_stamp.second}"
    build_file_name_and_type = f"game_{platform_arg}_{configuration}_{architecture}_{precision}_{date_time_stamp}_{latest_git_commit_id}{build_suffix}"
    print(f"Build Name: {build_file_name_and_type}", flush=True)

necessary_file_path = ""
export_command_type = ""
if configuration in ["editor", "editor_game", "template_debug"]:
    export_command_type = "debug"
    if platform_arg == "windows":
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"game.{platform_arg}.template_debug.{architecture}.dev{library_suffix}")
    else:
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"libgame.{platform_arg}.template_debug.{architecture}.dev{library_suffix}")
else:
    export_command_type = "release"
    if platform_arg == "windows":
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"game.{platform_arg}.template_release.{architecture}{library_suffix}")
    else:
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"libgame.{platform_arg}.template_release.{architecture}{library_suffix}")

if precision == "double":
    necessary_file_path = necessary_file_path.replace(f"{architecture}", f"{precision}.{architecture}")

if platform_arg == "web":
    necessary_file_path = necessary_file_path.replace(f"{architecture}", f"{architecture}.nothreads")

if configuration in ["editor", "editor_game", "template_debug"]:
    necessary_file_path = necessary_file_path.replace(".dev", "")

if not os.path.exists(necessary_file_path):
    sys.exit(f"Error: {necessary_file_path} file is missing, please build project for {platform_arg} template_{export_command_type} {architecture} {precision}")

godot_engine_architecture = ""
is_os_64_bit = sys.maxsize > 2**32
if is_os_64_bit:
    godot_engine_architecture = "x86_64"
else:
    godot_engine_architecture = "x86_32"

godot_binary_file_name = ""
if platform.system() == "Windows":
    godot_binary_file_name = f"godot.windows.editor.dev.{godot_engine_architecture}.exe"
elif platform.system() == "Darwin":
    godot_binary_file_name = f"godot.macos.editor.dev.{godot_engine_architecture}"
elif platform.system() == "Linux":
    godot_binary_file_name = f"godot.linuxbsd.editor.dev.{godot_engine_architecture}"

if configuration in ["template_release", "profile", "production"] or is_ci:
    godot_binary_file_name = godot_binary_file_name.replace(".dev", "")

if precision == "double":
    godot_binary_file_name = godot_binary_file_name.replace(f"{godot_engine_architecture}", f"{precision}.{godot_engine_architecture}")

if not os.path.exists(godot_binary_file_name):
    sys.exit(f"Error: godot editor {godot_binary_file_name} doesn't exist yet, please build the godot editor for your OS platform first before attempting to export.")

export_command = f"{godot_binary_file_name} --path \"{os.path.join(project_directory, "game")}\" --headless --export-{export_command_type} \"{platform_arg} {configuration} {architecture} {precision}\" \"{os.path.join(project_directory, "bin", platform_arg, build_file_name_and_type)}\" --verbose"
print(export_command, flush=True)
return_code = subprocess.call(export_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to export game for {platform_arg} {configuration} {architecture} {precision} from godot binary {godot_binary_file_name}")
    
print("Done")
