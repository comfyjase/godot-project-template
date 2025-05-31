#!/usr/bin/env python

import os
import platform
import shutil
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from glob import glob
from tools.scripts.system import *

# Change to project directory if we are not already there
project_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{project_directory}", "game")):
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

if architecture_arg == platform_arg:
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
# Build Godot
os.chdir("godot")

print("=====================================", flush=True)
print("Creating Custom Export Template", flush=True)
print("=====================================", flush=True)

godot_configuration_arg = configuration_arg
if godot_configuration_arg in ["profile", "production"]:
    godot_configuration_arg = "template_release"
elif godot_configuration_arg == "editor_game":
    godot_configuration_arg = "template_debug"

build_command = ""
if using_wsl:
    build_command = "wsl "
    
if configuration_arg == "production":
    build_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} production=yes"
elif configuration_arg == "profile":
    build_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} production=yes debug_symbols=yes"
    if is_ci:
        build_command = build_command.replace(" debug_symbols=yes", "")
elif configuration_arg == "template_release":
    build_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg}"
else:
    build_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} dev_build=yes dev_mode=yes"
    if is_ci:
        build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")

if is_ci:
    build_command += " debug_symbols=no"
if configuration_arg == "template_debug":
    build_command += " tests=yes"
    
if platform_arg == "macos":
    if is_ci:
        build_command += " vulkan=yes"
    elif platform.system() == "Linux":
        build_command += " vulkan_sdk_path=$HOME/VulkanSDK"
        if platform.system() == "Linux":
            build_command += " osxcross_sdk=darwin24.4"        
    build_command += " generate_bundle=yes"
elif platform_arg == "web":
    if configuration_arg in ["editor", "editor_game", "template_debug"]:
        build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")
        if os.path.isdir(f"bin/.web_zip"):
            shutil.rmtree(f"bin/.web_zip", True)
    else:
        if os.path.isdir(f"bin/web_{configuration_arg}.zip"):
            shutil.rmtree(f"bin/web_{configuration_arg}.zip", True)
            
    build_command += " dlink_enabled=yes threads=no"
    if is_ci:
        build_command += " lto=none"
elif platform_arg == "android":
    build_command += " generate_apk=yes"

print(build_command, flush=True)
return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to create godot export template for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg}")

# ===============================================
# Rename Files
os.chdir("bin")

template_suffix = ""
if platform_arg == "windows":
    template_suffix = ".exe"
elif platform_arg == "macos":
    template_suffix = ".zip"
elif platform_arg == "linux":
    template_suffix = ""
elif platform_arg == "web":
    template_suffix = ".zip"
elif platform_arg == "android":
    template_suffix = ".apk"
elif platform_arg == "ios":
    template_suffix = ".zip"

godot_files = []
suffix = f"{configuration_arg}.{architecture_arg}{template_suffix}"
if precision_arg == "double":
    suffix = suffix.replace(f"{architecture_arg}", f"{precision_arg}.{architecture_arg}")
if platform_arg == "web":
    if configuration_arg in ["editor", "editor_game"]:
        shutil.copytree(".web_zip", f"web_{configuration_arg}", dirs_exist_ok=True)
        shutil.make_archive(f"web_{configuration_arg}", "zip", f"web_{configuration_arg}")
    else:
        old_name = f"godot.web.{godot_configuration_arg}.{architecture_arg}.nothreads.dlink{template_suffix}"
        if precision_arg == "double":
            old_name = old_name.replace(f"{architecture_arg}", f"{precision_arg}.{architecture_arg}")
        new_name = f"web.{suffix}"
        os.rename(f"{old_name}", f"{new_name}")
elif platform_arg == "android":
    old_name = f"android_dev{template_suffix}"
    if (configuration_arg in ["editor", "editor_game", "template_debug"]):
        if is_ci:  
            old_name = f"android_debug{template_suffix}"
    else:
        old_name = f"android_release{template_suffix}"
    
    if os.path.isfile(old_name):
        print(f"Renaming {old_name} to android.{suffix}", flush=True)
        os.rename(old_name, f"android.{suffix}")
    else:
        print(f"{old_name} custom export template file not found, here are the available files: ", flush=True)
        print_files()
elif platform_arg == "macos":
    old_name = f"godot_macos{template_suffix}"
    new_name = f"macos.{suffix}"
    
    if (configuration_arg in ["editor", "editor_game", "template_debug"]) and not is_ci:
        old_name = old_name.replace("macos", "macos_dev")
        if precision_arg == "double":
            old_name = old_name.replace("macos_dev", "macos_dev_double")
    
    if precision_arg == "double":
        old_name = old_name.replace("macos", "macos_double")
        
    if os.path.isfile(f"{old_name}"):
        os.rename(f"{old_name}", f"{new_name}")
    else:
        print_files()
else:
    godot_platform_name = platform_arg
    if platform_arg == "linux":
        godot_platform_name = "linuxbsd"
    godot_files = glob(f"godot.{godot_platform_name}.{godot_configuration_arg}.*")
    for file in godot_files:
        old_name = file
        new_name = file.replace("godot.", "").replace(f"{godot_configuration_arg}", f"{configuration_arg}")
        os.rename(old_name, new_name)

# ===============================================
# Update export_presets.cfg with this template
os.chdir(os.path.join("..", "..", "game"))

# TODO: Check what is needed for web/android here...
with open("export_presets.cfg", "r") as export_presets_read:
    godot_platform_name = platform_arg
    if platform_arg == "linux":
        godot_platform_name = "linuxbsd"
    export_template_file_path = os.path.join(project_directory, "godot", "bin", f"{godot_platform_name}.{suffix}")
    export_template_file_path = os.path.normpath(export_template_file_path).replace("\\", "/")
    if using_wsl:
        export_template_file_path = "/mnt/" + export_template_file_path.replace(":", "").lower()
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        export_template_file_path = export_template_file_path.lower()
        print(f"Called chmod +x {export_template_file_path}", flush=True)
        subprocess.call(f"chmod +x {export_template_file_path}", shell=True)
    all_lines=export_presets_read.readlines()
    
    found_export = False
    for index, line in enumerate(all_lines):
        if line == f"name=\"{platform_arg} {configuration_arg} {architecture_arg} {precision_arg}\"\n":
            found_export = True
            print(f"Found export preset for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg}", flush=True)
            
        if found_export:
            if "custom_template/debug=" in line:
                all_lines[index] = f"custom_template/debug=\"{export_template_file_path}\"\n"
                print(f"Updating template debug to {export_template_file_path}", flush=True)
            elif "custom_template/release=" in line:
                all_lines[index] = f"custom_template/release=\"{export_template_file_path}\"\n"
                print(f"Updating template release to {export_template_file_path}", flush=True)
                break

    with open("export_presets.cfg", "w") as export_presets_write:
        export_presets_write.writelines(all_lines)
