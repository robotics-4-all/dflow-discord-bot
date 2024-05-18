#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
import typing
import requests

load_dotenv()
intents = discord.Intents.all()
intents.message_content = True

BOT_TOKEN = os.getenv('DFLOW_BOT_TOKEN')
RASA_DOMAIN_URL = os.getenv('RASA_DOMAIN_URL')
RASA_TRAIN_MODEL_PATH = os.getenv('RASA_TRAIN_MODEL_PATH')
RASA_CHAT_PATH = os.getenv('RASA_CHAT_PATH')
RASA_TOKEN = os.getenv('RASA_TOKEN')
RASA_DIALOGUE_URL = f"{RASA_DOMAIN_URL}{RASA_CHAT_PATH}"


CHANNEL_IDS_TO_LISTEN = ["1239936124340932748"]

command_char = '!'

bot_dialogue = commands.Bot(command_prefix="!", intents=intents)



def call_rasa_dialogue(msg: str, username: str):
    try:
        data = '{"sender": "' + username + '", "message": "' +  str(msg) + '"}'
        data = data.encode('utf-8')
        response = requests.post(RASA_DIALOGUE_URL, data=data, verify=False)
        print(f'Rasa response: {response.json()}')
        return response
    except Exception as e:
        print(f'[X] Failed to call RASA Dialogue - {e}')
        return {}


@bot_dialogue.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot_dialogue))


@bot_dialogue.event
async def on_message(message):
    if message.channel.id not in CHANNEL_IDS_TO_LISTEN:
        return
    if command_char in message.content:
        return
    print(f"Rasa request: {message.content}")
    if message.author == bot_dialogue.user:
        return

    if message.content.startswith('!'):
        return

    if message.content == '':
        await message.channel.send('Please say something...')
        return

    username = str(message.author).split("#")[0].replace(".",'').replace(" ",'')
    response = call_rasa_dialogue(message.content, username)
    try:
        if response.ok:
            data = response.json()
            for item in data:
                if 'text' in item:
                    msg = item['text']
                elif 'custom' in item:
                    msg = item['custom']
                print(f"Rasa response --> {msg}")
                await message.channel.send(msg)
        else:
            raise Exception
    except Exception as e:
        msg = "There was a problem connecting with Rasa server."
        print(f'{msg}: {str(e)}')
        await message.channel.send(msg)
    return


if __name__ == "__main__":
    # resp = call_rasa_dialogue('Hello', 'klpanagi2483')
    bot_dialogue.run(BOT_TOKEN)
