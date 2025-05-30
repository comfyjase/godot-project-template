#!/usr/bin/env python

import datetime
import platform
import os
import re
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

if platform_arg == architecture_arg:
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
# Export
git_command = ""
if using_wsl:
    git_command = "wsl "
git_command += "git rev-parse --short HEAD"
latest_git_commit_id = subprocess.check_output(git_command, shell=True).decode('ascii').strip()

os.chdir(os.path.join("godot", "bin"))

build_suffix = ""
if platform_arg == "windows":
    build_suffix = ".exe"
elif platform_arg == "macos":
    build_suffix = ".zip"
elif platform_arg == "linux":
    build_suffix = ""
elif platform_arg == "web":
    build_suffix = ".html"
elif platform_arg == "android":
    build_suffix = ".apk"
elif platform_arg == "ios":
    build_suffix = ".zip"
    
library_suffix = ""
if platform_arg == "windows":
    library_suffix = ".dll"
elif platform_arg == "macos":
    library_suffix = ".dylib"
elif platform_arg == "linux":
    library_suffix = ".so"
elif platform_arg == "web":
    library_suffix = ".wasm"
elif platform_arg == "android":
    library_suffix = ".so"
elif platform_arg == "ios":
    library_suffix = ".dylib"

native_platform = platform.system().lower()
if native_platform == "darwin":
    native_platform = "macos"
native_library_suffix = ""
if native_platform == "windows":
    native_library_suffix = ".dll"
elif native_platform == "linux":
    native_library_suffix = ".so"
elif native_platform == "macos":
    native_library_suffix = ".dylib"

build_file_name_and_type = ""
if platform_arg == "web":
    build_file_name_and_type = f"index{build_suffix}"
elif platform_arg == "android" and configuration_arg == "editor_game":
    build_file_name_and_type = f"android_{configuration_arg}{build_suffix}"
else:
    date_time_stamp = datetime.datetime.strftime(datetime.datetime.now(), '%m%d%Y_%H%M%S')
    build_file_name_and_type = f"game_{platform_arg}_{configuration_arg}_{architecture_arg}_{precision_arg}_{date_time_stamp}_{latest_git_commit_id}{build_suffix}"
    print(f"Build Name: {build_file_name_and_type}", flush=True)

godot_engine_architecture_arg = ""
if is_os_64_bit:
    godot_engine_architecture_arg = "x86_64"
else:
    godot_engine_architecture_arg = "x86_32"

godot_binary_file_name = ""
if native_platform == "windows":
    if using_wsl:
        godot_binary_file_name = f"godot.linuxbsd.editor.dev.{godot_engine_architecture_arg}"
    else:
        godot_binary_file_name = f"godot.windows.editor.dev.{godot_engine_architecture_arg}.exe"
elif native_platform == "macos":
    godot_binary_file_name = f"godot.macos.editor.dev.{godot_engine_architecture_arg}"
elif native_platform == "linux":
    godot_binary_file_name = f"godot.linuxbsd.editor.dev.{godot_engine_architecture_arg}"

if configuration_arg in ["template_release", "profile", "production"] or is_ci:
    godot_binary_file_name = godot_binary_file_name.replace(".dev", "")

if precision_arg == "double":
    godot_binary_file_name = godot_binary_file_name.replace(f"{godot_engine_architecture_arg}", f"{precision_arg}.{godot_engine_architecture_arg}")

if not os.path.exists(godot_binary_file_name):
    sys.exit(f"Error: godot editor {godot_binary_file_name} doesn't exist yet, please build the godot editor for your OS platform first before attempting to export.")

native_file_path = ""
necessary_file_path = ""
export_command_type = ""
if configuration_arg in ["editor", "editor_game", "template_debug"]:
    export_command_type = "debug"
    
    if native_platform == "windows":
        native_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{native_platform}", f"game.{native_platform}.editor.{godot_engine_architecture_arg}.dev{native_library_suffix}")
    else:
        native_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{native_platform}", f"libgame.{native_platform}.editor.{godot_engine_architecture_arg}.dev{native_library_suffix}")
        
    if platform_arg == "windows":
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"game.{platform_arg}.template_debug.{architecture_arg}.dev{library_suffix}")
    else:
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"libgame.{platform_arg}.template_debug.{architecture_arg}.dev{library_suffix}")
else:
    export_command_type = "release"
    
    if native_platform == "windows":
        native_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{native_platform}", f"game.{native_platform}.editor.{godot_engine_architecture_arg}{native_library_suffix}")
    else:
        native_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{native_platform}", f"libgame.{native_platform}.editor.{godot_engine_architecture_arg}{native_library_suffix}")
    
    if platform_arg == "windows":
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"game.{platform_arg}.template_release.{architecture_arg}{library_suffix}")
    else:
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"libgame.{platform_arg}.template_release.{architecture_arg}{library_suffix}")

imgui_file_path = os.path.join(f"{project_directory}", "game", "addons", "imgui-godot", "bin", f"libimgui-godot-native.{platform_arg}.{export_command_type}.{architecture_arg}{library_suffix}")

if precision_arg == "double":
    necessary_file_path = necessary_file_path.replace(f"{architecture_arg}", f"{precision_arg}.{architecture_arg}")
    native_file_path = native_file_path.replace(f"{architecture_arg}", f"{precision_arg}.{architecture_arg}")
    imgui_file_path = imgui_file_path.replace(f"{export_command_type}", f"{export_command_type}.{precision_arg}")
    
if platform_arg == "web":
    necessary_file_path = necessary_file_path.replace(f"{architecture_arg}", f"{architecture_arg}.nothreads")
elif platform_arg == "macos":
    native_file_path = native_file_path.replace(f".{architecture_arg}", "")
    necessary_file_path = necessary_file_path.replace(f".{architecture_arg}", "")
    imgui_file_path = imgui_file_path.replace(f"{architecture_arg}{library_suffix}", "framework")

if configuration_arg in ["editor", "editor_game", "template_debug"]:
    native_file_path = native_file_path.replace(".dev", "")
    necessary_file_path = necessary_file_path.replace(".dev", "")

if not os.path.exists(necessary_file_path):
    sys.exit(f"Error: {necessary_file_path} file is missing, please build project for {platform_arg} template_{export_command_type} {architecture_arg} {precision_arg}")
if platform_arg in ["web", "android", "ios"]:
    if not os.path.exists(native_file_path):
        print(f"Available binary files: ", flush=True)
        print_files(os.path.dirname(os.path.abspath(native_file_path)))
        sys.exit(f"Error {native_file_path} file is missing, make sure the Build Project step has built the game project for editor configuration.")
else:
    if not os.path.exists(imgui_file_path):
        imgui_godot_binary_folder_name = os.path.dirname(os.path.abspath(imgui_file_path))
        print(f"imgui-godot binary files: {imgui_godot_binary_folder_name}: ", flush=True)
        print_files(imgui_godot_binary_folder_name)
        sys.exit(f"Error: {imgui_file_path} file is missing, please check the game/addons/imgui-godot/bin folder for relevant binary files and make sure permissions are granted {export_command_type} {platform_arg} {configuration_arg} {architecture_arg} {precision_arg}")
    
if native_platform == "linux" or native_platform == "macos":
    print(f"Called chmod +xr {necessary_file_path}", flush=True)
    subprocess.call(f"chmod +xr {necessary_file_path}", shell=True)
    if platform_arg not in ["web", "android", "ios"]:
        print(f"Called chmod +xr {imgui_file_path}", flush=True)
        subprocess.call(f"chmod +xr {imgui_file_path}", shell=True)

project_path = f"{os.path.join(project_directory, "game")}".replace("\\", "/")
build_output_path = f"{os.path.join(project_directory, "bin", platform_arg, build_file_name_and_type)}".replace("\\", "/")
export_command = ""
if using_wsl:
    export_command += "wsl ./"
    project_path = "/mnt/" + project_path.replace(":", "").lower()
    build_output_path = "/mnt/" + build_output_path.replace(":", "").lower()
elif native_platform == "linux" or native_platform == "macos":
    export_command += "./"
    project_path = project_path.lower()
    build_output_path = build_output_path.lower()

def update_gdextension_file(gdextension_file_path):
    all_lines = []
    with open(f"{gdextension_file_path}", "r") as gdextension_file_read:
        all_lines = gdextension_file_read.readlines()
        
        found_libraries_section = False
        for index, line in enumerate(all_lines):
            if "libraries" in line:
                found_libraries_section = True
                continue
                
            if found_libraries_section:
                if native_platform in line:
                    new_line = re.sub('\"(.+?)\"', f"\"res://bin/{native_platform}/{os.path.basename(native_file_path)}\"", line, flags=re.DOTALL)
                    all_lines[index] = new_line
                    continue
                if platform_arg in line:
                    new_line = re.sub('\"(.+?)\"', f"\"res://bin/{platform_arg}/{os.path.basename(necessary_file_path)}\"", line, flags=re.DOTALL)
                    all_lines[index] = new_line
                
    with open(f"{gdextension_file_path}", "w") as gdextension_file_write:
        gdextension_file_write.writelines(all_lines)

# (CI Only) Update GDExtension File
if is_ci:
    game_gdextension_file_path = os.path.join(project_path, "bin", "game.gdextension").replace("\\", "/")
    update_gdextension_file(game_gdextension_file_path)
        
# Export Game
export_command += f"{godot_binary_file_name} --path \"{project_path}\" --headless --export-{export_command_type} \"{platform_arg} {configuration_arg} {architecture_arg} {precision_arg}\" \"{build_output_path}\" --verbose"
print("Exporting Game", flush=True)
print(f"{export_command}", flush=True)
return_code = subprocess.call(export_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to export game for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg} from godot binary {godot_binary_file_name}")

print("Done")
