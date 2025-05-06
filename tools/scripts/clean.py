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

if architecture_arg == "Win32":
    architecture_arg = "x86_32"
elif architecture_arg in ["x64", "linux", "macos"]:
    architecture_arg = "x86_64"
elif architecture_arg == "web":
    architecture_arg = "wasm32"

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
    
if configuration_arg == "production":
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision_arg={precision_arg} production=yes -c"
elif configuration_arg == "profile":
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision_arg={precision_arg} production=yes debug_symbols=yes -c"
elif configuration_arg == "template_release":
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision_arg={precision_arg} -c"
else:
    clean_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision_arg={precision_arg} dev_build=yes dev_mode=yes -c"

if platform_arg == "web" and configuration_arg in ["editor", "editor_game", "template_debug"]:
    clean_command = clean_command.replace(" dev_build=yes dev_mode=yes", "")

return_code = subprocess.call(clean_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to clean project using scons for {platform_arg} {godot_configuration_arg} {architecture_arg} {precision_arg}")
