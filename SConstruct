#!/usr/bin/env python
import os
import sys

from methods import *
from msvs import *

lib_name = "game"
project_dir = "game"

local_env = Environment(tools=["default"], PLATFORM="")

customs = ["custom.py"]
customs = [os.path.abspath(path) for path in customs]

opts = Variables(customs, ARGUMENTS)

platforms = ["linux", "macos", "windows", "android", "ios", "web"]

# CPU architecture options.
architecture_array = [
    "",
    "universal",
    "x86_32",
    "x86_64",
    "arm32",
    "arm64",
    "rv64",
    "ppc32",
    "ppc64",
    "wasm32",
]

architecture_aliases = {
    "x64": "x86_64",
    "amd64": "x86_64",
    "armv7": "arm32",
    "armv8": "arm64",
    "arm64v8": "arm64",
    "aarch64": "arm64",
    "rv": "rv64",
    "riscv": "rv64",
    "riscv64": "rv64",
    "ppcle": "ppc32",
    "ppc": "ppc32",
    "ppc64le": "ppc64",
}

if sys.platform.startswith("linux"):
    default_platform = "linux"
elif sys.platform == "darwin":
    default_platform = "macos"
elif sys.platform == "win32" or sys.platform == "msys":
    default_platform = "windows"
elif ARGUMENTS.get("platform", ""):
    default_platform = ARGUMENTS.get("platform")
else:
    raise ValueError("Could not detect platform automatically, please specify with platform=<platform>")

opts.Add(
    EnumVariable(
        key="platform",
        help="Target platform",
        default=local_env.get("platform", default_platform),
        allowed_values=platforms,
        ignorecase=2,
    )
)
opts.Add(
    EnumVariable(
        key="target",
        help="Compilation target",
        default=local_env.get("target", configurations[0]),
        allowed_values=(configurations),
    )
)
opts.Add(
    EnumVariable(
        key="precision",
        help="Set the floating-point precision level",
        default=local_env.get("precision", "single"),
        allowed_values=("single", "double"),
    )
)
opts.Add(
    EnumVariable(
        key="arch",
        help="CPU architecture",
        default=local_env.get("arch", ""),
        allowed_values=architecture_array,
        map=architecture_aliases,
    )
)
opts.Add(BoolVariable("vsproj", "Generate a Visual Studio solution", False))
opts.Add("vsproj_name", "Name of the Visual Studio solution", lib_name)
opts.Add(BoolVariable("debug_symbols", "Build with debugging symbols", True))
opts.Add(BoolVariable("dev_build", "Developer build with dev-only debugging code (DEV_ENABLED)", False))
opts.Add(BoolVariable("production", "Used for shipping a build", False))

opts.Update(local_env)

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

dir_name = 'godot'
if not is_submodule_initialized(dir_name):
    sys.exit(1)
dir_name = 'godot-cpp'
if not is_submodule_initialized(dir_name):
    sys.exit(1)
dir_name = 'thirdparty/imgui'
if not is_submodule_initialized(dir_name):
    sys.exit(1)

# Convert from game configuration to something godot/godot-cpp understands
game_target = env["target"]
if game_target == "editor_game":
    env["target"] = "editor"
elif game_target == "profile":
    env["target"] = "template_release"
elif game_target == "production":
    env["target"] = "template_release"

ARGUMENTS["target"] = env["target"]

env = SConscript("godot-cpp/SConstruct", {"env": env, "customs": customs})

# Then convert back to the original target value
env["target"] = game_target
ARGUMENTS["target"] = env["target"]

if env["target"] in ["editor", "editor_game", "template_debug"]:
    try:
        doc_data = env.GodotCPPDocData("src/gen/doc_data.gen.cpp", source=Glob("doc_classes/*.xml", strings=True))
    except AttributeError:
        print("Not including class reference as we're targeting a pre-4.3 baseline.")

all_directories = []
source_files = []
include_files = []
cpp_defines = []

# imgui
should_include_imgui = (env["arch"] != "x86_32") and (env["platform"] not in ["web", "android", "ios"])
if should_include_imgui:
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

if env["platform"] == "windows":
    if env["arch"] == "x86_64":
        cpp_defines.append("PLATFORM_WIN64")
    else:
        cpp_defines.append("PLATFORM_WIN32")
elif env["platform"] == "linux":
    cpp_defines.append("PLATFORM_LINUX")
elif env["platform"] == "macos":
    cpp_defines.append("PLATFORM_MACOS")
elif env["platform"] == "android":
    cpp_defines.append("PLATFORM_ANDROID")
elif env["platform"] == "ios":
    cpp_defines.append("PLATFORM_IOS")
elif env["platform"] == "web":
    cpp_defines.append("PLATFORM_WEB")
    
if env["target"] == "production":
    cpp_defines.append("PRODUCTION")
elif env["target"] == "profile":
    cpp_defines.append("PROFILE")
elif env["target"] == "template_release":
    cpp_defines.append("RELEASE")
else:
    cpp_defines.append("DEBUG")

env.Append(CPPPATH=all_directories)
env.Append(CPPDEFINES=cpp_defines)

# .dev doesn't inhibit compatibility, so we don't need to key it.
# .universal just means "compatible with all relevant arches" so we don't need to key it.
suffix = env['suffix'].replace(".dev", "").replace(".universal", "")

lib_filename = "{}{}{}{}".format(env.subst('$SHLIBPREFIX'), lib_name, suffix, env.subst('$SHLIBSUFFIX'))
if env["platform"] in ["web", "android"]:
    lib_filename = "lib" + lib_filename

library = env.SharedLibrary(
    "bin/{}/{}".format(env['platform'], lib_filename),
    source=source_files,
)

copy = env.Install("{}/bin/{}/".format(project_dir, env["platform"]), library)

if env["vsproj"]:
    resource_files = []
    
    misc_files = get_all_files_recursive("godot-cpp/gdextension/", "*.h")
    misc_files.extend(get_all_files_recursive("godot-cpp/gen/include/", "*.hpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/gen/src/", "*.cpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/include/", "*.hpp"))
    misc_files.extend(get_all_files_recursive("godot-cpp/src/", "*.cpp"))
    misc_files.append(".runsettings")
    misc_files.append(".editorconfig")
    
    game_project_file = generate_vs_project(env, source_files, include_files, resource_files, misc_files)
        
    vcxproj_files = []
    vcxproj_files.append("godot/godot.vcxproj")
    vcxproj_files.append(game_project_file)
    
    game_solution_file = generate_and_build_vs_solution(env, vcxproj_files)
else:
    default_args = [library, copy]
    Default(*default_args)
