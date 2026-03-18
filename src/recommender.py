import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a numeric value to the inclusive range [low, high]."""
    return max(low, min(high, value))


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences and return score plus reasons."""
    genre_weights: Dict[str, float] = {
        str(k).lower(): float(v)
        for k, v in user_prefs.get("genre_weights", {}).items()
    }
    mood_weights: Dict[str, float] = {
        str(k).lower(): float(v)
        for k, v in user_prefs.get("mood_weights", {}).items()
    }

    # Backward-compatible fallbacks for starter-style prefs.
    if not genre_weights and user_prefs.get("genre"):
        genre_weights[str(user_prefs["genre"]).lower()] = 1.0
    if not mood_weights and user_prefs.get("mood"):
        mood_weights[str(user_prefs["mood"]).lower()] = 1.0

    energy_range = user_prefs.get("energy_range")
    if not energy_range and user_prefs.get("energy") is not None:
        target = float(user_prefs["energy"])
        energy_range = (_clamp(target - 0.1), _clamp(target + 0.1))
    if not energy_range:
        energy_range = (0.0, 1.0)
    e_min, e_max = float(energy_range[0]), float(energy_range[1])

    acoustic_preference = float(user_prefs.get("acoustic_preference", 0.5))

    song_genre = str(song.get("genre", "")).lower()
    song_mood = str(song.get("mood", "")).lower()
    song_energy = float(song.get("energy", 0.0))
    song_acousticness = float(song.get("acousticness", 0.0))

    genre_match = _clamp(genre_weights.get(song_genre, 0.0))
    mood_match = _clamp(mood_weights.get(song_mood, 0.0))

    if e_min <= song_energy <= e_max:
        energy_match = 1.0
    else:
        distance = min(abs(song_energy - e_min), abs(song_energy - e_max))
        energy_match = _clamp(1.0 - distance)

    acoustic_match = _clamp(1.0 - abs(song_acousticness - acoustic_preference))

    mood_weight = 0.35
    genre_weight = 0.30
    energy_weight = 0.25
    acoustic_weight = 0.10

    mood_contrib = mood_weight * mood_match
    genre_contrib = genre_weight * genre_match
    energy_contrib = energy_weight * energy_match
    acoustic_contrib = acoustic_weight * acoustic_match

    score = mood_contrib + genre_contrib + energy_contrib + acoustic_contrib

    reasons = [
        f"mood match (+{mood_contrib:.3f}; raw={mood_match:.2f})",
        f"genre match (+{genre_contrib:.3f}; raw={genre_match:.2f})",
        f"energy fit (+{energy_contrib:.3f}; raw={energy_match:.2f}, range={e_min:.2f}-{e_max:.2f})",
        f"acoustic fit (+{acoustic_contrib:.3f}; raw={acoustic_match:.2f}, pref={acoustic_preference:.2f})",
    ]

    return score, reasons

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    # Multiple tastes with strength (0.0 to 1.0)
    genre_weights: Dict[str, float] = field(default_factory=dict)
    mood_weights: Dict[str, float] = field(default_factory=dict)

    # Prefer a range, not a single target
    energy_range: Tuple[float, float] = (0.0, 1.0)

    # Continuous preference instead of yes/no
    # 0.0 = dislikes acoustic, 1.0 = strongly likes acoustic
    acoustic_preference: float = 0.5

    # Optional extra signals for diversity + control
    diversity_boost: float = 0.2      # promotes varied top-k results


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a list of songs."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs for a user profile by descending score."""
        scored: List[Tuple[Song, float]] = []
        user_prefs = {
            "genre_weights": user.genre_weights,
            "mood_weights": user.mood_weights,
            "energy_range": user.energy_range,
            "acoustic_preference": user.acoustic_preference,
        }
        for song in self.songs:
            song_dict = {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "tempo_bpm": song.tempo_bpm,
                "valence": song.valence,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((song, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable score explanation string for one song."""
        user_prefs = {
            "genre_weights": user.genre_weights,
            "mood_weights": user.mood_weights,
            "energy_range": user.energy_range,
            "acoustic_preference": user.acoustic_preference,
        }
        song_dict = {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }
        score, reasons = score_song(user_prefs, song_dict)
        return f"Score {score:.3f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dictionaries."""
    songs: List[Dict] = []

    with open(csv_path, mode="r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )

    print(f"Loaded songs: {len(songs)}")
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return top-k (song, score, explanation) tuples for the given preferences."""
    scored_results = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    return sorted(scored_results, key=lambda item: item[1], reverse=True)[:k]
