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

default_platform = ""
platforms = ["linux", "macos", "windows", "android", "ios", "web"]

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

is_os_64_bit = sys.maxsize > 2**32

wsl_available = False
if (shutil.which("wsl") is not None):
    return_code = subprocess.call("wsl -l -v", shell=True)
    if return_code == 0:
        wsl_install_output = subprocess.check_output(f"wsl -l -v", shell=True).decode('ascii').strip()
        if "Windows subsystem for Linux has no installed distributions" not in wsl_install_output:
            wsl_available = True
            print("WSL is available", flush=True)
        else:
            print("WSL is not available", flush=True)

def init_system_variables(arguments):
    global default_platform
    
    if sys.platform.startswith("linux"):
        default_platform = "linux"
    elif sys.platform == "darwin":
        default_platform = "macos"
    elif sys.platform == "win32" or sys.platform == "msys":
        default_platform = "windows"
    elif arguments.get("platform", ""):
        default_platform = arguments.get("platform")
    else:
        raise ValueError("Could not detect platform automatically, please specify with platform=<platform>")

def print_files(directory = "."):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for f in files:
        print(f"\t{f}", flush=True)

def detect_arch():
    host_machine = platform.machine().lower()
    if host_machine in architectures:
        return host_machine
    elif host_machine in architecture_aliases.keys():
        return architecture_aliases[host_machine]
    elif "86" in host_machine:
        # Catches x86, i386, i486, i586, i686, etc.
        return "x86_32"
    else:
        methods.print_warning(f'Unsupported CPU architecture: "{host_machine}". Falling back to x86_64.')
        return "x86_64"

def clean_up_files(directory, extension):
    dir = pathlib.Path(directory)
    so_files = dir.rglob(f"*{extension}")  # recursively
    for so_file in so_files:
        print(f"Removing {so_file}", flush=True)
        os.remove(so_file)
