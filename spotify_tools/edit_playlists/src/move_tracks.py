import logging
import os

import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_tracks_from_csv(filepath):
    """Load tracks from CSV file"""
    try:
        df = pd.read_csv(filepath)
        if "tracks" not in df.columns:
            raise ValueError("CSV file must contain a 'tracks' column")
        tracks = df["tracks"].dropna().tolist()
        logger.info(f"Loaded {len(tracks)} tracks from CSV")
        return tracks
    except FileNotFoundError:
        logger.error(f"CSV file not found: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        raise


def setup_spotify():
    """Initialize Spotify client with necessary permissions"""
    required_env_vars = [
        "SPOTIFY_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET",
        "SPOTIFY_REDIRECT_URI",
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    scope = "playlist-modify-public playlist-modify-private playlist-read-private"
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


def validate_track(track):
    """Validate track structure and URI"""
    if not isinstance(track, dict):
        return False, "Track is not a dictionary"

    if "track" not in track:
        return False, "No 'track' key in track object"

    track_data = track["track"]
    if not isinstance(track_data, dict):
        return False, "'track' value is not a dictionary"

    if "uri" not in track_data:
        return False, "No 'uri' in track data"

    if not isinstance(track_data["uri"], str):
        return False, "URI is not a string"

    if not track_data["uri"].startswith("spotify:track:"):
        return False, f"Invalid URI format: {track_data['uri']}"

    return True, track_data["uri"]


def create_new_playlist(sp, name="TBD", description="Progressive tracks"):
    """Create a new playlist and return its ID"""
    try:
        user_id = sp.me()["id"]
        playlist = sp.user_playlist_create(
            user_id, name, public=False, description=description
        )
        logger.info(f"Created new playlist: {name}")
        return playlist["id"]
    except Exception as e:
        logger.error(f"Failed to create playlist: {str(e)}")
        raise


def get_playlist_tracks(sp, playlist_id):
    """Get all tracks from a playlist with validation"""
    try:
        results = sp.playlist_items(playlist_id)
        all_tracks = results["items"]

        while results["next"]:
            results = sp.next(results)
            all_tracks.extend(results["items"])

        logger.info(f"Retrieved {len(all_tracks)} tracks from playlist")

        # Validate tracks
        valid_tracks = []
        for track in all_tracks:
            is_valid, result = validate_track(track)
            if is_valid:
                valid_tracks.append(track)
            else:
                logger.warning(f"Invalid track found: {result}")

        return valid_tracks
    except Exception as e:
        logger.error(f"Error fetching playlist tracks: {str(e)}")
        raise


def move_tracks(source_playlist_id, progressive_tracks_list):
    """Move progressive tracks to a new playlist"""
    try:
        # Initialize Spotify client
        sp = setup_spotify()
        logger.info("Spotify client initialized successfully")

        # Validate source playlist ID
        if not source_playlist_id:
            raise ValueError("Source playlist ID is required")

        # Debug: Print the source playlist details
        try:
            playlist_info = sp.playlist(source_playlist_id, fields="name,id")
            logger.info(
                f"Source playlist found: {playlist_info.get('name', 'Unknown')} ({playlist_info['id']})"
            )
        except Exception as e:
            logger.error(f"Error accessing source playlist: {str(e)}")
            raise

        # Create new playlist
        new_playlist_id = create_new_playlist(sp)

        # Get and validate all tracks from source playlist
        all_tracks = get_playlist_tracks(sp, source_playlist_id)

        # Find tracks to move and their URIs
        tracks_to_move = []
        for track in all_tracks:
            track_name = track["track"]["name"]
            track_uri = track["track"]["uri"]

            # Debug: Print track info
            logger.debug(f"Processing track: {track_name} ({track_uri})")

            if any(
                prog_track.lower() in track_name.lower()
                for prog_track in progressive_tracks_list
            ):
                tracks_to_move.append(track_uri)
                logger.info(f"Found matching track: {track_name}")

        # Add tracks to new playlist
        if tracks_to_move:
            logger.info(f"Attempting to move {len(tracks_to_move)} tracks")

            # First verify all URIs are valid
            valid_uris = [
                uri for uri in tracks_to_move if uri.startswith("spotify:track:")
            ]
            if len(valid_uris) != len(tracks_to_move):
                logger.warning(
                    f"Found {len(tracks_to_move) - len(valid_uris)} invalid URIs"
                )

            # Spotify API has a limit of 100 tracks per request
            for i in range(0, len(valid_uris), 100):
                chunk = valid_uris[i : i + 100]
                try:
                    # Debug: Print the chunk we're about to add
                    logger.debug(f"Adding chunk of {len(chunk)} tracks to new playlist")
                    logger.debug(f"First URI in chunk: {chunk[0]}")

                    sp.playlist_add_items(new_playlist_id, chunk)
                    logger.info(f"Successfully added chunk of {len(chunk)} tracks")

                    # Remove from original playlist
                    sp.playlist_remove_all_occurrences_of_items(
                        source_playlist_id, chunk
                    )
                    logger.info(
                        f"Successfully removed chunk of {len(chunk)} tracks from source"
                    )
                except Exception as e:
                    logger.error(f"Error processing chunk: {str(e)}")
                    # Print the problematic URIs
                    for uri in chunk:
                        logger.debug(f"URI in failed chunk: {uri}")
                    raise

            logger.info(f"Successfully moved {len(valid_uris)} tracks to new playlist")
        else:
            logger.info("No matching tracks found to move")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


def main():
    load_dotenv()

    # Load source playlist ID from environment
    source_playlist_id = os.getenv("SPOTIFY_PLAYLIST_ID")
    if not source_playlist_id:
        logger.error("SPOTIFY_PLAYLIST_ID not found in environment variables")
        return

    try:
        # Load tracks from CSV
        progressive_tracks = load_tracks_from_csv("./tracklist.csv")

        # Move tracks
        move_tracks(source_playlist_id, progressive_tracks)
    except Exception as e:
        logger.error(f"Failed to process playlist: {str(e)}")


if __name__ == "__main__":
    main()
