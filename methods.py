import fnmatch
import os
import sys
from enum import Enum

# Colors are disabled in non-TTY environments such as pipes. This means
# that if output is redirected to a file, it won't contain color codes.
# Colors are always enabled on continuous integration.
_colorize = bool(sys.stdout.isatty() or os.environ.get("CI"))


class ANSI(Enum):
    """
    Enum class for adding ansi colorcodes directly into strings.
    Automatically converts values to strings representing their
    internal value, or an empty string in a non-colorized scope.
    """

    RESET = "\x1b[0m"

    BOLD = "\x1b[1m"
    ITALIC = "\x1b[3m"
    UNDERLINE = "\x1b[4m"
    STRIKETHROUGH = "\x1b[9m"
    REGULAR = "\x1b[22;23;24;29m"

    BLACK = "\x1b[30m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"

    PURPLE = "\x1b[38;5;93m"
    PINK = "\x1b[38;5;206m"
    ORANGE = "\x1b[38;5;214m"
    GRAY = "\x1b[38;5;244m"

    def __str__(self) -> str:
        global _colorize
        return str(self.value) if _colorize else ""


def print_warning(*values: object) -> None:
    """Prints a warning message with formatting."""
    print(f"{ANSI.YELLOW}{ANSI.BOLD}WARNING:{ANSI.REGULAR}", *values, ANSI.RESET, file=sys.stderr)


def print_error(*values: object) -> None:
    """Prints an error message with formatting."""
    print(f"{ANSI.RED}{ANSI.BOLD}ERROR:{ANSI.REGULAR}", *values, ANSI.RESET, file=sys.stderr)

def get_all_directories_recursive(root_directory):
    directories = []
    
    for (search_path,directory_names,files) in os.walk(root_directory, topdown=True):
        search_path_with_ending_slash = os.path.join(search_path, '').replace('\\', '/')
        directories.append(search_path_with_ending_slash)
    
    return directories
    
def get_all_files_recursive(root_directory, filetype='*.*'):
    files_matching_type = []

    for (search_path,directory_names,files) in os.walk(root_directory, topdown=True):
        search_path_with_ending_slash = os.path.join(search_path, '').replace('\\', '/')
        
        for (file) in files:
            if fnmatch.fnmatch(file, '*' + filetype):
                files_matching_type.append(str(search_path_with_ending_slash + file))
                
    return files_matching_type

