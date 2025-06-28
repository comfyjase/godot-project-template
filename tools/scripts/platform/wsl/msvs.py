#!/usr/bin/env python

import os
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from tools.scripts.system import *

def get_platforms():
    return [
        "linux"
    ]

def get_vs_variants():
    vs_variants = []
    for (configuration) in configurations:
        for (vs_platform) in get_platforms():
            vs_variants.append(configuration + '|' + vs_platform)
            
    return vs_variants

def get_vs_debug_settings():
    vs_debug_settings = []
    
    binary_file_name = "godot.linuxbsd.editor.dev.x86_64"
      
    wsl_command_arguments_to_open_project_in_editor = f"./godot/bin/{binary_file_name} --editor --path \"game\""
    wsl_command_arguments_to_run_project_as_game = f"./godot/bin/{binary_file_name} --path \"game\""
    
    vs_debug_settings.extend([
        # linux editor
        {
            'LocalDebuggerCommand': "wsl.exe",
            'LocalDebuggerCommandArguments': wsl_command_arguments_to_open_project_in_editor
        },
        # linux editor_game
        {
            'LocalDebuggerCommand': "wsl.exe",
            'LocalDebuggerCommandArguments': wsl_command_arguments_to_run_project_as_game
        },
        # linux development
        {
        },
        # linux template_debug
        {
        },
        # linux template_release
        {
        },
        # linux profile
        {
        },
        # linux production
        {
        }
    ])

    return vs_debug_settings

def get_vs_cpp_defines():
    vs_cpp_defines = []
    
    vs_cpp_defines.extend([
        # linux editor
        [
            "PLATFORM_LINUX",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # linux editor_game
        [
            "PLATFORM_LINUX",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # linux development
        [
            "PLATFORM_LINUX",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # linux template_debug
        [
            "PLATFORM_LINUX",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # linux template_release
        [
            "PLATFORM_LINUX",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "RELEASE",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # linux profile
        [
            "PLATFORM_LINUX",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "PROFILE",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # linux production
        [
            "PLATFORM_LINUX",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "PRODUCTION",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ]
    ])
    return vs_cpp_defines

def get_vs_cpp_flags():
    vs_cpp_flags = []
    
    vs_cpp_flags.extend([
        # linux editor
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # linux editor_game
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # linux development
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # linux template_debug
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # linux template_release
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # linux profile
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # linux production
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ]
    ])

    return vs_cpp_flags
