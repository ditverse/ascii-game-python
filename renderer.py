"""
Renderer Module
ASCII/Unicode rendering for lobby and game screens with color support.
"""

import re

from config import (
    GAME_WIDTH, GAME_HEIGHT, PADDLE_HEIGHT, MAX_CHAT_HISTORY,
    BALL_CHAR, PADDLE_CHAR, NET_CHAR, ENABLE_COLORS, ENABLE_UNICODE
)
from input_handler import clear_screen
from colors import (
    Style, colorize, COLORS_ENABLED,
    bold, dim, red, green, yellow, blue, cyan, magenta,
    success, error, warning, info, player1_color, player2_color
)
from ui_components import (
    get_box_char, get_symbol, get_terminal_size, center_text,
    draw_box_top, draw_box_bottom, draw_box_middle, draw_box_separator,
    status_indicator, center_block, get_lobby_width
)


def pad_line(content, width):
    """Pad content to width, accounting for ANSI codes."""
    visible = re.sub(r'\033\[[0-9;]*m', '', content)
    padding = width - len(visible)
    if padding > 0:
        return content + ' ' * padding
    return content


def render_lobby(lobby_state, player_id, input_text=""):
    """Render the lobby screen with clean UI."""
    clear_screen()
    
    w = get_lobby_width()  # Dynamic width based on terminal
    inner_w = w - 2
    v = get_box_char('v')
    vc = colorize(v, Style.WHITE)
    
    lines = []
    
    # Header - Single line border (rounded style)
    lines.append(colorize(draw_box_top(w, 'rounded'), Style.WHITE))
    
    # Title - centered, title case
    title = bold("Game Lobby")
    title_padded = pad_line(center_text(title, inner_w), inner_w)
    lines.append(f"{vc}{title_padded}{vc}")
    
    lines.append(colorize(draw_box_separator(w, 'single'), Style.WHITE))
    
    # Player status section - centered
    p1_connected = lobby_state.players_connected[0]
    p2_connected = lobby_state.players_connected[1]
    
    p1_indicator = get_symbol('bullet') if p1_connected else get_symbol('circle')
    p2_indicator = get_symbol('bullet') if p2_connected else get_symbol('circle')
    
    if p1_connected:
        p1_status = f"{colorize(p1_indicator, Style.GREEN)} Player 1: {green('Ready')}"
    else:
        p1_status = f"{dim(p1_indicator)} Player 1: {dim('Waiting...')}"
    
    if p2_connected:
        p2_status = f"{colorize(p2_indicator, Style.GREEN)} Player 2: {green('Ready')}"
    else:
        p2_status = f"{dim(p2_indicator)} Player 2: {dim('Waiting...')}"
    
    status_line = f"{p1_status}  |  {p2_status}"
    status_padded = pad_line(center_text(status_line, inner_w), inner_w)
    lines.append(f"{vc}{status_padded}{vc}")
    
    # Last game result (if any) - scalable centered layout
    if lobby_state.last_winner is not None:
        lines.append(colorize(draw_box_separator(w, 'single'), Style.WHITE))
        
        if lobby_state.last_winner == 1:
            winner_text = f"Player 1 {bold('WINS!')}"
        else:
            winner_text = f"Player 2 {bold('WINS!')}"
        
        winner_padded = pad_line(center_text(winner_text, inner_w), inner_w)
        lines.append(f"{vc}{winner_padded}{vc}")
        
        p1_score = lobby_state.last_score1
        p2_score = lobby_state.last_score2
        score_text = f"Score: P1 [{p1_score}] - [{p2_score}] P2"
        score_padded = pad_line(center_text(score_text, inner_w), inner_w)
        lines.append(f"{vc}{score_padded}{vc}")
    
    # Chat section
    lines.append(colorize(draw_box_separator(w, 'single'), Style.WHITE))
    chat_header = bold("Chat")
    chat_padded = pad_line(center_text(chat_header, inner_w), inner_w)
    lines.append(f"{vc}{chat_padded}{vc}")
    lines.append(colorize(draw_box_separator(w, 'single'), Style.DIM))
    
    # Chat messages
    chat_lines_count = MAX_CHAT_HISTORY - 2 if lobby_state.last_winner else MAX_CHAT_HISTORY
    for i in range(chat_lines_count):
        if i < len(lobby_state.chat_history):
            pid, msg = lobby_state.chat_history[i]
            if pid == 1:
                player_tag = "[P1]"
            else:
                player_tag = dim("[P2]")
            line = f"  {player_tag} {msg}"
            
            # Truncate if too long (basic handling)
            visible_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
            if visible_len > inner_w:
                line = line[:inner_w - 3] + "..."
                
            lines.append(f"{vc}{pad_line(line, inner_w)}{vc}")
        else:
            lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    # Instructions - Quit on left, [Q] on right
    lines.append(colorize(draw_box_separator(w, 'single'), Style.DIM))
    
    if player_id == 1:
        left_ctrl = f" {bold('[TAB]')} Start Game"
        right_ctrl = f"Quit {bold('[Q]')} "
    else:
        left_ctrl = f" {dim('Waiting for host...')}"
        right_ctrl = f"Quit {bold('[Q]')} "
    
    # Calculate padding for right-aligned quit
    left_visible = len(re.sub(r'\033\[[0-9;]*m', '', left_ctrl))
    right_visible = len(re.sub(r'\033\[[0-9;]*m', '', right_ctrl))
    middle_space = inner_w - left_visible - right_visible
    controls_line = f"{left_ctrl}{' ' * max(0, middle_space)}{right_ctrl}"
    
    lines.append(f"{vc}{controls_line}{vc}")
    
    # Input line
    lines.append(colorize(draw_box_separator(w, 'single'), Style.DIM))
    
    cursor = "_"
    input_display = f" > {input_text}{cursor}"
    lines.append(f"{vc}{pad_line(input_display, inner_w)}{vc}")
    
    # Footer
    lines.append(colorize(draw_box_bottom(w, 'rounded'), Style.WHITE))
    
    # Print centered
    for line in center_block(lines):
        print(line)


def render_game(state, player_id):
    """Render the game state with ASCII art."""
    clear_screen()
    
    # Create field buffer
    field = [[' ' for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
    
    # Draw center net
    center_x = GAME_WIDTH // 2
    net_char = NET_CHAR
    for y in range(GAME_HEIGHT):
        if y % 2 == 0:
            field[y][center_x] = net_char
    
    # Paddle positions
    paddle1_x = 2
    paddle2_x = GAME_WIDTH - 3
    
    # Draw paddles
    paddle_char = PADDLE_CHAR if ENABLE_UNICODE else '|'
    for i in range(PADDLE_HEIGHT):
        y1 = state.paddle1_y + i
        y2 = state.paddle2_y + i
        if 0 <= y1 < GAME_HEIGHT:
            field[y1][paddle1_x] = paddle_char
        if 0 <= y2 < GAME_HEIGHT:
            field[y2][paddle2_x] = paddle_char
    
    # Draw ball
    ball_x = int(state.ball_x)
    ball_y = int(state.ball_y)
    ball_char = BALL_CHAR if ENABLE_UNICODE else 'O'
    if 0 <= ball_x < GAME_WIDTH and 0 <= ball_y < GAME_HEIGHT:
        field[ball_y][ball_x] = ball_char
    
    # Check if ball is near goal (for warning effect)
    ball_near_goal = ball_x < 8 or ball_x > GAME_WIDTH - 8
    
    # === RENDER OUTPUT ===
    screen_lines = []
    
    # Score display (no header title)
    if player_id == 1:
        you_label = f"YOU (P1): {state.score1}"
        opp_label = f"Opponent (P2): {state.score2}"
    else:
        you_label = f"YOU (P2): {state.score2}"
        opp_label = f"Opponent (P1): {state.score1}"
    
    score_line = f"  {bold(you_label)}  |  {dim(opp_label)}"
    screen_lines.append(pad_line(score_line, GAME_WIDTH + 2))
    
    # Top border
    top_border = get_box_char('tl') + get_box_char('h') * GAME_WIDTH + get_box_char('tr')
    screen_lines.append(colorize(top_border, Style.DIM))
    
    # Render field
    for y, row in enumerate(field):
        line_content = ""
        for x, char in enumerate(row):
            if char == paddle_char:
                # Highlight paddles
                if x < GAME_WIDTH // 2:
                    line_content += bold(char)
                else:
                    line_content += dim(char)
            elif char == ball_char:
                # Ball with warning effect
                if ball_near_goal:
                    line_content += colorize(char, Style.BOLD, Style.RED)
                else:
                    line_content += bold(char)
            elif char == net_char:
                line_content += dim(char)
            else:
                line_content += char
        
        v = colorize(get_box_char('v'), Style.DIM)
        screen_lines.append(f"{v}{line_content}{v}")
    
    # Bottom border
    bottom_border = get_box_char('bl') + get_box_char('h') * GAME_WIDTH + get_box_char('br')
    screen_lines.append(colorize(bottom_border, Style.DIM))
    
    # Controls (no footer thick line)
    controls = f"  Controls: {bold('[W]')} Up  {bold('[S]')} Down  |  {dim('[Q] Quit')}"
    screen_lines.append(pad_line(controls, GAME_WIDTH + 2))
    
    # Render Centered
    for line in center_block(screen_lines):
        print(line)


def show_game_over(winner, player_id):
    """Display game over screen."""
    clear_screen()
    
    w = 50
    inner_w = w - 2
    
    v = get_box_char('dv')
    vc = colorize(v, Style.WHITE)
    
    lines = []
    lines.append(colorize(draw_box_top(w, 'double'), Style.WHITE))
    
    # Title
    title = bold("GAME OVER")
    lines.append(f"{vc}{center_text(title, inner_w)}{vc}")
    
    lines.append(colorize(draw_box_separator(w, 'double'), Style.WHITE))
    lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    # Winner announcement
    if winner == player_id:
        result = bold("CONGRATULATIONS! YOU WIN!")
    else:
        result = "Better luck next time!"
    
    lines.append(f"{vc}{center_text(result, inner_w)}{vc}")
    lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    lines.append(colorize(draw_box_separator(w, 'double'), Style.WHITE))
    
    # Return message
    return_msg = dim("Returning to lobby in 3 seconds...")
    lines.append(f"{vc}{center_text(return_msg, inner_w)}{vc}")
    
    lines.append(colorize(draw_box_bottom(w, 'double'), Style.WHITE))
    
    # Render Centered
    for line in center_block(lines):
        print(line)


def show_connecting():
    """Display connecting animation."""
    clear_screen()
    
    lines = []
    lines.append(colorize(draw_box_top(40, 'rounded'), Style.WHITE))
    lines.append(f"{get_box_char('v')}{center_text('Connecting...', 38)}{get_box_char('v')}")
    lines.append(colorize(draw_box_bottom(40, 'rounded'), Style.WHITE))
    
    # Render Centered
    for line in center_block(lines):
        print(line)


def show_waiting_for_player():
    """Display waiting for opponent screen."""
    clear_screen()
    
    lines = []
    lines.append(colorize(draw_box_top(50, 'double'), Style.WHITE))
    
    title = bold("TERMINAL PONG")
    lines.append(f"{colorize(get_box_char('dv'), Style.WHITE)}{center_text(title, 48)}{colorize(get_box_char('dv'), Style.WHITE)}")
    
    lines.append(colorize(draw_box_separator(50, 'double'), Style.WHITE))
    
    waiting = "Waiting for opponent to connect..."
    lines.append(f"{colorize(get_box_char('dv'), Style.WHITE)}{center_text(waiting, 48)}{colorize(get_box_char('dv'), Style.WHITE)}")
    
    lines.append(colorize(draw_box_bottom(50, 'double'), Style.WHITE))
    
    # Render Centered
    for line in center_block(lines):
        print(line)


def render_game_ai(state):
    """Render game screen for VS AI mode."""
    clear_screen()
    
    # Create field
    field = [[' ' for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
    
    # Draw center net
    center_x = GAME_WIDTH // 2
    net_char = NET_CHAR
    for y in range(GAME_HEIGHT):
        if y % 2 == 0:
            field[y][center_x] = net_char
    
    # Paddle positions
    paddle1_x = 2
    paddle2_x = GAME_WIDTH - 3
    
    # Draw paddles
    paddle_char = PADDLE_CHAR if ENABLE_UNICODE else '|'
    for i in range(PADDLE_HEIGHT):
        y1 = state.paddle1_y + i
        if 0 <= y1 < GAME_HEIGHT:
            field[y1][paddle1_x] = paddle_char
    
    for i in range(PADDLE_HEIGHT):
        y2 = state.paddle2_y + i
        if 0 <= y2 < GAME_HEIGHT:
            field[y2][paddle2_x] = paddle_char
    
    # Draw ball
    ball_x = int(state.ball_x)
    ball_y = int(state.ball_y)
    ball_char = BALL_CHAR if ENABLE_UNICODE else 'O'
    if 0 <= ball_x < GAME_WIDTH and 0 <= ball_y < GAME_HEIGHT:
        field[ball_y][ball_x] = ball_char
    
    # Ball near goal warning
    ball_near_goal = ball_x < 8 or ball_x > GAME_WIDTH - 8
    
    # === RENDER OUTPUT ===
    screen_lines = []
    
    # Score display
    you_label = f"YOU: {state.score1}"
    ai_label = f"AI: {state.score2}"
    score_line = f"  {bold(you_label)}  |  {dim(ai_label)}"
    screen_lines.append(pad_line(score_line, GAME_WIDTH + 2))
    
    # Top border
    top_border = get_box_char('tl') + get_box_char('h') * GAME_WIDTH + get_box_char('tr')
    screen_lines.append(colorize(top_border, Style.DIM))
    
    # Render field
    for y, row in enumerate(field):
        line_content = ""
        for x, char in enumerate(row):
            if char == paddle_char:
                if x < GAME_WIDTH // 2:
                    line_content += bold(char)
                else:
                    line_content += dim(char)
            elif char == ball_char:
                if ball_near_goal:
                    line_content += colorize(char, Style.BOLD, Style.RED)
                else:
                    line_content += bold(char)
            elif char == net_char:
                line_content += dim(char)
            else:
                line_content += char
        
        v = colorize(get_box_char('v'), Style.DIM)
        screen_lines.append(f"{v}{line_content}{v}")
    
    # Bottom border
    bottom_border = get_box_char('bl') + get_box_char('h') * GAME_WIDTH + get_box_char('br')
    screen_lines.append(colorize(bottom_border, Style.DIM))
    
    # Controls
    controls = f"  Controls: {bold('[W]')} Up  {bold('[S]')} Down  |  {dim('[Q] Quit')}"
    screen_lines.append(pad_line(controls, GAME_WIDTH + 2))
    
    # Render Centered
    for line in center_block(screen_lines):
        print(line)


def show_game_over_ai(winner):
    """Display game over screen for VS AI mode - responsive with rounded borders."""
    clear_screen()
    
    w = get_lobby_width()
    inner_w = w - 2
    
    v = get_box_char('v')
    vc = colorize(v, Style.WHITE)
    
    lines = []
    
    # Top border (rounded)
    lines.append(colorize(draw_box_top(w, 'rounded'), Style.WHITE))
    
    # Title - centered with proper padding
    title = bold("GAME OVER")
    title_padded = pad_line(center_text(title, inner_w), inner_w)
    lines.append(f"{vc}{title_padded}{vc}")
    
    # Separator
    lines.append(colorize(draw_box_separator(w, 'single'), Style.WHITE))
    lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    # Winner announcement - centered
    if winner == 1:
        result = bold("CONGRATULATIONS! YOU WIN!")
    else:
        result = "AI Wins! Better luck next time!"
    result_padded = pad_line(center_text(result, inner_w), inner_w)
    lines.append(f"{vc}{result_padded}{vc}")
    
    lines.append(f"{vc}{' ' * inner_w}{vc}")
    
    # Separator
    lines.append(colorize(draw_box_separator(w, 'single'), Style.WHITE))
    
    # Return message - centered
    return_msg = dim("Returning to menu in 3 seconds...")
    return_padded = pad_line(center_text(return_msg, inner_w), inner_w)
    lines.append(f"{vc}{return_padded}{vc}")
    
    # Bottom border (rounded)
    lines.append(colorize(draw_box_bottom(w, 'rounded'), Style.WHITE))
    
    # Render Centered
    for line in center_block(lines):
        print(line)


def render_game_with_effects(state, player_id, effects_manager=None, powerup_manager=None):
    """
    Render the game state with visual effects.
    
    Args:
        state: GameState object
        player_id: Current player ID (1 or 2)
        effects_manager: Optional EffectsManager for visual effects
        powerup_manager: Optional PowerUpManager for power-up display
    """
    clear_screen()
    
    # Get paddle heights (support power-ups)
    paddle1_height = getattr(state, 'paddle1_height', PADDLE_HEIGHT)
    paddle2_height = getattr(state, 'paddle2_height', PADDLE_HEIGHT)
    
    # Create field buffer with effects layer
    field = [[' ' for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
    effect_layer = [[None for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
    
    # Draw effects first (background layer)
    if effects_manager:
        # Update effects
        effects_manager.update()
        effects_manager.update_ball_trail(state.ball_x, state.ball_y)
        
        # Get all particles
        for x, y, char, effect_type in effects_manager.get_all_particles():
            if 0 <= x < GAME_WIDTH and 0 <= y < GAME_HEIGHT:
                effect_layer[int(y)][int(x)] = (char, effect_type)
    
    # Draw power-ups
    if powerup_manager:
        for powerup in powerup_manager.get_field_powerups():
            px, py = int(powerup.x), int(powerup.y)
            if 0 <= px < GAME_WIDTH and 0 <= py < GAME_HEIGHT:
                field[py][px] = powerup.symbol
    
    # Draw center net
    center_x = GAME_WIDTH // 2
    net_char = NET_CHAR
    for y in range(GAME_HEIGHT):
        if y % 2 == 0:
            field[y][center_x] = net_char
    
    # Paddle positions
    paddle1_x = 2
    paddle2_x = GAME_WIDTH - 3
    
    # Draw paddles with dynamic heights
    paddle_char = PADDLE_CHAR if ENABLE_UNICODE else '|'
    for i in range(paddle1_height):
        y1 = state.paddle1_y + i
        if 0 <= y1 < GAME_HEIGHT:
            field[y1][paddle1_x] = paddle_char
    
    for i in range(paddle2_height):
        y2 = state.paddle2_y + i
        if 0 <= y2 < GAME_HEIGHT:
            field[y2][paddle2_x] = paddle_char
    
    # Draw ball
    ball_x = int(state.ball_x)
    ball_y = int(state.ball_y)
    ball_char = BALL_CHAR if ENABLE_UNICODE else 'O'
    if 0 <= ball_x < GAME_WIDTH and 0 <= ball_y < GAME_HEIGHT:
        field[ball_y][ball_x] = ball_char
    
    # Check if ball is near goal (for warning effect)
    ball_near_goal = ball_x < 8 or ball_x > GAME_WIDTH - 8
    
    # === RENDER OUTPUT ===
    screen_lines = []
    
    # Score display
    if player_id == 1:
        you_label = f"YOU (P1): {state.score1}"
        opp_label = f"Opponent (P2): {state.score2}"
    else:
        you_label = f"YOU (P2): {state.score2}"
        opp_label = f"Opponent (P1): {state.score1}"
    
    score_line = f"  {bold(you_label)}  |  {dim(opp_label)}"
    
    # Active effects indicator
    if effects_manager:
        active_effects = []
        if powerup_manager:
            for effect in powerup_manager.get_active_effects():
                remaining = effect.effect_duration - (
                    __import__('time').time() - effect.effect_start_time
                )
                if remaining > 0:
                    active_effects.append(f"{effect.symbol} {effect.name}: {remaining:.1f}s")
        if active_effects:
            effects_str = "  |  " + "  ".join(active_effects)
            score_line += dim(effects_str)
    
    screen_lines.append(pad_line(score_line, GAME_WIDTH + 2))
    
    # Top border
    top_border = get_box_char('tl') + get_box_char('h') * GAME_WIDTH + get_box_char('tr')
    screen_lines.append(colorize(top_border, Style.DIM))
    
    # Render field with effects
    for y, row in enumerate(field):
        line_content = ""
        for x, char in enumerate(row):
            # Check for effect at this position
            effect = effect_layer[y][x]
            
            if effect:
                eff_char, eff_type = effect
                # Render effect with appropriate style
                if eff_type == 'explosion':
                    line_content += colorize(eff_char, Style.BOLD, Style.YELLOW)
                elif eff_type == 'trail':
                    line_content += dim(eff_char)
                elif eff_type == 'hit':
                    line_content += colorize(eff_char, Style.CYAN)
                else:
                    line_content += eff_char
            elif char == paddle_char:
                # Highlight paddles
                if x < GAME_WIDTH // 2:
                    line_content += bold(char)
                else:
                    line_content += dim(char)
            elif char == ball_char:
                # Ball with warning effect
                if ball_near_goal:
                    line_content += colorize(char, Style.BOLD, Style.RED)
                else:
                    line_content += bold(char)
            elif char == net_char:
                line_content += dim(char)
            elif char in ['+', '-', 'S']:  # Power-up symbols (ASCII)
                line_content += colorize(char, Style.BOLD, Style.YELLOW)
            else:
                line_content += char
        
        v = colorize(get_box_char('v'), Style.DIM)
        screen_lines.append(f"{v}{line_content}{v}")
    
    # Bottom border
    bottom_border = get_box_char('bl') + get_box_char('h') * GAME_WIDTH + get_box_char('br')
    screen_lines.append(colorize(bottom_border, Style.DIM))
    
    # Controls
    controls = f"  Controls: {bold('[W]')} Up  {bold('[S]')} Down  |  {dim('[Q] Quit')}"
    screen_lines.append(pad_line(controls, GAME_WIDTH + 2))
    
    # Render Centered
    for line in center_block(screen_lines):
        print(line)
