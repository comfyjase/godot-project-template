#!/usr/bin/env python
import os
import platform
import sys

import tools.scripts.system as system

from methods import *
from tools.scripts.msvs import *
from tools.scripts.options import *

local_env = Environment(tools=["default"], PLATFORM="")

customs = ["custom.py"]
customs = [os.path.abspath(path) for path in customs]

opts = Variables(customs, ARGUMENTS)
init_system_variables(ARGUMENTS)
init_options(local_env, opts, lib_name)
opts.Update(local_env)

cache_path = local_env["cache_path"]
if cache_path == "":
    cache_path = ".scons_cache"
CacheDir(cache_path)

Help(opts.GenerateHelpText(local_env))

# To use MSVSProject/MSVSSolution the default system platform needs to be used
# The PLATFORM="" above in the default environment removes any platform specific tools
# and prevents the MSVS functions from working.
# Cloning another environment here where PLATFORM = system default fixes this issue when
# the user wants to generate a '.sln' file.
environment_to_clone = local_env
if local_env["vsproj"]:
    environment_to_clone = Environment(tools=["default"])
    opts.Update(environment_to_clone)

env = environment_to_clone.Clone()

if not is_submodule_initialized(system.engine_godot_dir):
    sys.exit(1)
if not is_submodule_initialized(system.engine_godot_cpp_dir):
    sys.exit(1)
if not is_submodule_initialized(system.thirdparty_imgui_dir_path):
    sys.exit(1)

# Convert from game configuration to something godot/godot-cpp understands
game_target = env["target"]
if game_target in ["editor_game", "development"]:
    env["target"] = "editor"
elif game_target == "profile":
    env["target"] = "template_release"
elif game_target == "production":
    env["target"] = "template_release"

ARGUMENTS["target"] = env["target"]

env = SConscript(os.path.join(system.engine_godot_cpp_dir, "SConstruct"), {"env": env, "customs": customs})

# Then convert back to the original target value
env["target"] = game_target
ARGUMENTS["target"] = env["target"]

if env["target"] in ["editor", "editor_game", "development", "template_debug"]:
    try:
        doc_data = env.GodotCPPDocData(os.path.join(system.project_src_dir, "gen", "doc_data.gen.cpp"), source=Glob("doc_classes/*.xml", strings=True))
    except AttributeError:
        print("Not including class reference as we're targeting a pre-4.4 baseline.")

all_directories = []
all_source_files = []
project_source_files = []
all_include_files = []
cpp_defines = []

# imgui
system.add_imgui(env, all_directories, all_source_files, project_source_files, all_include_files, cpp_defines)

# tests
system.add_doctest(all_directories, all_include_files)

# godot-cpp
all_directories.extend(get_all_directories_recursive(system.godot_cpp_extension_dir_path))
all_directories.extend(get_all_directories_recursive(system.godot_cpp_gen_include_dir_path))
all_directories.extend(get_all_directories_recursive(system.godot_cpp_gen_src_dir_path))
all_directories.extend(get_all_directories_recursive(system.godot_cpp_include_dir_path))
all_directories.extend(get_all_directories_recursive(system.godot_cpp_src_dir_path))

all_include_files.extend(get_all_files_recursive(system.godot_cpp_extension_dir_path, "*.h"))
all_include_files.extend(get_all_files_recursive(system.godot_cpp_gen_include_dir_path, "*.hpp"))
all_source_files.extend(get_all_files_recursive(system.godot_cpp_gen_src_dir_path, "*.cpp"))
all_include_files.extend(get_all_files_recursive(system.godot_cpp_include_dir_path, "*.hpp"))
all_source_files.extend(get_all_files_recursive(system.godot_cpp_src_dir_path, "*.cpp"))

# project
all_directories.extend(get_all_directories_recursive(system.project_src_dir))
all_source_files.extend(get_all_files_recursive(system.project_src_dir, "*.cpp"))
project_source_files.extend(get_all_files_recursive(system.project_src_dir, "*.cpp"))
all_include_files.extend(get_all_files_recursive(system.project_src_dir, "*.h"))
system.add_cpp_defines(env, cpp_defines)

# Add plugins
system.add_plugins(system.project_plugins, env, customs, all_directories, project_source_files, all_source_files, all_include_files)

env.Append(CPPPATH=all_directories)
env.Append(CPPDEFINES=cpp_defines)

# Fixing warnings for LNK4099: PDB '' was not found with...
# This is only needed for CI purposes but included in the main build
# to avoid having to add extra CI build parameter in this script
if env["platform"] == "windows":
    env.Append(LINKFLAGS=["/ignore:4099"])

# .dev doesn't inhibit compatibility, so we don't need to key it.
# .universal just means "compatible with all relevant arches" so we don't need to key it.
suffix = env['suffix'].replace(".dev", "").replace(".universal", "")
library_suffix = env.subst('$SHLIBSUFFIX')
if platform.system() == "Linux" and env["platform"] == "macos":
    library_suffix = ".dylib"
lib_filename = "{}{}{}{}".format(env.subst('$SHLIBPREFIX'), lib_name, suffix, library_suffix)
if platform.system() == "Windows" and (env["platform"] in ["web", "android"]):
    lib_filename = "lib" + lib_filename

library = env.SharedLibrary(
    "bin/{}/{}".format(env['platform'], lib_filename),
    source=project_source_files,
)

copy = env.Install("{}/bin/{}/".format(project_dir_name, env["platform"]), library)

if env["vsproj"]:
    init_msvs()
    
    resource_files = []
    misc_files = []
    
    misc_files.append(".runsettings")
    misc_files.append(".editorconfig")
    
    game_project_file = generate_vs_project(env, all_source_files, all_include_files, resource_files, misc_files)
    env.NoCache(game_project_file)
    
    vcxproj_files = []
    vcxproj_files.append(os.path.join(system.engine_godot_dir, "godot.vcxproj"))
    vcxproj_files.append(game_project_file)
    
    game_solution_file = generate_vs_solution(env, vcxproj_files)
    env.NoCache(game_solution_file)
else:
    default_args = [library, copy]
    Default(*default_args)
