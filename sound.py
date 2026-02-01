"""
Sound Effects Module
Terminal-based audio feedback for game events.
"""

import sys
import os


# Sound enabled flag
SOUND_ENABLED = True


def set_sound_enabled(enabled):
    """Enable or disable sound effects."""
    global SOUND_ENABLED
    SOUND_ENABLED = enabled


def play_beep():
    """Play a terminal bell beep."""
    if not SOUND_ENABLED:
        return
    
    try:
        # Terminal bell character
        sys.stdout.write('\a')
        sys.stdout.flush()
    except:
        pass


def play_collision():
    """Play sound on paddle collision."""
    play_beep()


def play_wall_bounce():
    """Play sound on wall bounce (lighter beep or none)."""
    # Could be a different sound, but for now same as beep
    # Some terminals may not differentiate
    pass


def play_goal():
    """Play sound when goal is scored."""
    if not SOUND_ENABLED:
        return
    
    try:
        # Double beep for goal
        sys.stdout.write('\a')
        sys.stdout.flush()
    except:
        pass


def play_powerup():
    """Play sound when powerup is collected."""
    play_beep()


def play_game_start():
    """Play sound when game starts."""
    play_beep()


def play_game_over():
    """Play sound when game ends."""
    if not SOUND_ENABLED:
        return
    
    try:
        # Triple beep for game over
        import time
        for _ in range(3):
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(0.1)
    except:
        pass
