@echo off
pushd %~dp0\..\..\..\

set "current_directory=%cd%"
set "configuration=%1"
set "is_valid_export_target=FALSE"
set "export_command_line_type=debug"

if "%configuration%" == "production" (
	set "is_valid_export_target=TRUE"
) else (
	if "%configuration%" == "profile" (
		set "is_valid_export_target=TRUE"
	) else (
		if "%configuration%" == "template_release" (
			set "is_valid_export_target=TRUE"
		) else (
			if "%configuration%" == "template_debug" (
				set "is_valid_export_target=TRUE"
			)
		)
	)
)

if %is_valid_export_target% == FALSE (
	echo "ERROR: Couldn't export project because the configuration (%configuration%) isn't valid."
	echo "Fix this by passing in one of the following: template_debug, template_release, profile or production."
	exit /b
)

echo:
echo "Exporting project for windows %configuration%"

:: Gets the latest git commit as a shortened ID
for /f "delims=" %%i in ('git rev-parse --short HEAD') do set "latest_git_commit_id=%%i"

cd godot
cd bin

:: Removes milliseconds from timestamp.
set "short_time=%time:~0,8%"
:: Removes separators from the date ("/") and time (":") data.
set "date_time_stamp=%date:/=%_%short_time::=%"

set "build_filename_and_type=game_%configuration%_%date_time_stamp%_%latest_git_commit_id%.exe"
echo "Build Name: %build_filename_and_type%"

if "%configuration%" == "template_debug" (
	set "export_command_line_type=debug"
	if not exist "%current_directory%\game\bin\windows\libgame.windows.%configuration%.dev.x86_64.dll" (
		echo "ERROR: "%current_directory%\game\bin\windows\libgame.windows.%configuration%.dev.x86_64.dll" doesn't exist, please build project for %configuration% first."
		exit /b
	)
) else (
	set "export_command_line_type=release"
	if not exist "%current_directory%\game\bin\windows\libgame.windows.%configuration%.x86_64.dll" (
		echo "ERROR: "%current_directory%\game\bin\windows\libgame.windows.%configuration%.x86_64.dll" doesn't exist, please build project for %configuration% first."
		exit /b
	)
)
godot.windows.editor.dev.x86_64.console.exe --path %current_directory%\game\ --headless --export-%export_command_line_type% "Windows Desktop %configuration%" "%current_directory%\bin\windows\%build_filename_and_type%"
if %errorlevel% neq 0 exit /b %errorlevel%

echo "Build finished installing: %current_directory%\bin\windows\%build_filename_and_type%"
echo "Done."

popd
