#!/usr/bin/env python

import os
import platform
import shutil
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

import tools.scripts.system as system

system.parse_arguments()

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
skip_building_plugins = (system.configuration_arg == "development") and system.process_exists(system.get_godot_binary_file_name_for_system())
if skip_building_plugins:
    print(f"Can't hot reload plugins with the godot editor running.\nIf you want to compile changes for plugins and see them in editor, please close the editor first, recompile and then open the editor again.", flush=True)
else:
    for (i, plugin_name) in enumerate(system.project_plugins):
        os.chdir(os.path.join(system.addons_dir_path, plugin_name))
        
        print("=====================================", flush=True)
        print(f"Building plugin {plugin_name}", flush=True)
        print("=====================================", flush=True)
        
        build_plugin_command = system.get_plugin_scons_command()
        if i == 0:
            build_plugin_command += " symbols_visibility=visible"
        else:
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
