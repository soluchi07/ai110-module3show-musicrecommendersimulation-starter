"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse
import re

from recommender import load_songs, recommend_songs


def _normalize_reasons(explanation: object) -> list[str]:
    """Normalize score explanations into readable bullet strings."""
    if isinstance(explanation, (list, tuple)):
        return [str(reason) for reason in explanation if str(reason).strip()]

    if explanation:
        text = str(explanation).strip()
        # Keep grouped reason details like "label (+x; raw=y)" on one line.
        if ");" in text:
            chunks = re.split(r"\)\s*;\s*", text)
            return [
                chunk.strip() + (")" if not chunk.strip().endswith(")") else "")
                for chunk in chunks
                if chunk.strip()
            ]

        return [reason.strip() for reason in text.split(";") if reason.strip()]

    return ["No specific reason provided."]


def _print_compact(profile_name: str, user_prefs: dict, recommendations: list[tuple]) -> None:
    """Print one profile's top-k recommendations in a compact table."""
    print("\n" + "=" * 108)
    print(f" {profile_name} ".center(108, "="))
    print("=" * 108)
    print(f"Prefs: {user_prefs}")
    print("-" * 108)
    print(f"{'#':<3} {'Title':<28} {'Score':>7} {'Genre':<12} {'Mood':<12} {'Energy':>7} {'Acoustic':>9}")
    print("-" * 108)

    for idx, rec in enumerate(recommendations, start=1):
        song, score, _ = rec
        title = str(song.get("title", ""))[:28]
        genre = str(song.get("genre", ""))[:12]
        mood = str(song.get("mood", ""))[:12]
        energy = float(song.get("energy", 0.0))
        acousticness = float(song.get("acousticness", 0.0))

        print(
            f"{idx:<3} {title:<28} {score:>7.3f} {genre:<12} {mood:<12} {energy:>7.2f} {acousticness:>9.2f}"
        )


def _print_detailed(profile_name: str, user_prefs: dict, recommendations: list[tuple]) -> None:
    """Print one profile's top-k recommendations with detailed scoring reasons."""
    print("\n" + "=" * 72)
    print(f" {profile_name} ".center(72, "="))
    print("=" * 72)
    print(f"Prefs: {user_prefs}")

    for idx, rec in enumerate(recommendations, start=1):
        # Expected pattern: (song, score, explanation)
        song, score, explanation = rec
        reasons = _normalize_reasons(explanation)

        print(f"\n[{idx}] {song['title']}")
        print(f"    Final Score : {score:.2f}")
        print("    Reasons     :")
        for reason in reasons:
            print(f"      - {reason}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run music recommender profile simulations.")
    parser.add_argument(
        "--view",
        choices=["compact", "detailed"],
        default="compact",
        help="Output style for recommendations.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    songs = load_songs("data/songs.csv")

    # Adversarial and edge-case profiles to probe unexpected ranking behavior.
    profiles = {
        "P1_conflicting_high_energy_sad": {
            "genre": "pop",
            "mood": "sad",
            "energy": 0.9,
            "acoustic_preference": 0.1,
        },
        "P2_unknown_genre_mood_energy_mid": {
            "genre": "vaportrap",
            "mood": "melancholic",
            "energy": 0.5,
            "acoustic_preference": 0.5,
        },
        "P3_extreme_low_energy_hype_mood": {
            "genre": "edm",
            "mood": "happy",
            "energy": 0.0,
            "acoustic_preference": 1.0,
        },
        "P4_out_of_range_energy_and_acoustic": {
            "genre": "rock",
            "mood": "calm",
            "energy": 1.5,
            "acoustic_preference": -0.4,
        },
        "P5_weight_conflict_overrides": {
            "genre_weights": {"pop": 1.0, "metal": 1.0},
            "mood_weights": {"sad": 1.0, "happy": 1.0},
            "energy_range": (0.95, 1.0),
            "acoustic_preference": 1.0,
        },
    }

    for profile_name, user_prefs in profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        if args.view == "compact":
            _print_compact(profile_name, user_prefs, recommendations)
        else:
            _print_detailed(profile_name, user_prefs, recommendations)

    print("\n" + ("=" * (108 if args.view == "compact" else 72)))


if __name__ == "__main__":
    main()
