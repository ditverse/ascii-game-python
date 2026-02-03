# PONG-CLI - Game Multiplayer Terminal

Sebuah permainan Pong modern berbasis terminal dengan grafis ASCII. Proyek ini menghadirkan aksi arcade klasik ke dalam terminal Anda dengan dukungan untuk **Multiplayer Real-time** (LAN) dan **Single Player VS AI**.

![Preview](docs/preview.png)

## Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Multiplayer LAN** | Dua pemain bermain real-time di jaringan lokal via TCP |
| **VS AI Mode** | Tantang komputer dalam 3 tingkat kesulitan |
| **Power-ups** | Item yang muncul di arena dan mempengaruhi gameplay |
| **Visual Effects** | Trail bola, animasi ledakan saat gol, efek paddle hit |
| **Sound Effects** | Suara collision menggunakan file audio (sfx.mp3) |
| **Lobby & Chat** | Sistem lobby interaktif dengan fitur chat |
| **UI Responsif** | Tampilan menyesuaikan dengan ukuran terminal |

## Persyaratan

- **Python 3.6+**
- **pyfiglet** (untuk ASCII art title)
- **ffplay/mpv** (opsional, untuk sound effects)
- Terminal dengan ANSI escape codes support

### Instalasi Dependensi

```bash
# Arch Linux / CachyOS
sudo pacman -S python-pyfiglet ffmpeg

# Ubuntu/Debian
pip install pyfiglet
sudo apt install ffmpeg

# Windows
pip install pyfiglet
# Download ffmpeg dari https://ffmpeg.org/
```

## Cara Bermain

```bash
# Clone repository
git clone https://github.com/username/pong-cli.git
cd pong-cli

# Jalankan game
python3 main.py
```

### Navigasi Menu
| Tombol | Aksi |
|--------|------|
| `W` / `↑` | Pilihan ke atas |
| `S` / `↓` | Pilihan ke bawah |
| `Enter` | Pilih menu |
| `Q` | Keluar |

### Mode Permainan

#### 1. VS AI (Single Player)
Bermain melawan komputer dengan 3 tingkat kesulitan:
- **Easy**: AI lambat, sering meleset
- **Medium**: Tantangan seimbang
- **Hard**: AI cepat dan akurat

#### 2. Multiplayer (Host/Join)
- **Host Game**: Menjadi server, tunggu pemain lain bergabung
- **Join Game**: Masukkan IP address host untuk bergabung

### Kontrol Dalam Game
| Tombol | Aksi |
|--------|------|
| `W` / `↑` | Paddle ke atas |
| `S` / `↓` | Paddle ke bawah |
| `Q` | Keluar dari game |

## Sistem Power-ups

Power-ups muncul secara acak di arena dan memberikan efek sementara (5 detik):

| Simbol | Nama | Efek |
|--------|------|------|
| **S** | Speed+ | Mempercepat bola 1.5x |
| **+** | Paddle+ | Memperbesar paddle pemain |
| **-** | Paddle- | Memperkecil paddle lawan |

## Struktur Proyek

```
pong-cli/
├── main.py           # Entry point & Menu utama
├── config.py         # Konfigurasi game (ukuran, kecepatan, dll)
├── game_state.py     # State management (skor, posisi)
├── physics.py        # Fisika bola & collision detection
├── renderer.py       # Rendering ASCII/Unicode ke terminal
├── input_handler.py  # Input keyboard non-blocking
├── ai.py             # AI opponent controller
├── powerups.py       # Sistem power-ups
├── effects.py        # Efek visual (trail, explosion)
├── sound.py          # Sound effects player
├── colors.py         # ANSI color utilities
├── ui_components.py  # Komponen UI (box, title, dll)
├── server.py         # TCP game server
├── client.py         # TCP game client
├── sfx.mp3           # File audio untuk collision
└── docs/             # Dokumentasi lengkap
    ├── USER_MANUAL.md
    ├── DEVELOPER_GUIDE.md
    ├── SYSTEM_ARCHITECTURE.md
    └── diagrams/
```

## Dokumentasi Lengkap

- [Panduan Pengguna](docs/USER_MANUAL.md) - Instalasi, kontrol, troubleshooting
- [Arsitektur Sistem](docs/SYSTEM_ARCHITECTURE.md) - Penjelasan teknis & diagram
- [Panduan Developer](docs/DEVELOPER_GUIDE.md) - Struktur kode & cara kontribusi
- [Diagram Visual](docs/diagrams/) - Class, Sequence, State diagrams

## Konfigurasi

Edit `config.py` untuk menyesuaikan game:

```python
GAME_WIDTH = 60       # Lebar arena
GAME_HEIGHT = 20      # Tinggi arena
PADDLE_HEIGHT = 4     # Tinggi paddle
WIN_SCORE = 5         # Skor untuk menang
FPS = 20              # Frame rate
BALL_SPEED_X = 1.5    # Kecepatan horizontal bola
BALL_SPEED_Y = 1.0    # Kecepatan vertikal bola
```

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Title tidak muncul | Install pyfiglet: `pip install pyfiglet` |
| Suara tidak berbunyi | Install ffmpeg/mpv, pastikan sfx.mp3 ada |
| Karakter aneh | Gunakan terminal dengan Unicode support |
| Input tidak responsif | Pastikan terminal dalam raw mode |

## Lisensi

MIT License - Bebas digunakan dan dimodifikasi.

## Penulis

Proyek Tugas Besar Network Programming.  
Dibuat dengan Python 3 Standard Library.
