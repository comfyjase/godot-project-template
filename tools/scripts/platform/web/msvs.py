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
        "web"
    ]

def get_vs_variants():
    vs_variants = []
    for (configuration) in configurations:
        for (vs_platform) in get_platforms():
            vs_variants.append(configuration + '|' + vs_platform)
            
    return vs_variants

def get_vs_debug_settings():
    vs_debug_settings = []
    
    binary_file_name = ""
    if platform.system() == "Windows":
        binary_file_name = "python.exe"
    else:
        binary_file_name = "python"
    
    web_command_arguments_to_run_editor = "godot/platform/web/serve.py --root ../../bin/.web_zip"
    web_command_arguments_to_run_project_as_game = "tools/scripts/export_and_run.py web editor_game wasm32 single"    
    
    vs_debug_settings.extend([
        # web editor
        {
            'LocalDebuggerCommand': binary_file_name,
            'LocalDebuggerCommandArguments': web_command_arguments_to_run_editor
        },
        # web editor_game
        {
            'LocalDebuggerCommand': binary_file_name,
            'LocalDebuggerCommandArguments': web_command_arguments_to_run_project_as_game
        },
        # web template_debug
        {
        },
        # web template_release
        {
        },
        # web profile
        {
        },
        # web production
        {
        }
    ])
    
    return vs_debug_settings

def get_vs_cpp_defines():
    vs_cpp_defines = []
    
    vs_cpp_defines.extend([
        # web editor
        [
            "PLATFORM_WEB",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG"
        ],
        # web editor_game
        [
            "PLATFORM_WEB",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG"
        ],
        # web template_debug
        [
            "PLATFORM_WEB",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG"
        ],
        # web template_release
        [
            "PLATFORM_WEB",
            "RELEASE"
        ],
        # web profile
        [
            "PLATFORM_WEB",
            "PROFILE"
        ],
        # web production
        [
            "PLATFORM_WEB",
            "PRODUCTION"
        ]
    ])
    
    return vs_cpp_defines

def get_vs_cpp_flags():
    vs_cpp_flags = []
    
    vs_cpp_flags.extend([
        # web editor
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # web editor_game
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # web template_debug
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # web template_release
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # web profile
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # web production
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ]
    ])
    
    return vs_cpp_flags
