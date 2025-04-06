#!/usr/bin/env python
import os
import sys

from methods import *

from msvs import configurations
from msvs import generate_vs_project
from msvs import generate_and_build_vs_solution

lib_name = "game"
project_dir = "game"

local_env = Environment(tools=["default"])

customs = ["custom.py"]
customs = [os.path.abspath(path) for path in customs]

opts = Variables(customs, ARGUMENTS)

opts.Add(BoolVariable("vsproj", "Generate a Visual Studio solution", False))
opts.Add("vsproj_name", "Name of the Visual Studio solution", lib_name)

# What configuration target to use for compiling with
# Defaults to template_debug if not specified
opts.Add(
    EnumVariable(
        key="target",
        help="Compilation target",
        default=local_env.get("target", configurations[0]),
        allowed_values=(configurations),
    )
)

opts.Update(local_env)

Help(opts.GenerateHelpText(local_env))

env = local_env.Clone()

dir_name = 'godot'
if not is_submodule_initialized(dir_name):
    sys.exit(1)
dir_name = 'godot-cpp'
if not is_submodule_initialized(dir_name):
    sys.exit(1)
dir_name = 'thirdparty/imgui'
if not is_submodule_initialized(dir_name):
    sys.exit(1)

env = SConscript("godot-cpp/SConstruct", {"env": env, "customs": customs})

if env["target"] in ["editor", "editor_game", "template_debug"]:
    try:
        doc_data = env.GodotCPPDocData("src/gen/doc_data.gen.cpp", source=Glob("doc_classes/*.xml", strings=True))
    except AttributeError:
        print("Not including class reference as we're targeting a pre-4.3 baseline.")

# imgui
all_directories = ["game/addons/imgui-godot/include", "thirdparty/imgui" ]
source_files = Glob("thirdparty/imgui/*.cpp", strings=True)
include_files = Glob("thirdparty/imgui/*.h", strings=True)
cpp_defines = [ 'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""', "IMGUI_ENABLED" ]

# game
all_directories.extend(get_all_directories_recursive("src/"))
source_files.extend(get_all_files_recursive("src/", "*.cpp"))
include_files.extend(get_all_files_recursive("src/", "*.h"))
if env["target"] in ["editor", "editor_game", "template_debug"]:
    cpp_defines.append("TOOLS_ENABLED")
    cpp_defines.append("DEBUG_ENABLED")
    cpp_defines.append("TESTS_ENABLED")

env.Append(CPPPATH=all_directories)
env.Append(CPPDEFINES=cpp_defines)

file = "{}{}{}".format(lib_name, env["suffix"], env["SHLIBSUFFIX"])
filepath = ""

if env["platform"] == "macos" or env["platform"] == "ios":
    filepath = "{}.framework/".format(env["platform"])
    file = "{}{}".format(lib_name, env["suffix"])

libraryfile = "bin/{}/{}{}".format(env["platform"], filepath, file)
library = env.SharedLibrary(
    libraryfile,
    source=source_files,
)

copy = env.InstallAs("{}/bin/{}/{}lib{}".format(project_dir, env["platform"], filepath, file), library)

if env["vsproj"]:    
    resource_files = []
    
    misc_files = get_all_files_recursive("godot-cpp/gdextension/", "*.h")
    misc_files.extend(get_all_files_recursive("godot-cpp/gen/include/", "*.hpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/gen/src/", "*.cpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/include/", "*.hpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/src/", "*.cpp"))
    misc_files.append(".runsettings")
    
    game_project_file = generate_vs_project(env, source_files, include_files, resource_files, misc_files)
        
    vcxproj_files = []
    vcxproj_files.append("godot/godot.vcxproj")
    vcxproj_files.append(game_project_file)
    
    game_solution_file = generate_and_build_vs_solution(env, vcxproj_files)
else:
    default_args = [library, copy]
    Default(*default_args)
