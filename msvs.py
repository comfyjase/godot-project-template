#!/usr/bin/env python

import os
import platform
import subprocess
import sys

from SCons.Script import *

# editor - run godot editor dev executable and pass --editor and --path
# editor_game - run godot editor dev executable and just pass --path
# template_debug - run the exported template_debug executable and then attach the visual studio instance to it.
# template_release - run the exported template_release executable and then attach the visual studio instance to it.
# profile - run the exported template_release executable (should be exported using production=yes and debugging_symbols=yes) and then attach the visual studio instance to it.
# production - run the exported template_release executable (should be exported using production=yes) and then attach the visual studio instance to it.

configurations = ["editor", "editor_game", "template_debug", "template_release", "profile", "production"]
vs_platforms = []

is_os_64_bit = sys.maxsize > 2**32

using_wsl = False

if platform.system() == "Linux":
    vs_platforms = [ "linux" ]
elif platform.system() == "Darwin":
    vs_platforms = [ "macos" ]
elif platform.system() == "Windows":
    if is_os_64_bit:
        vs_platforms = [ "Win32", "x64" ]
        wsl_install_output = subprocess.check_output(f"wsl -l -v").decode('ascii').strip()
        if "Windows subsystem for Linux has no installed distributions" not in wsl_install_output:
            using_wsl = True
            vs_platforms.append("linux")
    else:
        vs_platforms = [ "Win32" ]

def set_vs_environment_variables(env):
    if not env.get('MSVS'):
        env["MSVS"]["PROJECTSUFFIX"] = ".vcxproj"    
        env["MSVS"]["SOLUTIONSUFFIX"] = ".sln"

def get_vs_variants():
    vs_variants = []
    for (configuration) in configurations:
        for (platform) in vs_platforms:
            vs_variants.append(configuration + '|' + platform)
    return vs_variants

def get_vs_debug_settings():
    vs_debug_settings = []
    
    command_arguments_to_open_project_in_editor = "--editor --path \"$(SolutionDir)game\""
    command_arguments_to_run_project_as_game = "--path \"$(SolutionDir)game\""
    
    godot_binary_file_names = []
    for (platform) in vs_platforms:
        godot_platform = platform
        architecture = "x86_64"
        
        if platform == "Win32":
            godot_platform = "windows"
            architecture = "x86_32"
        elif platform == "x64":
            godot_platform = "windows"
            
        godot_binary_file_name = f"godot.{godot_platform}.editor.dev.{architecture}"
        if godot_platform == "windows":
            godot_binary_file_name += ".exe"
        elif godot_platform == "linux":
            godot_binary_file_name = godot_binary_file_name.replace("linux", "linuxbsd")
        
        godot_binary_file_names.append(godot_binary_file_name)
    
    if is_os_64_bit:
        if using_wsl:
            wsl_command_arguments_to_open_project_in_editor = f"./godot/bin/{godot_binary_file_names[2]} --editor --path \"game\""
            wsl_command_arguments_to_run_project_as_game = f"./godot/bin/{godot_binary_file_names[2]} --path \"game\""
            
            vs_debug_settings.extend([
                # Win32 editor
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[0]}", 
                    'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
                },
                # x64 editor
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[1]}",
                    'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
                },
                # linux editor
                {
                    'LocalDebuggerCommand': "wsl.exe",
                    'LocalDebuggerCommandArguments': wsl_command_arguments_to_open_project_in_editor
                },
                # Win32 editor_game
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[0]}",
                    'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
                },
                # x64 editor_game
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[1]}",
                    'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
                },
                # linux editor_game
                {
                    'LocalDebuggerCommand': "wsl.exe",
                    'LocalDebuggerCommandArguments': wsl_command_arguments_to_run_project_as_game
                },
                # Win32 template_debug
                {
                },
                # x64 template_debug
                {
                },
                # linux template_debug
                {
                },
                # Win32 template_release
                {
                },
                # x64 template_release
                {
                },
                # linux template_release
                {
                },
                # Win32 profile
                {
                },
                # x64 profile
                {
                },
                # linux profile
                {
                },
                # Win32 production
                {
                },
                # x64 production
                {
                },
                # linux production
                {
                }
            ])
        else:
            vs_debug_settings.extend([
                # Win32 editor
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[0]}", 
                    'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
                },
                # x64 editor
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[1]}",
                    'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
                },
                # Win32 editor_game
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[0]}", 
                    'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
                },
                # x64 editor_game
                {
                    'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[1]}", 
                    'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
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
    else:
        vs_debug_settings.extend([
            # Win32 editor
            {
                'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[0]}", 
                'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
            },
            # Win32 editor_game
            {
                'LocalDebuggerCommand': f"$(SolutionDir)godot/bin/{godot_binary_file_names[0]}", 
                'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
            },
            # Win32 template_debug
            {
            },
            # Win32 template_release
            {
            },
            # Win32 profile
            {
            },
            # Win32 production
            {
            }
        ])
    
    return vs_debug_settings

def get_vs_cpp_defines():
    vs_cpp_defines = []
    
    if is_os_64_bit:
        if using_wsl:
            vs_cpp_defines.extend([
                # Win32 editor
                [
                    "PLATFORM_WIN32",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # x64 editor
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # linux editor
                [
                    "PLATFORM_LINUX",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # Win32 editor_game
                [
                    "PLATFORM_WIN32",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # x64 editor_game
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # linux editor_game
                [
                    "PLATFORM_LINUX",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # Win32 template_debug
                [
                    "PLATFORM_WIN32",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # x64 template_debug
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # linux template_debug
                [
                    "PLATFORM_LINUX",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # Win32 template_release
                [
                    "PLATFORM_WIN32",
                    "RELEASE"
                ],
                # x64 template_release
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "RELEASE"
                ],
                # linux template_release
                [
                    "PLATFORM_LINUX",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "RELEASE"
                ],
                # Win32 profile
                [
                    "PLATFORM_WIN32",
                    "PROFILE"
                ],
                # x64 profile
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "PROFILE"
                ],
                # linux profile
                [
                    "PLATFORM_LINUX",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "PROFILE"
                ],
                # Win32 production
                [
                    "PLATFORM_WIN32",
                    "PRODUCTION"
                ],
                # x64 production
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "PRODUCTION"
                ],
                # linux production
                [
                    "PLATFORM_LINUX",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "PRODUCTION"
                ]
            ])
        else:
            vs_cpp_defines.extend([
                # Win32 editor
                [
                    "PLATFORM_WIN32",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # x64 editor
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # Win32 editor_game
                [
                    "PLATFORM_WIN32",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # x64 editor_game
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # Win32 template_debug
                [
                    "PLATFORM_WIN32",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # x64 template_debug
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "TOOLS_ENABLED",
                    "DEBUG_ENABLED",
                    "TESTS_ENABLED",
                    "DEBUG"
                ],
                # Win32 template_release
                [
                    "PLATFORM_WIN32",
                    "RELEASE"
                ],
                # x64 template_release
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "RELEASE"
                ],
                # Win32 profile
                [
                    "PLATFORM_WIN32",
                    "PROFILE"
                ],
                # x64 profile
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "PROFILE"
                ],
                # Win32 production
                [
                    "PLATFORM_WIN32",
                    "PRODUCTION"
                ],
                # x64 production
                [
                    "PLATFORM_WIN64",
                    'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""',
                    "IMGUI_ENABLED",
                    "PRODUCTION"
                ]
            ])
    else:
        vs_cpp_defines.extend([
            # Win32 editor
            [
                "PLATFORM_WIN32",
                "TOOLS_ENABLED",
                "DEBUG_ENABLED",
                "TESTS_ENABLED",
                "DEBUG"
            ],
            # Win32 editor_game
            [
                "PLATFORM_WIN32",
                "TOOLS_ENABLED",
                "DEBUG_ENABLED",
                "TESTS_ENABLED",
                "DEBUG"
            ],
            # Win32 template_debug
            [
                "PLATFORM_WIN32",
                "TOOLS_ENABLED",
                "DEBUG_ENABLED",
                "TESTS_ENABLED",
                "DEBUG"
            ],
            # Win32 template_release
            [
                "PLATFORM_WIN32",
                "RELEASE"
            ],
            # Win32 profile
            [
                "PLATFORM_WIN32",
                "PROFILE"
            ],
            # Win32 production
            [
                "PLATFORM_WIN32",
                "PRODUCTION"
            ]
        ])

    return vs_cpp_defines

def get_vs_cpp_flags():
    vs_cpp_flags = []
    
    if is_os_64_bit:
        if using_wsl:
            vs_cpp_flags.extend([
                # Win32 editor
                [
                    "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
                ],
                # x64 editor
                [
                    "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
                ],
                # linux editor
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
                # linux editor_game
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
                # linux template_debug
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
                # linux template_release
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
                # linux profile
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
                ],
                # linux production
                [
                    "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
                ]
            ])
        else:
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
    else:
        vs_cpp_flags.extend([
            # Win32 editor
            [
                "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
            ],
            # Win32 editor_game
            [
                "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
            ],
            # Win32 template_debug
            [
                "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
            ],
            # Win32 template_release
            [
                "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
            ],
            # Win32 profile
            [
                "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
            ],
            # Win32 production
            [
                "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
            ]
        ])

    return vs_cpp_flags

def generate_vs_project(env, source_files, include_files, resource_files, misc_files):
    set_vs_environment_variables(env)
    
    env["MSVSBUILDCOM"] = "python \"$(SolutionDir)tools\\scripts\\build.py\" $(Platform) $(Configuration) $(Platform) single"
    env["MSVSREBUILDCOM"] = "python \"$(SolutionDir)tools\\scripts\\clean.py\" $(Platform) $(Configuration) $(Platform) single && python \"$(SolutionDir)tools\\scripts\\build.py\" $(Platform) $(Configuration) $(Platform) single"
    env["MSVSCLEANCOM"] = "python \"$(SolutionDir)tools\\scripts\\clean.py\" $(Platform) $(Configuration) $(Platform) single"
    
    vcxproj_files = []

    project_file = env.MSVSProject(target = env["vsproj_name"] + env["MSVSPROJECTSUFFIX"],
                        srcs = source_files,
                        incs = include_files,
                        resources = resource_files,
                        misc = misc_files,
                        variant = get_vs_variants(),
                        DebugSettings = get_vs_debug_settings(),
                        cppdefines = get_vs_cpp_defines(),
                        cppflags = get_vs_cpp_flags(),
                        auto_build_solution=0)
    
    return project_file

def update_vs_solution_file(target, source, env):
    set_vs_environment_variables(env)
    
    lines = []
    
    godot_project_unique_identifier = ""
    
    # Read all lines in sln file
    # ["MSVSSOLUTIONSUFFIX"] gives ${GET_MSVSSOLUTIONSUFFIX} which throws an error, so just using the file extension directly here.
    with open(env["vsproj_name"] + ".sln", "r") as in_file:
        lines = in_file.readlines()
        for line in lines:
            if "godot.vcxproj" in line:
                split_line = line.split(", ")
                godot_project_unique_identifier = split_line[-1].replace('"', '').replace('\n', '')
    
    # Updating the godot project in this game project sln file to map the new game configuration(s) to the relevant godot configuration (always editor in this instance)
    with open(env["vsproj_name"] + ".sln", "w") as out_file:
        for line in lines:
            line_write_done = False
            for configuration in configurations:
                for vs_platform in vs_platforms:
                    godot_platform = vs_platform
                    if using_wsl:
                        if godot_platform == "linux":
                            godot_platform = "x64"  # Convert to map to Win64 instead since the godot engine project doesn't have a windows -> linux config mapping
                    if godot_project_unique_identifier + "." + configuration + "|" + vs_platform + ".ActiveCfg" in line:
                        out_file.write("\t\t" + godot_project_unique_identifier + "." + configuration + "|" + vs_platform + ".ActiveCfg = editor|" + godot_platform + "\n")
                        line_write_done = True
                    elif godot_project_unique_identifier + "." + configuration + "|" + vs_platform + ".Build.0" in line:
                        out_file.write("\t\t" + godot_project_unique_identifier + "." + configuration + "|" + vs_platform + ".Build.0 = editor|" + godot_platform + "\n")
                        line_write_done = True
            if line_write_done == False:
                out_file.write(line)
    
def generate_and_build_vs_solution(env, vcxproj_files):
    set_vs_environment_variables(env)
    
    solution_file = env.MSVSSolution(target = env["vsproj_name"] + env["MSVSSOLUTIONSUFFIX"], 
                        projects = vcxproj_files,
                        variant = get_vs_variants())

    AddPostAction(solution_file, update_vs_solution_file)
    
    return solution_file
