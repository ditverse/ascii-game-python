"""
Game Client Module
TCP Client for connecting to game server with logging and error handling.
"""

import socket
import threading
import time
import logging

from config import PORT, BUFFER_SIZE, FRAME_TIME, LOG_LEVEL, LOG_FORMAT
from game_state import GameState, LobbyState
from input_handler import InputHandler
from renderer import render_lobby, render_game, show_game_over

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


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
        self.connected = False
    
    def connect(self, host_ip, timeout=10):
        """
        Connect to game server.
        
        Args:
            host_ip: Server IP address
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if connected successfully
        """
        logger.info(f"Connecting to {host_ip}:{PORT}...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((host_ip, PORT))
            self.socket.settimeout(None)
            
            # Wait for player assignment
            data = self.socket.recv(BUFFER_SIZE).decode()
            if data.startswith("PLAYER,"):
                self.player_id = int(data.split(',')[1])
                logger.info(f"Connected as Player {self.player_id}")
                self.connected = True
                return True
            else:
                logger.error(f"Unexpected server response: {data}")
                return False
            
        except socket.timeout:
            logger.error("Connection timeout - server not responding")
            return False
        except ConnectionRefusedError:
            logger.error("Connection refused - is the server running?")
            return False
        except OSError as e:
            logger.error(f"Network error: {e}")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def receive_updates(self):
        """Receive updates from server in background thread."""
        buffer = ""
        while self.running and self.connected:
            try:
                self.socket.settimeout(0.5)
                try:
                    data = self.socket.recv(BUFFER_SIZE).decode()
                except socket.timeout:
                    continue
                    
                if not data:
                    logger.warning("Server disconnected")
                    self.connected = False
                    break
                
                buffer += data
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    if message:
                        self.process_message(message)
                    
            except ConnectionResetError:
                logger.warning("Connection reset by server")
                self.connected = False
                break
            except Exception as e:
                if self.running:
                    logger.debug(f"Receive error: {e}")
                break
        
        logger.debug("Receiver thread ended")
    
    def process_message(self, message):
        """Process a message from server."""
        logger.debug(f"Received: {message[:50]}...")
        
        if message == "LOBBY_READY":
            with self.lock:
                self.in_lobby = True
                self.in_game = False
                logger.info("Entered lobby")
                
        elif message.startswith("LOBBY_STATE,"):
            parts = message.split(",", 6)
            with self.lock:
                self.lobby_state.players_connected[0] = parts[1] == "1"
                self.lobby_state.players_connected[1] = parts[2] == "1"
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
                logger.info("Game started")
                
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
                logger.info(f"Game over - Player {winner} wins")
                
        elif message == "RETURN_LOBBY":
            with self.lock:
                self.in_lobby = True
                self.in_game = False
                logger.info("Returned to lobby")
    
    def send_message(self, message):
        """Send message to server with error handling."""
        if not self.connected:
            return False
            
        try:
            self.socket.send((message + "\n").encode())
            return True
        except Exception as e:
            logger.debug(f"Send error: {e}")
            self.connected = False
            return False
    
    def run(self):
        """Main client loop."""
        self.input_handler = InputHandler()
        self.input_handler.start()
        
        receiver = threading.Thread(target=self.receive_updates)
        receiver.daemon = True
        receiver.start()
        
        try:
            while self.running and self.connected:
                with self.lock:
                    in_lobby = self.in_lobby
                    in_game = self.in_game
                
                if in_lobby:
                    self.run_lobby()
                elif in_game:
                    self.run_game()
                else:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.input_handler.stop()
    
    def run_lobby(self):
        """Run lobby loop with chat."""
        self.input_handler.set_mode("line")
        last_render = 0
        
        while self.running and self.connected:
            with self.lock:
                if not self.in_lobby:
                    break
                lobby_copy = LobbyState()
                lobby_copy.chat_history = self.lobby_state.chat_history.copy()
                lobby_copy.players_connected = self.lobby_state.players_connected.copy()
                lobby_copy.last_winner = self.lobby_state.last_winner
                lobby_copy.last_score1 = self.lobby_state.last_score1
                lobby_copy.last_score2 = self.lobby_state.last_score2
            
            # Check for completed line input
            line = self.input_handler.get_line()
            if line:
                if line.upper() == 'Q':
                    self.running = False
                    break
                elif line.strip():
                    self.send_message(f"CHAT,{line}")
            
            # Check for single key input
            key = self.input_handler.get_key()
            if key == 'Q':
                self.running = False
                break
            elif key == '\t' and self.player_id == 1:  # TAB key
                self.send_message("START_GAME")
            
            # Render at fixed rate
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
        
        while self.running and self.connected:
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
        """Close connection gracefully."""
        logger.info("Closing connection...")
        self.running = False
        self.connected = False
        
        if self.input_handler:
            self.input_handler.stop()
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        logger.info("Connection closed")
