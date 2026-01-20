import socket
import threading
import time

from config import PORT, BUFFER_SIZE, FRAME_TIME
from game_state import GameState, LobbyState
from input_handler import InputHandler
from renderer import render_lobby, render_game, show_game_over


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
            parts = message.split(",", 6)
            with self.lock:
                self.lobby_state.players_connected[0] = parts[1] == "1"
                self.lobby_state.players_connected[1] = parts[2] == "1"
                # Parse game result
                lw = int(parts[3]) if len(parts) > 3 else 0
                self.lobby_state.last_winner = lw if lw > 0 else None
                self.lobby_state.last_score1 = int(parts[4]) if len(parts) > 4 else 0
                self.lobby_state.last_score2 = int(parts[5]) if len(parts) > 5 else 0
                if len(parts) > 6:
                    self.lobby_state.chat_history = LobbyState.deserialize_chat(parts[6])
                    
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
                lobby_copy.last_winner = self.lobby_state.last_winner
                lobby_copy.last_score1 = self.lobby_state.last_score1
                lobby_copy.last_score2 = self.lobby_state.last_score2
            
            line = self.input_handler.get_line()
            if line:
                if line.upper() == 'Q':
                    self.running = False
                    break
                elif line.strip():
                    self.send_message(f"CHAT,{line}")
            
            key = self.input_handler.get_key()
            if key == 'Q':
                self.running = False
                break
            elif key == '\t' and self.player_id == 1:  # TAB key
                self.send_message("START_GAME")
            
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
            
            key = self.input_handler.get_key()
            if key == 'Q':
                self.running = False
                break
            elif key in ['W', 'S']:
                self.send_message(f"INPUT,{key}")
            
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
