"""openFDA real large-scale data acquisition module.

This module is an additive replacement for the drugs.com scraper in
``anggota1/anggota1.py`` after the latter was permanently blocked by
the drugs.com Akamai edge (HTTP 403 on every URL, see
``anggota1/scraper.log``). It pulls real adverse-event and recall data
from the public openFDA REST API and writes JSON files in the same
schema the rest of the codebase already consumes.

Public entry points:
    - ``fetch_main()``: run the full acquisition (script entry point).
    - ``fetch_adverse_events_for_drug()``: per-drug reaction counts.
    - ``fetch_drug_recalls()``: paginated recall pull.

The openFDA API key is read from the ``OPENFDA_API_KEY`` environment
variable. The value is never printed, logged, or committed.

Author: Ghaisan Khoirul Badruzaman / 251524048 / Kelompok B5
"""

from .fetch import (
    fetch_adverse_events_for_drug,
    fetch_drug_recalls,
    main as fetch_main,
)

__all__ = [
    "fetch_adverse_events_for_drug",
    "fetch_drug_recalls",
    "fetch_main",
]
