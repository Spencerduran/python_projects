import csv
import os
import time
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TMDBEnricher:
    def __init__(self, api_key: str):
        """
        Initialize TMDB API client

        Args:
            api_key: TMDB API key
        """
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {"accept": "application/json"}

    def search_title(self, title: str, content_type: str = None) -> Optional[Dict]:
        """
        Search for a title on TMDB

        Args:
            title: Title to search for
            content_type: Either 'movie' or 'tv' if known

        Returns:
            Dict containing title information if found, None otherwise
        """
        # If content type is known, search specific endpoint
        if content_type == "movie":
            endpoint = f"{self.base_url}/search/movie"
        elif content_type == "tv":
            endpoint = f"{self.base_url}/search/tv"
        else:
            # Search both movies and TV shows
            endpoint = f"{self.base_url}/search/multi"

        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "en-US",
            "page": 1,
        }

        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()

        results = response.json().get("results", [])
        return results[0] if results else None


def process_csv(
    input_path: str, output_path: str, tmdb_api_key: str, content_type_col: str = None
) -> None:
    """
    Process CSV file and add TMDB IDs

    Args:
        input_path: Path to input CSV file
        output_path: Path for output CSV file
        tmdb_api_key: TMDB API key
        content_type_col: Name of column containing content type (movie/tv) if exists
    """
    enricher = TMDBEnricher(tmdb_api_key)

    # Read input CSV
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        # Get fieldnames and add new columns
        fieldnames = reader.fieldnames + ["tmdb_id", "type", "year", "match_title"]

        # Process each row
        enriched_rows = []
        for row in rows:
            title = row["title"]  # Assumes 'title' column exists
            content_type = row.get(content_type_col) if content_type_col else None

            print(f"Processing: {title}")

            try:
                # Search TMDB
                result = enricher.search_title(title, content_type)

                if result:
                    # Extract year from release_date or first_air_date
                    year = None
                    if "release_date" in result:
                        year = result["release_date"][:4]
                    elif "first_air_date" in result:
                        year = result["first_air_date"][:4]

                    # Update row with TMDB info
                    row.update(
                        {
                            "tmdb_id": result["id"],
                            "type": "movie" if "release_date" in result else "tv",
                            "year": year,
                            "match_title": result.get("title") or result.get("name"),
                        }
                    )
                else:
                    # If no match found, add empty values
                    row.update(
                        {"tmdb_id": "", "type": "", "year": "", "match_title": ""}
                    )

                enriched_rows.append(row)

                # Sleep briefly to avoid rate limiting
                time.sleep(0.25)  # 4 requests per second should be safe

            except requests.exceptions.RequestException as e:
                print(f"Error processing {title}: {str(e)}")
                continue
            except Exception as e:
                print(f"Unexpected error processing {title}: {str(e)}")
                continue

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    print(f"\nProcessing complete. Results written to {output_path}")
    print(f"Total processed: {len(enriched_rows)}")


def split_into_sonarr_radarr(
    input_path: str, sonarr_output: str, radarr_output: str
) -> None:
    """
    Split enriched CSV into separate files for Sonarr and Radarr

    Args:
        input_path: Path to enriched CSV file
        sonarr_output: Path for Sonarr CSV output
        radarr_output: Path for Radarr CSV output
    """
    tv_shows = []
    movies = []

    # Read enriched CSV
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["type"] == "tv":
                tv_shows.append(
                    {
                        "title": row["match_title"],
                        "tmdb_id": row["tmdb_id"],
                        "year": row["year"],
                    }
                )
            elif row["type"] == "movie":
                movies.append(
                    {
                        "title": row["match_title"],
                        "tmdb_id": row["tmdb_id"],
                        "year": row["year"],
                    }
                )

    # Write Sonarr CSV
    if tv_shows:
        with open(sonarr_output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "tmdb_id", "year"])
            writer.writeheader()
            writer.writerows(tv_shows)

    # Write Radarr CSV
    if movies:
        with open(radarr_output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "tmdb_id", "year"])
            writer.writeheader()
            writer.writerows(movies)

    print(f"\nFound {len(tv_shows)} TV shows and {len(movies)} movies")
    print(f"TV shows written to: {sonarr_output}")
    print(f"Movies written to: {radarr_output}")


if __name__ == "__main__":
    # Configuration
    INPUT_CSV = "titles.csv"  # Your input CSV with titles
    ENRICHED_CSV = "enriched_titles.csv"  # Intermediate file with TMDB data
    SONARR_CSV = "sonarr_import.csv"  # Final Sonarr import file
    RADARR_CSV = "radarr_import.csv"  # Final Radarr import file
    # Get API key from environment variable
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    if not TMDB_API_KEY:
        raise ValueError(
            "TMDB_API_KEY not found in environment variables. Please check your .env file."
        )

    # Process CSV and add TMDB IDs
    process_csv(INPUT_CSV, ENRICHED_CSV, TMDB_API_KEY)

    # Split into separate files for Sonarr and Radarr
    split_into_sonarr_radarr(ENRICHED_CSV, SONARR_CSV, RADARR_CSV)
