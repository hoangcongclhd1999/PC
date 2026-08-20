import re


STATION_RE = re.compile(
    r"\bstation\s*#?\s*(\d{1,2})\b",
    re.IGNORECASE,
)

SINGLE_SLOT_RE = re.compile(
    r"^\s*([1-8])\s*[:=\-]?\s*(P|F|PASS|FAIL)\s*$",
    re.IGNORECASE,
)

COMPACT_SLOT_RE = re.compile(
    r"\bslot\s*((?:\d+\s*,\s*)*\d+)\s*(P|F|PASS|FAIL)\b",
    re.IGNORECASE,
)


def parse_line(text):
    """
    Return dict:
    {
        "station": int|None,
        "status": "Waiting"|"Testing"|None,
        "results": {slot: "Pass"/"Fail"},
        "clear": bool,
        "slot_header": bool,
        "heartbeat": bool,
        "raw": str,
    }

    Supported:
        Station 4: W
        Station 4: T
        slot:
        1 P
        4 F
        D

    Old compact format is still accepted:
        Station4 T, slot1,2,3 P, slot4 F
    """
    raw = text.strip()

    result = {
        "station": None,
        "status": None,
        "results": {},
        "clear": False,
        "slot_header": False,
        "heartbeat": False,
        "raw": raw,
    }

    if not raw:
        return result

    if re.fullmatch(r"\s*slot\s*:?\s*", raw, re.IGNORECASE):
        result["slot_header"] = True
        return result

    if re.fullmatch(r"\s*D\s*", raw, re.IGNORECASE):
        result["clear"] = True
        result["status"] = "Waiting"
        return result

    station_match = STATION_RE.search(raw)
    if station_match:
        station = int(station_match.group(1))
        if 1 <= station <= 16:
            result["station"] = station

    remainder = STATION_RE.sub(" ", raw, count=1)

    if re.search(r"\bHB\b|\bHEARTBEAT\b", remainder, re.IGNORECASE):
        result["heartbeat"] = True

    if re.search(r"\bD\b", remainder, re.IGNORECASE):
        result["clear"] = True
        result["status"] = "Waiting"
    elif re.search(r"\bT\b|\bTESTING\b", remainder, re.IGNORECASE):
        result["status"] = "Testing"
    elif re.search(r"\bW\b|\bWAITING\b", remainder, re.IGNORECASE):
        result["status"] = "Waiting"

    single = SINGLE_SLOT_RE.fullmatch(raw)
    if single:
        slot = int(single.group(1))
        token = single.group(2).upper()
        result["results"][slot] = (
            "Pass" if token in ("P", "PASS") else "Fail"
        )
        return result

    for match in COMPACT_SLOT_RE.finditer(raw):
        slots_text = match.group(1)
        token = match.group(2).upper()
        value = "Pass" if token in ("P", "PASS") else "Fail"

        for slot_text in re.findall(r"\d+", slots_text):
            slot = int(slot_text)
            if 1 <= slot <= 8:
                result["results"][slot] = value

    return result
