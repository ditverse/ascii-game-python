#!/usr/bin/env python3
"""
Terminal Pong - CLI-Based Multiplayer Game
Network Programming Final Project

A real-time multiplayer Pong game running entirely in CLI/Terminal using ASCII graphics.
Uses Host-Client architecture over TCP sockets.
Features: Chat Lobby, Real-time gameplay, ASCII UI
"""

import socket
import threading
import time
import os
import sys
import random

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

GAME_WIDTH = 60
GAME_HEIGHT = 20
PADDLE_HEIGHT = 4
WIN_SCORE = 5
FPS = 20
FRAME_TIME = 1.0 / FPS

PORT = 5555
BUFFER_SIZE = 2048

# Ball speed
BALL_SPEED_X = 1.5
BALL_SPEED_Y = 1.0

# Lobby settings
MAX_CHAT_HISTORY = 8
LOBBY_WIDTH = 62

# ============================================================================
# CROSS-PLATFORM INPUT HANDLING
# ============================================================================

class InputHandler:
    """Thread-safe input handler for cross-platform keyboard input."""
    
    def __init__(self):
        self.current_key = None
        self.current_line = ""
        self.line_ready = False
        self.lock = threading.Lock()
        self.running = True
        self._old_settings = None
        self._thread = None
        self.mode = "key"  # "key" for single key, "line" for text input
        
    def start(self):
        """Start the input handler thread."""
        if os.name != 'nt':
            import termios
            try:
                self._old_settings = termios.tcgetattr(sys.stdin.fileno())
            except:
                pass
        
        self._thread = threading.Thread(target=self._input_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the input handler and restore terminal."""
        self.running = False
        if os.name != 'nt' and self._old_settings:
            import termios
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except:
                pass
    
    def set_mode(self, mode):
        """Set input mode: 'key' or 'line'."""
        with self.lock:
            self.mode = mode
            self.current_line = ""
            self.line_ready = False
    
    def get_key(self):
        """Get the current key (thread-safe)."""
        with self.lock:
            key = self.current_key
            self.current_key = None
            return key
    
    def get_line(self):
        """Get completed line input."""
        with self.lock:
            if self.line_ready:
                line = self.current_line
                self.current_line = ""
                self.line_ready = False
                return line
            return None
    
    def get_partial_line(self):
        """Get current partial line being typed."""
        with self.lock:
            return self.current_line
    
    def _input_loop(self):
        """Background thread that reads keyboard input."""
        if os.name == 'nt':
            self._windows_input_loop()
        else:
            self._linux_input_loop()
    
    def _windows_input_loop(self):
        """Windows input loop using msvcrt."""
        import msvcrt
        while self.running:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    try:
                        key_char = key.decode('utf-8')
                        self._process_key(key_char)
                    except:
                        pass
                time.sleep(0.01)
            except:
                break
    
    def _linux_input_loop(self):
        """Linux input loop using raw terminal mode."""
        import tty
        import termios
        import select
        
        fd = sys.stdin.fileno()
        try:
            tty.setcbreak(fd)
            while self.running:
                try:
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        key = sys.stdin.read(1)
                        self._process_key(key)
                except:
                    break
        finally:
            if self._old_settings:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
                except:
                    pass
    
    def _process_key(self, key):
        """Process a key press based on current mode."""
        with self.lock:
            # Always set current_key for single-key reading (used in game mode)
            self.current_key = key.upper()
            
            if self.mode == "line":
                # In line mode, also accumulate text for chat
                if key == '\r' or key == '\n':
                    self.line_ready = True
                elif key == '\x7f' or key == '\b':  # Backspace
                    self.current_line = self.current_line[:-1]
                elif key.isprintable() and key.upper() not in ['S', 'Q']:
                    # Don't add S/Q to chat line (they are commands)
                    if len(self.current_line) < 40:
                        self.current_line += key



def clear_screen():
    """Clear the terminal screen."""
    print("\033[H\033[J", end="", flush=True)


def restore_terminal():
    """Restore terminal to normal mode."""
    if os.name != 'nt':
        import termios
        os.system('stty sane')


# ============================================================================
# GAME STATE
# ============================================================================

class GameState:
    """Holds all game state data."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset game to initial state."""
        self.ball_x = GAME_WIDTH // 2
        self.ball_y = GAME_HEIGHT // 2
        self.ball_vx = BALL_SPEED_X * random.choice([-1, 1])
        self.ball_vy = BALL_SPEED_Y * random.choice([-1, 1])
        self.paddle1_y = GAME_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle2_y = GAME_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.score1 = 0
        self.score2 = 0
        self.running = True
        self.winner = None
    
    def serialize(self):
        """Convert state to string for network transmission."""
        return f"STATE,{self.ball_x:.2f},{self.ball_y:.2f},{self.paddle1_y},{self.paddle2_y},{self.score1},{self.score2}"
    
    @staticmethod
    def deserialize(data):
        """Parse state from network string."""
        parts = data.split(',')
        if parts[0] != 'STATE':
            return None
        state = GameState()
        state.ball_x = float(parts[1])
        state.ball_y = float(parts[2])
        state.paddle1_y = int(parts[3])
        state.paddle2_y = int(parts[4])
        state.score1 = int(parts[5])
        state.score2 = int(parts[6])
        return state


# ============================================================================
# LOBBY STATE
# ============================================================================

class LobbyState:
    """Holds lobby and chat data."""
    
    def __init__(self):
        self.chat_history = []  # List of (player_id, message)
        self.players_connected = [False, False]  # Player 1, Player 2
    
    def add_message(self, player_id, message):
        """Add a chat message."""
        self.chat_history.append((player_id, message))
        if len(self.chat_history) > MAX_CHAT_HISTORY:
            self.chat_history.pop(0)
    
    def serialize_chat(self):
        """Serialize chat for network."""
        messages = []
        for pid, msg in self.chat_history:
            messages.append(f"{pid}:{msg}")
        return "|".join(messages)
    
    @staticmethod
    def deserialize_chat(data):
        """Parse chat history from network."""
        if not data:
            return []
        messages = []
        for item in data.split("|"):
            if ":" in item:
                pid, msg = item.split(":", 1)
                messages.append((int(pid), msg))
        return messages


# ============================================================================
# LOBBY RENDERER
# ============================================================================

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
    
    print("+" + "-" * w + "+")
    print("|" + " CHAT".ljust(w) + "|")
    print("+" + "-" * w + "+")
    
    # Chat messages (show last MAX_CHAT_HISTORY)
    for i in range(MAX_CHAT_HISTORY):
        if i < len(lobby_state.chat_history):
            pid, msg = lobby_state.chat_history[i]
            player_tag = f"[P{pid}]"
            line = f"  {player_tag} {msg}"
            print("|" + line[:w].ljust(w) + "|")
        else:
            print("|" + " " * w + "|")
    
    print("+" + "-" * w + "+")
    
    # Instructions
    if player_id == 1:
        print("|" + "  [S] Start Game  |  [Q] Quit".ljust(w) + "|")
    else:
        print("|" + "  Waiting for host to start...  |  [Q] Quit".ljust(w) + "|")
    
    print("+" + "-" * w + "+")
    
    # Input line
    input_display = f"> {input_text}_"
    print("|" + input_display[:w].ljust(w) + "|")
    print("+" + "=" * w + "+")


# ============================================================================
# GAME RENDERER
# ============================================================================

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


# ============================================================================
# GAME PHYSICS
# ============================================================================

def update_physics(state):
    """Update ball position and handle collisions."""
    state.ball_x += state.ball_vx
    state.ball_y += state.ball_vy
    
    if state.ball_y <= 0 or state.ball_y >= GAME_HEIGHT - 1:
        state.ball_vy = -state.ball_vy
        state.ball_y = max(0, min(GAME_HEIGHT - 1, state.ball_y))
    
    paddle1_x = 2
    if state.ball_x <= paddle1_x + 1 and state.ball_vx < 0:
        if state.paddle1_y <= state.ball_y <= state.paddle1_y + PADDLE_HEIGHT:
            state.ball_vx = -state.ball_vx
            state.ball_x = paddle1_x + 1
    
    paddle2_x = GAME_WIDTH - 3
    if state.ball_x >= paddle2_x - 1 and state.ball_vx > 0:
        if state.paddle2_y <= state.ball_y <= state.paddle2_y + PADDLE_HEIGHT:
            state.ball_vx = -state.ball_vx
            state.ball_x = paddle2_x - 1
    
    if state.ball_x <= 0:
        state.score2 += 1
        reset_ball(state, direction=1)
    elif state.ball_x >= GAME_WIDTH - 1:
        state.score1 += 1
        reset_ball(state, direction=-1)
    
    if state.score1 >= WIN_SCORE:
        state.running = False
        state.winner = 1
    elif state.score2 >= WIN_SCORE:
        state.running = False
        state.winner = 2


def reset_ball(state, direction):
    """Reset ball to center after scoring."""
    state.ball_x = GAME_WIDTH // 2
    state.ball_y = GAME_HEIGHT // 2
    state.ball_vx = BALL_SPEED_X * direction
    state.ball_vy = BALL_SPEED_Y * random.choice([-1, 1])


def move_paddle(state, player_id, direction):
    """Move paddle up or down."""
    if player_id == 1:
        if direction == 'W':
            state.paddle1_y = max(0, state.paddle1_y - 1)
        elif direction == 'S':
            state.paddle1_y = min(GAME_HEIGHT - PADDLE_HEIGHT, state.paddle1_y + 1)
    else:
        if direction == 'W':
            state.paddle2_y = max(0, state.paddle2_y - 1)
        elif direction == 'S':
            state.paddle2_y = min(GAME_HEIGHT - PADDLE_HEIGHT, state.paddle2_y + 1)


# ============================================================================
# SERVER
# ============================================================================

class GameServer:
    """TCP Server that manages lobby and game."""
    
    def __init__(self):
        self.game_state = GameState()
        self.lobby_state = LobbyState()
        self.clients = {}
        self.client_sockets = []
        self.lock = threading.Lock()
        self.running = True
        self.in_lobby = True
        self.game_running = False
        self.players_ready = 0
    
    def get_local_ip(self):
        """Get the local LAN IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def start(self):
        """Start the game server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', PORT))
        self.server_socket.listen(2)
        
        local_ip = self.get_local_ip()
        print(f"\n[SERVER] Started on {local_ip}:{PORT}")
        print("[SERVER] Waiting for players...")
        
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
        return local_ip
    
    def accept_connections(self):
        """Accept incoming client connections."""
        player_id = 1
        while self.running and player_id <= 2:
            try:
                client_socket, addr = self.server_socket.accept()
                with self.lock:
                    self.clients[client_socket] = player_id
                    self.client_sockets.append(client_socket)
                    self.lobby_state.players_connected[player_id - 1] = True
                
                print(f"[SERVER] Player {player_id} connected from {addr}")
                client_socket.send(f"PLAYER,{player_id}".encode())
                
                handler = threading.Thread(target=self.handle_client, args=(client_socket, player_id))
                handler.daemon = True
                handler.start()
                
                player_id += 1
                
                if player_id > 2:
                    print("[SERVER] All players connected! Entering lobby...")
                    self.broadcast("LOBBY_READY")
                    self.broadcast_lobby_state()
                    
            except Exception as e:
                if self.running:
                    print(f"[SERVER] Error: {e}")
    
    def handle_client(self, client_socket, player_id):
        """Handle messages from a client."""
        while self.running:
            try:
                data = client_socket.recv(BUFFER_SIZE).decode()
                if not data:
                    break
                
                # Handle multiple messages in buffer
                for message in data.split('\n'):
                    if not message:
                        continue
                    self.process_message(message, player_id)
                            
            except Exception as e:
                break
        
        print(f"[SERVER] Player {player_id} disconnected")
        with self.lock:
            self.lobby_state.players_connected[player_id - 1] = False
    
    def process_message(self, message, player_id):
        """Process a single message from client."""
        if message.startswith("CHAT,"):
            chat_msg = message[5:]
            with self.lock:
                self.lobby_state.add_message(player_id, chat_msg)
            self.broadcast_lobby_state()
            
        elif message.startswith("INPUT,"):
            direction = message.split(',')[1]
            with self.lock:
                if direction in ['W', 'S']:
                    move_paddle(self.game_state, player_id, direction)
                    
        elif message == "START_GAME" and player_id == 1:
            # Run game in separate thread to avoid blocking handle_client
            game_thread = threading.Thread(target=self.start_game)
            game_thread.daemon = True
            game_thread.start()
    
    def broadcast(self, message):
        """Send message to all clients."""
        for client_socket in self.client_sockets:
            try:
                client_socket.send((message + "\n").encode())
            except:
                pass
    
    def broadcast_lobby_state(self):
        """Send lobby state to all clients."""
        with self.lock:
            chat_data = self.lobby_state.serialize_chat()
            p1 = "1" if self.lobby_state.players_connected[0] else "0"
            p2 = "1" if self.lobby_state.players_connected[1] else "0"
        self.broadcast(f"LOBBY_STATE,{p1},{p2},{chat_data}")
    
    def start_game(self):
        """Start the game from lobby."""
        with self.lock:
            self.in_lobby = False
            self.game_running = True
            self.game_state.reset()
        
        self.broadcast("GAME_START")
        time.sleep(0.5)
        
        # Run game loop
        self.run_game_loop()
        
        # Return to lobby
        with self.lock:
            self.in_lobby = True
            self.game_running = False
        
        time.sleep(3)
        self.broadcast("RETURN_LOBBY")
        self.broadcast_lobby_state()
    
    def run_game_loop(self):
        """Main game physics loop."""
        while self.game_state.running and self.running:
            start_time = time.time()
            
            with self.lock:
                update_physics(self.game_state)
                state_data = self.game_state.serialize()
            
            self.broadcast(state_data)
            
            if not self.game_state.running:
                self.broadcast(f"GAMEOVER,{self.game_state.winner}")
                break
            
            elapsed = time.time() - start_time
            if elapsed < FRAME_TIME:
                time.sleep(FRAME_TIME - elapsed)
    
    def stop(self):
        """Stop the server."""
        self.running = False
        for client_socket in self.client_sockets:
            try:
                client_socket.close()
            except:
                pass
        try:
            self.server_socket.close()
        except:
            pass


# ============================================================================
# CLIENT
# ============================================================================

class GameClient:
    """TCP Client for connecting to game server."""
    
    def __init__(self):
        self.socket = None
        self.player_id = None
        self.game_state = GameState()
        self.lobby_state = LobbyState()
        self.running = True
        self.in_lobby = False
        self.in_game = False
        self.lock = threading.Lock()
        self.input_handler = None
    
    def connect(self, host_ip):
        """Connect to game server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host_ip, PORT))
            self.socket.settimeout(None)
            
            data = self.socket.recv(BUFFER_SIZE).decode()
            if data.startswith("PLAYER,"):
                self.player_id = int(data.split(',')[1])
                print(f"\n[CLIENT] Connected as Player {self.player_id}")
                print("[CLIENT] Waiting for lobby...")
                return True
            return False
            
        except socket.timeout:
            print("[CLIENT] Connection timeout!")
            return False
        except ConnectionRefusedError:
            print("[CLIENT] Connection refused!")
            return False
        except Exception as e:
            print(f"[CLIENT] Error: {e}")
            return False
    
    def receive_updates(self):
        """Receive updates from server."""
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode()
                if not data:
                    break
                
                buffer += data
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    self.process_message(message)
                    
            except Exception as e:
                break
    
    def process_message(self, message):
        """Process a message from server."""
        if message == "LOBBY_READY":
            with self.lock:
                self.in_lobby = True
                self.in_game = False
                
        elif message.startswith("LOBBY_STATE,"):
            parts = message.split(",", 3)
            with self.lock:
                self.lobby_state.players_connected[0] = parts[1] == "1"
                self.lobby_state.players_connected[1] = parts[2] == "1"
                if len(parts) > 3:
                    self.lobby_state.chat_history = LobbyState.deserialize_chat(parts[3])
                    
        elif message == "GAME_START":
            with self.lock:
                self.in_lobby = False
                self.in_game = True
                self.game_state.reset()
                
        elif message.startswith("STATE,"):
            new_state = GameState.deserialize(message)
            if new_state:
                with self.lock:
                    self.game_state = new_state
                    
        elif message.startswith("GAMEOVER,"):
            winner = int(message.split(',')[1])
            with self.lock:
                self.game_state.running = False
                self.game_state.winner = winner
                self.in_game = False
                
        elif message == "RETURN_LOBBY":
            with self.lock:
                self.in_lobby = True
                self.in_game = False
    
    def send_message(self, message):
        """Send message to server."""
        try:
            self.socket.send((message + "\n").encode())
        except:
            pass
    
    def run(self):
        """Main client loop."""
        self.input_handler = InputHandler()
        self.input_handler.start()
        
        receiver = threading.Thread(target=self.receive_updates)
        receiver.daemon = True
        receiver.start()
        
        try:
            while self.running:
                with self.lock:
                    in_lobby = self.in_lobby
                    in_game = self.in_game
                
                if in_lobby:
                    self.run_lobby()
                elif in_game:
                    self.run_game()
                else:
                    time.sleep(0.1)
        finally:
            self.input_handler.stop()
    
    def run_lobby(self):
        """Run lobby loop with chat."""
        self.input_handler.set_mode("line")
        last_render = 0
        
        while self.running:
            with self.lock:
                if not self.in_lobby:
                    break
                lobby_copy = LobbyState()
                lobby_copy.chat_history = self.lobby_state.chat_history.copy()
                lobby_copy.players_connected = self.lobby_state.players_connected.copy()
            
            # Check for completed chat message
            line = self.input_handler.get_line()
            if line:
                if line.upper() == 'Q':
                    self.running = False
                    break
                elif line.upper() == 'S' and self.player_id == 1:
                    self.send_message("START_GAME")
                elif line.strip():
                    self.send_message(f"CHAT,{line}")
            
            # Also check for single key commands
            key = self.input_handler.get_key()
            if key == 'Q':
                self.running = False
                break
            elif key == 'S' and self.player_id == 1:
                self.send_message("START_GAME")
            
            # Render lobby
            now = time.time()
            if now - last_render >= 0.1:
                partial = self.input_handler.get_partial_line()
                render_lobby(lobby_copy, self.player_id, partial)
                last_render = now
            
            time.sleep(0.05)
    
    def run_game(self):
        """Run game loop."""
        self.input_handler.set_mode("key")
        last_render = 0
        
        while self.running:
            with self.lock:
                if not self.in_game:
                    break
                state_copy = GameState()
                state_copy.ball_x = self.game_state.ball_x
                state_copy.ball_y = self.game_state.ball_y
                state_copy.paddle1_y = self.game_state.paddle1_y
                state_copy.paddle2_y = self.game_state.paddle2_y
                state_copy.score1 = self.game_state.score1
                state_copy.score2 = self.game_state.score2
                state_copy.running = self.game_state.running
                state_copy.winner = self.game_state.winner
            
            # Handle input
            key = self.input_handler.get_key()
            if key == 'Q':
                self.running = False
                break
            elif key in ['W', 'S']:
                self.send_message(f"INPUT,{key}")
            
            # Render
            now = time.time()
            if now - last_render >= FRAME_TIME:
                if state_copy.running:
                    render_game(state_copy, self.player_id)
                else:
                    show_game_over(state_copy.winner, self.player_id)
                last_render = now
            
            time.sleep(0.01)
    
    def close(self):
        """Close connection."""
        self.running = False
        if self.input_handler:
            self.input_handler.stop()
        try:
            self.socket.close()
        except:
            pass


# ============================================================================
# MAIN MENU & ENTRY POINT
# ============================================================================

def show_menu():
    """Display main menu."""
    clear_screen()
    print("""
+==============================================================+
|                                                              |
|              TERMINAL PONG                                   |
|              CLI-Based Multiplayer Game                      |
|              with Chat Lobby                                 |
|                                                              |
+==============================================================+
|                                                              |
|                    [1] Host Game (Server)                    |
|                    [2] Join Game (Client)                    |
|                    [Q] Quit                                  |
|                                                              |
+==============================================================+
    """)


def host_game():
    """Start as host."""
    clear_screen()
    print("\n[HOST MODE] Starting server...")
    
    server = GameServer()
    local_ip = server.start()
    
    time.sleep(0.5)
    client = GameClient()
    if client.connect("127.0.0.1"):
        client.run()
        client.close()
    
    server.stop()
    restore_terminal()


def join_game():
    """Join as guest."""
    clear_screen()
    print("\n[JOIN MODE]")
    
    host_ip = input("Enter Host IP Address: ").strip()
    if not host_ip:
        print("Invalid IP address!")
        time.sleep(2)
        return
    
    client = GameClient()
    if client.connect(host_ip):
        client.run()
        client.close()
    else:
        time.sleep(2)
    
    restore_terminal()


def main():
    """Main entry point."""
    while True:
        show_menu()
        choice = input("\n  Select option: ").strip().upper()
        
        if choice == '1':
            host_game()
        elif choice == '2':
            join_game()
        elif choice == 'Q':
            clear_screen()
            print("\nThank you for playing Terminal Pong!\n")
            break
        else:
            print("Invalid option!")
            time.sleep(1)


if __name__ == "__main__":
    main()
