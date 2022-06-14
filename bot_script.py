import os
import hangman
import time
import asyncio
import epicstore_api

from dotenv import load_dotenv, find_dotenv
from discord.ext import commands


load_dotenv('token.env')
TOKEN = os.environ.get('DISCORD_TOKEN')
FREE_GAME_CHANNEL_ID = int(os.environ.get('FREE_GAME_CHANNEL_ID'))
TEST_CHANNEL_ID = int(os.environ.get('TEST_CHANNEL_ID'))

bot = commands.Bot(command_prefix='daddy ')
hangman_entity = hangman.start_hangman()
global timer, stop_timer

@bot.event
async def on_ready():
    print("Bot initialised")
    channel = bot.get_channel(FREE_GAME_CHANNEL_ID)
    while (True):
        EGS_obj = epicstore_api.api.EpicGamesStoreAPI()
        free_games = EGS_obj.get_free_games()

        for game in free_games['data']['Catalog']['searchStore']['elements']:
            if game['promotions'] is not None:
                if game['promotions']['promotionalOffers']:
                    try:
                        found = False
                        with open('free_games.txt') as f:
                            for line in f:
                                if line == game['title'] + "\n":
                                    found = True
                            f.close()
                        if not found:
                            with open('free_games.txt', 'a') as f:
                                f.write(game['title'] + "\n")
                                f.close()
                            #ANNOUNCEMENT
                            await channel.send("<@&867045278694637578>" + " " + game['title'] + " is free to keep on the epic store!")
                            if "\home" in game['productSlug']:
                                slug = game['productSlug'].split("\home")[0]
                                await channel.send("https://store.epicgames.com/en-US/p/" + slug)
                            else:
                                await channel.send("https://store.epicgames.com/en-US/p/" + game['productSlug'])
                    except FileNotFoundError:
                        with open('free_games.txt', 'w') as f:
                            f.write(game['title'] + "\n")
                            f.close()
                else:
                    try:
                        found = False
                        with open('free_games.txt') as f:
                            fdata = f.read()
                            for line in f:
                                if line == game['title'] + "\n":
                                    found = True
                            f.close()
                        if found:
                            fdata.replace(game['title'] + "\n", "")
                            with open('free_games.txt', 'w') as f:
                                f.write(fdata)
                                f.close()
                    except FileNotFoundError:
                        with open('free_games.txt', 'w') as f:
                            f.close()
        await asyncio.sleep(10)

@bot.command(
    name='print',
    help='Prints a saucy text'
    )
async def bot_print(ctx):
    await ctx.send("Daddy chill!")

@bot.command(
    name='hangman',
    help='Start a game of hangman.'
    )
async def bot_start_hangman(ctx):
    global timer, stop_timer
    if hangman_entity.player != '':
        await ctx.send("Wait your turn! " + hangman_entity.player + " is still playing!")
        return

    hangman_entity.reset()
    hangman_entity.player = ctx.author.nick.split("#")[0]
    await ctx.send("Hangman game started, use 'daddy guess' to guess!")
    await ctx.send(hangman_entity)

    print("Word: " + hangman_entity.word)
    
    stop_timer = False
    timer = 0
    while (not stop_timer):
        if timer > 60:
            hangman_entity.reset()
            await ctx.send("<@{}>".format(ctx.author.id) + " Waited too long to guess. Game over :/")
            return
        await asyncio.sleep(1)
        timer += 1
    stop_timer = False

@bot.command(
    name='guess',
    help='Guess a letter or word for hangman game.'
    )
async def bot_guess_hangman(ctx, guess=''):
    global timer, stop_timer
    timer = 0
    if hangman_entity.player == '':
        await ctx.send("No hangman game being played.")
        return
    elif ctx.author.nick.split("#")[0] != hangman_entity.player:
        await ctx.send("OI " + ctx.author.nick.split("#")[0] + ", it's not ur turn, stfu!")
        return
    
    guess = guess.lower()
    if guess == '':
        await ctx.send("YOU HAVE TO GUESS SOMETHING YOU FUCKER!")
        return
    elif len(guess) > 1:
        if guess == hangman_entity.word:
            hangman_entity.update_output(False, guess, guess)
            await ctx.send("YOU WIN!")
            await ctx.send(hangman_entity)
            hangman_entity.reset()
            stop_timer = True
            return
        else:
            hangman_entity.errors_made += 1
            hangman_entity.update_output(True, guess, guess)
    else:
        if 97 <= ord(guess) <= 122:
            if guess in hangman_entity.guessed_letters:
                await ctx.send("Already guessed that letter... Dumbass.")
                return
            elif guess in hangman_entity.word:
                hangman_entity.update_output(False, guess)
            else:
                hangman_entity.errors_made += 1
                hangman_entity.update_output(True, guess)

    if hangman_entity.errors_made == 7:
        hangman_entity.update_output(False, hangman_entity.word, hangman_entity.word)
        await ctx.send("WAAA WAAA YOU LOST!")
        await ctx.send(hangman_entity)
        hangman_entity.reset()
        stop_timer = True
        return
    elif "".join(hangman_entity.word_status) == hangman_entity.word:
        hangman_entity.update_output(False, hangman_entity.word, hangman_entity.word)
        await ctx.send("Holy shit you actually guessed it...")
        await ctx.send(hangman_entity)
        hangman_entity.reset()
        stop_timer = True
        return
    await ctx.send(hangman_entity)

@bot.command(
    name='show',
    help='Show the current hangman game.'
    )
async def bot_hang_show(ctx):
    if hangman_entity.player == '':
        await ctx.send("No hangman game being played.")
        return
    else:
        await ctx.send(hangman_entity)

@bot.command(
    name='quit',
    help='Quit the current hangman game.'
    )
async def bot_hang_quit(ctx):
    global stop_timer
    if hangman_entity.player == '':
        await ctx.send("No hangman game being played.")
        return
    elif ctx.author.nick.split("#")[0] != hangman_entity.player:
        await ctx.send("HA, no ya fucking don't...")
        return
    else:
        await ctx.send("The word was: " + hangman_entity.word)
        hangman_entity.reset()
        stop_timer = True

print("Initiating BOT")
bot.run(TOKEN)

