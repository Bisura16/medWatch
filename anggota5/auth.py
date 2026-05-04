"""
Modul Autentikasi Desktop MedWatch
Login CLI dengan role-based access control.
Roles: admin, tenaga_kesehatan
"""
import json
import os


def verifikasi_login():
    """
    Login user via CLI prompt. Cocokin username dan password ke users.json.
    Return tuple (status_login, username, role).
    Kalau gagal, return (False, None, None).
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    path_users = os.path.join(base_path, "data", "users.json")

    print("\n=== LOGIN SISTEM MEDWATCH ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    try:
        with open(path_users, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['username'] == username and user['password'] == password:
                    role = user.get('role', 'tenaga_kesehatan')
                    return True, user['username'], role
    except FileNotFoundError:
        print("[!] File users.json tidak ditemukan di folder data.")

    return False, None, None


def hanya_admin(role):
    """
    Return True kalau role-nya admin. Kalau bukan, print error dan return False.
    Pakai sebelum jalanin fitur yang cuma admin yang boleh
    (misal: scraper trigger, CRUD akun tenaga kesehatan).
    """
    if role != "admin":
        print("[!] Akses ditolak. Fitur ini hanya untuk admin.")
        return False
    return True


def hanya_tkesehatan_atau_admin(role):
    """
    Return True kalau role-nya tenaga_kesehatan atau admin.
    Pakai sebelum jalanin fitur CRUD pasien.
    Admin tetap bisa karena admin punya akses semua.
    """
    if role not in ("tenaga_kesehatan", "admin"):
        print("[!] Akses ditolak.")
        return False
    return True


if __name__ == "__main__":
    status, user, role = verifikasi_login()
    if status:
        print(f"Tes Berhasil. Login sebagai: {user} (role: {role})")
    else:
        print("Tes Gagal. Akun tidak ditemukan.")
