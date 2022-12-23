#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
import typing
import requests
import base64
import yaml
import tarfile
from gha_update import update_repo

load_dotenv()
intents = discord.Intents.all()
intents.message_content = True
TMP_FILE = '/tmp/tmp_file.tar.gz'
TMP_ACTION_FILE = '/tmp/actions.py'

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
rasa_put_model_path = os.getenv('RASA_PUT_MODEL_PATH')


bot_commands = commands.Bot(command_prefix="!", intents=intents)


@bot_commands.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot_commands))

@bot_commands.command("ping")
async def ping(ctx):
    await ctx.send('Pong!')

@bot_commands.command("validate")
async def validate(ctx, arg: typing.Optional[discord.Attachment], text: typing.Optional[str]):
    await ctx.send('Validating model...')
    if text != None:
        model = text
    elif arg != None:
        model = await arg.read()
        model = model.decode()
    else:
        raise Exception('Please provide a correct model...')

    # Connect to dflow api
    url = f"{dflow_domain_url}{dflow_login_path}"
    username = str(ctx.message.author).replace("#",'').replace(".",'').replace(" ",'')
    payload = {
        'username': username,
        'password': '123123'
    }
    try:
        response = requests.post(url, data = payload)
        print(f"--> Login response: {response}")
        if response.status_code == 401:
            raise Exception
        token = response.json()['access_token']
        headers = {'Authorization' : f'Bearer {token}'}
    except:
        raise Exception('Login to dflow-api failed')

    model = model.encode('ascii')
    model = base64.b64encode(model)
    model = model.decode('ascii')
    payload = f'fenc={model}'
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
async def generate(ctx, arg: typing.Optional[discord.Attachment], text: typing.Optional[str]): #: typing.Union[discord.Attachment, str]
    await ctx.send('Generating model...')
    if text != None:
        model = text
    elif arg != None:
        model = await arg.read()
        model = model.decode()
    else:
        raise Exception('Please provide a correct model...')

    # Connect to dflow api
    url = f"{dflow_domain_url}{dflow_login_path}"
    username = str(ctx.message.author).replace("#",'').replace(".",'').replace(" ",'')
    payload = {
        'username': username,
        'password': '123123'
    }
    try:
        response = requests.post(url, data = payload)
        print(f"--> Login response: {response}")
        if response.status_code == 401:
            raise Exception
        token = response.json()['access_token']
        headers = {'Authorization' : f'Bearer {token}'}
    except:
        raise Exception('Login to dflow-api failed')

    # Generate and store tarball
    url = f"{dflow_domain_url}{dflow_generate_path}"
    model = model.encode('ascii')
    model = base64.b64encode(model)
    model = model.decode('ascii')
    payload = f'fenc={model}'
    try:
        response = requests.post(url, headers = headers, params = payload)
        print(f"--> Generation response: {response}")
        if response.status_code not in [200, 201, 202, 204]:
            await ctx.send(f"Generation failed! Reason: {response.json()['message']}")
            raise Exception
        with open(TMP_FILE, 'wb') as f:
            f.write(response.content)
        await ctx.send('Model generated correctly!')

    except:
        raise Exception('Generation problem with the API')

    # Read tarball and send data for Rasa training
    tar = tarfile.open(TMP_FILE)

    payload = {}

    for member in tar.getmembers():
        f = tar.extractfile(member)
        try:
            content = f.read()
            content = content.decode()
            name = member.name.split('/')[-1]
            if name in ['nlu.yml', 'stories.yml', 'rules.yml', 'config.yml', 'domain.yml', 'endpoints.yml']:
                data = yaml.safe_load(content)
                payload.update(data)

            if name in ['actions.py']:
                action_file = open(TMP_ACTION_FILE, 'wt')
                action_file.write(content)
                action_file.close()

        except:
            continue

    payload = yaml.dump(payload)
    headers = {
      'Content-Type': 'application/yaml'
    }
    try:
        url = f"{rasa_domain_url}{rasa_train_model_path}?token={rasa_token}"

        response = requests.post(url, headers=headers, data=payload, verify=False)
        print(f"Training new model response: {response}")
        filename = response.headers['filename']
        print(f'Model {filename} trained successfully!')
    except:
        print(f"Training new model response: {response.text}")
        raise Exception('Problem with Rasa training')

    # Activate new model in Rasa instance
    model_file_path = f'/app/models/{filename}'
    headers = {'Content-Type': 'application/json'}
    body_params = {'model_file': model_file_path}
    query_params = {'token': 'rasaToken'}

    url = f"{rasa_domain_url}{rasa_put_model_path}"
    try:
        response = requests.put(url, headers=headers,
                                    json=body_params, params=query_params, verify=False)
        print(f"Activate new model response: {response}")
    except:
        raise Exception('Problem when activating newly trained Rasa model.')

    # Update Rasa action server
    update_repo(TMP_ACTION_FILE)


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
