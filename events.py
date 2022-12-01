import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()

token = os.getenv('DFLOW_BOT_TOKEN')

bot_dialogue = commands.Bot(command_prefix="!", intents=intents)


@bot_dialogue.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot_dialogue))


@bot_dialogue.event
async def on_message(message):
    print("message-->", message)
    if message.author == bot_dialogue.user:
        return

    if message.content.startswith('hi'):
        await message.channel.send('Hello!')


@bot_dialogue.command("ping")
async def ping(ctx):
  await ctx.send('Pong!')


if __name__ == "__main__":
    bot_dialogue.run(token)
