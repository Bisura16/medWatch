"""
Industrial-grade diagram generator for MedWatch.
Produces 18 diagrams as PNG (matplotlib) and minimal valid .drawio XML.

Material Design palette per spec:
  process/system   = #1976D2 (dark blue)
  actor outline    = #F57C00 (orange)
  external system  = #757575 (gray)
  data store       = #388E3C (green)
  cloud service    = #7B1FA2 (purple)
  boundary         = dashed #212121

No emoji, no gradients, no sketch fonts. Helvetica/Arial throughout.
Title pattern: "MedWatch | <Type> | <Subject>"
Subtitle: "Kelompok B5, D4 Teknik Informatika POLBAN"

Run: python docs/diagrams/_generate.py
Output: docs/diagrams/png/*.png + docs/diagrams/*.drawio
"""
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon
from matplotlib.lines import Line2D

OUT_DIR = Path(__file__).resolve().parent
PNG_DIR = OUT_DIR / "png"
PNG_DIR.mkdir(exist_ok=True, parents=True)

PALETTE = {
    "process":  {"fill": "#1976D2", "edge": "#0D47A1", "text": "white"},
    "actor":    {"fill": "white",   "edge": "#F57C00", "text": "#E65100"},
    "external": {"fill": "#757575", "edge": "#424242", "text": "white"},
    "store":    {"fill": "#388E3C", "edge": "#1B5E20", "text": "white"},
    "cloud":    {"fill": "#7B1FA2", "edge": "#4A148C", "text": "white"},
    "boundary": {"edge": "#212121"},
    "subtle":   {"fill": "#F5F5F5", "edge": "#BDBDBD", "text": "#212121"},
}

FONT = "DejaVu Sans"


def setup_axes(title, subject, ax, w, h):
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0.4, h - 0.3, f"MedWatch | {title} | {subject}", fontsize=12, fontweight="bold",
            family=FONT, color="#212121")
    ax.text(0.4, h - 0.6, "Kelompok B5, D4 Teknik Informatika POLBAN", fontsize=8,
            family=FONT, color="#616161")


def legend_box(ax, x, y, items):
    """items: list of (color_key, label) tuples."""
    ax.add_patch(Rectangle((x, y), 3.0, 0.4 + 0.35 * len(items), facecolor="white",
                            edgecolor="#BDBDBD", linewidth=0.5))
    ax.text(x + 0.1, y + 0.4 + 0.35 * len(items) - 0.25, "LEGEND", fontsize=7,
            fontweight="bold", color="#616161", family=FONT)
    for i, (key, label) in enumerate(items):
        cy = y + 0.4 + 0.35 * (len(items) - 1 - i) - 0.1
        if key in PALETTE:
            ax.add_patch(Rectangle((x + 0.15, cy - 0.1), 0.25, 0.2,
                                    facecolor=PALETTE[key]["fill"],
                                    edgecolor=PALETTE[key].get("edge", "#000"),
                                    linewidth=0.5))
        else:
            ax.plot([x + 0.15, x + 0.4], [cy, cy], color=key, linewidth=1.5,
                    linestyle="--" if "dashed" in label.lower() else "-")
        ax.text(x + 0.55, cy, label, fontsize=7, family=FONT, va="center", color="#212121")


def box(ax, x, y, w, h, label, kind="process", fontsize=8.5, lines=None):
    p = PALETTE[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                 boxstyle="round,pad=0.02,rounding_size=0.05",
                                 facecolor=p["fill"], edgecolor=p["edge"], linewidth=1.2))
    if lines:
        line_h = 0.18
        total = line_h * len(lines)
        start = y + h / 2 + total / 2 - line_h / 2
        for i, ln in enumerate(lines):
            ax.text(x + w / 2, start - i * line_h, ln, ha="center", va="center",
                    fontsize=fontsize - 1, family=FONT, color=p["text"])
    else:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fontsize, family=FONT, color=p["text"], fontweight="bold")


def actor(ax, x, y, label):
    """UML stick-figure actor."""
    p = PALETTE["actor"]
    ax.add_patch(Circle((x, y + 0.5), 0.12, facecolor=p["fill"], edgecolor=p["edge"], linewidth=1.5))
    ax.plot([x, x], [y + 0.38, y - 0.1], color=p["edge"], linewidth=1.5)
    ax.plot([x - 0.18, x + 0.18], [y + 0.2, y + 0.2], color=p["edge"], linewidth=1.5)
    ax.plot([x, x - 0.15], [y - 0.1, y - 0.4], color=p["edge"], linewidth=1.5)
    ax.plot([x, x + 0.15], [y - 0.1, y - 0.4], color=p["edge"], linewidth=1.5)
    ax.text(x, y - 0.55, label, ha="center", va="top", fontsize=8.5, family=FONT,
            color=p["text"], fontweight="bold")


def store(ax, x, y, w, label):
    """Cylinder shape for data stores."""
    p = PALETTE["store"]
    h = 0.7
    from matplotlib.patches import Ellipse
    ax.add_patch(Rectangle((x, y), w, h, facecolor=p["fill"], edgecolor=p["edge"], linewidth=1.2))
    ax.add_patch(Ellipse((x + w / 2, y + h), w, 0.18, facecolor=p["fill"], edgecolor=p["edge"], linewidth=1.2))
    ax.add_patch(Ellipse((x + w / 2, y), w, 0.18, facecolor=p["fill"], edgecolor=p["edge"], linewidth=1.2))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=8, family=FONT,
            color=p["text"], fontweight="bold")


def arrow(ax, p1, p2, label="", style="-", color="#424242", curved=0):
    """Draw an arrow with optional label."""
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12,
                        color=color, linewidth=1.0, linestyle=style,
                        connectionstyle=f"arc3,rad={curved}")
    ax.add_patch(a)
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(mx, my + 0.12, label, ha="center", va="center", fontsize=7,
                family=FONT, color=color, bbox=dict(facecolor="white", edgecolor="none", pad=1))


def boundary(ax, x, y, w, h, label):
    ax.add_patch(Rectangle((x, y), w, h, facecolor="none",
                            edgecolor=PALETTE["boundary"]["edge"], linewidth=1.0,
                            linestyle="--"))
    ax.text(x + 0.15, y + h - 0.2, label, fontsize=8, family=FONT,
            color="#212121", fontweight="bold", style="italic")


def save(fig, name, w_inches=16, h_inches=9):
    fig.set_size_inches(w_inches, h_inches)
    out = PNG_DIR / f"{name}.png"
    fig.savefig(out, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


# ============================================================
# DRAWIO XML GENERATION
# ============================================================

def make_drawio(name, cells_xml):
    """Wrap cells_xml in mxfile / mxGraphModel structure."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="medwatch-generator" version="22.0.0">
  <diagram id="{name}" name="{name}">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="826" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        {cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""


def cell_box(id_, label, x, y, w=140, h=60, kind="process"):
    fills = {"process": "#1976D2", "external": "#757575", "store": "#388E3C",
             "cloud": "#7B1FA2", "subtle": "#F5F5F5"}
    edges = {"process": "#0D47A1", "external": "#424242", "store": "#1B5E20",
             "cloud": "#4A148C", "subtle": "#BDBDBD"}
    text_colors = {"process": "white", "external": "white", "store": "white",
                   "cloud": "white", "subtle": "#212121"}
    fill = fills.get(kind, "#1976D2")
    edge = edges.get(kind, "#0D47A1")
    txt = text_colors.get(kind, "white")
    return f'''<mxCell id="{id_}" value="{label}" style="rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={edge};fontColor={txt};fontSize=12;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />
        </mxCell>'''


def cell_actor(id_, label, x, y):
    return f'''<mxCell id="{id_}" value="{label}" style="shape=umlActor;verticalLabelPosition=bottom;labelBackgroundColor=none;verticalAlign=top;html=1;outlineConnect=0;strokeColor=#F57C00;fontColor=#E65100;fontSize=11;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="40" height="60" as="geometry" />
        </mxCell>'''


def cell_edge(id_, src, dst, label=""):
    return f'''<mxCell id="{id_}" style="endArrow=classic;html=1;rounded=0;strokeColor=#424242;fontSize=10;" edge="1" parent="1" source="{src}" target="{dst}">
          <mxGeometry relative="1" as="geometry" />
          {f'<mxCell value="{label}" />' if label else ''}
        </mxCell>'''


# ============================================================
# 18 DIAGRAMS
# ============================================================

def diag_01_c4_context():
    name = "01-c4-context"
    fig, ax = plt.subplots()
    setup_axes("C4 Level 1 (System Context)", "MedWatch", ax, 16, 9)

    # 3 actors on the left
    actor(ax, 1.2, 6.5, "Tenaga\nKesehatan")
    actor(ax, 1.2, 4.5, "Masyarakat")
    actor(ax, 1.2, 2.5, "Admin")

    # MedWatch system in center
    box(ax, 5.5, 4.0, 5.0, 2.0, "MedWatch\nSistem Monitoring Keamanan Obat &\nManajemen Klinik Faskes 1", kind="process",
        lines=["MedWatch", "Sistem Monitoring Keamanan Obat &", "Manajemen Klinik Faskes 1"])

    # External systems on the right
    box(ax, 12.5, 6.5, 2.5, 0.9, "drugs.com", kind="external")
    box(ax, 12.5, 5.0, 2.5, 0.9, "FDA Recall Feed", kind="external")

    # Arrows: actors -> system
    arrow(ax, (1.85, 6.5), (5.5, 5.5), "kelola pasien, cek obat")
    arrow(ax, (1.85, 4.5), (5.5, 4.8), "cari obat, cek keamanan")
    arrow(ax, (1.85, 2.5), (5.5, 4.3), "kelola users, scraper")

    # Arrows: system -> external
    arrow(ax, (10.5, 5.5), (12.5, 6.9), "scrape data obat")
    arrow(ax, (10.5, 5.0), (12.5, 5.4), "ambil data recall")

    legend_box(ax, 12.5, 1.0, [
        ("actor", "User actor"),
        ("process", "MedWatch system"),
        ("external", "External service"),
    ])

    save(fig, name)

    cells = "\n        ".join([
        cell_actor("a1", "Tenaga Kesehatan", 80, 80),
        cell_actor("a2", "Masyarakat", 80, 220),
        cell_actor("a3", "Admin", 80, 360),
        cell_box("s1", "MedWatch System", 360, 200, w=240, h=120),
        cell_box("e1", "drugs.com", 760, 80, kind="external"),
        cell_box("e2", "FDA Recall Feed", 760, 220, kind="external"),
        cell_edge("e_a1_s", "a1", "s1"),
        cell_edge("e_a2_s", "a2", "s1"),
        cell_edge("e_a3_s", "a3", "s1"),
        cell_edge("e_s_e1", "s1", "e1"),
        cell_edge("e_s_e2", "s1", "e2"),
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_02_c4_container():
    name = "02-c4-container"
    fig, ax = plt.subplots()
    setup_axes("C4 Level 2 (Container)", "MedWatch", ax, 18, 10)

    # Browser
    box(ax, 1.0, 8.0, 2.5, 0.8, "Browser (User)", kind="subtle")

    # Vercel boundary
    boundary(ax, 0.5, 5.5, 7.5, 2.0, "Vercel (vercel.app)")
    box(ax, 1.0, 6.5, 3.0, 0.8, "Next.js Frontend", kind="cloud")
    box(ax, 4.5, 6.5, 3.0, 0.8, "API Proxy Route", kind="cloud")

    # Cloud Run boundary
    boundary(ax, 9.5, 4.5, 7.5, 4.0, "GCP Cloud Run (asia-southeast1)")
    box(ax, 10.0, 6.8, 2.5, 0.8, "Flask api/", kind="cloud")
    box(ax, 13.0, 6.8, 4.0, 0.8, "Modul anggota1-5 (read-only)", kind="process")
    store(ax, 10.5, 4.9, 1.7, "GCS Bucket")
    box(ax, 13.5, 5.0, 3.0, 0.8, "Secret Manager", kind="store")

    # GitHub
    box(ax, 1.0, 2.5, 3.0, 0.8, "Bisura16/medWatch", kind="external")
    box(ax, 4.5, 2.5, 3.0, 0.8, "Finerium/FrontendMedwatch", kind="external")

    # Arrows
    arrow(ax, (2.25, 8.0), (2.5, 7.3), "HTTPS")
    arrow(ax, (4.0, 6.9), (4.5, 6.9), "/api/...")
    arrow(ax, (7.5, 6.9), (10.0, 7.2), "HTTPS + JWT")
    arrow(ax, (12.5, 7.2), (13.0, 7.2), "import")
    arrow(ax, (11.0, 6.8), (11.35, 5.6), "load/save")
    arrow(ax, (12.5, 6.8), (15.0, 5.8), "fetch JWT")

    legend_box(ax, 14.5, 1.0, [
        ("cloud", "Cloud service"),
        ("process", "Application"),
        ("store", "Data store"),
        ("external", "External"),
        ("subtle", "User device"),
    ])
    save(fig, name)

    cells = "\n        ".join([
        cell_box("b", "Browser", 40, 40, w=140, h=50, kind="subtle"),
        cell_box("v_fe", "Next.js Frontend (Vercel)", 40, 160, w=200, h=60, kind="cloud"),
        cell_box("v_api", "API Proxy (Vercel)", 280, 160, w=180, h=60, kind="cloud"),
        cell_box("cr_api", "Flask api/ (Cloud Run)", 540, 160, w=200, h=60, kind="cloud"),
        cell_box("cr_mod", "anggota1-5 modules", 780, 160, w=180, h=60),
        cell_box("gcs", "GCS Bucket", 540, 320, w=160, h=70, kind="store"),
        cell_box("sm", "Secret Manager", 740, 320, w=180, h=70, kind="store"),
        cell_box("gh1", "Bisura16/medWatch", 40, 440, w=200, h=50, kind="external"),
        cell_box("gh2", "Finerium/FrontendMedwatch", 280, 440, w=240, h=50, kind="external"),
        cell_edge("e1", "b", "v_fe"),
        cell_edge("e2", "v_fe", "v_api"),
        cell_edge("e3", "v_api", "cr_api"),
        cell_edge("e4", "cr_api", "cr_mod"),
        cell_edge("e5", "cr_api", "gcs"),
        cell_edge("e6", "cr_api", "sm"),
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_03_c4_component_api():
    name = "03-c4-component-api"
    fig, ax = plt.subplots()
    setup_axes("C4 Level 3 (Component) - api/", "Backend internals", ax, 18, 11)

    boundary(ax, 0.5, 0.5, 17.0, 9.5, "api/ Flask Application")

    box(ax, 1.0, 8.5, 2.5, 0.7, "app.py (Flask entry)", kind="process")
    box(ax, 4.0, 8.5, 2.0, 0.7, "config.py", kind="subtle")
    box(ax, 6.5, 8.5, 2.0, 0.7, "bootstrap.py", kind="subtle")
    box(ax, 9.0, 8.5, 2.0, 0.7, "auth.py", kind="subtle")
    box(ax, 11.5, 8.5, 2.0, 0.7, "middleware.py", kind="subtle")
    box(ax, 14.0, 8.5, 2.0, 0.7, "storage.py", kind="subtle")

    # Blueprints row
    bps = [
        ("auth_routes", "/api/auth/*"),
        ("patient_routes", "/api/patients/*"),
        ("drug_routes", "/api/drugs/*"),
        ("safety_routes", "/api/safety/*"),
        ("visualization_routes", "/api/visualizations/*"),
        ("pdf_routes", "/api/pdf/*"),
        ("admin_routes", "/api/admin/*"),
    ]
    for i, (m, path) in enumerate(bps):
        box(ax, 1.0 + i * 2.3, 6.5, 2.1, 1.0, m, kind="process",
            lines=[m, path])

    # Wraps anggota
    boundary(ax, 0.5, 3.5, 17.0, 2.0, "Modul anggota (read-only, imported via bootstrap)")
    for i, ang in enumerate(["anggota1\nscraper", "anggota2\npasien_helper", "anggota3\n(skipped)",
                              "anggota4\ndata_loader\nsafety_checker", "anggota5\nexport_pdf"]):
        box(ax, 1.0 + i * 3.3, 4.0, 3.0, 1.2, ang, kind="external",
            lines=ang.split("\n"))

    # Stores
    store(ax, 4.5, 1.0, 2.0, "users.json (GCS)")
    store(ax, 8.5, 1.0, 2.0, "patients.json (GCS)")
    box(ax, 12.0, 1.0, 3.0, 0.8, "JWT Secret (Secret Manager)", kind="cloud")

    # Arrows from auth_routes to auth.py and storage
    arrow(ax, (1.55, 7.5), (10.0, 8.5), "")
    arrow(ax, (5.5, 6.5), (5.5, 2.0), "")

    legend_box(ax, 14.5, 0.7, [
        ("process", "Component"),
        ("external", "External module"),
        ("subtle", "Helper"),
        ("store", "Data store"),
    ])
    save(fig, name, w_inches=18, h_inches=11)

    cells = "\n        ".join([
        cell_box("app", "app.py", 40, 40, w=140, h=50),
        cell_box("auth", "auth.py", 200, 40, w=140, h=50, kind="subtle"),
        cell_box("mw", "middleware.py", 360, 40, w=160, h=50, kind="subtle"),
        cell_box("st", "storage.py", 540, 40, w=140, h=50, kind="subtle"),
        *[cell_box(f"bp{i}", bp[0], 40 + i * 150, 140, w=140, h=50)
          for i, bp in enumerate(bps)],
        *[cell_box(f"ang{i}", ang.replace("\n", " "), 40 + i * 200, 280, w=180, h=70, kind="external")
          for i, ang in enumerate(["anggota1", "anggota2", "anggota3", "anggota4", "anggota5"])],
        cell_box("st1", "users.json", 200, 420, w=140, h=60, kind="store"),
        cell_box("st2", "patients.json", 360, 420, w=140, h=60, kind="store"),
        cell_box("sm", "JWT Secret", 520, 420, w=160, h=60, kind="cloud"),
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_04_use_case():
    name = "04-use-case"
    fig, ax = plt.subplots()
    setup_axes("UML Use Case", "MedWatch System", ax, 16, 11)

    boundary(ax, 4.0, 1.0, 8.0, 9.0, "MedWatch")

    # Actors
    actor(ax, 1.5, 8.0, "Tenaga\nKesehatan")
    actor(ax, 1.5, 5.0, "Masyarakat")
    actor(ax, 1.5, 2.0, "Admin")

    # Use cases as ellipses
    from matplotlib.patches import Ellipse
    use_cases_tk = [
        ("Login", 5.5, 9.0),
        ("Kelola Data Pasien", 8.0, 9.0),
        ("Cek Keamanan Obat", 10.5, 8.5),
        ("Lihat Visualisasi", 8.0, 7.5),
        ("Ekspor Rekam Medis PDF", 5.5, 7.5),
    ]
    use_cases_m = [
        ("Cari Obat", 5.5, 5.5),
        ("Cek Keamanan Obat (sendiri)", 9.0, 5.5),
        ("Lihat Profil", 5.5, 4.5),
    ]
    use_cases_a = [
        ("Trigger Scraper", 5.5, 3.0),
        ("Kelola Akun User", 8.0, 3.0),
        ("Monitor Sistem", 10.5, 3.0),
        ("Ekspor Laporan Bulanan", 8.0, 1.7),
    ]
    all_uc = []
    for uc, x, y in use_cases_tk + use_cases_m + use_cases_a:
        ax.add_patch(Ellipse((x, y), 2.4, 0.7, facecolor="white",
                              edgecolor="#0D47A1", linewidth=1.0))
        ax.text(x, y, uc, ha="center", va="center", fontsize=8, family=FONT, color="#212121")
        all_uc.append((uc, x, y))

    # Connections
    for _, x, y in use_cases_tk:
        ax.plot([2.0, x - 1.2], [8.0, y], color="#616161", linewidth=0.7)
    for _, x, y in use_cases_m:
        ax.plot([2.0, x - 1.2], [5.0, y], color="#616161", linewidth=0.7)
    for _, x, y in use_cases_a:
        ax.plot([2.0, x - 1.2], [2.0, y], color="#616161", linewidth=0.7)

    legend_box(ax, 13.0, 1.0, [
        ("actor", "Actor"),
        ("subtle", "Use case (ellipse)"),
    ])
    save(fig, name, w_inches=16, h_inches=11)

    cells = "\n        ".join([
        cell_actor("a_tk", "Tenaga Kesehatan", 40, 80),
        cell_actor("a_m", "Masyarakat", 40, 240),
        cell_actor("a_a", "Admin", 40, 400),
        *[f'<mxCell id="uc{i}" value="{uc}" style="ellipse;whiteSpace=wrap;html=1;fillColor=white;strokeColor=#0D47A1;" vertex="1" parent="1"><mxGeometry x="{200 + (i % 3) * 200}" y="{40 + (i // 3) * 120}" width="160" height="50" as="geometry" /></mxCell>'
          for i, (uc, _, _) in enumerate(all_uc)],
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_05_class():
    name = "05-class-diagram"
    fig, ax = plt.subplots()
    setup_axes("UML Class", "Backend Models & Services", ax, 18, 12)

    classes = [
        # x, y, name, attrs, methods
        (1, 9, "User", ["+ username: str", "+ role: str", "+ name: str", "- password_hash: str"],
         ["+ verify_password()"]),
        (5, 9, "Patient", ["+ id: str", "+ nama: str", "+ tanggal_kunjungan: str",
                            "+ kategori: str"], ["+ to_pdf_format()"]),
        (9, 9, "SOAP_Record", ["+ S: dict", "+ O: dict", "+ A: dict", "+ P: dict"], []),
        (13, 9, "Drug", ["+ nama_obat: str", "+ kategori: str", "+ bahan_aktif: list",
                          "+ efek_samping: list"], []),
        (1, 4, "AuthService", ["+ JWT_SECRET", "+ JWT_EXPIRY_HOURS"],
         ["+ hash_password()", "+ verify_password()", "+ issue_token()", "+ verify_token()"]),
        (5, 4, "StorageService", ["+ USE_CLOUD_STORAGE", "+ GCS_BUCKET"],
         ["+ load_users()", "+ save_users()", "+ load_patients()", "+ save_patients()"]),
        (9, 4, "SafetyChecker", ["+ BOBOT_KEPARAHAN"],
         ["+ cek_keamanan_obat()", "+ cross_reference_efek_obat()"]),
        (13, 4, "PDFGenerator", [],
         ["+ buat_laporan_pdf()", "+ to_anggota5_format()"]),
    ]

    for x, y, name_, attrs, methods in classes:
        h = 0.5 + 0.3 * (len(attrs) + len(methods)) + 0.4
        box_top = y + h - 0.4
        ax.add_patch(Rectangle((x, y), 3.5, h, facecolor="white",
                                edgecolor="#0D47A1", linewidth=1.2))
        ax.add_patch(Rectangle((x, box_top), 3.5, 0.4, facecolor="#1976D2",
                                edgecolor="#0D47A1", linewidth=1.2))
        ax.text(x + 1.75, box_top + 0.2, name_, ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", family=FONT)
        cy = box_top - 0.15
        for a in attrs:
            ax.text(x + 0.1, cy, a, fontsize=7, family=FONT, color="#212121")
            cy -= 0.25
        if methods:
            ax.plot([x, x + 3.5], [cy + 0.1, cy + 0.1], color="#0D47A1", linewidth=0.5)
            for m in methods:
                ax.text(x + 0.1, cy - 0.1, m, fontsize=7, family=FONT, color="#212121")
                cy -= 0.25

    # Composition: Patient has SOAP
    arrow(ax, (8.5, 10.0), (9.0, 10.0), "1..1")

    legend_box(ax, 14.5, 0.6, [
        ("process", "Class header"),
        ("subtle", "Class body"),
    ])
    save(fig, name, w_inches=18, h_inches=12)

    cells = "\n        ".join([
        cell_box(f"c{i}", c[2], 40 + (i % 4) * 220, 40 + (i // 4) * 200, w=200, h=120, kind="subtle")
        for i, c in enumerate(classes)
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_sequence(name, title, lifelines, messages):
    """Generic sequence diagram. lifelines = [(label, x), ...]; messages = [(from_x, to_x, y, label, dashed)]"""
    fig, ax = plt.subplots()
    setup_axes("UML Sequence", title, ax, 16, 11)

    top_y = 9.5
    bot_y = 1.0
    for label, x in lifelines:
        ax.add_patch(Rectangle((x - 0.7, top_y - 0.3), 1.4, 0.5, facecolor="#1976D2",
                                edgecolor="#0D47A1", linewidth=1.0))
        ax.text(x, top_y - 0.05, label, ha="center", va="center", fontsize=8.5,
                color="white", fontweight="bold", family=FONT)
        ax.plot([x, x], [top_y - 0.3, bot_y], color="#9E9E9E", linewidth=0.8, linestyle=":")

    for from_x, to_x, y, label, dashed in messages:
        style = "--" if dashed else "-"
        arrow(ax, (from_x, y), (to_x, y), label, style=style)

    legend_box(ax, 13.5, 0.5, [
        ("process", "Lifeline"),
        ("#424242", "synchronous call"),
        ("#424242", "dashed = response/async"),
    ])
    save(fig, name)

    cells = "\n        ".join([
        cell_box(f"ll{i}", ll[0], 40 + i * 150, 40, w=120, h=50)
        for i, ll in enumerate(lifelines)
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_06_sequence_auth():
    diag_sequence(
        "06-sequence-auth",
        "Login Flow",
        [("Browser", 2), ("Vercel Proxy", 5), ("Cloud Run", 8.5), ("users.json", 12), ("Cookie", 14.5)],
        [
            (2, 5, 8.5, "POST /api/auth/login {user, pass}", False),
            (5, 8.5, 8.0, "POST {user, pass}", False),
            (8.5, 12, 7.5, "load_users()", False),
            (12, 8.5, 7.0, "users[]", True),
            (8.5, 8.5, 6.5, "verify_password (bcrypt)", False),
            (8.5, 8.5, 6.0, "issue_token (JWT)", False),
            (8.5, 5, 5.5, "200 {token, user}", True),
            (5, 14.5, 5.0, "Set-Cookie httpOnly", False),
            (5, 2, 4.5, "200 {user}", True),
            (2, 5, 3.5, "GET /api/patients (next req)", False),
            (5, 8.5, 3.0, "Authorization: Bearer <token>", False),
            (8.5, 5, 2.5, "200 [...]", True),
            (5, 2, 2.0, "200 [...]", True),
        ],
    )


def diag_07_sequence_patient_create():
    diag_sequence(
        "07-sequence-patient-create",
        "Create Patient",
        [("Bidan", 2), ("Form", 5), ("Vercel API", 8), ("Cloud Run", 11), ("GCS", 14)],
        [
            (2, 5, 9.0, "Submit form", False),
            (5, 8, 8.5, "POST /api/patients", False),
            (8, 11, 8.0, "POST + JWT", False),
            (11, 11, 7.5, "@require_role check", False),
            (11, 14, 7.0, "load_patients()", False),
            (14, 11, 6.5, "[]", True),
            (11, 11, 6.0, "pasien_helper.generate_id() -> P001", False),
            (11, 14, 5.5, "save_patients(...)", False),
            (14, 11, 5.0, "ok", True),
            (11, 8, 4.5, "201 {id: P001, ...}", True),
            (8, 5, 4.0, "201", True),
            (5, 2, 3.5, "Toast 'P001 created'", True),
        ],
    )


def diag_08_sequence_safety():
    diag_sequence(
        "08-sequence-safety-check",
        "Safety Check",
        [("UI", 2), ("Vercel", 5), ("Cloud Run", 8), ("anggota4", 11.5), ("DB JSON", 14)],
        [
            (2, 5, 9.0, "POST /api/safety/check {drugs}", False),
            (5, 8, 8.5, "Forward + JWT", False),
            (8, 11.5, 8.0, "cek_keamanan_obat(drugs)", False),
            (11.5, 14, 7.5, "muat_database_obat()", False),
            (14, 11.5, 7.0, "drugs[]", True),
            (11.5, 14, 6.5, "muat_database_efek_samping()", False),
            (14, 11.5, 6.0, "effects[]", True),
            (11.5, 11.5, 5.5, "cross_reference + score", False),
            (11.5, 8, 5.0, "{hasil_obat, ...}", True),
            (8, 8, 4.5, "aggregate severity_score", False),
            (8, 5, 4.0, "200 {severity_level, ...}", True),
            (5, 2, 3.5, "200", True),
        ],
    )


def diag_09_activity():
    name = "09-activity-patient-flow"
    fig, ax = plt.subplots()
    setup_axes("UML Activity", "Patient Record Creation", ax, 12, 14)

    # Vertical activity flow
    nodes = [
        (6, 12.5, "Start", "ellipse", "#388E3C"),
        (6, 11.0, "Bidan login", "rect"),
        (6, 9.7, "Decision: role == tenaga_kesehatan?", "diamond"),
        (3, 8.0, "Show error", "rect"),
        (6, 8.0, "Open patient form", "rect"),
        (6, 6.7, "Fill SOAP fields", "rect"),
        (6, 5.4, "Decision: required fields filled?", "diamond"),
        (3, 4.0, "Highlight errors", "rect"),
        (6, 4.0, "Submit POST /api/patients", "rect"),
        (6, 2.7, "Backend assigns P001", "rect"),
        (6, 1.5, "Show detail page", "rect"),
        (6, 0.3, "End", "ellipse", "#F44336"),
    ]

    for n in nodes:
        x, y, lbl, shape = n[0], n[1], n[2], n[3]
        color = n[4] if len(n) > 4 else "#1976D2"
        if shape == "rect":
            ax.add_patch(FancyBboxPatch((x - 1.4, y - 0.3), 2.8, 0.6,
                                         boxstyle="round,pad=0.05,rounding_size=0.05",
                                         facecolor=color, edgecolor="#0D47A1", linewidth=1.0))
            ax.text(x, y, lbl, ha="center", va="center", fontsize=8.5, color="white",
                    fontweight="bold", family=FONT)
        elif shape == "diamond":
            from matplotlib.patches import Polygon
            ax.add_patch(Polygon([(x, y + 0.5), (x + 1.7, y), (x, y - 0.5), (x - 1.7, y)],
                                  facecolor="#FFA000", edgecolor="#FF6F00", linewidth=1.0))
            ax.text(x, y, lbl, ha="center", va="center", fontsize=7.5, color="white",
                    fontweight="bold", family=FONT)
        else:
            from matplotlib.patches import Ellipse
            ax.add_patch(Ellipse((x, y), 1.6, 0.5, facecolor=color, edgecolor="#0D47A1",
                                  linewidth=1.0))
            ax.text(x, y, lbl, ha="center", va="center", fontsize=9, color="white",
                    fontweight="bold", family=FONT)

    # Edges (top-down + branches)
    edges = [
        ((6, 12.25), (6, 11.3), ""),
        ((6, 10.7), (6, 10.2), ""),
        ((5.5, 9.7), (3.5, 8.3), "no"),
        ((6.5, 9.7), (6, 8.3), "yes"),
        ((6, 7.7), (6, 7.0), ""),
        ((6, 6.4), (6, 5.9), ""),
        ((5.5, 5.4), (3.5, 4.3), "no"),
        ((6.5, 5.4), (6, 4.3), "yes"),
        ((6, 3.7), (6, 3.0), ""),
        ((6, 2.4), (6, 1.8), ""),
        ((6, 1.2), (6, 0.5), ""),
    ]
    for p1, p2, lbl in edges:
        arrow(ax, p1, p2, lbl)

    save(fig, name, w_inches=12, h_inches=14)
    cells = "\n        ".join([cell_box(f"a{i}", n[2], 100, 40 + i * 80, w=200, h=50) for i, n in enumerate(nodes)])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_10_state():
    name = "10-state-auth-session"
    fig, ax = plt.subplots()
    setup_axes("UML State Machine", "Auth Session", ax, 16, 9)

    from matplotlib.patches import Ellipse, FancyBboxPatch
    states = [
        (2, 5, "Anonymous"),
        (6, 5, "Authenticating"),
        (10, 5, "Authenticated"),
        (14, 5, "Expired"),
    ]
    for x, y, s in states:
        ax.add_patch(FancyBboxPatch((x - 1.2, y - 0.5), 2.4, 1.0,
                                     boxstyle="round,pad=0.05,rounding_size=0.15",
                                     facecolor="#1976D2", edgecolor="#0D47A1", linewidth=1.2))
        ax.text(x, y, s, ha="center", va="center", fontsize=10, color="white",
                fontweight="bold", family=FONT)

    arrow(ax, (3.2, 5), (4.8, 5), "submit credentials")
    arrow(ax, (7.2, 5), (8.8, 5), "valid + JWT issued")
    arrow(ax, (11.2, 5), (12.8, 5), "12h elapsed")
    arrow(ax, (10, 4.5), (3, 4.0), "logout (curved)", curved=-0.3)
    arrow(ax, (14, 4.5), (3, 4.5), "re-login required", curved=-0.4)
    arrow(ax, (6, 4.5), (3, 4.5), "invalid", curved=-0.2)

    legend_box(ax, 12.0, 1.0, [("process", "State")])
    save(fig, name)

    cells = "\n        ".join([cell_box(f"s{i}", s[2], 40 + i * 200, 200, w=160, h=70) for i, s in enumerate(states)])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_11_er():
    name = "11-er-schema"
    fig, ax = plt.subplots()
    setup_axes("ER Diagram", "Conceptual Data Model", ax, 16, 10)

    entities = [
        (2, 7, "User", ["username PK", "password_hash", "role", "name", "phone"]),
        (7, 7, "Patient", ["id PK (P001)", "nama", "tanggal_kunjungan", "umur", "alamat", "kategori",
                            "created_by FK -> User"]),
        (12, 7, "SOAP_Record", ["S, O, A, P (composed in Patient)"]),
        (2, 2, "Drug", ["nama_obat PK", "kategori", "bahan_aktif", "indikasi",
                         "kontraindikasi", "interaksi", "efek_samping[] -> SideEffect"]),
        (10, 2, "SideEffect", ["nama_efek PK", "kategori", "tingkat_keparahan", "rekomendasi"]),
    ]

    for x, y, name_, fields in entities:
        h = 0.5 + 0.25 * len(fields) + 0.4
        ax.add_patch(Rectangle((x, y), 3.8, h, facecolor="white",
                                edgecolor="#0D47A1", linewidth=1.2))
        ax.add_patch(Rectangle((x, y + h - 0.5), 3.8, 0.5, facecolor="#1976D2",
                                edgecolor="#0D47A1", linewidth=1.2))
        ax.text(x + 1.9, y + h - 0.25, name_, ha="center", va="center",
                fontsize=11, fontweight="bold", color="white", family=FONT)
        cy = y + h - 0.7
        for f in fields:
            ax.text(x + 0.15, cy, f, fontsize=7.5, family=FONT, color="#212121")
            cy -= 0.25

    # Relations (crow's foot inspired, just labeled lines here)
    arrow(ax, (5.8, 7.5), (7.0, 7.5), "1..N created_by")
    arrow(ax, (10.8, 7.5), (12.0, 7.5), "1..1 contains")
    arrow(ax, (5.8, 2.5), (10.0, 2.5), "N..M has effects")

    legend_box(ax, 13.5, 0.5, [("process", "Entity header"), ("subtle", "Attribute")])
    save(fig, name)

    cells = "\n        ".join([cell_box(f"e{i}", n[2], 40 + (i % 3) * 250, 40 + (i // 3) * 200, w=220, h=140)
                                for i, n in enumerate(entities)])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_12_deployment():
    name = "12-deployment"
    fig, ax = plt.subplots()
    setup_axes("UML Deployment", "MedWatch Production Topology", ax, 18, 10)

    # User device node
    box(ax, 0.5, 6.5, 2.5, 1.0, "User Device\n(Browser)", kind="subtle",
        lines=["User Device", "(Browser)"])

    # Vercel Edge boundary
    boundary(ax, 4.0, 5.5, 5.0, 3.0, "Vercel Edge Network (global)")
    box(ax, 4.5, 7.0, 4.0, 0.7, "Next.js Static + SSR", kind="cloud")
    box(ax, 4.5, 6.0, 4.0, 0.7, "API Proxy Function", kind="cloud")

    # GCP boundary
    boundary(ax, 10.0, 1.0, 7.5, 8.0, "GCP project medwatch-polban-2026")
    boundary(ax, 10.5, 5.0, 6.5, 3.5, "Cloud Run (asia-southeast1)")
    box(ax, 11.0, 7.0, 5.5, 0.7, "Service: medwatch-api", kind="cloud")
    box(ax, 11.0, 5.5, 2.5, 0.7, "Container: Python 3.11", kind="process")
    box(ax, 14.0, 5.5, 2.5, 0.7, "Gunicorn 2 workers", kind="process")

    boundary(ax, 10.5, 1.5, 6.5, 3.0, "Storage")
    store(ax, 11.0, 2.0, 2.0, "GCS Bucket\nstate")
    box(ax, 14.0, 2.5, 3.0, 0.7, "Secret Manager", kind="store")

    # Connections
    arrow(ax, (3.0, 7.0), (4.5, 7.3), "HTTPS")
    arrow(ax, (8.5, 6.3), (10.5, 7.3), "HTTPS + JWT")
    arrow(ax, (13.7, 6.2), (12.0, 4.5), "load/save")
    arrow(ax, (15.5, 6.2), (15.5, 3.2), "fetch JWT")

    legend_box(ax, 0.5, 0.5, [
        ("cloud", "Cloud service"),
        ("subtle", "User device"),
        ("process", "Container/Process"),
        ("store", "Storage"),
    ])
    save(fig, name, w_inches=18, h_inches=10)

    cells = "\n        ".join([
        cell_box("user", "User Device", 40, 40, w=160, h=60, kind="subtle"),
        cell_box("ven", "Vercel Edge", 240, 40, w=200, h=60, kind="cloud"),
        cell_box("crun", "Cloud Run", 480, 40, w=200, h=60, kind="cloud"),
        cell_box("gcs", "GCS Bucket", 480, 200, w=180, h=60, kind="store"),
        cell_box("sm", "Secret Manager", 700, 200, w=180, h=60, kind="store"),
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_13_network():
    name = "13-network-topology"
    fig, ax = plt.subplots()
    setup_axes("Network Topology", "Request Path & Trust Zones", ax, 18, 10)

    boundary(ax, 0.5, 1.0, 5.0, 8.0, "Public Internet")
    box(ax, 1.0, 6.5, 4.0, 0.8, "Browser (anywhere)", kind="subtle")
    box(ax, 1.0, 4.5, 4.0, 0.8, "Vercel Edge POP", kind="cloud")
    box(ax, 1.0, 2.5, 4.0, 0.8, "Vercel Function Region", kind="cloud")

    boundary(ax, 6.5, 1.0, 5.0, 8.0, "GCP Project Network")
    box(ax, 7.0, 6.5, 4.0, 0.8, "Cloud Run (allow_unauth=true)", kind="cloud")
    store(ax, 7.5, 4.0, 1.5, "GCS Bucket")
    box(ax, 9.5, 4.0, 1.8, 0.8, "Secret Manager", kind="store")

    boundary(ax, 12.5, 1.0, 5.0, 8.0, "External Sources")
    box(ax, 13.0, 6.5, 4.0, 0.8, "drugs.com (HTTPS)", kind="external")
    box(ax, 13.0, 4.5, 4.0, 0.8, "FDA Recall API", kind="external")

    arrow(ax, (5.0, 6.9), (1.0, 4.9), "HTTPS\n(public)")
    arrow(ax, (5.0, 4.9), (1.0, 2.9), "internal\n(Vercel)")
    arrow(ax, (5.0, 2.9), (7.0, 6.9), "HTTPS\n(public, JWT auth)")
    arrow(ax, (8.5, 6.5), (8.0, 4.7), "private\nGoogle access")
    arrow(ax, (10.5, 6.5), (10.5, 4.7), "private\nGoogle access")
    arrow(ax, (11.0, 6.9), (13.0, 6.9), "HTTPS\n(scraper, manual trigger)")

    legend_box(ax, 0.5, 0.2, [
        ("cloud", "Cloud function/service"),
        ("subtle", "Client"),
        ("store", "Storage (private)"),
        ("external", "External HTTP source"),
    ])
    save(fig, name, w_inches=18, h_inches=10)

    cells = "\n        ".join([
        cell_box("br", "Browser", 40, 40, w=180, h=60, kind="subtle"),
        cell_box("vp", "Vercel POP", 40, 200, w=180, h=60, kind="cloud"),
        cell_box("vf", "Vercel Function", 40, 360, w=180, h=60, kind="cloud"),
        cell_box("cr", "Cloud Run", 280, 40, w=180, h=60, kind="cloud"),
        cell_box("gcs", "GCS", 280, 200, w=180, h=60, kind="store"),
        cell_box("sm", "Secret Mgr", 280, 360, w=180, h=60, kind="store"),
        cell_box("dc", "drugs.com", 520, 40, w=180, h=60, kind="external"),
        cell_box("fda", "FDA Feed", 520, 200, w=180, h=60, kind="external"),
    ])
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, cells))


def diag_structure_chart(name, anggota_label, top, branches):
    """Hierarchical structure chart per anggota."""
    fig, ax = plt.subplots()
    setup_axes("Structure Chart", anggota_label, ax, 18, 10)

    # Top
    box(ax, 7.5, 8.0, 3.0, 0.8, top, kind="process")

    # Branches in row 2
    n = len(branches)
    spacing = 16.0 / (n + 1)
    for i, br in enumerate(branches):
        bx = (i + 1) * spacing
        if isinstance(br, tuple):
            label, sub = br
        else:
            label, sub = br, []
        box(ax, bx - 1.2, 5.5, 2.4, 0.7, label, kind="process")
        arrow(ax, (9.0, 8.0), (bx, 6.2), "")
        # sub-functions in row 3
        if sub:
            sub_spacing = 2.4 / (len(sub) + 0.5)
            for j, s in enumerate(sub):
                sx = bx - 1.2 + (j + 0.5) * sub_spacing
                box(ax, sx - 0.6, 3.0, 1.2, 0.5, s, kind="subtle", fontsize=7)
                arrow(ax, (bx, 5.5), (sx, 3.5), "")

    legend_box(ax, 14.5, 0.5, [
        ("process", "Module/Function"),
        ("subtle", "Sub-function"),
    ])
    save(fig, name, w_inches=18, h_inches=10)

    cells = [cell_box("top", top, 320, 40, w=160, h=60)]
    for i, br in enumerate(branches):
        label = br[0] if isinstance(br, tuple) else br
        cells.append(cell_box(f"br{i}", label, 40 + i * 150, 200, w=140, h=50))
    (OUT_DIR / f"{name}.drawio").write_text(make_drawio(name, "\n        ".join(cells)))


def diag_14_to_18_structure():
    diag_structure_chart(
        "14-structure-chart-anggota1",
        "anggota1 (Ghaisan, Scraper)",
        "anggota1.py main",
        [
            ("scrape_efek_samping", ["fetch HTML", "parse BS4", "clean"]),
            ("scrape_recall", ["FDA API", "parse JSON"]),
            ("write JSON", ["drug_safety_data.json", "drug_recalls.json"]),
        ],
    )

    diag_structure_chart(
        "15-structure-chart-anggota2",
        "anggota2 (Bimo, CRUD Pasien)",
        "PasienCRUD.menu",
        [
            ("TambahPasien", []),
            ("ReadDataPasien", ["TampilDashboard", "TampilDetail"]),
            ("EditDataPasien", []),
            ("HapusDataPasien", []),
            ("pasien_helper", ["baca_file", "simpan_file", "generate_id"]),
        ],
    )

    diag_structure_chart(
        "16-structure-chart-anggota3",
        "anggota3 (Alia, Visualisasi)",
        "TampilGrafik.entry",
        [
            ("BacaData", ["distribusi_keluhan", "perbandingan_obat", "kunjungan_bulanan"]),
            ("PerbandinganObat", ["heatmap_data"]),
            ("grafik_efek", []),
            ("grafik_kunjungan_bar", []),
            ("grafik_kunjungan_line", []),
            ("grafik_penyakit", []),
            ("grafik_top_efek", []),
        ],
    )

    diag_structure_chart(
        "17-structure-chart-anggota4",
        "anggota4 (Iqbal, Drug Safety)",
        "pencarian_obat.entry",
        [
            ("data_loader", ["muat_database_obat", "muat_database_efek_samping"]),
            ("safety_checker", ["cek_keamanan_obat", "cross_reference"]),
            ("severity scoring", ["ringan=1", "sedang=2", "serius=4"]),
        ],
    )

    diag_structure_chart(
        "18-structure-chart-anggota5",
        "anggota5 (Abhidal, PDF + Auth)",
        "main_anggota5.entry",
        [
            ("auth", ["verifikasi_login", "hanya_admin", "hanya_tkesehatan"]),
            ("tkesehatan_crud", ["tambah", "lihat", "edit", "hapus"]),
            ("export_pdf", ["buat_laporan_pdf"]),
            ("ambil_data", ["ambil_seluruh_data_pasien"]),
        ],
    )


# Execute all
if __name__ == "__main__":
    print("Generating 18 diagrams...")
    diag_01_c4_context()
    diag_02_c4_container()
    diag_03_c4_component_api()
    diag_04_use_case()
    diag_05_class()
    diag_06_sequence_auth()
    diag_07_sequence_patient_create()
    diag_08_sequence_safety()
    diag_09_activity()
    diag_10_state()
    diag_11_er()
    diag_12_deployment()
    diag_13_network()
    diag_14_to_18_structure()
    print(f"Done. PNG outputs in {PNG_DIR}/")
    print(f"Drawio sources in {OUT_DIR}/")
