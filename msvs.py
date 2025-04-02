import os

def set_vs_environment_variables(env):
    if not env.get('MSVS'):
        env["MSVS"]["PROJECTSUFFIX"] = ".vcxproj"    
        env["MSVS"]["SOLUTIONSUFFIX"] = ".sln"

def get_vs_variants(configurations, platforms):
    vs_variants = []
    for (configuration) in configurations:
        for (platform) in platforms:
            vs_variants.append(configuration + '|' + platform)    
    return vs_variants

def generate_vs_project(env, project_name, configurations, platforms, source_files, include_files, misc_files):
    set_vs_environment_variables(env)
    
    env["MSVSBUILDCOM"] = "scons target=$(Configuration)"
    env["MSVSREBUILDCOM"] = "scons --clean && scons target=$(Configuration)"
    env["MSVSCLEANCOM"] = "scons --clean"
    
    platforms = [ "x64" ] # TODO: Add other platforms here if you have console SDKs for example.

    visual_studio_debug_settings = [
        # template_debug
        {
        },
        # template_release
        {
        }
    ]
    
    visual_studio_cpp_defines = [
        # template_debug
        [
            "TOOLS_ENABLED",
            "DEBUG_ENABLED",
            "TESTS_ENABLED"
        ],
        # template_release
        [
        ]
    ]
    
    visual_studio_cpp_flags = [
        # template_debug
        [
            "/nologo /utf-8 /MT /Zi /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ],
        [
            "/nologo /utf-8 /MT /FS /O2 /TP /std:c++17 /Zc:__cplusplus"
        ]
    ]

    vcxproj_files = []

    project_file = env.MSVSProject(target = project_name + env["MSVSPROJECTSUFFIX"],
                        srcs = source_files,
                        incs = include_files,
                        misc = misc_files,
                        variant = get_vs_variants(configurations, platforms),
                        DebugSettings=visual_studio_debug_settings,
                        cppdefines = visual_studio_cpp_defines,
                        cppflags = visual_studio_cpp_flags,
                        auto_build_solution=0)
    #AddPostAction(gameProjectEnv["vsproj_name"] + ".vcxproj", "$UpdateVisualStudioProjectFileFunction")
    
    return project_file
    
def generate_and_build_vs_solution(env, solution_name, configurations, platforms, vcxproj_files):
    set_vs_environment_variables(env)
    solution_file = env.MSVSSolution(target = solution_name + env["MSVSSOLUTIONSUFFIX"], 
                        projects = vcxproj_files,
                        variant = get_vs_variants(configurations, platforms))
    return solution_file
