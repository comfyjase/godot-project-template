#!/usr/bin/env python

import platform
import os
import subprocess

generate_command = "scons platform=<p> target=editor arch=x86_64 precision=single dev_build=yes dev_mode=yes vsproj=yes"
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

# Generate Game Project Files
return_code = subprocess.call(generate_command, shell=True)
if return_code != 0:
    sys.exit(f"Error: Failed to generate visual studio solution files for {platform.system()}")
