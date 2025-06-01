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
    
using_wsl = wsl_available and (platform_arg == "linux" or platform_arg == "macos")

# ===============================================
# Build Godot
os.chdir("godot")

build_engine = (configuration_arg in ["editor", "editor_game"] or is_ci)
if build_engine:
    print("=====================================", flush=True)
    print("Build Godot Engine", flush=True)
    print("=====================================", flush=True)
    
    build_command = ""
    if using_wsl:
        build_command = "wsl "
    
    godot_platform = platform_arg
    godot_architecture = architecture_arg
    # For CI, need to make sure there's some native os version of the godot editor for the next step
    # Generating the cpp bindings needs a godot binary file.
    if is_ci:
        if godot_platform not in ["windows", "linux", "macos"]:
            godot_platform = platform.system().lower()
            if godot_platform == "windows" or godot_platform == "linux" or godot_platform == "darwin":
                godot_architecture = "x86_64"
            if godot_platform == "darwin":
                godot_platform = "macos"
            print(f"Building godot engine for native os {godot_platform} {godot_architecture}", flush=True)
    
    if configuration_arg == "production":
        build_command += f"scons platform={godot_platform} target=editor arch={godot_architecture} precision={precision_arg} production=yes"
    elif configuration_arg == "profile":
        build_command += f"scons platform={godot_platform} target=editor arch={godot_architecture} precision={precision_arg} production=yes debug_symbols=yes"
        if is_ci:   # engine debug symbols are too large for CI
            build_command = build_command.replace(" debug_symbols=yes", "")
    elif configuration_arg == "template_release":
        build_command += f"scons platform={godot_platform} target=editor arch={godot_architecture} precision={precision_arg}"
    else:
        build_command += f"scons platform={godot_platform} target=editor arch={godot_architecture} precision={precision_arg} dev_build=yes dev_mode=yes"
        if is_ci:   # Same as above...
            build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")

    if is_ci:
        build_command += " debug_symbols=no"
    
    if configuration_arg == "template_debug":
        build_command += " tests=yes"
    
    if platform_arg == "macos" or platform_arg == "ios":
        if is_ci:
            build_command += " vulkan=yes"
        elif platform.system() == "Linux":
            build_command += " vulkan_sdk_path=$HOME/VulkanSDK osxcross_sdk=darwin24.4"
    # Removing dev_build/dev_mode from web editor because it doesn't compile (get emscripten errors...) and adding dlink_enabled
    elif platform_arg == "web":
        if not is_ci:
            if configuration_arg in ["editor", "editor_game", "template_debug"]:
                build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")
            
            build_command += " dlink_enabled=yes threads=no"
    elif platform_arg == "android":
        if not is_ci:
            build_command += " generate_apk=yes"
        
    print("Build Command: " + build_command, flush=True)
    return_code = subprocess.call(build_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to build godot for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg}")
    
    if platform_arg == "web" and configuration_arg in ["editor", "editor_game"]:
        print(os.getcwd(), flush=True)
        os.chdir(os.path.join("bin", ".web_zip"))
        
        godot_html_editor_file_name = "godot.editor.html"
        if os.path.isfile(godot_html_editor_file_name):
            shutil.copyfile(godot_html_editor_file_name, "index.html")
            
        os.chdir(os.path.join("..", ".."))

# ===============================================
# Generate C++ extension api files
print("=====================================", flush=True)
print("Generate C++ extension api files", flush=True)
print("=====================================", flush=True)
os.chdir("bin")

print(f"Detected System Platform: {platform.system()}", flush=True)

godot_engine_architecture_arg = ""
if is_os_64_bit:
    godot_engine_architecture_arg = "x86_64"
else:
    godot_engine_architecture_arg = "x86_32"

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

build_command = ""
if using_wsl:
    build_command = "wsl ./"
if platform.system() == "Linux" or platform.system() == "Darwin":
    print(f"Called chmod +x {godot_binary_file_name}", flush=True)
    subprocess.call(f"chmod +x {godot_binary_file_name}", shell=True)
    build_command += "./"
build_command += f"{godot_binary_file_name} --headless --dump-extension-api --dump-gdextension-interface"

return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to generate C++ extension api files from {godot_binary_file_name}")

try:
    shutil.copy(os.path.join(f"{os.getcwd()}", "extension_api.json"), os.path.join(f"{project_directory}", "godot-cpp", "gdextension", "extension_api.json"))
    shutil.copy(os.path.join(f"{os.getcwd()}", "gdextension_interface.h"), os.path.join(f"{project_directory}", "godot-cpp", "gdextension", "gdextension_interface.h"))
except IOError as e:
    sys.exit(f"Error: Failed to copy extension api files from godot/bin -> godot_cpp/gdextension/ {e}")

# ===============================================
# Build Game
print("=====================================", flush=True)
print("Build Game", flush=True)
print("=====================================", flush=True)
os.chdir("..")
os.chdir("..")

build_command = ""
if using_wsl:
    build_command = "wsl "
game_architecture = architecture_arg
if platform_arg == "macos" and architecture_arg != "universal":
    game_architecture = "universal"
    
if configuration_arg == "production":
    build_command += f"scons platform={platform_arg} target={configuration_arg} arch={game_architecture} precision={precision_arg} production=yes"
elif configuration_arg == "profile":
    build_command += f"scons platform={platform_arg} target={configuration_arg} arch={game_architecture} precision={precision_arg} production=yes debug_symbols=yes"
elif configuration_arg == "template_release":
    build_command += f"scons platform={platform_arg} target={configuration_arg} arch={game_architecture} precision={precision_arg}"
else:
    build_command += f"scons platform={platform_arg} target={configuration_arg} arch={game_architecture} precision={precision_arg} dev_build=yes dev_mode=yes"

if platform_arg == "macos":
    if is_ci:
        build_command += " vulkan=yes"
    elif platform.system() == "Linux" or using_wsl:
        build_command += " vulkan_sdk_path=$HOME/VulkanSDK osxcross_sdk=darwin24.4"
elif platform_arg == "web":
    if configuration_arg in ["editor", "editor_game", "template_debug"]:
        build_command = build_command.replace(" dev_build=yes dev_mode=yes", "")
    build_command += " threads=no"
    
print(f"Command: {build_command}", flush=True)
return_code = subprocess.call(build_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to build game for {platform_arg} {configuration_arg} {game_architecture} {precision_arg}")

# ===============================================
# (Web Editor Only) Zip Project
if platform_arg == "web" and configuration_arg == "editor":
    print("=====================================", flush=True)
    print("Zip Game Project For Web Editor", flush=True)
    print("=====================================", flush=True)
    
    # Remove the old folder
    if os.path.isdir("game.zip"):
        shutil.rmtree("game.zip", True)

    # Make new zip folder
    shutil.make_archive("game", "zip", "game")
    
# ==============================================
# (iOS Only) Convert
if platform_arg == "ios":
    game_binary_file_name = f"libgame.ios.{configuration_arg}.{architecture_arg}.dylib"
    game_xcframework_file_name = f"libgame.ios.{configuration_arg}.xcframework"
    
    #godot_cpp_binary_file_name = f"libgodot-cpp.ios.{configuration_arg}.{architecture_arg}.dylib"
    #godot_cpp_xcframework_file_name = f"libgodot-cpp.ios.{configuration_arg}.xcframework"
    
    if precision_arg == "double":
        game_xcframework_file_name = game_xcframework_file_name.replace(configuration_arg, f"{configuration_arg}.{precision_arg}")
    
    ios_xcodebuild_command = f"xcodebuild -create-xcframework -library game/bin/{game_binary_file_name} -output game/bin/{game_xcframework_file_name}"
    print(f"iOS xcode build command: {ios_xcodebuild_command}", flush=True)
    return_code = subprocess.call(ios_xcodebuild_command, shell=True)
    if return_code != 0:
        sys.exit("Error: iOS xcode build command failed for the game project")
    
    #ios_xcodebuild_command = f"xcodebuild -create-xcframework -library godot-cpp/bin/{godot_cpp_binary_file_name} -output godot-cpp/bin/{godot_cpp_xcframework_file_name}"
    #print(f"iOS xcode build command: {ios_xcodebuild_command}", flush=True)
    #return_code = subprocess.call(ios_xcodebuild_command, shell=True)
    #if return_code != 0:
    #    sys.exit("Error: iOS xcode build command failed for the godot-cpp project")
