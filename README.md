# Godot Project Template
This repository serves as a quickstart template for game development with Godot 4.4+ using GDExtension.

[![🎮 Build & Export Game](https://github.com/comfyjase/godot-project-template/actions/workflows/builds.yml/badge.svg)](https://github.com/comfyjase/godot-project-template/actions/workflows/builds.yml)

![Screenshot of a project open in the godot editor with a sprite on screen.](.github_assets/images/gdextension_cpp_example_project.png)
| Godot C++ GDExtension tutorial implemented in the project.

## Features
* Setup script to help download and install prerequisites.
* Script to generate a visual studio sln file with separate project files the godot engine and the game GDExtension project.
* Implements these configurations: `editor`, `editor_game`, `development`, `template_debug`, `template_release`, `profile` and `production`.
* `project` setup using the [gdextension_cpp_example](https://docs.godotengine.org/en/4.4/tutorials/scripting/gdextension/gdextension_cpp_example.html) godot tutorial.
* `godot` and `godot-cpp` as submodules (tracking the respective 4.4 branches).
* GitHub issues template (`.github/ISSUE_TEMPLATE.yml`) for bug reports.
* CI scripts to build and export the game for different platforms.
* Setup to automatically generate `.xml` files in a `doc_classes/` directory to be parsed by Godot as [GDExtension built-in documentation](https://docs.godotengine.org/en/4.4/tutorials/scripting/gdextension/gdextension_docs_system.html)
* Additional GDExtension plugins to demonstrate developing areas of the codebase as separate plugins linked to the main game project (see (core)[project/addons/core] and (gdextension_cpp_example)[project/addons/gdextension_cpp_example]).
* Support for writing and running doctest unit tests (see (run_unit_tests.py)[tools/scripts/run_unit_tests.py]).
* Includes the `imgui-godot` addon for helpful runtime debugging by implementing `void draw_debug();` in your nodes (see (custom_sprite.cpp)[project/addons/gdextension_cpp_example/project/src/sprite/custom_sprite.cpp]).
* Includes the `godot-git-plugin` addon for godot git integration.
* Implements a `core` addon with some helpful C++ macros to be reused across other plugins and in the main `game` project.
* Toolbox app to support project development - includes a commit checker and build downloader.

## Visual Studio Sln
This has been tested and used with Visual Studio Community 2022.

| Configuration | Description | Debug Available |
|---|---|---|
| `editor` | Builds the godot editor and opens the `game` project for editing. | ✅ |
| `editor_game` | Builds the godot editor and `game` and then runs the `game` project. | ✅ |
| `development` | Builds the `game` project and hot reloads the `game` GDExtension code whilst the editor is running. | ✅ |
| `template_debug` | Builds the godot editor and the `game` project intended to be attached to a running `template_debug` build of the `game`. | ✅ |
| `template_release` | Same as above but with `template_release` instead. | ❌ |
| `profile` | Same as above but for `profile` which uses `production=yes` and `debug_symbols=yes`. | ✅ |
| `production` | Same as above but for `production` which uses `production=yes` | ❌ |

> [!NOTE]  
> Debugging C++ in Visual Studio Community isn't available when running `editor` or `editor_game` for `web` and `android`.  

> [!NOTE]  
> GDExtensions plugins located in the `addons` folder can't hot reload their C++ code whilst the editor is running.  

The following gifs are sped up for brevity.

### Editor
#### Windows
![Gif of visual studio building and running godot game engine and opening the example project.](.github_assets/images/vs_windows_editor_configuration_running.gif)

### Editor Game 
#### Windows
![Gif of visual studio building and running the example project.](.github_assets/images/vs_windows_editor_game_configuration_running.gif)

#### Web
![Gif of visual studio building and running the example project for web.](.github_assets/images/vs_web_editor_game_configuration_running.gif)

### Tools
![Screenshot of an python app named toolbox with a toolbox icon and three buttons: builds, commit checker and maintanence.](.github_assets/images/toolbox.png)

> [!NOTE]  
> These tools are written using python scripts but have only been tested properly on a Windows OS - with some work they should be able to be cross-platform friendly.  

#### Builds
Provides a list of the saved game builds from the github actions artifacts and allows users to download them to a specified folder.
![Gif of a user selecting two different builds in a list and then downloading them to a local binary folder.](.github_assets/images/tools_builds_downloading.gif)

#### Commit Checker
Provides a way to compile for a different platform and configuration locally and then runs unit tests and reports if these are successful or not.  
Also provides a way to write commit messages and link them with specific GitHub issues with the option to automatically close an issue once the commit is pushed.
