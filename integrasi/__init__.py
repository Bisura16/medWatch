"""Desktop CLI integration layer for MedWatch.

This package glues the per-anggota modules (``anggota1`` through
``anggota5``) into a single Bahasa-Indonesia command-line menu so a
bidan or admin can run the full Faskes 1 workflow without launching
each module separately. The adapter intentionally never edits the
teammate source files; it dispatches by subprocess or by importing
read-only.
"""
