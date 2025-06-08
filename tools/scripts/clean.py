#!/usr/bin/env python

import os
import platform
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from tools.scripts.system import *

# Change to project directory if we are not already there
current_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{current_directory}", "game")):
    os.chdir("..")
    os.chdir("..")

platform_arg = sys.argv[1]
configuration_arg = sys.argv[2]
architecture_arg = sys.argv[3]
precision_arg = sys.argv[4]
is_ci = False
if len(sys.argv) == 6:
    is_ci = sys.argv[5]
    
# ===============================================
# Visual Studio 2022 specific stuff
if platform_arg == "Win32" or platform_arg == "x64":
    platform_arg = "windows"

# Visual Studio 2022 doesn't seem to have a separate setting for architecture_arg, so it's bundled in with the platform.
# Have to parse it out separately in these scripts to get the correct one.
# E.g. windows_x86_64 -> x86_64
if architecture_arg == "Win32":
    architecture_arg = "x86_32"
elif architecture_arg == "x64" or architecture_arg == "linux":
    architecture_arg = "x86_64"
elif architecture_arg == "web":
    architecture_arg = "wasm32"
elif architecture_arg == "android": # TODO: Add different android processor platforms? E.g. android_arm32, android_arm64, android_x86_32, android_x86_64?
    architecture_arg = "arm64"
    
using_wsl = wsl_available and platform_arg == "linux"
    
# ===============================================
# Engine Clean

# Switch to True if you want to clean engine symbols too...
clean_engine = True

if clean_engine:
    print("=====================================", flush=True)
    print("Cleaning Godot Engine", flush=True)
    print("=====================================", flush=True)
    
    os.chdir("godot")
    
    building_editor_for_non_native_os = (platform_arg in ["web", "android"] and configuration_arg == "editor")
    
    # Assuming for windows/linux/mac that arch arg is what the user wants to build the engine with.
    godot_engine_architecture_arg = architecture_arg
    if not building_editor_for_non_native_os and platform_arg not in ["windows", "linux", "macos"]:
        godot_engine_architecture_arg = detect_arch()
    
    clean_command = ""
    if using_wsl:
        clean_command = "wsl "
    
    godot_platform = platform_arg
    building_editor_for_non_native_os = (godot_platform in ["web", "android"] and configuration_arg == "editor")
    
    # Always make sure there's some native os version of the godot editor for the next step
    # Generating the cpp bindings needs a godot binary file.
    if godot_platform not in ["windows", "linux", "macos"]:
        # Unless building the editor for web/android, then don't update godot_platform.
        if not building_editor_for_non_native_os:
            godot_platform = platform.system().lower()
            if godot_platform == "darwin":
                godot_platform = "macos"
            print(f"Building godot engine for native os {godot_platform} {godot_engine_architecture_arg}", flush=True)
        
    if configuration_arg == "production":
        clean_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg} production=yes"
    elif configuration_arg == "profile":
        clean_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg} production=yes debug_symbols=yes"
        if is_ci:   # engine debug symbols are too large for CI
            clean_command = clean_command.replace(" debug_symbols=yes", "")
    elif configuration_arg == "template_release":
        clean_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg}"
    else:
        clean_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg} dev_build=yes dev_mode=yes"
        if is_ci:   # Same as above...
            clean_command = clean_command.replace(" dev_build=yes dev_mode=yes", "")
    
    if is_ci:
        clean_command += " debug_symbols=no"
    if configuration_arg in ["editor", "editor_game", "template_debug"]:
        clean_command += " tests=yes"
    
    if platform_arg == "macos" or platform_arg == "ios":
        clean_command += " vulkan=yes"
    elif platform_arg == "web":
        if building_editor_for_non_native_os:
            clean_command += " dlink_enabled=yes threads=no"
    elif platform_arg == "android":
        if building_editor_for_non_native_os:
            clean_command += " generate_apk=yes"
    
    clean_command += " -c"
    print("Clean Command: " + clean_command, flush=True)
    return_code = subprocess.call(clean_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to clean godot for {platform_arg} editor {godot_engine_architecture_arg} {precision_arg}")

    os.chdir("..")
    
# ===============================================
# Project Clean
print("=====================================", flush=True)
print("Cleaning Game", flush=True)
print("=====================================", flush=True)

clean_command = ""
if using_wsl:
    clean_command = "wsl "

game_target = configuration_arg
if game_target == "editor_game" and platform_arg in ["web", "android"]:
    game_target = "template_debug"
    
game_architecture = architecture_arg
if platform_arg == "macos" and architecture_arg != "universal":
    game_architecture = "universal"
    
if game_target == "production":
    clean_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg} production=yes"
elif game_target == "profile":
    clean_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg} production=yes debug_symbols=yes"
elif game_target == "template_release":
    clean_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg}"
else:
    clean_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg} dev_build=yes dev_mode=yes"

if platform_arg == "macos":
    clean_command += " vulkan=yes"
elif platform_arg == "web":
    if game_target in ["editor", "editor_game", "template_debug"]:
        clean_command = clean_command.replace(" dev_build=yes dev_mode=yes", "")
    clean_command += " threads=no"
    
clean_command += " -c"
print(f"Command: {clean_command}", flush=True)
return_code = subprocess.call(clean_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to clean game for {platform_arg} {game_target} {game_architecture} {precision_arg}")
