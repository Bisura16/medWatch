"""Test scripts for the MedWatch API.

The primary entry point is ``smoke_test.py``, an end-to-end script
that exercises every public route against a running server. There
is no pytest configuration here on purpose; the smoke test runs as
a plain script so it can be executed both locally and against the
deployed Cloud Run revision.
"""
