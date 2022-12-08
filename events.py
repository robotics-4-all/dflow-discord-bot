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

token = os.getenv('DFLOW_BOT_TOKEN')

token = os.getenv('DFLOW_BOT_TOKEN')
rasa_domain_url = os.getenv('RASA_DOMAIN_URL')
rasa_train_model_path = os.getenv('RASA_TRAIN_MODEL_PATH')
rasa_chat_path = os.getenv('RASA_CHAT_PATH')
rasa_token = os.getenv('RASA_TOKEN')
dflow_domain_url = os.getenv('DFLOW_DOMAIN_URL')
dflow_validate_path = os.getenv('DFLOW_VALIDATE_PATH')
dflow_generate_path = os.getenv('DFLOW_GENERATE_PATH')

bot_dialogue = commands.Bot(command_prefix="!", intents=intents)


@bot_dialogue.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot_dialogue))

@bot_dialogue.event
async def on_message(message):
    print("message -->", message)
    print("message content -->", message.content)
    if message.author == bot_dialogue.user:
        return

    if message.content.startswith('hi'):
        await message.channel.send('Hello!')

    if message.content == '':
        await message.channel.send('Please say something...')
        return

    username = str(message.author)
    data = '{"sender": "' + username + '", "message": "' +  str(message.content) + '"}'
    data = data.encode('utf-8')
    url = f"{rasa_domain_url}{rasa_chat_path}"
    try:
        response = requests.post(url, data = data)
        if response.ok:
            data = json.loads(response.text)
            print(data)
            for item in data:
                msg = item['text']
                print(f"Rasa response --> {msg}")
                await message.channel.send(msg)
        else:
            raise Exception
    except:
        msg = "There was a problem connecting with Rasa server."
        print(msg)
        await message.channel.send(msg)
    return

if __name__ == "__main__":
    bot_dialogue.run(token)
