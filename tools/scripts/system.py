#!/usr/bin/env python

import fnmatch
import os
import pathlib
import platform
import psutil
import shutil
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

from SCons.Script import *

# Default values
lib_name = "game"
project_dir_name = "project"
project_src_dir = os.path.join(project_dir_name, "src")
platform_arg = ""
configuration_arg = ""
architecture_arg = ""
precision_arg = ""
is_ci = False
macos_vulkan_installed = "no"
wsl_available = False
using_wsl = False
is_os_64_bit = sys.maxsize > 2**32
default_platform = ""

platforms = ["linux", "macos", "windows", "android", "ios", "web"]

# editor - run godot editor dev executable and pass --editor and --path
# editor_game - run godot editor dev executable and just pass --path
# development - only builds the game project, this is intended to be used when running the godot binary separately and working on the GDExtension code exclusively. So you can hot reload your changes whilst the editor is running.
# template_debug - run the exported template_debug executable and then attach the visual studio instance to it.
# template_release - run the exported template_release executable and then attach the visual studio instance to it.
# profile - run the exported template_release executable (should be exported using production=yes and debugging_symbols=yes) and then attach the visual studio instance to it.
# production - run the exported template_release executable (should be exported using production=yes) and then attach the visual studio instance to it.
configurations = ["editor", "editor_game", "development", "template_debug", "template_release", "profile", "production"]

# CPU architecture options.
architectures = [
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

project_plugins = ["core", "gdextension_cpp_example"]

if (shutil.which("wsl") is not None):
    return_code = subprocess.call("wsl -l -v", shell=True)
    if return_code == 0:
        wsl_install_output = subprocess.check_output(f"wsl -l -v", shell=True).decode('ascii').strip()
        if "Windows subsystem for Linux has no installed distributions" not in wsl_install_output:
            wsl_available = True
            print("WSL is available", flush=True)
        else:
            print("WSL is not available", flush=True)

# Change to project directory if we are not already there
current_dir = os.getcwd()
if not os.path.exists(os.path.join(f"{current_dir}", project_dir_name)):
    os.chdir("..")
    os.chdir("..")

repo_dir_path = os.getcwd().replace("\\", "/")
project_cache_path = os.path.join(repo_dir_path, ".scons_cache").replace("\\", "/")
project_dir_path = os.path.join(repo_dir_path, project_dir_name).replace("\\", "/")
project_src_path = os.path.join(project_dir_path, "src").replace("\\", "/")
addons_dir_path = os.path.join(project_dir_name, "addons").replace("\\", "/")
addons_imgui_godot_dir_path = os.path.join(addons_dir_path, "imgui-godot").replace("\\", "/")
addons_imgui_godot_include_dir_path = os.path.join(addons_imgui_godot_dir_path, "include").replace("\\", "/")
absolute_thirdparty_dir_path = os.path.join(repo_dir_path, "thirdparty").replace("\\", "/")
thirdparty_dir_path = "thirdparty"
thirdparty_imgui_dir_path = os.path.join(thirdparty_dir_path, "imgui").replace("\\", "/")
access_kit_path = os.path.join(absolute_thirdparty_dir_path, "accesskit", "accesskit-c-0.16.0").replace("\\", "/")
absolute_tools_scripts_dir_path = os.path.join(repo_dir_path, "tools", "scripts").replace("\\", "/")
tools_scripts_dir_path = os.path.join("tools", "scripts").replace("\\", "/")

build_information_file_path = os.path.join(project_dir_path, "bin", "build.info").replace("\\", "/")

engine_dir_name = "engine"
engine_godot_dir = os.path.join(engine_dir_name, "godot").replace("\\", "/")
engine_godot_cpp_dir = os.path.join(engine_dir_name, "godot-cpp").replace("\\", "/")

absolute_godot_dir_path = os.path.join(repo_dir_path, engine_godot_dir).replace("\\", "/")
absolute_godot_bin_dir_path = os.path.join(absolute_godot_dir_path, "bin").replace("\\", "/")
godot_thirdparty_dir_path = os.path.join(engine_godot_dir, "thirdparty").replace("\\", "/")
godot_bin_path = os.path.join(engine_godot_dir, "bin").replace("\\", "/")
godot_cache_path = os.path.join(absolute_godot_dir_path, ".scons_cache").replace("\\", "/")
godot_cpp_dir_path = engine_godot_cpp_dir
absolute_godot_cpp_extension_dir_path = os.path.join(repo_dir_path, godot_cpp_dir_path, "gdextension").replace("\\", "/")
godot_cpp_extension_dir_path = os.path.join(godot_cpp_dir_path, "gdextension").replace("\\", "/")
godot_cpp_gen_include_dir_path = os.path.join(godot_cpp_dir_path, "gen", "include").replace("\\", "/")
godot_cpp_gen_src_dir_path = os.path.join(godot_cpp_dir_path, "gen", "src").replace("\\", "/")
godot_cpp_include_dir_path = os.path.join(godot_cpp_dir_path, "include").replace("\\", "/")
godot_cpp_src_dir_path = os.path.join(godot_cpp_dir_path, "src").replace("\\", "/")

building_editor_for_non_native_os = False
godot_engine_architecture_arg = ""

def get_all_directories_recursive(root_directory):
    directories = []
    
    for (search_path,directory_names,files) in os.walk(root_directory, topdown=True):
        search_path_with_ending_slash = os.path.join(search_path, '').replace('\\', '/')
        directories.append(search_path_with_ending_slash)
    
    return directories
    
def get_all_files_recursive(root_directory, filetype='*.*'):
    files_matching_type = []

    for (search_path,directory_names,files) in os.walk(root_directory, topdown=True):
        search_path_with_ending_slash = os.path.join(search_path, '').replace('\\', '/')
        
        for (file) in files:
            if fnmatch.fnmatch(file, '*' + filetype):
                files_matching_type.append(str(search_path_with_ending_slash + file))
                
    return files_matching_type

def add_imgui(env, all_directories, all_source_files, project_source_files, all_include_files, cpp_defines):
    should_include_imgui = (env["arch"] not in ["x86_32", "arm32", "arm64"]) and (env["platform"] not in ["web", "android", "ios"])
    if should_include_imgui:
        all_directories.extend([addons_imgui_godot_include_dir_path, thirdparty_imgui_dir_path ])
        all_source_files.extend(Glob(f"{thirdparty_imgui_dir_path}/*.cpp", strings=True))
        project_source_files.extend(Glob(f"{thirdparty_imgui_dir_path}/*.cpp", strings=True))
        all_include_files.extend(Glob(f"{thirdparty_imgui_dir_path}/*.h", strings=True))
        all_include_files.extend(get_all_files_recursive(addons_imgui_godot_include_dir_path, "*.h"))
        cpp_defines.extend([ 'IMGUI_USER_CONFIG="\\"imconfig-godot.h\\""', "IMGUI_ENABLED" ])

def add_doctest(all_directories, all_include_files):
    all_directories.append(os.path.join(godot_thirdparty_dir_path, "doctest"))
    all_include_files.append(os.path.join(godot_thirdparty_dir_path, "doctest", "doctest.h"))

def add_cpp_defines(env, cpp_defines):
    if env["target"] in ["editor", "editor_game", "development", "template_debug"]:
        cpp_defines.append("TOOLS_ENABLED")
        cpp_defines.append("DEBUG_ENABLED")
        cpp_defines.append("TESTS_ENABLED")
        cpp_defines.append("DOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS")
    
    if env["platform"] == "windows":
        cpp_defines.append("PLATFORM_WINDOWS")
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
    
def process_exists(process_name):
    for (i, process) in enumerate(psutil.process_iter(attrs=["name"])):
        if process_name in process.name():
            return True
            
    return False

def parse_arguments():
    global platform_arg
    global configuration_arg
    global architecture_arg
    global precision_arg
    global is_ci
    global macos_vulkan_installed
    global using_wsl
    global godot_engine_cache_path
    
    platform_arg = sys.argv[1]
    configuration_arg = sys.argv[2]
    architecture_arg = sys.argv[3]
    precision_arg = sys.argv[4]
    if len(sys.argv) == 6:
        is_ci = sys.argv[5]
    if len(sys.argv) == 7:
        macos_vulkan_installed = sys.argv[6]
        
    if is_ci:
        godot_engine_cache_path = os.path.join(repo_dir_path, ".scons_cache").replace("\\", "/")
        
    # ===============================================
    # Visual Studio 2022 specific stuff
    if platform_arg == "Win32" or platform_arg == "x64":
        platform_arg = "windows"
    
    # Visual Studio 2022 doesn't seem to have a separate setting for architecture_arg, so it's bundled in with the platform.
    # Have to parse it out separately in these scripts to get the correct one.
    # E.g. windows_x86_64 -> x86_64
    if architecture_arg == "Win32":
        architecture_arg = "x86_32"
    elif architecture_arg == "x64" or architecture_arg == "linux":
        architecture_arg = "x86_64"
    elif architecture_arg == "web":
        architecture_arg = "wasm32"
    elif architecture_arg == "android": # TODO: Add different android processor platforms? E.g. android_arm32, android_arm64, android_x86_32, android_x86_64?
        architecture_arg = "arm64"
        
    using_wsl = wsl_available and platform_arg == "linux"

def init_system_variables(arguments):
    global default_platform
    
    if sys.platform.startswith("linux"):
        default_platform = "linux"
    elif sys.platform == "darwin":
        default_platform = "macos"
    elif sys.platform == "win32" or sys.platform == "msys":
        default_platform = "windows"
    elif arguments.get("platform", ""):
        default_platform = arguments.get("platform")
    else:
        raise ValueError("Could not detect platform automatically, please specify with platform=<platform>")

def print_files(directory = "."):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for f in files:
        print(f"\t{f}", flush=True)

def detect_arch():
    host_machine = platform.machine().lower()
    if host_machine in architectures:
        return host_machine
    elif host_machine in architecture_aliases.keys():
        return architecture_aliases[host_machine]
    elif "86" in host_machine:
        # Catches x86, i386, i486, i586, i686, etc.
        return "x86_32"
    else:
        methods.print_warning(f'Unsupported CPU architecture: "{host_machine}". Falling back to x86_64.')
        return "x86_64"

def clean_up_files(directory, extension):
    dir = pathlib.Path(directory)
    so_files = dir.rglob(f"*{extension}")  # recursively
    for so_file in so_files:
        print(f"Removing {so_file}", flush=True)
        os.remove(so_file)
        
def generate_cpp_bindings():
    print("=====================================", flush=True)
    print("Generate C++ extension api files", flush=True)
    print("=====================================", flush=True)
    
    print(f"Detected System Platform: {platform.system()}", flush=True)
    
    godot_binary_file_name = get_godot_binary_file_name_for_system()
    build_command = ""
    if using_wsl:
        build_command = "wsl ./"
    if platform.system() == "Linux" or platform.system() == "Darwin":
        print(f"Called chmod +x {godot_binary_file_name}", flush=True)
        subprocess.call(f"chmod +x {godot_binary_file_name}", shell=True)
        build_command += "./"
    build_command += f"{godot_binary_file_name} --headless --dump-extension-api --dump-gdextension-interface"
    
    return_code = subprocess.call(build_command, shell=True)
    if return_code != 0:
        sys.exit(f"Error: Failed to generate C++ extension api files from {godot_binary_file_name}")
    
    try:
        shutil.copy(os.path.join(f"{os.getcwd()}", "extension_api.json"), os.path.join(absolute_godot_cpp_extension_dir_path, "extension_api.json"))
        shutil.copy(os.path.join(f"{os.getcwd()}", "gdextension_interface.h"), os.path.join(absolute_godot_cpp_extension_dir_path, "gdextension_interface.h"))
    except IOError as e:
        sys.exit(f"Error: Failed to copy extension api files from godot/bin -> godot_cpp/gdextension/ {e}")
        
def add_plugins(plugin_names, env, customs, all_directories_array, project_source_files, all_source_files_array, all_include_files_array):
    dynamically_link_plugins = (env["platform"] != "web")
    
    # Include all plugin files so they can be seen in the IDE.
    for (i, plugin_name) in enumerate(plugin_names):
        plugin_src_dir_path = os.path.join(addons_dir_path, plugin_name, project_dir_name, "src")
        all_directories_array.extend(get_all_directories_recursive(plugin_src_dir_path))
        all_source_files_array.extend(get_all_files_recursive(plugin_src_dir_path, "*.cpp"))
        if not dynamically_link_plugins:
            project_source_files.extend(get_all_files_recursive(plugin_src_dir_path, "*.cpp"))
        all_include_files_array.extend(get_all_files_recursive(plugin_src_dir_path, "*.h"))

    if not dynamically_link_plugins:
        print("Plugins will all be built into single project library", flush=True)
        return;

    # Link all the plugins
    suffix = env['suffix'].replace(".dev", "").replace(".universal", "")
    library_suffix = env.subst('$SHLIBSUFFIX')
    if platform.system() == "Linux" and env["platform"] == "macos":
        library_suffix = ".dylib"
    
    # Link all plugins.
    for (i, plugin_name) in enumerate(plugin_names):
        lib_filename = "{}{}{}{}".format(env.subst('$SHLIBPREFIX'), plugin_name, suffix, library_suffix)
        if platform.system() == "Windows" and (env["platform"] in ["web", "android"]):
            lib_filename = "lib" + lib_filename
        
        lib_filename = lib_filename.rsplit('.', 1)[0]
        
        env.AppendUnique(LIBS=[lib_filename])
        env.AppendUnique(LIBPATH=[".", f"{addons_dir_path}/{plugin_name}/bin/{env["platform"]}/"])
        
def get_godot_scons_command():
    global building_editor_for_non_native_os
    global godot_engine_architecture_arg
    
    godot_platform = platform_arg
    building_editor_for_non_native_os = (godot_platform in ["web", "android"] and configuration_arg == "editor")
    
    # Assuming for windows/linux/mac that arch arg is what the user wants to build the engine with.
    godot_engine_architecture_arg = architecture_arg
    if not building_editor_for_non_native_os and platform_arg not in ["windows", "linux", "macos"]:
        godot_engine_architecture_arg = detect_arch()
        
    scons_command = ""
    if using_wsl:
        scons_command = "wsl "
    
    # Always make sure there's some native os version of the godot editor for the next step
    # Generating the cpp bindings needs a godot binary file.
    if godot_platform not in ["windows", "linux", "macos"]:
        # Unless building the editor for web/android, then don't update godot_platform.
        if not building_editor_for_non_native_os:
            godot_platform = platform.system().lower()
            if godot_platform == "darwin":
                godot_platform = "macos"
            print(f"Building godot engine for native os {godot_platform} {godot_engine_architecture_arg}", flush=True)
        
    if configuration_arg == "production":
        scons_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg} production=yes"
    elif configuration_arg == "profile":
        scons_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg} production=yes debug_symbols=yes"
        if is_ci:   # engine debug symbols are too large for CI
            scons_command = scons_command.replace(" debug_symbols=yes", "")
    elif configuration_arg == "template_release":
        scons_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg}"
    else:
        scons_command += f"scons platform={godot_platform} target=editor arch={godot_engine_architecture_arg} precision={precision_arg} dev_build=yes dev_mode=yes"
        if is_ci:   # Same as above...
            scons_command = scons_command.replace(" dev_build=yes dev_mode=yes", "")
    
    if is_ci:
        scons_command += " debug_symbols=no"
    if configuration_arg in ["editor", "editor_game", "template_debug"]:
        scons_command += " tests=yes"
    
    if (platform_arg == "macos" or platform_arg == "ios"):
        scons_command += f" vulkan={macos_vulkan_installed}"
    elif platform_arg == "web":
        if building_editor_for_non_native_os:
            if configuration_arg in ["editor", "editor_game", "template_debug"]:
                scons_command = scons_command.replace(" dev_build=yes dev_mode=yes", "")
            scons_command += " dlink_enabled=yes threads=no"
    elif platform_arg == "android":
        if building_editor_for_non_native_os:
            scons_command += " generate_apk=yes"
            
    scons_command += f" cache_path={godot_cache_path}"
    scons_command += f" accesskit_sdk_path={access_kit_path}"
    
    return scons_command

def get_godot_custom_export_template_scons_command():
    godot_configuration_arg = configuration_arg
    if godot_configuration_arg in ["profile", "production"]:
        godot_configuration_arg = "template_release"
    elif godot_configuration_arg == "editor_game":
        godot_configuration_arg = "template_debug"
    
    scons_command = ""
    if using_wsl:
        scons_command = "wsl "
        
    if configuration_arg == "production":
        scons_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} production=yes"
    elif configuration_arg == "profile":
        scons_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} production=yes debug_symbols=yes"
        if is_ci:
            scons_command = scons_command.replace(" debug_symbols=yes", "")
    elif configuration_arg == "template_release":
        scons_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg}"
    else:
        scons_command += f"scons platform={platform_arg} target={godot_configuration_arg} arch={architecture_arg} precision={precision_arg} dev_build=yes dev_mode=yes"
        if is_ci:
            scons_command = scons_command.replace(" dev_build=yes dev_mode=yes", "")
    
    if is_ci:
        scons_command += " debug_symbols=no"
    if configuration_arg in ["editor", "editor_game", "template_debug"]:
        scons_command += " tests=yes"
        
    if platform_arg == "macos":
        scons_command += f" vulkan={macos_vulkan_installed}"
        scons_command += " generate_bundle=yes"
    elif platform_arg == "web":
        if configuration_arg in ["editor", "editor_game", "template_debug"]:
            scons_command = scons_command.replace(" dev_build=yes dev_mode=yes", "")
            if os.path.isdir(f"bin/.web_zip"):
                shutil.rmtree(f"bin/.web_zip", True)
        else:
            if os.path.isdir(f"bin/web_{configuration_arg}.zip"):
                shutil.rmtree(f"bin/web_{configuration_arg}.zip", True)
                
        scons_command += " dlink_enabled=yes threads=no"
        if is_ci:
            scons_command += " lto=none"
    elif platform_arg == "android":
        scons_command += " generate_apk=yes"
    elif platform_arg == "ios":
        scons_command += " generate_bundle=yes"
    
    scons_command += f" cache_path={godot_cache_path}"
    scons_command += f" accesskit_sdk_path={access_kit_path}"

    return scons_command

def get_godot_binary_file_name_for_system():
    print(f"Detected System Platform: {platform.system()}", flush=True)
    
    # Assuming for windows/linux/mac that arch arg is what the user wants to build the engine with.
    building_editor_for_non_native_os = (platform_arg in ["web", "android"] and configuration_arg == "editor")
    godot_engine_architecture_arg = architecture_arg
    if not building_editor_for_non_native_os and platform_arg not in ["windows", "linux", "macos"]:
        godot_engine_architecture_arg = detect_arch()
        
    godot_binary_file_name = ""
    if platform.system() == "Windows":
        if platform_arg == "linux":
            godot_binary_file_name = f"godot.linuxbsd.editor.dev.{godot_engine_architecture_arg}"
        else:
            godot_binary_file_name = f"godot.windows.editor.dev.{godot_engine_architecture_arg}.exe"
    elif platform.system() == "Linux":
        godot_binary_file_name = f"godot.linuxbsd.editor.dev.{godot_engine_architecture_arg}"
    elif platform.system() == "Darwin":
        godot_binary_file_name = f"godot.macos.editor.dev.{godot_engine_architecture_arg}"
    
    if configuration_arg in ["template_release", "profile", "production"] or is_ci:
        godot_binary_file_name = godot_binary_file_name.replace(".dev", "")
    
    if precision_arg == "double":
        godot_binary_file_name = godot_binary_file_name.replace(f"{godot_engine_architecture_arg}", f"{precision_arg}.{godot_engine_architecture_arg}")

    return godot_binary_file_name

def get_godot_import_command():
    import_command = ""
    
    if using_wsl:
        import_command += "wsl ./"
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        import_command += "./"
    import_command += f"{get_godot_binary_file_name_for_system()} --path \"{project_dir_path}\" --headless --import"
    
    return import_command

def get_godot_export_command(export_type, output_path):
    export_command = ""
    
    if using_wsl:
        export_command += "wsl ./"
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        export_command += "./"
    
    export_command += f"{get_godot_binary_file_name_for_system()} --path \"{project_dir_path}\" --headless --export-{export_type} \"{platform_arg} {configuration_arg} {architecture_arg} {precision_arg}\" \"{output_path}\" --verbose"
    if platform_arg == "android":
        export_command += " --install-android-build-template"
        
    return export_command
    
def get_project_scons_command():
    scons_command = ""
    if using_wsl:
        scons_command = "wsl "
    
    game_target = configuration_arg
    if game_target in ["editor_game", "development"] and platform_arg in ["web", "android"]:
        game_target = "template_debug"
        
    game_architecture = architecture_arg
    if platform_arg == "macos" and architecture_arg != "universal":
        game_architecture = "universal"
        
    if game_target == "production":
        scons_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg} production=yes"
    elif game_target == "profile":
        scons_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg} production=yes debug_symbols=yes"
    elif game_target == "template_release":
        scons_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg}"
    else:
        scons_command += f"scons platform={platform_arg} target={game_target} arch={game_architecture} precision={precision_arg} dev_build=yes dev_mode=yes"
    
    if platform_arg == "macos":
        scons_command += f" vulkan={macos_vulkan_installed}"
    elif platform_arg == "web":
        if game_target in ["editor", "editor_game", "template_debug", "development"]:
            scons_command = scons_command.replace(" dev_build=yes dev_mode=yes", "")
        scons_command += " threads=no"
    
    scons_command += f" cache_path={project_cache_path}"
    
    return scons_command
