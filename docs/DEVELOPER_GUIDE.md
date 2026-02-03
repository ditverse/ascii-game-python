# Panduan Developer

## Daftar Isi
1. [Arsitektur](#arsitektur)
2. [Struktur File](#struktur-file)
3. [Modul Utama](#modul-utama)
4. [Protokol Jaringan](#protokol-jaringan)
5. [Menambah Fitur](#menambah-fitur)
6. [Testing](#testing)

---

## Arsitektur

Game menggunakan arsitektur **MVC (Model-View-Controller)** yang dimodifikasi:

```
┌─────────────────────────────────────────────────┐
│                   main.py                       │
│              (Entry Point & Menu)               │
└─────────────────────┬───────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ VS AI   │   │  Host   │   │  Join   │
   │  Mode   │   │  Mode   │   │  Mode   │
   └────┬────┘   └────┬────┘   └────┬────┘
        │             │             │
        ▼             ▼             ▼
   ┌─────────────────────────────────────┐
   │            Game Loop                │
   │  ┌─────────┐ ┌─────────┐ ┌────────┐│
   │  │ Input   │→│ Physics │→│ Render ││
   │  └─────────┘ └─────────┘ └────────┘│
   └─────────────────────────────────────┘
```

---

## Struktur File

```
pong-cli/
├── main.py           # Entry point, menu, game loops
├── config.py         # Konstanta dan konfigurasi
├── game_state.py     # GameState class (Model)
├── physics.py        # Fisika bola, collision, scoring
├── renderer.py       # Rendering ke terminal (View)
├── input_handler.py  # Non-blocking keyboard input
├── ai.py             # AI Controller
├── powerups.py       # Sistem power-ups
├── effects.py        # Efek visual (trail, explosion)
├── sound.py          # Sound effects player
├── colors.py         # ANSI color utilities
├── ui_components.py  # Komponen UI reusable
├── server.py         # TCP Server
├── client.py         # TCP Client
├── sfx.mp3           # Audio file
└── docs/
    ├── USER_MANUAL.md
    ├── DEVELOPER_GUIDE.md
    ├── SYSTEM_ARCHITECTURE.md
    └── diagrams/
```

---

## Modul Utama

### game_state.py
```python
class GameState:
    paddle1_y: int      # Posisi Y paddle player 1
    paddle2_y: int      # Posisi Y paddle player 2
    ball_x: float       # Posisi X bola
    ball_y: float       # Posisi Y bola
    ball_vx: float      # Kecepatan X bola
    ball_vy: float      # Kecepatan Y bola
    score1: int         # Skor player 1
    score2: int         # Skor player 2
    running: bool       # Game sedang berjalan
    winner: int         # Pemenang (1 atau 2)
```

### physics.py
```python
def update_physics(state, return_events=False):
    """Update posisi bola dan deteksi collision."""
    # Returns PhysicsEvents jika return_events=True
    
class PhysicsEvents:
    wall_bounce: bool           # Bola memantul dinding
    paddle1_hit: bool           # Bola kena paddle 1
    paddle2_hit: bool           # Bola kena paddle 2
    goal_scored: int            # Player yang mencetak gol
    goal_position: tuple        # Posisi gol (x, y)
    paddle_hit_position: tuple  # Posisi paddle hit

def process_physics_events(events, effects_manager=None):
    """Proses event untuk trigger sound dan visual effects."""
```

### ai.py
```python
class AIController:
    def __init__(self, difficulty='medium'):
        # Difficulty: 'easy', 'medium', 'hard'
        
    def update(self, state) -> str:
        """Return 'W' untuk naik, 'S' untuk turun, None diam."""
```

### powerups.py
```python
class PowerUp:
    symbol: str         # Karakter yang ditampilkan
    name: str           # Nama power-up
    effect_duration: float  # Durasi efek (detik)

class SpeedBoost(PowerUp):    # Simbol: 'S'
class PaddleGrow(PowerUp):    # Simbol: '+'
class PaddleShrink(PowerUp):  # Simbol: '-'

class PowerUpManager:
    def update(self, state, current_time):
        """Spawn, collect, dan expire power-ups."""
```

### effects.py
```python
class BallTrail:
    """Jejak bola yang memudar."""
    
class GoalExplosion:
    """Animasi ledakan saat gol."""
    
class PaddleHitEffect:
    """Efek kilat saat paddle memukul bola."""
    
class EffectsManager:
    """Mengelola semua efek visual."""
    def update(): ...
    def get_all_particles(): ...
```

### sound.py
```python
# Auto-detect audio player: ffplay, mpv, paplay
def play_collision():  # Play sfx.mp3
def play_goal(): ...
def play_powerup(): ...
def play_game_start(): ...
def play_game_over(): ...
```

---

## Protokol Jaringan

Game menggunakan **TCP** untuk komunikasi multiplayer.

### Message Format
```
TYPE:DATA\n
```

### Message Types

| Type | Direction | Data | Deskripsi |
|------|-----------|------|-----------|
| `PLAYER_ID` | S→C | `1` atau `2` | Assign player ID |
| `STATE` | S→C | JSON GameState | Update game state |
| `LOBBY` | S→C | JSON LobbyState | Update lobby state |
| `INPUT` | C→S | `W`, `S`, `Q` | Player input |
| `CHAT` | C↔S | String message | Chat message |
| `START` | S→C | - | Game dimulai |
| `GAME_OVER` | S→C | Winner ID | Game selesai |

### Flow Diagram
```
Client                    Server
   │                         │
   │──── Connect ───────────>│
   │<─── PLAYER_ID:1 ────────│
   │                         │
   │<─── LOBBY:{"players":..}│  (Periodic)
   │                         │
   │<─── START ──────────────│
   │                         │
   │──── INPUT:W ───────────>│
   │<─── STATE:{...} ────────│  (30 FPS)
   │                         │
   │<─── GAME_OVER:1 ────────│
```

---

## Menambah Fitur

### Menambah Power-up Baru

1. Buat class di `powerups.py`:
```python
class MyPowerUp(PowerUp):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = 'X'  # Karakter ASCII
        self.name = 'MyPower'
        
    def apply(self, state, player_id):
        super().apply(state, player_id)
        # Efek saat diambil
        
    def remove_effect(self, state):
        # Hapus efek saat expire
```

2. Tambah ke `POWER_UP_TYPES`:
```python
POWER_UP_TYPES = [SpeedBoost, PaddleGrow, PaddleShrink, MyPowerUp]
```

3. Update renderer untuk menampilkan simbol:
```python
elif char in ['+', '-', 'S', 'X']:  # Tambah 'X'
```

### Menambah Efek Visual Baru

1. Buat class di `effects.py`:
```python
class MyEffect:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.finished = False
        
    def update(self):
        # Update animasi, set finished=True saat selesai
        
    def get_particles(self):
        # Return list of (x, y, char)
```

2. Tambah ke `EffectsManager`:
```python
def trigger_my_effect(self, x, y):
    effect = MyEffect(x, y)
    self.active_effects.append(effect)
```

---

## Testing

### Compile Check
```bash
python3 -m py_compile *.py
```

### Run Game
```bash
python3 main.py
```

### Test Multiplayer Lokal
```bash
# Terminal 1 (Host)
python3 main.py
# Pilih Host Game

# Terminal 2 (Client)
python3 main.py
# Pilih Join Game, IP: 127.0.0.1
```

### Test Sound
```bash
python3 -c "from sound import play_collision; play_collision(); import time; time.sleep(1)"
```

---

## Style Guide

- **PEP 8** untuk Python code style
- **Docstrings** untuk semua fungsi publik
- **Type hints** untuk parameter penting
- **ANSI colors** via `colors.py`, bukan hardcoded
- **Constants** di `config.py`

---

*Happy Coding!* 💻
