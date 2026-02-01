import random
from config import (
    GAME_WIDTH, GAME_HEIGHT, PADDLE_HEIGHT,
    BALL_SPEED_X, BALL_SPEED_Y, MAX_CHAT_HISTORY
)


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
        self.paddle1_height = PADDLE_HEIGHT  # Dynamic paddle height
        self.paddle2_height = PADDLE_HEIGHT  # Dynamic paddle height
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


class LobbyState:
    """Holds lobby and chat data."""
    
    def __init__(self):
        self.chat_history = []  # List of (player_id, message)
        self.players_connected = [False, False]  # Player 1, Player 2
        # Last game result
        self.last_winner = None
        self.last_score1 = 0
        self.last_score2 = 0
    
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
