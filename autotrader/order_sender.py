import discord
import json
import asyncio
from pynput.keyboard import Controller, Key

DISCORD_TOKEN = "ODk2NDIyOTg1MTc3NjUzMzEw.GHEHKK.LjBUlyMpxp1UNnbBK87yoKviM5SSK85e02OeMI"
WEBHOOK_USERNAME = "NQ Alert"
CHANNEL_NAME = "chart-triggers"

intents = discord.Intents.default()
intents.message_content = True  # explicitly enable the message content intents
intents.messages = True

client = discord.Client(intents=intents)
keyboard = Controller()


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
        content = message.embeds[0].title.strip().lower(
        ) if message.embeds else message.content.strip().lower()

        if len(message.embeds) > 0:
            content = message.embeds[0].title.strip().lower(
            ) if message.embeds else message.content.strip().lower()

        #print( f"Karma Algo: {message.content if message.content else content}")

        if "open long position alert" in content:
            await send_key_combination([Key.alt, Key.shift, "c"])
            print(f'Signal Bot: "Closed any open positions, Enter long"\n')
            bot_message = "Closed any open positions, Entering long"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "b"])

        elif "open short position alert" in content:
            await send_key_combination([Key.alt, Key.shift, "c"])
            print(f'Signal Bot: "Closed any open position, Entering short"\n')
            bot_message = "Closed any open positions, Entering short"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "s"])
        elif "close" in content:
            print(f'Signal Bot: "Closed position, all out"\n')
            bot_message = "Closed position"
            await message.channel.send(bot_message)
            await send_key_combination([Key.alt, Key.shift, "c"])

client.run(DISCORD_TOKEN)
