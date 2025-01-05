# Trakt Library Sync

A Python script to sync your movie and TV show library with Trakt.tv using TMDb IDs. This script allows you to bulk import your media library into Trakt using CSV files.

## Prerequisites

- Python 3.6 or higher
- A Trakt.tv account
- Trakt API credentials (Client ID and Client Secret)

## Installation

1. Clone this repository or download the script
2. Install required packages:
```bash
pip install pandas requests python-dotenv
```

## Configuration

1. Create a `.env` file in the same directory as the script with your Trakt API credentials:
```
TRAKT_CLIENT_ID=your_client_id_here
TRAKT_CLIENT_SECRET=your_client_secret_here
```

2. Create your CSV files:

### Movies (movies.csv)
```csv
title,tmdb_id,year
A Man Called Otto,937278,2022
Big Trouble in Little China,6978,1986
```

### TV Shows (shows.csv)
```csv
title,tmdb_id,year
The Last of Us,100088,2023
House of the Dragon,94997,2022
```

Note: The `title` and `year` fields are optional and for reference only. The script uses `tmdb_id` for matching.

## Usage

Run the script:
```bash
python trakt_sync.py
```

The script will:
1. Load your API credentials from the `.env` file
2. Start the Trakt authentication process
   - Provides a URL to visit
   - Gives you a code to enter on the Trakt website
3. After authentication, it will:
   - Process `movies.csv` if it exists
   - Process `shows.csv` if it exists
   - Add all items to your Trakt collection

## Features

- Supports both movies and TV shows
- Uses secure environment variables for API credentials
- Automatic media type detection based on filename
- Bulk import capability
- TMDb ID-based matching for accuracy

## Security Notes

- Never commit your `.env` file to version control
- Generate new API credentials if you accidentally expose them
- The script uses the device authentication flow for secure access

## Limitations

- Currently adds entire TV series (no episode-level tracking)
- Does not handle ratings or watched status
- Does not remove items from collection

## Error Handling

The script includes basic error handling for:
- Missing environment variables
- Authentication failures
- API request errors
- Missing CSV files

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
