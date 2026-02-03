"""
Sound Effects Module
Audio playback for game events using system audio players.
"""

import os
import subprocess
import threading


# Sound enabled flag
SOUND_ENABLED = True

# Path to sound files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SFX_COLLISION = os.path.join(SCRIPT_DIR, 'sfx.mp3')

# Audio player command (auto-detected)
AUDIO_PLAYER = None
AUDIO_ARGS = []


def _detect_audio_player():
    """Detect available audio player."""
    global AUDIO_PLAYER, AUDIO_ARGS
    
    # Check for mpv (best for low latency)
    try:
        result = subprocess.run(['which', 'mpv'], capture_output=True)
        if result.returncode == 0:
            AUDIO_PLAYER = 'mpv'
            AUDIO_ARGS = ['--no-video', '--really-quiet']
            return
    except:
        pass
    
    # Check for ffplay (ffmpeg)
    try:
        result = subprocess.run(['which', 'ffplay'], capture_output=True)
        if result.returncode == 0:
            AUDIO_PLAYER = 'ffplay'
            AUDIO_ARGS = ['-nodisp', '-autoexit', '-loglevel', 'quiet']
            return
    except:
        pass
    
    # Check for paplay (PulseAudio) - may not support mp3
    try:
        result = subprocess.run(['which', 'paplay'], capture_output=True)
        if result.returncode == 0:
            AUDIO_PLAYER = 'paplay'
            AUDIO_ARGS = []
            return
    except:
        pass
    
    # Check for aplay (ALSA) - wav only
    try:
        result = subprocess.run(['which', 'aplay'], capture_output=True)
        if result.returncode == 0:
            AUDIO_PLAYER = 'aplay'
            AUDIO_ARGS = ['-q']
            return
    except:
        pass
    
    AUDIO_PLAYER = None


# Initialize audio player
_detect_audio_player()


def set_sound_enabled(enabled):
    """Enable or disable sound effects."""
    global SOUND_ENABLED
    SOUND_ENABLED = enabled


def _play_sound_async(filepath):
    """Play sound file in background thread."""
    if not SOUND_ENABLED or not AUDIO_PLAYER:
        return
    
    if not os.path.exists(filepath):
        return
    
    def _play():
        try:
            cmd = [AUDIO_PLAYER] + AUDIO_ARGS + [filepath]
            subprocess.run(cmd, capture_output=True, timeout=5)
        except:
            pass
    
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()


def play_beep():
    """Play a beep sound."""
    _play_sound_async(SFX_COLLISION)


def play_collision():
    """Play sound on paddle collision."""
    _play_sound_async(SFX_COLLISION)


def play_wall_bounce():
    """Play sound on wall bounce."""
    pass  # Disabled


def play_goal():
    """Play sound when goal is scored."""
    pass  # Disabled


def play_powerup():
    """Play sound when powerup is collected."""
    pass  # Disabled


def play_game_start():
    """Play sound when game starts."""
    pass  # Disabled


def play_game_over():
    """Play sound when game ends."""
    pass  # Disabled


def get_sound_info():
    """Get information about sound configuration."""
    return {
        'enabled': SOUND_ENABLED,
        'player': AUDIO_PLAYER,
        'sfx_file': SFX_COLLISION,
        'sfx_exists': os.path.exists(SFX_COLLISION)
    }
