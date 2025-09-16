# Godot Project Template
This repository serves as a quickstart template for game development with Godot 4.4+ using GDExtension.

[![🎮 Build & Export Game](https://github.com/comfyjase/godot-project-template/actions/workflows/builds.yml/badge.svg)](https://github.com/comfyjase/godot-project-template/actions/workflows/builds.yml)

![Screenshot of a project open in the godot editor with a sprite on screen.](.github_assets/images/gdextension_cpp_example_project.png)
> Godot C++ GDExtension tutorial implemented in the project.

## Features
* Setup script to help download and install prerequisites.
* Script to generate a visual studio sln file with separate project files for the godot engine and the game GDExtension project.
* Implements these configurations: `editor`, `editor_game`, `development`, `template_debug`, `template_release`, `profile` and `production`.
* `project` setup using the [gdextension_cpp_example](https://docs.godotengine.org/en/4.4/tutorials/scripting/gdextension/gdextension_cpp_example.html) godot tutorial.
* `godot` and `godot-cpp` as submodules (tracking the respective 4.4 branches).
* GitHub issues template (`.github/ISSUE_TEMPLATE.yml`) for bug reports.
* CI scripts to build and export the game for different platforms.
* Setup to automatically generate `.xml` files in a `doc_classes/` directory to be parsed by Godot as [GDExtension built-in documentation](https://docs.godotengine.org/en/4.4/tutorials/scripting/gdextension/gdextension_docs_system.html)
* Additional GDExtension plugins to demonstrate developing areas of the codebase as separate plugins linked to the main game project - see [core](./project/addons/core) and [gdextension_cpp_example](./project/addons/gdextension_cpp_example).
* Includes the `imgui-godot` addon for helpful runtime debugging by implementing `void draw_debug();` in your nodes - see [custom_sprite.cpp](./project/addons/gdextension_cpp_example/project/src/sprite/custom_sprite.cpp).
* Includes the `godot-git-plugin` addon for godot git integration.
* `core` addon with some helpful C++ macros to be reused across other plugins and in the main `game` project.
* Support for writing and running doctest unit tests - see [doctest_runner](./project/addons/doctest_runner), [test_custom_sprite.h](./project/addons/gdextension_cpp_example/project/src/tests/sprite) and [run_unit_tests.py](./tools/scripts/run_unit_tests.py).
* Toolbox app to support project development - includes a commit checker and build downloader.

## Visual Studio Solution File
![Screenshot of two projects in Visual Studio Community solution: game and godot](./.github_assets/images/visual-studio-solution-projects.png)
This is generated using scons (makes an NMake project) and has been tested with Visual Studio Community 2022.

| Configuration | Description | Debug Symbols |
|---|---|---|
| `editor` | Builds the godot editor and `game` and opens the `game` project for editing. | ✅ |
| `editor_game` | Builds the godot editor and `game` and then runs the `game` project. | ✅ |
| `development` | Builds the `game` project and hot reloads the `game` GDExtension code whilst the editor is running. | ✅ |
| `template_debug` | Builds the godot editor and the `game` project intended to be attached to a running `template_debug` build of the `game`. | ✅ |
| `template_release` | Same as above but with `template_release` instead. | ❌ |
| `profile` | Same as above but for `profile` which uses `production=yes` and `debug_symbols=yes`. | ✅ |
| `production` | Same as above but for `production` which uses `production=yes` | ❌ |

> [!NOTE]  
> Debugging C++ in Visual Studio Community isn't available when running for `web` and `android`.  

> [!NOTE]  
> GDExtensions plugins located in the `addons` folder can't hot reload their C++ code whilst the editor is running.  

Below are some examples of running different platforms/configurations from the visual studio solution. The gifs are sped up for brevity.

### Editor
#### Windows
![Gif of visual studio building and running godot game engine and opening the example project.](.github_assets/images/vs_windows_editor_configuration_running.gif)

### Editor Game 
#### Windows
![Gif of visual studio building and running the example project.](.github_assets/images/vs_windows_editor_game_configuration_running.gif)

#### Web
![Gif of visual studio building and running the example project for web.](.github_assets/images/vs_web_editor_game_configuration_running.gif)

#### Android
![Gif of visual studio building the example project for android.](.github_assets/images/vs_android_editor_game_building_pc.gif)
![Gif of the example project running on an android phone.](.github_assets/images/vs_android_editor_game_running_phone.gif)

## Tools
![Screenshot of an python app named toolbox with a toolbox icon and three buttons: builds, commit checker and maintanence.](.github_assets/images/toolbox.png)

> [!NOTE]  
> These tools are written using python scripts but have only been tested properly on a Windows OS - with some work they should be able to be cross-platform friendly.  

### Builds
![Gif of a user selecting two different builds in a list and then downloading them to a local binary folder.](.github_assets/images/tools_builds_downloading.gif)
Provides a list of the saved game builds from the github actions artifacts and allows users to download them to a specified folder.

### Commit Checker
![Gif of an app with multiple checkboxes for different platforms and configurations, user selects android production and clicks on a run checklist button.](.github_assets/images/tools_commit_checker_running.gif)
![Image of an app that will let users write a commit title, description and see what changed files they have as well as a list of open issues they can link the commit to.](.github_assets/images/tools_commit_checker_message.png)
Provides a way to compile for a different platform and configuration locally and then runs unit tests and reports if these are successful or not. Also provides a way to write commit messages and link them with specific GitHub issues with the option to automatically resolve an issue once the commit is pushed.

### Maintanence
![Screenshot of an python app named maintanence which lists workflows from the github repo and allows the user to select and delete them.](.github_assets/images/tools_maintanence.png)
Provides a list of github workflows and allows the user to select one or multiple and delete them. I created this to help manage some of the GitHub actions/storage limits I was hitting with private repos and this is faster than having to scroll through each github workflow and manually delete it from there. Not really intended for wider use but might help some users manage their GitHub limits.
