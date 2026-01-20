import random
from config import (
    GAME_WIDTH, GAME_HEIGHT, PADDLE_HEIGHT, WIN_SCORE,
    BALL_SPEED_X, BALL_SPEED_Y
)


def update_physics(state):
    """Update ball position and handle collisions."""
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
