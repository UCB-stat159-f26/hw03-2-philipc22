"""Plot a player's career matches like the NYT chart of Serena Williams."""

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

COLORS = {"W": "#56C1E8", "L": "#7B2A83"}  # light blue = won, purple = lost
LABELS = {"W": "Match won", "L": "Match lost"}


def _draw_points(ax, matches):
    """One layer of points per result, plus a line at age_diff = 0."""
    for result in ["W", "L"]:
        subset = matches[matches["result"] == result]
        ax.scatter(subset["age"], subset["age_diff"], c=COLORS[result],
                   alpha=0.75, s=15, label=LABELS[result])
    ax.axhline(0, color="gray", lw=0.8)  # same age as the opponent


def _style_axes(ax):
    """Ages on top, light grid, no tick marks and no box around the plot."""
    ax.xaxis.tick_top()
    ax.xaxis.set_major_locator(MultipleLocator(2))   # every 2 years of age
    ax.yaxis.set_major_locator(MultipleLocator(10))  # -10, 0, +10, ...
    ax.yaxis.set_major_formatter(lambda y, pos: f"{y:+.0f}" if y else "0")
    ax.tick_params(length=0)
    ax.grid(color="#e5e5e5")
    ax.set_axisbelow(True)
    ax.spines[:].set_visible(False)


def _add_titles(fig, ax, matches):
    """Title with the player's age range, legend on top, source note."""
    first_age, last_age = int(matches["age"].min()), int(matches["age"].max())
    player = matches["player"].iloc[0]
    ax.set_title(f"{player}'s Matches, Age {first_age} to {last_age}",
                 weight="bold", pad=45)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=2,
              frameon=False)
    fig.subplots_adjust(top=0.82, bottom=0.07)  # room for title and legend
    fig.text(0.1, 0.01, "Source: Tennis Abstract.", fontsize=8, color="gray")


def plot_matches(matches):
    """Scatter plot of a player's matches: age vs. age difference, by result.

    matches: data frame from get_matches() (uses player, age, age_diff, result).
    Returns the matplotlib Axes; save with ax.figure.savefig("plot.png").
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    _draw_points(ax, matches)
    _style_axes(ax)
    _add_titles(fig, ax, matches)
    return ax
