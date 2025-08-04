import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image

import asyncio
import glob
import os
import pathlib
import platform
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
print(project_directory)

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # App Window
        self.title("Maintenance")
        self.geometry(f"{1100}x{600}")

        # Grid Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Create app frames
        self.create_sidebar_frame()
        self.create_workflows_frame()
        
        # Default values
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")

        # Set first frame as visible
        self.select_frame_by_name("workflows")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.navigation_frame_workflows_button.configure(fg_color=("#36719F", "#144870") if name == "workflows" else ("#3B8ED0", "#1F6AA5"))

        # show selected frame
        if name == "workflows":
            self.workflows_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.workflows_frame.grid_forget()

    def workflows_button_event(self):
        self.select_frame_by_name("workflows")

    def create_sidebar_frame(self):
        # Sidebar With Title
        self.navigation_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.navigation_frame, text="Maintenance", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.navigation_frame_workflows_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="⤴️ Workflows",
                                                      text_color="white", hover_color=("#36719F", "#144870"), anchor="w", command=self.workflows_button_event)
        self.navigation_frame_workflows_button.grid(row=2, column=0, sticky="ew")

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

    def create_workflows_frame(self):
        self.workflows_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.workflows_frame.grid(row=0, column=1, sticky="nsew")
        self.workflows_frame.grid_columnconfigure((1, 2, 3), weight=1)
        self.workflows_frame.configure(fg_color="transparent")
        
        self.workflows_list_frame = customtkinter.CTkScrollableFrame(self.workflows_frame, height=500, corner_radius=0)
        self.workflows_list_frame._scrollbar.configure(height=0)
        self.workflows_list_frame.grid(row=1, column=1, columnspan=3, padx=20, pady=(10, 0), sticky="esw")
        self.workflows_list_frame.grid_columnconfigure(0, weight=1)
        
        self.workflows_checkboxes = []
        self.create_workflows_list()
        
        self.select_button = customtkinter.CTkButton(self.workflows_frame, text="Select All", height=50, command=self.toggle_select_all_workflows)
        self.select_button.grid(row=2, column=1, padx=(10, 20), pady=(20, 0))
        self.select_all = False
        
        self.delete_button = customtkinter.CTkButton(self.workflows_frame, text="Delete", height=50, command=self.delete_selected_workflows)
        self.delete_button.grid(row=2, column=2, padx=(10, 20), pady=(20, 0))
        self.delete_button.configure(state="disabled")
        
    def get_workflows(self):
        workflows = []
        workflows_str = subprocess.check_output("gh run list", shell=True).decode().strip()
        if ("no runs" in workflows_str) or (workflows_str != ""):
            workflows = workflows_str.split("\n")
        print(f"Workflows: {workflows}")   
        return workflows

    def get_selected_workflows(self):
        selected_workflows = []
        for checkbox in self.workflows_checkboxes:
            if checkbox.get() != "off":
                selected_workflows.append(checkbox.cget("onvalue"))
                
        print(selected_workflows)
        return selected_workflows
        
    def check_selection_state(self):
        all_checkboxes_selected = True
        any_checkbox_selected = False
        
        for checkbox in self.workflows_checkboxes:
            if checkbox.get() == "off":
                all_checkboxes_selected = False
                if self.select_all:
                    self.select_all = False
                    self.select_button.configure(text="Select All")
            else:
                any_checkbox_selected = True
                
        if all_checkboxes_selected:
            self.select_all = True
            self.select_button.configure(text="Deselect All")
        
        if any_checkbox_selected:
            self.delete_button.configure(state="normal")
        else:
            self.delete_button.configure(state="disabled")
            
    def create_workflows_list(self):
        workflows = self.get_workflows()
        for i, workflow in enumerate(workflows):
            workflow_str_arr = workflow.strip().split("\t")
            workflow_status = workflow_str_arr[0]
            
            # Only care about querying completed workflows
            if workflow_status != "completed":
                continue
            
            workflow_title = workflow_str_arr[2]
            workflow_id = workflow_str_arr[6]
            workflow_timestamp = workflow_str_arr[8]
                
            check_var = customtkinter.StringVar(value=workflow_id)
            checkbox = customtkinter.CTkCheckBox(self.workflows_list_frame, text=f"{workflow_timestamp} {workflow_id} {workflow_title}", variable=check_var, onvalue=workflow_id, offvalue="off", command=self.check_selection_state)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.workflows_checkboxes.append(checkbox)
            checkbox.deselect()

    def refresh_workflows_list(self):       
        for i, checkbox in enumerate(self.workflows_checkboxes):
            checkbox.configure(text="")
            checkbox.grid_forget()
            
        self.workflows_checkboxes.clear()
        self.create_workflows_list()

    def toggle_select_all_workflows(self):
        self.select_all = not self.select_all
        
        # Checks all workflows
        if self.select_all:
            self.select_button.configure(text="Deselect All")
            for checkbox in self.workflows_checkboxes:
                checkbox.select()
            self.delete_button.configure(state="normal")
        # Unchecks all workflows
        else:
            self.select_button.configure(text="Select All")            
            for checkbox in self.workflows_checkboxes:
                checkbox.deselect()
            self.delete_button.configure(state="disabled")

    def delete_selected_workflows(self):
        self.delete_button.configure(state="disabled")
        
        selected_workflows = self.get_selected_workflows()

        number_of_selected_workflows = len(selected_workflows)
        if number_of_selected_workflows == 0:
            return
            
        print("Removing " + str(number_of_selected_workflows) + " workflows")

        for i, workflow in enumerate(selected_workflows):
            command = f"gh run delete {workflow}"
            print(command)
            return_code = subprocess.call(command, shell=True)
            if return_code != 0:
                sys.exit(f"Failed to run {command}")

        self.refresh_workflows_list()

if __name__ == "__main__":
    app = App()
    app.mainloop()
