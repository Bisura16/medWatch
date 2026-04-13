"""
anggota1.py
Modul scraping data obat MedWatch (efek samping + recall obat).
Ghaisan Khoirul Badruzaman / 251524048 / Kelompok B5

Output:
    data/drug_safety_data.json   - efek samping per obat
    data/drug_recalls.json       - data recall FDA
"""

import json
import time
import random
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


BASE = "https://www.drugs.com"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# header browser fake biar drugs.com gak nganggep request kita ini bot
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# 60 obat umum dari WHO Essential Medicines + obat populer di Indonesia.
# dipilih 60 biar pasti dapet 50+ entry valid (asumsi 5-10 page bakal gagal parse).
DRUGS = [
    # analgesik / pereda nyeri
    "ibuprofen", "paracetamol", "aspirin", "naproxen", "diclofenac",
    "tramadol", "celecoxib", "meloxicam", "ketoprofen", "mefenamic-acid",
    # antibiotik
    "amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline", "cephalexin",
    "clindamycin", "metronidazole", "levofloxacin", "erythromycin", "ampicillin",
    # antihistamin (alergi)
    "cetirizine", "loratadine", "diphenhydramine", "fexofenadine", "chlorpheniramine",
    # antidepresan & anxiolytic
    "sertraline", "fluoxetine", "escitalopram", "amitriptyline", "alprazolam",
    # antihipertensi & kardiovaskular
    "amlodipine", "lisinopril", "losartan", "valsartan", "metoprolol",
    "atenolol", "captopril", "bisoprolol", "nifedipine", "furosemide",
    # statin & pengencer darah
    "simvastatin", "atorvastatin", "rosuvastatin", "warfarin", "clopidogrel",
    # antidiabetik
    "metformin", "glipizide", "glimepiride", "sitagliptin", "insulin",
    # PPI / saluran cerna
    "omeprazole", "lansoprazole", "ranitidine", "pantoprazole", "famotidine",
    "domperidone", "ondansetron", "loperamide",
    # lain-lain
    "prednisone", "dexamethasone", "salbutamol", "montelukast", "levothyroxine",
    "allopurinol",
]

# kategori obat berdasarkan prefix nama. drugs.com gak konsisten nampilin
# kategori di page side effects, jadi gw mapping manual.
KATEGORI = {
    "Antibiotik":     ["amox", "azith", "cipro", "doxy", "ceph", "clinda", "metro", "levo", "eryth", "ampi"],
    "Analgesik":      ["ibu", "paracet", "aspir", "napro", "diclo", "tramad", "cele", "melox", "keto", "mefen"],
    "Antihistamin":   ["ceti", "lorat", "diphen", "fexo", "chlorph"],
    "Antidepresan":   ["sertr", "fluo", "escit", "amit"],
    "Antihipertensi": ["amlo", "lisin", "losar", "valsa", "metop", "aten", "capto", "biso", "nife"],
    "Statin":         ["simva", "atorva", "rosuva"],
    "Antidiabetik":   ["metfor", "glipi", "glime", "sita", "insul"],
    "Saluran Cerna":  ["omepra", "lansop", "raniti", "pantop", "famot", "domper", "ondan", "loper"],
}


def tebak_kategori(nama):
    # cari prefix yang match nama obat, return kategori pertama yang ketemu
    nama = nama.lower()
    for kat, prefixes in KATEGORI.items():
        if any(p in nama for p in prefixes):
            return kat
    return "Umum"


def fetch(url):
    # ambil HTML dari URL, return None kalau gagal apapun
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.text
        print(f"    status {r.status_code}")
    except Exception as e:
        print(f"    error: {e}")
    return None


def bersihin(s):
    # rapiin whitespace + buang nbsp biar JSON-nya gak berantakan
    if not s:
        return ""
    s = s.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s).strip()


# ----- SCRAPER 1: efek samping obat -----

def scrape_efek_samping():
    print(f"\n[1/2] scraping efek samping ({len(DRUGS)} obat)")
    hasil = []

    for i, drug in enumerate(DRUGS, 1):
        # tiap obat punya page sendiri di /sfx/<nama>-side-effects.html
        url = f"{BASE}/sfx/{drug}-side-effects.html"
        print(f"  [{i}/{len(DRUGS)}] {drug}")

        html = fetch(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        # cek halaman valid. drugs.com kadang return 200 walau page sebenernya gak ada
        h1 = soup.find("h1")
        if not h1 or "not found" in h1.get_text().lower():
            continue

        # default keparahan = mild, naik jadi moderate/severe kalo nemu marker
        keparahan = "mild"
        efek_samping = []

        # iterasi tiap heading section, cari yang relevan sama side effects
        for h in soup.find_all(["h2", "h3"]):
            judul = bersihin(h.get_text()).lower()

            # skip heading yang bukan tentang efek samping
            if not any(k in judul for k in ["common", "rare", "serious", "emergency", "side effect"]):
                continue

            # naikin level keparahan kalo heading-nya nunjukin yang serius
            if any(k in judul for k in ["emergency", "serious", "severe"]):
                keparahan = "severe"
            elif "more common" in judul and keparahan != "severe":
                keparahan = "moderate"

            # walking sibling: ambil <ul> setelah heading sampe ketemu heading berikutnya
            sib = h.find_next_sibling()
            while sib and sib.name not in ("h2", "h3"):
                if sib.name == "ul":
                    for li in sib.find_all("li"):
                        teks = bersihin(li.get_text())
                        if teks and len(teks) < 200:
                            efek_samping.append(teks)
                sib = sib.find_next_sibling()

        # dedup tapi tetep preserve urutan asli (set langsung gak preserve order)
        seen = set()
        efek_unik = []
        for e in efek_samping:
            if e.lower() not in seen:
                seen.add(e.lower())
                efek_unik.append(e)

        # kalo gak dapet apa-apa berarti page-nya format-nya beda, skip
        if not efek_unik:
            continue

        # cari section warning buat field warnings (ga semua page punya)
        warnings_text = "Konsultasikan dengan tenaga kesehatan sebelum penggunaan."
        for h in soup.find_all(["h2", "h3"]):
            jud = h.get_text().lower()
            if "warning" in jud or "precaution" in jud:
                p = h.find_next("p")
                if p:
                    warnings_text = bersihin(p.get_text())[:400]
                    break

        # rakit dict sesuai schema PRD
        hasil.append({
            "drug_name": drug.replace("-", " ").title(),
            "category": tebak_kategori(drug),
            "side_effects": efek_unik[:15],   # cap 15 item biar JSON gak bloated
            "severity_level": keparahan,
            "warnings": warnings_text,
            "source_url": url,
        })

        # jeda random 1.5-2.5 detik biar gak kena rate limit drugs.com
        time.sleep(random.uniform(1.5, 2.5))

    return hasil


# ----- SCRAPER 2: recall obat dari FDA -----

def scrape_recall():
    print(f"\n[2/2] scraping recall obat")
    hasil = []
    bulan_map = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }

    # loop pagination max 7 halaman atau sampe dapet 50 entry
    for page in range(1, 8):
        url = f"{BASE}/fda-recalls/" if page == 1 else f"{BASE}/fda-recalls/?page={page}"
        print(f"  halaman {page}")

        html = fetch(url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")

        # selector utama buat news list di drugs.com
        items = soup.select("div.news-list-item, li.news-list-item")

        # fallback kalo selector di atas miss (struktur HTML bisa berubah)
        if not items:
            items = [h.parent for h in soup.find_all("h3") if h.find_next("p")]

        if not items:
            print(f"    gak nemu item di halaman ini, stop")
            break

        for it in items:
            # nama produk biasanya di h3 atau h4
            judul = it.select_one("h3, h4")
            if not judul:
                continue
            nama = bersihin(judul.get_text())
            if len(nama) < 5:
                continue

            # ambil paragraph pertama buat reason/deskripsi
            p = it.select_one("p")
            deskripsi = bersihin(p.get_text()) if p else ""

            # cari tanggal di teks, format "Jan 15, 2026" atau "January 15, 2026"
            tanggal = ""
            m = re.search(
                r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})",
                deskripsi, re.I,
            )
            if m:
                bln = bulan_map[m.group(1).lower()[:3]]
                tanggal = f"{m.group(3)}-{bln}-{m.group(2).zfill(2)}"

            # cari class recall di teks (Class I = paling serius, III = paling ringan)
            severity = "Unknown"
            cm = re.search(r"class\s+(i{1,3}|[123])\b", deskripsi, re.I)
            if cm:
                v = cm.group(1).upper()
                severity = {
                    "1": "Class I", "I": "Class I",
                    "2": "Class II", "II": "Class II",
                    "3": "Class III", "III": "Class III",
                }.get(v, "Unknown")

            # tebak nama company dari pattern umum di teks recall
            company = "Tidak diketahui"
            cm2 = re.search(r"([A-Z][A-Za-z0-9&,\.\- ]{2,50}?)\s+(?:is recalling|has recalled)", deskripsi)
            if cm2:
                company = cm2.group(1).strip()

            hasil.append({
                "product_name": nama[:200],
                "reason": deskripsi[:400] if deskripsi else "Detail tidak tersedia pada halaman sumber",
                "recall_date": tanggal,
                "severity_class": severity,
                "company": company,
            })

        # cukup 50 udah aman, ga usah lanjut paginasi
        if len(hasil) >= 50:
            break
        time.sleep(random.uniform(1.5, 2.5))

    return hasil


def simpan(data, nama_file):
    # tulis list of dict ke file JSON di folder data/
    path = DATA_DIR / nama_file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  -> {path} ({len(data)} baris)")


if __name__ == "__main__":
    safety = scrape_efek_samping()
    simpan(safety, "drug_safety_data.json")

    recalls = scrape_recall()
    simpan(recalls, "drug_recalls.json")

    print(f"\nselesai. safety={len(safety)} baris, recalls={len(recalls)} baris")
