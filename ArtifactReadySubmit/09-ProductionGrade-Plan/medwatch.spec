# -*- mode: python ; coding: utf-8 -*-
#
# MedWatch PyInstaller spec, one-folder mode.
#
# Status: REFERENCE ONLY. This file is committed in Wave 2 as part of the
# ProductionGrade-ImplementationPlan/ folder. It is NOT executed in Wave 2.
# Execution of `pyinstaller medwatch.spec --clean --noconfirm` happens in
# Phase 2 of the roadmap (Juni-Juli 2026), not now.
#
# Build command (Phase 2):
#     pyinstaller ProductionGrade-ImplementationPlan/build/medwatch.spec \
#                 --clean --noconfirm
#
# Output: dist/MedWatch/
#
# Owner: Ghaisan Khoirul Badruzaman (NIM 251524048)
# Date: 2026-05-18
# Related docs:
#     ProductionGrade-ImplementationPlan/03-packaging-and-distribution.md
#     ProductionGrade-ImplementationPlan/02-offline-implementation-plan.md

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # openFDA snapshot (build-time data, bundled for offline runtime)
        ('anggota1/data/drug_safety_data.json', 'data/anggota1'),
        ('anggota1/data/drug_recalls.json',     'data/anggota1'),
        # Drug catalog and side effect master (anggota4)
        ('anggota4/data/drug_database.json',    'data/anggota4'),
        ('anggota4/data/effect_database.json',  'data/anggota4'),
        # Seed users (akan di-hash on first read per api/storage.py:90)
        ('api/data/users.json',                 'data/api'),
        # User documentation
        ('docs/USER-MANUAL.md',                 'docs'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'jwt',
        'bcrypt',
        'fpdf',
        'matplotlib',
        'numpy',
        'PIL',
        # CustomTkinter sub-imports lazy
        'customtkinter',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Build-time only modules (not for runtime bundle)
        'anggota1.openfda.fetch',
        # Test framework artefacts
        'pytest',
        'unittest',
        '_pytest',
        # Cloud storage client not used in production offline build
        'google.cloud.storage',
        # Wave 2 doc tools, not runtime
        'pandoc',
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
    [],
    exclude_binaries=True,
    name='MedWatch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,        # UPX kompresi sering trigger AV; disabled per 03-packaging Section 6
    console=False,    # GUI app, no console window
    icon='assets/medwatch.ico',          # placeholder; akan dibuat di Phase 2
    version='build/version_info.txt',    # placeholder; akan dibuat di Phase 2
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='MedWatch',
)
