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
# SCons Clean
godot_configuration_arg = configuration_arg
if godot_configuration_arg in ["profile", "production"]:
    godot_configuration_arg = "template_release"
elif godot_configuration_arg == "editor_game":
    godot_configuration_arg = "editor"

clean_command = ""
if using_wsl:
    clean_command = "wsl "
    
# ===============================================
# Engine Clean

# Switch to True if you want to clean engine symbols too...
clean_engine = False

if clean_engine:
    os.chdir("godot")
        
    if configuration_arg == "production":
        clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} production=yes"
    elif configuration_arg == "profile":
        clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} production=yes debug_symbols=yes"
    elif configuration_arg == "template_release":
        clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg}"
    else:
        clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} dev_build=yes dev_mode=yes"
    
    if platform_arg == "macos":
        clean_command += " vulkan_sdk_path=$HOME/VulkanSDK"
        if platform.system() == "Linux":
            clean_command += " osxcross_sdk=darwin24.4"
    elif platform_arg == "web":
        if configuration_arg in ["editor", "editor_game", "template_debug"]:
            clean_command = clean_command.replace(" dev_build=yes dev_mode=yes", "")
        clean_command += " dlink_enabled=yes threads=no use_closure_compiler=yes"
        
    clean_command += " -c"
    return_code = subprocess.call(clean_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to clean engine using scons for {platform_arg} {godot_configuration_arg} {architecture_arg} {precision_arg}")
    
    os.chdir("..")
    
# ===============================================
# Project Clean
game_architecture = architecture_arg
if platform_arg == "macos" and architecture_arg != "universal":
    game_architecture = "universal"

if configuration_arg == "production":
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={game_architecture} precision={precision_arg} production=yes"
elif configuration_arg == "profile":
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={game_architecture} precision={precision_arg} production=yes debug_symbols=yes"
elif configuration_arg == "template_release":
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={game_architecture} precision={precision_arg}"
else:
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={game_architecture} precision={precision_arg} dev_build=yes dev_mode=yes"

if platform_arg == "macos":
    build_command += " vulkan_sdk_path=$HOME/VulkanSDK"
    if platform.system() == "Linux":
        build_command += " osxcross_sdk=darwin24.4"
elif platform_arg == "web":
    if configuration_arg in ["editor", "editor_game", "template_debug"]:
        clean_command = clean_command.replace(" dev_build=yes dev_mode=yes", "")
    clean_command += " threads=no use_closure_compiler=yes"

clean_command += " -c"
return_code = subprocess.call(clean_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to clean project using scons for {platform_arg} {godot_configuration_arg} {game_architecture} {precision_arg}")
