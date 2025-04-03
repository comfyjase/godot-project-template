@echo off
pushd %~dp0\..\..\..\

set "configuration=%1"

:: TODO: Take into account any more configurations here...
set "game_configuration=%configuration%"
if "%game_configuration%" == "editor_game" (
	set "game_configuration=editor"
) else (
	if "%game_configuration%" == "profile" (
		set "game_configuration=template_release"
	) else (
		if "%game_configuration%" == "production" (
			set "game_configuration=template_release"
		)
	)
)

set "file_suffix=%game_configuration%"
if "%game_configuration%" == "template_release" (
	set "file_suffix=%game_configuration%"
) else (
	set "file_suffix=%game_configuration%.dev"
)

scons --clean
if %errorlevel% neq 0 exit /b %errorlevel%

:: Only takes into account godot-cpp and game files, not the godot engine files.
cd godot-cpp
del /S *.windows.%file_suffix%.x86_64.obj
del /S *.windows.%file_suffix%.x86_64.lib
if %errorlevel% neq 0 exit /b %errorlevel%

cd ..
cd src
del /S *.windows.%file_suffix%.x86_64.obj
if %errorlevel% neq 0 exit /b %errorlevel%

cd..
cd bin
del /S *.windows.%file_suffix%.x86_64.lib
if %errorlevel% neq 0 exit /b %errorlevel%

popd
