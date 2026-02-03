# Arsitektur Sistem

## Overview

PONG-CLI adalah aplikasi game terminal yang menggunakan arsitektur **Client-Server** untuk mode multiplayer dan **Single-Process** untuk mode VS AI.

```
┌────────────────────────────────────────────────────────────┐
│                      PONG-CLI                              │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   VS AI     │  │    Host     │  │       Join          │ │
│  │ Single Proc │  │   Server    │  │      Client         │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                     │           │
│         ▼                ▼                     ▼           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   Game Engine                       │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │  │
│  │  │GameState│ │ Physics │ │Renderer │ │  Input   │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   Extensions                         │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │  │
│  │  │   AI    │ │PowerUps │ │ Effects │ │  Sound   │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## Class Diagram

```mermaid
classDiagram
    class GameState {
        +int paddle1_y
        +int paddle2_y
        +float ball_x
        +float ball_y
        +float ball_vx
        +float ball_vy
        +int score1
        +int score2
        +bool running
        +int winner
        +to_dict()
        +from_dict()
    }
    
    class PhysicsEvents {
        +bool wall_bounce
        +bool paddle1_hit
        +bool paddle2_hit
        +int goal_scored
        +tuple goal_position
    }
    
    class AIController {
        -str difficulty
        -float reaction_time
        -float accuracy
        +update(state): str
    }
    
    class PowerUp {
        +int x
        +int y
        +str symbol
        +str name
        +float effect_duration
        +apply(state, player_id)
        +remove_effect(state)
        +is_effect_expired(): bool
    }
    
    class SpeedBoost
    class PaddleGrow
    class PaddleShrink
    
    class PowerUpManager {
        +list active_powerups
        +list active_effects
        +update(state, time)
        +get_field_powerups()
        +get_active_effects()
    }
    
    class EffectsManager {
        +BallTrail ball_trail
        +list active_explosions
        +update()
        +get_all_particles()
        +trigger_goal_explosion(x, y)
        +trigger_paddle_hit(...)
    }
    
    class InputHandler {
        +start()
        +stop()
        +set_mode(mode)
        +get_key()
        +get_line()
    }
    
    PowerUp <|-- SpeedBoost
    PowerUp <|-- PaddleGrow
    PowerUp <|-- PaddleShrink
    PowerUpManager --> PowerUp
    EffectsManager --> BallTrail
    EffectsManager --> GoalExplosion
```

---

## Sequence Diagram: VS AI Game Loop

```mermaid
sequenceDiagram
    participant Main as main.py
    participant Input as InputHandler
    participant AI as AIController
    participant Physics as physics.py
    participant Effects as EffectsManager
    participant PowerUps as PowerUpManager
    participant Renderer as renderer.py
    participant Sound as sound.py
    
    Main->>Input: get_key()
    Input-->>Main: 'W' / 'S' / None
    Main->>Physics: move_paddle(state, 1, key)
    
    Main->>AI: update(state)
    AI-->>Main: 'W' / 'S' / None
    Main->>Physics: move_paddle(state, 2, ai_move)
    
    Main->>Physics: update_physics(state, return_events=True)
    Physics-->>Main: PhysicsEvents
    
    Main->>Physics: process_physics_events(events, effects)
    Physics->>Sound: play_collision()
    Physics->>Effects: trigger_paddle_hit()
    
    Main->>PowerUps: update(state, current_time)
    Main->>Renderer: render_game_with_effects(state, 1, effects, powerups)
    
    loop 20 FPS
        Main->>Main: sleep(FRAME_TIME)
    end
```

---

## Sequence Diagram: Multiplayer Flow

```mermaid
sequenceDiagram
    participant Host as Host (Server)
    participant Client as Client
    
    Host->>Host: Start listening on port
    Client->>Host: TCP Connect
    Host-->>Client: PLAYER_ID:2
    
    loop Lobby Phase
        Host-->>Client: LOBBY:{"players":2}
        Client->>Host: CHAT:Hello!
        Host-->>Client: CHAT:Hello!
    end
    
    Host->>Client: START
    
    loop Game Phase (30 FPS)
        Client->>Host: INPUT:W
        Host->>Host: update_physics()
        Host-->>Client: STATE:{...}
    end
    
    Host-->>Client: GAME_OVER:1
```

---

## State Diagram: Game States

```mermaid
stateDiagram-v2
    [*] --> Menu
    
    Menu --> VSAIDifficulty: Select VS AI
    Menu --> HostLobby: Select Host
    Menu --> JoinInput: Select Join
    Menu --> [*]: Quit
    
    VSAIDifficulty --> Playing: Select Difficulty
    HostLobby --> Playing: Player Joined + TAB
    JoinInput --> ClientLobby: Connect Success
    ClientLobby --> Playing: Host Starts
    
    Playing --> GameOver: Win Condition
    Playing --> Menu: Quit (Q)
    
    GameOver --> Menu: Timeout 3s
    GameOver --> HostLobby: Multiplayer
```

---

## Data Flow

```
┌──────────────────────────────────────────────────────────┐
│                      INPUT LAYER                         │
│  ┌────────────────┐  ┌────────────────┐                 │
│  │ Keyboard Input │  │ Network Input  │                 │
│  │ (InputHandler) │  │ (Client recv)  │                 │
│  └───────┬────────┘  └───────┬────────┘                 │
└──────────┼───────────────────┼──────────────────────────┘
           │                   │
           ▼                   ▼
┌──────────────────────────────────────────────────────────┐
│                     LOGIC LAYER                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Physics │  │   AI    │  │PowerUps │  │ Effects │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
│       │            │            │            │          │
│       └────────────┴────────────┴────────────┘          │
│                         │                               │
│                         ▼                               │
│                   ┌───────────┐                         │
│                   │ GameState │                         │
│                   └─────┬─────┘                         │
└─────────────────────────┼───────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                         │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │
│  │    Renderer    │  │ Network Send   │  │  Sound   │  │
│  │   (Terminal)   │  │ (Server send)  │  │  Player  │  │
│  └────────────────┘  └────────────────┘  └──────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Modul Dependencies

```
main.py
├── config.py
├── colors.py
├── ui_components.py (uses pyfiglet)
├── input_handler.py
├── game_state.py
├── physics.py
│   └── sound.py
├── renderer.py
│   ├── colors.py
│   └── ui_components.py
├── ai.py
├── powerups.py
├── effects.py
├── server.py
│   ├── game_state.py
│   └── physics.py
└── client.py
    └── game_state.py
```

---

## Network Protocol Details

### TCP Connection
- **Port**: 5555 (configurable)
- **Buffer Size**: 2048 bytes
- **Encoding**: UTF-8
- **Delimiter**: Newline (`\n`)

### Message Format
```
TYPE:DATA\n
```

### State Serialization
```json
{
    "paddle1_y": 8,
    "paddle2_y": 8,
    "ball_x": 30.5,
    "ball_y": 10.2,
    "ball_vx": 1.5,
    "ball_vy": -1.0,
    "score1": 2,
    "score2": 1,
    "running": true,
    "winner": 0
}
```

---

## Performance Considerations

| Component | Target | Actual |
|-----------|--------|--------|
| Frame Rate | 20 FPS | ~20 FPS |
| Network Latency | <50ms | LAN: ~5ms |
| Input Latency | <16ms | ~10ms |
| Render Time | <10ms | ~5ms |

---

*Dokumentasi ini di-generate berdasarkan implementasi aktual.*
