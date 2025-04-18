#!/usr/bin/env python

import os
import platform
import shutil
import subprocess
import sys

from glob import glob

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
elif architecture == "x64" or architecture == "linux":
    architecture = "x86_64"
elif architecture == "web":
    architecture = "wasm32"
elif architecture == "android": # TODO: Add different android processor platforms? E.g. android_arm32, android_arm64, android_x86_32, android_x86_64?
    architecture = "arm64"
    
using_wsl = (platform.system() == "Windows") and (platform_arg == "linux")

# ===============================================
# Build Godot
os.chdir("godot")

godot_configuration = configuration
if godot_configuration in ["profile", "production"]:
    godot_configuration = "template_release"
elif godot_configuration == "editor_game":
    godot_configuration = "template_debug"

build_command = ""
if using_wsl:
    build_command = "wsl "
    
if configuration == "production":
    build_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} production=yes"
elif configuration == "profile":
    build_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} production=yes debug_symbols=yes"
elif configuration == "template_release":
    build_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision}"
else:
    build_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} dev_build=yes dev_mode=yes"

if platform_arg == "web":
    if configuration in ["editor", "editor_game", "template_debug"]:
        build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")
    
    build_command += " dlink_enabled=yes threads=no"
    
    if os.path.isdir(f"bin/.web_zip"):
        shutil.rmtree(f"bin/.web_zip", True)
        
elif platform_arg == "android":
    build_command += " generate_apk=yes"

return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    print(f"Error: Failed to create godot export template for {platform_arg} {configuration} {architecture} {precision}")
    exit()

# ===============================================
# Rename Files
os.chdir("bin")

godot_files = []
if platform_arg == "web":    
    shutil.copytree(".web_zip", f"web_{configuration}", dirs_exist_ok=True)
    shutil.make_archive(f"web_{configuration}", "zip", f"web_{configuration}")
else:
    godot_files = glob(f"godot.{platform_arg}.{godot_configuration}.*")
    print(godot_files, flush=True)
    for file in godot_files:
        old_name = file
        new_name = file.replace("godot.", "").replace(f"{godot_configuration}", f"{configuration}")
        os.rename(old_name, new_name)
    