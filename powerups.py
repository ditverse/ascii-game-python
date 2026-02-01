"""
Power-ups Module
Game modifiers that spawn on the field and affect gameplay.
"""

import random
import time
from config import GAME_WIDTH, GAME_HEIGHT


class PowerUp:
    """Base class for power-ups."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.collected = False
        self.effect_duration = 5.0  # seconds
        self.effect_start_time = None
        self.symbol = '?'
        self.name = 'Unknown'
    
    def apply(self, state, player_id):
        """Apply power-up effect to game state."""
        self.collected = True
        self.active = False
        self.effect_start_time = time.time()
    
    def is_effect_expired(self):
        """Check if power-up effect has expired."""
        if self.effect_start_time is None:
            return False
        return time.time() - self.effect_start_time >= self.effect_duration
    
    def remove_effect(self, state):
        """Remove power-up effect from game state."""
        pass


class SpeedBoost(PowerUp):
    """Increases ball speed temporarily."""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = '⚡'
        self.name = 'Speed Boost'
        self.speed_multiplier = 1.5
    
    def apply(self, state, player_id):
        super().apply(state, player_id)
        state.ball_vx *= self.speed_multiplier
        state.ball_vy *= self.speed_multiplier
    
    def remove_effect(self, state):
        state.ball_vx /= self.speed_multiplier
        state.ball_vy /= self.speed_multiplier


class PaddleGrow(PowerUp):
    """Increases player's paddle size."""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = '↕'
        self.name = 'Paddle Grow'
        self.size_increase = 2
        self.affected_player = None
    
    def apply(self, state, player_id):
        super().apply(state, player_id)
        self.affected_player = player_id
        if player_id == 1:
            state.paddle1_height = getattr(state, 'paddle1_height', 4) + self.size_increase
        else:
            state.paddle2_height = getattr(state, 'paddle2_height', 4) + self.size_increase
    
    def remove_effect(self, state):
        if self.affected_player == 1:
            state.paddle1_height = max(4, getattr(state, 'paddle1_height', 4) - self.size_increase)
        else:
            state.paddle2_height = max(4, getattr(state, 'paddle2_height', 4) - self.size_increase)


class PaddleShrink(PowerUp):
    """Shrinks opponent's paddle size."""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = '↔'
        self.name = 'Paddle Shrink'
        self.size_decrease = 2
        self.affected_player = None
    
    def apply(self, state, player_id):
        super().apply(state, player_id)
        # Shrink opponent's paddle
        opponent = 2 if player_id == 1 else 1
        self.affected_player = opponent
        if opponent == 1:
            state.paddle1_height = max(2, getattr(state, 'paddle1_height', 4) - self.size_decrease)
        else:
            state.paddle2_height = max(2, getattr(state, 'paddle2_height', 4) - self.size_decrease)
    
    def remove_effect(self, state):
        if self.affected_player == 1:
            state.paddle1_height = getattr(state, 'paddle1_height', 4) + self.size_decrease
        else:
            state.paddle2_height = getattr(state, 'paddle2_height', 4) + self.size_decrease


class PowerUpManager:
    """Manages power-up spawning and effects."""
    
    POWER_UP_TYPES = [SpeedBoost, PaddleGrow, PaddleShrink]
    
    def __init__(self):
        self.active_powerups = []      # PowerUps on field (not collected)
        self.active_effects = []       # Applied effects with timers
        self.last_spawn_time = 0
        self.spawn_interval = 10.0     # Spawn every 10 seconds
        self.enabled = True
    
    def update(self, state, current_time):
        """Update power-ups: spawn new ones, check collections, expire effects."""
        if not self.enabled:
            return
        
        # Spawn new power-up
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self._spawn_powerup()
            self.last_spawn_time = current_time
        
        # Check for power-up collection (ball collision)
        ball_x = int(state.ball_x)
        ball_y = int(state.ball_y)
        
        for powerup in self.active_powerups[:]:
            if abs(powerup.x - ball_x) <= 1 and abs(powerup.y - ball_y) <= 1:
                # Determine which player collected (based on ball direction)
                player_id = 1 if state.ball_vx > 0 else 2
                powerup.apply(state, player_id)
                self.active_powerups.remove(powerup)
                self.active_effects.append(powerup)
        
        # Expire old effects
        for effect in self.active_effects[:]:
            if effect.is_effect_expired():
                effect.remove_effect(state)
                self.active_effects.remove(effect)
    
    def _spawn_powerup(self):
        """Spawn a random power-up on the field."""
        if len(self.active_powerups) >= 2:  # Max 2 power-ups on field
            return
        
        # Random position (avoid edges and paddles)
        x = random.randint(GAME_WIDTH // 4, 3 * GAME_WIDTH // 4)
        y = random.randint(2, GAME_HEIGHT - 3)
        
        # Random power-up type
        PowerUpClass = random.choice(self.POWER_UP_TYPES)
        powerup = PowerUpClass(x, y)
        self.active_powerups.append(powerup)
    
    def get_field_powerups(self):
        """Get list of power-ups currently on field for rendering."""
        return self.active_powerups
    
    def get_active_effects(self):
        """Get list of currently active effects."""
        return self.active_effects
    
    def reset(self):
        """Reset all power-ups."""
        self.active_powerups = []
        self.active_effects = []
        self.last_spawn_time = 0
