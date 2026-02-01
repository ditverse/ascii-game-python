# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# Game dimensions
GAME_WIDTH = 60
GAME_HEIGHT = 20
PADDLE_HEIGHT = 4

# Scoring
WIN_SCORE = 5

# Frame rate
FPS = 20
FRAME_TIME = 1.0 / FPS

# Network
PORT = 5555
BUFFER_SIZE = 2048

# Ball speed
BALL_SPEED_X = 1.5
BALL_SPEED_Y = 1.0

# Lobby
MAX_CHAT_HISTORY = 8
LOBBY_WIDTH = 62

# ============================================================================
# UI/UX SETTINGS
# ============================================================================

# Enable ANSI color codes (disable for terminals that don't support)
ENABLE_COLORS = True

# Enable Unicode box drawing (disable for ASCII-only terminals)
ENABLE_UNICODE = True

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

import logging

LOG_LEVEL = logging.INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "[%(levelname)s] %(message)s"

# ============================================================================
# CUSTOMIZATION (Phase 5 - placeholder)
# ============================================================================

# Default player name
DEFAULT_PLAYER_NAME = "Player"

# Game elements (can be customized later)
BALL_CHAR = "●"
PADDLE_CHAR = "█"
NET_CHAR = ":"
