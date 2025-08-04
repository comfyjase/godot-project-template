import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image

import asyncio
import os
import subprocess
import sys
import threading

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Toolbox")
        self.geometry(f"{1100}x{600}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(0, weight=1)

        # Images
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.toolbox_logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "icon_toolbox_logo.png")), size=(500, 200))
        self.builds_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "icon_builds.png")), size=(200, 200))
        self.commit_checker_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "icon_commit_checker.png")), size=(200, 200))
        self.maintenance_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "icon_maintenance.png")), size=(200, 200))
        
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.sidebar_frame.configure(fg_color="transparent")
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        # Tools        
        self.toolbox_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.toolbox_frame.grid(row=0, column=1, sticky="nsew")
        self.toolbox_frame.configure(fg_color="transparent")
        
        self.toolbox_logo_label = customtkinter.CTkLabel(self.toolbox_frame, text="", image=self.toolbox_logo_image)
        self.toolbox_logo_label.grid(row=0, column=1, columnspan=3, pady=(20, 10))
        
        # Builds
        self.builds_button = customtkinter.CTkButton(self.toolbox_frame, border_spacing=10, text="", image=self.builds_image, command=self.start_builds)
        self.builds_button.grid(row=2, column=1, padx=20)
        
        # Commit Checker
        self.commit_checker_button = customtkinter.CTkButton(self.toolbox_frame, border_spacing=10, text="", image=self.commit_checker_image, command=self.start_commit_checker)
        self.commit_checker_button.grid(row=2, column=2, padx=20)
        
        # Maintenance
        self.maintenance_button = customtkinter.CTkButton(self.toolbox_frame, border_spacing=10, text="", image=self.maintenance_image, command=self.start_maintenance)
        self.maintenance_button.grid(row=2, column=3, padx=20)
        
        # set default values
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    async def async_open_toolbox_app(self, name):
        return_code = subprocess.call(f"python {os.path.dirname(os.path.realpath(__file__))}/{name}/{name}.py", shell=True)
        if return_code != 0:
            sys.exit(f"Failed to call {name}.py")

    def start_builds(self):
        threading.Thread(
            target=lambda loop: loop.run_until_complete(self.async_open_toolbox_app("builds")),
            args=(asyncio.new_event_loop(),)
        ).start()

    def start_commit_checker(self):
        threading.Thread(
            target=lambda loop: loop.run_until_complete(self.async_open_toolbox_app("commit_checker")),
            args=(asyncio.new_event_loop(),)
        ).start()

    def start_maintenance(self):
        threading.Thread(
            target=lambda loop: loop.run_until_complete(self.async_open_toolbox_app("maintenance")),
            args=(asyncio.new_event_loop(),)
        ).start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
