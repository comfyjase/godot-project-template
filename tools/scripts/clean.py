#!/usr/bin/env python

import os
import platform
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

import tools.scripts.system as system

system.parse_arguments()
    
# ===============================================
# Engine Clean

# Switch to True if you want to clean engine symbols too...
clean_engine = system.configuration_arg != "development":

if clean_engine:
    print("=====================================", flush=True)
    print("Cleaning Godot Engine", flush=True)
    print("=====================================", flush=True)
    
    os.chdir("godot")
    
    clean_command = system.get_godot_scons_command() + " -c"
    print("Clean Command: " + clean_command, flush=True)
    return_code = subprocess.call(clean_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to clean godot")

    os.chdir("..")
    
# ===============================================
# Project Clean
print("=====================================", flush=True)
print("Cleaning Game", flush=True)
print("=====================================", flush=True)

clean_command = system.get_project_scons_command() + " -c"
print(f"Command: {clean_command}", flush=True)
return_code = subprocess.call(clean_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to clean game")
