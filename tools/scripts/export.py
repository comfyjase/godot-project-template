#!/usr/bin/env python

import datetime
import platform
import os
import os.path
import re
import shutil
import subprocess
import sys
from pathlib import Path

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

import tools.scripts.system as system

system.parse_arguments()

# ===============================================
# Export
git_command = ""
if system.using_wsl:
    git_command = "wsl "
git_command += "git rev-parse --short HEAD"
latest_git_commit_id = subprocess.check_output(git_command, shell=True).decode('ascii').strip()

os.chdir(system.godot_bin_path)

build_suffix = ""
if system.platform_arg == "windows":
    build_suffix = ".exe"
elif system.platform_arg == "macos":
    build_suffix = ".zip"
elif system.platform_arg == "linux":
    build_suffix = ""
elif system.platform_arg == "web":
    build_suffix = ".html"
elif system.platform_arg == "android":
    build_suffix = ".aab"
elif system.platform_arg == "ios":
    build_suffix = ".ipa"
    
library_suffix = ""
if system.platform_arg == "windows":
    library_suffix = ".dll"
elif system.platform_arg == "macos":
    library_suffix = ".dylib"
elif system.platform_arg == "linux":
    library_suffix = ".so"
elif system.platform_arg == "web":
    library_suffix = ".wasm"
elif system.platform_arg == "android":
    library_suffix = ".so"
elif system.platform_arg == "ios":
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
if system.platform_arg == "web":
    build_file_name_and_type = f"index{build_suffix}"
elif system.platform_arg == "android" and system.configuration_arg == "editor_game":
    build_file_name_and_type = f"android_{system.configuration_arg}.apk"
else:
    build_file_name_and_type = f"{system.lib_name}{build_suffix}"
print(f"Build Name: {build_file_name_and_type}", flush=True)

necessary_file_path = ""
export_command_type = ""
if system.configuration_arg in ["editor", "editor_game", "template_debug"]:
    export_command_type = "debug"
    if system.platform_arg == "windows":
        necessary_file_path = os.path.join(system.project_dir_path, "bin", system.platform_arg, f"{system.lib_name}.{system.platform_arg}.template_debug.{system.architecture_arg}.dev{library_suffix}")
    else:
        necessary_file_path = os.path.join(system.project_dir_path, "bin", system.platform_arg, f"lib{system.lib_name}.{system.platform_arg}.template_debug.{system.architecture_arg}.dev{library_suffix}")
else:
    export_command_type = "release"
    if system.platform_arg == "windows":
        necessary_file_path = os.path.join(system.project_dir_path, "bin", system.platform_arg, f"{system.lib_name}.{system.platform_arg}.template_release.{system.architecture_arg}{library_suffix}")
    else:
        necessary_file_path = os.path.join(system.project_dir_path, "bin", system.platform_arg, f"lib{system.lib_name}.{system.platform_arg}.template_release.{system.architecture_arg}{library_suffix}")

imgui_file_path = os.path.join(system.project_dir_path, "addons", "imgui-godot", "bin", f"libimgui-godot-native.{system.platform_arg}.{export_command_type}.{system.architecture_arg}{library_suffix}")

if system.precision_arg == "double":
    necessary_file_path = necessary_file_path.replace(system.architecture_arg, f"{system.precision_arg}.{system.architecture_arg}")
    imgui_file_path = imgui_file_path.replace(export_command_type, f"{export_command_type}.{system.precision_arg}")
    
if system.platform_arg == "web":
    necessary_file_path = necessary_file_path.replace(system.architecture_arg, f"{system.architecture_arg}.nothreads")
elif system.platform_arg == "macos":
    necessary_file_path = necessary_file_path.replace(f".{system.architecture_arg}", "")
    imgui_file_path = imgui_file_path.replace(f"{system.architecture_arg}{library_suffix}", "framework")

if system.configuration_arg in ["editor", "editor_game", "template_debug"]:
    necessary_file_path = necessary_file_path.replace(".dev", "")

if system.platform_arg == "android" and platform.system() == "Windows":
    android_binary_made_on_windows_file_path = necessary_file_path.replace(f"lib{system.lib_name}.", f"{system.lib_name}.").replace("\\", "/")
    if not os.path.exists(android_binary_made_on_windows_file_path) and not os.path.exists(necessary_file_path):
        sys.exit(f"{android_binary_made_on_windows_file_path} or {necessary_file_path} don't exist. Has build.py created editor_game custom export template correctly?")
    
    if os.path.exists(android_binary_made_on_windows_file_path):
        os.replace(android_binary_made_on_windows_file_path, necessary_file_path)
    
if not os.path.exists(necessary_file_path):
    print("Available binary files:", flush=True)
    system.print_files(os.path.dirname(os.path.abspath(necessary_file_path)))
    sys.exit(f"Error: {necessary_file_path} file is missing, please build project for {system.platform_arg} template_{export_command_type} {system.architecture_arg} {system.precision_arg}")
if (system.platform_arg not in ["web", "android", "ios"]) and (system.architecture_arg not in ["x86_32", "arm64", "arm32", "rv64"]):
    if not os.path.exists(imgui_file_path):
        imgui_godot_binary_folder_name = os.path.dirname(os.path.abspath(imgui_file_path))
        print(f"imgui-godot binary files: {imgui_godot_binary_folder_name}: ", flush=True)
        system.print_files(imgui_godot_binary_folder_name)
        sys.exit(f"Error: {imgui_file_path} file is missing, please check the addons/imgui-godot/bin folder for relevant binary files and make sure permissions are granted {export_command_type} {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}")
    
if native_platform == "linux" or native_platform == "macos":
    print(f"Called chmod +xr {necessary_file_path}", flush=True)
    subprocess.call(f"chmod +xr {necessary_file_path}", shell=True)
    if (system.platform_arg not in ["web", "android", "ios"]) and (system.architecture_arg not in ["x86_32", "arm64", "arm32", "rv64"]):
        print(f"Called chmod +xr {imgui_file_path}", flush=True)
        subprocess.call(f"chmod +xr {imgui_file_path}", shell=True)

project_path = system.project_dir_path
build_output_path = f"{os.path.join(system.repo_dir_path, "bin", system.platform_arg, build_file_name_and_type)}".replace("\\", "/")
if system.using_wsl:
    project_path = "/mnt/" + project_path.replace(":", "").lower()
    build_output_path = "/mnt/" + build_output_path.replace(":", "").lower()
elif native_platform == "linux" or native_platform == "macos":
    project_path = project_path.lower()
    build_output_path = build_output_path.lower()

def update_gdextension_file(gdextension_file_path):
    all_lines = []
    
    gdextension_name = Path(gdextension_file_path).stem
    copy_gdextension_file_path = gdextension_file_path.replace(".gdextension", "_gdextension.copy").replace("\\", "/")
    shutil.copy(gdextension_file_path, copy_gdextension_file_path)

    gdextension_binary_file_path = necessary_file_path.replace(system.lib_name, gdextension_name)

    with open(f"{gdextension_file_path}", "r") as gdextension_file_read:
        all_lines = gdextension_file_read.readlines()
        
        found_libraries_section = False
        for index, line in enumerate(all_lines):
            if "libraries" in line:
                found_libraries_section = True
                continue
                
            if found_libraries_section:
                if system.platform_arg in line:
                    new_line = re.sub('\"(.+?)\"', f"\"res://bin/{system.platform_arg}/{os.path.basename(gdextension_binary_file_path)}\"", line, flags=re.DOTALL)
                    all_lines[index] = new_line
                
    with open(f"{gdextension_file_path}", "w") as gdextension_file_write:
        gdextension_file_write.writelines(all_lines)

def revert_file(path):
    if os.path.isfile(path):
        os.remove(path)

def revert_copy_file(copy_path, original_path):
    if os.path.isfile(copy_path):
        os.remove(original_path) # This was the temp version of the gdextension file, so remove it.
        os.rename(copy_path, original_path)

game_gdextension_file_path = os.path.join(system.project_dir_path, "bin", f"{system.lib_name}.gdextension").replace("\\", "/")
update_gdextension_file(game_gdextension_file_path)

for (i, plugin_name) in enumerate(system.project_plugins):
    plugin_dir = os.path.join(system.absolute_plugins_dir_path, plugin_name).replace("\\", "/")
    addons_dir = os.path.join(system.absolute_addons_dir_path, plugin_name).replace("\\", "/")
    
    plugin_gdextension_file_path = os.path.join(plugin_dir, f"{plugin_name}.gdextension").replace("\\", "/")
    update_gdextension_file(plugin_gdextension_file_path)
    
    # Move plugins to addons folder
    shutil.move(plugin_dir, addons_dir)

# Import the project first, to guarantee .godot folder is valid
print("=====================================", flush=True)
print("Importing Game", flush=True)
print("=====================================", flush=True)
print(system.get_godot_import_command(), flush=True)
return_code = subprocess.call(system.get_godot_import_command(), shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to import project for {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg} from godot binary {system.get_godot_binary_file_name_for_system()}")

export_credentials_file_path = f"{project_path}/.godot/export_credentials.cfg"
if system.platform_arg == "android" and system.configuration_arg in ["template_release", "profile", "production"]:
    # Check for generated keystore file
    release_keystore_file_path = os.path.join(system.repo_dir_path, "release.keystore").replace("\\", "/")
    if not os.path.exists(release_keystore_file_path):
        print("Project directory files:", flush=True)
        system.print_files(system.repo_dir_path)
        sys.exit(f"Error: {release_keystore_file_path} doesn't exist under {system.repo_dir_path}. Is it located somewhere else?")    
    
    # Update export credentials with keystore file information
    export_godot_preset_tag = ""
    export_godot_preset_tag_options = ""
    all_lines = []
    with open(system.project_export_presets_path, "r") as export_presets_read:
        all_lines=export_presets_read.readlines()
        
        for index, line in enumerate(all_lines):
            if line == f"name=\"{system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}\"\n":
                export_godot_preset_tag = all_lines[index - 2]
                export_godot_preset_tag_options = export_godot_preset_tag.replace("]", ".options]")
                break

    if os.path.exists(export_credentials_file_path):
        os.remove(export_credentials_file_path)
    
    with open(export_credentials_file_path, "w") as export_credentials_write:
        print(f"Created {export_credentials_file_path}", flush=True)
        
        android_keystore_alias = "$ANDROID_KEYSTORE_ALIAS"
        android_keystore_password = "$ANDROID_KEYSTORE_PASSWORD"
        if not system.is_ci:
            android_keystore_alias = os.getenv("ANDROID_KEYSTORE_ALIAS")
            android_keystore_password = os.getenv("ANDROID_KEYSTORE_PASSWORD")
            
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
        export_credentials_write.write(f"keystore/release_user=\"{android_keystore_alias}\"\n")
        export_credentials_write.write(f"keystore/release_password=\"{android_keystore_password}\"\n")
elif system.platform_arg == "windows":
    app_data_file_path = subprocess.check_output("echo %APPDATA%", shell=True).decode('ascii').strip().replace("\\", "/")
    godot_editor_settings_file_path = f"{app_data_file_path}/Godot/editor_settings-4.4.tres"
    if not os.path.exists(godot_editor_settings_file_path):
        system.print_files(f"{app_data_file_path}/Godot")
        sys.exit(f"Error: Godot editor settings file {godot_editor_settings_file_path} does not exist under {app_data_file_path}/Godot/. Does project need to be imported first or is {app_data_file_path} not expanding correctly?")
    
    rcedit_file_path = f"{system.absolute_thirdparty_dir_path}/rcedit/rcedit_x64.exe".replace("\\", "/")
    if system.architecture_arg == "x86_32":
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

print("=====================================", flush=True)
print("Exporting Game", flush=True)
print("=====================================", flush=True)
print(system.get_godot_export_command(export_command_type, build_output_path), flush=True)
return_code = subprocess.call(system.get_godot_export_command(export_command_type, build_output_path), shell=True)

export_succeeded = os.path.exists(build_output_path)
if system.using_wsl:
    export_succeeded = os.path.exists(build_output_path.replace("/mnt/c/", "c:/")) # Note os path exists will only works for windows file paths even if using wsl
    
if not export_succeeded:
    print("Available godot binary files:", flush=True)
    system.print_files()
    print(f"Available {system.lib_name} binary files:", flush=True)
    system.print_files(os.path.dirname(os.path.abspath(necessary_file_path)))
    system.print_files(os.path.join(system.repo_dir_path, "bin", system.platform_arg))
    with open(system.project_export_presets_path, "r") as export_presets_read:
        all_lines=export_presets_read.readlines()
        print("export_presets.cfg:", flush=True)
        for index, line in enumerate(all_lines):
            if f"name=\"{system.platform_arg}" in line:
                print(line, flush=True)
            elif ("custom_template/debug" in line and "custom_template/debug=\"\"" not in line):
                print(line, flush=True)
            elif ("custom_template/release" in line and "custom_template/release=\"\"" not in line):
                print(line, flush=True)

    sys.exit(f"Error: Failed to export {system.lib_name} to build output path {build_output_path} for {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg} from godot binary {system.get_godot_binary_file_name_for_system()}")

# (Web Only) - Copy serve.py to bin folder for ease of use.
if system.platform_arg == "web":
    bin_folder_path = os.path.join(system.repo_dir_path, "bin", system.platform_arg)
    
    serve_source_file_path = os.path.join(system.absolute_godot_dir_path, "platform", system.platform_arg, "serve.py")
    serve_destination_file_path = bin_folder_path
    print(f"Copying godot serve.py from {serve_source_file_path} to {serve_destination_file_path}", flush=True)
    
    run_web_build_script_source_file_path = os.path.join(system.absolute_tools_scripts_dir_path, "run_web_build.py")
    run_web_build_script_destination_file_path = bin_folder_path
    print(f"Copying run_web_build.py from {run_web_build_script_source_file_path} to {run_web_build_script_destination_file_path}", flush=True)
    
    os.chdir(os.path.join("..", ".."))
    if not os.path.exists(bin_folder_path):
        os.makedirs(bin_folder_path, exist_ok=True)
    
    shutil.copy(serve_source_file_path, serve_destination_file_path)
    shutil.copy(run_web_build_script_source_file_path, run_web_build_script_destination_file_path)

if system.is_ci:
    for (i, plugin_name) in enumerate(system.project_plugins):
        plugin_dir = os.path.join(system.absolute_plugins_dir_path, plugin_name).replace("\\", "/")
        addons_dir = os.path.join(system.absolute_addons_dir_path, plugin_name).replace("\\", "/")
        
        # Move back to plugins folder
        shutil.move(addons_dir, plugin_dir)
else:
    # Only want to revert the files locally to not flag changes for local exports users make
    # CI would need to retain the information updated in these files in case it needs to run unit tests
    copy_game_gdextension_file_path = game_gdextension_file_path.replace(".gdextension", "_gdextension.copy").replace("\\", "/")
    copy_export_presets_file_path = os.path.join(system.project_dir_path, "export_presets_cfg.copy").replace("\\", "/")

    revert_copy_file(copy_game_gdextension_file_path, game_gdextension_file_path)
    revert_copy_file(copy_export_presets_file_path, system.project_export_presets_path)
    revert_file(export_credentials_file_path)
    
    for (i, plugin_name) in enumerate(system.project_plugins):
        plugin_dir = os.path.join(system.absolute_plugins_dir_path, plugin_name).replace("\\", "/")
        addons_dir = os.path.join(system.absolute_addons_dir_path, plugin_name).replace("\\", "/")
        
        # Move back to plugins folder
        shutil.move(addons_dir, plugin_dir)
        
        plugin_gdextension_file_path = os.path.join(plugin_dir, f"{plugin_name}.gdextension").replace("\\", "/")
        revert_copy_file(plugin_gdextension_file_path.replace(".gdextension", "_gdextension.copy"), plugin_gdextension_file_path)

print("Done")
