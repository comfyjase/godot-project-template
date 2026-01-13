import os
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)
    
import tools.scripts.system as system

godot_bin_file_path = os.path.join(system.godot_bin_path, "godot.windows.editor.dev.x86_64.exe").replace("\\", "/")

command = f"\"{godot_bin_file_path}\" --editor --path \"project\""
return_code = subprocess.call(command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to run {command}")
