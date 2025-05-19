#!/usr/bin/env python

import os
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
# template_debug - run the exported template_debug executable and then attach the visual studio instance to it.
# template_release - run the exported template_release executable and then attach the visual studio instance to it.
# profile - run the exported template_release executable (should be exported using production=yes and debugging_symbols=yes) and then attach the visual studio instance to it.
# production - run the exported template_release executable (should be exported using production=yes) and then attach the visual studio instance to it.
configurations = ["editor", "editor_game", "template_debug", "template_release", "profile", "production"]

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
    wsl_install_output = subprocess.check_output(f"wsl.exe -l -v", shell=True).decode('ascii').strip()
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
