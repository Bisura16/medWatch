"""End-to-end smoke test. Run after server is up:
    BASE_URL=http://localhost:8080 python api/tests/smoke_test.py
or against deployed Cloud Run:
    BASE_URL=https://medwatch-api-xxx.run.app python api/tests/smoke_test.py
"""
import os
import sys
import requests

BASE = os.environ.get("BASE_URL", "http://localhost:8080")


def _login(username, password):
    r = requests.post(f"{BASE}/api/auth/login", json={"username": username, "password": password}, timeout=15)
    assert r.status_code == 200, f"login failed for {username}: {r.status_code} {r.text}"
    return r.json()["token"]


def test_health():
    r = requests.get(f"{BASE}/api/health", timeout=10)
    assert r.status_code == 200, f"/api/health returned {r.status_code}"
    print("OK /api/health")


def test_login_three_roles():
    for u, p, expected_role in [
        ("bidan_siti", "siti2026", "tenaga_kesehatan"),
        ("umum_budi", "budi2026", "masyarakat"),
        ("admin_ghaisan", "admin2026", "admin"),
    ]:
        r = requests.post(f"{BASE}/api/auth/login", json={"username": u, "password": p}, timeout=15)
        assert r.status_code == 200, f"login {u}: {r.text}"
        assert r.json()["user"]["role"] == expected_role
        print(f"OK login {u} as {expected_role}")


def test_login_invalid():
    r = requests.post(f"{BASE}/api/auth/login", json={"username": "bidan_siti", "password": "wrong"}, timeout=15)
    assert r.status_code == 401, f"wrong-password should 401, got {r.status_code}"
    r = requests.post(f"{BASE}/api/auth/login", json={"username": "no_such_user", "password": "x"}, timeout=15)
    assert r.status_code == 401, f"unknown-user should 401, got {r.status_code}"
    r = requests.get(f"{BASE}/api/auth/me", timeout=15)
    assert r.status_code == 401, f"missing-token should 401, got {r.status_code}"
    print("OK auth negatives all 401")


def test_patients_crud():
    token = _login("bidan_siti", "siti2026")
    headers = {"Authorization": f"Bearer {token}"}

    new_patient = {
        "tanggal_kunjungan": "28-02-2026",
        "nama": "Ny. Dewi",
        "umur": "25",
        "alamat": "Kp. Selang Cau",
        "kategori": "Ibu Hamil",
        "S": {
            "keluhan": "mengeluh mual, muntah, pusing, telat mens 1 bln mens terakhir tgl 25 Januari 2026",
            "riwayat": "",
        },
        "O": {
            "tekanan_darah": "110/70",
            "nadi": "",
            "suhu_c": "",
            "respirasi": "",
            "bb_kg": "50",
            "tb_cm": "150",
            "lila_cm": "23",
            "catatan": "tespek positif",
        },
        "A": {"diagnosa": "G1P0A0 hamil 5 mg"},
        "P": {
            "tindakan": "Istirahat cukup\nMakan sedikit tapi sering",
            "resep": "Asam folat 1x1 sehari",
            "jadwal_kontrol": "",
        },
    }
    r = requests.post(f"{BASE}/api/patients", json=new_patient, headers=headers, timeout=15)
    assert r.status_code == 201, f"create: {r.status_code} {r.text}"
    pid = r.json()["id"]
    assert pid.startswith("P") and len(pid) == 4, f"id format: {pid}"
    print(f"OK POST /api/patients -> {pid}")

    r = requests.get(f"{BASE}/api/patients/{pid}", headers=headers, timeout=15)
    assert r.status_code == 200, r.text
    assert r.json()["nama"] == "Ny. Dewi"
    assert r.json()["A"]["diagnosa"] == "G1P0A0 hamil 5 mg"
    print(f"OK GET /api/patients/{pid}")


def test_drug_search():
    r = requests.get(f"{BASE}/api/drugs/search?q=paracetamol", timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 1, "expected at least one paracetamol match"
    print("OK /api/drugs/search?q=paracetamol")


def test_safety_check():
    token = _login("bidan_siti", "siti2026")
    r = requests.post(
        f"{BASE}/api/safety/check",
        json={"drugs": ["paracetamol", "ibuprofen"]},
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "severity_score" in body
    assert "severity_level" in body
    assert body["severity_level"] in ("low", "medium", "high")
    print(f"OK /api/safety/check -> severity={body['severity_level']} score={body['severity_score']}")


def test_visualizations():
    token = _login("bidan_siti", "siti2026")
    headers = {"Authorization": f"Bearer {token}"}
    for path in [
        "/api/visualizations/kunjungan-trend",
        "/api/visualizations/keluhan-distribution",
        "/api/visualizations/top-efek-samping",
        "/api/visualizations/heatmap-efek",
    ]:
        r = requests.get(f"{BASE}{path}", headers=headers, timeout=15)
        assert r.status_code == 200, f"{path}: {r.status_code} {r.text}"
        print(f"OK {path}")


def test_role_enforcement():
    bidan = _login("bidan_siti", "siti2026")
    r = requests.get(f"{BASE}/api/admin/users", headers={"Authorization": f"Bearer {bidan}"}, timeout=15)
    assert r.status_code == 403, f"bidan on /api/admin/users should 403, got {r.status_code}"

    admin = _login("admin_ghaisan", "admin2026")
    r = requests.get(f"{BASE}/api/admin/users", headers={"Authorization": f"Bearer {admin}"}, timeout=15)
    assert r.status_code == 200, f"admin on /api/admin/users should 200, got {r.status_code} {r.text}"
    users = r.json()
    assert all("password_hash" not in u and "password_plain" not in u for u in users), "passwords must not leak"
    print("OK role-based access enforced and passwords not leaked")


def main():
    print(f"smoke testing {BASE}\n")
    test_health()
    test_login_three_roles()
    test_login_invalid()
    test_patients_crud()
    test_drug_search()
    test_safety_check()
    test_visualizations()
    test_role_enforcement()
    print("\ndone all smoke tests passed")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\nFAIL: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\nNETWORK ERROR: {e}", file=sys.stderr)
        sys.exit(2)
