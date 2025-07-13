#!/usr/bin/env python

import platform
import os
import subprocess
import sys

generate_command = "scons platform=<p> target=editor arch=x86_64 precision=single dev_build=yes dev_mode=yes vsproj=yes build_library=no"
if platform.system() == "Windows":
    generate_command = generate_command.replace("<p>", "windows")
elif platform.system() == "Darwin":
    generate_command = generate_command.replace("<p>", "macos")
elif platform.system() == "Linux":
    generate_command = generate_command.replace("<p>", "linux")
    
# Generate Godot Engine Project Files
if not os.path.exists("godot/godot.vcxproj"):
    os.chdir("godot")
    return_code = subprocess.call(generate_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to generate visual studio solution files for {platform.system()}")
    os.chdir("..")

# Build godot-cpp
godot_cpp_build_command = generate_command.replace("build_library=no", "")
return_code = subprocess.call(godot_cpp_build_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to build godot-cpp for {platform.system()}")
    
# Generate Game Project Files
return_code = subprocess.call(generate_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to generate visual studio solution files for {platform.system()}")
