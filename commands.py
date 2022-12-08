import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()
intents.message_content = True

token = os.getenv('DFLOW_BOT_TOKEN')
rasa_domain_url = os.getenv('RASA_DOMAIN_URL')
rasa_train_model_path = os.getenv('RASA_TRAIN_MODEL_PATH')
rasa_token = os.getenv('RASA_TOKEN')
dflow_domain_url = os.getenv('DFLOW_DOMAIN_URL')
dflow_validate_path = os.getenv('DFLOW_VALIDATE_PATH')
dflow_generate_path = os.getenv('DFLOW_GENERATE_PATH')
rasa_chat_path = os.getenv('RASA_CHAT_PATH')


bot_commands = commands.Bot(command_prefix="!", intents=intents)


@bot_commands.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot_commands))


@bot_commands.command("ping")
async def ping(ctx):
  await ctx.send('Pong!')


if __name__ == "__main__":
    bot_commands.run(token)
