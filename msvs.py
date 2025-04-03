#!/usr/bin/env python

import os

from SCons.Script import *

# editor - run godot editor dev executable and pass --editor and --path
# editor_game - run godot editor dev executable and just pass --path
# template_debug - run the exported template_debug executable and then attach the visual studio instance to it.
# template_release - run the exported template_release executable and then attach the visual studio instance to it.
# profile - run the exported template_release executable (should be exported using production=yes and debugging_symbols=yes) and then attach the visual studio instance to it.
# production - run the exported template_release executable (should be exported using production=yes) and then attach the visual studio instance to it.

configurations = ["editor", "editor_game", "template_debug", "template_release", "profile", "production"]
platforms = [ "x64" ] # TODO: Add other platforms here, for example, if you are targeting consoles.

def set_vs_environment_variables(env):
    if not env.get('MSVS'):
        env["MSVS"]["PROJECTSUFFIX"] = ".vcxproj"    
        env["MSVS"]["SOLUTIONSUFFIX"] = ".sln"

def get_vs_variants():
    vs_variants = []
    for (configuration) in configurations:
        for (platform) in platforms:
            vs_variants.append(configuration + '|' + platform)    
    return vs_variants

def get_vs_debug_settings():
    editor_command = "\"$(SolutionDir)godot\\bin\\godot.windows.editor.dev.x86_64.exe\""
    command_arguments_to_open_project_in_editor = "--editor --path \"$(SolutionDir)game\""
    command_arguments_to_run_project_as_game = "--path \"$(SolutionDir)game\""
    return [
        # editor
        {
            'LocalDebuggerCommand': editor_command, 
            'LocalDebuggerCommandArguments': command_arguments_to_open_project_in_editor
        },
        # editor_game
        {
            'LocalDebuggerCommand': editor_command, 
            'LocalDebuggerCommandArguments': command_arguments_to_run_project_as_game
        },
        # template_debug
        {
        },
        # template_release
        {
        },
        # profile
        {
        },
        # production
        {
        }
    ]

def get_vs_cpp_defines():
    return [
        # editor
        [
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED"
        ],
        # editor_game
        [
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED"
        ],
        # template_debug
        [
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED"
        ],
        # template_release
        [
        ],
        # profile
        [
        ],
        # production
        [
        ]
    ]

def get_vs_cpp_flags():
    return [
        # editor
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # editor_game
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # template_debug
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # template_release
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # profile
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        # production
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ]
    ]

def generate_vs_project(env, source_files, include_files, resource_files, misc_files):
    set_vs_environment_variables(env)
    
    env["MSVSBUILDCOM"] = "call \"$(SolutionDir)tools\\scripts\\windows\\build.bat\" $(Configuration)"
    env["MSVSREBUILDCOM"] = "call \"$(SolutionDir)tools\\scripts\\windows\\clean.bat\" $(Configuration) && call \"$(SolutionDir)tools\\scripts\\windows\\build.bat\" $(Configuration)"
    env["MSVSCLEANCOM"] = "call \"$(SolutionDir)tools\\scripts\\windows\\clean.bat\" $(Configuration)"
    
    vcxproj_files = []

    project_file = env.MSVSProject(target = env["vsproj_name"] + env["MSVSPROJECTSUFFIX"],
                        srcs = source_files,
                        incs = include_files,
                        resources = resource_files,
                        misc = misc_files,
                        variant = get_vs_variants(),
                        DebugSettings=get_vs_debug_settings(),
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
    
    # Updating the godot project in this game project sln file to map the new configuration(s) (e.g. production configuration) to the relevant godot configuration
    with open(env["vsproj_name"] + ".sln", "w") as out_file:
        for line in lines:
            line_write_done = False
            for configuration in configurations:
                for platform in platforms:
                    if godot_project_unique_identifier + "." + configuration + "|" + platform + ".ActiveCfg" in line:
                        out_file.write("\t\t" + godot_project_unique_identifier + "." + configuration + "|" + platform + ".ActiveCfg = editor|" + platform + "\n")
                        line_write_done = True
                    elif godot_project_unique_identifier + "." + configuration + "|" + platform + ".Build.0" in line:
                        out_file.write("\t\t" + godot_project_unique_identifier + "." + configuration + "|" + platform + ".Build.0 = editor|" + platform + "\n")
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
