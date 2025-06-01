#!/usr/bin/env python

import datetime
import os
import platform
import subprocess
import sys

script_path_to_append = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if script_path_to_append not in sys.path:
    sys.path.append(script_path_to_append)

env_file = os.getenv('GITHUB_ENV')

with open(env_file, "a") as file:
    git_command = "git rev-parse --short HEAD"
    latest_git_commit_id = subprocess.check_output(git_command, shell=True).decode('ascii').strip()
    
    git_command = "git show -s --date=format:'%Y%m%d_%H%M%S' --format=%cd"
    latest_commit_timestamp = subprocess.check_output(git_command, shell=True).decode('ascii').strip().replace("\'", "")
    
    file.write(f"BUILD_TIME={latest_commit_timestamp}\n")
    file.write(f"SHA_SHORT={latest_git_commit_id}\n")
