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

import tools.scripts.system as system

system.parse_arguments()

def run_script(script_name):
    return_code = subprocess.call(f"python {os.path.join(system.tools_scripts_dir_path, f"{script_name}.py")} {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg}", shell=True)
    if return_code != 0:
        sys.exit(f"Error: {script_name}.py {system.platform_arg} {system.configuration_arg} {system.architecture_arg} {system.precision_arg} failed")

# Clean up the bin folder for this platform so it will only have files relevant from this create_build process
system.clean_up_bin_folder(system.platform_arg)

# ===============================================
# Builds the project and then exports it
run_script("build")
run_script("create_custom_export_template")
run_script("export")
