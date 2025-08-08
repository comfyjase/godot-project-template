# Godot Project Template
This repository serves as a quickstart template for game development with Godot 4.4+ using GDExtension.

[![🎮 Build & Export Game](https://github.com/comfyjase/godot-project-template/actions/workflows/builds.yml/badge.svg)](https://github.com/comfyjase/godot-project-template/actions/workflows/builds.yml)

## Contents
* the gdextension C++ example project from the godot tutorial (`game/`)
* godot as a submodule (`godot/` - v4.4)
* godot-cpp as a submodule (`godot-cpp/` - v4.4)
* GitHub Issues template (`.github/ISSUE_TEMPLATE.yml`)
* GitHub CI/CD workflows with an option to upload your exported game to GitHub Actions (`.github/workflows/builds.yml`)
* preconfigured source files for C++ development of the GDExtension (`src/`)
* setup to automatically generate `.xml` files in a `doc_classes/` directory to be parsed by Godot as [GDExtension built-in documentation](https://docs.godotengine.org/en/stable/tutorials/scripting/gdextension/gdextension_docs_system.html)
* support for writing C++ doctest unit tests from within gdextension code
* profile and production configurations

## Usage - Template

To use this template, log in to GitHub and click the green "Use this template" button at the top of the repository page.
This will let you create a copy of this repository with a clean git history. Make sure you clone the correct branch as these are configured for development of their respective Godot development branches and differ from each other. Refer to the docs to see what changed between the versions.

For getting started after cloning your own copy to your local machine, you should: 
* initialize the godot-cpp git submodule via `git submodule update --init` (if needed)
* run setup.py as administrator and follow the instructions
* restart your machine (for environment variable updates to take effect)
* run generate_project_files.py if you want to generate a visual studio solution

## Usage - Actions

This repository comes with a GitHub action that builds the GDExtension for cross-platform use. It triggers automatically for each pushed change. You can find and edit it in [builds.yml](.github/workflows/builds.yml).
After a workflow run is complete - and if you have set `upload-artifact` to `true` for the corresponding workflows - you can find different types of builds of the game on the `Actions` tab on GitHub.
