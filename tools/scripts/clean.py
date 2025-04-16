#!/usr/bin/env python

import os
import platform
import subprocess
import sys

# Change to project directory if we are not already there
current_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{current_directory}", "game")):
    os.chdir("..")
    os.chdir("..")

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
elif architecture in ["x64", "linux", "macos"]:
    architecture = "x86_64"
elif architecture == "web":
    architecture = "wasm32"

using_wsl = (platform.system() == "Windows") and (platform_arg == "linux")

# ===============================================
# SCons Clean
godot_configuration = configuration
if godot_configuration in ["profile", "production"]:
    godot_configuration = "template_release"
elif godot_configuration == "editor_game":
    godot_configuration = "editor"
    
clean_command = ""
if using_wsl:
    clean_command = "wsl "
    
if configuration == "production":
    clean_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} production=yes -c"
elif configuration == "profile":
    clean_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} production=yes debug_symbols=yes -c"
elif configuration == "template_release":
    clean_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} -c"
else:
    clean_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} dev_build=yes dev_mode=yes -c"

if platform_arg == "web" and configuration in ["editor", "editor_game", "template_debug"]:
    clean_command = clean_command.replace(" dev_build=yes dev_mode=yes", "")

return_code = subprocess.call(clean_command, shell=True)
if return_code != 0:
    print(f"Error: Failed to clean project using scons for {platform_arg} {godot_configuration} {architecture} {precision}")
