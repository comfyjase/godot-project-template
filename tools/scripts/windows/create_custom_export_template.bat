@echo off
pushd %~dp0\..\..\..\

set "platform=%1"
set "configuration=%2"
set "godot_engine_configuration=%configuration%"
set "is_valid_export_configuration=FALSE"

:: Godot/Godot-CPP have editor, template_debug, template_release configurations, so make sure it's one of them or can be mapped to one of them (e.g. production -> template_release).
:: Creating export templates requires either template_debug or template_release, so enforce that here.
if "%configuration%" == "production" (
	set "godot_engine_configuration=template_release"
	set "is_valid_export_configuration=TRUE"
) else (
	if "%configuration%" == "profile" (
		set "godot_engine_configuration=template_release"
		set "is_valid_export_configuration=TRUE"
	) else (
		if "%configuration%" == "template_release" (
			set "is_valid_export_configuration=TRUE"
		) else (
			if "%configuration%" == "template_debug" (
				set "is_valid_export_configuration=TRUE"
			)
		)
	)
)

if %is_valid_export_configuration% == FALSE (
	echo "ERROR: Couldn't create export template using godot because the configuration (%configuration%) isn't valid."
	echo "Fix this by passing in either template_debug, template_release, profile or production as the configuration."
	exit /b
)

echo:
echo "Creating custom export templates for windows %configuration% with godot"
cd godot
echo "Godot Engine - %configuration%"
if "%configuration%" == "production" (
	scons platform=%platform% target=%godot_engine_configuration% production=yes
) else (
	if "%configuration%" == "profile" (
		scons platform=%platform% target=%godot_engine_configuration% production=yes debug_symbols=yes
	) else (
		if "%configuration%" == "template_release" (
			scons platform=%platform% target=%godot_engine_configuration%
		) else (
			scons platform=%platform% target=%godot_engine_configuration% dev_build=yes dev_mode=yes
		)
	)
)
if %errorlevel% neq 0 exit /b %errorlevel%

echo "Rename custom exports"
cd bin

if "%configuration%" == "template_debug" (
	ren godot.windows.template_debug.dev.x86_64.console.exe windows_%configuration%_x86_64.console.exe
	ren godot.windows.template_debug.dev.x86_64.console.pdb windows_%configuration%_x86_64.console.pdb
	ren godot.windows.template_debug.dev.x86_64.exe windows_%configuration%_x86_64.exe
	ren godot.windows.template_debug.dev.x86_64.exp windows_%configuration%_x86_64.exp
	ren godot.windows.template_debug.dev.x86_64.lib windows_%configuration%_x86_64.lib
	ren godot.windows.template_debug.dev.x86_64.pdb windows_%configuration%_x86_64.pdb
) else (
	if "%configuration%" == "profile" (
		ren godot.windows.template_release.x86_64.console.pdb windows_%configuration%_x86_64.console.pdb
		ren godot.windows.template_release.x86_64.pdb windows_%configuration%_x86_64.pdb
	)
	ren godot.windows.template_release.x86_64.console.exe windows_%configuration%_x86_64.console.exe
	ren godot.windows.template_release.x86_64.exe windows_%configuration%_x86_64.exe
	ren godot.windows.template_release.x86_64.exp windows_%configuration%_x86_64.exp
	ren godot.windows.template_release.x86_64.lib windows_%configuration%_x86_64.lib
)
if %errorlevel% neq 0 exit /b %errorlevel%

popd
