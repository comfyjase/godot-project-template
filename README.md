# godot-cpp template
This repository serves as a quickstart template for GDExtension development with Godot 4.0+.

[![🎮 Build & Export Game](https://github.com/comfyjase/godot-cpp-template/actions/workflows/builds.yml/badge.svg)](https://github.com/comfyjase/godot-cpp-template/actions/workflows/builds.yml)

## Contents
* The gdextension C++ example project from the godot tutorial (`game/`)
* godot as a submodule (`godot/`)
* godot-cpp as a submodule (`godot-cpp/`)
* GitHub Issues template (`.github/ISSUE_TEMPLATE.yml`)
* GitHub CI/CD workflows to publish your exported game files when creating a release (`.github/workflows/builds.yml`)
* preconfigured source files for C++ development of the GDExtension (`src/`)
* setup to automatically generate `.xml` files in a `doc_classes/` directory to be parsed by Godot as [GDExtension built-in documentation](https://docs.godotengine.org/en/stable/tutorials/scripting/gdextension/gdextension_docs_system.html)

## Usage - Template

To use this template, log in to GitHub and click the green "Use this template" button at the top of the repository page.
This will let you create a copy of this repository with a clean git history. Make sure you clone the correct branch as these are configured for development of their respective Godot development branches and differ from each other. Refer to the docs to see what changed between the versions.

For getting started after cloning your own copy to your local machine, you should: 
* initialize the godot-cpp git submodule via `git submodule update --init`
* run setup.py
* run generate_project_files.py if you want to generate a visual studio solution

## Usage - Actions

This repository comes with a GitHub action that builds the GDExtension for cross-platform use. It triggers automatically for each pushed change. You can find and edit it in [builds.yml](.github/workflows/builds.yml).
After a workflow run is complete, you can find different types of builds of the game on the `Actions` tab on GitHub.
