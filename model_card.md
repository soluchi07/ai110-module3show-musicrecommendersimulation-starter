# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**MoodMatch 1.0**

A lightweight playlist recommender that matches songs to what you're feeling and how energetic you want to be.

---

## 2. Intended Use

MoodMatch is a classroom learning tool, not for real music apps. It shows how recommenders work by scoring songs based on mood, genre, energy, and acoustic style. It assumes you can describe your taste clearly (e.g., "I want upbeat pop" or "melancholic music"). It won't work well if you use made-up genres or describe feelings that don't exist in the dataset. This is meant to teach you how recommendation systems make trade-offs and fail, not to actually pick your next song.

---

## 3. How the Model Works

Imagine a song as a recipe with four ingredients: mood (how it makes you feel), genre (the style, like pop or jazz), energy (how intense it is, 0 = chill, 1 = crazy), and acousticness (how "raw" or "processed" it sounds).

You tell the system what you like. For each song in our catalog, we ask: "Does the mood match?" "Is it the right genre?" "Is the energy level close to what they want?" "Is it acoustic enough (or not acoustic enough)?" We score song on how many of these match.

Mood is the most important (35%), then genre (15%), then energy (50%), then acousticness (10%). This is an experiment—we doubled energy and halved genre to see if it makes recommendations better. Each score gets added up and divided by the total to keep everything fair. The top five songs with the highest scores win.

---

## 4. Data

Our catalog has 20 songs covering 17 different genres and 16 different moods. Genres range from pop and rock to jazz, metal, and afrobeat. Moods include happy, chill, melancholic, intense, romantic, and more. We didn't add or remove songs—this is the starter dataset.

Some big gaps: "chill" and "happy" show up 3 and 2 times, but moods like "melancholic" and "serene" appear only once. This creates bottlenecks—if you really want a melancholic song, there's only one option. Also, the dataset skews toward mid-to-high energy (9 out of 20 songs are above 0.7 energy). If you want a mellow, relaxing experience, choices are limited.

---

## 5. Strengths

The system works well for straightforward tastes: "I want happy pop songs" or "I like energetic rock." If you like the mood first and don't have weird energy requirements, you'll get solid picks. The system also handles contradictions gracefully—when you ask for impossible things (like negative acousticness or 1.5 energy), it clamps the values instead of crashing.

Mood matching is surprisingly good. When we tested a profile that asked for "vaportrap" (a fake genre), the system ignored the broken genre and found actual melancholic songs, which felt right by accident. Energy and acoustic scoring also seem fair—they reward songs that match your preferences without overpowering mood choices.

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly.

### Literal Genre and Mood Matching Creates Filter Bubbles

The system uses exact string matching for genres and moods, meaning any preference that does not exist in the dataset receives zero score contribution. Profile P2 requested the genre "vaportrap," which does not exist in the 20-song catalog, automatically setting genre_match = 0 for every song. Additionally, 11 of the 16 moods in the dataset appear only once (e.g., "melancholic," "serene," "rebellious"), creating a bottleneck where users asking for those rare emotional tones find at most one single-song recommendation for that dimension. This design excludes cross-genre or mood-adjacent recommendations that might capture the spirit of a user's request but use different terminology. The system has no semantic fallback, preventing users with unconventional or niche tastes from receiving diversified, thoughtful recommendations. A more robust approach would use fuzzy matching, mood embeddings, or a similarity graph to suggest emotionally adjacent songs even when exact matches are unavailable.

---

## 7. Evaluation

How you checked whether the recommender behaved as expected.

### Profiles Tested

I tested five deliberately tricky user profiles to probe the system's behavior:

1. **P1 (Conflicting preferences):** Someone who wants sad music but with super high energy (0.9) and low acoustic sound. This is weird because sad songs are usually slow and mellow, not energetic. The system recommended upbeat pop songs like "Gym Hero" because high energy scored so well, but ignored the "sad" request entirely since no sad songs existed in our catalog.

2. **P2 (Unknown taste):** A user asking for "vaportrap" (a made-up genre) with melancholic mood and mid-range energy. Since vaportrap doesn't exist, the system couldn't score genre at all. It fell back to mood and energy, landing on "Blue Porch Light" (a reflective blues song), which felt surprisingly right even though the genre didn't match.

3. **P3 (Opposite poles):** Someone asking for happy mood and extremely low energy (0.0) but high acoustic preference (1.0). Think of someone wanting to feel joyful but in a quiet, acoustic way. The system picked "Rooftop Lights," which is happy and energetic—missing the low-energy ask entirely because high energy and acoustic songs weren't the same ones.

4. **P4 (Out of range):** Requesting rock music, calm mood, impossibly high energy (1.5, which is above the 0–1 scale), and negative acousticness (-0.4, which is impossible). The system clamped these invalid values and still found "Storm Runner," a rock song with high energy, showing it was resilient to bad input.

5. **P5 (Weighted preferences):** Explicitly asking the system to like both pop and metal equally, both sad and happy equally, but only in the 0.95–1.0 energy range, and with maximum acoustic preference. This is inherently contradictory (metal songs are usually not acoustic). The system picked pop songs because they fit the energy range better than metal.

### What We Looked For

For each profile, I checked:

- Whether recommendations matched the stated preferences
- Whether the system made sensible compromises when preferences conflicted
- Whether rare or unknown tastes were handled gracefully

### What Surprised Us

The biggest surprise was how **literal the mood matching worked**. When P2 asked for melancholic music but specified a fake genre, the system ignored the broken genre entirely and nailed the mood—finding the one melancholic song in the dataset. It felt lucky. But this also revealed a trap: users with niche or unknown tastes are locked into whatever 1–2 songs happen to exist for those rare moods, with no room for similar alternatives.

Another surprise: **the weight shift experiment mattered less than expected**. When we doubled the energy weight and halved the genre weight, most top rankings stayed the same. This suggests that for the profiles we tested, energy and genre weren't the deciding factors—mood was. But for energy-focused users (P3, P4), the rebalancing did push acoustic and high-energy songs higher, which felt slightly more intuitive.

### Tests Run

- Baseline run with original weights (mood 35%, genre 30%, energy 25%, acoustic 10%)
- Experimental weight shift (energy doubled to 50%, genre halved to 15%)
- Comparison of top-5 rankings between the two runs
- Manual gut-check: did the resulting recommendations "feel right" for realistic listeners?

---

## 8. Future Work

**Add fuzzy mood matching:** Instead of requiring exact mood matches, the system could suggest "dreamy" when you ask for "melancholic," since they're emotionally adjacent. This would fix the biggest bias (filter bubbles for rare moods).

**Include danceability and tempo:** Right now we ignore how "dance-able" a song is and how fast it's played. Real listeners care about these. We could let users set preferred BPM ranges.

**Explain why songs scored low:** Right now we show top recommendations, but not why other songs lost. Showing negative reasons ("too energetic" or "genre mismatch") would help users understand the system's thinking.

**Diversity boost:** Add a feature that penalizes recommending five songs that are too similar. Right now the top 5 can all be pop songs; real recommendation engines spread across genres for variety.

**Collaborative filtering:** If we had data about which songs users actually liked, we could learn patterns. "Users who like pop also tend to like indie pop" could improve cold-start recommendations.

---

## 9. Personal Reflection

Building this recommender taught me that simple scoring can feel smart but hide huge biases. The biggest lesson: a good algorithm is only as good as the data behind it. When 11 moods show up only once, you've built a system that accidentally ignores quirky users. I also discovered that weight changes matter less than I expected—when we doubled energy importance, rankings barely moved because mood was doing all the work.

Most surprising was how easy it is to fail gracefully. Even when a user asked for a fake genre, the system didn't crash; it just ignored that dimension. But that "graceful failure" is actually a trap—it lets broken input silently produce mediocre results.

This changed how I think about apps like Spotify. When it recommends a song, a lot of invisible trade-offs happen. My taste might ask for three contradictory things, and the algorithm picked one without telling me. Real recommenders also face scale (millions of songs) and cold-start problems (new users with no history). The math here is simple, but real-world systems are way messier.

AI tools were most helpful for analyzing the dataset and calculating statistics quickly. When I needed to count genre and mood distributions or compute energy statistics, AI generated Python code in seconds that would have taken me longer to write from scratch. It also helped me spot biases I'd missed.

But I had to double-check constantly. AI sometimes suggested mathematical normalizations that sounded right but needed verification—like the weight normalization formula, which I had to trace through manually to confirm it kept scores bounded and fair. It also generated bias descriptions that were too formal; I had to rewrite them in plain language to match the assignment requirements.

Most importantly, I couldn't trust AI to understand the experiment I actually ran. When I implemented the weight shift (doubling energy, halving genre), AI initially suggested changes that didn't match my design. I had to verify the actual code and results myself before writing about what changed. AI is great for speed, but understanding my own system and deciding what's correct is still on me.
