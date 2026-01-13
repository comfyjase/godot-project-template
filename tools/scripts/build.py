#!/usr/bin/env python

import os
import platform
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
# Clean Up Old Unix Files
if system.platform_arg == "linux" or system.platform_arg == "android":
    # Removing any temporary files so that we don't get false failures.
    # I think this happens because the commit checker compiles files with production flags.
    # Then this checks for any local .os files and editor_game isn't compatible with production - so it fails.
    system.clean_up_files(system.engine_godot_dir, ".os")
    system.clean_up_files(system.absolute_plugins_dir_path, ".os")
    system.clean_up_files(system.project_src_path, ".os")

# ===============================================
# Build Godot
if system.configuration_arg != "development":
    print("=====================================", flush=True)
    print("Build Godot Engine", flush=True)
    print("=====================================", flush=True)
    
    os.chdir(system.engine_godot_dir)
    print(os.getcwd(), flush=True)
    
    print("Build Command: " + system.get_godot_scons_command(), flush=True)
    return_code = subprocess.call(system.get_godot_scons_command(), shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to build godot")
    
    if system.platform_arg == "web" and system.building_editor_for_non_native_os:
        print(os.getcwd(), flush=True)
        os.chdir(os.path.join("bin", ".web_zip"))
        
        godot_html_editor_file_name = "godot.editor.html"
        if os.path.isfile(godot_html_editor_file_name):
            shutil.copyfile(godot_html_editor_file_name, "index.html")
            
        os.chdir(os.path.join("..", ".."))

    # ===============================================
    # Generate C++ extension api files
    if not system.building_editor_for_non_native_os:
        os.chdir("bin")
        system.generate_cpp_bindings()
    
if system.configuration_arg != "development":
    os.chdir(os.path.join("..", ".."))
    if not system.building_editor_for_non_native_os:
        os.chdir("..")

# ===============================================
# Build Plugins

# Development Configuration Only
# Rename the old file - will be removed later by the gdextension on hot reload if possible
if system.configuration_arg == "development":
    project_bin_temp_folder = Path(os.path.join(system.project_bin_path, "temp").replace("\\", "/"))
    project_bin_temp_folder.mkdir(parents=True, exist_ok=True)
    gdignore_file_path = project_bin_temp_folder / ".gdignore"
    
    if not os.path.exists(gdignore_file_path):
        with open(gdignore_file_path, "w") as f:
            pass
    
    for (i, plugin_name) in enumerate(system.project_plugins):
        plugin_binary_file_path = Path(system.get_gdextension_binary_file_path(plugin_name))
        plugin_binary_file_name = os.path.basename(plugin_binary_file_path)
        temp_file_path = project_bin_temp_folder / (str(i) + "." + plugin_binary_file_name + ".temp")
        
        if os.path.exists(plugin_binary_file_path):
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError as e:
                    pass
                    
                new_temp_file_path = project_bin_temp_folder / (str(i) + "." + plugin_binary_file_name + ".temp.2")
                
                try:
                    os.replace(plugin_binary_file_path, new_temp_file_path)
                except PermissionError as e:
                    try:
                        shutil.move(plugin_binary_file_path, temp_file_path)
                    except PermissionError as another_e:
                        print("Please go to the editor to trigger a hot reload first", flush=True)
            elif not os.path.exists(temp_file_path):
                shutil.move(plugin_binary_file_path, temp_file_path)

# Build a new file
for (i, plugin_name) in enumerate(system.project_plugins):
    os.chdir(os.path.join(system.plugins_dir_path, plugin_name))
    
    print("=====================================", flush=True)
    print(f"Building plugin {plugin_name}", flush=True)
    print("=====================================", flush=True)
    
    build_plugin_command = system.get_plugin_scons_command()
    if i > 0:
        build_plugin_command += " build_library=no"

    print(f"Command: {build_plugin_command}", flush=True)
    return_code = subprocess.call(build_plugin_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to build plugin {plugin_name} for {platform.system()}")
    
    os.chdir(os.path.join("..", "..", ".."))

# ===============================================
# Build Game
print("=====================================", flush=True)
print("Build Game", flush=True)
print("=====================================", flush=True)

print(f"Command: {system.get_project_scons_command()}", flush=True)
return_code = subprocess.call(system.get_project_scons_command(), shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to build game")

# ===============================================
# Generate Documentation
print("=====================================", flush=True)
print("Generate GDExtension Documentation", flush=True)
print("=====================================", flush=True)

# Note: It's on the developer to make sure these documentation files are committed.
system.generate_gdextension_documentation()

# ===============================================
# Write To Build Information File
with open(system.build_information_file_path, "w") as build_information_file_write:
    git_command = "git rev-parse --short HEAD"
    latest_git_commit_id = subprocess.check_output(git_command, shell=True).decode('ascii').strip()
    
    git_command = "git show -s --date=format:'%Y%m%d_%H%M%S' --format=%cd"
    latest_commit_timestamp = subprocess.check_output(git_command, shell=True).decode('ascii').strip().replace("\'", "")
    
    git_command = "git branch --show-current"
    current_branch_name = subprocess.check_output(git_command, shell=True).decode('ascii').strip()
    
    build_information_file_write.writelines(f"Game_{system.platform_arg.capitalize()}_{system.configuration_arg.replace("_", " ").title().replace(" ", "_")}_{system.architecture_arg}_{system.precision_arg.capitalize()}_{latest_commit_timestamp}_{current_branch_name}_{latest_git_commit_id}")

# ===============================================
# (Web Only) Zip Project
if system.platform_arg == "web" and system.configuration_arg == "editor":
    print("=====================================", flush=True)
    print("Zip Game Project For Web Editor", flush=True)
    print("=====================================", flush=True)
    
    # Remove the old folder
    if os.path.isdir("game.zip"):
        shutil.rmtree("game.zip", True)

    # Make new zip folder
    shutil.make_archive("game", "zip", "game")
    
# ===============================================
# (Web/Android Only) Create Custom Export Template If Needed
if system.configuration_arg == "editor_game":
    if system.platform_arg in ["web", "android"]:
        return_code = subprocess.call(f"python {os.path.join(system.tools_scripts_dir_path, "create_custom_export_template.py")} {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}", shell=True)
        if return_code != 0:
            sys.exit(f"Error: create_custom_export_template.py {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg} failed")
        
        return_code = subprocess.call(f"python {os.path.join(system.tools_scripts_dir_path, "export.py")} {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}", shell=True)
        if return_code != 0:
            sys.exit(f"Error: export.py {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg} failed")
