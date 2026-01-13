#!/usr/bin/env python

import asyncio
import glob
import os
import pathlib
import platform
import subprocess
import sys
import threading
import time

import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image

extended_limit = 1024 * 128 # 128 KiB

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

project_dir_name = "project"

# Change to project directory if we are not already there
current_directory = os.getcwd()
if not os.path.exists(os.path.join(current_directory, project_dir_name)):
    os.chdir(os.path.join("..", ".."))
repo_directory = os.getcwd()
repo_bin_path = os.path.join(repo_directory, "bin").replace("\\", "/")

project_dir_path = os.path.join(repo_directory, project_dir_name).replace("\\", "/")
project_src_dir = os.path.join(project_dir_name, "src").replace("\\", "/")
build_information_file_path = os.path.join(project_dir_path, "bin", "build.info").replace("\\", "/")

supported_platforms = [ "linux", "windows", "web", "android" ]  # For command line
platform_labels = [ "🐧 Linux", "🪟 Windows", "🌐 Web", "🤖 Android" ] # For UI display

supported_configurations = [ "template_debug", "template_release", "profile", "production" ]
configuration_labels = [ "Template Debug", "Template Release", "Profile", "Production" ]

# Images
images_folder_path = os.path.join(script_path_to_append, "assets")
loading_light_image_file_path = os.path.join(images_folder_path, "loading_cog_light.png")
loading_dark_image_file_path = os.path.join(images_folder_path, "loading_cog_dark.png")
passed_image_file_path = os.path.join(images_folder_path, "green_tick.png")
failed_image_file_path = os.path.join(images_folder_path, "red_cross.png")

loading_light_image_object = Image.open(loading_light_image_file_path)
loading_dark_image_object = Image.open(loading_dark_image_file_path)
passed_image_object = Image.open(passed_image_file_path)
failed_image_object = Image.open(failed_image_file_path)

image_size = (20, 20)
loading_image = customtkinter.CTkImage(light_image = loading_light_image_object, dark_image = loading_dark_image_object, size=image_size)
passed_image = customtkinter.CTkImage(passed_image_object, size=image_size)
failed_image = customtkinter.CTkImage(failed_image_object, size=image_size)

class LoadingImage():
    def __init__(self, animation_interval = (1 / 120)):
        self.should_animate = False
        self.animation_interval = animation_interval

    def start_rotating_loading_image(self, loading_image_label):
        self.should_animate = True
        thread = threading.Thread(
            target=lambda loop: loop.run_until_complete(self.async_rotate_loading_image(loading_image_label)),
            args=(asyncio.new_event_loop(),)
        )
        thread.start()

    def stop_rotating_loading_image(self):
        self.should_animate = False

    async def async_rotate_loading_image(self, loading_image_label):
        degrees_per_tick = 2
        degrees = 0
        
        while (self.should_animate):
            degrees += degrees_per_tick
            if degrees >= 360:
                degrees %= 360
            
            rotated_light_image_object = loading_light_image_object.rotate(degrees)
            rotated_dark_image_object = loading_dark_image_object.rotate(degrees)
            rotated_image = customtkinter.CTkImage(light_image = rotated_light_image_object, dark_image = rotated_dark_image_object, size=image_size)
            loading_image_label.configure(image = rotated_image)
            
            await asyncio.sleep(self.animation_interval)

class ErrorMessagesWindow(customtkinter.CTkToplevel):
    def __init__(self, error_messages):
        super().__init__()
        
        self.title("Error Messages")
        self.geometry("800x400")

        self.error_messages = []
        self.textbox = customtkinter.CTkTextbox(self, width=780)
        self.textbox.pack(padx=20, pady=20)
        for i, error_message in enumerate(error_messages):
            self.textbox.insert("0.0", f"{error_message}")
        self.textbox.configure(state="disabled")

class FolderSelection(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.folder_path = customtkinter.StringVar()
        
        self.folder_label = customtkinter.CTkLabel(master, text="Folder:")
        self.folder_label.grid(row=0, column=1, padx=(20, 0), pady=20, sticky="w")
        self.folder_label_entry = customtkinter.CTkEntry(master, textvariable=self.folder_path)
        self.folder_label_entry.grid(row=0, column=2, columnspan=2, pady=20, sticky="ew")
        self.folder_browse_button = customtkinter.CTkButton(master, text="Browse...", command=self.folder_browse_button_event)
        self.folder_browse_button.grid(row=0, column=4, padx=20, pady=20)

    def set_folder_path(self, new_path):
        new_path.replace("\\", "/").strip()
        self.folder_path.set(new_path)
        if not os.path.exists(self.folder_path.get()):
            pathlib.Path(self.folder_path.get()).mkdir(parents=True, exist_ok=True)
    
    def folder_browse_button_event(self):
        # Done here in case the user has manually updated the entry text
        if not os.path.exists(self.folder_path.get()):
            pathlib.Path(self.folder_path.get()).mkdir(parents=True, exist_ok=True)
        
        print(self.folder_path.get())
        folder = customtkinter.filedialog.askdirectory(initialdir=self.folder_path.get())
        if folder:
            self.folder_path.set(folder.replace("\\", "/"))

class Command():
    def __init__(self, title, command):
        self.title = title
        self.command = command

class TargetPlatformSelection(customtkinter.CTkFrame):
    def __init__(self, master, command_title_text, command_button_text, command_function_to_run_for_platform_and_configuration, starting_row=0, starting_column=1, auto_selected_platforms = [], auto_selected_configurations = [], custom_commands = [], on_command_finished_function = None):
        super().__init__(master)
        
        self.starting_row = starting_row
        self.configuration_titles = []
        self.platform_titles = []
        self.checkboxes = []
        self.error_messages_window = None
        self.error_messages = []
        self.custom_commands = custom_commands
        self.on_command_finished_function = on_command_finished_function
        self.command_font_size = 16
         
        for i, target_configuration in enumerate(configuration_labels):
            configuration_title = customtkinter.CTkLabel(master, text=target_configuration, fg_color=("#3B8ED0", "#1F6AA5"), text_color="white", corner_radius=6, width=150)
            configuration_title.grid(row=self.starting_row, column=i+2, padx=10, pady=10)
            self.configuration_titles.append(configuration_title)
            
        for i, target_platform in enumerate(platform_labels):
            platform_title = customtkinter.CTkLabel(master, text=target_platform, fg_color=("#3B8ED0", "#1F6AA5"), text_color="white", corner_radius=6, width=150)
            platform_title.grid(row=self.starting_row+i+1, column=1, padx=10, pady=10)
            self.platform_titles.append(platform_title)

        for i, supported_configuration in enumerate(supported_configurations):
            for j, supported_platform in enumerate(supported_platforms):
                string_value = f"{supported_platform}+{supported_configuration}+{platform_labels[j]}+{configuration_labels[i]}"
                check_var = customtkinter.StringVar(value=string_value)
                checkbox = customtkinter.CTkCheckBox(master, text="",
                    variable=check_var, onvalue=string_value, offvalue="off", command=self.checkbox_callback)
                checkbox.grid(row=self.starting_row+j+1, column=i+2, padx=(20, 0), pady=(10, 0), sticky="ne")
                checkbox.deselect()
                
                for k, auto_select_platform in enumerate(auto_selected_platforms):
                    for l, auto_select_configuration in enumerate(auto_selected_configurations):
                        if supported_configuration == auto_select_configuration and supported_platform == auto_select_platform:
                            checkbox.select()
                
                self.checkboxes.append(checkbox)
        
        self.command_function_to_run_for_platform_and_configuration = command_function_to_run_for_platform_and_configuration
        self.command_button = customtkinter.CTkButton(master, text=command_button_text, height=50, command=self.start_commands)
        self.command_button.grid(row=self.starting_row+5, column=1, columnspan=5, padx=(10, 20), pady=(20, 0), sticky="nswe")
        
        self.commands_frame = customtkinter.CTkScrollableFrame(master, corner_radius=0)
        self.commands_frame.grid(row=self.starting_row+6, column=1, columnspan=5, sticky="nsew")
        self.commands_frame.configure(fg_color="transparent")
        self.commands_frame.grid_forget()

        # command title
        self.command_title_label = customtkinter.CTkLabel(self.commands_frame, text=command_title_text)
        self.command_title_label.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="w")
        self.command_title_label.cget("font").configure(size=20)
        self.command_title_label.cget("font").configure(weight="bold")
        
        self.command_stages = []
        self.command_rows = []
        self.commands = []
        self.command_platforms = []
        self.command_configurations= []
        self.command_status_labels = []

        # command error messages button
        self.show_error_messages_button = customtkinter.CTkButton(self.commands_frame, text="See Errors", command=self.display_error_messages_window)
        self.show_error_messages_button.grid(row=1, column=1, padx=20, pady=(10, 0), sticky="w")
        self.show_error_messages_button.grid_forget()
        
        # Log output text
        self.log_output_label = customtkinter.CTkLabel(self.commands_frame, text="Log: ", width=200, height=20, corner_radius=0)
        self.log_output_label.grid(row=0, column=3, padx=20, pady=(10, 0), sticky="w")
        self.log_output_label.cget("font").configure(size=self.command_font_size)
        self.log_output_label.grid_forget()
        
        self.number_of_commands = 0
        self.loading_image = LoadingImage()

    def get(self):
        checkbox_values = []
        for checkbox in self.checkboxes:
            if checkbox.get() != "off":
                checkbox_values.append(checkbox.cget("onvalue"))
        return checkbox_values

    def checkbox_callback(self):
        print("Target Platform Selection:", self.get())
    
    def display_error_messages_window(self):
        if self.error_messages_window is None or not self.error_messages_window.winfo_exists():
            self.error_messages_window = ErrorMessagesWindow(self.error_messages)
        else:
            self.error_messages_window.focus()
    
    def setup_commands_frame(self):
        self.command_button.configure(state="disabled")
        self.commands_frame.grid(row=self.starting_row+6, column=1, columnspan=5, sticky="new")
        
        for i, stage in enumerate(self.command_stages):
            stage.grid_forget()
            
            self.command_status_labels[i].configure(image=None)
            self.command_status_labels[i].grid_forget()
        
        self.command_stages.clear()
        self.command_rows.clear()
        self.commands.clear()
        self.command_platforms.clear()
        self.command_configurations.clear()
        self.command_status_labels.clear()
        
        checked_targets = self.get()
        for i, checked_target in enumerate(checked_targets):
            target_information = checked_target.split("+")
            
            self.command_rows.append(i+2)
            
            target_platform = target_information[0]
            target_configuration = target_information[1]
            target_platform_pretty_label = target_information[2]
            target_configuration_pretty_label = target_information[3]
            target_stage = f"{target_platform_pretty_label} / {target_configuration_pretty_label}"
            
            self.command_platforms.append(target_platform)
            self.command_configurations.append(target_configuration)
            
            running_command_platform_description = customtkinter.CTkLabel(self.commands_frame, text=f"{target_stage}", height=20)
            running_command_platform_description.grid(row=i+2, column=1, padx=20, pady=(10, 0), sticky="w")
            running_command_platform_description.cget("font").configure(size=self.command_font_size)
            self.command_stages.append(running_command_platform_description)
            
            if i == 0:
                running_command_result_description = customtkinter.CTkLabel(self.commands_frame, text="", image = loading_image, width=20, height=20)
            else:
                running_command_result_description = customtkinter.CTkLabel(self.commands_frame, text=f"Waiting...", width=20, height=20)
            
            running_command_result_description.grid(row=i+2, column=2, padx=20, pady=(10, 0), sticky="w")
            running_command_result_description.cget("font").configure(size=self.command_font_size)
            self.command_status_labels.append(running_command_result_description)
            
            self.commands.append(self.command_function_to_run_for_platform_and_configuration(target_platform, target_configuration))

        for i, custom_command in enumerate(self.custom_commands):
            self.add_custom_command(custom_command.title, custom_command.command)

    def start_commands(self):
        self.setup_commands_frame()
        self.run_commands()

    def add_custom_command(self, custom_command_title, custom_command):
        new_row_number = len(self.command_rows)+2
        self.command_rows.append(new_row_number)
        custom_command_description = customtkinter.CTkLabel(self.commands_frame, text=custom_command_title, height=20)
        custom_command_description.grid(row=new_row_number, column=1, padx=20, pady=(10, 0), sticky="w")
        custom_command_description.cget("font").configure(size=self.command_font_size)
        self.command_stages.append(custom_command_description)

        self.custom_command_result_description = customtkinter.CTkLabel(self.commands_frame, text=f"Waiting...", height=20)
        self.custom_command_result_description.grid(row=new_row_number, column=2, padx=20, pady=(10, 0), sticky="w")
        self.custom_command_result_description.cget("font").configure(size=self.command_font_size)
        
        self.commands.append(custom_command)
        self.command_status_labels.append(self.custom_command_result_description)

    def run_commands(self):
        thread = threading.Thread(target=asyncio.run, args=(self.async_run_commands(),))
        thread.start()
        
    async def async_run_commands(self):
        self.show_error_messages_button.grid_forget()
        self.log_output_label.grid_forget()
        
        self.number_of_commands = len(self.commands)
        print(f"{self.number_of_commands} commands to run")
        
        while (self.number_of_commands != 0):
            for i, command in enumerate(self.commands):        
                print("Start animating loading icon")
                self.command_status_labels[i].configure(text = "")
                self.command_status_labels[i].configure(image = loading_image)
                self.loading_image.start_rotating_loading_image(self.command_status_labels[i])
                
                if "linux" in command or "android" in command:
                    dir = pathlib.Path(os.path.join(repo_directory, project_src_dir))
                    so_files = dir.rglob("*.os")  # recursively
                    for so_file in so_files:
                        print(f"Removing {so_file}", flush=True)
                        os.remove(so_file)
                
                print(f"Running command: {command}")
                proc = await asyncio.create_subprocess_shell(
                    command,
                    limit = extended_limit,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
        
                await self.start_writing_log_output(proc, self.command_rows[i])
                
                stdout, stderr = await proc.communicate()
                
                self.loading_image.stop_rotating_loading_image()
                print("Stop animating loading icon")
                
                # Give at least 2 frames worth of time for the loading icon to stop correctly
                await asyncio.sleep(self.loading_image.animation_interval * 2)
                
                print(f"[{command!r} exited with {proc.returncode}]")
                
                self.log_output_label.configure(text = "")
                self.log_output_label.grid_forget()
                
                std_output = stdout.decode()
                if stdout:
                    print(f"[stdout]\n{std_output}")
                
                if proc.returncode == 0:
                    self.command_status_labels[i].configure(text = "")
                    self.command_status_labels[i].configure(image = passed_image)
                else:
                    self.command_status_labels[i].configure(text = "")
                    self.command_status_labels[i].configure(image = failed_image)
                    
                    if stderr:
                        error_output = stderr.decode()
                        error_message = f"{self.command_stages[i].cget("text")}\n{error_output}\n"
                        print(f"[stderr]\n{error_message}")
                        self.error_messages.append(std_output)
                        self.error_messages.append(error_message)
                
                if self.on_command_finished_function is not None:
                    self.on_command_finished_function(self.command_platforms[i], self.command_configurations[i])
                    
                print(f"Finished running command: {command}")
                self.number_of_commands -= 1
                
                if self.number_of_commands == 0:
                    print("command finished!")
                    
                    # Display error message button if any errors have occurred.
                    if len(self.error_messages) > 0:
                        self.show_error_messages_button.grid(row=self.command_rows[i]+1, column=1, padx=20, pady=(10, 0), sticky="w")
                
                    self.command_button.configure(state="normal")
                else:
                    print(f"{self.number_of_commands} command(s) left to run")
    
    async def start_writing_log_output(self, proc, row_number):
        self.log_output_label.grid(row=row_number, column=3, padx=20, pady=(10, 0), sticky="w")
        
        while True:
            buf = await proc.stdout.readline()
            if not buf:
                break
            output = buf.decode().rstrip()
            self.log_output_label.configure(text=f"Log Output: {output}")
        