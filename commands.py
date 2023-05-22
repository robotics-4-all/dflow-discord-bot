#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import uuid
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
TMP_DIR = '/tmp/rasa-discord'
TMP_ACTION_FILE = '/tmp/actions.py'

token = os.getenv('DFLOW_BOT_TOKEN')
rasa_domain_url = os.getenv('RASA_DOMAIN_URL')
rasa_train_model_path = os.getenv('RASA_TRAIN_MODEL_PATH')
rasa_token = os.getenv('RASA_TOKEN')
dflow_domain_url = os.getenv('DFLOW_DOMAIN_URL')
dflow_login_path = os.getenv('DFLOW_LOGIN_PATH')
dflow_register_path = os.getenv('DFLOW_REGISTER_PATH')
dflow_validate_path = os.getenv('DFLOW_VALIDATE_PATH')
dflow_generate_path = os.getenv('DFLOW_GENERATE_PATH')
dflow_push_model_path = os.getenv('DFLOW_PUSH_MODEL_PATH')
dflow_merge_path = os.getenv('DFLOW_MERGE_PATH')
rasa_chat_path = os.getenv('RASA_CHAT_PATH')
rasa_put_model_path = os.getenv('RASA_PUT_MODEL_PATH')


bot_commands = commands.Bot(command_prefix="!", intents=intents)


@bot_commands.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot_commands))

@bot_commands.command("ping")
async def ping(ctx):
    await ctx.send('Pong!')

@bot_commands.command("register")
async def register(ctx, *, arg):
    # Connect to dflow api
    url = f"{dflow_domain_url}{dflow_register_path}"
    username = str(ctx.message.author).replace("#",'').replace(".",'').replace(" ",'')
    payload = {
        'new_user': {
            'username': username,
            'password': '123123',
            'email': arg
        }
    }
    try:
        response = requests.post(url, data = payload)
        print(f"--> Register response: {response}")
        if response.status_code == 401:
            raise Exception
    except:
        raise Exception('Login to dflow-api failed')


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
async def generate(ctx,
                   arg: typing.Optional[discord.Attachment],
                   text: typing.Optional[str]):
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
        response = requests.post(url,
                                 headers=headers,
                                 params=payload
                                 )
        print(f"--> Generation response: {response}")
        if response.status_code not in [200, 201, 202, 204]:
            await ctx.send(f"Generation failed! Reason: {response.json()['message']}")
            raise Exception
        u_id = uuid.uuid4().hex[0:8]
        fpath = os.path.join(TMP_DIR, f'model-{u_id}.tar.gz')
        with open(fpath, 'wb') as f:
            f.write(response.content)
        await ctx.send('Model generated correctly!')
    except:
        raise Exception('Generation problem with the API')

    # Read tarball and send data for Rasa training
    tar = tarfile.open(fpath)

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
                with open(TMP_ACTION_FILE, 'wt') as f:
                    f.write(content)
        except:
            continue

    payload = yaml.dump(payload)
    headers = {
      'Content-Type': 'application/yaml'
    }
    try:
        url = f"{rasa_domain_url}{rasa_train_model_path}?token={rasa_token}"

        response = requests.post(url,
                                 headers=headers,
                                 data=payload,
                                 verify=False
                                 )
        print(f"Training new model response: {response}")
        filename = response.headers['filename']
        print(f'Model {filename} trained successfully!')
        await ctx.send('Model trained correctly!')
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
        await ctx.send('Activating new Rasa model...')
        response = requests.put(url,
                                headers=headers,
                                json=body_params,
                                params=query_params,
                                verify=False
                                )
        print(f"Activate new model response: {response}")
        await ctx.send('Activated new Rasa model!')
    except:
        raise Exception('Problem when activating newly trained Rasa model.')

    # Update Rasa action server
    await ctx.send('Deploying new actions...')
    update_repo(TMP_ACTION_FILE)
    await ctx.send('Deployed new actions!')


@generate.error
async def generate_error(ctx, error):
    print('Error:', error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide a model...')
    else:
        await ctx.send(error)


@bot_commands.command("push")
async def push(ctx, arg: typing.Optional[discord.Attachment], text: typing.Optional[str]):
    await ctx.send('Pushing model...')
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

    # Store model
    model = model.encode('ascii')
    model = base64.b64encode(model)
    model = model.decode('ascii')
    payload = f'fenc={model}'
    url = f"{dflow_domain_url}{dflow_push_model_path}"
    try:
        response = requests.post(url, headers = headers, params = payload)
        print(f"--> Push model response: {response}")
        if response.status_code not in [200, 201, 202, 204]:
            raise Exception
        if response.status_code == 200:
            await ctx.send('Model pushed correctly!')
        else:
            await ctx.send(f"Push model failed! Reason: {response.reason}")
    except:
        raise Exception('Push model problem with the API')

@push.error
async def push_error(ctx, error):
    print('Error:', error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please provide a model...')
    else:
        await ctx.send(error)


@bot_commands.command("train")
async def train(ctx):
    await ctx.send('Training model...')


@bot_commands.command("train_merged")
async def train_merged(ctx):
    await ctx.send('Training all models...')


@bot_commands.command("merge")
async def merge(ctx):
    await ctx.send('Merging user models into a single model...')
    url = f"{dflow_domain_url}{dflow_login_path}"
    username = str(ctx.message.author).replace("#",'').replace(".",'').replace(" ",'')
    headers = {}
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

    url = f"{dflow_domain_url}{dflow_merge_path}"
    try:
        response = requests.get(url, headers=headers)
        print(f"--> Merge models response: {response}")
        if response.status_code not in [200, 201, 202, 204]:
            raise Exception
        if response.status_code == 200:
            await ctx.send('Model merged correctly!')
            u_id = uuid.uuid4().hex[0:8]
            fpath = os.path.join(TMP_DIR, f'model-merged-{u_id}.dflow')
            with open(fpath, 'wb') as f:
                f.write(response.content)
            await ctx.send(file=discord.File(fpath))
        else:
            await ctx.send(f"Merge models failed! Reason: {response.reason}")
    except:
        raise Exception('Merge Models problem with the dFlow API')


@merge.error
async def merge_error(ctx, error):
    print('Error:', error)
    await ctx.send(error)


if __name__ == "__main__":
    bot_commands.run(token)
