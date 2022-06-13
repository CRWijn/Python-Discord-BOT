import os

import discord
from dotenv import load_dotenv, find_dotenv

load_dotenv('token.env')
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD = os.environ.get('GUILD_NAME')

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.channel.name != 'disgusting_bot_spam':
        return

    if message.author == client.user:
        return
    
    if 'choke' in message.content.lower() and 'me' in message.content.lower() and 'daddy' in message.content.lower():
        response = 'yes, kitten'
        await message.channel.send(response)

client.run(TOKEN)
