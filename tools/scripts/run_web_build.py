#!/usr/bin/env python

import subprocess
import sys

return_code = subprocess.call("python serve.py --root .", shell=True)
if (return_code != 0):
    sys.exit("Error: Failed to run serve.py command")
