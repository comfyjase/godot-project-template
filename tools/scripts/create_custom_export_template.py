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
if configuration_arg in ["editor", "editor_game", "template_debug"]:
    build_command += " tests=yes"
    
if platform_arg == "macos":
    if is_ci:
        build_command += " vulkan=yes"
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
elif platform_arg == "ios":
    build_command += " generate_bundle=yes"
    
if not is_ci:
    cache_path = project_directory.replace("\\", "/") + "/godot/.scons_cache"
    build_command += f" cache_path={cache_path}"
    
print(build_command, flush=True)
return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to build godot export template for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg}")

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
        shutil.copytree(".web_zip", f"web.{configuration_arg}.{architecture_arg}", dirs_exist_ok=True)
        shutil.make_archive(f"web.{configuration_arg}.{architecture_arg}", "zip", f"web.{configuration_arg}.{architecture_arg}")
    else:
        old_name = f"godot.web.{godot_configuration_arg}.{architecture_arg}.nothreads.dlink{template_suffix}"
        if precision_arg == "double":
            old_name = old_name.replace(f"{architecture_arg}", f"{precision_arg}.{architecture_arg}")
        new_name = f"web.{suffix}"
        os.replace(f"{old_name}", f"{new_name}")
elif platform_arg == "android":
    old_name = f"android_dev{template_suffix}"
    if (configuration_arg in ["editor", "editor_game", "template_debug"]):
        if is_ci:  
            old_name = f"android_debug{template_suffix}"
    else:
        old_name = f"android_release{template_suffix}"
    
    if os.path.isfile(old_name):
        print(f"Renaming {old_name} to android.{suffix}", flush=True)
        os.replace(old_name, f"android.{suffix}")
    else:
        print(f"{old_name} custom export template file not found, here are the available files: ", flush=True)
        print_files()
elif platform_arg == "macos" or platform_arg == "ios":
    platform_name_to_use = platform_arg
    
    old_name = f"godot_{platform_name_to_use}{template_suffix}"
    new_name = f"{platform_name_to_use}.{suffix}"
    
    if (configuration_arg in ["editor", "editor_game", "template_debug"]) and not is_ci:
        old_name = old_name.replace(f"{platform_name_to_use}", f"{platform_name_to_use}_dev")
        if precision_arg == "double":
            old_name = old_name.replace(f"{platform_name_to_use}_dev", f"{platform_name_to_use}_dev_double")
    
    if precision_arg == "double":
        old_name = old_name.replace(f"{platform_name_to_use}", f"{platform_name_to_use}_double")
        
    if os.path.isfile(f"{old_name}"):
        os.replace(f"{old_name}", f"{new_name}")
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
        os.replace(old_name, new_name)

# ===============================================
# Update export_presets.cfg with this template
os.chdir(os.path.join("..", "..", "game"))

godot_platform_name = platform_arg
if platform_arg == "linux":
    godot_platform_name = "linuxbsd"
export_template_file_path = os.path.join(project_directory, "godot", "bin", f"{godot_platform_name}.{suffix}")
export_template_file_path = os.path.normpath(export_template_file_path).replace("\\", "/")
if using_wsl:
    export_template_file_path = "/mnt/" + export_template_file_path.replace(":", "").lower()
elif platform.system() == "Linux" or platform.system() == "Darwin":
    export_template_file_path = export_template_file_path.lower()
    
if not os.path.exists(export_template_file_path):
    print("Available files:", flush=True)
    print_files()
    sys.exit(f"Error: Failed to create {export_template_file_path} for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg}")

if platform.system() == "Linux" or platform.system() == "Darwin":
    print(f"Called chmod a+rwx {export_template_file_path}", flush=True)
    subprocess.call(f"chmod a+rwx {export_template_file_path}", shell=True)

with open("export_presets.cfg", "r") as export_presets_read:
    all_lines=export_presets_read.readlines()
    
    found_export = False
    for index, line in enumerate(all_lines):
        if f"name=\"{platform_arg} {configuration_arg} {architecture_arg} {precision_arg}" in line:
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
