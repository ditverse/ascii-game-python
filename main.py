#!/usr/bin/env python3
"""
Terminal Pong - CLI-Based Multiplayer Game
Network Programming Final Project

A real-time multiplayer Pong game running entirely in CLI/Terminal using ASCII graphics.
Uses Host-Client architecture over TCP sockets.
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
BUFFER_SIZE = 1024

# Ball speed
BALL_SPEED_X = 1.5
BALL_SPEED_Y = 1.0

# ============================================================================
# CROSS-PLATFORM INPUT HANDLING
# ============================================================================

class InputHandler:
    """Thread-safe input handler for cross-platform keyboard input."""
    
    def __init__(self):
        self.current_key = None
        self.lock = threading.Lock()
        self.running = True
        self._old_settings = None
        self._thread = None
        
    def start(self):
        """Start the input handler thread."""
        if os.name != 'nt':
            # Save terminal settings on Linux
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
    
    def get_key(self):
        """Get the current key (thread-safe)."""
        with self.lock:
            key = self.current_key
            self.current_key = None
            return key
    
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
                        key_char = key.decode('utf-8').upper()
                        with self.lock:
                            self.current_key = key_char
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
            tty.setcbreak(fd)  # Use cbreak mode instead of raw for better compatibility
            while self.running:
                try:
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        key = sys.stdin.read(1).upper()
                        with self.lock:
                            self.current_key = key
                except:
                    break
        finally:
            if self._old_settings:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
                except:
                    pass


def clear_screen():
    """Clear the terminal screen."""
    # Use ANSI escape codes for faster clearing (avoids subprocess)
    print("\033[H\033[J", end="", flush=True)


# ============================================================================
# GAME STATE
# ============================================================================

class GameState:
    """Holds all game state data."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset game to initial state."""
        # Ball position (center)
        self.ball_x = GAME_WIDTH // 2
        self.ball_y = GAME_HEIGHT // 2
        
        # Ball velocity (random direction)
        self.ball_vx = BALL_SPEED_X * random.choice([-1, 1])
        self.ball_vy = BALL_SPEED_Y * random.choice([-1, 1])
        
        # Paddle positions (center vertically)
        self.paddle1_y = GAME_HEIGHT // 2 - PADDLE_HEIGHT // 2  # Left paddle (Player 1)
        self.paddle2_y = GAME_HEIGHT // 2 - PADDLE_HEIGHT // 2  # Right paddle (Player 2)
        
        # Scores
        self.score1 = 0
        self.score2 = 0
        
        # Game status
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
# ASCII RENDERER
# ============================================================================

def render_game(state, player_id):
    """Render the game state as ASCII art."""
    clear_screen()
    
    # Create empty game field
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
    
    # Build display string
    top_border = '+' + '-' * GAME_WIDTH + '+'
    
    # Score display
    player_label = f"YOU (Player {player_id})"
    opponent_label = f"Opponent (Player {2 if player_id == 1 else 1})"
    
    if player_id == 1:
        score_line = f"  {player_label}: {state.score1}  |  {opponent_label}: {state.score2}"
    else:
        score_line = f"  {opponent_label}: {state.score1}  |  {player_label}: {state.score2}"
    
    print("\n" + "=" * (GAME_WIDTH + 2))
    print("        TERMINAL PONG - Network Programming Project")
    print("=" * (GAME_WIDTH + 2))
    print(score_line)
    print(top_border)
    
    for row in field:
        print('|' + ''.join(row) + '|')
    
    print(top_border)
    print("  Controls: W = Up, S = Down, Q = Quit")
    print("=" * (GAME_WIDTH + 2))


def show_game_over(winner, player_id):
    """Display game over screen."""
    clear_screen()
    print("\n" + "=" * 40)
    print("           GAME OVER!")
    print("=" * 40)
    
    if winner == player_id:
        print("\n      🎉 CONGRATULATIONS! YOU WIN! 🎉")
    else:
        print("\n         ❌ YOU LOSE! Better luck next time!")
    
    print("\n" + "=" * 40)
    print("  Press any key to return to menu...")


# ============================================================================
# GAME PHYSICS (Server-side)
# ============================================================================

def update_physics(state):
    """Update ball position and handle collisions."""
    # Move ball
    state.ball_x += state.ball_vx
    state.ball_y += state.ball_vy
    
    # Top/Bottom wall collision
    if state.ball_y <= 0 or state.ball_y >= GAME_HEIGHT - 1:
        state.ball_vy = -state.ball_vy
        state.ball_y = max(0, min(GAME_HEIGHT - 1, state.ball_y))
    
    # Left paddle collision (Player 1)
    paddle1_x = 2
    if state.ball_x <= paddle1_x + 1 and state.ball_vx < 0:
        if state.paddle1_y <= state.ball_y <= state.paddle1_y + PADDLE_HEIGHT:
            state.ball_vx = -state.ball_vx
            state.ball_x = paddle1_x + 1
    
    # Right paddle collision (Player 2)
    paddle2_x = GAME_WIDTH - 3
    if state.ball_x >= paddle2_x - 1 and state.ball_vx > 0:
        if state.paddle2_y <= state.ball_y <= state.paddle2_y + PADDLE_HEIGHT:
            state.ball_vx = -state.ball_vx
            state.ball_x = paddle2_x - 1
    
    # Scoring
    if state.ball_x <= 0:
        state.score2 += 1
        reset_ball(state, direction=1)
    elif state.ball_x >= GAME_WIDTH - 1:
        state.score1 += 1
        reset_ball(state, direction=-1)
    
    # Check win condition
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
# SERVER (Host Mode)
# ============================================================================

class GameServer:
    """TCP Server that manages game state and clients."""
    
    def __init__(self):
        self.state = GameState()
        self.clients = {}  # {socket: player_id}
        self.client_sockets = []
        self.lock = threading.Lock()
        self.running = True
        self.game_started = False
    
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
        print(f"\n[SERVER] Game server started!")
        print(f"[SERVER] Your IP Address: {local_ip}")
        print(f"[SERVER] Port: {PORT}")
        print(f"[SERVER] Waiting for players to connect...")
        
        # Accept connections in a thread
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
                
                print(f"[SERVER] Player {player_id} connected from {addr}")
                
                # Send player ID to client
                client_socket.send(f"PLAYER,{player_id}".encode())
                
                # Start handler thread
                handler = threading.Thread(target=self.handle_client, args=(client_socket, player_id))
                handler.daemon = True
                handler.start()
                
                player_id += 1
                
                if player_id > 2:
                    self.game_started = True
                    print("[SERVER] All players connected! Starting game...")
                    self.broadcast("START")
                    time.sleep(0.5)
                    
            except Exception as e:
                if self.running:
                    print(f"[SERVER] Accept error: {e}")
    
    def handle_client(self, client_socket, player_id):
        """Handle input from a client."""
        while self.running:
            try:
                data = client_socket.recv(BUFFER_SIZE).decode()
                if not data:
                    break
                
                if data.startswith("INPUT,"):
                    direction = data.split(',')[1]
                    with self.lock:
                        if direction in ['W', 'S']:
                            move_paddle(self.state, player_id, direction)
                            
            except Exception as e:
                break
        
        print(f"[SERVER] Player {player_id} disconnected")
    
    def broadcast(self, message):
        """Send message to all connected clients."""
        for client_socket in self.client_sockets:
            try:
                client_socket.send(message.encode())
            except:
                pass
    
    def run_game_loop(self):
        """Main game physics loop."""
        # Wait for all players
        while not self.game_started and self.running:
            time.sleep(0.1)
        
        while self.state.running and self.running:
            start_time = time.time()
            
            with self.lock:
                update_physics(self.state)
                state_data = self.state.serialize()
            
            self.broadcast(state_data)
            
            # Check for game over
            if not self.state.running:
                self.broadcast(f"GAMEOVER,{self.state.winner}")
                break
            
            # Frame timing
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
        self.state = GameState()
        self.running = True
        self.game_started = False
        self.lock = threading.Lock()
        self.input_handler = None
    
    def connect(self, host_ip):
        """Connect to game server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host_ip, PORT))
            self.socket.settimeout(None)
            
            # Receive player ID
            data = self.socket.recv(BUFFER_SIZE).decode()
            if data.startswith("PLAYER,"):
                self.player_id = int(data.split(',')[1])
                print(f"\n[CLIENT] Connected as Player {self.player_id}")
                print("[CLIENT] Waiting for opponent...")
                return True
            return False
            
        except socket.timeout:
            print("[CLIENT] Connection timeout! Is the host running?")
            return False
        except ConnectionRefusedError:
            print("[CLIENT] Connection refused! Check host IP and ensure host is running.")
            return False
        except Exception as e:
            print(f"[CLIENT] Connection error: {e}")
            return False
    
    def receive_updates(self):
        """Receive state updates from server."""
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode()
                if not data:
                    break
                
                if data == "START":
                    self.game_started = True
                elif data.startswith("STATE,"):
                    new_state = GameState.deserialize(data)
                    if new_state:
                        with self.lock:
                            self.state = new_state
                elif data.startswith("GAMEOVER,"):
                    winner = int(data.split(',')[1])
                    self.state.running = False
                    self.state.winner = winner
                    break
                    
            except Exception as e:
                break
    
    def send_input(self, key):
        """Send input to server."""
        try:
            self.socket.send(f"INPUT,{key}".encode())
        except:
            pass
    
    def run(self):
        """Main client loop."""
        # Start input handler
        self.input_handler = InputHandler()
        self.input_handler.start()
        
        # Start receiver thread
        receiver = threading.Thread(target=self.receive_updates)
        receiver.daemon = True
        receiver.start()
        
        # Wait for game to start
        while not self.game_started and self.running:
            time.sleep(0.1)
        
        if not self.running:
            self.input_handler.stop()
            return
        
        # Game loop with input and rendering
        last_render = 0
        try:
            while self.state.running and self.running:
                # Handle input
                key = self.input_handler.get_key()
                if key == 'Q':
                    self.running = False
                    break
                elif key in ['W', 'S']:
                    self.send_input(key)
                
                # Render at target FPS
                now = time.time()
                if now - last_render >= FRAME_TIME:
                    with self.lock:
                        render_game(self.state, self.player_id)
                    last_render = now
                
                time.sleep(0.01)
        finally:
            self.input_handler.stop()
        
        # Game over
        if self.state.winner:
            show_game_over(self.state.winner, self.player_id)
            time.sleep(2)
    
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
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ████████ █████ ██████ ██   ██  ██████           ║
║              ██      ██   ██ ██   ██ ███  ██ ██              ║
║              ████████ ██   ██ ██   ██ ██ ██ ██ ██  ███       ║
║              ██      ██   ██ ██   ██ ██  ███ ██    ██        ║
║              ██       █████  ██   ██ ██   ██  ██████         ║
║                                                              ║
║              ═══════════════════════════════════             ║
║              CLI-Based Multiplayer Pong Game                 ║
║              Network Programming Final Project               ║
║              ═══════════════════════════════════             ║
║                                                              ║
║                    [1] Host Game (Server)                    ║
║                    [2] Join Game (Client)                    ║
║                    [Q] Quit                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def host_game():
    """Start as host (server + player 1)."""
    clear_screen()
    print("\n[HOST MODE] Starting server...")
    
    server = GameServer()
    local_ip = server.start()
    
    # Start game loop in background
    game_thread = threading.Thread(target=server.run_game_loop)
    game_thread.daemon = True
    game_thread.start()
    
    # Connect local client
    time.sleep(0.5)
    client = GameClient()
    if client.connect("127.0.0.1"):
        client.run()
        client.close()
    
    server.stop()


def join_game():
    """Join as guest (client / player 2)."""
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
            print("\nThank you for playing Terminal Pong!")
            print("Network Programming Final Project\n")
            break
        else:
            print("Invalid option! Please try again.")
            time.sleep(1)


if __name__ == "__main__":
    main()
