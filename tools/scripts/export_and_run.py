#!/usr/bin/env python

import datetime
import platform
import os
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
# Export
os.chdir(os.path.join("tools", "scripts"))

return_code = subprocess.call(f"export.py {platform_arg} {configuration} {architecture} {precision}", shell=True)
if return_code != 0:
    sys.exit(f"Error: export.py {platform_arg} {configuration} {architecture} {precision} failed")

# ===============================================
# Run exported project
if platform_arg == "web":
    os.chdir(os.path.join("..", ".."))    
    return_code = subprocess.call(f"python godot/platform/web/serve.py --root ../../../bin/web", shell=True)
elif platform_arg == "android":
    return_code = subprocess.call(f"python android_install_and_run.py {configuration} {architecture} {precision}", shell=True)
    
if return_code != 0:
    sys.exit(f"Error: Failed to run project for {platform_arg} {configuration} {architecture} {precision}")
