#!/usr/bin/env python

import os
import platform
import requests
import shutil
import subprocess
import sys
import webbrowser

if platform.system() == "Windows":
    import winreg

from methods import *
from pathlib import Path

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

print("==========================================", flush=True)
print("Installing Python Libraries", flush=True)
print("==========================================", flush=True)
# pip
run_subprocess("python -m ensurepip --upgrade", "Error: Failed to install pip, have you installed python correctly and added it to PATH? Aborting!")

# scons
run_subprocess("pip install scons", "Error: Failed to install scons somehow... aborting!")
run_subprocess("pip install customtkinter", "Error: Failed to install customtkinter... aborting!")
run_subprocess("pip install pillow", "Error: Failed to install pillow... aborting!")
run_subprocess("pip install requests", "Error: Failed to install requests... aborting!")
print("Done", flush=True)
print("", flush=True)

print("==========================================", flush=True)
print("Installing Godot Swappy", flush=True)
print("==========================================", flush=True)
URL = "https://github.com/godotengine/godot-swappy/releases/download/from-source-2025-01-31/godot-swappy.zip"
r = requests.get(URL)
with open("godot-swappy.zip", "wb") as fd:
    fd.write(r.content)
shutil.unpack_archive("godot-swappy.zip", "godot/thirdparty/swappy-frame-pacing")
print("Done", flush=True)
print("", flush=True)

print("==========================================", flush=True)
print("Installing Android SDK", flush=True)
print("==========================================", flush=True)

print("Next, you will have to manually download OpenJDK 17 from the next website that will open up.", flush=True)
input("Press Enter to go to the OpenJDK 17 website (https://adoptium.net/en-GB/temurin/releases/?variant=openjdk17&os=any&arch=any&version=17)...")
webbrowser.open("https://adoptium.net/en-GB/temurin/releases/?variant=openjdk17&os=any&arch=any&version=17")
input("Press Enter once you have installed OpenJDK 17...")

print("")
print("Next, this script will open a website link for you where you have to accept the license terms and manually download the android sdk command line tools.", flush=True)
print("You will have to scroll down towards the bottom of the page until you see the Command line tools only header - download the sdk for your platform.", flush=True)
downloads_folder = Path.home() / "Downloads/"

print("")
input("Press Enter to go to the Android SDK download website (https://developer.android.com/studio#command-tools)...")
webbrowser.open("https://developer.android.com/studio#command-tools")
print("")
input("Press Enter to continue once you have downloaded the Androidn SDK zip folder...")
android_sdk_version_folder_name = "commandlinetools-win-13114758_latest.zip"
android_sdk_downloaded_folder = downloads_folder + android_sdk_version_folder_name
android_sdk_root_folder = Path.home().drive + "/sdks/android/"
android_sdk_destination_folder = android_sdk_root_folder + "cmdline-tools/latest/"
shutil.unpack_archive(android_sdk_downloaded_folder, android_sdk_destination_folder)
input(f"Please add ANDROID_HOME={Path.home().drive}/sdks/android to your environment variables then press enter...")
run_subprocess(f"{android_sdk_root_folder}/cmdline-tools/latest/bin/sdkmanager --sdk_root={android_sdk_root_folder} --licenses", f"Failed to install android sdk {android_sdk_version_folder_name}")
run_subprocess(f"{android_sdk_root_folder}/cmdline-tools/latest/bin/sdkmanager --sdk_root={android_sdk_root_folder} \"platform-tools\" \"build-tools;34.0.0\" \"platforms;android-34\" \"cmdline-tools;latest\" \"cmake;3.10.2.4988404\" \"ndk;23.2.8568313\"", f"Failed to install android sdk {android_sdk_version_folder_name}")
print("Done", flush=True)
print("", flush=True)

print("==========================================", flush=True)
print(f"Installing System Dependencies For {platform.system()}", flush=True)
print("==========================================", flush=True)
# (Windows Only)
if platform.system() == "Windows":
    wsl_install_output = subprocess.check_output(f"wsl -l -v").decode('ascii').strip()
    if "Windows subsystem for Linux has no installed distributions" in wsl_install_output:
        run_subprocess("wsl --install", "Error: Failed to install WSL, aborting!")
    run_subprocess("winget install --id GitHub.cli", "Error: Failed to install Github CLI (gh) using winget. Aborting!")
    
    # WSL Installs
    run_subprocess("wsl sudo apt-get update", "Error: Failed to update linux somehow, aborting!")
    run_subprocess("wsl sudo apt-get install -y build-essential scons pkg-config libx11-dev libxcursor-dev libxinerama-dev libgl1-mesa-dev libglu1-mesa-dev libasound2-dev libpulse-dev libudev-dev libxi-dev libxrandr-dev libwayland-dev", "Error: Failed to install linux libraries, aborting!")
    run_subprocess("wsl sudo apt-get install -y libembree-dev libenet-dev libfreetype-dev libpng-dev zlib1g-dev libgraphite2-dev libharfbuzz-dev libogg-dev libtheora-dev libvorbis-dev libwebp-dev libmbedtls-dev libminiupnpc-dev libpcre2-dev libzstd-dev libsquish-dev libicu-dev", "Error: Failed to install linux libraries part 2, aborting!")   
# (Linux Only) 
elif platform.system() == "Linux":
    run_subprocess("sudo apt-get update", "Error: Failed to update linux somehow, aborting!")
    run_subprocess("sudo apt-get install -y build-essential scons pkg-config libx11-dev libxcursor-dev libxinerama-dev libgl1-mesa-dev libglu1-mesa-dev libasound2-dev libpulse-dev libudev-dev libxi-dev libxrandr-dev libwayland-dev", "Error: Failed to install linux libraries, aborting!")
    run_subprocess("sudo apt-get install -y libembree-dev libenet-dev libfreetype-dev libpng-dev zlib1g-dev libgraphite2-dev libharfbuzz-dev libogg-dev libtheora-dev libvorbis-dev libwebp-dev libmbedtls-dev libminiupnpc-dev libpcre2-dev libzstd-dev libsquish-dev libicu-dev", "Error: Failed to update linux somehow, aborting!")   
    run_subprocess("(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
    && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y", "Error: Failed to install Github CLI (gh). Aborting!")
# (MacOS Only)
elif platform.system() == "Darwin":
    run_subprocess("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", "Error: Failed to install brew. Aborting!")
    run_subprocess("brew install gh", "Error: Failed to install Github CLI (gh) using brew. Aborting!")

print("Please enter your github account details - needed for the Commit Checker which uses Github CLI (gh commands)", flush=True)  
run_subprocess("gh auth login", "Error: Failed Github CLI auth login, might need to restart the terminal for the install to take effect? Aborting!")
print("Done", flush=True)
print("", flush=True)

# ======================================================
# Submodules
print("==========================================", flush=True)
print(f"Installing EMSDK For Web Platform", flush=True)
print("==========================================", flush=True)
# emsdk install and activate 
os.chdir("thirdparty/emsdk")
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

print("Done", flush=True)
print("", flush=True)

# ======================================================
# (Windows Only) Create New Platforms For Visual Studio
# NOTE: Only tested with VS 2022... would need to update v170 below for other versions!

if platform.system() == "Windows":
    print("==========================================", flush=True)
    print(f"Adding New Visual Studio Platforms", flush=True)
    print("==========================================", flush=True)

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
    
    new_platforms_to_add = [ "linux", "web", "android" ]
    for (new_platform in new_platforms_to_add):
        create_new_vs_platform(new_platform)
        
    print("Done", flush=True)
    print("", flush=True)

print("############################################", flush=True)
print("######### PROJECT SETUP FINISHED ###########", flush=True)
print("############################################", flush=True)
