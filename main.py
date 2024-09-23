
import discord
from discord.ext import commands
import requests
import random
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

TOKEN = '<YOUR OWN TOKEN >'


intents = discord.Intents.default()
intents.messages = True 

bot = commands.Bot(command_prefix='!', intents=intents)

CHALLENGES_FILE = 'challenges.json'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello, {message.author.name}!')

    await bot.process_commands(message)

@bot.command(name='quote')
async def quote(ctx):
    try:
        response = requests.get('https://dummyjson.com/quotes')
        data = response.json()
        quote = random.choice(data['quotes'])
        await ctx.send(f'"{quote["quote"]}" - {quote["author"]}')
    except Exception as e:
        await ctx.send("Sorry, I couldn't fetch a quote at the moment.")

@bot.command(name='challenge')
async def challenge(ctx):
    try:
        with open(CHALLENGES_FILE, 'r') as file:
            data = json.load(file)
            challenges = data['challenges']
        
        challenge = random.choice(challenges)
        await ctx.send(f'**Challenge:** {challenge["name"]}\n**URL:** {challenge["url"]}')
    except Exception as e:
        await ctx.send("Sorry, I couldn't fetch a challenge at the moment.")

@bot.command(name='add')
async def add_challenge(ctx, challenge_url: str):
    # Validate URL
    parsed_url = urlparse(challenge_url)
    if not (parsed_url.scheme and parsed_url.netloc) or 'codingchallenges.fyi' not in parsed_url.netloc:
        await ctx.send("Invalid URL. Please provide a valid challenge URL from codingchallenges.fyi.")
        return

    try:
        response = requests.get(challenge_url)
        
        if response.status_code != 200:
            await ctx.send("The URL does not refer to a valid challenge.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            challenge_name = title_tag.string.strip()
        else:
            await ctx.send("Could not find a challenge title on that page.")
            return

        with open(CHALLENGES_FILE, 'r') as file:
            data = json.load(file)
        new_challenge = {
            "name": challenge_name,
            "url": challenge_url
        }
        data['challenges'].append(new_challenge)

        with open(CHALLENGES_FILE, 'w') as file:
            json.dump(data, file, indent=4)

        await ctx.send(f'Added new challenge: **{challenge_name}** - {challenge_url}')
    except Exception as e:
        await ctx.send("Sorry, I couldn't add the challenge at the moment.")

@bot.command(name='list')
async def list_challenges(ctx):
    try:
        with open(CHALLENGES_FILE, 'r') as file:
            data = json.load(file)
            challenges = data['challenges']

        if challenges:
            challenge_list = '\n'.join([f'**{c["name"]}** - {c["url"]}' for c in challenges])
            await ctx.send(f'Available Challenges:\n{challenge_list}')
        else:
            await ctx.send("No challenges available.")
    except Exception as e:
        await ctx.send("Sorry, I couldn't list the challenges at the moment.")


bot.run(TOKEN)
