@echo off
pushd %~dp0\..\..\..\

set "current_directory=%cd%"
set "configuration=%1"
set "build_info_file=%cd%\bin\windows\build_info.txt"

:: ===========================================================================
:: Build Godot
echo "Step 1) Build Godot Engine"
cd godot
if "%configuration%" == "production" (
	scons target=editor production=yes
) else (
	if "%configuration%" == "profile" (
		scons target=editor production=yes debug_symbols=yes
	) else (
		if "%configuration%" == "template_release" (
			scons target=editor
		) else (
			:: editor / editor_game / template_debug
			scons target=editor dev_build=yes dev_mode=yes
		)
	)
)
if %errorlevel% neq 0 exit /b %errorlevel%

:: ===========================================================================
:: Generate C++ extension api files
echo "Step 2) Generate C++ extension api files"
cd bin
call godot.windows.editor.dev.x86_64.console.exe --headless --dump-extension-api --dump-gdextension-interface
(robocopy . "%current_directory%\godot-cpp\gdextension" extension_api.json) ^& if %errorlevel% lss 8 set errorlevel = 0
(robocopy . "%current_directory%\godot-cpp\gdextension" gdextension_interface.h) ^& if %errorlevel% lss 8 set errorlevel = 0
if %errorlevel% neq 0 exit /b %errorlevel%

:: ===========================================================================
:: Build Game
echo "Step 3) Build Game %configuration%"
cd ..
cd ..
if "%configuration%" == "production" (
	scons target=%configuration% production=yes
) else (
	if "%configuration%" == "profile" (
		scons target=%configuration% production=yes debug_symbols=yes
	) else (
		if "%configuration%" == "template_release" (
			scons target=%configuration%
		) else (
			:: editor / editor_game / template_debug
			scons target=%configuration% dev_build=yes dev_mode=yes
		)
	)
)

popd
