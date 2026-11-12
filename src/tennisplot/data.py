"""Download and clean a player's career matches from Tennis Abstract."""

import json

import pandas as pd

# Positions of the fields we keep inside each match array.
# Same positions for women and men; only the meaning of 16 differs:
# women's files give the opponent's birth date ("19770119"),
# men's files give the opponent's age ("22.264202601").
FIELDS = {
    0: "date",               # "19951030"
    1: "tournament",         # "Canadian Open"
    3: "level",              # "W", "G", "C", ...
    4: "result",             # "W" = player won, "L" = player lost
    9: "score",              # "6-1 6-1" ("W/O" = walkover)
    11: "opponent",          # "Anne Miller"
    16: "opp_birth_or_age",  # see above
}


def _format_name(player_name):
    """Turn 'serena williams' or 'SerenaWilliams' into 'SerenaWilliams'."""
    words = player_name.split()
    if not words:
        raise ValueError("player_name must not be empty, e.g. 'Serena Williams'")
    # Fix all-lower or all-upper words; keep inner capitals ('SerenaWilliams')
    fixed = [w.capitalize() if w.islower() or w.isupper() else w[0].upper() + w[1:]
             for w in words]
    return "".join(fixed)


def _parse_matches(js_text):
    """Turn the text of a Career JS file into a raw table, one row per match."""
    # The data is the [[...], [...]] array after `var morematchmx =`
    array_text = js_text[js_text.index("["): js_text.rindex("]") + 1]
    matches = json.loads(array_text)
    rows = [{name: m[i] for i, name in FIELDS.items()} for m in matches]
    raw = pd.DataFrame(rows)
    raw["date"] = pd.to_datetime(raw["date"], format="%Y%m%d")
    return raw


def _years_between(start, end):
    """Return the years from `start` to `end` dates (days / 365.25)."""
    return (end - start).dt.days / 365.25


def _compute_opp_age(raw):
    """Opponent's age in years, from a birth date (women) or an age (men)."""
    values = raw["opp_birth_or_age"]
    is_dob = values.str.fullmatch(r"\d{8}")  # YYYYMMDD
    dob = pd.to_datetime(values.where(is_dob), format="%Y%m%d", errors="coerce")
    age_from_dob = _years_between(dob, raw["date"])
    age_given = pd.to_numeric(values.where(~is_dob), errors="coerce")  # "" -> NaN
    return age_from_dob.where(is_dob, age_given)
