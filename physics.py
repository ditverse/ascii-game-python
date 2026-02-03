"""
Physics Module
Ball and paddle physics with collision detection.
Includes event callbacks for sound and visual effects.
"""

import random
from config import (
    GAME_WIDTH, GAME_HEIGHT, PADDLE_HEIGHT, WIN_SCORE,
    BALL_SPEED_X, BALL_SPEED_Y
)


class PhysicsEvents:
    """Container for physics events that occurred during update."""
    
    def __init__(self):
        self.wall_bounce = False
        self.paddle1_hit = False
        self.paddle2_hit = False
        self.goal_scored = None  # 1 or 2 (which player scored)
        self.goal_position = None  # (x, y) where ball crossed
        self.paddle_hit_position = None  # (x, y, height) of paddle hit


def update_physics(state, return_events=False):
    """
    Update ball position and handle collisions.
    
    Args:
        state: GameState object
        return_events: If True, return PhysicsEvents object
        
    Returns:
        PhysicsEvents if return_events=True, else None
    """
    events = PhysicsEvents() if return_events else None
    
    # Store previous position for collision detection
    prev_x = state.ball_x
    prev_y = state.ball_y
    
    # Update position
    state.ball_x += state.ball_vx
    state.ball_y += state.ball_vy
    
    # Top/Bottom wall collision
    if state.ball_y <= 0 or state.ball_y >= GAME_HEIGHT - 1:
        state.ball_vy = -state.ball_vy
        state.ball_y = max(0, min(GAME_HEIGHT - 1, state.ball_y))
        if events:
            events.wall_bounce = True
    
    # Get paddle heights (support for power-ups)
    paddle1_height = getattr(state, 'paddle1_height', PADDLE_HEIGHT)
    paddle2_height = getattr(state, 'paddle2_height', PADDLE_HEIGHT)
    
    # Left paddle collision (Player 1)
    paddle1_x = 2
    if state.ball_x <= paddle1_x + 1 and state.ball_vx < 0:
        if state.paddle1_y <= state.ball_y <= state.paddle1_y + paddle1_height:
            state.ball_vx = -state.ball_vx
            state.ball_x = paddle1_x + 1
            
            if events:
                events.paddle1_hit = True
                events.paddle_hit_position = (paddle1_x, state.paddle1_y, paddle1_height)
    
    # Right paddle collision (Player 2)
    paddle2_x = GAME_WIDTH - 3
    if state.ball_x >= paddle2_x - 1 and state.ball_vx > 0:
        if state.paddle2_y <= state.ball_y <= state.paddle2_y + paddle2_height:
            state.ball_vx = -state.ball_vx
            state.ball_x = paddle2_x - 1
            
            if events:
                events.paddle2_hit = True
                events.paddle_hit_position = (paddle2_x, state.paddle2_y, paddle2_height)
    
    # Scoring
    if state.ball_x <= 0:
        state.score2 += 1
        if events:
            events.goal_scored = 2
            events.goal_position = (int(state.ball_x), int(state.ball_y))
        reset_ball(state, direction=1)
    elif state.ball_x >= GAME_WIDTH - 1:
        state.score1 += 1
        if events:
            events.goal_scored = 1
            events.goal_position = (int(state.ball_x), int(state.ball_y))
        reset_ball(state, direction=-1)
    
    # Check win condition
    if state.score1 >= WIN_SCORE:
        state.running = False
        state.winner = 1
    elif state.score2 >= WIN_SCORE:
        state.running = False
        state.winner = 2
    
    return events


def reset_ball(state, direction):
    """Reset ball to center after scoring."""
    state.ball_x = GAME_WIDTH // 2
    state.ball_y = GAME_HEIGHT // 2
    state.ball_vx = BALL_SPEED_X * direction
    state.ball_vy = BALL_SPEED_Y * random.choice([-1, 1])


def move_paddle(state, player_id, direction):
    """Move paddle up or down."""
    # Get paddle heights (support for power-ups)
    paddle1_height = getattr(state, 'paddle1_height', PADDLE_HEIGHT)
    paddle2_height = getattr(state, 'paddle2_height', PADDLE_HEIGHT)
    
    if player_id == 1:
        if direction == 'W':
            state.paddle1_y = max(0, state.paddle1_y - 1)
        elif direction == 'S':
            state.paddle1_y = min(GAME_HEIGHT - paddle1_height, state.paddle1_y + 1)
    else:
        if direction == 'W':
            state.paddle2_y = max(0, state.paddle2_y - 1)
        elif direction == 'S':
            state.paddle2_y = min(GAME_HEIGHT - paddle2_height, state.paddle2_y + 1)


def process_physics_events(events, effects_manager=None):
    """
    Process physics events and trigger appropriate effects.
    
    Args:
        events: PhysicsEvents object from update_physics
        effects_manager: Optional EffectsManager for visual effects
    """
    if events is None:
        return
    
    # Import sound module
    try:
        from sound import play_collision, play_wall_bounce, play_goal
    except ImportError:
        play_collision = play_wall_bounce = play_goal = lambda: None
    
    # Handle wall bounce
    if events.wall_bounce:
        play_wall_bounce()
    
    # Handle paddle hits
    if events.paddle1_hit or events.paddle2_hit:
        play_collision()
        if effects_manager and events.paddle_hit_position:
            x, y, height = events.paddle_hit_position
            effects_manager.trigger_paddle_hit(x, y, height)
    
    # Handle goal scored
    if events.goal_scored:
        play_goal()
        if effects_manager and events.goal_position:
            x, y = events.goal_position
            effects_manager.trigger_goal_explosion(x, y)
