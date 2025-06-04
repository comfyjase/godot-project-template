import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image

import asyncio
import os
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

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ErrorMessagesWindow(customtkinter.CTkToplevel):
    def __init__(self, error_messages):
        super().__init__()
        
        self.title("Error Messages")
        self.geometry("800x400")

        self.textbox = customtkinter.CTkTextbox(self, width=780)
        self.textbox.pack(padx=20, pady=20)
        for i, error_message in enumerate(error_messages):
            self.textbox.insert("0.0", f"{error_message}")
        self.textbox.configure(state="disabled")
        
class TargetPlatformSelection(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.target_configurations = [ "template_debug", "template_release", "profile", "production" ]
        self.target_platforms = [ "linux", "windows", "web", "android" ]
        
        self.configuration_labels = [ "Template Debug", "Template Release", "Profile", "Production" ]
        self.platform_labels = [ "🐧 Linux", "🪟 Windows", "🌐 Web", "🤖 Android" ]
        
        self.configuration_titles = []
        self.platform_titles = []
        self.checkboxes = []

        for i, target_configuration in enumerate(self.configuration_labels):
            configuration_title = customtkinter.CTkLabel(master, text=target_configuration, fg_color=("#3B8ED0", "#1F6AA5"), text_color="white", corner_radius=6, width=150)
            configuration_title.grid(row=0, column=i+2, padx=10, pady=10)
            self.configuration_titles.append(configuration_title)
            
        for i, target_platform in enumerate(self.platform_labels):
            platform_title = customtkinter.CTkLabel(master, text=target_platform, fg_color=("#3B8ED0", "#1F6AA5"), text_color="white", corner_radius=6, width=150)
            platform_title.grid(row=i+1, column=1, padx=10, pady=10)
            self.platform_titles.append(platform_title)

        for i, target_configuration in enumerate(self.target_configurations):
            for j, target_platform in enumerate(self.target_platforms):
                string_value = f"{target_platform}+{target_configuration}+{self.platform_labels[j]}+{self.configuration_labels[i]}"
                check_var = customtkinter.StringVar(value=string_value)
                checkbox = customtkinter.CTkCheckBox(master, text="",
                    variable=check_var, onvalue=string_value, offvalue="off", command=self.checkbox_callback)
                checkbox.grid(row=j+1, column=i+2, padx=(20, 0), pady=(10, 0), sticky="ne")
                checkbox.deselect()
                
                # Selecting default targets for convenience
                if target_configuration == "template_debug" and target_platform == "linux":
                    checkbox.select()
                if target_configuration == "production" and target_platform == "android":
                    checkbox.select()
                    
                self.checkboxes.append(checkbox)

    def get(self):
        checkbox_values = []
        for checkbox in self.checkboxes:
            if checkbox.get() != "off":
                checkbox_values.append(checkbox.cget("onvalue"))
        return checkbox_values

    def checkbox_callback(self):
        print("Target Platform Selection:", self.get())

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        print("CommitChecker starting up")

        # App Window
        self.title("Commit Checker")
        self.geometry(f"{1100}x{600}")

        # Grid Layout
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Create app frames
        self.create_sidebar_frame()
        self.create_perform_checks_frame()
        self.create_commit_message_frame()
        
        # Default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

        # Set first frame as visible
        self.select_frame_by_name("perform_checks")
        
        self.error_messages_window = None
        self.error_messages = []
        self.number_of_commands = 0
        self.should_animate_loading_icon = False
        self.animation_interval = (1 / 120)

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.navigation_frame_perform_checks_button.configure(fg_color=("#36719F", "#144870") if name == "perform_checks" else ("#3B8ED0", "#1F6AA5"))
        self.navigation_frame_commit_message_button.configure(fg_color=("#36719F", "#144870") if name == "commit_message" else ("#3B8ED0", "#1F6AA5"))

        # show selected frame
        if name == "perform_checks":
            self.perform_checks_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.perform_checks_frame.grid_forget()
        if name == "commit_message":
            self.commit_message_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.commit_message_frame.grid_forget()

    def perform_checks_button_event(self):
        self.select_frame_by_name("perform_checks")

    def commit_message_button_event(self):
        self.select_frame_by_name("commit_message")

    def create_sidebar_frame(self):
        # Sidebar With Title
        self.navigation_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.navigation_frame, text="Commit Checker", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.navigation_frame_perform_checks_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="🔍 Perform Checks",
                                                      text_color="white", hover_color=("#36719F", "#144870"), anchor="w", command=self.perform_checks_button_event)
        self.navigation_frame_perform_checks_button.grid(row=2, column=0, sticky="ew")

        self.navigation_frame_commit_message_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="📝 Commit Message",
                                                      text_color="white", hover_color=("#36719F", "#144870"), anchor="w", command=self.commit_message_button_event)
        self.navigation_frame_commit_message_button.grid(row=3, column=0, sticky="ew")

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

    def create_perform_checks_frame(self):
        # Perform checks frame
        self.perform_checks_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.perform_checks_frame.grid(row=0, column=1, sticky="nsew")
        self.perform_checks_frame.configure(fg_color="transparent")

        # Target platform/configuration selection        
        self.target_platform_selection = TargetPlatformSelection(self.perform_checks_frame)
        
        # Run checklist button
        self.run_checks_button = customtkinter.CTkButton(self.perform_checks_frame, text="Run Checklist", height=50, command=self.run_checks)
        self.run_checks_button.grid(row=5, column=1, columnspan=5, padx=(10, 20), pady=(20, 0), sticky="nswe")
        
        # Run checklist frame
        self.run_checks_frame = customtkinter.CTkScrollableFrame(self.perform_checks_frame, corner_radius=0)
        self.run_checks_frame.grid(row=6, column=1, columnspan=5, sticky="nsew")
        self.run_checks_frame.configure(fg_color="transparent")
        self.run_checks_frame.grid_forget()

        # Checklist title
        self.checks_title_label = customtkinter.CTkLabel(self.run_checks_frame, text="Checklist")
        self.checks_title_label.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="w")
        self.checks_title_label.cget("font").configure(size=20)
        self.checks_title_label.cget("font").configure(weight="bold")
        
        self.checklist_stages = []
        self.checklist_rows = []
        self.checklist_commands = []
        self.checklist_platforms = []
        self.checklist_status_labels = []

        # Checklist error messages button
        self.show_error_messages_button = customtkinter.CTkButton(self.run_checks_frame, text="See Errors", command=self.display_error_messages_window)
        self.show_error_messages_button.grid(row=1, column=1, padx=20, pady=(10, 0), sticky="w")
        self.show_error_messages_button.grid_forget()
        
        # Log output text
        self.log_output_label = customtkinter.CTkLabel(self.run_checks_frame, text="Log: ", width=200, height=20, corner_radius=0)
        self.log_output_label.grid(row=0, column=3, padx=20, pady=(10, 0), sticky="w")
        self.log_output_label.cget("font").configure(size=16)
        self.log_output_label.grid_forget()
        
        # Images
        self.images_folder_path = os.path.join(project_directory, "tools", "commit_checker", "assets", "images")
        loading_image_file_path = os.path.join(self.images_folder_path, "loading_cog.png")
        passed_image_file_path = os.path.join(self.images_folder_path, "green_tick.png")
        failed_image_file_path = os.path.join(self.images_folder_path, "red_cross.png")
        
        self.loading_image_object = Image.open(loading_image_file_path)
        self.passed_image_object = Image.open(passed_image_file_path)
        self.failed_image_object = Image.open(failed_image_file_path)
        
        self.image_size = (20, 20)
        self.loading_image = customtkinter.CTkImage(self.loading_image_object, size=self.image_size)
        self.passed_image = customtkinter.CTkImage(self.passed_image_object, size=self.image_size)
        self.failed_image = customtkinter.CTkImage(self.failed_image_object, size=self.image_size)

    def create_commit_message_frame(self):
        # Images
        git_icon_added_image_file_path = os.path.join(self.images_folder_path, "git_icon_added.png")
        git_icon_deleted_image_file_path = os.path.join(self.images_folder_path, "git_icon_deleted.png")
        git_icon_modified_image_file_path = os.path.join(self.images_folder_path, "git_icon_modified.png")
        
        git_icon_added_image_object = Image.open(git_icon_added_image_file_path)
        git_icon_deleted_image_object = Image.open(git_icon_deleted_image_file_path)
        git_icon_modified_image_object = Image.open(git_icon_modified_image_file_path)
        
        self.image_size = (20, 20)
        self.git_icon_added_image = customtkinter.CTkImage(git_icon_added_image_object, size=self.image_size)
        self.git_icon_deleted_image = customtkinter.CTkImage(git_icon_deleted_image_object, size=self.image_size)
        self.git_icon_modified_image = customtkinter.CTkImage(git_icon_modified_image_object, size=self.image_size)
        
        # Commit Frame
        self.commit_message_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.commit_message_frame.grid(row=0, column=1, sticky="nesw")
        self.commit_message_frame.grid_columnconfigure((1, 2), weight=1)
        self.commit_message_frame.grid_columnconfigure(3, weight=0)
        self.commit_message_frame.configure(fg_color="transparent")
        
        # Commit Title Textbox
        self.commit_title_label = customtkinter.CTkLabel(self.commit_message_frame, text="Commit Title")
        self.commit_title_label.grid(row=0, column=1, padx=20, pady=(10, 0), sticky="w")
        self.commit_title_label.cget("font").configure(size=16)
        self.commit_title_label.cget("font").configure(weight="bold")
        
        self.commit_title_textbox = customtkinter.CTkTextbox(self.commit_message_frame, height=10)
        self.commit_title_textbox.grid(row=1, column=1, padx=20, sticky="ew")
        
        # Branch Name
        self.branch_name_title_label = customtkinter.CTkLabel(self.commit_message_frame, text=f"Branch")
        self.branch_name_title_label.grid(row=0, column=2, padx=20, pady=(10, 0), sticky="w")
        self.branch_name_title_label.cget("font").configure(size=16)
        self.branch_name_title_label.cget("font").configure(weight="bold")
        
        self.branch_name_label = customtkinter.CTkLabel(self.commit_message_frame, text=f"{self.get_branch_name()}")
        self.branch_name_label.grid(row=1, column=2, padx=20, pady=(10, 10), sticky="w")
        self.branch_name_label.cget("font").configure(size=16)
        self.branch_name_label.cget("font").configure(weight="bold")
        
        # Commit Message Textbox
        self.commit_message_label = customtkinter.CTkLabel(self.commit_message_frame, text="Commit Message")
        self.commit_message_label.grid(row=2, column=1, padx=20, pady=(10, 0), sticky="w")      
        self.commit_message_label.cget("font").configure(size=16)
        self.commit_message_label.cget("font").configure(weight="bold")
        
        self.commit_message_textbox = customtkinter.CTkTextbox(self.commit_message_frame, height=200)
        self.commit_message_textbox.grid(row=3, column=1, padx=20, sticky="ew")
        
        # Changed files frame
        self.changed_files_label = customtkinter.CTkLabel(self.commit_message_frame, text="Changes")
        self.changed_files_label.grid(row=2, column=2, padx=20, pady=(10, 0), sticky="w")      
        self.changed_files_label.cget("font").configure(size=16)
        self.changed_files_label.cget("font").configure(weight="bold")
        
        self.changed_files_refresh_button = customtkinter.CTkButton(self.commit_message_frame, text="Refresh", command=self.refresh_changed_files_list)
        self.changed_files_refresh_button.grid(row=2, column=2, padx=20, pady=(10, 10), sticky="e")
        
        self.changed_files_frame = customtkinter.CTkScrollableFrame(self.commit_message_frame, corner_radius=0)
        self.changed_files_frame.grid(row=3, column=2, padx=20, sticky="nesw")
        self.changed_files_frame.grid_columnconfigure(0, weight=1)
        
        self.changed_files_status_labels = []
        self.changed_files_checkboxes = []
        self.create_changed_files_list()
        
        # Issues list
        self.issues_label = customtkinter.CTkLabel(self.commit_message_frame, text="Issues")
        self.issues_label.grid(row=4, column=2, padx=20, pady=(10, 0), sticky="w")
        self.issues_label.cget("font").configure(size=16)
        self.issues_label.cget("font").configure(weight="bold")
        
        self.issues_list_refresh_button = customtkinter.CTkButton(self.commit_message_frame, text="Refresh", command=self.refresh_issues_list)
        self.issues_list_refresh_button.grid(row=4, column=2, padx=20, pady=(10, 0), sticky="e")
        
        self.issues_frame = customtkinter.CTkScrollableFrame(self.commit_message_frame, height=120, corner_radius=0)
        self.issues_frame._scrollbar.configure(height=0)
        self.issues_frame.grid(row=5, column=2, padx=20, pady=(10, 0), sticky="ew")
        self.issues_frame.grid_columnconfigure(0, weight=1)
        
        self.issues_checkboxes = []
        self.create_issues_list()
        
        # Resolve issues on commit checkbox
        self.resolve_issues_on_commit_checkbox = customtkinter.CTkCheckBox(self.commit_message_frame, text=f"Resolve selected issues on commit")
        self.resolve_issues_on_commit_checkbox.grid(row=6, column=2, padx=20, pady=(10, 0), sticky="w")
        
        # Commit Button
        self.commit_button = customtkinter.CTkButton(self.commit_message_frame, text="Commit", height=50, command=self.commit_changed_files_and_close)
        self.commit_button.grid(row=4, column=1, rowspan=2, padx=20, pady=(10, 0), sticky="nw")
        
    def get_branch_name(self):
        branch_name = subprocess.check_output("git branch --show-current", shell=True).decode('ascii').strip()
        return branch_name
    
    def create_changed_files_list(self):
        changed_files = self.get_changed_files()
        for i, changed_file in enumerate(changed_files):
            status_and_file_arr = changed_file.strip().split()
            status = status_and_file_arr[0]
            file = status_and_file_arr[1]
            
            # Default to modified status
            status_image = self.git_icon_modified_image
            if status == "??" or status == "A":
                status_image = self.git_icon_added_image
            elif status == "D":
                status_image = self.git_icon_deleted_image
            
            checkbox = customtkinter.CTkCheckBox(self.changed_files_frame, text=f"{file}", command=self.get_selected_changed_files)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            checkbox.select()
            self.changed_files_checkboxes.append(checkbox)
            
            label = customtkinter.CTkLabel(self.changed_files_frame, text="", image=status_image)
            label.grid(row=i+1, column=0, padx=(0, 0), pady=(10, 0), sticky="e")
            self.changed_files_status_labels.append(label)
        
    def refresh_changed_files_list(self):
        self.changed_files_refresh_button.configure(state="disabled")
        
        for i, changed_file_status in enumerate(self.changed_files_status_labels):
            self.changed_files_status_labels[i].configure(image=None)
            self.changed_files_checkboxes[i].configure(text="")
            self.changed_files_status_labels[i].grid_forget()
            self.changed_files_checkboxes[i].grid_forget()
            
        self.changed_files_status_labels.clear()
        self.changed_files_checkboxes.clear()
        
        self.create_changed_files_list()
        
        self.changed_files_refresh_button.configure(state="normal")
        
    def get_changed_files(self):
        changed_files = []
        changed_files_str = subprocess.check_output("git status --short", shell=True).decode('ascii').strip().replace("\\", "/")
        if changed_files_str != "":
            changed_files = changed_files_str.split("\n")
        print(f"Changed Files: {changed_files}")
        return changed_files
        
    def get_selected_changed_files(self):
        selected_changed_files = ""
        for checkbox in self.changed_files_checkboxes:
            if checkbox.get() == 1:
                selected_changed_files += f"{checkbox.cget("text")} "
        
        print(selected_changed_files)
        return selected_changed_files
        
    def create_issues_list(self):
        issues = self.get_issues()
        for i, issue in enumerate(issues):            
            issue_str_arr = issue.strip().split("\t")
            issue_number = issue_str_arr[0]
            issue_title = issue_str_arr[2]
            
            print(f"Number: #{issue_number} Title: {issue_title}")
            
            checkbox = customtkinter.CTkCheckBox(self.issues_frame, text=f"#{issue_number} {issue_title}", command=self.get_selected_issues)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.issues_checkboxes.append(checkbox)
    
    def refresh_issues_list(self):
        self.issues_list_refresh_button.configure(state="disabled")
        
        for i, issue_checkbox in enumerate(self.issues_checkboxes):
            issue_checkbox.configure(text="")
            issue_checkbox.grid_forget()
            
        self.issues_checkboxes.clear()
        self.create_issues_list()
        self.issues_list_refresh_button.configure(state="normal")
       
    def get_issues(self):
        issues = []
        issues_str = subprocess.check_output("gh issue list", shell=True).decode('ascii').strip()
        if ("no open issues" in issues_str) or (issues_str != ""):
            issues = issues_str.split("\n")
            issues.reverse()
        print(f"Issues: {issues}")   
        return issues
       
    def get_selected_issues(self):
        selected_issues = ""
        for checkbox in self.issues_checkboxes:
            if checkbox.get() == 1:
                if (self.resolve_issues_on_commit_checkbox.get() == 1):
                    selected_issues += f"Resolves {checkbox.cget("text")}, "
                else:
                    selected_issues += f"Updates {checkbox.cget("text")}, "
        
        selected_issues = selected_issues.removesuffix(", ")
        print(selected_issues)
        return selected_issues
            
    def commit_changed_files_and_close(self):
        self.commit_button.configure(state="disabled")
        
        selected_files = self.get_selected_changed_files()
        git_command = f"git add {selected_files}"
        return_code = subprocess.call(git_command, shell=True)
        if return_code != 0:
            self.error_messages.clear()
            self.error_messages.append(f"git add {selected_files}")
            self.error_messages.append("Failed to add all unstaged files, please review changed in github desktop or other similar software.")
            self.display_error_messages_window()
            return
        
        selected_issues = self.get_selected_issues()
        commit_checker_tag = "[CommitChecker]"
        commit_message_suffix = f"-m \" \" -m \"{commit_checker_tag}\""
        if selected_issues != "":
            commit_message_suffix += f" -m \"{selected_issues}\""
            
        commit_title = self.commit_title_textbox.get("0.0", "end").strip()
        commit_message_arr = self.commit_message_textbox.get("0.0", "end").strip().split("\n")
        commit_message = "".join(f"-m \"{w}\" " for w in commit_message_arr)
        commit_message += commit_message_suffix
        commit_message = commit_message.replace("-m \"\"", "-m \" \"")
        
        git_command = f"git commit -m \"{commit_title}\" {commit_message}"
        print(f"git command:\n{git_command}")
        return_code = subprocess.call(git_command, shell=True)
        if return_code != 0:
            self.error_messages.clear()
            self.error_messages.append("Failed to commit files.")
            self.display_error_messages_window()
            return
        
        git_command = f"git push"
        return_code = subprocess.call(git_command, shell=True)
        if return_code != 0:
            self.error_messages.clear()
            self.error_messages.append("Failed to push files to repository.")
            self.display_error_messages_window()
            return
        
        self.on_post_commit()
        
    def start_rotating_loading_image(self, loading_image_label):
        thread = threading.Thread(target=asyncio.run, args=(self.async_rotate_loading_image(loading_image_label),))
        thread.start()
        
    async def async_rotate_loading_image(self, loading_image_label):
        degrees_per_tick = 2
        degrees = 0
        
        while (self.should_animate_loading_icon):
            degrees += degrees_per_tick
            if degrees >= 360:
                degrees %= 360
            
            rotated_image_object = self.loading_image_object.rotate(degrees)
            rotated_image = customtkinter.CTkImage(rotated_image_object, size=self.image_size)
            loading_image_label.configure(image = rotated_image)
            
            await asyncio.sleep(self.animation_interval)
    
    async def start_writing_log_output(self, proc, row_number):
        #self.console_output_frame.grid(row=7, column=1, columnspan=5, sticky="nsew")
        self.log_output_label.grid(row=row_number, column=3, padx=20, pady=(10, 0), sticky="w")
        
        while True:
            buf = await proc.stdout.readline()
            if not buf:
                break
            self.log_output_label.configure(text=f"Log Output: {buf.decode().rstrip()}")
        
    def start_checklist_subprocesses(self):
        thread = threading.Thread(target=asyncio.run, args=(self.async_run_checklist_subprocesses(self.checklist_commands),))
        thread.start()
        
    async def async_run_checklist_subprocesses(self, commands):        
        self.show_error_messages_button.grid_forget()
        self.log_output_label.grid_forget()
        
        self.number_of_commands = len(commands)
        print(f"{self.number_of_commands} checklist commands to run")
        
        while (self.number_of_commands != 0):
            for i, command in enumerate(commands):        
                print("Start animating loading icon")
                self.checklist_status_labels[i].configure(text = "")
                self.checklist_status_labels[i].configure(image = self.loading_image)
                self.should_animate_loading_icon = True
                self.start_rotating_loading_image(self.checklist_status_labels[i])
                
                print(f"Running command: {command}")
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
        
                await self.start_writing_log_output(proc, self.checklist_rows[i])
                
                stdout, stderr = await proc.communicate()
                
                self.should_animate_loading_icon = False
                print("Stop animating loading icon")
                
                # Give at least 2 frames worth of time for the loading icon to stop correctly
                await asyncio.sleep(self.animation_interval * 2)
                
                print(f"[{command!r} exited with {proc.returncode}]")
                
                self.log_output_label.configure(text = "")
                self.log_output_label.grid_forget()
                
                if stdout:
                    print(f"[stdout]\n{stdout.decode()}")
                
                if proc.returncode == 0:
                    self.checklist_status_labels[i].configure(text = "")
                    self.checklist_status_labels[i].configure(image = self.passed_image)
                else:
                    self.checklist_status_labels[i].configure(text = "")
                    self.checklist_status_labels[i].configure(image = self.failed_image)
                    
                    if stderr:
                        error_output = stderr.decode()
                        print(f"[stderr]\n{error_output}")
                        self.error_messages.append(f"{self.checklist_stages[i].cget("text")}\n{error_output}\n")
                
                print(f"Finished running command: {command}")
                self.number_of_commands -= 1
                
                if self.number_of_commands == 0:
                    print("Checklist finished!")
                    
                    # Display error message button if any errors have occurred.
                    if len(self.error_messages) > 0:
                        self.show_error_messages_button.grid(row=self.checklist_rows[i]+1, column=1, padx=20, pady=(10, 0), sticky="w")
                
                    self.run_checks_button.configure(state="normal")
                else:
                    print(f"{self.number_of_commands} checklist command(s) left to run")

    def display_error_messages_window(self):
        if self.error_messages_window is None or not self.error_messages_window.winfo_exists():
            self.error_messages_window = ErrorMessagesWindow(self.error_messages)
        else:
            self.error_messages_window.focus()

    def run_checks(self):
        font_size = 16
        
        self.run_checks_button.configure(state="disabled")
        self.run_checks_frame.grid(row=6, column=1, columnspan=5, sticky="new")
        
        for i, stage in enumerate(self.checklist_stages):
            stage.grid_forget()
            
            self.checklist_status_labels[i].configure(image=None)
            self.checklist_status_labels[i].grid_forget()
        
        self.checklist_stages.clear()
        self.checklist_rows.clear()
        self.checklist_commands.clear()
        self.checklist_platforms.clear()
        self.checklist_status_labels.clear()
        
        checked_targets = self.target_platform_selection.get()
        for i, checked_target in enumerate(checked_targets):
            target_information = checked_target.split("+")
            
            self.checklist_rows.append(i+2)
            
            target_platform = target_information[0]
            target_configuration = target_information[1]
            target_platform_pretty_label = target_information[2]
            target_configuration_pretty_label = target_information[3]
            target_stage = f"{target_platform_pretty_label} / {target_configuration_pretty_label}"
            
            self.checklist_platforms.append(target_platform)
            
            running_check_platform_description = customtkinter.CTkLabel(self.run_checks_frame, text=f"{target_stage}", height=20)
            running_check_platform_description.grid(row=i+2, column=1, padx=20, pady=(10, 0), sticky="w")
            running_check_platform_description.cget("font").configure(size=font_size)
            self.checklist_stages.append(running_check_platform_description)
            
            if i == 0:
                running_check_result_description = customtkinter.CTkLabel(self.run_checks_frame, text="", image = self.loading_image, width=20, height=20)
            else:
                running_check_result_description = customtkinter.CTkLabel(self.run_checks_frame, text=f"Waiting...", width=20, height=20)
            
            running_check_result_description.grid(row=i+2, column=2, padx=20, pady=(10, 0), sticky="w")
            running_check_result_description.cget("font").configure(size=font_size)
            self.checklist_status_labels.append(running_check_result_description)
            
            compile_command = self.get_compile_command(target_platform, target_configuration)
            self.checklist_commands.append(compile_command)
            
        unit_test_row = len(checked_targets)+2
        self.checklist_rows.append(unit_test_row)
        running_check_unit_test_description = customtkinter.CTkLabel(self.run_checks_frame, text=f"🧪 Unit Tests", height=20)
        running_check_unit_test_description.grid(row=unit_test_row, column=1, padx=20, pady=(10, 0), sticky="w")
        running_check_unit_test_description.cget("font").configure(size=font_size)
        self.checklist_stages.append(running_check_unit_test_description)

        self.running_check_unit_test_result_description = customtkinter.CTkLabel(self.run_checks_frame, text=f"Waiting...", height=20)
        self.running_check_unit_test_result_description.grid(row=unit_test_row, column=2, padx=20, pady=(10, 0), sticky="w")
        self.running_check_unit_test_result_description.cget("font").configure(size=font_size)
        
        unit_test_command = f"python tools/scripts/run_unit_tests.py <p> editor x86_64 single"
        unit_test_platform = ""
        if platform.system() == "Windows" or platform.system() == "Linux":
            unit_test_platform = platform.system().lower()
        elif platform.system == "Darwin":
            unit_test_platform = "macos"
        unit_test_command = unit_test_command.replace("<p>", unit_test_platform)
        self.checklist_platforms.append(unit_test_platform)
        self.checklist_commands.append(unit_test_command)
        self.checklist_status_labels.append(self.running_check_unit_test_result_description)
        
        self.start_checklist_subprocesses()
        
    def get_compile_command(self, target_platform, target_configuration):
        compile_platform = target_platform
        compile_target = target_configuration
        compile_architecture = "x86_64"
        if compile_platform == "web":
            compile_architecture = "wasm32"
        elif compile_platform == "android":
            compile_architecture = "arm64"
        compile_precision = "single"
        
        return f"python tools/scripts/build.py {compile_platform} {compile_target} {compile_architecture} {compile_precision}"
        
    def on_post_commit(self):
        commit_passed_image_size = (30, 30)
        commit_passed_image = customtkinter.CTkImage(self.passed_image_object, size=commit_passed_image_size)
        commit_status_label = customtkinter.CTkLabel(self.commit_message_frame, text="", image=commit_passed_image)
        commit_status_label.grid(row=4, column=1, padx=20, pady=(10, 0), sticky="e")
        
        thread = threading.Thread(target=asyncio.run, args=(self.async_wait_and_close_down(),))
        thread.start()
        
    async def async_wait_and_close_down(self):
        await asyncio.sleep(3)
        print("CommitChecker finished and closing now")
        self.quit()
        
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

if __name__ == "__main__":
    app = App()
    app.mainloop()