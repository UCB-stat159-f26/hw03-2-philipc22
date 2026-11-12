# HW3: tennisplot

STAT 159, Philip Chiu

## Aims

`tennisplot` is a Python package that downloads any player's career matches
from [Tennis Abstract](https://www.tennisabstract.com) and plots them like the
New York Times chart of Serena Williams's matches from HW2: each point is one
match, placed by the player's age (x) and the age difference with the
opponent (y), and colored by win or loss.

## Installation

```bash
pip install git+https://github.com/UCB-stat159-f26/hw03-2-philipc22.git
```

This also installs the dependencies: `pandas`, `matplotlib` and `requests`
(Python 3.9 or newer).

## Usage

```python
import tennisplot

# Serena Williams data and plot
serena = tennisplot.get_matches("serena williams")
tennisplot.plot_matches(serena)

# Rafael Nadal data and plot
rafa = tennisplot.get_matches("Rafael Nadal")
tennisplot.plot_matches(rafa)

# An unknown player gives a meaningful error:
# ValueError: No Tennis Abstract player named 'GastonSanchez'. ...
unknown_player = tennisplot.get_matches("GastonSanchez")
```

### `get_matches(player_name)`

Accepts names like `"serena williams"`, `"Serena Williams"` or
`"SerenaWilliams"`, and returns a data frame with one row per match:

| Column | Description |
|---|---|
| `player` | Player's name, e.g. "Serena Williams" (used in the plot title) |
| `date` | Date of the match |
| `tournament`, `level` | Tournament name and Tennis Abstract level code |
| `opponent` | Opponent's name |
| `result` | `"W"` if the player won, `"L"` if they lost |
| `age`, `opp_age` | Ages of the player and the opponent, in years |
| `age_diff` | `age - opp_age`: positive means the player was older |

### `plot_matches(matches)`

Takes the data frame from `get_matches` and draws the scatter plot (light
blue = won, purple = lost, ages on top, no annotations). It returns the
matplotlib Axes. To save the plot:

```python
ax = tennisplot.plot_matches(serena)
ax.figure.savefig("serena.png")
```

## Repository Structure

| Path | Description |
|------|-------------|
| `README.md` | This file. |
| `instructions.md` | Assignment instructions. |
| `pyproject.toml` | Package name, version and dependencies (what makes `pip install` work). |
| `src/tennisplot/__init__.py` | Exposes the two public functions. |
| `src/tennisplot/data.py` | `get_matches()` and its private helpers: name formatting, download, JS parsing, ages, cleaning. |
| `src/tennisplot/plot.py` | `plot_matches()` and its private helpers for points, axes and titles. |
| `tests/test_data.py` | Tests for name formatting, parsing, ages, cleaning and error messages. |
| `tests/test_plot.py` | Tests that the plot has the right points, title and source note. |
| `tests/mock/` | Mock female and male Career JS files from the instructions. |

## Running the Tests

From the top folder of the repository:

```bash
pip install -e . pytest
pytest
```

The tests never contact tennisabstract.com. Parsing and cleaning are tested
on the mock JS files, and the download functions are tested with a fake
`requests.get` that returns mock pages or a 404.

## Main Judgment Calls

- **Player's own birth date:** the Career JS file only has the opponent's
  birth date or age, so the player's birth date is read from their Tennis
  Abstract page (`var dob = YYYYMMDD`): the women's page if the Career file
  has opponents' birth dates, the men's page otherwise.
- **Female vs. male files:** both use the same field positions. Field 16 is
  treated as a birth date when it is exactly 8 digits (women) and as an age
  otherwise (men), so the package never needs to know the player's gender.
- **Ages** are in years, computed as days / 365.25, as in HW2.
- **Walkovers** (`W/O`) are dropped because no tennis was played.
  **Retirements** (`RET`) are kept because the match was partly played.
- **Matches with no opponent age** are dropped, with a warning that says how
  many.
- **Invalid names:** Tennis Abstract returns 404 for an unknown player's
  Career file, which `get_matches` turns into a `ValueError`.
- **Name formatting** only removes spaces and capitalizes words, so names
  whose Tennis Abstract spelling differs (e.g. accents or hyphens) need to be
  typed as Tennis Abstract spells them.

## Personal Reflections

TODO (Philip)

## AI Assistance

I used an AI assistant (Claude, Anthropic) as a pair-programming partner to
plan the package structure, draft and test functions, and explain design
choices. I ran every command and test myself, checked the results against my
HW2 numbers (1,016 Serena matches: 858 wins, 158 losses), and made each
commit myself.
