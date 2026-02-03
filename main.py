#!/usr/bin/env python3
"""
Terminal Pong - CLI-Based Multiplayer Game
Network Programming Final Project

A real-time multiplayer Pong game running entirely in CLI/Terminal using ASCII graphics.
Uses Host-Client architecture over TCP sockets.
Features: Chat Lobby, Real-time gameplay, ASCII UI
"""

import re
import time
import logging

from config import LOG_LEVEL, LOG_FORMAT
from input_handler import (
    clear_screen, restore_terminal, InputHandler,
    is_valid_ip
)
from colors import (
    Style, colorize, bold, dim, red, green, yellow, blue, cyan, magenta,
    success, error, warning, info
)
from ui_components import (
    get_box_char, get_symbol, draw_box_top, draw_box_bottom,
    draw_box_separator, center_text, PONG_TITLE_SIMPLE, generate_title,
    get_title_lines, center_block, get_menu_width
)
from server import GameServer
from client import GameClient

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


# Menu options
MENU_OPTIONS = [
    ("Host Game", "(Server)", "host"),
    ("Join Game", "(Client)", "join"),
    ("VS AI", "(Single Player)", "ai"),
    ("Quit", "", "quit"),
]


def pad_line(content, width):
    """Pad content to width, accounting for ANSI codes."""
    visible = re.sub(r'\033\[[0-9;]*m', '', content)
    padding = width - len(visible)
    if padding > 0:
        return content + ' ' * padding
    return content


def show_menu(selected=0):
    """Display main menu with arrow key navigation support."""
    clear_screen()
    
    w = get_menu_width()  # Dynamic width based on terminal
    inner_w = w - 2
    
    v = get_box_char('v')
    vc = colorize(v, Style.WHITE)
    
    menu_lines = []
    
    # 1. Box Top (Unified)
    menu_lines.append(colorize(draw_box_top(w, 'rounded'), Style.WHITE))
    
    # 2. Title "PONG-CLI" in WHITE
    title_lines = get_title_lines("PONG-CLI", font="slant", width=w)
    for line in title_lines:
        line_content = center_text(line, inner_w)
        line_padded = pad_line(line_content, inner_w)
        menu_lines.append(f"{vc}{colorize(line_padded, Style.WHITE)}{vc}")
    
    # 3. Subtitle
    subtitle = "CLI-Based Multiplayer Game"
    menu_lines.append(f"{vc}{' ' * inner_w}{vc}")
    sub_centered = center_text(subtitle, inner_w)
    sub_padded = pad_line(sub_centered, inner_w)
    menu_lines.append(f"{vc}{colorize(sub_padded, Style.DIM)}{vc}")
    
    # Description (10 words)
    desc = "Classic arcade action in your terminal with real-time multiplayer support."
    desc_centered = center_text(desc, inner_w)
    desc_padded = pad_line(desc_centered, inner_w)
    menu_lines.append(f"{vc}{colorize(desc_padded, Style.DIM)}{vc}")
    
    menu_lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    # 4. Separator
    menu_lines.append(colorize(draw_box_separator(w, 'rounded'), Style.WHITE))
    
    # 5. Menu Options
    menu_lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    arrow = get_symbol('arrow_right')
    
    for i, (label, hint, action) in enumerate(MENU_OPTIONS):
        if i == selected:
            # Selected item - highlighted with arrow
            if action == "quit":
                opt = f"       {colorize(arrow, Style.GREEN)} {bold(label)}"
            else:
                opt = f"       {colorize(arrow, Style.GREEN)} {bold(label)} {dim(hint)}"
        else:
            # Non-selected item
            if action == "quit":
                opt = f"         {dim(label)}"
            else:
                opt = f"         {dim(label)} {dim(hint)}"
        
        menu_lines.append(f"{vc}{pad_line(opt, inner_w)}{vc}")
    
    menu_lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    # Navigation hint
    nav_hint = dim("  [W/S] Navigate  [Enter] Select  [Q] Quit")
    menu_lines.append(f"{vc}{pad_line(nav_hint, inner_w)}{vc}")
    
    # Menu box bottom
    menu_lines.append(colorize(draw_box_bottom(w, 'rounded'), Style.WHITE))
    
    # Print centered block
    centered_output = center_block(menu_lines)
    for line in centered_output:
        print(line)


def host_game():
    """Start as host."""
    clear_screen()
    print()
    print(colorize(f"  {get_symbol('arrow_right')} {bold('HOST MODE')}", Style.WHITE))
    print(dim("  Starting server..."))
    print()
    
    try:
        server = GameServer()
        local_ip = server.start()
        
        print(success(f"  Server started on {local_ip}"))
        print(info("  Waiting for opponent to connect..."))
        print()
        
        time.sleep(0.5)
        
        client = GameClient()
        if client.connect("127.0.0.1"):
            client.run()
            client.close()
        
        server.stop()
        
    except Exception as e:
        logger.error(f"Host error: {e}")
        print(error(f"  Error: {e}"))
        time.sleep(2)
    
    restore_terminal()


def join_game():
    """Join as guest."""
    clear_screen()
    print()
    print(colorize(f"  {get_symbol('arrow_right')} {bold('JOIN MODE')}", Style.WHITE))
    print()
    
    host_ip = input(f"  Enter Host IP Address: ").strip()
    
    # Validate IP
    if not host_ip:
        print(error("  IP address cannot be empty!"))
        time.sleep(2)
        return
    
    if not is_valid_ip(host_ip):
        print(error(f"  Invalid IP address format: {host_ip}"))
        print(dim("    Expected format: xxx.xxx.xxx.xxx or 'localhost'"))
        time.sleep(2)
        return
    
    print()
    print(info(f"  Connecting to {host_ip}..."))
    
    try:
        client = GameClient()
        if client.connect(host_ip):
            client.run()
            client.close()
        else:
            print(error("  Connection failed!"))
            time.sleep(2)
    except Exception as e:
        logger.error(f"Join error: {e}")
        print(error(f"  Error: {e}"))
        time.sleep(2)
    
    restore_terminal()


def play_vs_ai(input_handler, difficulty='medium'):
    """Play against AI opponent."""
    from game_state import GameState
    from physics import update_physics, move_paddle, process_physics_events
    from ai import AIController
    from sound import play_game_over, play_game_start
    from renderer import render_game_with_effects, show_game_over_ai
    from config import FPS, FRAME_TIME
    from effects import EffectsManager
    from powerups import PowerUpManager
    
    clear_screen()
    print()
    print(colorize(f"  {get_symbol('arrow_right')} {bold('VS AI MODE')}", Style.WHITE))
    print(dim(f"  Difficulty: {difficulty.upper()}"))
    print()
    print(info("  Starting game..."))
    time.sleep(1)
    
    # Initialize game
    state = GameState()
    ai = AIController(difficulty)
    effects = EffectsManager(use_unicode=True)
    powerups = PowerUpManager()
    
    # input_handler already running
    input_handler.set_mode("key")
    
    play_game_start()
    
    last_frame_time = time.time()
    
    try:
        while state.running:
            current_time = time.time()
            
            # Frame rate control
            elapsed = current_time - last_frame_time
            if elapsed < FRAME_TIME:
                time.sleep(FRAME_TIME - elapsed)
                current_time = time.time()
            last_frame_time = current_time
            
            # Handle player input
            key = input_handler.get_key()
            if key == 'Q':
                break
            elif key == 'W' or key == 'UP':
                move_paddle(state, 1, 'W')
            elif key == 'S' or key == 'DOWN':
                move_paddle(state, 1, 'S')
            
            # AI move
            ai_move = ai.update(state)
            if ai_move:
                move_paddle(state, 2, ai_move)
            
            # Update physics with events
            events = update_physics(state, return_events=True)
            
            # Process events for sound and visual effects
            process_physics_events(events, effects)
            
            # Update power-ups
            powerups.update(state, current_time)
            
            # Render with effects
            render_game_with_effects(state, 1, effects, powerups)
    
    except KeyboardInterrupt:
        pass
    
    # Game over
    if state.winner:
        play_game_over()
        show_game_over_ai(state.winner)
        time.sleep(3)


    # restore_terminal() removed - keep handler running for menu


def select_ai_difficulty(input_handler):
    """Show difficulty selection menu for VS AI mode."""
    difficulties = ['Easy', 'Medium', 'Hard']
    selected = 1  # Default to Medium
    
    # input_handler passed from menu
    input_handler.set_mode("key")
    
    try:
        while True:
            clear_screen()
            
            w = get_menu_width()
            inner_w = w - 2
            v = get_box_char('v')
            vc = colorize(v, Style.WHITE)
            
            lines = []
            
            # Box top
            lines.append(colorize(draw_box_top(w, 'rounded'), Style.WHITE))
            
            # Title - centered with padding
            title = bold("Select Difficulty")
            title_padded = pad_line(center_text(title, inner_w), inner_w)
            lines.append(f"{vc}{title_padded}{vc}")
            
            # Separator
            lines.append(colorize(draw_box_separator(w, 'single'), Style.WHITE))
            lines.append(f"{vc}{' ' * inner_w}{vc}")
            
            # Difficulty options - centered
            arrow = get_symbol('arrow_right')
            for i, diff in enumerate(difficulties):
                if i == selected:
                    opt = f"{colorize(arrow, Style.GREEN)} {bold(diff)}"
                else:
                    opt = f"  {dim(diff)}"
                opt_padded = pad_line(center_text(opt, inner_w), inner_w)
                lines.append(f"{vc}{opt_padded}{vc}")
            
            lines.append(f"{vc}{' ' * inner_w}{vc}")
            
            # Navigation hint - centered
            nav = dim("[W/S] Navigate  [Enter] Select  [Q] Back")
            nav_padded = pad_line(center_text(nav, inner_w), inner_w)
            lines.append(f"{vc}{nav_padded}{vc}")
            
            # Box bottom
            lines.append(colorize(draw_box_bottom(w, 'rounded'), Style.WHITE))
            
            # Print centered
            for line in center_block(lines):
                print(line)
            
            # Wait for input
            while True:
                key = input_handler.get_key()
                if key:
                    break
                time.sleep(0.05)
            
            if key == 'W' or key == 'UP':
                selected = (selected - 1) % len(difficulties)
            elif key == 'S' or key == 'DOWN':
                selected = (selected + 1) % len(difficulties)
            elif key == '\r' or key == '\n' or key == 'ENTER':
                return difficulties[selected].lower()
            elif key == 'Q':
                return None
    except:
        pass


def run_menu():
    """Run interactive menu with arrow key navigation."""
    selected = 0
    max_options = len(MENU_OPTIONS)
    
    input_handler = InputHandler()
    input_handler.start()
    input_handler.set_mode("key")
    
    try:
        while True:
            show_menu(selected)
            
            # Wait for key press
            while True:
                key = input_handler.get_key()
                if key:
                    break
                time.sleep(0.05)
            
            # Handle navigation
            if key == 'W' or key == 'UP':
                selected = (selected - 1) % max_options
            elif key == 'S' or key == 'DOWN':
                selected = (selected + 1) % max_options
            elif key == '\r' or key == '\n' or key == 'ENTER':
                # Execute selected action
                action = MENU_OPTIONS[selected][2]
                if action == "host":
                    input_handler.stop()
                    host_game()
                    input_handler.start()
                    input_handler.set_mode("key")
                elif action == "join":
                    input_handler.stop()
                    join_game()
                    input_handler.start()
                    input_handler.set_mode("key")
                elif action == "ai":
                    difficulty = select_ai_difficulty(input_handler)
                    if difficulty:
                        play_vs_ai(input_handler, difficulty)
                    input_handler.set_mode("key")
                elif action == "quit":
                    break
            elif key == 'Q':
                break
            elif key == '1':
                input_handler.stop()
                host_game()
                input_handler.start()
                input_handler.set_mode("key")
            elif key == '2':
                input_handler.stop()
                join_game()
                input_handler.start()
                input_handler.set_mode("key")
            elif key == '3':
                difficulty = select_ai_difficulty(input_handler)
                if difficulty:
                    play_vs_ai(input_handler, difficulty)
                input_handler.set_mode("key")
                
    finally:
        input_handler.stop()


def main():
    """Main entry point."""
    logger.info("Terminal Pong started")
    
    try:
        run_menu()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        clear_screen()
        print()
        print(colorize("  Thank you for playing Terminal Pong!", Style.WHITE))
        print()
        restore_terminal()
        logger.info("Terminal Pong exited")


if __name__ == "__main__":
    main()
