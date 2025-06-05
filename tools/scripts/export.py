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
    build_suffix = ".ipa"
    
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
    build_file_name_and_type = f"game{build_suffix}"
print(f"Build Name: {build_file_name_and_type}", flush=True)

godot_engine_architecture_arg = architecture_arg
if platform_arg not in ["windows", "linux", "macos"]:
    godot_engine_architecture_arg = detect_arch()

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

necessary_file_path = ""
export_command_type = ""
if configuration_arg in ["editor", "editor_game", "template_debug"]:
    export_command_type = "debug"
    if platform_arg == "windows":
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"game.{platform_arg}.template_debug.{architecture_arg}.dev{library_suffix}")
    else:
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"libgame.{platform_arg}.template_debug.{architecture_arg}.dev{library_suffix}")
else:
    export_command_type = "release"
    if platform_arg == "windows":
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"game.{platform_arg}.template_release.{architecture_arg}{library_suffix}")
    else:
        necessary_file_path = os.path.join(f"{project_directory}", "game", "bin", f"{platform_arg}", f"libgame.{platform_arg}.template_release.{architecture_arg}{library_suffix}")

imgui_file_path = os.path.join(f"{project_directory}", "game", "addons", "imgui-godot", "bin", f"libimgui-godot-native.{platform_arg}.{export_command_type}.{architecture_arg}{library_suffix}")

if precision_arg == "double":
    necessary_file_path = necessary_file_path.replace(f"{architecture_arg}", f"{precision_arg}.{architecture_arg}")
    imgui_file_path = imgui_file_path.replace(f"{export_command_type}", f"{export_command_type}.{precision_arg}")
    
if platform_arg == "web":
    necessary_file_path = necessary_file_path.replace(f"{architecture_arg}", f"{architecture_arg}.nothreads")
elif platform_arg == "macos":
    necessary_file_path = necessary_file_path.replace(f".{architecture_arg}", "")
    imgui_file_path = imgui_file_path.replace(f"{architecture_arg}{library_suffix}", "framework")

if configuration_arg in ["editor", "editor_game", "template_debug"]:
    necessary_file_path = necessary_file_path.replace(".dev", "")

if platform_arg == "android" and platform.system() == "Windows":
    android_binary_made_on_windows_file_path = necessary_file_path.replace("libgame.", "game.").replace("\\", "/")
    if not os.path.exists(android_binary_made_on_windows_file_path) and not os.path.exists(necessary_file_path):
        sys.exit(f"{android_binary_made_on_windows_file_path} or {necessary_file_path} don't exist. Has build.py created editor_game custom export template correctly?")
    
    if os.path.exists(android_binary_made_on_windows_file_path):
        os.replace(android_binary_made_on_windows_file_path, necessary_file_path)
    
if not os.path.exists(necessary_file_path):
    print("Available binary files:", flush=True)
    print_files(os.path.dirname(os.path.abspath(necessary_file_path)))
    sys.exit(f"Error: {necessary_file_path} file is missing, please build project for {platform_arg} template_{export_command_type} {architecture_arg} {precision_arg}")
if (platform_arg not in ["web", "android", "ios"]) and (architecture_arg not in ["x86_32", "arm64", "arm32", "rv64"]):
    if not os.path.exists(imgui_file_path):
        imgui_godot_binary_folder_name = os.path.dirname(os.path.abspath(imgui_file_path))
        print(f"imgui-godot binary files: {imgui_godot_binary_folder_name}: ", flush=True)
        print_files(imgui_godot_binary_folder_name)
        sys.exit(f"Error: {imgui_file_path} file is missing, please check the game/addons/imgui-godot/bin folder for relevant binary files and make sure permissions are granted {export_command_type} {platform_arg} {configuration_arg} {architecture_arg} {precision_arg}")
    
if native_platform == "linux" or native_platform == "macos":
    print(f"Called chmod +xr {necessary_file_path}", flush=True)
    subprocess.call(f"chmod +xr {necessary_file_path}", shell=True)
    if (platform_arg not in ["web", "android", "ios"]) and (architecture_arg not in ["x86_32", "arm64", "arm32", "rv64"]):
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
                if platform_arg in line:
                    new_line = re.sub('\"(.+?)\"', f"\"res://bin/{platform_arg}/{os.path.basename(necessary_file_path)}\"", line, flags=re.DOTALL)
                    all_lines[index] = new_line
                
    with open(f"{gdextension_file_path}", "w") as gdextension_file_write:
        gdextension_file_write.writelines(all_lines)

# (CI Only) Update GDExtension File
if is_ci:
    game_gdextension_file_path = os.path.join(project_path, "bin", "game.gdextension").replace("\\", "/")
    update_gdextension_file(game_gdextension_file_path)

    # Android CI only, import project first so we know .godot folder exists
    if platform_arg == "android" and configuration_arg != "template_debug":
        # Check for generated keystore file
        release_keystore_file_path = os.path.join(project_directory, "release.keystore")
        if not os.path.exists(release_keystore_file_path):
            print("Project directory files:", flush=True)
            print_files(project_directory)
            sys.exit(f"Error: {release_keystore_file_path} doesn't exist under {project_directory}. Is it located somewhere else?")
            
        import_command = ""
        if using_wsl:
            import_command += "wsl ./"
        elif native_platform == "linux" or native_platform == "macos":
            import_command += "./"
        import_command += f"{godot_binary_file_name} --path \"{project_path}\" --headless --import"
        print("=====================================", flush=True)
        print("Importing Game", flush=True)
        print("=====================================", flush=True)
        print(import_command, flush=True)
        return_code = subprocess.call(import_command, shell=True)
        if return_code != 0:
            sys.exit(f"Error: Failed to import game for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg} from godot binary {godot_binary_file_name}")
        
        # Update export credentials with keystore file information
        export_credentials_file_path = f"{project_path}/.godot/export_credentials.cfg"
        export_godot_preset_tag = ""
        export_godot_preset_tag_options = ""
        all_lines = []
        with open(f"{project_path}/export_presets.cfg", "r") as export_presets_read:
            all_lines=export_presets_read.readlines()
            
            for index, line in enumerate(all_lines):
                if line == f"name=\"{platform_arg} {configuration_arg} {architecture_arg} {precision_arg}\"\n":
                    export_godot_preset_tag = all_lines[index - 2]
                    export_godot_preset_tag_options = export_godot_preset_tag.replace("]", ".options]")
                    break
        
        if os.path.exists(export_credentials_file_path):
            sys.exit(f"Error: {export_credentials_file_path} already exists, you need to modify it instead of just writing to it.")
        else:
            with open(export_credentials_file_path, "w") as export_credentials_write:
                print(f"Created {export_credentials_file_path}", flush=True)
                
                export_credentials_write.write(export_godot_preset_tag + "\n")
                export_credentials_write.write("\n")
                export_credentials_write.write("script_encryption_key=\"\"\n")
                export_credentials_write.write("\n")
                export_credentials_write.write(export_godot_preset_tag_options + "\n")
                export_credentials_write.write("\n")
                export_credentials_write.write("keystore/debug=\"\"\n")
                export_credentials_write.write("keystore/debug_user=\"\"\n")
                export_credentials_write.write("keystore/debug_password=\"\"\n")
                export_credentials_write.write(f"keystore/release=\"{release_keystore_file_path}\"\n")
                export_credentials_write.write(f"keystore/release_user=\"$ANDROID_KEYSTORE_ALIAS\"\n")
                export_credentials_write.write(f"keystore/release_password=\"$ANDROID_KEYSTORE_PASSWORD\"\n")
    elif platform_arg == "windows":
        app_data_file_path = subprocess.check_output("echo %APPDATA%", shell=True).decode('ascii').strip().replace("\\", "/")
        godot_editor_settings_file_path = f"{app_data_file_path}/Godot/editor_settings-4.4.tres"
        
        import_command = f"{godot_binary_file_name} --path \"{project_path}\" --headless --import"
        print("=====================================", flush=True)
        print("Importing Game", flush=True)
        print("=====================================", flush=True)
        print(import_command, flush=True)
        return_code = subprocess.call(import_command, shell=True)
        if return_code != 0:
            sys.exit(f"Error: Failed to import game for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg} from godot binary {godot_binary_file_name}")
        
        if not os.path.exists(godot_editor_settings_file_path):
            print_files(f"{app_data_file_path}/Godot")
            sys.exit(f"Error: Godot editor settings file {godot_editor_settings_file_path} does not exist under {app_data_file_path}/Godot/. Does project need to be imported first or is {app_data_file_path} not expanding correctly?")
        
        rcedit_file_path = f"{project_directory}/thirdparty/rcedit/rcedit_x64.exe".replace("\\", "/")
        if architecture_arg == "x86_32":
            rcedit_file_path = rcedit_file_path.replace("rcedit_x64", "rcedit_x32")
            
        all_lines = []
        with open(godot_editor_settings_file_path, "r") as editor_settings_file_read:
            all_lines = editor_settings_file_read.readlines()
            for index, line in enumerate(all_lines):
                if "export/windows/rcedit" in line:
                    all_lines[index] = f"export/windows/rcedit = \"{rcedit_file_path}\"\n"
                    print(f"Updated editor settings rcedit file path to {rcedit_file_path}", flush=True)
                
        with open(godot_editor_settings_file_path, "w") as editor_settings_file_write:
            editor_settings_file_write.writelines(all_lines)
            
# Export Game
export_command += f"{godot_binary_file_name} --path \"{project_path}\" --headless --export-{export_command_type} \"{platform_arg} {configuration_arg} {architecture_arg} {precision_arg}\" \"{build_output_path}\" --verbose"
print("=====================================", flush=True)
print("Exporting Game", flush=True)
print("=====================================", flush=True)
print(export_command, flush=True)
return_code = subprocess.call(export_command, shell=True)
if not os.path.exists(build_output_path):
    print("Available godot binary files:", flush=True)
    print_files()
    print("Available game binary files:", flush=True)
    print_files(os.path.dirname(os.path.abspath(necessary_file_path)))
    print_files(os.path.join(project_directory, "bin", platform_arg))
    with open(f"{project_path}/export_presets.cfg", "r") as export_presets_read:
        all_lines=export_presets_read.readlines()
        print("export_presets.cfg:", flush=True)
        for index, line in enumerate(all_lines):
            if f"name=\"{platform_arg}" in line:
                print(line, flush=True)
            elif ("custom_template/debug" in line and "custom_template/debug=\"\"" not in line):
                print(line, flush=True)
            elif ("custom_template/release" in line and "custom_template/release=\"\"" not in line):
                print(line, flush=True)

    sys.exit(f"Error: Failed to export game for {platform_arg} {configuration_arg} {architecture_arg} {precision_arg} from godot binary {godot_binary_file_name}")

print("Done")
