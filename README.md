# Data Mahasiswa

Aplikasi web untuk mencatat data mahasiswa program studi, pengganti spreadsheet. Dibuat untuk UTS Lab Pemrograman 2026/2027 Gasal, Departemen Bisnis Digital, Universitas Diponegoro.

- Nama: Achmad Habibie
- NIM: 12010223140051

## Fitur

| Fitur | Halaman |
|---|---|
| Tambah mahasiswa (Create) | tombol **Tambah mahasiswa** |
| Daftar semua mahasiswa dalam tabel (Read) | halaman utama `/` |
| Detail satu mahasiswa (Read) | klik nama di tabel |
| Ubah data (Update) | tombol **Ubah** |
| Hapus data (Delete) | tombol **Hapus**, ada konfirmasi dulu |

Aturan yang dicek server:

- NIM, nama, dan program studi wajib diisi. Kalau kosong, data ditolak dan muncul pesan kesalahan.
- IPK harus di antara 0.00 dan 4.00.
- NIM tidak boleh kembar. Kolom `nim` di database memakai `UNIQUE`, jadi NIM yang sudah terdaftar ditolak.
- Lama studi dihitung program dengan rumus `tahun sekarang - angkatan`. Pengguna tidak mengisinya.
- Data disimpan di file SQLite `mahasiswa.db`, jadi tetap ada setelah aplikasi dimatikan lalu dijalankan lagi.

## Teknologi

- Python 3 + Flask (backend)
- SQLite lewat modul `sqlite3` bawaan Python (database)
- HTML + CSS dengan template Jinja (frontend)

## Cara menjalankan

1. Pastikan Python 3 sudah terpasang.
2. Buka terminal di folder ini, lalu pasang Flask:

   ```
   pip install -r requirements.txt
   ```

3. Jalankan aplikasi:

   ```
   python app.py
   ```

4. Buka `http://127.0.0.1:5000` di browser.

File `mahasiswa.db` dibuat otomatis saat aplikasi pertama kali jalan.

## Struktur folder

```
app.py              backend: koneksi database, validasi, dan semua route CRUD
requirements.txt    daftar library Python yang dipakai
templates/
  base.html         kerangka halaman (header, pesan, footer)
  index.html        tabel daftar mahasiswa
  form.html         form tambah dan ubah
  detail.html       detail satu mahasiswa
static/
  style.css         tampilan
```

## Route

| Method | URL | Fungsi |
|---|---|---|
| GET | `/` | daftar mahasiswa |
| GET, POST | `/tambah` | form tambah dan simpan data baru |
| GET | `/mahasiswa/<id>` | detail mahasiswa |
| GET, POST | `/mahasiswa/<id>/ubah` | form ubah dan simpan perubahan |
| POST | `/mahasiswa/<id>/hapus` | hapus mahasiswa |
