# Class Diagram

Diagram ini menunjukkan struktur class dan hubungan antar komponen dalam PONG-CLI.

```mermaid
classDiagram
    %% Core Classes
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
        +int paddle1_height
        +int paddle2_height
        +to_dict() dict
        +from_dict(data) GameState
    }
    
    class PhysicsEvents {
        +bool wall_bounce
        +bool paddle1_hit
        +bool paddle2_hit
        +int goal_scored
        +tuple goal_position
        +tuple paddle_hit_position
    }
    
    %% AI Module
    class AIController {
        -str difficulty
        -float reaction_time
        -float accuracy
        -float error_margin
        -float last_move_time
        +update(state) str
        -_predict_ball_y(state) float
    }
    
    %% Power-ups Module
    class PowerUp {
        <<abstract>>
        +int x
        +int y
        +bool active
        +bool collected
        +str symbol
        +str name
        +float effect_duration
        +float effect_start_time
        +apply(state, player_id)
        +remove_effect(state)
        +is_effect_expired() bool
    }
    
    class SpeedBoost {
        +str symbol = "S"
        +float speed_multiplier = 1.5
        +apply(state, player_id)
        +remove_effect(state)
    }
    
    class PaddleGrow {
        +str symbol = "+"
        +int size_increase = 2
        +apply(state, player_id)
        +remove_effect(state)
    }
    
    class PaddleShrink {
        +str symbol = "-"
        +int size_decrease = 2
        +apply(state, player_id)
        +remove_effect(state)
    }
    
    class PowerUpManager {
        +list active_powerups
        +list active_effects
        +float last_spawn_time
        +float spawn_interval
        +bool enabled
        +update(state, current_time)
        +get_field_powerups() list
        +get_active_effects() list
        +reset()
    }
    
    %% Effects Module
    class BallTrail {
        +deque positions
        +int max_length
        +bool use_unicode
        +update(x, y)
        +get_trail() list
        +clear()
    }
    
    class GoalExplosion {
        +int x
        +int y
        +int current_frame
        +bool finished
        +update()
        +get_particles() list
    }
    
    class PaddleHitEffect {
        +int paddle_x
        +int paddle_y
        +int paddle_height
        +bool finished
        +update()
        +get_particles() list
    }
    
    class EffectsManager {
        +BallTrail ball_trail
        +list active_explosions
        +list active_hit_effects
        +update()
        +update_ball_trail(x, y)
        +trigger_goal_explosion(x, y)
        +trigger_paddle_hit(x, y, h)
        +get_all_particles() list
        +clear()
    }
    
    %% Input Module
    class InputHandler {
        -Thread input_thread
        -bool running
        -str mode
        -str current_key
        -str current_line
        +start()
        +stop()
        +set_mode(mode)
        +get_key() str
        +get_line() str
    }
    
    %% Network Classes
    class Server {
        +socket server_socket
        +list clients
        +GameState state
        +bool running
        +start(port)
        +broadcast(message)
        +handle_client(client)
    }
    
    class Client {
        +socket client_socket
        +int player_id
        +bool connected
        +connect(host, port)
        +send(message)
        +receive() str
    }
    
    %% Relationships
    PowerUp <|-- SpeedBoost
    PowerUp <|-- PaddleGrow
    PowerUp <|-- PaddleShrink
    PowerUpManager "1" --> "*" PowerUp : manages
    
    EffectsManager "1" --> "1" BallTrail : contains
    EffectsManager "1" --> "*" GoalExplosion : contains
    EffectsManager "1" --> "*" PaddleHitEffect : contains
    
    Server --> GameState : uses
    Client --> GameState : receives
    
    AIController --> GameState : reads
```

## Penjelasan

### Core Classes
- **GameState**: Menyimpan seluruh state permainan (posisi, skor, dll)
- **PhysicsEvents**: Container untuk event yang terjadi saat physics update

### AI Module
- **AIController**: Mengontrol paddle AI dengan berbagai tingkat kesulitan

### Power-ups Module
- **PowerUp**: Base class untuk semua power-up
- **SpeedBoost**: Mempercepat bola (simbol: S)
- **PaddleGrow**: Memperbesar paddle (simbol: +)
- **PaddleShrink**: Memperkecil paddle lawan (simbol: -)
- **PowerUpManager**: Mengelola spawn dan efek power-up

### Effects Module
- **BallTrail**: Efek jejak bola
- **GoalExplosion**: Animasi ledakan saat gol
- **PaddleHitEffect**: Efek kilat saat paddle memukul bola
- **EffectsManager**: Mengelola semua efek visual

### Network Classes
- **Server**: TCP server untuk mode multiplayer
- **Client**: TCP client untuk join game
