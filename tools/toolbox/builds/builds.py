import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image

import asyncio
import glob
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import threading
import time

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)
    
from shared.shared import *

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class Build():
    def __init__(self):
        self.name = ""
        self.workflow_id = 0
        self.size = 0
        self.name_label = None
        self.download_finished_label = None

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # App Window
        self.title("Builds")
        self.geometry(f"{1100}x{600}")

        # Grid Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Create app frames
        self.create_sidebar_frame()
        self.create_github_builds_frame()
        self.create_export_frame()
        
        # Default values
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")

        # Set first frame as visible
        self.select_frame_by_name("download")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.navigation_frame_github_builds_button.configure(fg_color=("#36719F", "#144870") if name == "download" else ("#3B8ED0", "#1F6AA5"))
        self.navigation_frame_export_builds_button.configure(fg_color=("#36719F", "#144870") if name == "export" else ("#3B8ED0", "#1F6AA5"))

        # show selected frame
        if name == "download":
            self.github_builds_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.github_builds_frame.grid_forget()

        if name == "export":
            self.export_builds_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.export_builds_frame.grid_forget()
        
    def create_sidebar_frame(self):
        # Sidebar With Title
        self.navigation_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.navigation_frame, text="Builds", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.navigation_frame_github_builds_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="📦 Download",
                                                      text_color="white", hover_color=("#36719F", "#144870"), anchor="w", command=self.github_builds_button_event)
        self.navigation_frame_github_builds_button.grid(row=2, column=0, sticky="ew")
        self.navigation_frame_export_builds_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="📤 Export",
                                                      text_color="white", hover_color=("#36719F", "#144870"), anchor="w", command=self.export_builds_button_event)
        self.navigation_frame_export_builds_button.grid(row=3, column=0, sticky="ew")
        
        # Appearance Theme Dropdown
        self.appearance_mode_label = customtkinter.CTkLabel(self.navigation_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        # UI Scaling Dropdown
        self.scaling_label = customtkinter.CTkLabel(self.navigation_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))        

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

# =============================================================================
# DOWNLOAD
    def github_builds_button_event(self):
        self.select_frame_by_name("download")
        
    def create_github_builds_frame(self):
        self.github_builds_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.github_builds_frame.grid(row=0, column=1, sticky="nsew")
        self.github_builds_frame.grid_columnconfigure((2, 3), weight=1)
        self.github_builds_frame.configure(fg_color="transparent")
        
        self.github_download_folder = FolderSelection(self.github_builds_frame)
        self.github_download_folder.set_folder_path(os.path.join(repo_directory, "bin", "github_builds"))
        
        self.github_builds_list_frame = customtkinter.CTkScrollableFrame(self.github_builds_frame, height=250, corner_radius=0)
        self.github_builds_list_frame._scrollbar.configure(height=0)
        self.github_builds_list_frame.grid(row=1, column=1, columnspan=3, padx=(20, 0), pady=(10, 0), sticky="esw")
        self.github_builds_list_frame.grid_columnconfigure(0, weight=1)
        
        self.github_downloads_progress_frame = customtkinter.CTkScrollableFrame(self.github_builds_frame, height=150, corner_radius=0)
        self.github_downloads_progress_frame._scrollbar.configure(height=0)
        self.github_downloads_progress_frame.grid(row=3, column=1, columnspan=3, padx=(20, 0), pady=(10, 0), sticky="new")
        self.github_downloads_progress_frame.configure(fg_color="transparent")
        self.github_downloads_progress_frame.grid_forget()
        
        self.github_download_builds_button = customtkinter.CTkButton(self.github_builds_frame, text="Download", height=50, command=self.start_github_build_download)
        self.github_download_builds_button.grid(row=2, column=1, padx=(20, 20), pady=(20, 0))
        self.github_download_builds_button.configure(state="disabled")
        
        self.completed_github_downloads_title_label = customtkinter.CTkLabel(self.github_downloads_progress_frame, text="Downloads")
        self.completed_github_downloads_title_label.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="w")
        self.completed_github_downloads_title_label.cget("font").configure(size=20)
        self.completed_github_downloads_title_label.cget("font").configure(weight="bold")
        
        self.github_download_status_label = customtkinter.CTkLabel(self.github_downloads_progress_frame, text="", image=loading_image)
        self.github_download_status_label.grid(row=2, column=2, padx=(10, 20), pady=(20, 0))
        self.github_download_status_label.grid_forget()
        
        self.loading_image = LoadingImage()
        
        self.github_builds = []
        self.github_builds_checkboxes = []
        self.create_github_builds_list()
    
    def get_github_builds(self):
        github_builds = []
        github_builds_str = subprocess.check_output("gh api /repos/{owner}/{repo}/actions/artifacts --jq \".artifacts[] | [.name, .workflow_run.id, .size_in_bytes]\"", shell=True).decode().strip()
        
        if ("no artifacts" in github_builds_str) or (github_builds_str != ""):
            github_builds = github_builds_str.split("\n")
        
        return github_builds

    def get_selected_github_builds(self):
        selected_builds = []
        for i, checkbox in enumerate(self.github_builds_checkboxes):
            if checkbox.get() != "off":
                selected_builds.append(self.github_builds[i])
                
        return selected_builds
        
    def check_github_builds_selection_state(self):
        any_checkbox_selected = False
        
        for checkbox in self.github_builds_checkboxes:
            if checkbox.get() != "off":
                any_checkbox_selected = True
        
        if any_checkbox_selected:
            self.github_download_builds_button.configure(state="normal")
        else:
            self.github_download_builds_button.configure(state="disabled")
    
    def is_build_information_cached(self, name, workflow_id):
        already_cached = False
        for i, build in enumerate(self.github_builds):
            if build.name == name and build.workflow_id == workflow_id:
                already_cached = True
                break
        return already_cached
    
    def create_github_builds_list(self):
        builds = self.get_github_builds()
        for i, build in enumerate(builds):
            build_str_arr = build.strip().replace("[", "").replace("]", "").replace("\"", "").split(",")
            
            if not self.is_build_information_cached(build_str_arr[0], build_str_arr[1]):
                build = Build()
                build.name = build_str_arr[0]
                build.workflow_id = build_str_arr[1]
                build.size = (int(build_str_arr[2]) / 1024 / 1024) # covert to MB
                build.name_label = customtkinter.CTkLabel(self.github_downloads_progress_frame, text=build.name)
                build.download_finished_label = customtkinter.CTkLabel(self.github_downloads_progress_frame, text="", image=passed_image)
                self.github_builds.append(build)
            
                check_var = customtkinter.StringVar(value=build.workflow_id)
                checkbox = customtkinter.CTkCheckBox(self.github_builds_list_frame, text=f"{build.name}\t\t\t{build.size:.1f}MB", variable=check_var, onvalue=build.workflow_id, offvalue="off", command=self.check_github_builds_selection_state)
                checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
                self.github_builds_checkboxes.append(checkbox)
                checkbox.deselect()

    def refresh_github_builds_list(self):  
        self.should_animate_loading_icon = False
        self.github_download_status_label.configure(image=None)
        self.github_download_status_label.grid_forget()
        
        for i, checkbox in enumerate(self.github_builds_checkboxes):
            checkbox.deselect()
        
        self.github_download_folder.folder_browse_button.configure(state="normal")

    def start_github_build_download(self):
        for i, build in enumerate(self.github_builds):
            if build.name_label != None:
                build.name_label.grid_forget()
            if build.download_finished_label != None:
                build.download_finished_label.grid_forget()
        
        threading.Thread(
            target=lambda loop: loop.run_until_complete(self.async_github_builds_download()),
            args=(asyncio.new_event_loop(),)
        ).start()

    async def async_github_builds_download(self):
        self.github_download_folder.folder_browse_button.configure(state="disabled")
        self.github_download_builds_button.configure(state="disabled")
        
        selected_builds = self.get_selected_github_builds()
        
        number_of_selected_builds = len(selected_builds)
        print("Downloading " + str(number_of_selected_builds) + " github builds")
        
        self.github_downloads_progress_frame.grid(row=3, column=1, columnspan=3, padx=(20, 0), pady=(10, 0), sticky="new")

        for i, build in enumerate(selected_builds):
            build_download_path = f"{self.github_download_folder.folder_path.get()}/{build.name}"
            if os.path.exists(build_download_path):
                shutil.rmtree(build_download_path)
            
            build.name_label.configure(text=build.name)
            build.name_label.grid(row=i+2, column=1, padx=20, pady=(10, 0), sticky="w")
            
            self.github_download_status_label.grid(row=i+2, column=2, padx=20, pady=(10, 0), sticky="w")
            self.loading_image.start_rotating_loading_image(self.github_download_status_label)
            
            command = f"gh run download {build.workflow_id} -n {build.name} -D {build_download_path}"
            return_code = subprocess.call(command, shell=True)
            if return_code != 0:
                sys.exit(f"Failed to run {command}")
            
            # Stop rotating icon and place a green tick alongside this build name.
            self.loading_image.stop_rotating_loading_image()
            build.download_finished_label.configure(image=passed_image)
            build.download_finished_label.grid(row=i+2, column=2, padx=20, pady=(10, 0), sticky="w")

        print("Finished")
        self.refresh_github_builds_list()

# =============================================================================
# EXPORT
    def export_builds_button_event(self):
        self.select_frame_by_name("export")
        
    def create_export_frame(self):
        # Perform checks frame
        self.export_builds_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.export_builds_frame.grid(row=0, column=1, sticky="nsew")
        self.export_builds_frame.configure(fg_color="transparent")

        self.export_folder = FolderSelection(self.export_builds_frame)
        self.export_folder.set_folder_path(os.path.join(repo_directory, "bin", "local_builds"))

        # Target platform/configuration selection
        self.target_platform_selection = TargetPlatformSelection(self.export_builds_frame,
                "Exporting Builds", "Export", self.get_export_command,
                starting_row=1)
        
    def get_export_command(self, target_platform, target_configuration):
        compile_platform = target_platform
        compile_target = target_configuration
        compile_architecture = "x86_64"
        if compile_platform == "web":
            compile_architecture = "wasm32"
        elif compile_platform == "android":
            compile_architecture = "arm64"
        compile_precision = "single"
        
        return f"python tools/scripts/create_build.py {compile_platform} {compile_target} {compile_architecture} {compile_precision}"

# =============================================================================

if __name__ == "__main__":
    app = App()
    app.mainloop()
