"""
pencarian_obat.py
=================
Fitur 1 anggota 4:
Pencarian obat dan penyusunan profil keamanan lengkap.
"""

from typing import Dict, List

from data_loader import ambil_obat_terbaik, cari_obat_dalam_database
from safety_checker import cross_reference_efek_obat


def cari_obat(kata_kunci: str) -> Dict:
    """Cari obat dan bungkus hasilnya agar mudah diformat oleh layer output."""
    hasil = cari_obat_dalam_database(kata_kunci)
    return {
        "kata_kunci": kata_kunci,
        "jumlah_hasil": len(hasil),
        "hasil": hasil,
    }


def ambil_profil_keamanan_lengkap(nama_obat: str) -> Dict:
    """
    Ambil satu profil obat yang paling relevan lalu lengkapi dengan hasil
    cross-reference efek samping.
    """
    obat = ambil_obat_terbaik(nama_obat)
    if not obat:
        return {
            "status": "not_found",
            "nama_input": nama_obat,
        }

    return {
        "status": "found",
        "nama_input": nama_obat,
        "obat": obat,
        "analisis_keamanan": cross_reference_efek_obat(obat),
    }


def _format_daftar(label: str, items: List[str]) -> List[str]:
    """Bantu render list ke bentuk teks yang rapi untuk CLI sederhana."""
    if not items:
        return [f"{label:<22}: -"]

    lines = [f"{label:<22}: {items[0]}"]
    for item in items[1:]:
        lines.append(f"{'':<22}  {item}")
    return lines


def format_hasil_pencarian(payload: Dict) -> str:
    """Ubah hasil pencarian obat menjadi teks siap tampil."""
    kata_kunci = payload.get("kata_kunci", "")
    hasil = payload.get("hasil", [])

    lines = ["=== HASIL PENCARIAN OBAT ==="]
    lines.append(f"Kata kunci            : {kata_kunci}")
    lines.append(f"Jumlah hasil          : {len(hasil)}")

    if not hasil:
        lines.append("Tidak ada obat yang cocok dengan kata kunci tersebut.")
        return "\n".join(lines)

    for index, obat in enumerate(hasil, start=1):
        lines.append("-" * 55)
        lines.append(f"{index}. {obat['nama_obat']} ({obat['kategori']})")
        lines.append(
            f"   Indikasi           : {', '.join(obat.get('indikasi', [])) or '-'}"
        )
        lines.append(
            f"   Bahan aktif        : {', '.join(obat.get('bahan_aktif', [])) or '-'}"
        )
        lines.append(f"   Dosis umum         : {obat.get('dosis_umum', '-')}")

    return "\n".join(lines)


def format_profil_keamanan(payload: Dict) -> str:
    """Ubah profil keamanan obat menjadi teks lengkap siap tampil."""
    if payload.get("status") != "found":
        return (
            "=== PROFIL KEAMANAN OBAT ===\n"
            f"Obat '{payload.get('nama_input', '')}' tidak ditemukan di database."
        )

    obat = payload["obat"]
    analisis = payload["analisis_keamanan"]

    lines = ["=== PROFIL KEAMANAN OBAT ==="]
    lines.append(f"Nama obat             : {obat['nama_obat']}")
    lines.append(
        f"Alias                 : {', '.join(obat.get('alias', [])) or '-'}"
    )
    lines.append(f"Kategori              : {obat.get('kategori', '-')}")
    lines.extend(_format_daftar("Bahan aktif", obat.get("bahan_aktif", [])))
    lines.extend(_format_daftar("Indikasi", obat.get("indikasi", [])))
    lines.append(f"Dosis umum            : {obat.get('dosis_umum', '-')}")
    lines.append(f"Kehamilan             : {obat.get('kehamilan', '-')}")
    lines.append(
        f"Skor risiko           : {analisis['skor_risiko']}/100 ({analisis['label_risiko']})"
    )

    ringkasan = analisis["ringkasan_keparahan"]
    lines.append(
        "Ringkasan efek        : "
        f"serius={ringkasan['serius']}, sedang={ringkasan['sedang']}, ringan={ringkasan['ringan']}"
    )

    lines.append("-" * 55)
    lines.append("Efek samping terpetakan:")
    if analisis["efek_dikenali"]:
        for efek in analisis["efek_dikenali"]:
            lines.append(
                f"- {efek['nama_efek']} [{efek['tingkat_keparahan']}] - {efek['rekomendasi']}"
            )
    else:
        lines.append("- Belum ada efek samping yang berhasil dicocokkan.")

    if analisis["efek_tidak_dikenali"]:
        lines.append("-" * 55)
        lines.append("Efek belum terpetakan:")
        for efek in analisis["efek_tidak_dikenali"]:
            lines.append(f"- {efek}")

    lines.append("-" * 55)
    lines.append("Peringatan penting:")
    for item in obat.get("peringatan", []):
        lines.append(f"- {item}")

    lines.append("-" * 55)
    lines.append("Kontraindikasi:")
    for item in obat.get("kontraindikasi", []):
        lines.append(f"- {item}")

    lines.append("-" * 55)
    lines.append("Interaksi penting:")
    for item in obat.get("interaksi", []):
        lines.append(f"- {item}")

    return "\n".join(lines)
