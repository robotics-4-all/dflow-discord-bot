#!/usr/bin/env python3

import asyncio
import discord
from discord.ext import commands
import os
import random
from dotenv import load_dotenv
import typing
import requests

from commlib.msg import MessageHeader, PubSubMessage
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters

load_dotenv()
intents = discord.Intents.all()
intents.message_content = True

BOT_TOKEN = os.getenv('DFLOW_BOT_TOKEN')
RASA_DOMAIN_URL = os.getenv('RASA_DOMAIN_URL')
RASA_TRAIN_MODEL_PATH = os.getenv('RASA_TRAIN_MODEL_PATH')
RASA_CHAT_PATH = os.getenv('RASA_CHAT_PATH')
RASA_TOKEN = os.getenv('RASA_TOKEN')
RASA_DIALOGUE_URL = f"{RASA_DOMAIN_URL}{RASA_CHAT_PATH}"

NOTIFICATIONS_MQTT_HOST = os.getenv("NOTIFICATIONS_MQTT_HOST", "locsys.issel.ee.auth.gr")
NOTIFICATIONS_MQTT_PORT = int(os.getenv("NOTIFICATIONS_MQTT_PORT", "1883"))
NOTIFICATIONS_MQTT_USERNAME = os.getenv("NOTIFICATIONS_MQTT_USERNAME", "")
NOTIFICATIONS_MQTT_PASSWORD = os.getenv("NOTIFICATIONS_MQTT_PASSWORD", "")
NOTIFICATIONS_MQTT_SSL = os.getenv("NOTIFICATIONS_MQTT_SSL", False)
NOTIFICATIONS_MQTT_TOPIC = os.getenv("NOTIFICATIONS_MQTT_TOPIC", "rasacloud.deployments.events")

DISCORD_CHANNEL = int(os.getenv("DISCORD_CHANNEL", 1239936124340932748))
# DISCORD_CHANNEL = 1239936124340932748

command_char = '!'

discord_client = discord.Client(intents=intents)


class Notification(PubSubMessage):
    header: MessageHeader = MessageHeader()
    msg: str = ""


class DeployEvents:
    def __init__(self):
        conn_params = ConnectionParameters(
            host=NOTIFICATIONS_MQTT_HOST,
            port=NOTIFICATIONS_MQTT_PORT,
            username=NOTIFICATIONS_MQTT_USERNAME,
            password=NOTIFICATIONS_MQTT_PASSWORD,
            ssl=NOTIFICATIONS_MQTT_SSL,
        )
        node = Node(
            node_name="rasa_cloud_deployment_listener_discord",
            connection_params=conn_params,
            debug=False,
        )
        self._node = node
        self._sub = node.create_subscriber(msg_type=Notification,
                                           topic=NOTIFICATIONS_MQTT_TOPIC,
                                           on_message=self.on_event)
        self._node.run()

    def on_event(self, msg):
        if not discord_client:
            return
        self.discord_send_sync(msg.msg)

    def discord_send_sync(self, msg):
        channel = discord_client.get_channel(DISCORD_CHANNEL)
        # asyncio.get_event_loop().create_task(channel.send(msg))
        asyncio.run_coroutine_threadsafe(channel.send(msg), discord_client.loop)


@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user}')
    text_channel_list = []
    print(f"Connected to channels:")
    for guild in discord_client.guilds:
        for channel in guild.text_channels:
            text_channel_list.append(channel)
            print("- ", channel.id, channel, guild.name)


if __name__ == "__main__":
    listener = DeployEvents()
    discord_client.run(BOT_TOKEN)
