from config import GAME_WIDTH, GAME_HEIGHT, PADDLE_HEIGHT, LOBBY_WIDTH, MAX_CHAT_HISTORY
from input_handler import clear_screen


def render_lobby(lobby_state, player_id, input_text=""):
    """Render the lobby screen."""
    clear_screen()
    
    w = LOBBY_WIDTH
    
    print("+" + "=" * w + "+")
    print("|" + "GAME LOBBY".center(w) + "|")
    print("+" + "-" * w + "+")
    
    # Player status
    p1_status = "Connected" if lobby_state.players_connected[0] else "Waiting..."
    p2_status = "Connected" if lobby_state.players_connected[1] else "Waiting..."
    status_line = f"  Player 1: {p1_status}  |  Player 2: {p2_status}"
    print("|" + status_line.ljust(w) + "|")
    
    # Last game result
    if lobby_state.last_winner is not None:
        print("+" + "-" * w + "+")
        winner_text = f"Last Game: Player {lobby_state.last_winner} WINS!"
        score_text = f"Score: P1 [{lobby_state.last_score1}] - [{lobby_state.last_score2}] P2"
        print("|" + winner_text.center(w) + "|")
        print("|" + score_text.center(w) + "|")
    
    print("+" + "-" * w + "+")
    print("|" + " CHAT".ljust(w) + "|")
    print("+" + "-" * w + "+")
    
    # Chat messages (reduce if game result shown)
    chat_lines = MAX_CHAT_HISTORY - 2 if lobby_state.last_winner else MAX_CHAT_HISTORY
    for i in range(chat_lines):
        if i < len(lobby_state.chat_history):
            pid, msg = lobby_state.chat_history[i]
            player_tag = f"[P{pid}]"
            line = f"  {player_tag} {msg}"
            print("|" + line[:w].ljust(w) + "|")
        else:
            print("|" + " " * w + "|")
    
    print("+" + "-" * w + "+")
    
    # Instructions - changed S to TAB
    if player_id == 1:
        print("|" + "  [TAB] Start Game  |  [Q] Quit".ljust(w) + "|")
    else:
        print("|" + "  Waiting for host to start...  |  [Q] Quit".ljust(w) + "|")
    
    print("+" + "-" * w + "+")
    
    # Input line
    input_display = f"> {input_text}_"
    print("|" + input_display[:w].ljust(w) + "|")
    print("+" + "=" * w + "+")


def render_game(state, player_id):
    """Render the game state as ASCII art."""
    clear_screen()
    
    field = [[' ' for _ in range(GAME_WIDTH)] for _ in range(GAME_HEIGHT)]
    
    # Draw center net
    center_x = GAME_WIDTH // 2
    for y in range(GAME_HEIGHT):
        if y % 2 == 0:
            field[y][center_x] = ':'
    
    # Draw paddles
    paddle1_x = 2
    paddle2_x = GAME_WIDTH - 3
    
    for i in range(PADDLE_HEIGHT):
        y1 = state.paddle1_y + i
        y2 = state.paddle2_y + i
        if 0 <= y1 < GAME_HEIGHT:
            field[y1][paddle1_x] = '|'
        if 0 <= y2 < GAME_HEIGHT:
            field[y2][paddle2_x] = '|'
    
    # Draw ball
    ball_x = int(state.ball_x)
    ball_y = int(state.ball_y)
    if 0 <= ball_x < GAME_WIDTH and 0 <= ball_y < GAME_HEIGHT:
        field[ball_y][ball_x] = 'O'
    
    top_border = '+' + '-' * GAME_WIDTH + '+'
    
    player_label = f"YOU (P{player_id})"
    opponent_label = f"Opponent (P{2 if player_id == 1 else 1})"
    
    if player_id == 1:
        score_line = f"  {player_label}: {state.score1}  |  {opponent_label}: {state.score2}"
    else:
        score_line = f"  {opponent_label}: {state.score1}  |  {player_label}: {state.score2}"
    
    print("\n" + "=" * (GAME_WIDTH + 2))
    print("  TERMINAL PONG - Network Programming")
    print("=" * (GAME_WIDTH + 2))
    print(score_line)
    print(top_border)
    
    for row in field:
        print('|' + ''.join(row) + '|')
    
    print(top_border)
    print("  Controls: W = Up, S = Down")
    print("=" * (GAME_WIDTH + 2))


def show_game_over(winner, player_id):
    """Display game over screen."""
    clear_screen()
    print("\n" + "=" * 40)
    print("           GAME OVER!")
    print("=" * 40)
    
    if winner == player_id:
        print("\n       CONGRATULATIONS! YOU WIN!")
    else:
        print("\n       YOU LOSE! Better luck next time!")
    
    print("\n" + "=" * 40)
    print("  Returning to lobby in 3 seconds...")
    print("=" * 40)
