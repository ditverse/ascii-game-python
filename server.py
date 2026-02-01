"""
Game Server Module
TCP Server that manages lobby and game with logging support.
"""

import socket
import threading
import time
import logging

from config import PORT, BUFFER_SIZE, FRAME_TIME, LOG_LEVEL, LOG_FORMAT
from game_state import GameState, LobbyState
from physics import update_physics, move_paddle

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


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
        self.server_socket = None
    
    def get_local_ip(self):
        """Get the local LAN IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.debug(f"Could not detect LAN IP: {e}")
            return "127.0.0.1"
    
    def start(self):
        """Start the game server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', PORT))
            self.server_socket.listen(2)
            
            local_ip = self.get_local_ip()
            logger.info(f"Server started on {local_ip}:{PORT}")
            
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            return local_ip
            
        except OSError as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    def accept_connections(self):
        """Accept incoming client connections."""
        player_id = 1
        while self.running and player_id <= 2:
            try:
                self.server_socket.settimeout(1.0)  # Allow periodic check
                try:
                    client_socket, addr = self.server_socket.accept()
                except socket.timeout:
                    continue
                    
                with self.lock:
                    self.clients[client_socket] = player_id
                    self.client_sockets.append(client_socket)
                    self.lobby_state.players_connected[player_id - 1] = True
                
                logger.info(f"Player {player_id} connected from {addr[0]}:{addr[1]}")
                
                try:
                    client_socket.send(f"PLAYER,{player_id}".encode())
                except Exception as e:
                    logger.error(f"Failed to send player ID: {e}")
                    continue
                
                handler = threading.Thread(target=self.handle_client, args=(client_socket, player_id))
                handler.daemon = True
                handler.start()
                
                player_id += 1
                
                if player_id > 2:
                    logger.info("All players connected! Entering lobby...")
                    self.broadcast("LOBBY_READY")
                    self.broadcast_lobby_state()
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Accept error: {e}")
    
    def handle_client(self, client_socket, player_id):
        """Handle messages from a client."""
        buffer = ""
        while self.running:
            try:
                client_socket.settimeout(0.5)
                try:
                    data = client_socket.recv(BUFFER_SIZE).decode()
                except socket.timeout:
                    continue
                    
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message:
                        self.process_message(message, player_id)
                            
            except ConnectionResetError:
                logger.warning(f"Player {player_id} connection reset")
                break
            except Exception as e:
                if self.running:
                    logger.debug(f"Client {player_id} error: {e}")
                break
        
        logger.info(f"Player {player_id} disconnected")
        with self.lock:
            self.lobby_state.players_connected[player_id - 1] = False
            if client_socket in self.client_sockets:
                self.client_sockets.remove(client_socket)
        
        try:
            client_socket.close()
        except:
            pass
    
    def process_message(self, message, player_id):
        """Process a single message from client."""
        logger.debug(f"P{player_id}: {message}")
        
        if message.startswith("CHAT,"):
            chat_msg = message[5:]
            with self.lock:
                self.lobby_state.add_message(player_id, chat_msg)
            self.broadcast_lobby_state()
            
        elif message.startswith("INPUT,"):
            parts = message.split(',')
            if len(parts) >= 2:
                direction = parts[1]
                with self.lock:
                    if direction in ['W', 'S']:
                        move_paddle(self.game_state, player_id, direction)
                    
        elif message == "START_GAME" and player_id == 1:
            if not self.game_running:
                game_thread = threading.Thread(target=self.start_game)
                game_thread.daemon = True
                game_thread.start()
    
    def broadcast(self, message):
        """Send message to all clients."""
        disconnected = []
        for client_socket in self.client_sockets:
            try:
                client_socket.send((message + "\n").encode())
            except Exception as e:
                logger.debug(f"Broadcast failed to client: {e}")
                disconnected.append(client_socket)
        
        # Remove disconnected clients
        for client in disconnected:
            if client in self.client_sockets:
                self.client_sockets.remove(client)
    
    def broadcast_lobby_state(self):
        """Send lobby state to all clients."""
        with self.lock:
            chat_data = self.lobby_state.serialize_chat()
            p1 = "1" if self.lobby_state.players_connected[0] else "0"
            p2 = "1" if self.lobby_state.players_connected[1] else "0"
            lw = self.lobby_state.last_winner if self.lobby_state.last_winner else 0
            ls1 = self.lobby_state.last_score1
            ls2 = self.lobby_state.last_score2
        self.broadcast(f"LOBBY_STATE,{p1},{p2},{lw},{ls1},{ls2},{chat_data}")
    
    def start_game(self):
        """Start the game from lobby."""
        logger.info("Starting game...")
        
        with self.lock:
            self.in_lobby = False
            self.game_running = True
            self.game_state.reset()
        
        self.broadcast("GAME_START")
        time.sleep(0.5)
        
        self.run_game_loop()
        
        # Save game result to lobby state
        with self.lock:
            self.lobby_state.last_winner = self.game_state.winner
            self.lobby_state.last_score1 = self.game_state.score1
            self.lobby_state.last_score2 = self.game_state.score2
            self.in_lobby = True
            self.game_running = False
        
        logger.info(f"Game ended. Winner: Player {self.game_state.winner}")
        
        time.sleep(3)
        self.broadcast("RETURN_LOBBY")
        self.broadcast_lobby_state()
    
    def run_game_loop(self):
        """Main game physics loop."""
        logger.debug("Game loop started")
        
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
        
        logger.debug("Game loop ended")
    
    def stop(self):
        """Stop the server gracefully."""
        logger.info("Stopping server...")
        self.running = False
        
        # Close all client connections
        for client_socket in self.client_sockets:
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Server stopped")
