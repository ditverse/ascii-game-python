# Panduan Pengguna

## 1. Pendahuluan

PONG-CLI adalah reimplementasi modern berbasis terminal dari permainan klasik Arcade Pong. Game ini memiliki antarmuka yang responsif, mode pemain tunggal melawan AI, dan kemampuan multipemain waktu nyata (real-time) melalui jaringan lokal.

## 2. Instalasi & Persyaratan

### 2.1 Persyaratan Sistem
- **Sistem Operasi**: Linux, macOS, atau Windows (Disarankan menggunakan Windows Terminal)
- **Perangkat Lunak**: Python 3.6 atau lebih baru
- **Jaringan**: Local Area Network (LAN) untuk fitur multipemain

### 2.2 Instruksi Instalasi
1. Clone repositori atau ekstrak kode sumber.
2. Buka terminal di dalam direktori proyek.
3. Tidak ada dependensi eksternal (`pip install`) yang diperlukan; game ini hanya menggunakan pustaka standar Python.

## 3. Cara Bermain

Jalankan permainan menggunakan perintah berikut:

```bash
python3 main.py
```

### 3.1 Menu Utama
Navigasi menu menggunakan keyboard:
- **Panah Atas/Bawah** atau **W/S**: Memindahkan pilihan
- **Enter**: Konfirmasi pilihan
- **Q**: Keluar aplikasi

### 3.2 Mode Permainan

#### VS AI (Pemain Tunggal)
Tantang komputer dalam pertandingan 1 lawan 1.
- **Pilih Tingkat Kesulitan**:
    - **Easy**: Untuk pemula. AI lambat dan sering melakukan kesalahan.
    - **Medium**: Tantangan seimbang.
    - **Hard**: Tantangan kompetitif untuk pemain ahli.

#### Host Game (Server Multipemain)
Mulai server permainan di mesin Anda.
- Pilih "Host Game".
- Masukkan nomor port (default: 5000).
- Bagikan alamat IP dan Port Anda ke teman.
- Tunggu pemain kedua bergabung.

#### Join Game (Klien Multipemain)
Hubungkan ke permainan yang di-host oleh teman.
- Pilih "Join Game".
- Masukkan Alamat IP Host.
- Masukkan Nomor Port Host.

### 3.3 Kontrol

| Aksi | Tombol 1 | Tombol 2 |
| :--- | :--- | :--- |
| **Gerak Atas** | `W` | `Panah Atas` |
| **Gerak Bawah** | `S` | `Panah Bawah` |
| **Keluar Match** | `Q` | - |

## 4. Pemecahan Masalah (Troubleshooting)

### 4.1 Gagal Terhubung
- **Firewall**: Pastikan firewall Anda mengizinkan Python untuk mengakses jaringan lokal.
- **Alamat IP**: Pastikan Anda menggunakan IP lokal yang benar dari mesin host (gunakan `ifconfig` atau `ip addr`).
- **Port**: Pastikan port tidak sedang digunakan oleh aplikasi lain.

### 4.2 Aplikasi Macet (Freeze)
- Mode input terminal terkadang bisa tidak sinkron. Jika ini terjadi, restart aplikasi.
- Gunakan `Ctrl+C` untuk menutup paksa jika tombol `Q` tidak merespon.
