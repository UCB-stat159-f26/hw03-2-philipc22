import matplotlib
import pandas as pd

from tennisplot import plot_matches

matplotlib.use("Agg")  # draw without opening a window


def small_matches():
    return pd.DataFrame({"player": ["Serena Williams"] * 3,
                         "age": [14.1, 20.5, 40.9],
                         "age_diff": [-4.7, 2.0, 21.1],
                         "result": ["L", "W", "W"]})


def test_plot_matches_draws_won_and_lost_points():
    ax = plot_matches(small_matches())
    won, lost = ax.collections  # one scatter layer per result
    assert len(won.get_offsets()) == 2
    assert len(lost.get_offsets()) == 1


def test_plot_matches_title_and_source():
    ax = plot_matches(small_matches())
    assert ax.get_title() == "Serena Williams's Matches, Age 14 to 40"
    assert ax.figure.texts[0].get_text() == "Source: Tennis Abstract."
