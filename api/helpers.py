"""Response helpers and shared utilities."""
import re
from flask import jsonify


def ok(data=None, status: int = 200):
    return jsonify(data if data is not None else {"status": "ok"}), status


def err(message: str, status: int = 400, **extra):
    payload = {"error": message}
    payload.update(extra)
    return jsonify(payload), status


def strip_password_fields(user: dict) -> dict:
    """Return a copy of user with password fields removed."""
    return {k: v for k, v in user.items() if k not in ("password_hash", "password_plain", "password")}


# Conservative dosage/frequency hint patterns that get stripped after the
# drug name when parsing a bidan-typed `P.resep` string. The bidan's free-form
# format is something like "Asam folat 1x1 sehari" or "Amoxicillin 3x500mg",
# so we strip trailing numerics + common Indonesian/English dosage words.
_DOSAGE_HINT_RE = re.compile(
    r"\s+("
    r"\d+\s*x\s*\d+(?:\s*(?:mg|mcg|ml|g|tablet|tab|kaps|kapsul|sdt|sdm|tetes|cc))?"  # 3x500mg, 1x1
    r"(?:\s*(?:sehari|per\s*hari|hari|sebelum|sesudah|pagi|siang|sore|malam))?"
    r"|"
    r"\d+\s*(?:mg|mcg|ml|g|tablet|tab|kaps|kapsul|sdt|sdm|tetes|cc)\b"           # 500mg
    r"(?:\s*(?:sehari|per\s*hari|hari))?"
    r"|"
    r"\d+\s*(?:sehari|per\s*hari|hari|kali|x)\b"                                  # 1 sehari, 3 kali
    r"|"
    r"\(.*?\)"                                                                    # parenthetical note
    r").*$",
    re.IGNORECASE,
)

# Non-name tokens that may follow a drug name as a separate fragment.
_TRAILING_NOTE_RE = re.compile(
    r"\s+(prn|p\.r\.n|jika\s+perlu|bila\s+perlu|qd|bid|tid|qid)\b.*$",
    re.IGNORECASE,
)


def parse_resep_to_meds(resep_text: str | None) -> list[str]:
    """Parse a bidan-typed `P.resep` field into a clean list of drug names.

    The bidan input is free-form, e.g.:
        "Asam folat 1x1 sehari\\nAmoxicillin 3x500mg"
        "Asam Folat, Paracetamol"
        "Vitamin B6 10mg 2x sehari; Asam Folat 1x1"

    Parser rules (documented for traceability):
      1. Split on newline, semicolon, and comma; keep order.
      2. Trim whitespace; drop empty fragments.
      3. Strip trailing dosage hints like `1x1 sehari`, `3x500mg`, `500mg`,
         `2 kali sehari`, parenthetical notes, and Latin frequency tokens
         (prn, qd, bid, tid, qid).
      4. Collapse internal whitespace.
      5. Deduplicate case-insensitively while preserving first-seen casing.
      6. Drop fragments that end up empty or are pure digits after stripping.

    Empty / non-string input yields an empty list.
    """
    if not resep_text or not isinstance(resep_text, str):
        return []

    # Split on newline, semicolon, or comma.
    raw_fragments = re.split(r"[\n;,]+", resep_text)

    seen_lower: set[str] = set()
    out: list[str] = []
    for frag in raw_fragments:
        if not frag:
            continue
        name = frag.strip()
        if not name:
            continue
        # Strip dosage / frequency hints from the tail.
        name = _DOSAGE_HINT_RE.sub("", name)
        name = _TRAILING_NOTE_RE.sub("", name)
        # Collapse internal whitespace and strip again.
        name = re.sub(r"\s+", " ", name).strip(" .;:-")
        if not name:
            continue
        # Reject fragments that are purely numeric after cleanup.
        if name.isdigit():
            continue
        key = name.lower()
        if key in seen_lower:
            continue
        seen_lower.add(key)
        out.append(name)
    return out
