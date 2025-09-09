#!/usr/bin/env python

import os
import pathlib
import platform
import shutil
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from glob import glob

import tools.scripts.system as system

system.parse_arguments()

# ===============================================
# Clean Up Old Gradle Build Files
if system.platform_arg == "android":
    
    # Removing any temporary files so that we don't get false failures.
    # I think this happens because the commit checker compiles files with production flags.
    # Then this checks for any local .os files and editor_game isn't compatible with production - so it fails.
    system.clean_up_files(system.godot_dir_path, ".os")
    
    android_build_folder = os.path.join(project_dir_path, "android", "build")
    if os.path.exists(android_build_folder):
        print("=====================================", flush=True)
        print("Cleaning Up Previous Gradle Files", flush=True)
        print("=====================================", flush=True)
    
        os.chdir(android_build_folder)
        
        if platform.system() == "Windows":
            gradle_clean_command = "gradlew clean"
        else:
            gradle_clean_command = "./gradlew clean"
        print(gradle_clean_command, flush=True)
        return_code = subprocess.call(gradle_clean_command, shell=True)
        if return_code != 0:
            sys.exit(f"Error: Failed to clean gradle files for {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}")
        
        os.chdir(os.path.join("..", "..", ".."))

# ===============================================
# Build Godot
os.chdir("godot")

print("=====================================", flush=True)
print("Creating Custom Export Template", flush=True)
print("=====================================", flush=True)
    
print(system.get_godot_custom_export_template_scons_command(), flush=True)
return_code = subprocess.call(system.get_godot_custom_export_template_scons_command(), shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to build godot export template for {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}")

# ===============================================
# Rename Files
os.chdir("bin")

template_suffix = ""
if system.platform_arg == "windows":
    template_suffix = ".exe"
elif system.platform_arg == "macos":
    template_suffix = ".zip"
elif system.platform_arg == "linux":
    template_suffix = ""
elif system.platform_arg == "web":
    template_suffix = ".zip"
elif system.platform_arg == "android":
    template_suffix = ".apk"
elif system.platform_arg == "ios":
    template_suffix = ".zip"

godot_files = []
suffix = f"{system.configuration_arg}.{system.architecture_arg}{template_suffix}"
if system.precision_arg == "double":
    suffix = suffix.replace(f"{system.architecture_arg}", f"{system.precision_arg}.{system.architecture_arg}")
if system.platform_arg == "web":
    if system.configuration_arg in ["editor", "editor_game"]:
        shutil.copytree(".web_zip", f"web.{system.configuration_arg}.{system.architecture_arg}", dirs_exist_ok=True)
        shutil.make_archive(f"web.{system.configuration_arg}.{system.architecture_arg}", "zip", f"web.{system.configuration_arg}.{system.architecture_arg}")
    else:
        old_name = f"godot.web.{godot_configuration_arg}.{system.architecture_arg}.nothreads.dlink{template_suffix}"
        if system.precision_arg == "double":
            old_name = old_name.replace(f"{system.architecture_arg}", f"{system.precision_arg}.{system.architecture_arg}")
        new_name = f"web.{suffix}"
        os.replace(f"{old_name}", f"{new_name}")
elif system.platform_arg == "android":
    old_name = f"android_dev{template_suffix}"
    if (system.configuration_arg in ["editor", "editor_game", "template_debug"]):
        if system.is_ci:  
            old_name = f"android_debug{template_suffix}"
    else:
        old_name = f"android_release{template_suffix}"
    
    if os.path.isfile(old_name):
        print(f"Renaming {old_name} to android.{suffix}", flush=True)
        os.replace(old_name, f"android.{suffix}")
    else:
        print(f"{old_name} custom export template file not found, here are the available files: ", flush=True)
        print_files()
elif system.platform_arg == "macos" or system.platform_arg == "ios":
    platform_name_to_use = system.platform_arg
    
    old_name = f"godot_{platform_name_to_use}{template_suffix}"
    new_name = f"{platform_name_to_use}.{suffix}"
    
    if (system.configuration_arg in ["editor", "editor_game", "template_debug"]) and not system.is_ci:
        old_name = old_name.replace(f"{platform_name_to_use}", f"{platform_name_to_use}_dev")
        if system.precision_arg == "double":
            old_name = old_name.replace(f"{platform_name_to_use}_dev", f"{platform_name_to_use}_dev_double")
    
    if system.precision_arg == "double":
        old_name = old_name.replace(f"{platform_name_to_use}", f"{platform_name_to_use}_double")
        
    if os.path.isfile(f"{old_name}"):
        os.replace(f"{old_name}", f"{new_name}")
    else:
        print_files()
else:
    godot_platform_name = system.platform_arg
    if system.platform_arg == "linux":
        godot_platform_name = "linuxbsd"
    godot_files = glob(f"godot.{godot_platform_name}.{godot_configuration_arg}.*")
    for file in godot_files:
        old_name = file
        new_name = file.replace("godot.", "").replace(f"{godot_configuration_arg}", f"{system.configuration_arg}")
        os.replace(old_name, new_name)

# ===============================================
# Update export_presets.cfg with this template
os.chdir(os.path.join("..", "..", "game"))

godot_platform_name = system.platform_arg
if system.platform_arg == "linux":
    godot_platform_name = "linuxbsd"

# Android specific
gradle_source_file_path = os.path.join(system.godot_bin_path, "android_source.zip")
gradle_source_file_path = os.path.normpath(gradle_source_file_path).replace("\\", "/")

export_template_file_path = os.path.join(system.godot_bin_path, f"{godot_platform_name}.{suffix}")
export_template_file_path = os.path.normpath(export_template_file_path).replace("\\", "/")
if system.using_wsl:
    export_template_file_path = "/mnt/" + export_template_file_path.replace(":", "").lower()
elif platform.system() == "Linux" or platform.system() == "Darwin":
    export_template_file_path = export_template_file_path.lower()
    
if system.platform_arg == "android":
    if not os.path.exists(gradle_source_file_path):
        print("Available files:", flush=True)
        print_files()
        sys.exit(f"Error: Failed to create {export_template_file_path} for {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}")
else:
    if not os.path.exists(export_template_file_path):
        print("Available files:", flush=True)
        print_files()
        sys.exit(f"Error: Failed to create {export_template_file_path} for {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}")

if platform.system() == "Linux" or platform.system() == "Darwin":
    print(f"Called chmod a+rwx {export_template_file_path}", flush=True)
    subprocess.call(f"chmod a+rwx {export_template_file_path}", shell=True)

with open("export_presets.cfg", "r") as export_presets_read:
    all_lines=export_presets_read.readlines()
    
    found_export = False
    for index, line in enumerate(all_lines):
        if f"name=\"{system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}" in line:
            found_export = True
            print(f"Found export preset for {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}", flush=True)
            
        if found_export:
            if system.platform_arg == "android":
                if "gradle_build/android_source_template=" in line:
                    all_lines[index] = f"gradle_build/android_source_template=\"{gradle_source_file_path}\"\n"
                    print(f"Updating gradle_build/android_source_template to {gradle_source_file_path}", flush=True)
                    break
            else:
                if "custom_template/debug=" in line:
                    all_lines[index] = f"custom_template/debug=\"{export_template_file_path}\"\n"
                    print(f"Updating template debug to {export_template_file_path}", flush=True)
                elif "custom_template/release=" in line:
                    all_lines[index] = f"custom_template/release=\"{export_template_file_path}\"\n"
                    print(f"Updating template release to {export_template_file_path}", flush=True)
                    break

    with open("export_presets.cfg", "w") as export_presets_write:
        export_presets_write.writelines(all_lines)

# Hacky workaround to fix godot 4.x gradle build issues (see https://github.com/godotengine/godot/issues/81668)
if system.platform_arg == "android":
    print("=====================================", flush=True)
    print("Copying Godot Lib File To Correct Gradle Build Folder", flush=True)
    print("=====================================", flush=True)
    
    godot_android_library_file = os.path.join(system.godot_bin_path, "godot-lib.template_debug.dev.aar")
    if godot_configuration_arg == "template_release":
        godot_android_library_file = godot_android_library_file.replace("godot-lib.template_debug.dev.aar", "godot-lib.template_release.aar")
    
    if not os.path.exists(godot_android_library_file):
        sys.exit(f"{godot_android_library_file} is missing! Are the file names correct?")
        print_files()
    
    android_build_folder = "debug"
    if godot_configuration_arg == "template_release":
        android_build_folder = "release"
    
    game_project_android_library_file_destination_folder = os.path.join(system.project_dir_path, "android", "build", "libs", android_build_folder)
    pathlib.Path(game_project_android_library_file_destination_folder).mkdir(parents=True, exist_ok=True)
    shutil.copy(godot_android_library_file, game_project_android_library_file_destination_folder)
