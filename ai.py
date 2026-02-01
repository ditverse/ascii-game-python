"""
AI Controller Module
Simple AI opponent for single-player Pong.
"""

import random
from config import GAME_HEIGHT, PADDLE_HEIGHT


class AIController:
    """AI controller for paddle movement with difficulty levels."""
    
    # Difficulty settings: (reaction_delay, accuracy, prediction_error)
    DIFFICULTY_SETTINGS = {
        'easy': {
            'reaction_chance': 0.15,   # 15% chance - Very stupid
            'prediction_error': 10,    # Huge error margin
            'move_speed': 1,
        },
        'medium': {
            'reaction_chance': 0.35,   # 35% chance - Stupid but playable
            'prediction_error': 5,     # Large error margin
            'move_speed': 1,
        },
        'hard': {
            'reaction_chance': 0.90,   # 90% chance - Competitive
            'prediction_error': 1,     # Low error
            'move_speed': 1,
        }
    }
    
    def __init__(self, difficulty='medium'):
        """Initialize AI with specified difficulty."""
        self.difficulty = difficulty
        self.settings = self.DIFFICULTY_SETTINGS.get(difficulty, self.DIFFICULTY_SETTINGS['medium'])
        self.target_y = GAME_HEIGHT // 2
    
    def update(self, state):
        """
        Calculate AI move based on ball position.
        Returns 'W' (up), 'S' (down), or None (no move).
        """
        # Check if AI should react this frame
        if random.random() > self.settings['reaction_chance']:
            return None
        
        # Predict where ball will be
        ball_y = state.ball_y
        ball_vy = state.ball_vy
        ball_x = state.ball_x
        ball_vx = state.ball_vx
        
        # Only track ball when it's coming towards AI (right side)
        if ball_vx > 0:
            # Simple prediction: where will ball be when it reaches paddle
            from config import GAME_WIDTH
            paddle_x = GAME_WIDTH - 3
            
            if ball_vx != 0:
                time_to_reach = (paddle_x - ball_x) / ball_vx
                predicted_y = ball_y + (ball_vy * time_to_reach)
                
                # Handle bounces (simplified)
                while predicted_y < 0 or predicted_y >= GAME_HEIGHT:
                    if predicted_y < 0:
                        predicted_y = -predicted_y
                    elif predicted_y >= GAME_HEIGHT:
                        predicted_y = 2 * (GAME_HEIGHT - 1) - predicted_y
                
                # Add prediction error based on difficulty
                error = random.uniform(-self.settings['prediction_error'], 
                                       self.settings['prediction_error'])
                self.target_y = predicted_y + error
        else:
            # Ball going away, move to center
            self.target_y = GAME_HEIGHT // 2
        
        # Move paddle towards target
        paddle_center = state.paddle2_y + PADDLE_HEIGHT // 2
        
        if paddle_center < self.target_y - 1:
            return 'S'  # Move down
        elif paddle_center > self.target_y + 1:
            return 'W'  # Move up
        
        return None  # Stay in position
    
    def set_difficulty(self, difficulty):
        """Change AI difficulty."""
        self.difficulty = difficulty
        self.settings = self.DIFFICULTY_SETTINGS.get(difficulty, self.DIFFICULTY_SETTINGS['medium'])
