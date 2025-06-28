#!/usr/bin/env python

import os
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from tools.scripts.system import *

def get_platforms():
    return [
        "Win32",
        "x64"
    ]

def get_vs_variants():
    vs_variants = []
    for (configuration) in configurations:
        for (vs_platform) in get_platforms():
            vs_variants.append(configuration + '|' + vs_platform)
            
    return vs_variants

def get_vs_debug_settings():
    vs_debug_settings = []
    
    command_arguments_to_open_project_in_editor = "--editor --path \"$(SolutionDir)game\""
    command_arguments_to_run_project_as_game = "--path \"$(SolutionDir)game\""
    
    binary_file_names = [
        "godot.windows.editor.dev.x86_32",
        "godot.windows.editor.dev.x86_64",
    ]
    
    vs_debug_settings.extend([
        # Win32 editor
        {
            'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{binary_file_names[0]}", 
            'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
        },
        # x64 editor
        {
            'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{binary_file_names[1]}",
            'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
        },
        # Win32 editor_game
        {
            'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{binary_file_names[0]}",
            'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
        },
        # x64 editor_game
        {
            'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{binary_file_names[1]}",
            'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
        },
        # Win32 development
        {
        },
        # x64 development
        {
        },
        # Win32 template_debug
        {
        },
        # x64 template_debug
        {
        },
        # Win32 template_release
        {
        },
        # x64 template_release
        {
        },
        # Win32 profile
        {
        },
        # x64 profile
        {
        },
        # Win32 production
        {
        },
        # x64 production
        {
        }
    ])
    
    return vs_debug_settings

def get_vs_cpp_defines():
    vs_cpp_defines = []
    
    vs_cpp_defines.extend([
        # Win32 editor
        [
            "PLATFORM_WINDOWS",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # x64 editor
        [
            "PLATFORM_WINDOWS",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # Win32 editor_game
        [
            "PLATFORM_WINDOWS",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # x64 editor_game
        [
            "PLATFORM_WINDOWS",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # Win32 development
        [
            "PLATFORM_WINDOWS",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # x64 development
        [
            "PLATFORM_WINDOWS",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # Win32 template_debug
        [
            "PLATFORM_WINDOWS",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # x64 template_debug
        [
            "PLATFORM_WINDOWS",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED",
            "DEBUG",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # Win32 template_release
        [
            "PLATFORM_WINDOWS",
            "RELEASE",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # x64 template_release
        [
            "PLATFORM_WINDOWS",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "RELEASE",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # Win32 profile
        [
            "PLATFORM_WINDOWS",
            "PROFILE",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # x64 profile
        [
            "PLATFORM_WINDOWS",
            'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
            "IMGUI_ENABLED",
            "PROFILE",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # Win32 production
        [
            "PLATFORM_WINDOWS",
            "PRODUCTION",
            "DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS"
        ],
        # x64 production
        [
            "PLATFORM_WINDOWS",
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
        # Win32 editor
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # x64 editor
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # Win32 editor_game
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # x64 editor_game
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # Win32 development
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # x64 development
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # Win32 template_debug
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # x64 template_debug
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # Win32 template_release
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # x64 template_release
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # Win32 profile
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # x64 profile
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # Win32 production
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # x64 production
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ]
    ])
    
    return vs_cpp_flags
