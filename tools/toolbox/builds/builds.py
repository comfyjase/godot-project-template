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

# Change to project directory if we are not already there
current_directory = os.getcwd()
if not os.path.exists(os.path.join(f"{current_directory}", "game")):
    os.chdir("..")
    os.chdir("..")
project_directory = os.getcwd()

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
        
        # Default values
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")

        # Set first frame as visible
        self.select_frame_by_name("download")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.navigation_frame_github_builds_button.configure(fg_color=("#36719F", "#144870") if name == "download" else ("#3B8ED0", "#1F6AA5"))

        # show selected frame
        if name == "download":
            self.github_builds_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.github_builds_frame.grid_forget()

    def github_builds_button_event(self):
        self.select_frame_by_name("download")

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

    def github_builds_download_folder_browse_button_event(self):
        # Done here in case the user has manually updated the entry text
        if not os.path.exists(self.github_download_folder_path.get()):
            pathlib.Path(self.github_download_folder_path.get()).mkdir(parents=True, exist_ok=True)
        
        folder = customtkinter.filedialog.askdirectory(initialdir=self.github_download_folder_path)
        if folder:
            self.github_download_folder_path.set(folder.replace("\\", "/"))

    def create_github_builds_frame(self):
        self.github_builds_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.github_builds_frame.grid(row=0, column=1, sticky="nsew")
        self.github_builds_frame.grid_columnconfigure((2, 3), weight=1)
        self.github_builds_frame.configure(fg_color="transparent")
        
        self.github_download_folder_path = customtkinter.StringVar()
        self.github_download_folder_path.set(os.path.join(project_directory, "bin", "github_builds").replace("\\", "/"))
        if not os.path.exists(self.github_download_folder_path.get()):
            pathlib.Path(self.github_download_folder_path.get()).mkdir(parents=True, exist_ok=True)
        
        self.github_download_folder_label = customtkinter.CTkLabel(self.github_builds_frame, text="Download Folder:")
        self.github_download_folder_label.grid(row=0, column=1, padx=(20, 0), pady=20, sticky="w")
        self.github_download_folder_entry = customtkinter.CTkEntry(self.github_builds_frame, textvariable=self.github_download_folder_path)
        self.github_download_folder_entry.grid(row=0, column=2, columnspan=2, pady=20, sticky="ew")        
        self.github_download_folder_browse_button = customtkinter.CTkButton(self.github_builds_frame, text="Browse...", command=self.github_builds_download_folder_browse_button_event)
        self.github_download_folder_browse_button.grid(row=0, column=4, padx=20, pady=20)
        
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
        
        self.images_folder_path = os.path.join(project_directory, "tools", "toolbox", "assets")
        
        loading_light_image_file_path = os.path.join(self.images_folder_path, "loading_cog_light.png")
        loading_dark_image_file_path = os.path.join(self.images_folder_path, "loading_cog_dark.png")
        green_tick_file_path = os.path.join(self.images_folder_path, "green_tick.png")
        
        self.loading_light_image_object = Image.open(loading_light_image_file_path)
        self.loading_dark_image_object = Image.open(loading_dark_image_file_path)
        self.green_tick_image_object = Image.open(green_tick_file_path)
        
        self.image_size = (20, 20)
        self.loading_image = customtkinter.CTkImage(light_image=self.loading_light_image_object, dark_image=self.loading_dark_image_object, size=self.image_size)
        self.green_tick_image = customtkinter.CTkImage(self.green_tick_image_object, size=self.image_size)
        
        self.github_download_status_label = customtkinter.CTkLabel(self.github_downloads_progress_frame, text="", image=self.loading_image)
        self.github_download_status_label.grid(row=2, column=2, padx=(10, 20), pady=(20, 0))
        self.github_download_status_label.grid_forget()
        
        self.should_animate_loading_icon = False
        self.animation_interval = (1 / 120)
        
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
                build.download_finished_label = customtkinter.CTkLabel(self.github_downloads_progress_frame, text="", image=self.green_tick_image)
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
        
        self.github_download_folder_browse_button.configure(state="normal")

    def start_rotating_loading_image(self):
        self.should_animate_loading_icon = True
        threading.Thread(
            target=lambda loop: loop.run_until_complete(self.async_rotate_loading_image()),
            args=(asyncio.new_event_loop(),)
        ).start()
        
    def stop_rotating_loading_image(self):
        self.should_animate_loading_icon = False
        
    async def async_rotate_loading_image(self):
        degrees_per_tick = 2
        degrees = 0
        
        while (self.should_animate_loading_icon):
            degrees += degrees_per_tick
            if degrees >= 360:
                degrees %= 360
            
            rotated_light_image_object = self.loading_light_image_object.rotate(degrees)
            rotated_dark_image_object = self.loading_dark_image_object.rotate(degrees)
            rotated_image = customtkinter.CTkImage(light_image = rotated_light_image_object, dark_image = rotated_dark_image_object, size=self.image_size)
            self.github_download_status_label.configure(image = rotated_image)
            
            await asyncio.sleep(self.animation_interval)

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
        self.github_download_folder_browse_button.configure(state="disabled")
        self.github_download_builds_button.configure(state="disabled")
        
        selected_builds = self.get_selected_github_builds()
        
        number_of_selected_builds = len(selected_builds)
        print("Downloading " + str(number_of_selected_builds) + " github builds")
        
        self.github_downloads_progress_frame.grid(row=3, column=1, columnspan=3, padx=(20, 0), pady=(10, 0), sticky="new")

        for i, build in enumerate(selected_builds):
            build_download_path = f"{self.github_download_folder_path.get()}/{build.name}"
            if os.path.exists(build_download_path):
                shutil.rmtree(build_download_path)
            
            build.name_label.configure(text=build.name)
            build.name_label.grid(row=i+2, column=1, padx=20, pady=(10, 0), sticky="w")
            
            self.github_download_status_label.grid(row=i+2, column=2, padx=20, pady=(10, 0), sticky="w")
            self.start_rotating_loading_image()
            
            command = f"gh run download {build.workflow_id} -n {build.name} -D {build_download_path}"
            return_code = subprocess.call(command, shell=True)
            if return_code != 0:
                sys.exit(f"Failed to run {command}")
            
            # Stop rotating icon and place a green tick alongside this build name.
            self.stop_rotating_loading_image()
            build.download_finished_label.configure(image=self.green_tick_image)
            build.download_finished_label.grid(row=i+2, column=2, padx=20, pady=(10, 0), sticky="w")

        self.refresh_github_builds_list()

if __name__ == "__main__":
    app = App()
    app.mainloop()
