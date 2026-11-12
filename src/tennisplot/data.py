"""Download and clean a player's career matches from Tennis Abstract."""


def _format_name(player_name):
    """Turn 'serena williams' or 'SerenaWilliams' into 'SerenaWilliams'."""
    words = player_name.split()
    if not words:
        raise ValueError("player_name must not be empty, e.g. 'Serena Williams'")
    # Fix all-lower or all-upper words; keep inner capitals ('SerenaWilliams')
    fixed = [w.capitalize() if w.islower() or w.isupper() else w[0].upper() + w[1:]
             for w in words]
    return "".join(fixed)
