import socket
import threading
import time

from config import PORT, BUFFER_SIZE, FRAME_TIME
from game_state import GameState, LobbyState
from physics import update_physics, move_paddle


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
            # Include last game result
            lw = self.lobby_state.last_winner if self.lobby_state.last_winner else 0
            ls1 = self.lobby_state.last_score1
            ls2 = self.lobby_state.last_score2
        self.broadcast(f"LOBBY_STATE,{p1},{p2},{lw},{ls1},{ls2},{chat_data}")
    
    def start_game(self):
        """Start the game from lobby."""
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
