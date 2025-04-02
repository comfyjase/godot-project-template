#!/usr/bin/env python
import os
import sys

from methods import print_error
from methods import get_all_directories_recursive
from methods import get_all_files_recursive

from msvs import generate_vs_project
from msvs import generate_and_build_vs_solution

lib_name = "game"
project_dir = "game"

local_env = Environment(tools=["default"])

customs = ["custom.py"]
customs = [os.path.abspath(path) for path in customs]

configurations = ['template_debug', 'template_release']    

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

submodule_initialized = False
dir_name = 'godot-cpp'
if os.path.isdir(dir_name):
    if os.listdir(dir_name):
        submodule_initialized = True

if not submodule_initialized:
    print_error("""godot-cpp is not available within this folder, as Git submodules haven't been initialized.
Run the following command to download godot-cpp:

    git submodule update --init --recursive""")
    sys.exit(1)

env = SConscript("godot-cpp/SConstruct", {"env": env, "customs": customs})

if env["target"] in ["editor", "template_debug"]:
    try:
        doc_data = env.GodotCPPDocData("src/gen/doc_data.gen.cpp", source=Glob("doc_classes/*.xml", strings=True))
    except AttributeError:
        print("Not including class reference as we're targeting a pre-4.3 baseline.")

env.Append(CPPPATH=get_all_directories_recursive("src/"))
sources = get_all_files_recursive("src/", "*.cpp")
includes = get_all_files_recursive("src/", "*.h")

file = "{}{}{}".format(lib_name, env["suffix"], env["SHLIBSUFFIX"])
filepath = ""

if env["platform"] == "macos" or env["platform"] == "ios":
    filepath = "{}.framework/".format(env["platform"])
    file = "{}{}".format(lib_name, env["suffix"])

libraryfile = "bin/{}/{}{}".format(env["platform"], filepath, file)
library = env.SharedLibrary(
    libraryfile,
    source=sources,
)

copy = env.InstallAs("{}/bin/{}/{}lib{}".format(project_dir, env["platform"], filepath, file), library)

if env["vsproj"]:
    platforms = [ "x64" ]
    
    misc_files = get_all_files_recursive("godot-cpp/gdextension/", "*.h")
    misc_files.extend(get_all_files_recursive("godot-cpp/gen/include/", "*.hpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/gen/src/", "*.cpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/include/", "*.hpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/src/", "*.cpp"))
    
    game_project_file = generate_vs_project(env, env["vsproj_name"], configurations, platforms, sources, includes, misc_files)
        
    vcxproj_files = []
    vcxproj_files.append(game_project_file)
    
    game_solution_file = generate_and_build_vs_solution(env, env["vsproj_name"], configurations, platforms, vcxproj_files)
else:
    default_args = [library, copy]
    Default(*default_args)
