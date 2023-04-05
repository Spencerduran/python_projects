import discord
import asyncio
import datetime
from pynput.keyboard import Controller, Key
from pywinauto import Desktop

DISCORD_TOKEN = "your_discord_token"
WEBHOOK_USERNAME = "NQ Alert"
CHANNEL_NAME = "chart-triggers"

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)
keyboard = Controller()

def switch_to_window(target_window_title):
    desktop_windows = Desktop(backend="uia").windows()
    for window in desktop_windows:
        if target_window_title == window.window_text():
            window.set_focus()
            break
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
    if message.author.name == WEBHOOK_USERNAME and message.channel.name == CHANNEL_NAME:
        now = datetime.datetime.now()
        print(message.content)
        
        # Switch to the specified window
        switch_to_window("Chart - NQ 06-23")
        
        content = message.embeds[0].title.strip().lower(
        ) if message.embeds else message.content.strip().lower()
        if "open long position alert" in content:
            await send_key_combination([Key.alt, Key.shift, "c"])
            print(f'\n{now}: Signal Bot: "Closed any open positions, Enter long"\n')
            bot_message = "Closed any open positions, Entering long"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "b"])

        elif "open short position alert" in content:
            await send_key_combination([Key.alt, Key.shift, "c"])
            print(f'\n{now}: Signal Bot: "Closed any open position, Entering short"\n')
            bot_message = "Closed any open positions, Entry short"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "s"])
        elif "close" in content:
            print(f'\n{now}: Signal Bot: "Closed position, all out"\n')
            bot_message = "Closed position, all out"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "c"])
        elif "profit" in content:
            print(f'\n{now}: Signal Bot: "Taking Profit, all out"\n')
            bot_message = "Bag secured"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "c"])

client.run(DISCORD_TOKEN)
