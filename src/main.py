"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import re

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 72)
    print(" TOP RECOMMENDATIONS ".center(72, "="))
    print("=" * 72)

    for idx, rec in enumerate(recommendations, start=1):
        # Expected pattern: (song, score, explanation)
        song, score, explanation = rec

        # Normalize reasons so this works for string or list-like explanations.
        if isinstance(explanation, (list, tuple)):
            reasons = [str(reason) for reason in explanation if str(reason).strip()]
        elif explanation:
            text = str(explanation).strip()
            # Keep grouped reason details like "label (+x; raw=y)" on one line.
            if ");" in text:
                chunks = re.split(r"\)\s*;\s*", text)
                reasons = [
                    chunk.strip() + (")" if not chunk.strip().endswith(")") else "")
                    for chunk in chunks
                    if chunk.strip()
                ]
            else:
                reasons = [reason.strip() for reason in text.split(";") if reason.strip()]
        else:
            reasons = ["No specific reason provided."]

        print(f"\n[{idx}] {song['title']}")
        print(f"    Final Score : {score:.2f}")
        print("    Reasons     :")
        for reason in reasons:
            print(f"      - {reason}")

    print("\n" + "=" * 72)


if __name__ == "__main__":
    main()
