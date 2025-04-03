import logging
import os
from time import sleep
from typing import Dict, List

import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_spotify():
    """Initialize Spotify client with necessary permissions"""
    # Updated scope to include audio-features for tempo access
    scope = "playlist-read-private user-library-read"
    try:
        return spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope=scope,
            )
        )
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {str(e)}")
        raise


def get_playlist_tracks(sp: spotipy.Spotify, playlist_id: str) -> List[Dict]:
    """Get all tracks from a playlist"""
    tracks = []
    try:
        results = sp.playlist_items(playlist_id)
        tracks.extend(results["items"])

        while results["next"]:
            results = sp.next(results)
            tracks.extend(results["items"])

        logger.info(f"Retrieved {len(tracks)} tracks from playlist")
        return tracks
    except Exception as e:
        logger.error(f"Error fetching playlist tracks: {str(e)}")
        raise


def get_artist_genres(sp: spotipy.Spotify, artist_id: str) -> List[str]:
    """Get genres for an artist with rate limiting"""
    try:
        artist_info = sp.artist(artist_id)
        sleep(0.25)  # Add a small delay to avoid rate limiting
        return artist_info.get("genres", [])
    except Exception as e:
        logger.error(f"Error getting artist genres: {str(e)}")
        return []


def get_audio_features(sp: spotipy.Spotify, track_id: str) -> Dict:
    """Get audio features for a track including tempo"""
    try:
        features = sp.audio_features(track_id)[0]
        sleep(0.25)  # Add delay to avoid rate limiting
        return features
    except Exception as e:
        logger.error(f"Error getting audio features: {str(e)}")
        return {}


def get_track_details(sp: spotipy.Spotify, track: Dict) -> Dict:
    """Get genre and audio feature information about a track"""
    try:
        track_data = track["track"]
        artist_id = track_data["artists"][0]["id"]
        track_id = track_data["id"]

        # Get artist genres
        genres = get_artist_genres(sp, artist_id)
        
        # Get audio features including tempo
        audio_features = get_audio_features(sp, track_id)
        
        # Get tempo from audio features
        tempo = audio_features.get("tempo", None) if audio_features else None

        return {
            "track_name": track_data["name"],
            "artist_name": track_data["artists"][0]["name"],
            "genres": genres,
            "artist_id": artist_id,
            "track_id": track_id,
            "popularity": track_data.get("popularity", 0),
            "album": track_data["album"]["name"],
            "release_date": track_data["album"].get("release_date", ""),
            "tempo": tempo,  # Add tempo information
            "danceability": audio_features.get("danceability", None) if audio_features else None,
            "energy": audio_features.get("energy", None) if audio_features else None,
            "key": audio_features.get("key", None) if audio_features else None,
            "mode": audio_features.get("mode", None) if audio_features else None,
        }
    except Exception as e:
        logger.warning(
            f"Error getting track details for {track.get('track', {}).get('name', 'Unknown')}: {str(e)}"
        )
        return None


def analyze_playlist(playlist_id: str):
    """Analyze all tracks in a playlist and export genre information"""
    try:
        sp = setup_spotify()

        # Get playlist info
        playlist_info = sp.playlist(playlist_id, fields="name,description")
        playlist_name = playlist_info["name"]
        logger.info(f"Analyzing playlist: {playlist_name}")

        # Get all tracks from playlist
        tracks = get_playlist_tracks(sp, playlist_id)

        # Get detailed information for each track
        track_details = []
        for track in tracks:
            if not track["track"]:  # Skip any invalid tracks
                continue

            logger.info(f"Processing track: {track['track']['name']}")
            details = get_track_details(sp, track)
            if details:
                track_details.append(details)

        # Convert to DataFrame
        df = pd.DataFrame(track_details)

        # Create a separate genres DataFrame
        genres_data = []
        for _, row in df.iterrows():
            for genre in row["genres"]:
                genres_data.append(
                    {
                        "track_name": row["track_name"],
                        "artist_name": row["artist_name"],
                        "genre": genre,
                        "tempo": row["tempo"],  # Include tempo in genre data
                    }
                )

        genres_df = pd.DataFrame(genres_data)

        # Export to CSV files
        df.to_csv("track_details.csv", index=False)
        if not genres_df.empty:
            genres_df.to_csv("track_genres.csv", index=False)

        logger.info(f"Exported track details to track_details.csv")

        # Print genre summary
        if not genres_df.empty:
            genre_counts = genres_df["genre"].value_counts()
            logger.info("\nGenre Summary:")
            for genre, count in genre_counts.items():
                logger.info(f"{genre}: {count} tracks")

            # Print tracks without genres
            tracks_without_genres = df[df["genres"].apply(len) == 0]
            if not tracks_without_genres.empty:
                logger.info("\nTracks without genre information:")
                for _, row in tracks_without_genres.iterrows():
                    logger.info(f"- {row['track_name']} by {row['artist_name']}")
        else:
            logger.info("No genre information found in the playlist")

        # Print tempo summary
        logger.info("\nTempo Summary:")
        if "tempo" in df.columns:
            avg_tempo = df["tempo"].mean()
            min_tempo = df["tempo"].min()
            max_tempo = df["tempo"].max()
            logger.info(f"Average tempo: {avg_tempo:.2f} BPM")
            logger.info(f"Min tempo: {min_tempo:.2f} BPM")
            logger.info(f"Max tempo: {max_tempo:.2f} BPM")
            
            # Group songs by tempo ranges
            tempo_ranges = {
                "Slow (< 80 BPM)": df[df["tempo"] < 80].shape[0],
                "Medium (80-120 BPM)": df[(df["tempo"] >= 80) & (df["tempo"] <= 120)].shape[0],
                "Fast (> 120 BPM)": df[df["tempo"] > 120].shape[0],
            }
            
            for range_name, count in tempo_ranges.items():
                logger.info(f"{range_name}: {count} tracks")
        else:
            logger.info("No tempo information available")

    except Exception as e:
        logger.error(f"Failed to analyze playlist: {str(e)}")


def main():
    load_dotenv()

    playlist_id = os.getenv("SPOTIFY_PLAYLIST_ID")
    if not playlist_id:
        logger.error("SPOTIFY_PLAYLIST_ID not found in environment variables")
        return

    # Remove any quotes and query parameters
    playlist_id = playlist_id.strip("\"'").split("?")[0]

    analyze_playlist(playlist_id)


if __name__ == "__main__":
    main()
