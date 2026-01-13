#!/usr/bin/env python

import fnmatch
import os
import pathlib
import platform
import shutil
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from SCons.Script import *

# Default values
lib_name = "core"
project_dir_name = "project"
project_src_dir = os.path.join("project", "src").replace("\\", "/")
root_dir = os.path.join("..", "..", "..").replace("\\", "/")
root_godot_cpp_dir = os.path.join(root_dir, "engine", "godot-cpp").replace("\\", "/")
addons_dir_path = os.path.join("..", "..", "addons").replace("\\", "/")
addons_imgui_godot_dir_path = os.path.join(addons_dir_path, "imgui-godot").replace("\\", "/")
addons_imgui_godot_include_dir_path = os.path.join(addons_imgui_godot_dir_path, "include").replace("\\", "/")
thirdparty_dir_path = os.path.join(root_dir, "thirdparty").replace("\\", "/")
thirdparty_imgui_dir_path = os.path.join(thirdparty_dir_path, "imgui").replace("\\", "/")

platforms = ["linux", "macos", "windows", "android", "ios", "web"]

default_platform = ""
if sys.platform.startswith("linux"):
    default_platform = "linux"
elif sys.platform == "darwin":
    default_platform = "macos"
elif sys.platform == "win32" or sys.platform == "msys":
    default_platform = "windows"
elif sys.argv.get("platform", ""):
    default_platform = sys.argv.get("platform")
else:
    raise ValueError("Could not detect platform automatically, please specify with platform=<platform>")
    
# editor - run godot editor dev executable and pass --editor and --path
# editor_game - run godot editor dev executable and just pass --path
# development - only builds the game project, this is intended to be used when running the godot binary separately and working on the GDExtension code exclusively. So you can hot reload your changes whilst the editor is running.
# template_debug - run the exported template_debug executable and then attach the visual studio instance to it.
# template_release - run the exported template_release executable and then attach the visual studio instance to it.
# profile - run the exported template_release executable (should be exported using production=yes and debugging_symbols=yes) and then attach the visual studio instance to it.
# production - run the exported template_release executable (should be exported using production=yes) and then attach the visual studio instance to it.
configurations = ["editor", "editor_game", "development", "template_debug", "template_release", "profile", "production"]

# CPU architecture options.
architectures = [
    "",
    "universal",
    "x86_32",
    "x86_64",
    "arm32",
    "arm64",
    "rv64",
    "ppc32",
    "ppc64",
    "wasm32",
]

architecture_aliases = {
    "x64": "x86_64",
    "amd64": "x86_64",
    "armv7": "arm32",
    "armv8": "arm64",
    "arm64v8": "arm64",
    "aarch64": "arm64",
    "rv": "rv64",
    "riscv": "rv64",
    "riscv64": "rv64",
    "ppcle": "ppc32",
    "ppc": "ppc32",
    "ppc64le": "ppc64",
}

def get_all_directories_recursive(root_directory):
    directories = []
    
    for (search_path,directory_names,files) in os.walk(root_directory, topdown=True):
        search_path_with_ending_slash = os.path.join(search_path, '').replace('\\', '/')
        directories.append(search_path_with_ending_slash)
    
    return directories
    
def get_all_files_recursive(root_directory, filetype='*.*'):
    files_matching_type = []

    for (search_path,directory_names,files) in os.walk(root_directory, topdown=True):
        search_path_with_ending_slash = os.path.join(search_path, '').replace('\\', '/')
        
        for (file) in files:
            if fnmatch.fnmatch(file, '*' + filetype):
                files_matching_type.append(str(search_path_with_ending_slash + file))
                
    return files_matching_type

def add_imgui(env, all_directories, all_source_files, cpp_defines):
    should_include_imgui = (env["arch"] not in ["x86_32", "arm32", "arm64"]) and (env["platform"] not in ["web", "android", "ios"])
    if should_include_imgui:
        all_directories.extend([addons_imgui_godot_include_dir_path, thirdparty_imgui_dir_path ])
        all_source_files.extend(Glob(f"{thirdparty_imgui_dir_path}/*.cpp", strings=True))
        cpp_defines.extend([ 'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""', "IMGUI_ENABLED" ])

def add_cpp_defines(env, cpp_defines):
    if env["target"] in ["editor", "editor_game", "development", "template_debug"]:
        cpp_defines.append("TOOLS_ENABLED")
        cpp_defines.append("DEBUG_ENABLED")
        cpp_defines.append("TESTS_ENABLED")
    
    if env["platform"] == "windows":
        cpp_defines.append("PLATFORM_WINDOWS")
    elif env["platform"] == "linux":
        cpp_defines.append("PLATFORM_LINUX")
    elif env["platform"] == "macos":
        cpp_defines.append("PLATFORM_MACOS")
    elif env["platform"] == "android":
        cpp_defines.append("PLATFORM_ANDROID")
    elif env["platform"] == "ios":
        cpp_defines.append("PLATFORM_IOS")
    elif env["platform"] == "web":
        cpp_defines.append("PLATFORM_WEB")
        
    if env["target"] == "production":
        cpp_defines.append("PRODUCTION")
    elif env["target"] == "profile":
        cpp_defines.append("PROFILE")
    elif env["target"] == "template_release":
        cpp_defines.append("RELEASE")
    else:
        if env["target"] == "development":
            cpp_defines.append("DEVELOPMENT")
        cpp_defines.append("DEBUG")