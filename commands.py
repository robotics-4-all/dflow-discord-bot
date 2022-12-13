import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
import typing
import requests
import base64

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
    data = arg.encode()
    url = f"{dflow_domain_url}{dflow_validate_path}"
    try:
        response = requests.post(url, data = data)
    except:
        raise Exception('Validation problem')

@validate.error
async def validate_error(ctx, error):
    print('Error:', error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide a model...')
    else:
        await ctx.send(error)

@bot_commands.command("generate")
async def generate(ctx, *, arg):
    await ctx.send('Generating model...')

@generate.error
async def generate_error(ctx, error):
    print('Error:', error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide a model...')
    else:
        await ctx.send(error)

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
