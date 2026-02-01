# Visualisasi Sequence Diagram Program

## Deskripsi
Sequence Diagram berikut mendetailkan interaksi yang terjadi dalam **satu frame** permainan (Single Player VS AI). Ini menunjukkan bagaimana InputHandler menangkap tombol, MainLoop mengorkestrasi logika, AI membuat keputusan, Physics menghitung pergerakan, dan Renderer menggambar hasilnya ke layar.

Alur ini berulang terus-menerus selama permainan berjalan (status `Running`).

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User as Pengguna
    participant Input as InputHandler (Thread)
    participant Main as MainLoop
    participant AI as AIController
    participant Physics as PhysicsModule
    participant State as GameState
    participant Render as Renderer

    Note over Input: Berjalan di background thread
    User->>Input: Tekan Tombol 'W'
    Input->>Input: Simpan keystroke

    Note over Main: Mulai Frame Baru
    Main->>Input: get_key()
    Input-->>Main: Return 'W'
    
    Main->>State: Update posisi Paddle 1 (Naik)
    
    Main->>AI: update(GameState)
    AI->>AI: Hitung prediksi bola
    AI->>AI: Tentukan arah gerak
    AI-->>Main: Return 'S' (Misal: AI Turun)
    Main->>State: Update posisi Paddle 2 (Turun)
    
    Main->>Physics: update_physics(GameState)
    Physics->>State: Update posisi Bola (x, y)
    Physics->>Physics: Cek Collision (Dinding/Raket)
    Physics-->>Main: Return (Status Skor)
    
    Main->>Render: render_game_ai(GameState)
    Render->>State: Baca posisi objek
    Render-->>User: Tampilkan Frame ASCII
    
    Main->>Main: Sleep(time_delta) untuk limit FPS
```
