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
- **Men's Career files end in 2016:** Tennis Abstract's `RafaelNadalCareer.js`
  ends on 2016-10-10, and newer matches are in a separate file
  (`RafaelNadal.js`). The package uses only the Career files, as the
  instructions say, so men's plots stop around 2016.
- **Ages** are in years, computed as days / 365.25, as in HW2.
- **Walkovers** (`W/O`) are dropped because no tennis was played.
  **Retirements** (`RET`) are kept because the match was partly played.
- **Matches with no opponent age** are dropped, with a warning that says how
  many.
- **Invalid names:** Tennis Abstract returns 404 for an unknown player's
  Career file, which `get_matches` turns into a `ValueError`.
- **Rate limits:** Tennis Abstract answers "429 Too Many Requests" when
  pages are requested too fast, so downloads wait (10, 30, then 60 seconds)
  and retry before giving up. Each player needs only two requests: the
  Career file and one player page.
- **Name formatting** only removes spaces and capitalizes words, so names
  whose Tennis Abstract spelling differs (e.g. accents or hyphens) need to be
  typed as Tennis Abstract spells them.

## Personal Reflections

- **A package is organized for someone else to use.** At first the package
  layout felt uncomfortable compared with HW2's scripts, which I just ran top
  to bottom. Now I understand how the organization works: `pyproject.toml`
  makes `pip install git+...` possible, `src/tennisplot/` holds the code,
  `tests/` holds the tests, and the data and plot code live in separate
  modules. It also forced me to remove HW2's hard-coded pieces (Serena's
  birth date, the 14 to 40 axis) so that any player name works.
- **Testing on mock data is easier in every way.** Computationally, all 33
  tests run in about a second without downloading anything. Logistically,
  the live site rate-limited me with "429 Too Many Requests" during my own
  install check, so tests that hit it would fail for reasons that have
  nothing to do with my code. What made this possible was writing the
  parsing functions to take text instead of URLs, and replacing
  `requests.get` with a fake in the tests.
- **The same file layout can mean different things.** The female and male
  Career files use the same field positions, but field 16 is the opponent's
  birth date for women ("19770119") and their age for men ("22.26"). Instead
  of asking the user for the player's gender, the code checks whether the
  value is exactly 8 digits. That handles both file types, and the mock
  files test both paths.
- **Small functions and small commits helped me stay organized.** The
  20-line limit split HW2's roughly 35-line plotting function into four short
  functions, each easy to read and test. Committing one step at a time, with
  tests passing, made it easy to keep track of progress and to go back if
  something broke. For example, the two rate-limit fixes were separate
  commits made after the package already worked.
- **AI help worked well, but I had to steer the workflow.** The assistant
  was useful for planning the structure, explaining design choices, and
  writing tests. It didn't always fit how I work, though. It gave me file
  contents to paste into the terminal, which bash tried to run as commands,
  and a README with code blocks inside it got cut off mid-paste. Next time
  I would create files directly in the JupyterLab editor.

## AI Assistance

I used an AI assistant (Claude, Anthropic) as a pair-programming partner to
plan the package structure, draft and test functions, and explain design
choices. I ran every command and test myself, checked the results against my
HW2 numbers (1,016 Serena matches: 858 wins, 158 losses), and made each
commit myself.
