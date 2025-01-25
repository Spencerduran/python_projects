import json
from collections import defaultdict

import pandas as pd


def transform_genres():
    """Transform the genre CSV into a flattened JSON structure"""
    # Read the CSV file
    df = pd.read_csv("track_genres.csv")

    # Create a dictionary to store tracks and their genres
    tracks_dict = defaultdict(
        lambda: {
            "artist_name": "",
            "genres": set(),  # Using a set to avoid duplicate genres
        }
    )

    # Process each row
    for _, row in df.iterrows():
        track_name = row["track_name"]
        tracks_dict[track_name]["artist_name"] = row["artist_name"]
        tracks_dict[track_name]["genres"].add(row["genre"])

    # Convert sets to lists for JSON serialization
    output_dict = {
        track_name: {
            "artist_name": info["artist_name"],
            "genres": sorted(list(info["genres"])),  # Sort genres for consistency
        }
        for track_name, info in tracks_dict.items()
    }

    # Create a genre index for quick lookups
    genre_index = defaultdict(list)
    for track_name, info in output_dict.items():
        for genre in info["genres"]:
            genre_index[genre].append(
                {"track_name": track_name, "artist_name": info["artist_name"]}
            )

    # Create the final structure
    final_output = {
        "tracks": output_dict,
        "genres": {
            genre: sorted(tracks, key=lambda x: x["track_name"])
            for genre, tracks in genre_index.items()
        },
    }

    # Save to JSON file
    with open("tracks_by_genre.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    # Print some stats
    print(f"Processed {len(output_dict)} unique tracks")
    print(f"Found {len(genre_index)} unique genres")

    # Print example of how to use the JSON
    print("\nExample of tracks by genre:")
    genre_example = "progressive house"
    if genre_example in final_output["genres"]:
        print(f"\nTracks with genre '{genre_example}':")
        for track in final_output["genres"][genre_example]:
            print(f"- {track['track_name']} by {track['artist_name']}")


def find_tracks_by_genre(genre):
    """Helper function to find tracks by genre from the JSON file"""
    try:
        with open("tracks_by_genre.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        if genre in data["genres"]:
            return data["genres"][genre]
        return []
    except FileNotFoundError:
        print(
            "Please run the transform_genres() function first to create the JSON file"
        )
        return []


def find_tracks_without_genre_keyword(keyword):
    """Find all tracks that don't have any genres containing the given keyword"""
    try:
        with open("tracks_by_genre.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        non_melodic_tracks = []
        for track_name, info in data["tracks"].items():
            # Check if none of the track's genres contain the keyword
            if not any(keyword.lower() in genre.lower() for genre in info["genres"]):
                non_melodic_tracks.append(
                    {
                        "track_name": track_name,
                        "artist_name": info["artist_name"],
                        "genres": info["genres"],
                    }
                )

        return sorted(non_melodic_tracks, key=lambda x: x["track_name"])
    except FileNotFoundError:
        print(
            "Please run the transform_genres() function first to create the JSON file"
        )
        return []


def find_track_info(track_name):
    """Helper function to get all genres for a specific track"""
    try:
        with open("tracks_by_genre.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        if track_name in data["tracks"]:
            return data["tracks"][track_name]
        return None
    except FileNotFoundError:
        print(
            "Please run the transform_genres() function first to create the JSON file"
        )
        return None


if __name__ == "__main__":
    # Transform the data
    transform_genres()

    # Example usage
    print("\nExample searches:")

    # Find all tracks with progressive house
    prog_house_tracks = find_tracks_by_genre("progressive house")
    if prog_house_tracks:
        print("\nAll progressive house tracks:")
        for track in prog_house_tracks:
            print(f"- {track['track_name']} by {track['artist_name']}")

    # Find all genres for a specific track
    track_name = "Bloom At Night"
    track_info = find_track_info(track_name)
    if track_info:
        print(f"\nGenres for '{track_name}':")
        print(f"Artist: {track_info['artist_name']}")
        print(f"Genres: {', '.join(track_info['genres'])}")

    # Find tracks without melodic genres
    non_melodic_tracks = find_tracks_without_genre_keyword("melodic")
    if non_melodic_tracks:
        print("\nTracks without 'melodic' in their genres:")
        for track in non_melodic_tracks:
            print(f"- {track['track_name']} by {track['artist_name']}")
            print(f"  Genres: {', '.join(track['genres'])}")
