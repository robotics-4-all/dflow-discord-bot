#!/usr/bin/env python3

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
dflow_login_path = os.getenv('DFLOW_LOGIN_PATH')
dflow_validate_path = os.getenv('DFLOW_VALIDATE_PATH')
dflow_generate_path = os.getenv('DFLOW_GENERATE_PATH')
dflow_push_model_path = os.getenv('DFLOW_PUSH_MODEL_PATH')
dflow_merge_n_train_path = os.getenv('DFLOW_MERGE_N_TRAIN_PATH')
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
    url = f"{dflow_domain_url}{dflow_login_path}"
    username = str(ctx.message.author).replace("#",'')
    data = {
        'username': username,
        'password': '123123'
    }
    try:
        response = requests.post(url, data = data)
        print(f"--> Login response: {response}")
        if response.status_code == 401:
            raise Exception
        token = response.json()['access_token']
        headers = {'Authorization' : f'Bearer {token}'}
    except:
        raise Exception('Login to dflow-api failed')

    data = arg.encode('ascii')
    data = base64.b64encode(data)
    data = data.decode('ascii')
    payload = f'fenc={data}'
    url = f"{dflow_domain_url}{dflow_validate_path}"
    try:
        response = requests.post(url, headers = headers, params = payload)
        print(f"--> Validaton response: {response}")
        print(f"--> Validaton response JSON: {response.json()}")
        if response.status_code not in [200, 201, 202, 204]:
            raise Exception
        status = response.json()['status']
        if status == 200:
            await ctx.send('Model validated correctly!')
        else:
            await ctx.send(f"Validation failed! Reason: {response.json()['message']}")
    except:
        raise Exception('Validation problem with the API')


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
