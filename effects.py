"""
Visual Effects Module
ASCII animations and visual effects for game events.
"""

import time
from collections import deque


class BallTrail:
    """
    Creates a trailing effect behind the ball.
    Stores recent ball positions and renders them with fading intensity.
    """
    
    # Trail characters from newest to oldest (fading effect)
    TRAIL_CHARS = ['●', '◉', '○', '◦', '·', ' ']
    TRAIL_CHARS_ASCII = ['O', 'o', '.', ' ']
    
    def __init__(self, max_length=5, use_unicode=True):
        """
        Initialize ball trail.
        
        Args:
            max_length: Number of trail positions to keep
            use_unicode: Whether to use Unicode characters
        """
        self.positions = deque(maxlen=max_length)
        self.use_unicode = use_unicode
    
    def update(self, x, y):
        """Add new ball position to trail."""
        self.positions.append((int(x), int(y)))
    
    def get_trail(self):
        """
        Get trail positions with their display characters.
        
        Returns:
            List of (x, y, char) tuples, oldest first
        """
        chars = self.TRAIL_CHARS if self.use_unicode else self.TRAIL_CHARS_ASCII
        trail = []
        
        positions = list(self.positions)
        # Skip the last position (current ball position)
        for i, (x, y) in enumerate(positions[:-1] if len(positions) > 1 else []):
            # Older positions use later characters (more faded)
            char_idx = len(positions) - i - 2
            if char_idx < len(chars):
                trail.append((x, y, chars[char_idx]))
        
        return trail
    
    def clear(self):
        """Clear the trail."""
        self.positions.clear()


class GoalExplosion:
    """
    Explosion animation when a goal is scored.
    """
    
    # Explosion frames - each frame is a list of (relative_x, relative_y, char)
    EXPLOSION_FRAMES = [
        # Frame 1: Small burst
        [
            (0, 0, '★'),
        ],
        # Frame 2: Expanding
        [
            (0, 0, '★'),
            (-1, 0, '*'), (1, 0, '*'),
            (0, -1, '*'), (0, 1, '*'),
        ],
        # Frame 3: Full explosion
        [
            (0, 0, '◉'),
            (-1, 0, '★'), (1, 0, '★'),
            (0, -1, '★'), (0, 1, '★'),
            (-2, 0, '*'), (2, 0, '*'),
            (0, -2, '*'), (0, 2, '*'),
            (-1, -1, '·'), (1, -1, '·'),
            (-1, 1, '·'), (1, 1, '·'),
        ],
        # Frame 4: Fading
        [
            (0, 0, '○'),
            (-1, 0, '·'), (1, 0, '·'),
            (0, -1, '·'), (0, 1, '·'),
        ],
        # Frame 5: Almost gone
        [
            (0, 0, '·'),
        ],
    ]
    
    EXPLOSION_FRAMES_ASCII = [
        [(0, 0, '*')],
        [(0, 0, '*'), (-1, 0, '+'), (1, 0, '+'), (0, -1, '+'), (0, 1, '+')],
        [(0, 0, 'O'), (-1, 0, '*'), (1, 0, '*'), (0, -1, '*'), (0, 1, '*'),
         (-2, 0, '+'), (2, 0, '+'), (0, -2, '+'), (0, 2, '+')],
        [(0, 0, 'o'), (-1, 0, '.'), (1, 0, '.'), (0, -1, '.'), (0, 1, '.')],
        [(0, 0, '.')],
    ]
    
    def __init__(self, x, y, use_unicode=True):
        """
        Start an explosion at the given position.
        
        Args:
            x, y: Center position of explosion
            use_unicode: Whether to use Unicode characters
        """
        self.x = x
        self.y = y
        self.use_unicode = use_unicode
        self.current_frame = 0
        self.frame_duration = 0.1  # seconds per frame
        self.last_frame_time = time.time()
        self.finished = False
    
    def update(self):
        """Update explosion animation. Call this each render frame."""
        if self.finished:
            return
        
        current_time = time.time()
        if current_time - self.last_frame_time >= self.frame_duration:
            self.current_frame += 1
            self.last_frame_time = current_time
            
            frames = self.EXPLOSION_FRAMES if self.use_unicode else self.EXPLOSION_FRAMES_ASCII
            if self.current_frame >= len(frames):
                self.finished = True
    
    def get_particles(self):
        """
        Get current explosion particles.
        
        Returns:
            List of (x, y, char) tuples for current frame
        """
        if self.finished:
            return []
        
        frames = self.EXPLOSION_FRAMES if self.use_unicode else self.EXPLOSION_FRAMES_ASCII
        if self.current_frame >= len(frames):
            return []
        
        frame = frames[self.current_frame]
        return [(self.x + dx, self.y + dy, char) for dx, dy, char in frame]


class PaddleHitEffect:
    """
    Brief flash effect when ball hits paddle.
    """
    
    FLASH_CHARS = ['█', '▓', '▒', '░']
    FLASH_CHARS_ASCII = ['#', '=', '-', ' ']
    
    def __init__(self, paddle_x, paddle_y, paddle_height, use_unicode=True):
        """
        Create hit effect on paddle.
        """
        self.paddle_x = paddle_x
        self.paddle_y = paddle_y
        self.paddle_height = paddle_height
        self.use_unicode = use_unicode
        self.current_frame = 0
        self.frame_duration = 0.05
        self.last_frame_time = time.time()
        self.finished = False
    
    def update(self):
        """Update hit effect animation."""
        if self.finished:
            return
        
        current_time = time.time()
        if current_time - self.last_frame_time >= self.frame_duration:
            self.current_frame += 1
            self.last_frame_time = current_time
            
            chars = self.FLASH_CHARS if self.use_unicode else self.FLASH_CHARS_ASCII
            if self.current_frame >= len(chars):
                self.finished = True
    
    def get_particles(self):
        """Get current effect particles."""
        if self.finished:
            return []
        
        chars = self.FLASH_CHARS if self.use_unicode else self.FLASH_CHARS_ASCII
        if self.current_frame >= len(chars):
            return []
        
        char = chars[self.current_frame]
        # Flash next to paddle
        return [(self.paddle_x, self.paddle_y + i, char) 
                for i in range(self.paddle_height)]


class EffectsManager:
    """
    Manages all visual effects during gameplay.
    """
    
    def __init__(self, use_unicode=True):
        """Initialize effects manager."""
        self.use_unicode = use_unicode
        self.ball_trail = BallTrail(max_length=5, use_unicode=use_unicode)
        self.active_explosions = []
        self.active_hit_effects = []
    
    def update_ball_trail(self, ball_x, ball_y):
        """Update ball trail with new position."""
        self.ball_trail.update(ball_x, ball_y)
    
    def trigger_goal_explosion(self, x, y):
        """Trigger a goal explosion at given position."""
        explosion = GoalExplosion(x, y, self.use_unicode)
        self.active_explosions.append(explosion)
    
    def trigger_paddle_hit(self, paddle_x, paddle_y, paddle_height):
        """Trigger a paddle hit effect."""
        effect = PaddleHitEffect(paddle_x, paddle_y, paddle_height, self.use_unicode)
        self.active_hit_effects.append(effect)
    
    def update(self):
        """Update all active effects."""
        # Update explosions
        for explosion in self.active_explosions[:]:
            explosion.update()
            if explosion.finished:
                self.active_explosions.remove(explosion)
        
        # Update hit effects
        for effect in self.active_hit_effects[:]:
            effect.update()
            if effect.finished:
                self.active_hit_effects.remove(effect)
    
    def get_all_particles(self):
        """
        Get all effect particles for rendering.
        
        Returns:
            List of (x, y, char, effect_type) tuples
        """
        particles = []
        
        # Ball trail
        for x, y, char in self.ball_trail.get_trail():
            particles.append((x, y, char, 'trail'))
        
        # Explosions
        for explosion in self.active_explosions:
            for x, y, char in explosion.get_particles():
                particles.append((x, y, char, 'explosion'))
        
        # Hit effects
        for effect in self.active_hit_effects:
            for x, y, char in effect.get_particles():
                particles.append((x, y, char, 'hit'))
        
        return particles
    
    def clear(self):
        """Clear all effects."""
        self.ball_trail.clear()
        self.active_explosions.clear()
        self.active_hit_effects.clear()


# Goal celebration text frames
GOAL_CELEBRATION = [
    "      GOAL!      ",
    "    ★ GOAL! ★    ",
    "  ★★ GOAL! ★★  ",
    " ★★★ GOAL! ★★★ ",
    "  ★★ GOAL! ★★  ",
    "    ★ GOAL! ★    ",
    "      GOAL!      ",
]

GOAL_CELEBRATION_ASCII = [
    "      GOAL!      ",
    "    * GOAL! *    ",
    "  ** GOAL! **  ",
    " *** GOAL! *** ",
    "  ** GOAL! **  ",
    "    * GOAL! *    ",
    "      GOAL!      ",
]
