"""Download and clean a player's career matches from Tennis Abstract."""

import json
import re
import warnings

import pandas as pd
import requests

BASE_URL = "https://www.tennisabstract.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (stat159 homework)"}

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

# Columns of the clean data frame, in order
COLUMNS = ["date", "tournament", "level", "opponent", "result",
           "age", "opp_age", "age_diff"]


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


def _parse_dob(page_html):
    """Return the birth date on a player page ('var dob = 19810926;'), or None."""
    found = re.search(r"\bdob\s*=\s*['\"]?(\d{8})", page_html)
    if found is None:
        return None
    return pd.to_datetime(found.group(1), format="%Y%m%d")


def _drop_missing_opp_age(df):
    """Drop matches with no opponent age, with a warning saying how many."""
    missing = df["opp_age"].isna()
    if missing.any():
        warnings.warn(f"Dropped {missing.sum()} matches with no opponent age.")
    return df[~missing]


def _clean_matches(raw, player_dob):
    """Drop walkovers, add age, opp_age and age_diff, keep COLUMNS."""
    # Walkovers: no tennis was played. Retirements ("RET") are kept.
    df = raw[~raw["score"].str.contains("W/O", na=False)].copy()
    df["age"] = _years_between(player_dob, df["date"])
    df["opp_age"] = _compute_opp_age(df)
    df = _drop_missing_opp_age(df)
    df["age_diff"] = df["age"] - df["opp_age"]  # > 0: player was older
    return df[COLUMNS].sort_values("date").reset_index(drop=True)


def _fetch_text(url):
    """Download `url` and return its text, or None if the page doesn't exist."""
    response = requests.get(url, headers=HEADERS, timeout=60)
    if response.status_code == 404:
        return None
    response.raise_for_status()  # any other error (403, 500, ...) stops here
    return response.text


def _download_career(name_key):
    """Return the text of the player's Career JS file; error if unknown."""
    js_text = _fetch_text(f"{BASE_URL}/jsmatches/{name_key}Career.js")
    if js_text is None:
        raise ValueError(f"No Tennis Abstract player named '{name_key}'. "
                         "Check the spelling, e.g. 'Serena Williams'.")
    return js_text


def _download_dob(name_key):
    """Return the player's birth date from their Tennis Abstract page."""
    for page in ["wplayer", "player"]:  # women's page, then men's page
        page_html = _fetch_text(f"{BASE_URL}/cgi-bin/{page}.cgi?p={name_key}")
        player_dob = _parse_dob(page_html or "")
        if player_dob is not None:
            return player_dob
    raise ValueError(f"No birth date for '{name_key}' on Tennis Abstract, "
                     "so ages can't be computed.")


def _display_name(name_key):
    """Turn 'SerenaWilliams' into 'Serena Williams' (used in the plot title)."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name_key)


def get_matches(player_name):
    """Download a player's career matches from Tennis Abstract and clean them.

    player_name: e.g. "serena williams", "Serena Williams" or "SerenaWilliams".
    Returns one row per match (walkovers dropped) with columns player, date,
    tournament, level, opponent, result ("W"/"L"), age, opp_age and
    age_diff = age - opp_age (> 0 means the player was older).
    Raises ValueError if Tennis Abstract has no player with that name.
    """
    name_key = _format_name(player_name)
    raw = _parse_matches(_download_career(name_key))
    matches = _clean_matches(raw, _download_dob(name_key))
    matches.insert(0, "player", _display_name(name_key))
    return matches
