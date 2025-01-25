import logging
import os
from collections import defaultdict

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_spotify():
    """Initialize Spotify client with necessary permissions"""
    load_dotenv()

    # Check for required environment variables
    required_vars = [
        "SPOTIFY_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET",
        "SPOTIFY_REDIRECT_URI",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    scope = "playlist-read-private"
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope=scope,
        )
    )


def analyze_artist_genres(sp, artist_id):
    """Get and analyze genres for an artist"""
    try:
        artist = sp.artist(artist_id)
        return {
            "name": artist["name"],
            "genres": artist["genres"],
            "popularity": artist["popularity"],
        }
    except Exception as e:
        logger.error(f"Error getting artist info: {e}")
        return None


def find_related_artists_genres(sp, artist_id):
    """Get genres from related artists"""
    try:
        related = sp.artist_related_artists(artist_id)
        genres_data = []

        for artist in related["artists"]:
            genres_data.append(
                {
                    "artist": artist["name"],
                    "genres": artist["genres"],
                    "popularity": artist["popularity"],
                }
            )

        return genres_data
    except Exception as e:
        logger.error(f"Error getting related artists: {e}")
        return []


def analyze_genre_patterns():
    """Analyze common genre patterns in your playlist"""
    try:
        sp = setup_spotify()
        playlist_id = os.getenv("SPOTIFY_PLAYLIST_ID")

        # Get all tracks from playlist
        results = sp.playlist_items(playlist_id)

        # Collect all unique artists and their genres
        artists_analyzed = {}
        genre_patterns = defaultdict(set)
        word_frequency = defaultdict(int)

        for item in results["items"]:
            if not item["track"] or not item["track"]["artists"]:
                continue

            artist_id = item["track"]["artists"][0]["id"]

            if artist_id not in artists_analyzed:
                artist_data = analyze_artist_genres(sp, artist_id)
                if artist_data:
                    artists_analyzed[artist_id] = artist_data

                    # Analyze genre patterns
                    for genre in artist_data["genres"]:
                        words = genre.split()
                        for word in words:
                            word_frequency[word] += 1

                        # Look for common prefix/suffix patterns
                        if len(words) > 1:
                            genre_patterns[words[0]].add(" ".join(words[1:]))

        # Print analysis
        print("\nArtist Genre Analysis:")
        for artist_data in artists_analyzed.values():
            print(f"\n{artist_data['name']}:")
            for genre in sorted(artist_data["genres"]):
                print(f"  - {genre}")

        print("\nCommon Genre Patterns:")
        for prefix, suffixes in genre_patterns.items():
            if len(suffixes) > 1:  # Show only when there are multiple variations
                print(f"\n'{prefix}' variations:")
                for suffix in sorted(suffixes):
                    print(f"  - {prefix} {suffix}")

        print("\nMost Common Genre Words:")
        common_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
        for word, count in common_words[:10]:
            print(f"  {word}: {count} occurrences")

    except Exception as e:
        logger.error(f"Error analyzing genres: {e}")


if __name__ == "__main__":
    analyze_genre_patterns()
