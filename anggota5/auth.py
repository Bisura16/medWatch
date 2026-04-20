import json
import os

def verifikasi_login():
    # Cari path users.json
    base_path = os.path.dirname(os.path.abspath(__file__))
    path_users = os.path.join(base_path, "data", "users.json")

    print("\n=== LOGIN SISTEM MEDWATCH ===")
    username = input("Username: ")
    password = input("Password: ")

    try:
        with open(path_users, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['username'] == username and user['password'] == password:
                    return True, user['username']
    except FileNotFoundError:
        print("[!] File users.json tidak ditemukan di folder data.")
    
    return False, None

if __name__ == "__main__":
    status, user = verifikasi_login()
    if status:
        print(f"Tes Berhasil! Login sebagai: {user}")
    else:
        print("Tes Gagal! Akun tidak ditemukan.")