# Arsitektur Sistem

## 1. Ringkasan Eksekutif

Dokumen ini memberikan gambaran teknis mengenai arsitektur sistem PONG-CLI. Aplikasi ini adalah permainan Pong berbasis terminal yang mendukung mode pemain tunggal (Lawan AI) dan multipemain (LAN/Localhost). Sistem ini dibangun menggunakan Python 3 dan memanfaatkan pustaka standar untuk threading, jaringan, dan manipulasi terminal.

## 2. Arsitektur Tingkat Tinggi

Sistem mengikuti arsitektur modular yang memisahkan tanggung jawab antara jaringan, logika permainan, penanganan input, dan perenderan (rendering).

### 2.1 Komponen Inti

- **Game Engine**: Mengelola status permainan, perhitungan fisika, dan aturan main.
- **Networking Layer**: Menangani koneksi soket TCP untuk sinkronisasi multipemain.
- **Input System**: Menangkap input keyboard secara asinkron dengan cara yang aman (thread-safe).
- **Renderer**: Menggambar status permainan ke terminal menggunakan kode escape ANSI.
- **AI Module**: Menyediakan logika untuk lawan komputer pada mode pemain tunggal.

### 2.2 Struktur Direktori

| Modul | Deskripsi |
| :--- | :--- |
| `main.py` | Titik masuk (entry point), sistem menu, dan orkestrasi loop permainan. |
| `game_state.py` | Mendefinisikan struktur data untuk status permainan (bola, raket, skor). |
| `physics.py` | Logika inti permainan dan algoritma deteksi tabrakan. |
| `renderer.py` | Menangani output terminal dan penggambaran UI. |
| `input_handler.py` | Manajemen input keyboard lintas platform. |
| `server.py` | Implementasi Server TCP untuk hosting permainan. |
| `client.py` | Implementasi Client TCP untuk bergabung ke permainan. |
| `ai.py` | Logika Kecerdasan Buatan (AI) untuk mode pemain tunggal. |

## 3. Struktur Kelas

Diagram kelas berikut mengilustrasikan hubungan antara komponen utama sistem.

```mermaid
classDiagram
    class GameState {
        +float ball_x
        +float ball_y
        +float ball_vx
        +float ball_vy
        +float paddle1_y
        +float paddle2_y
        +int score1
        +int score2
        +reset()
    }

    class AIController {
        +float reaction_chance
        +float prediction_error
        +update(GameState state)
    }

    class InputHandler {
        +start()
        +stop()
        +get_key()
    }

    class GameServer {
        +host
        +port
        +start()
        +broadcast_state()
    }

    class GameClient {
        +connect()
        +send_input()
        +receive_state()
    }

    class Physics {
        +update_physics(GameState)
        +check_collisions()
    }

    main --> GameState : Mengelola
    main --> InputHandler : Menggunakan
    main --> AIController : Menggunakan (VS AI)
    main --> Physics : Memanggil
    
    GameServer --> GameState : Sinkronisasi
    GameClient --> GameState : Update salinan lokal
```

## 4. Alur Eksekusi (Game Loop)

Permainan beroperasi pada loop "fixed time-step" untuk memastikan konsistensi fisika di berbagai kecepatan mesin.

```mermaid
sequenceDiagram
    participant P as Pemain
    participant I as InputHandler
    participant M as MainLoop
    participant PHY as Physics
    participant R as Renderer
    participant AI as AIController

    Note over M: Mulai Permainan
    loop Setiap Frame (misal: 30 FPS)
        P->>I: Tekan Tombol
        I-->>M: Event Tombol
        
        alt Mode VS AI
            M->>AI: update(GameState)
            AI-->>M: Gerakan AI
        end

        M->>PHY: update_physics(GameState)
        Note right of PHY: Gerak Bola, Cek Tabrakan
        PHY-->>M: Status Terupdate

        M->>R: render_game(GameState)
        R-->>P: Output Terminal
        
        M->>M: Sleep(TargetFrameTime - Elapsed)
    end
```
