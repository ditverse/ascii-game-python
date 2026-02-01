# Panduan Pengembang

## 1. Ikhtisar
Panduan ini ditujukan bagi pengembang yang ingin memodifikasi atau mengembangkan basis kode (codebase) PONG-CLI. Proyek ini dirancang dengan prinsip modularitas, sehingga mudah untuk menambahkan fitur baru atau mengubah mekanik yang sudah ada.

## 2. Kamus Modul

| File | Tanggung Jawab |
| :--- | :--- |
| **ai.py** | Mengimplementasikan kelas `AIController`. Menangani logika lawan dan tingkat kesulitan. |
| **client.py** | Mengelola soket TCP klien, mengirim input lokal, dan menerima pembaruan status permainan. |
| **colors.py** | Fungsi bantuan untuk kode warna ANSI dan pemformatan teks. |
| **config.py** | Konstanta global (ukuran layar, default jaringan, *frame rate*). |
| **game_state.py** | Satu-satunya sumber kebenaran (*single source of truth*) untuk dunia permainan. Berisi kelas `GameState`. |
| **input_handler.py** | Penangkapan input menggunakan `termios/tty` (Linux/Mac) atau `msvcrt` (Windows) dalam thread terpisah. |
| **main.py** | Titik masuk aplikasi. Menangani menu utama dan loop permainan. |
| **physics.py** | Berisi `update_physics()` yang menghitung pergerakan dan tabrakan. |
| **renderer.py** | Bertanggung jawab membersihkan layar dan menggambar frame saat ini. |
| **server.py** | Mengelola server TCP, koneksi klien, dan penyiaran (*broadcasting*) status. |
| **sound.py** | Menangani efek suara menggunakan bunyi *beep* terminal (`\a`). |

## 3. Protokol Jaringan
PONG-CLI menggunakan protokol berbasis teks sederhana melalui soket TCP. Pesan dibatasi hingga 1024 byte dan mengandalkan parsing string.

### 3.1 Struktur Paket
Pembaruan status permainan dikirim sebagai string yang dipisahkan koma:
```text
ball_x,ball_y,score1,score2,paddle1_y,paddle2_y,event
```
- **event**: Digunakan untuk pemicu suara (misal: `collision`, `goal`).

### 3.2 Input Klien
Klien mengirim karakter tunggal yang mewakili penekanan tombol:
- `W` / `S`: Gerakan Raket.
- `Q`: Sinyal Keluar (Quit).

## 4. Algoritma Utama

### 4.1 Deteksi Tabrakan
Diimplementasikan di `physics.py`. Kami menggunakan logika AABB (*Axis-Aligned Bounding Box*) sederhana:
1. **Tabrakan Dinding**: Membalikkan `ball_vy` jika bola mengenai atas/bawah (`y <= 0` atau `y >= HEIGHT`).
2. **Tabrakan Raket**: Memeriksa apakah koordinat bola tumpang tindih dengan koordinat raket. Membalikkan `ball_vx` dan sedikit meningkatkan kecepatan.

### 4.2 Logika AI
Diimplementasikan di `ai.py` menggunakan algoritma prediktif:
1. **Pemeriksaan Reaksi**: Acak (*random roll*) terhadap `reaction_chance` menentukan apakah AI memperbarui strateginya pada frame ini.
2. **Prediksi Lintasan**: Jika bola bergerak ke arah AI, ia menghitung titik potong dengan garis raket.
3. **Injeksi Kesalahan**: Offset acak `prediction_error` ditambahkan untuk mensimulasikan ketidaksempurnaan manusia, disesuaikan dengan tingkat kesulitan.

## 5. Panduan Ekstensi

### Menambahkan Fitur Baru
1. **Game State**: Tambahkan field baru ke `GameState.__init__` dan `reset`.
2. **Physics**: Perbarui `update_physics` untuk menangani logika baru.
3. **Rendering**: Perbarui `renderer.py` untuk menggambar elemen baru.
4. **Networking**: Pastikan variabel status baru diserialisasi di `server.py` dan diparsing di `client.py` jika perlu disinkronkan.
