import requests
import json

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1301995437590577192/r1PzkV7Sp_SnecW4CY6a8kaFAQsQxpa5OpmBbwE5aVWBX8k_wkzBff4AfoiM0YGsZf1f"

# Test 1: Simple message
def send_simple_message():
    data = {
        "content": "Test message from Python"
    }
    response = requests.post(webhook_url, json=data)
    print(f"Simple message status code: {response.status_code}")

# Test 2: Message with embed
def send_embed_message():
    data = {
        "embeds": [
            {
                "title": "60min -> Short 1 2D",
                "color": 10038562,
                "fields": [
                    {
                        "name": "60🔴 4H🟢 D🔴 W🟢",
                        "value": "─────────────",
                        "inline": False
                    },
                    {
                        "name": "",
                        "value": "```Daily -> LONG (LONG 2D 2U)\n4Hour -> SHORT (SHORT 2U 2D)```",
                        "inline": False
                    }
                ],
                "description": " ",
                "footer": {
                    "text": "11/01/2024 14:30"
                }
            }
        ]
    }
    response = requests.post(webhook_url, json=data)
    print(f"Embed message status code: {response.status_code}")

# Run tests
if __name__ == "__main__":
    print("Testing Discord webhook...")
    #send_simple_message()
    send_embed_message()
