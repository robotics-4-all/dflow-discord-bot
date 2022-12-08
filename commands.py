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

@bot_commands.command("validate")
async def validate(ctx, *, arg):
    await ctx.send('Validating model...')
@validate.error
async def validate_error(ctx, error):
    await ctx.send('I could not find that model...')

@bot_commands.command("generate")
async def generate(ctx, *, arg):
    await ctx.send('Generating model...')

@generate.error
async def generate_error(ctx, error):
    # if isinstance(error, commands.BadArgument):
    await ctx.send('I could not find that model...')

@bot_commands.command("push")
async def push(ctx):
    await ctx.send('Pushing model...')

@bot_commands.command("train")
async def train(ctx):
    await ctx.send('Training model...')
@bot_commands.command("train_merged")
async def train_merged(ctx):
    await ctx.send('Training all models...')

if __name__ == "__main__":
    bot_commands.run(token)
