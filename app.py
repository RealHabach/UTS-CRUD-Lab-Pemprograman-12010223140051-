import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, render_template

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


# READ: daftar semua mahasiswa
@app.route("/")
def index():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM mahasiswa ORDER BY nim").fetchall()
    mahasiswa = [dict(row, lama_studi=lama_studi(row["angkatan"])) for row in rows]
    rata_ipk = sum(m["ipk"] for m in mahasiswa) / len(mahasiswa) if mahasiswa else None
    return render_template("index.html", mahasiswa=mahasiswa, rata_ipk=rata_ipk)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
