#!/usr/bin/env python

import os
import platform
import shutil
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

project_directory = os.getcwd()

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

# Visual Studio 2022 doesn't seem to have a separate setting for architecture_arg, so it's bundled in with the platform.
# Have to parse it out separately in these scripts to get the correct one.
# E.g. windows_x86_64 -> x86_64
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
# Run Unit Tests
print("=====================================", flush=True)
print("Run Engine Unit Tests", flush=True)
print("=====================================", flush=True)

os.chdir("godot")

godot_engine_architecture_arg = architecture_arg
if platform_arg not in ["windows", "linux", "macos"]:
    godot_engine_architecture_arg = detect_arch()

godot_binary_file_name = ""
if platform.system() == "Windows":
    if platform_arg == "linux":
        godot_binary_file_name = f"godot.linuxbsd.editor.dev.{godot_engine_architecture_arg}"
    else:
        godot_binary_file_name = f"godot.windows.editor.dev.{godot_engine_architecture_arg}.exe"
elif platform.system() == "Linux":
    godot_binary_file_name = f"godot.linuxbsd.editor.dev.{godot_engine_architecture_arg}"
elif platform.system() == "Darwin":
    godot_binary_file_name = f"godot.macos.editor.dev.{godot_engine_architecture_arg}"

if configuration_arg in ["template_release", "profile", "production"] or is_ci:
    godot_binary_file_name = godot_binary_file_name.replace(".dev", "")

if precision_arg == "double":
    godot_binary_file_name = godot_binary_file_name.replace(f"{godot_engine_architecture_arg}", f"{precision_arg}.{godot_engine_architecture_arg}")

run_unit_test_command = ""
if using_wsl:
    run_unit_test_command = "wsl ./"
elif platform.system() == "Linux" or platform.system() == "Darwin":
    subprocess.call(f"chmod +x bin/{godot_binary_file_name}", shell=True)
    run_unit_test_command += "./"
run_unit_test_command += f"\"bin/{godot_binary_file_name}\" --headless --test"

print(run_unit_test_command, flush=True)
return_code = subprocess.call(run_unit_test_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed unit tests, see output for details.")

# ===============================================
# Build Game
print("=====================================", flush=True)
print("Run Game Unit Tests", flush=True)
print("=====================================", flush=True)

os.chdir("..")

run_unit_test_command = f"\"godot/bin/{godot_binary_file_name}\" --path \"game\" --headless --game-test"
print(run_unit_test_command, flush=True)
return_code = subprocess.call(run_unit_test_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed game unit tests, see output for details.")

print("Done")
