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

user_platform = sys.argv[1]
configuration = sys.argv[2]
architecture = sys.argv[3]
precision = sys.argv[4]

# ===============================================
# Visual Studio 2022 specific stuff
if user_platform == "Win32" or user_platform == "x64":
    user_platform = "windows"

# Visual Studio 2022 doesn't seem to have a separate setting for architecture, so it's bundled in with the platform.
# Have to parse it out separately in these scripts to get the correct one.
# E.g. windows_x86_64 -> x86_64
if architecture == "Win32":
    architecture = "x86_32"
elif architecture == "x64" or architecture == "linux":
    architecture = "x86_64"

using_wsl = (platform.system() == "Windows") and (user_platform == "linux")

# ===============================================
# Build Godot
print("Step 1) Build Godot Engine", flush=True)
os.chdir("godot")

build_command = ""
if using_wsl:
    build_command = "wsl "

return_code = 0
if "production" in configuration:
    build_command += f"scons platform={user_platform} target=editor arch={architecture} precision={precision} production=yes"
    return_code = subprocess.call(build_command, shell=True)
elif "profile" in configuration:
    build_command += f"scons platform={user_platform} target=editor arch={architecture} precision={precision} production=yes debug_symbols=yes"
    return_code = subprocess.call(build_command, shell=True)
elif "template_release" in configuration:
    build_command += f"scons platform={user_platform} target=editor arch={architecture} precision={precision}"
    return_code = subprocess.call(build_command, shell=True)
else:
    build_command += f"scons platform={user_platform} target=editor arch={architecture} precision={precision} dev_build=yes dev_mode=yes"
    return_code = subprocess.call(build_command, shell=True)

if return_code != 0:
    print(f"Error: Failed to build godot for {user_platform} {configuration} {architecture} {precision}")
    exit()

# ===============================================
# Generate C++ extension api files
print("Step 2) Generate C++ extension api files", flush=True)
os.chdir("bin")

godot_binary_file_name = ""
if precision == "single":
    godot_binary_file_name = f"godot.{user_platform}.editor.dev.{architecture}"
elif precision == "double":
    godot_binary_file_name = f"godot.{user_platform}.editor.dev.{precision}.{architecture}"

if user_platform == "windows":
    godot_binary_file_name += ".exe"
elif user_platform == "linux":
    godot_binary_file_name = godot_binary_file_name.replace("linux", "linuxbsd")

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
    build_command += f"scons platform={user_platform} target={configuration} arch={architecture} precision={precision} production=yes"
    return_code = subprocess.call(build_command, shell=True)
elif configuration == "profile":
    build_command += f"scons platform={user_platform} target={configuration} arch={architecture} precision={precision} production=yes debug_symbols=yes"
    return_code = subprocess.call(build_command, shell=True)
elif configuration == "template_release":
    build_command += f"scons platform={user_platform} target={configuration} arch={architecture} precision={precision}"
    return_code = subprocess.call(build_command, shell=True)
else:
    build_command += f"scons platform={user_platform} target={configuration} arch={architecture} precision={precision} dev_build=yes dev_mode=yes"
    return_code = subprocess.call(build_command, shell=True)

if return_code != 0:
    print(f"Error: Failed to build game for {user_platform} {configuration} {architecture} {precision}")
    exit()
