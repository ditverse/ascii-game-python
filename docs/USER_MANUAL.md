# Panduan Pengguna (User Manual)

## Daftar Isi
1. [Instalasi](#instalasi)
2. [Menjalankan Game](#menjalankan-game)
3. [Mode Permainan](#mode-permainan)
4. [Kontrol](#kontrol)
5. [Power-ups](#power-ups)
6. [Efek Visual](#efek-visual)
7. [Sound Effects](#sound-effects)
8. [Troubleshooting](#troubleshooting)

---

## Instalasi

### Persyaratan Sistem
- Python 3.6 atau lebih baru
- Terminal dengan dukungan ANSI colors
- (Opsional) pyfiglet untuk ASCII art title
- (Opsional) ffmpeg/mpv untuk sound effects

### Langkah Instalasi

```bash
# 1. Clone repository
git clone https://github.com/username/pong-cli.git
cd pong-cli

# 2. Install dependensi (opsional tapi disarankan)
# Arch Linux / CachyOS
sudo pacman -S python-pyfiglet ffmpeg

# Ubuntu/Debian
pip install pyfiglet
sudo apt install ffmpeg
```

---

## Menjalankan Game

```bash
python3 main.py
```

### Navigasi Menu
- `W` atau `↑` - Pilihan ke atas
- `S` atau `↓` - Pilihan ke bawah
- `Enter` - Pilih/Konfirmasi
- `Q` - Keluar

---

## Mode Permainan

### 1. VS AI (Single Player)

Bermain melawan komputer dengan 3 tingkat kesulitan:

| Difficulty | Deskripsi |
|------------|-----------|
| **Easy** | AI lambat dan sering meleset. Cocok untuk pemula. |
| **Medium** | Tantangan seimbang. AI cukup responsif. |
| **Hard** | AI sangat cepat dan akurat. Tantangan maksimal. |

**Cara Bermain:**
1. Pilih "VS AI" dari menu utama
2. Pilih tingkat kesulitan
3. Game dimulai otomatis

### 2. Host Game (Multiplayer - Server)

Menjadi host server untuk pemain lain bergabung.

**Cara Bermain:**
1. Pilih "Host Game" dari menu utama
2. Port default: 5555 (atau masukkan port lain)
3. Tunggu pemain lain bergabung di lobby
4. Tekan `TAB` untuk memulai game

### 3. Join Game (Multiplayer - Client)

Bergabung ke game yang di-host oleh pemain lain.

**Cara Bermain:**
1. Pilih "Join Game" dari menu utama
2. Masukkan IP Address host (contoh: 192.168.1.100)
3. Masukkan port (default: 5555)
4. Tunggu di lobby sampai host memulai game

---

## Kontrol

### Menu
| Tombol | Aksi |
|--------|------|
| `W` / `↑` | Navigasi ke atas |
| `S` / `↓` | Navigasi ke bawah |
| `Enter` | Pilih opsi |
| `Q` | Keluar |

### Dalam Game
| Tombol | Aksi |
|--------|------|
| `W` / `↑` | Paddle ke atas |
| `S` / `↓` | Paddle ke bawah |
| `Q` | Keluar dari game |

### Lobby (Multiplayer)
| Tombol | Aksi |
|--------|------|
| `TAB` | Mulai game (hanya host) |
| `Q` | Keluar dari lobby |
| Ketik + `Enter` | Kirim chat |

---

## Power-ups

Power-ups adalah item yang muncul secara acak di arena dan memberikan efek sementara.

### Daftar Power-ups
| Simbol | Nama | Efek | Durasi |
|--------|------|------|--------|
| **S** (kuning) | Speed+ | Mempercepat bola 1.5x | 5 detik |
| **+** (kuning) | Paddle+ | Memperbesar paddle Anda | 5 detik |
| **-** (kuning) | Paddle- | Memperkecil paddle lawan | 5 detik |

### Cara Kerja
1. Power-up spawn setiap 10 detik di posisi random
2. Maksimal 2 power-up di arena sekaligus
3. Power-up diambil saat bola menyentuhnya
4. Pemain yang mendapat efek ditentukan oleh arah bola:
   - Bola bergerak ke kanan → Player 1
   - Bola bergerak ke kiri → Player 2/AI

---

## Efek Visual

### Ball Trail
Jejak bola yang memudar saat bergerak, memberikan kesan kecepatan.

### Goal Explosion
Animasi ledakan (★) saat gol dicetak.

### Paddle Hit Flash
Efek kilat saat bola memukul paddle.

### Ball Warning
Bola berubah warna **merah** saat mendekati gol.

---

## Sound Effects

Game menggunakan file `sfx.mp3` untuk efek suara collision.

### Persyaratan
- File `sfx.mp3` harus ada di folder game
- Audio player: ffplay, mpv, atau paplay

### Mengaktifkan/Menonaktifkan
Sound aktif secara default. Untuk menonaktifkan, edit `sound.py`:
```python
SOUND_ENABLED = False
```

---

## Troubleshooting

### Title Tidak Muncul / Tampilan Aneh
**Masalah:** Pyfiglet tidak terinstall  
**Solusi:**
```bash
# Arch Linux
sudo pacman -S python-pyfiglet

# Pip
pip install pyfiglet
```

### Suara Tidak Berbunyi
**Masalah:** Audio player tidak ditemukan  
**Solusi:**
```bash
# Arch Linux
sudo pacman -S ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

### Karakter Kotak/Aneh
**Masalah:** Terminal tidak mendukung Unicode  
**Solusi:** Gunakan terminal modern seperti:
- Konsole
- GNOME Terminal
- Windows Terminal
- Kitty

### Input Tidak Responsif
**Masalah:** Terminal tidak dalam raw mode  
**Solusi:** Pastikan menjalankan langsung di terminal, bukan di IDE

### Koneksi Multiplayer Gagal
**Masalah:** Firewall atau port tertutup  
**Solusi:**
1. Pastikan host dan client di jaringan yang sama
2. Buka port 5555 di firewall:
   ```bash
   sudo ufw allow 5555
   ```
3. Cek IP address host dengan `ip addr` atau `hostname -I`

---

## Tips Bermain

1. **Antisipasi** - Prediksi arah bola dan posisikan paddle lebih awal
2. **Gunakan Power-ups** - Ambil power-up saat bola mengarah ke arah yang menguntungkan
3. **Perhatikan Warna Bola** - Bola merah berarti hampir gol!
4. **Latihan vs AI Easy** - Mulai dari Easy untuk memahami mekanik game
5. **Komunikasi** - Di multiplayer, gunakan fitur chat untuk koordinasi

---

*Selamat bermain!* 🎮
