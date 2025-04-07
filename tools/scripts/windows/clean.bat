@echo off
pushd %~dp0\..\..\..\

set "configuration=%1"

:: Take into account godot-cpp files too, convert from game -> godot configurations
set "godot_configuration=%configuration%"
if "%godot_configuration%" == "editor_game" (
	set "godot_configuration=editor"
) else (
	if "%godot_configuration%" == "profile" (
		set "godot_configuration=template_release"
	) else (
		if "%godot_configuration%" == "production" (
			set "godot_configuration=template_release"
		)
	)
)

set "game_file_suffix=%configuration%"
if "%configuration%" == "template_release" (
	set "game_file_suffix=%configuration%"
) else (
	if "%configuration%" == "profile" (
		set "game_file_suffix=%configuration%"
	) else (
		if "%configuration%" == "production" (
			set "game_file_suffix=%configuration%"
		) else (
			set "game_file_suffix=%configuration%.dev"
		)
	)
)

set "godot_cpp_file_suffix=%configuration%"
if "%configuration%" == "template_release" (
	set "godot_cpp_file_suffix=%godot_configuration%"
) else (
	set "godot_cpp_file_suffix=%godot_configuration%.dev"
)

scons --clean
if %errorlevel% neq 0 exit /b %errorlevel%

:: Only takes into account godot-cpp and game files, not the godot engine files.
cd godot-cpp
del /S *.windows.%godot_cpp_file_suffix%.x86_64.obj
del /S *.windows.%godot_cpp_file_suffix%.x86_64.lib
if %errorlevel% neq 0 exit /b %errorlevel%

cd ..
cd src
del /S *.windows.%game_file_suffix%.x86_64.obj
if %errorlevel% neq 0 exit /b %errorlevel%

cd..
cd bin
del /S *.windows.%game_file_suffix%.x86_64.lib
if %errorlevel% neq 0 exit /b %errorlevel%

popd
