import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "uts-lab-pemrograman"  # dipakai untuk pesan flash, ganti kalau aplikasi dipasang online

# File database ada di sebelah app.py, jadi data tetap ada walau aplikasi dimatikan.
DB_PATH = Path(__file__).with_name("mahasiswa.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # supaya kolom bisa dipanggil pakai nama, misal row["nama"]
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nim           INTEGER NOT NULL UNIQUE,
                nama          TEXT    NOT NULL,
                program_studi TEXT    NOT NULL,
                angkatan      INTEGER NOT NULL,
                ipk           REAL    NOT NULL
            )
        """)


def lama_studi(angkatan):
    # Dihitung program setiap halaman dibuka, tidak disimpan di database.
    return date.today().year - angkatan


def cari_mahasiswa(id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM mahasiswa WHERE id = ?", (id,)).fetchone()


def validasi(form):
    """Cek isi form. Hasilnya (data_bersih, daftar_pesan_error)."""
    errors = []
    tahun_ini = date.today().year
    nim = form.get("nim", "").strip()
    nama = form.get("nama", "").strip()
    program_studi = form.get("program_studi", "").strip()
    angkatan = form.get("angkatan", "").strip()
    ipk = form.get("ipk", "").strip().replace(",", ".")  # "3,5" juga diterima

    if not nim:
        errors.append("NIM wajib diisi.")
    elif not nim.isdigit():
        errors.append("NIM hanya boleh berisi angka.")

    if not nama:
        errors.append("Nama wajib diisi.")

    if not program_studi:
        errors.append("Program studi wajib diisi.")

    if not angkatan:
        errors.append("Angkatan wajib diisi.")
    elif not angkatan.isdigit() or not 1950 <= int(angkatan) <= tahun_ini:
        errors.append(f"Angkatan harus berupa tahun antara 1950 dan {tahun_ini}.")

    if not ipk:
        errors.append("IPK wajib diisi.")
    else:
        try:
            nilai_ipk = float(ipk)
        except ValueError:
            nilai_ipk = None
        if nilai_ipk is None or not 0 <= nilai_ipk <= 4:
            errors.append("IPK harus angka di antara 0.00 dan 4.00.")

    if errors:
        return None, errors
    data = {
        "nim": int(nim),
        "nama": nama,
        "program_studi": program_studi,
        "angkatan": int(angkatan),
        "ipk": round(nilai_ipk, 2),
    }
    return data, []


# READ: daftar semua mahasiswa
@app.route("/")
def index():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM mahasiswa ORDER BY nim").fetchall()
    mahasiswa = [dict(row, lama_studi=lama_studi(row["angkatan"])) for row in rows]
    rata_ipk = sum(m["ipk"] for m in mahasiswa) / len(mahasiswa) if mahasiswa else None
    return render_template("index.html", mahasiswa=mahasiswa, rata_ipk=rata_ipk)


# CREATE: tambah mahasiswa baru
@app.route("/tambah", methods=["GET", "POST"])
def tambah():
    if request.method == "GET":
        return render_template("form.html", mode="tambah", form={}, errors=[])

    data, errors = validasi(request.form)
    if not errors:
        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk) "
                    "VALUES (:nim, :nama, :program_studi, :angkatan, :ipk)",
                    data,
                )
            flash(f"{data['nama']} berhasil ditambahkan.")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:  # kolom nim UNIQUE, jadi NIM kembar ditolak database
            errors.append(f"NIM {data['nim']} sudah terdaftar.")
    return render_template("form.html", mode="tambah", form=request.form, errors=errors), 400


# READ: detail satu mahasiswa
@app.route("/mahasiswa/<int:id>")
def detail(id):
    m = cari_mahasiswa(id)
    if m is None:
        flash("Data mahasiswa tidak ditemukan.")
        return redirect(url_for("index"))
    return render_template("detail.html", m=m, lama_studi=lama_studi(m["angkatan"]), tahun_ini=date.today().year)


# UPDATE: ubah data mahasiswa
@app.route("/mahasiswa/<int:id>/ubah", methods=["GET", "POST"])
def ubah(id):
    m = cari_mahasiswa(id)
    if m is None:
        flash("Data mahasiswa tidak ditemukan.")
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("form.html", mode="ubah", form=dict(m), errors=[])

    data, errors = validasi(request.form)
    if not errors:
        try:
            with get_db() as conn:
                conn.execute(
                    "UPDATE mahasiswa SET nim = :nim, nama = :nama, program_studi = :program_studi, "
                    "angkatan = :angkatan, ipk = :ipk WHERE id = :id",
                    {**data, "id": id},
                )
            flash(f"Data {data['nama']} berhasil diperbarui.")
            return redirect(url_for("detail", id=id))
        except sqlite3.IntegrityError:
            errors.append(f"NIM {data['nim']} sudah dipakai mahasiswa lain.")
    return render_template("form.html", mode="ubah", form=request.form, errors=errors), 400


# DELETE: hapus mahasiswa
@app.route("/mahasiswa/<int:id>/hapus", methods=["POST"])
def hapus(id):
    m = cari_mahasiswa(id)
    if m is None:
        flash("Data mahasiswa tidak ditemukan.")
    else:
        with get_db() as conn:
            conn.execute("DELETE FROM mahasiswa WHERE id = ?", (id,))
        flash(f"{m['nama']} sudah dihapus.")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
