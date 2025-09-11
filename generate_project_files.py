#!/usr/bin/env python

import platform
import os
import subprocess
import sys

import tools.scripts.system as system

generate_command = "scons platform=<p> target=editor arch=x86_64 precision=single dev_build=yes dev_mode=yes vsproj=yes build_library=no"
if platform.system() == "Windows":
    generate_command = generate_command.replace("<p>", "windows")
elif platform.system() == "Darwin":
    generate_command = generate_command.replace("<p>", "macos")
elif platform.system() == "Linux":
    generate_command = generate_command.replace("<p>", "linux")
    
# Generate Godot Engine Project Files
if not os.path.exists(f"{system.engine_godot_dir}/godot.vcxproj"):    
    os.chdir(system.engine_godot_dir)
    return_code = subprocess.call(generate_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to generate visual studio solution files for {platform.system()}")
    
    print("=====================================", flush=True)
    print("Build godot", flush=True)
    print("=====================================", flush=True)
    
    build_command = generate_command.replace("vsproj=yes build_library=no", f" tests=yes cache_path={system.godot_cache_path} accesskit_sdk_path={system.access_kit_path}")
    print("Build Command: " + build_command, flush=True)
    return_code = subprocess.call(build_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to build godot")
    
    os.chdir("bin")
    system.generate_cpp_bindings()
    os.chdir(os.path.join("..", "..", ".."))

# Build plugins
for (i, plugin_name) in enumerate(system.project_plugins):
    os.chdir(os.path.join(system.addons_dir_path, plugin_name))
    
    print("=====================================", flush=True)
    print(f"Building plugin {plugin_name}", flush=True)
    print("=====================================", flush=True)
    
    build_plugin_command = generate_command.replace(" vsproj=yes build_library=no", f" cache_path={system.project_cache_path} symbols_visibility=visible")
    print(build_plugin_command, flush=True)
    return_code = subprocess.call(build_plugin_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to build {plugin_name} for {platform.system()}")
    
    print(f"Done", flush=True)
    os.chdir(os.path.join("..", "..", ".."))
    
# Generate Game Project Files
print("=====================================", flush=True)
print(f"Generating game project files", flush=True)
print("=====================================", flush=True)
return_code = subprocess.call(generate_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to generate visual studio solution files for {platform.system()}")
