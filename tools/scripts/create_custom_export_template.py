#!/usr/bin/env python

import os
import platform
import shutil
import subprocess
import sys

from glob import glob

# Change to project directory if we are not already there
project_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{project_directory}", "game")):
    os.chdir("..")
    os.chdir("..")

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

if architecture == platform_arg:
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
    if is_ci:
        build_command = build_command.replace(" debug_symbols=yes", "")
elif configuration == "template_release":
    build_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision}"
else:
    build_command += f"scons platform={platform_arg} target={godot_configuration} arch={architecture} precision={precision} dev_build=yes dev_mode=yes"
    if is_ci:
        build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")

if is_ci:
    build_command += " debug_symbols=no tests=yes"

if platform_arg == "web":
    if configuration in ["editor", "editor_game", "template_debug"]:
        build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")
        if os.path.isdir(f"bin/.web_zip"):
            shutil.rmtree(f"bin/.web_zip", True)
    else:
        if os.path.isdir(f"bin/web_{configuration}.zip"):
            shutil.rmtree(f"bin/web_{configuration}.zip", True)
            
    build_command += " dlink_enabled=yes threads=no"
        
elif platform_arg == "android":
    build_command += " generate_apk=yes"

print("Create Export Template Command: " + build_command)
return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    print(f"Error: Failed to create godot export template for {platform_arg} {configuration} {architecture} {precision}")
    exit()

# ===============================================
# Rename Files
os.chdir("bin")

template_suffix = ""
if platform_arg == "windows":
    template_suffix = ".exe"
elif platform_arg == "macos":
    template_suffix = ".dmg"
elif platform_arg == "linux":
    template_suffix = ""
elif platform_arg == "web":
    template_suffix = ".zip"
elif platform_arg == "android":
    template_suffix = ".apk"
elif platform_arg == "ios":
    template_suffix = ".zip"

godot_files = []
if platform_arg == "web":
    if configuration in ["editor", "editor_game"]:
        shutil.copytree(".web_zip", f"web_{configuration}", dirs_exist_ok=True)
        shutil.make_archive(f"web_{configuration}", "zip", f"web_{configuration}")
    else:
        os.rename(f"godot.web.{godot_configuration}.{architecture}.nothreads.dlink{template_suffix}", f"web.{configuration}.{architecture}{template_suffix}")
elif platform_arg == "android":
    if configuration in ["editor", "editor_game", "template_debug"]:
        if os.path.isfile(f"android_dev{template_suffix}"):
            os.rename(f"android_dev{template_suffix}", f"android.{configuration}.{architecture}{template_suffix}")
    else:
        if os.path.isfile(f"android_release{template_suffix}"):
            os.rename(f"android_release{template_suffix}", f"android.{configuration}.{architecture}{template_suffix}")
else:
    godot_files = glob(f"godot.{platform_arg}.{godot_configuration}.*")
    print(godot_files, flush=True)
    for file in godot_files:
        old_name = file
        new_name = file.replace("godot.", "").replace(f"{godot_configuration}", f"{configuration}")
        os.rename(old_name, new_name)

# ===============================================
# Update export_presets.cfg with this template
os.chdir(os.path.join("..", "..", "game"))

# TODO: Check what is needed for web/android here...
with open("export_presets.cfg", "r") as export_presets_read:
    export_template_file_path = os.path.join(project_directory, "godot", "bin", f"{platform_arg}.{configuration}.{architecture}{template_suffix}")
    export_template_file_path = os.path.normpath(export_template_file_path).replace("\\", "/")
    all_lines=export_presets_read.readlines()
    
    found_export = False
    for index, line in enumerate(all_lines):
        if line == f"name=\"{platform_arg} {configuration} {architecture} {precision}\"\n":
            found_export = True
            print(f"Found export preset for {platform_arg} {configuration} {architecture} {precision}", flush=True)
            
        if found_export:
            if configuration in ["editor", "editor_game", "template_debug"]:
                if "custom_template/debug=" in line:
                    all_lines[index] = f"custom_template/debug=\"{export_template_file_path}\"\n"
                    print(f"Updating template debug to {export_template_file_path}", flush=True)
                    break
            else:
                if "custom_template/release=" in line:
                    all_lines[index] = f"custom_template/release=\"{export_template_file_path}\"\n"
                    print(f"Updating template release to {export_template_file_path}", flush=True)
                    break

    with open("export_presets.cfg", "w") as export_presets_write:
        export_presets_write.writelines(all_lines)
