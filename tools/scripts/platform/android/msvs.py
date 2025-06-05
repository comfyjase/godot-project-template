#!/usr/bin/env python

import os
import platform
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from tools.scripts.system import *

def get_platforms():
    return [
        "android"   # TODO: Different architectures...
    ]

def get_vs_variants():
    vs_variants = []
    for (configuration) in configurations:
        for (vs_platform) in get_platforms():   
            vs_variants.append(configuration + '|' + vs_platform)
            
    return vs_variants
    
def get_vs_debug_settings():
    vs_debug_settings = []
    
    if platform.system() == "Windows":
        binary_file_name = "python.exe"
    else:
        binary_file_name = "python"

    # TODO: Pass $(Configuration) for architecture for arm32 and other configs...
    android_editor_command_arguments_to_install_and_run = "tools/scripts/android_install_and_run.py $(Configuration) arm64 single"
    android_editor_game_command_arguments_to_install_and_run = "tools/scripts/export_and_run.py android $(Configuration) arm64 single"    

    vs_debug_settings.extend([
        # android editor
        {
            'LocalDebuggerCommand': binary_file_name,
            'LocalDebuggerCommandArguments': android_editor_command_arguments_to_install_and_run
        },
        # android editor_game
        {
            'LocalDebuggerCommand': binary_file_name,
            'LocalDebuggerCommandArguments': android_editor_game_command_arguments_to_install_and_run
        },
        # android template_debug
        {
        },
        # android template_debug
        {
        },
        # android profile
        {
        },
        # android production
        {
        }
    ])
    
    return vs_debug_settings

def get_vs_cpp_defines():
    vs_cpp_defines = []
    
    vs_cpp_defines.extend([
        # android editor
        [
            "PLATFORM_ANDROID",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG"
        ],
        # android editor_game
        [
            "PLATFORM_ANDROID",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG"
        ],
        # android template_debug
        [
            "PLATFORM_ANDROID",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG"
        ],
        # android template_release
        [
            "PLATFORM_ANDROID",
            "RELEASE"
        ],
        # android profile
        [
            "PLATFORM_ANDROID",
            "PROFILE"
        ],
        # android production
        [
            "PLATFORM_ANDROID",
            "PRODUCTION"
        ]
    ])

    return vs_cpp_defines

def get_vs_cpp_flags():
    vs_cpp_flags = []
    
    vs_cpp_flags.extend([
        # android editor
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # android editor_game
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # android template_debug
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # android template_release
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # android profile
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # android production
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ]
    ])

    return vs_cpp_flags
