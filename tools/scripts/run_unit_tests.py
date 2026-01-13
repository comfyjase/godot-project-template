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

godot_binary_file_name = system.get_godot_binary_file_name_for_system()
run_unit_test_command = ""
run_engine_unit_tests = True
run_game_unit_tests = True

# ===============================================
# Run Engine Unit Tests
if run_engine_unit_tests:
    print("=====================================", flush=True)
    print("Run Engine Unit Tests", flush=True)
    print("=====================================", flush=True)
    
    os.chdir(system.engine_godot_dir)
        
    if system.using_wsl:
        run_unit_test_command = "wsl ./"
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        subprocess.call(f"chmod +x bin/{godot_binary_file_name}", shell=True)
        run_unit_test_command += "./"
    run_unit_test_command += f"\"bin/{godot_binary_file_name}\" --headless --test"
    
    print(run_unit_test_command, flush=True)
    return_code = subprocess.call(run_unit_test_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed unit tests, see output for details.")
        
    os.chdir(os.path.join("..", ".."))

# ===============================================
# Run Game Unit Tests
if run_game_unit_tests:
    print("=====================================", flush=True)
    print("Run Game Unit Tests", flush=True)
    print("=====================================", flush=True)
    
    run_unit_test_command = f"\"{system.engine_godot_dir}/bin/{godot_binary_file_name}\" --path \"{system.project_dir_name}\" --headless scenes/unit_tests/test.tscn"
    print(run_unit_test_command, flush=True)
    return_code = subprocess.call(run_unit_test_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed game unit tests, see output for details.")
    
    print("Done")
