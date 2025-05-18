#!/usr/bin/env python

import os
import platform
import subprocess
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
script_path_to_append = os.path.join(script_directory, "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from SCons.Script import *
from tools.scripts.system import *

import tools.scripts.platform.windows.msvs
import tools.scripts.platform.wsl.msvs
import tools.scripts.platform.web.msvs
import tools.scripts.platform.android.msvs

vs_platforms = []

def init_msvs():
    global vs_platforms
    
    vs_platforms.extend(tools.scripts.platform.windows.msvs.get_platforms())
    vs_platforms.extend(tools.scripts.platform.wsl.msvs.get_platforms())
    vs_platforms.extend(tools.scripts.platform.web.msvs.get_platforms())
    vs_platforms.extend(tools.scripts.platform.android.msvs.get_platforms())

def set_vs_environment_variables(env):
    if not env.get('MSVS'):
        env["MSVS"]["PROJECTSUFFIX"] = ".vcxproj"    
        env["MSVS"]["SOLUTIONSUFFIX"] = ".sln"

def get_vs_variants():
    vs_variants = []
    
    vs_variants.extend(tools.scripts.platform.windows.msvs.get_vs_variants())
    vs_variants.extend(tools.scripts.platform.wsl.msvs.get_vs_variants())
    vs_variants.extend(tools.scripts.platform.web.msvs.get_vs_variants())
    vs_variants.extend(tools.scripts.platform.android.msvs.get_vs_variants())
    
    return vs_variants

def get_vs_debug_settings():
    vs_debug_settings = []
    
    vs_debug_settings.extend(tools.scripts.platform.windows.msvs.get_vs_debug_settings())
    vs_debug_settings.extend(tools.scripts.platform.wsl.msvs.get_vs_debug_settings())
    vs_debug_settings.extend(tools.scripts.platform.web.msvs.get_vs_debug_settings())
    vs_debug_settings.extend(tools.scripts.platform.android.msvs.get_vs_debug_settings())
    
    return vs_debug_settings

def get_vs_cpp_defines():
    vs_cpp_defines = []
    
    vs_cpp_defines.extend(tools.scripts.platform.windows.msvs.get_vs_cpp_defines())
    vs_cpp_defines.extend(tools.scripts.platform.wsl.msvs.get_vs_cpp_defines())
    vs_cpp_defines.extend(tools.scripts.platform.web.msvs.get_vs_cpp_defines())
    vs_cpp_defines.extend(tools.scripts.platform.android.msvs.get_vs_cpp_defines())
    
    return vs_cpp_defines

def get_vs_cpp_flags():
    vs_cpp_flags = []
    
    vs_cpp_flags.extend(tools.scripts.platform.windows.msvs.get_vs_cpp_flags())
    vs_cpp_flags.extend(tools.scripts.platform.wsl.msvs.get_vs_cpp_flags())
    vs_cpp_flags.extend(tools.scripts.platform.web.msvs.get_vs_cpp_flags())
    vs_cpp_flags.extend(tools.scripts.platform.android.msvs.get_vs_cpp_flags())
    
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
                    if wsl_available:
                        if godot_platform == "linux":
                            godot_platform = "x64"  # Convert to map to Win64 instead since the godot engine project doesn't have a windows -> linux config mapping
                    if godot_platform in ["web", "android"]:
                        godot_platform = "x64"
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
