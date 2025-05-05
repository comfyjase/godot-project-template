#!/usr/bin/env python

import os
import platform
import sys

from SCons.Variables import *
from tools.scripts.system import *

def init_options(env, opts, library_name):
    opts.Add(
        EnumVariable(
            key="platform",
            help="Target platform",
            default=env.get("platform", default_platform),
            allowed_values=platforms,
            ignorecase=2,
        )
    )
    opts.Add(
        EnumVariable(
            key="target",
            help="Compilation target",
            default=env.get("target", configurations[0]),
            allowed_values=(configurations),
        )
    )
    opts.Add(
        EnumVariable(
            key="precision",
            help="Set the floating-point precision level",
            default=env.get("precision", "single"),
            allowed_values=("single", "double"),
        )
    )
    opts.Add(
        EnumVariable(
            key="arch",
            help="CPU architecture",
            default=env.get("arch", ""),
            allowed_values=architectures,
            map=architecture_aliases,
        )
    )
    opts.Add(BoolVariable("vsproj", "Generate a Visual Studio solution", False))
    opts.Add("vsproj_name", "Name of the Visual Studio solution", library_name)
    opts.Add(BoolVariable("debug_symbols", "Build with debugging symbols", True))
    opts.Add(BoolVariable("dev_build", "Developer build with dev-only debugging code (DEV_ENABLED)", False))
    opts.Add(BoolVariable("production", "Used for shipping a build", False))
