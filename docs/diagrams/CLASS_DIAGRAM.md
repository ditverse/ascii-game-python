# Visualisasi Class Diagram Program

## Deskripsi
Class Diagram ini memetakan struktur statis dari perangkat lunak, menunjukkan kelas-kelas utama, atribut penting, metode-metode kunci, dan hubungan antar mereka.
- **GameState**: Kelas pusat yang meyimpan data permainan. Diakses oleh hampir semua modul lain.
- **AIController**: Kelas yang membungkus logika keputusan lawan komputer.
- **GameServer/GameClient**: Kelas-kelas yang menangani komunikasi jaringan TCP.
- **InputHandler**: Kelas utilitas untuk abstraksi input keyboard.
- **Physics**: Bukan kelas (modul fungsional), tetapi digambarkan untuk menunjukkan tanggung jawab logika fisika.

## Diagram Mermaid

```mermaid
classDiagram
    direction TB
    
    class GameState {
        +float ball_x
        +float ball_y
        +float ball_vx
        +float ball_vy
        +float paddle1_y
        +float paddle2_y
        +int score1
        +int score2
        +bool running
        +reset()
    }

    class AIController {
        +dict settings
        +str difficulty
        +float target_y
        +update(state) str
        +set_difficulty(diff)
    }

    class InputHandler {
        +lock threading.Lock
        +str mode
        +start()
        +stop()
        +get_key() char
    }

    class GameServer {
        +str host
        +int port
        +socket sock
        +list clients
        +start()
        +broadcast_state()
    }

    class GameClient {
        +socket sock
        +connect(host, port)
        +send_input(key)
        +receive_state()
    }

    class Renderer {
        <<Module>>
        +render_game_ai(state)
        +show_game_over_ai(winner)
        +draw_box()
        +center_text()
    }

    class Physics {
        <<Module>>
        +update_physics(state)
        +check_collision(state)
        +move_paddle(state, id, direction)
    }

    %% Relationships
    Main ..> input_handler : Instantiates
    Main ..> GameState : Manages
    Main ..> Renderer : Calls
    
    %% VS AI Mode
    Main ..> AIController : Uses
    AIController ..> GameState : Reads
    
    %% Multiplayer Mode
    Main ..> GameServer : Starts
    Main ..> GameClient : Starts
    GameServer ..> GameState : Syncs
    
    %% Logic
    Main ..> Physics : Calls Loop
    Physics ..> GameState : Modifies
```
