import os
import time
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv


class TraktSync:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.trakt.tv"
        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": client_id,
        }
        self.access_token = None

    def authenticate(self):
        """
        Perform device authentication flow.
        Returns the access token needed for API calls.
        """
        # First get the device code
        response = requests.post(
            f"{self.base_url}/oauth/device/code", json={"client_id": self.client_id}
        )
        device_code_data = response.json()

        print(f"Please visit: {device_code_data['verification_url']}")
        print(f"And enter code: {device_code_data['user_code']}")

        # Poll for the token
        interval = device_code_data["interval"]
        device_code = device_code_data["device_code"]

        while True:
            time.sleep(interval)

            response = requests.post(
                f"{self.base_url}/oauth/device/token",
                json={
                    "code": device_code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.access_token}"
                print("Successfully authenticated!")
                break
            elif response.status_code != 400:  # 400 means still waiting
                print(f"Error: {response.text}")
                break

    def add_to_collection(self, items: List[Dict], media_type: str):
        """
        Add items to Trakt collection
        media_type: either 'movies' or 'shows'
        """
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")

        # Format payload based on media type
        if media_type == "movies":
            payload = {"movies": [{"ids": {"tmdb": item["tmdb_id"]}} for item in items]}
        else:  # shows
            payload = {"shows": [{"ids": {"tmdb": item["tmdb_id"]}} for item in items]}

        response = requests.post(
            f"{self.base_url}/sync/collection", headers=self.headers, json=payload
        )

        if response.status_code == 201:
            print(f"Successfully added {len(items)} {media_type} to collection!")
            return response.json()
        else:
            print(f"Error adding {media_type}: {response.text}")
            return None


def process_file(filename: str):
    """
    Process a CSV file and determine its media type
    Returns tuple of (items, media_type)
    """
    df = pd.read_csv(filename)

    # Try to determine if this is a movie or show file based on filename
    media_type = "movies" if "movie" in filename.lower() else "shows"

    # Convert DataFrame to list of dictionaries
    items = df.to_dict("records")

    return items, media_type


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get credentials from environment variables
    client_id = os.getenv("TRAKT_CLIENT_ID")
    client_secret = os.getenv("TRAKT_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "Missing TRAKT_CLIENT_ID or TRAKT_CLIENT_SECRET environment variables"
        )

    # Create TraktSync instance
    trakt = TraktSync(client_id, client_secret)

    # Authenticate
    trakt.authenticate()

    # Process movies if file exists
    if os.path.exists("../TMDB_ID_finder/radarr_import.csv"):
        items, media_type = process_file("movies.csv")
        trakt.add_to_collection(items, media_type)

    # Process shows if file exists
    if os.path.exists("../TMDB_ID_finder/sonarr_import.csv"):
        items, media_type = process_file("shows.csv")
        trakt.add_to_collection(items, media_type)


if __name__ == "__main__":
    main()
