"""
UI Components Module
Reusable ASCII/Unicode UI components for terminal rendering.
"""

import shutil
from colors import Style, colorize, COLORS_ENABLED

# Try to import pyfiglet for ASCII art generation
try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False


def get_title_lines(text, font="slant", width=65):
    """
    Generate ASCII art title lines.
    Returns list of strings.
    """
    if PYFIGLET_AVAILABLE:
        try:
            fig = pyfiglet.Figlet(font=font, width=width - 4)
            ascii_art = fig.renderText(text)
            return ascii_art.rstrip().split('\n')
        except Exception:
            pass
    
    # Fallback to simple title (strip newline at start/end)
    return PONG_TITLE_SIMPLE.strip().split('\n')


def generate_title(text, font="slant", width=65):
    """
    Generate ASCII art title wrapped in a box (Legacy/Double style).
    """
    lines = get_title_lines(text, font, width)
    if not lines:
        return ""
        
    max_len = max(len(line) for line in lines)
    box_width = max(max_len + 4, width)
    
    result = []
    result.append('╔' + '═' * (box_width - 2) + '╗')
    result.append('║' + ' ' * (box_width - 2) + '║')
    
    for line in lines:
        padded = line.center(box_width - 4) # Centered
        result.append('║ ' + padded + ' ║')
    
    result.append('║' + ' ' * (box_width - 2) + '║')
    result.append('╚' + '═' * (box_width - 2) + '╝')
    
    return '\n'.join(result)


# Unicode box drawing characters
BOX = {
    # Single line
    'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
    'h': '─', 'v': '│',
    'lt': '├', 'rt': '┤', 'tt': '┬', 'bt': '┴', 'cross': '┼',
    
    # Double line
    'dtl': '╔', 'dtr': '╗', 'dbl': '╚', 'dbr': '╝',
    'dh': '═', 'dv': '║',
    'dlt': '╠', 'drt': '╣', 'dtt': '╦', 'dbt': '╩', 'dcross': '╬',
    
    # Rounded corners
    'rtl': '╭', 'rtr': '╮', 'rbl': '╰', 'rbr': '╯',
    
    # Mixed (double horizontal, single vertical)
    'mtl': '╒', 'mtr': '╕', 'mbl': '╘', 'mbr': '╛',
}

# ASCII fallback for terminals without Unicode
BOX_ASCII = {
    'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
    'h': '-', 'v': '|',
    'lt': '+', 'rt': '+', 'tt': '+', 'bt': '+', 'cross': '+',
    'dtl': '+', 'dtr': '+', 'dbl': '+', 'dbr': '+',
    'dh': '=', 'dv': '|',
    'dlt': '+', 'drt': '+', 'dtt': '+', 'dbt': '+', 'dcross': '+',
    'rtl': '+', 'rtr': '+', 'rbl': '+', 'rbr': '+',
    'mtl': '+', 'mtr': '+', 'mbl': '+', 'mbr': '+',
}

# Symbols
SYMBOLS = {
    'bullet': '●',
    'circle': '○',
    'arrow_right': '▶',
    'arrow_left': '◀',
    'arrow_up': '▲',
    'arrow_down': '▼',
    'star': '★',
    'star_empty': '☆',
    'check': '✓',
    'cross': '✗',
    'heart': '♥',
    'diamond': '◆',
    'block_full': '█',
    'block_dark': '▓',
    'block_medium': '▒',
    'block_light': '░',
    'dot_center': '·',
}

SYMBOLS_ASCII = {
    'bullet': '*',
    'circle': 'o',
    'arrow_right': '>',
    'arrow_left': '<',
    'arrow_up': '^',
    'arrow_down': 'v',
    'star': '*',
    'star_empty': '*',
    'check': '+',
    'cross': 'x',
    'heart': '<3',
    'diamond': '*',
    'block_full': '#',
    'block_dark': '#',
    'block_medium': '=',
    'block_light': '-',
    'dot_center': '.',
}

# Global toggle for Unicode
UNICODE_ENABLED = True


def get_box_char(name):
    """Get box drawing character with fallback."""
    if UNICODE_ENABLED:
        return BOX.get(name, BOX_ASCII.get(name, '?'))
    return BOX_ASCII.get(name, '?')


def get_symbol(name):
    """Get symbol with fallback."""
    if UNICODE_ENABLED:
        return SYMBOLS.get(name, SYMBOLS_ASCII.get(name, '?'))
    return SYMBOLS_ASCII.get(name, '?')


def get_terminal_size():
    """Get terminal dimensions."""
    try:
        cols, rows = shutil.get_terminal_size()
        return cols, rows
    except:
        return 80, 24  # Default fallback


def get_responsive_width(min_width=40, max_width=100, margin=4):
    """
    Calculate responsive width based on terminal size.
    
    Args:
        min_width: Minimum width
        max_width: Maximum width  
        margin: Left+right margin from terminal edges
        
    Returns:
        Calculated width that fits within terminal
    """
    cols, _ = get_terminal_size()
    available = cols - margin
    return max(min_width, min(max_width, available))


def get_menu_width():
    """Get responsive menu width (65-100, centered in terminal)."""
    return get_responsive_width(min_width=50, max_width=80, margin=4)


def get_lobby_width():
    """Get responsive lobby width."""
    return get_responsive_width(min_width=50, max_width=80, margin=4)


def get_game_display_width():
    """Get game display width (fixed for physics consistency)."""
    # Game physics require fixed width, so we keep this constant
    # but the display will be centered
    from config import GAME_WIDTH
    return GAME_WIDTH + 2  # +2 for borders


def center_text(text, width):
    """Center text within given width."""
    # Strip ANSI codes for length calculation
    import re
    visible_text = re.sub(r'\033\[[0-9;]*m', '', text)
    padding = max(0, (width - len(visible_text)) // 2)
    return " " * padding + text


def center_block(content_lines):
    """
    Center a block of text vertically and horizontally in the terminal.
    
    Args:
        content_lines: List of strings or single string with newlines
        
    Returns:
        List of centered strings (with vertical padding adjusted)
    """
    cols, rows = get_terminal_size()
    
    if isinstance(content_lines, str):
        content_lines = content_lines.split('\n')
        
    # Remove empty lines at start/end
    while content_lines and not content_lines[0].strip():
        content_lines.pop(0)
    while content_lines and not content_lines[-1].strip():
        content_lines.pop()
        
    if not content_lines:
        return []
        
    content_height = len(content_lines)
    
    # Calculate vertical padding
    v_padding = max(0, (rows - content_height) // 2)
    
    result = []
    # Add vertical padding
    result.extend([''] * v_padding)
    
    # Add horizontally centered lines
    import re
    for line in content_lines:
        visible_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
        h_padding = max(0, (cols - visible_len) // 2)
        result.append(" " * h_padding + line)
        
    return result


def draw_horizontal_line(width, style='single', color=None):
    """Draw a horizontal line."""
    char = get_box_char('dh' if style == 'double' else 'h')
    line = char * width
    if color and COLORS_ENABLED:
        return colorize(line, color)
    return line


def draw_box_top(width, style='single', color=None):
    """Draw top border of a box."""
    if style == 'double':
        line = get_box_char('dtl') + get_box_char('dh') * (width - 2) + get_box_char('dtr')
    elif style == 'rounded':
        line = get_box_char('rtl') + get_box_char('h') * (width - 2) + get_box_char('rtr')
    else:
        line = get_box_char('tl') + get_box_char('h') * (width - 2) + get_box_char('tr')
    
    if color and COLORS_ENABLED:
        return colorize(line, color)
    return line


def draw_box_bottom(width, style='single', color=None):
    """Draw bottom border of a box."""
    if style == 'double':
        line = get_box_char('dbl') + get_box_char('dh') * (width - 2) + get_box_char('dbr')
    elif style == 'rounded':
        line = get_box_char('rbl') + get_box_char('h') * (width - 2) + get_box_char('rbr')
    else:
        line = get_box_char('bl') + get_box_char('h') * (width - 2) + get_box_char('br')
    
    if color and COLORS_ENABLED:
        return colorize(line, color)
    return line


def draw_box_middle(content, width, style='single', color=None):
    """Draw a middle line with content."""
    if style == 'double':
        v = get_box_char('dv')
    else:
        v = get_box_char('v')
    
    # Strip ANSI for length calculation
    import re
    visible_content = re.sub(r'\033\[[0-9;]*m', '', content)
    padding = width - 2 - len(visible_content)
    
    line = v + content + " " * padding + v
    if color and COLORS_ENABLED:
        # Only color the borders, not content
        return colorize(v, color) + content + " " * padding + colorize(v, color)
    return line


def draw_box_separator(width, style='single', color=None):
    """Draw a separator line within a box."""
    if style == 'double':
        line = get_box_char('dlt') + get_box_char('dh') * (width - 2) + get_box_char('drt')
    else:
        line = get_box_char('lt') + get_box_char('h') * (width - 2) + get_box_char('rt')
    
    if color and COLORS_ENABLED:
        return colorize(line, color)
    return line


def draw_progress_bar(progress, width=30, filled_char=None, empty_char=None):
    """
    Draw a progress bar.
    
    Args:
        progress: Float between 0 and 1
        width: Total width of the bar
        filled_char: Character for filled portion
        empty_char: Character for empty portion
    """
    filled_char = filled_char or get_symbol('block_full')
    empty_char = empty_char or get_symbol('block_light')
    
    filled = int(width * min(1, max(0, progress)))
    empty = width - filled
    
    bar = filled_char * filled + empty_char * empty
    percentage = int(progress * 100)
    
    if COLORS_ENABLED:
        bar = colorize(filled_char * filled, Style.GREEN) + colorize(empty_char * empty, Style.DIM)
    
    return f"[{bar}] {percentage}%"


def status_indicator(connected, label=""):
    """
    Draw a status indicator.
    
    Args:
        connected: Boolean
        label: Optional label text
    """
    if connected:
        symbol = get_symbol('bullet')
        if COLORS_ENABLED:
            indicator = colorize(symbol, Style.GREEN)
        else:
            indicator = symbol
        status = "Connected"
    else:
        symbol = get_symbol('circle')
        if COLORS_ENABLED:
            indicator = colorize(symbol, Style.DIM)
        else:
            indicator = symbol
        status = "Waiting..."
    
    if label:
        return f"{indicator} {label}: {status}"
    return f"{indicator} {status}"


def menu_item(text, selected=False, prefix="  "):
    """
    Draw a menu item.
    
    Args:
        text: Menu item text
        selected: Whether this item is selected
        prefix: Prefix for non-selected items
    """
    if selected:
        arrow = get_symbol('arrow_right')
        if COLORS_ENABLED:
            return colorize(f" {arrow} {text}", Style.BOLD, Style.CYAN)
        return f" {arrow} {text}"
    return f"{prefix}{text}"


def title_banner(text, style='double'):
    """Create a title banner."""
    width = len(text) + 4
    lines = [
        draw_box_top(width, style),
        draw_box_middle(f" {text} ", width, style),
        draw_box_bottom(width, style),
    ]
    return "\n".join(lines)


# ASCII Art title for PONG
PONG_TITLE = """
╔═══════════════════════════════════════════════════════════════╗
║  ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗ ║
║  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║ ║
║     ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║ ║
║     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║ ║
║     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███║║
║     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══╝║
║                        🏓 PONG 🏓                              ║
╚═══════════════════════════════════════════════════════════════╝
"""

PONG_TITLE_SIMPLE = """
                    ████  ████  █   █  ████                    
                    █  █  █  █  ██  █  █                       
                    ████  █  █  █ █ █  █ ██                    
                    █     █  █  █  ██  █  █                    
                    █     ████  █   █  ████                    
                                                               
                     TERMINAL PONG                             
"""

# Score celebration frames
GOAL_FRAMES = [
    "   ★ GOAL! ★   ",
    "  ★★ GOAL! ★★  ",
    " ★★★ GOAL! ★★★ ",
    "  ★★ GOAL! ★★  ",
    "   ★ GOAL! ★   ",
]

WINNER_FRAMES = [
    "   ★ WINNER! ★   ",
    "  ★★ WINNER! ★★  ",
    " ★★★ WINNER! ★★★ ",
    "★★★★ WINNER! ★★★★",
]
