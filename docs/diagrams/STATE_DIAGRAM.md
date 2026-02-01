# Visualisasi State Diagram Program

## Deskripsi
State Diagram ini memodelkan status-status yang mungkin terjadi dalam aplikasi dan transisi apa yang memicu perpindahan status tersebut.
- **MainMenu**: Status awal saat aplikasi dibuka.
- **DiffSelect**: Sub-menu untuk memilih kesulitan AI.
- **Connecting**: Proses negosiasi socket untuk multipemain.
- **Playing**: Status utama saat permainan berlangsung.
- **Paused**: Status sementara (jika implementasi pause ada atau saat menunggu sinkronisasi).
- **GameOver**: Status akhir permainan sebelum kembali ke menu.

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> MainMenu
    
    state MainMenu {
        [*] --> Idle
        Idle --> Hosting : Pilih 'Host'
        Idle --> Joining : Pilih 'Join'
        Idle --> DifficultySelection : Pilih 'AI'
        DifficultySelection --> Idle : Tombol 'Q'
    }
    
    MainMenu --> Connecting : Host/Join Start
    MainMenu --> PlayingSingle : Difficulty Selected
    
    Connecting --> PlayingMulti : Koneksi Sukses
    Connecting --> MainMenu : Koneksi Gagal/Batal
    
    state PlayingMulti {
        [*] --> Syncing
        Syncing --> Running
        Running --> Syncing : Network Delay
    }
    
    state PlayingSingle {
        [*] --> RunningAI
        RunningAI --> LogicUpdate
        LogicUpdate --> RunningAI
    }
    
    PlayingMulti --> GameOver : Skor Mencapai 5
    PlayingSingle --> GameOver : Skor Mencapai 5
    
    GameOver --> MainMenu : Timer 3 Detik Habis
    
    MainMenu --> [*] : Pilih 'Quit'
```
