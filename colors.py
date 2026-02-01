"""
ANSI Escape Codes Module
Provides color and styling support for terminal output.
"""

import os
import sys


class Style:
    """ANSI escape codes for terminal styling."""
    
    # Reset
    RESET = "\033[0m"
    
    # Text styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    
    # Foreground colors (bright/light variants)
    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Dark foreground colors
    DARK_RED = "\033[31m"
    DARK_GREEN = "\033[32m"
    DARK_YELLOW = "\033[33m"
    DARK_BLUE = "\033[34m"
    DARK_MAGENTA = "\033[35m"
    DARK_CYAN = "\033[36m"
    GRAY = "\033[90m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


# Feature detection
def supports_color():
    """Check if terminal supports ANSI colors."""
    # Windows needs special handling
    if os.name == 'nt':
        # Windows 10+ supports ANSI if enabled
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except:
            return False
    
    # Unix-like systems
    if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        return True
    
    return False


# Global flag - can be overridden
COLORS_ENABLED = supports_color()


def colorize(text, *styles):
    """
    Apply styles to text.
    
    Usage:
        colorize("Hello", Style.BOLD, Style.RED)
    """
    if not COLORS_ENABLED:
        return text
    
    style_str = "".join(styles)
    return f"{style_str}{text}{Style.RESET}"


def disable_colors():
    """Disable color output globally."""
    global COLORS_ENABLED
    COLORS_ENABLED = False


def enable_colors():
    """Enable color output globally."""
    global COLORS_ENABLED
    COLORS_ENABLED = True


# Shorthand functions for common uses
def bold(text):
    return colorize(text, Style.BOLD)

def dim(text):
    return colorize(text, Style.DIM)

def red(text):
    return colorize(text, Style.RED)

def green(text):
    return colorize(text, Style.GREEN)

def yellow(text):
    return colorize(text, Style.YELLOW)

def blue(text):
    return colorize(text, Style.BLUE)

def cyan(text):
    return colorize(text, Style.CYAN)

def magenta(text):
    return colorize(text, Style.MAGENTA)

def success(text):
    """Green bold text for success messages."""
    return colorize(text, Style.BOLD, Style.GREEN)

def error(text):
    """Red bold text for error messages."""
    return colorize(text, Style.BOLD, Style.RED)

def warning(text):
    """Yellow text for warnings."""
    return colorize(text, Style.YELLOW)

def info(text):
    """Gray text for info."""
    return colorize(text, Style.GRAY)

def highlight(text):
    """Reverse colors for highlighting."""
    return colorize(text, Style.REVERSE)


# Player colors - using white/gray palette
def player1_color(text):
    """Color for Player 1 (bold white)."""
    return colorize(text, Style.BOLD, Style.WHITE)

def player2_color(text):
    """Color for Player 2 (dim/gray)."""
    return colorize(text, Style.DIM)

