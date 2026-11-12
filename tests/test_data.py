from pathlib import Path

import pandas as pd
import pytest

from tennisplot.data import _compute_opp_age, _format_name, _parse_matches

MOCK_DIR = Path(__file__).parent / "mock"


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
