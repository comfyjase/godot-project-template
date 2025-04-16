#!/usr/bin/env python

import os
import platform
import shutil
import subprocess
import sys

if platform.system() == "Windows":
    import winreg

from methods import *

current_directory = os.getcwd()

# Helper Functions
def run_subprocess(subprocess_command, return_code_error_message):
    subprocess.call(subprocess_command, shell=True)
        if return_code != 0:
            print(return_code_error_message)
            exit()

# TODO: Test...
def get_vs_install_directory():
    if platform.system() != "Windows":
        print("Getting vs install directory not supported for non Windows platform, aborting!")
        exit()
        
    vs_install_directory_path = ""
    vs_install_directories = get_all_directories_recursive("C:/ProgramData/Microsoft/VisualStudio/Packages/_Instances/")
    
    for (vs_install_directory in vs_install_directories):
        directory_name = os.path.dirname(vs_install_directory)
        
        root_key_name = f"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{directory_name}\\"
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, root_key_name) as key:
            try:
                vs_install_directory_path, registry_type = winreg.QueryValueEx(key, "InstallLocation")
                if vs_install_directory_path != "":
                    break
            # Can happen if the root_key_name doesn't have "InstallLocation" as a sub key name
            # So just continue since this is a valid situation, not all VS registries have "InstallLocation" setup
            except EnvironmentError:
                continue
    
    return vs_install_directory_path

print("############################################", flush=True)
print("############# PROJECT SETUP ################", flush=True)
print("############################################", flush=True)

# ======================================================
# Installs
print("Installing software and system dependencies for project", flush=True)

# pip
run_subprocess("python -m ensurepip --upgrade", "Error: Failed to install pip, have you installed python correctly and added it to PATH? Aborting!")

# scons
run_subprocess("pip install scons", "Error: Failed to install scons somehow... aborting!")

# (Windows Only) WSL
if platform.system() == "Windows":
    wsl_install_output = subprocess.check_output(f"wsl -l -v").decode('ascii').strip()
    if "Windows subsystem for Linux has no installed distributions" in wsl_install_output:
        run_subprocess("wsl --install", "Error: Failed to install WSL, aborting!")

# (Linux Only) Libraries 
if platform.system() == "Linux":
    run_subprocess("sudo apt-get update", "Error: Failed to update linux somehow, aborting!")
    run_subprocess("sudo apt-get install -y build-essential scons pkg-config libx11-dev libxcursor-dev libxinerama-dev libgl1-mesa-dev libglu1-mesa-dev libasound2-dev libpulse-dev libudev-dev libxi-dev libxrandr-dev libwayland-dev", "Error: Failed to install linux libraries, aborting!")
    run_subprocess("sudo apt-get install -y libembree-dev libenet-dev libfreetype-dev libpng-dev zlib1g-dev libgraphite2-dev libharfbuzz-dev libogg-dev libtheora-dev libvorbis-dev libwebp-dev libmbedtls-dev libminiupnpc-dev libpcre2-dev libzstd-dev libsquish-dev libicu-dev", "Error: Failed to update linux somehow, aborting!") 
    
# ======================================================
# Submodules

# ImGui checkout correct branch to match imgui-godot
os.chdir("thirdparty/imgui")
run_subprocess("git checkout v1.91.6-docking", "Error: Failed to checkout imgui at branch v1.91.6-docking, has submodule been initialized? Aborting!")
os.chdir("..")

# emsdk install and activate 
os.chdir("emsdk")
emsdk_version = "latest"
if platform.system() == "Windows":
    run_subprocess(f"emsdk.bat install {emsdk_version}", f"Error: Failed to install emsdk version {emsdk_version}, has submodule been initialized? Aborting!")
    run_subprocess(f"emsdk.bat activate {emsdk_version} --permanent", f"Error: Failed to activate emsdk version {emsdk_version}, has submodule been initialized? Aborting!")
else:
    run_subprocess(f"./emsdk install {emsdk_version}", f"Error: Failed to install emsdk version {emsdk_version}, has submodule been initialized? Aborting!")
    run_subprocess(f"./emsdk activate {emsdk_version} --permanent", f"Error: Failed to activate emsdk version {emsdk_version}, has submodule been initialized? Aborting!")

print("Please restart your machine after this project setup has finished - this is needed to make sure emsdk path/environment variables are set properly.")

os.chdir("..")
os.chdir("..")

# ======================================================
# (Windows Only) Create New Platforms For Visual Studio
# NOTE: Only tested with VS 2022... would need to update v170 below for other versions!

if platform.system() == "Windows":
    # Default to VS 2022
    visual_studio_version = "2022"
    visual_studio_vc_directory_name = "v170"
    
    # Leaving commented in case vs2025 comes out soon
    #if len(sys.argv) == 2:
        #visual_studio_version = sys.argv[1]
        #if visual_studio_version == "2025":
        #    visual_studio_vc_directory_name = "v200" # Anticipating the future name of VS2025...
    
    def create_new_vs_platform(platform_name):
        vs_install_directory = get_vs_install_directory()
        vs_platforms_directory = vs_install_directory + f"/MSBuild/Microsoft/VC/{visual_studio_vc_directory_name}/Platforms/"
        
        x64_bit_platform_folder = vs_platforms_directory + "x64"
        new_platform_folder = vs_platforms_directory + platform_name
        
        shutil.copytree(x64_bit_platform_folder, new_platform_folder, dirs_exist_ok=True)
    
    new_platforms_to_add = [ "linux", "web" ]
    for (new_platform in new_platforms_to_add):
        create_new_vs_platform(new_platform)

print("############################################", flush=True)
print("######### PROJECT SETUP FINISHED ###########", flush=True)
print("############################################", flush=True)
