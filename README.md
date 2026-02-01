# PONG-CLI - Game Multiplayer Terminal

Sebuah permainan Pong modern berbasis terminal dengan grafis ASCII. Proyek ini menghadirkan aksi arcade klasik ke dalam terminal Anda dengan dukungan untuk **Multiplayer Real-time** (LAN) dan **Single Player VS AI**.

Dibuat menggunakan Python 3 Standard Library tanpa dependensi eksternal.

## Fitur Utama

- **Multiplayer LAN**: Dua pemain dapat bermain secara real-time di jaringan lokal.
- **VS AI Mode**: Tantang komputer dalam 3 tingkat kesulitan (Easy, Medium, Hard).
- **Lobby & Chat**: Sistem lobby interaktif untuk menunggu lawan dan mengobrol.
- **UI Responsif**: Tampilan menyesuaikan dengan ukuran terminal Anda.
- **Efek Suara**: Umpan balik audio sederhana (beep) untuk aksi permainan.
- **Tanpa Instalasi Ribet**: Cukup `git clone` dan jalankan.

## Dokumentasi Lengkap

Dokumentasi rinci tersedia di folder `docs/`:

- **[Panduan Pengguna (User Manual)](docs/USER_MANUAL.md)**: Cara instalasi, kontrolgame, dan troubleshooting.
- **[Arsitektur Sistem](docs/SYSTEM_ARCHITECTURE.md)**: Penjelasan teknis, diagram kelas, dan alur sistem.
- **[Panduan Pengembang](docs/DEVELOPER_GUIDE.md)**: Struktur kode, protokol jaringan, dan cara berkontribusi.
- **[Diagram Visual](docs/diagrams/)**: Flowchart, Sequence, dan Class Diagram.

## Persyaratan

- Python 3.6 atau lebih baru.
- Terminal yang mendukung ANSI escape codes (Linux/Mac default, Windows Terminal disarankan).
- Koneksi jaringan (Wi-Fi/LAN) untuk fitur multiplayer.

## Cara Bermain

1. Buka terminal di folder proyek.
2. Jalankan permainan:
   ```bash
   python3 main.py
   ```
3. Gunakan tombol **Panah Atas/Bawah** atau **W/S** untuk navigasi menu, **Enter** untuk memilih.

### Mode VS AI (Single Player)
- Pilih menu **VS AI**.
- Pilih tingkat kesulitan:
  - **Easy**: AI lambat dan sering meleset.
  - **Medium**: Tantangan seimbang.
  - **Hard**: Tantangan kompetitif.

### Mode Multiplayer
- **Host**: Pilih **Host Game**, masukkan port, dan tunggu lawan.
- **Join**: Pilih **Join Game**, masukkan IP Host dan port.

### Kontrol Permainan

| Pemain | Atas | Bawah | Keluar |
| :--- | :--- | :--- | :--- |
| **Anda** | `W` atau `Panah Atas` | `S` atau `Panah Bawah` | `Q` |

## Struktur Proyek

```text
pong-cli/
├── main.py           # Entry point & Menu
├── game_state.py     # Data permainan (Model)
├── renderer.py       # Tampilan UI (View)
├── physics.py        # Logika pergerakan & tabrakan
├── ai.py             # Logika Kecerdasan Buatan
├── server.py         # Kode Server TCP
├── client.py         # Kode Client TCP
├── sound.py          # Sistem Suara
├── input_handler.py  # Input Keyboard Asinkron
└── docs/             # Dokumentasi Lengkap
```

## Penulis
Proyek Tugas Besar Network Programming.
Dibuat dengan ❤️ menggunakan Python.
