#!/usr/bin/env python

import os
import subprocess
import sys

from glob import glob

# Change to project directory if we are not already there
current_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{current_directory}", "game")):
    os.chdir("..")
    os.chdir("..")

platform = sys.argv[1]
configuration = sys.argv[2]
architecture = sys.argv[3]
precision = sys.argv[4]

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
# Build Godot
os.chdir("godot")

godot_configuration = configuration
if godot_configuration in ["profile", "production"]:
    godot_configuration = "template_release"
elif godot_configuration == "editor_game":
    godot_configuration = "editor"

return_code = 0
if configuration == "production":
    return_code = subprocess.call(f"scons platform={platform} target={godot_configuration} arch={architecture} precision={precision} production=yes", shell=True)
elif configuration == "profile":
    return_code = subprocess.call(f"scons platform={platform} target={godot_configuration} arch={architecture} precision={precision} production=yes debug_symbols=yes", shell=True)
elif configuration == "template_release":
    return_code = subprocess.call(f"scons platform={platform} target={godot_configuration} arch={architecture} precision={precision}", shell=True)
else:
    return_code = subprocess.call(f"scons platform={platform} target={godot_configuration} arch={architecture} precision={precision} dev_build=yes dev_mode=yes", shell=True)

if return_code != 0:
    print(f"Error: Failed to build godot for {platform} {configuration}")
    exit()

# ===============================================
# Rename Files
os.chdir("bin")

godot_files = glob(f"godot.{platform}.{godot_configuration}.*")
print(godot_files, flush=True)
for file in godot_files:
    old_name = file
    new_name = file.replace("godot.", "").replace(f"{godot_configuration}", f"{configuration}")
    os.rename(old_name, new_name)
