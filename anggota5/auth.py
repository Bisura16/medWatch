import json
import os

<<<<<<< HEAD
def verifikasi_login():
    # Cari path users.json
    base_path = os.path.dirname(os.path.abspath(__file__))
    path_users = os.path.join(base_path, "data", "users.json")

=======
def get_path_users():
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Menyesuaikan dengan folder data di root proyek
    return os.path.join(base_path, "data", "users.json")

def verifikasi_login():
    path_users = get_path_users()
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
    print("\n=== LOGIN SISTEM MEDWATCH ===")
    username = input("Username: ")
    password = input("Password: ")

    try:
<<<<<<< HEAD
=======
        if not os.path.exists(path_users):
            return False, None, None, None
            
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
        with open(path_users, 'r') as f:
            users = json.load(f)
            for user in users:
                if user['username'] == username and user['password'] == password:
<<<<<<< HEAD
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
=======
                    return True, user['username'], user.get('role', 'pasien'), user.get('id_faskes', 'PUBLIC')
    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")
    
    return False, None, None, None

def registrasi_akun():
    path_users = get_path_users()
    users = []
    if os.path.exists(path_users):
        with open(path_users, 'r') as f:
            users = json.load(f)

    print("\n=== PENDAFTARAN AKUN BARU ===")
    print("1. Pasien (Masyarakat Umum)\n2. Dokter\n3. Admin Faskes")
    pilihan = input("Pilih peran (1/2/3): ").strip()

    username = input("Username Baru: ").strip()
    if any(u['username'] == username for u in users):
        print("[!] Username sudah ada.")
        return

    password = input("Password Baru: ").strip()
    user_baru = {"username": username, "password": password}

    if pilihan == "1":
        user_baru.update({"role": "pasien", "id_faskes": "PUBLIC"})
    elif pilihan == "2":
        user_baru.update({
            "role": "dokter",
            "no_str": input("Nomor STR: ").strip(),
            "id_faskes": input("ID Faskes Klinik: ").strip()
        })
    elif pilihan == "3":
        total_f = len([u for u in users if u.get('role') == 'admin faskes'])
        new_id = f"FASKES_{str(total_f + 1).zfill(3)}"
        user_baru.update({
            "role": "admin faskes",
            "nama_faskes": input("Nama Klinik: ").strip(),
            "id_faskes": new_id
        })
        print(f"\n[!] ID Faskes Baru: {new_id} (Berikan ke dokter Anda)")
    
    users.append(user_baru)
    with open(path_users, 'w') as f:
        json.dump(users, f, indent=4)
    print("[✓] Registrasi Berhasil.")
>>>>>>> 93c21ad (Mencoba sistem login sesuai dengan role)
