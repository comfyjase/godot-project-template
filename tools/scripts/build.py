#!/usr/bin/env python

import os
import platform
import shutil
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

# ===============================================
# Visual Studio 2022 specific stuff
if platform_arg == "Win32" or platform_arg == "x64":
    platform_arg = "windows"

# Visual Studio 2022 doesn't seem to have a separate setting for architecture, so it's bundled in with the platform.
# Have to parse it out separately in these scripts to get the correct one.
# E.g. windows_x86_64 -> x86_64
if architecture == "Win32":
    architecture = "x86_32"
elif architecture == "x64" or architecture == "linux":
    architecture = "x86_64"
elif architecture == "web":
    architecture = "wasm32"
    
using_wsl = (platform.system() == "Windows") and (platform_arg == "linux")

# ===============================================
# Build Godot
print("Step 1) Build Godot Engine", flush=True)
os.chdir("godot")

build_command = ""
if using_wsl:
    build_command = "wsl "

return_code = 0
if "production" in configuration:
    build_command += f"scons platform={platform_arg} target=editor arch={architecture} precision={precision} production=yes"
elif "profile" in configuration:
    build_command += f"scons platform={platform_arg} target=editor arch={architecture} precision={precision} production=yes debug_symbols=yes"
elif "template_release" in configuration:
    build_command += f"scons platform={platform_arg} target=editor arch={architecture} precision={precision}"
else:
    build_command += f"scons platform={platform_arg} target=editor arch={architecture} precision={precision} dev_build=yes dev_mode=yes"

# Removing dev_build/dev_mode from web editor because it doesn't compile (get emscripten errors...) and adding dlink_enabled
if platform_arg == "web":
    if configuration in ["editor", "editor_game", "template_debug"]:
        build_command = build_command.replace("dev_build=yes dev_mode=yes", "dlink_enabled=yes")
    else:
        build_command += " dlink_enabled=yes"
        
return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    print(f"Error: Failed to build godot for {platform_arg} {configuration} {architecture} {precision}")
    exit()

# ===============================================
# Generate C++ extension api files
print("Step 2) Generate C++ extension api files", flush=True)
os.chdir("bin")

godot_binary_file_name = ""
if precision == "single":
    godot_binary_file_name = f"godot.{platform_arg}.editor.dev.{architecture}"
elif precision == "double":
    godot_binary_file_name = f"godot.{platform_arg}.editor.dev.{precision}.{architecture}"

if platform_arg == "windows":
    godot_binary_file_name += ".exe"
elif platform_arg == "linux":
    godot_binary_file_name = godot_binary_file_name.replace("linux", "linuxbsd")
elif platform_arg == "macos":
    godot_binary_file_name += ".universal"
elif platform_arg == "web":
    godot_binary_file_name = godot_binary_file_name.replace("wasm32", "x86_64")
    if platform.system() == "Windows":
        godot_binary_file_name = godot_binary_file_name.replace("web", "windows") + ".exe"
    elif platform.system() == "Linux":
        godot_binary_file_name = godot_binary_file_name.replace("web", "linuxbsd")
    elif platform.system() == "Darwin":
        godot_binary_file_name = godot_binary_file_name.replace("web", "macos") + ".universal"

build_command = ""
if using_wsl:
    build_command = "wsl ./"
build_command += f"{godot_binary_file_name} --headless --dump-extension-api --dump-gdextension-interface"

return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    print(f"Error: Failed to generate C++ extension api files from {godot_binary_file_name}")
    exit()

try:
    shutil.copy(os.path.join(f"{os.getcwd()}", "extension_api.json"), os.path.join(f"{project_directory}", "godot-cpp", "gdextension", "extension_api.json"))
    shutil.copy(os.path.join(f"{os.getcwd()}", "gdextension_interface.h"), os.path.join(f"{project_directory}", "godot-cpp", "gdextension", "gdextension_interface.h"))
except IOError as e:
    print(f"Error: Failed to copy extension api files from godot/bin -> godot_cpp/gdextension/ {e}")
    exit()

# ===============================================
# Build Game
print("Step 3) Build Game", flush=True)
os.chdir("..")
os.chdir("..")

build_command = ""
if using_wsl:
    build_command = "wsl "
    
if configuration == "production":
    build_command += f"scons platform={platform_arg} target={configuration} arch={architecture} precision={precision} production=yes"
elif configuration == "profile":
    build_command += f"scons platform={platform_arg} target={configuration} arch={architecture} precision={precision} production=yes debug_symbols=yes"
elif configuration == "template_release":
    build_command += f"scons platform={platform_arg} target={configuration} arch={architecture} precision={precision}"
else:
    build_command += f"scons platform={platform_arg} target={configuration} arch={architecture} precision={precision} dev_build=yes dev_mode=yes"

if platform_arg == "web" and configuration in ["editor", "editor_game", "template_debug"]:
    build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")
    
return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    print(f"Error: Failed to build game for {platform_arg} {configuration} {architecture} {precision}")
    exit()

# ===============================================
# (Web Only) Zip Project
if platform_arg == "web" and configuration in ["editor", "editor_game"]:
    print("Step 4) Zip Game Project For Web Editor", flush=True)
    
    # Remove the old folder
    if os.path.isdir("game.zip"):
        shutil.rmtree("game.zip", True)

    # Make new zip folder
    shutil.make_archive("game", "zip", "game")
    