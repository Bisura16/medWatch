# medwatch_desktop.spec
# PyInstaller spec for the MedWatch desktop backend bundle.
#
# Build (from backend repo root, inside a Python 3.13 venv with
# requirements.txt and pyinstaller installed):
#
#   pyinstaller medwatch_desktop.spec --clean --noconfirm
#
# Output:
#   dist/medwatch-backend          (macOS, Linux)
#   dist/medwatch-backend.exe      (Windows host)
#
# The bundle binds to 127.0.0.1 on an OS-assigned ephemeral port
# when MEDWATCH_DESKTOP=1 and prints MEDWATCH_BACKEND_PORT=<n> to
# stdout so the Electron parent can capture it.

block_cipher = None

a = Analysis(
    ["api/desktop_entry.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("api/static", "api/static"),
        # Seed users/patients copied to the writable data dir on first launch.
        ("api/data", "api/data"),
        # Teammate modules loaded at runtime by api.bootstrap via sys.path,
        # plus the JSON data the PDF/safety/visualization routes read by path.
        ("anggota1/data", "anggota1/data"),
        ("anggota2", "anggota2"),
        ("anggota4", "anggota4"),
        ("anggota5", "anggota5"),
    ],
    hiddenimports=[
        "flask",
        "flask_cors",
        "werkzeug.middleware",
        "werkzeug.middleware.proxy_fix",
        "jwt",
        "bcrypt",
        "argon2",
        "argon2.low_level",
        "_cffi_backend",
        "fpdf",
        "sqlite3",
        "api.app",
        "api.config",
        "api.bootstrap",
        "api.storage",
        "api.helpers",
        "api.middleware",
        "api.auth",
        "api.security",
        "api.ratelimit",
        "api.drug_db",
        "api.routes.health",
        "api.routes.auth_routes",
        "api.routes.patient_routes",
        "api.routes.drug_routes",
        "api.routes.safety_routes",
        "api.routes.visualization_routes",
        "api.routes.pdf_routes",
        "api.routes.admin_routes",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "google.cloud.storage",
        "google.cloud",
        "google.api_core",
        "google.auth",
        "gunicorn",
        "matplotlib",
        "numpy",
        "PIL",
        "scipy",
        "pandas",
        "tkinter",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "IPython",
        "jupyter",
        "pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="medwatch-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
