"""End-to-end smoke test for the MedWatch API.

Exercises every public route (health, three-role login, auth
negatives, patient create + fetch, drug search, safety check, the
four visualization endpoints, role enforcement, password leak
guard). Designed to be run against either the local Flask server
or a live Cloud Run revision so the same script doubles as a
deployment gate.

Usage::

    BASE_URL=http://localhost:8080 python api/tests/smoke_test.py
    BASE_URL=https://medwatch-api-xxx.run.app python api/tests/smoke_test.py
"""
import os
import sys
import requests

BASE = os.environ.get("BASE_URL", "http://localhost:8080")


def _login(username, password):
    """Authenticate and return the issued bearer token.

    Raises ``AssertionError`` when the login response is not HTTP
    200 so the caller test surfaces a clear failure path.
    """
    r = requests.post(f"{BASE}/api/auth/login", json={"username": username, "password": password}, timeout=15)
    assert r.status_code == 200, f"login failed for {username}: {r.status_code} {r.text}"
    return r.json()["token"]


def test_health():
    """Liveness probe: ``/api/health`` must return HTTP 200."""
    r = requests.get(f"{BASE}/api/health", timeout=10)
    assert r.status_code == 200, f"/api/health returned {r.status_code}"
    print("OK /api/health")


def test_login_three_roles():
    """Verify each seeded credential resolves to its expected role."""
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
    """Wrong password, unknown user, and missing token must all return 401."""
    r = requests.post(f"{BASE}/api/auth/login", json={"username": "bidan_siti", "password": "wrong"}, timeout=15)
    assert r.status_code == 401, f"wrong-password should 401, got {r.status_code}"
    r = requests.post(f"{BASE}/api/auth/login", json={"username": "no_such_user", "password": "x"}, timeout=15)
    assert r.status_code == 401, f"unknown-user should 401, got {r.status_code}"
    r = requests.get(f"{BASE}/api/auth/me", timeout=15)
    assert r.status_code == 401, f"missing-token should 401, got {r.status_code}"
    print("OK auth negatives all 401")


def test_patients_crud():
    """Create and re-fetch a patient using the canonical reference record."""
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
    """Confirm ``paracetamol`` returns at least one match."""
    r = requests.get(f"{BASE}/api/drugs/search?q=paracetamol", timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body, list)
    assert len(body) >= 1, "expected at least one paracetamol match"
    print("OK /api/drugs/search?q=paracetamol")


def test_safety_check():
    """Run the safety checker on a known overlap pair and assert envelope shape."""
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
    """All four visualization endpoints must return HTTP 200 for an authed bidan."""
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
    """Bidan must be blocked from admin routes; admin must see no password fields."""
    bidan = _login("bidan_siti", "siti2026")
    r = requests.get(f"{BASE}/api/admin/users", headers={"Authorization": f"Bearer {bidan}"}, timeout=15)
    assert r.status_code == 403, f"bidan on /api/admin/users should 403, got {r.status_code}"

    admin = _login("admin_ghaisan", "admin2026")
    r = requests.get(f"{BASE}/api/admin/users", headers={"Authorization": f"Bearer {admin}"}, timeout=15)
    assert r.status_code == 200, f"admin on /api/admin/users should 200, got {r.status_code} {r.text}"
    users = r.json()
    assert all("password_hash" not in u and "password_plain" not in u for u in users), "passwords must not leak"
    print("OK role-based access enforced and passwords not leaked")


def test_safety_check_masyarakat_no_pii_leak():
    """H07-1: masyarakat must not receive another patient's PII.

    Login as the demo masyarakat user, call /api/safety/check with a
    pasien_id that is NOT owned by that user, and assert the response
    omits pasien_context (None) and pasien_active_meds (empty list).
    Bidan and admin must keep the existing behaviour: pasien_context
    and pasien_active_meds populated for the same pasien_id.
    """
    masy = _login("umum_budi", "budi2026")
    r = requests.post(
        f"{BASE}/api/safety/check",
        json={"drugs": ["paracetamol"], "pasien_id": "P001"},
        headers={"Authorization": f"Bearer {masy}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("pasien_context") is None, (
        f"H07-1 leak: masyarakat received pasien_context={body.get('pasien_context')}"
    )
    assert body.get("pasien_active_meds") == [], (
        f"H07-1 leak: masyarakat received pasien_active_meds={body.get('pasien_active_meds')}"
    )
    print("OK /api/safety/check pasien_context hidden from masyarakat (H07-1)")

    bidan = _login("bidan_siti", "siti2026")
    r = requests.post(
        f"{BASE}/api/safety/check",
        json={"drugs": ["paracetamol"], "pasien_id": "P001"},
        headers={"Authorization": f"Bearer {bidan}"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("pasien_context") is not None, "bidan must still receive pasien_context"
    assert body["pasien_context"].get("id") == "P001"
    assert isinstance(body.get("pasien_active_meds"), list)
    print("OK /api/safety/check pasien_context retained for bidan (H07-1 baseline preserved)")


def main():
    """Run the full smoke suite in order; print a summary line at the end."""
    print(f"smoke testing {BASE}\n")
    test_health()
    test_login_three_roles()
    test_login_invalid()
    test_patients_crud()
    test_drug_search()
    test_safety_check()
    test_visualizations()
    test_role_enforcement()
    test_safety_check_masyarakat_no_pii_leak()
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
