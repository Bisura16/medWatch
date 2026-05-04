"""
Modul CRUD Tenaga Kesehatan
Cuma admin yang boleh akses fungsi-fungsi di sini.
Semua fungsi dijalankan dari menu admin di main_anggota5.py.
"""
import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_USERS = os.path.join(BASE_PATH, "data", "users.json")


def baca_users():
    """Load semua user dari users.json. Return list, atau list kosong kalau file gak ada."""
    if not os.path.exists(PATH_USERS):
        return []
    with open(PATH_USERS, 'r') as f:
        return json.load(f)


def simpan_users(users):
    """Tulis ulang seluruh users.json."""
    with open(PATH_USERS, 'w') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def generate_username(nama):
    """Auto-generate username dari nama: lowercase, tanpa spasi, tanpa gelar."""
    nama_bersih = nama.lower().replace("dr.", "").replace("bidan", "").strip()
    return nama_bersih.replace(" ", "")


def generate_password(nama, telepon):
    """Auto-generate password: nama_depan + 4 digit terakhir telepon."""
    nama_depan = nama.split()[0].lower().replace("dr.", "").replace("bidan", "").strip()
    if not nama_depan:
        nama_depan = "user"
    digit_telepon = telepon[-4:] if len(telepon) >= 4 else "0000"
    return f"{nama_depan}{digit_telepon}"


def tambah_tkesehatan():
    """Admin tambah akun tenaga kesehatan baru. Username dan password auto-generate."""
    print("\n=== TAMBAH TENAGA KESEHATAN ===")
    nama = input("Nama lengkap: ").strip()
    if not nama:
        print("[!] Nama tidak boleh kosong.")
        return

    telepon = input("Nomor telepon: ").strip()

    username = generate_username(nama)
    password = generate_password(nama, telepon)

    users = baca_users()

    base_username = username
    counter = 1
    while any(u['username'] == username for u in users):
        username = f"{base_username}{counter}"
        counter += 1

    user_baru = {
        "username": username,
        "password": password,
        "role": "tenaga_kesehatan",
        "name": nama,
    }
    users.append(user_baru)
    simpan_users(users)

    print(f"\n[OK] Akun berhasil dibuat.")
    print(f"     Username : {username}")
    print(f"     Password : {password}")
    print(f"     Nama     : {nama}")
    print(f"     Role     : tenaga_kesehatan")


def lihat_tkesehatan():
    """Tampilkan semua akun tenaga kesehatan dalam tabel sederhana."""
    users = baca_users()
    tkesehatan = [u for u in users if u.get('role') == "tenaga_kesehatan"]

    if not tkesehatan:
        print("\n[!] Belum ada tenaga kesehatan terdaftar.")
        return

    print("\n=== DAFTAR TENAGA KESEHATAN ===")
    print(f"{'No':<4}{'Username':<20}{'Nama':<30}")
    print("-" * 54)
    for i, u in enumerate(tkesehatan, start=1):
        print(f"{i:<4}{u['username']:<20}{u.get('name', '-'):<30}")


def edit_tkesehatan():
    """Admin edit akun tenaga kesehatan (ubah nama atau reset password)."""
    lihat_tkesehatan()
    username = input("\nUsername yang mau diedit: ").strip()
    if not username:
        return

    users = baca_users()
    target = None
    for u in users:
        if u['username'] == username and u.get('role') == "tenaga_kesehatan":
            target = u
            break

    if not target:
        print(f"[!] Tenaga kesehatan dengan username '{username}' tidak ditemukan.")
        return

    print(f"\nEdit akun {target['username']} (kosongin kalau gak mau ubah):")
    nama_baru = input(f"Nama baru [{target.get('name', '')}]: ").strip()
    password_baru = input("Password baru (kosongin kalau gak ganti): ").strip()

    if nama_baru:
        target['name'] = nama_baru
    if password_baru:
        target['password'] = password_baru

    simpan_users(users)
    print(f"[OK] Akun {target['username']} berhasil diupdate.")


def hapus_tkesehatan():
    """Admin hapus akun tenaga kesehatan."""
    lihat_tkesehatan()
    username = input("\nUsername yang mau dihapus: ").strip()
    if not username:
        return

    konfirmasi = input(f"Yakin hapus '{username}'? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Dibatalkan.")
        return

    users = baca_users()
    users_baru = [u for u in users if not (u['username'] == username and u.get('role') == "tenaga_kesehatan")]

    if len(users_baru) == len(users):
        print(f"[!] Tenaga kesehatan dengan username '{username}' tidak ditemukan.")
        return

    simpan_users(users_baru)
    print(f"[OK] Akun '{username}' berhasil dihapus.")


def menu_tkesehatan_crud():
    """Menu CRUD tenaga kesehatan untuk admin."""
    while True:
        print("\n" + "=" * 50)
        print("   MENU CRUD TENAGA KESEHATAN (ADMIN)")
        print("=" * 50)
        print("  [1] Tambah Tenaga Kesehatan")
        print("  [2] Lihat Daftar Tenaga Kesehatan")
        print("  [3] Edit Data Tenaga Kesehatan")
        print("  [4] Hapus Tenaga Kesehatan")
        print("  [0] Kembali ke menu utama")
        print("-" * 50)

        pilihan = input("Pilih menu: ").strip()
        if pilihan == "1":
            tambah_tkesehatan()
        elif pilihan == "2":
            lihat_tkesehatan()
        elif pilihan == "3":
            edit_tkesehatan()
        elif pilihan == "4":
            hapus_tkesehatan()
        elif pilihan == "0":
            break
        else:
            print("[!] Pilihan tidak valid.")


if __name__ == "__main__":
    menu_tkesehatan_crud()
