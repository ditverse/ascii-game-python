# Visualisasi Flowchart Program

## Deskripsi
Diagram alir (flowchart) di bawah ini menggambarkan alur eksekusi utama dari aplikasi PONG-CLI. Dimulai dari inisialisasi aplikasi, pengguna masuk ke **Menu Utama** di mana mereka memiliki tiga pilihan mode permainan utama:
1.  **Host Game**: Menjadikan komputer sebagai server untuk permainan multipemain.
2.  **Join Game**: Menghubungkan komputer sebagai klien ke server yang sudah ada.
3.  **VS AI**: Bermain melawan komputer (Single Player) dengan pilihan tingkat kesulitan.

Setelah permainan selesai (Game Over), alur akan kembali ke Menu Utama, memungkinkan pengguna untuk memulai permainan baru atau keluar dari aplikasi.

## Flowchart

```mermaid
flowchart TD
    Start([Mulai Aplikasi]) --> Init[Inisialisasi Config & Logger]
    Init --> MainMenu{Menu Utama}
    
    MainMenu -->|Pilih Host| HostSetup[Setup Server & Socket]
    MainMenu -->|Pilih Join| JoinSetup[Setup Client & Socket]
    MainMenu -->|Pilih VS AI| DiffSelect{Pilih Tingkat Kesulitan}
    MainMenu -->|Pilih Quit| Stop([Keluar Aplikasi])
    
    HostSetup --> LobbyHost[Lobby: Menunggu Client]
    JoinSetup --> LobbyJoin[Lobby: Menunggu Koneksi]
    
    LobbyHost -->|Tersambung| MpGameLoop[Loop Game Multipemain]
    LobbyJoin -->|Tersambung| MpGameLoop
    
    DiffSelect -->|Easy/Med/Hard| AiGameLoop[Loop Game Single Player]
    DiffSelect -->|Batal| MainMenu
    
    subgraph Gameplay [Proses Permainan]
        MpGameLoop --> UpdateNet[Sync Network State]
        AiGameLoop --> UpdateAi[Hitung Logika AI]
        
        UpdateNet --> Physics[Update Fisika Bola & Raket]
        UpdateAi --> Physics
        
        Physics --> Render[Render Frame ke Terminal]
        Render --> CheckWin{Ada Pemenang?}
        
        CheckWin -->|Tidak| Physics
        CheckWin -->|Ya| GameOver[Tampilkan Layar Game Over]
    end
    
    GameOver -->|Tunggu 3 Detik| MainMenu
```
