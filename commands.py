import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.all()

token = os.getenv('DFLOW_BOT_TOKEN')

bot_commands = commands.Bot(command_prefix="!", intents=intents)


@bot_commands.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot_commands))


@bot_commands.command("ping")
async def ping(ctx):
  await ctx.send('Pong!')


if __name__ == "__main__":
    bot_commands.run(token)
