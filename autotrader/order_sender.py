import asyncio
import datetime
import ctypes
from ctypes import wintypes
from pynput.keyboard import Controller, Key

import discord

DISCORD_TOKEN = "ODk2NDIyOTg1MTc3NjUzMzEw.GHEHKK.LjBUlyMpxp1UNnbBK87yoKviM5SSK85e02OeMI"
CHANNEL_NAME = "futures-trades"
author_window_map = {
    "ES Alert": "Chart - ES 06-23",
    "NQ Alert": "Chart - NQ 06-23",
    "YM Alert": "Chart - YM 06-23",
    "RTY Alert": "Chart - RTY 06-23",
}

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)
keyboard = Controller()

# Define necessary Windows API functions and constants
FindWindow = ctypes.windll.user32.FindWindowW
FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
FindWindow.restype = wintypes.HWND

SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
SetForegroundWindow.argtypes = [wintypes.HWND]
SetForegroundWindow.restype = wintypes.BOOL


def switch_to_window(target_window_title):
    hwnd = FindWindow(None, target_window_title)
    if hwnd:
        SetForegroundWindow(hwnd)
    else:
        print(f"No window with the title '{target_window_title}' was found.")


async def send_key_combination(keys):
    for key in keys:
        keyboard.press(key)
    await asyncio.sleep(0.1)
    for key in keys:
        keyboard.release(key)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.channel.name == CHANNEL_NAME and message.author.name in author_window_map:
        now = datetime.datetime.now()
        ticker = message.author.name[:-6]

        # Switch to the corresponding window for the message author
        switch_to_window(author_window_map[message.author.name])

        content = message.embeds[0].title.strip().lower(
        ) if message.embeds else message.content.strip().lower()
        if "open long position alert" in content:
            await send_key_combination([Key.alt, Key.shift, "c"])
            print(f'\n{now}: Signal Bot: "Long Entry"\n')
            bot_message = f"Closed any open {ticker} positions, Entered long"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "b"])

        elif "open short position alert" in content:
            await send_key_combination([Key.alt, Key.shift, "c"])
            print(
                f'\n{now}: Signal Bot: "Short Entry"\n')
            bot_message = f"Closed any open {ticker} positions, Entered long"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "s"])

        elif "close" in content:
            print(f'\n{now}: Signal Bot: "Flattened {ticker} position, all out"\n')
            bot_message = f"Closed {ticker} position, all out"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "c"])

        elif "profit" in content:
            print(f'\n{now}: Signal Bot: "Taking {ticker} Profit, all out"\n')
            bot_message = f"{ticker} Bag secured"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "c"])

client.run(DISCORD_TOKEN)
