from pathlib import Path

import pandas as pd
import pytest
import requests

from tennisplot.data import (_clean_matches, _compute_opp_age, _download_career,
                             _download_dob, _format_name, _parse_dob,
                             _parse_matches)

MOCK_DIR = Path(__file__).parent / "mock"
SERENA_DOB = pd.Timestamp("1981-09-26")  # mock female rows are Serena's
NADAL_DOB = pd.Timestamp("1986-06-03")   # mock male rows are Nadal's


class FakeResponse:
    """Stands in for requests' Response, so tests never hit the live server."""

    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")


def fake_site(pages):
    """Return a fake requests.get: URL containing a key -> (status, text)."""
    def fake_get(url, **kwargs):
        for key, (status_code, text) in pages.items():
            if key in url:
                return FakeResponse(status_code, text)
        return FakeResponse(404)
    return fake_get


@pytest.fixture
def female_raw():
    return _parse_matches((MOCK_DIR / "female_career.js").read_text())


@pytest.fixture
def male_raw():
    return _parse_matches((MOCK_DIR / "male_career.js").read_text())


# _format_name ---------------------------------------------------------------

@pytest.mark.parametrize("player_name", [
    "serena williams", "Serena Williams", "SerenaWilliams",
    "  serena   williams ", "SERENA WILLIAMS",
])
def test_format_name_accepts_flexible_formats(player_name):
    assert _format_name(player_name) == "SerenaWilliams"


def test_format_name_rejects_empty_name():
    with pytest.raises(ValueError, match="must not be empty"):
        _format_name("   ")


# _parse_matches -------------------------------------------------------------

def test_parse_matches_reads_female_file(female_raw):
    assert len(female_raw) == 3
    first = female_raw.iloc[0]
    assert first["date"] == pd.Timestamp("1995-10-30")
    assert first["opponent"] == "Anne Miller"
    assert first["result"] == "L"
    assert first["opp_birth_or_age"] == "19770119"


def test_parse_matches_reads_male_file(male_raw):
    assert len(male_raw) == 3
    last = male_raw.iloc[2]
    assert last["opponent"] == "Israel Matos Gil"
    assert last["result"] == "W"
    assert last["opp_birth_or_age"] == "18.7597535934"


# _compute_opp_age -----------------------------------------------------------

def test_compute_opp_age_from_birth_date(female_raw):
    # Anne Miller: born 1977-01-19, match on 1995-10-30 -> 6858 days
    opp_age = _compute_opp_age(female_raw)
    assert opp_age.iloc[0] == pytest.approx(6858 / 365.25)


def test_compute_opp_age_uses_given_age(male_raw):
    opp_age = _compute_opp_age(male_raw)
    assert opp_age.tolist() == pytest.approx([22.264202601, 24.2902121834,
                                              18.7597535934])


def test_compute_opp_age_missing_is_nan(female_raw):
    female_raw.loc[0, "opp_birth_or_age"] = ""
    assert _compute_opp_age(female_raw).isna().tolist() == [True, False, False]


# _parse_dob -----------------------------------------------------------------

def test_parse_dob_finds_birth_date():
    page_html = "<script>var fullname = 'Serena Williams';\nvar dob = 19810926;</script>"
    assert _parse_dob(page_html) == pd.Timestamp("1981-09-26")


def test_parse_dob_ignores_other_dob_words():
    # The real page also has JS code like `function age(dobString) {...}`
    page_html = "function age(dobString) { dobString.substring(0, 4) }"
    assert _parse_dob(page_html) is None


def test_parse_dob_missing_returns_none():
    assert _parse_dob("<html>no player here</html>") is None


# _clean_matches -------------------------------------------------------------

def test_clean_matches_female_ages(female_raw):
    clean = _clean_matches(female_raw, SERENA_DOB)
    first = clean.iloc[0]  # 1995-10-30 vs Anne Miller (born 1977-01-19)
    assert first["age"] == pytest.approx(5147 / 365.25)       # about 14.1
    assert first["opp_age"] == pytest.approx(6858 / 365.25)   # about 18.8
    assert first["age_diff"] == pytest.approx((5147 - 6858) / 365.25)


def test_clean_matches_male_ages(male_raw):
    clean = _clean_matches(male_raw, NADAL_DOB)
    first = clean.iloc[0]  # 2001-09-10 vs Guillermo Platel (age 22.26)
    assert first["age"] == pytest.approx(5578 / 365.25)       # about 15.3
    assert first["age_diff"] == pytest.approx(5578 / 365.25 - 22.264202601)


def test_clean_matches_columns(female_raw):
    clean = _clean_matches(female_raw, SERENA_DOB)
    assert list(clean.columns) == ["date", "tournament", "level", "opponent",
                                   "result", "age", "opp_age", "age_diff"]


def test_clean_matches_drops_walkovers(female_raw):
    female_raw.loc[1, "score"] = "W/O"
    clean = _clean_matches(female_raw, SERENA_DOB)
    assert "Alexia Dechaume Balleret" not in clean["opponent"].tolist()
    assert len(clean) == 2


def test_clean_matches_keeps_retirements(female_raw):
    female_raw.loc[1, "score"] = "6-4 2-1 RET"
    assert len(_clean_matches(female_raw, SERENA_DOB)) == 3


def test_clean_matches_warns_about_missing_opp_age(female_raw):
    female_raw.loc[0, "opp_birth_or_age"] = ""
    with pytest.warns(UserWarning, match="Dropped 1 matches"):
        clean = _clean_matches(female_raw, SERENA_DOB)
    assert len(clean) == 2


# downloads (requests.get is replaced by a fake: no live server) -------------

def test_download_career_unknown_player(monkeypatch):
    monkeypatch.setattr(requests, "get", fake_site({}))  # every URL -> 404
    with pytest.raises(ValueError, match="No Tennis Abstract player named "
                                         "'GastonSanchez'"):
        _download_career("GastonSanchez")


def test_download_career_other_http_error(monkeypatch):
    monkeypatch.setattr(requests, "get", fake_site({"jsmatches": (500, "")}))
    with pytest.raises(requests.HTTPError):
        _download_career("SerenaWilliams")


def test_download_dob_tries_men_page(monkeypatch):
    pages = {"wplayer": (200, "<html></html>"),
             "player.cgi": (200, "var dob = 19860603;")}
    monkeypatch.setattr(requests, "get", fake_site(pages))
    assert _download_dob("RafaelNadal") == NADAL_DOB


def test_download_dob_missing(monkeypatch):
    monkeypatch.setattr(requests, "get", fake_site({"cgi-bin": (200, "")}))
    with pytest.raises(ValueError, match="No birth date"):
        _download_dob("GastonSanchez")
