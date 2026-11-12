import pytest

from tennisplot.data import _format_name


@pytest.mark.parametrize("player_name", [
    "serena williams", "Serena Williams", "SerenaWilliams",
    "  serena   williams ", "SERENA WILLIAMS",
])
def test_format_name_accepts_flexible_formats(player_name):
    assert _format_name(player_name) == "SerenaWilliams"


def test_format_name_rejects_empty_name():
    with pytest.raises(ValueError, match="must not be empty"):
        _format_name("   ")
