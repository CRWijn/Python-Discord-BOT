import os
import hangman
import time
import asyncio

from dotenv import load_dotenv, find_dotenv
from discord.ext import commands


load_dotenv('token.env')
TOKEN = os.environ.get('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='daddy ')
hangman_entity = hangman.start_hangman()
global timer

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
    global timer
    if hangman_entity.player != '':
        await ctx.send("Wait your turn! " + hangman_entity.player + " is still playing!")
        return

    hangman_entity.reset()
    hangman_entity.player = ctx.author.nick.split("#")[0]
    await ctx.send("Hangman game started, use 'daddy guess' to guess!")
    await ctx.send(hangman_entity)

    timer = 0
    while (True):
        print(timer)
        if timer > 60:
            hangman_entity.reset()
            await ctx.send("<@{}>".format(ctx.author.id) + " Waited too long to guess. Game over :/")
            return
        await asyncio.sleep(1)
        timer += 1

@bot.command(
    name='guess',
    help='Guess a letter or word for hangman game.'
    )
async def bot_guess_hangman(ctx, guess=''):
    global timer
    timer = 0
    if hangman_entity.player == '':
        await ctx.send("No hangman game being played.")
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
        return
    elif "".join(hangman_entity.word_status) == hangman_entity.word:
        hangman_entity.update_output(False, hangman_entity.word, hangman_entity.word)
        await ctx.send("Holy shit you actually guessed it...")
        await ctx.send(hangman_entity)
        hangman_entity.reset()
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
    if hangman_entity.player == '':
        await ctx.send("No hangman game being played.")
        return
    else:
        await ctx.send("The word was: " + hangman_entity.word)
        hangman_entity.reset()

print("Initiating BOT")
bot.run(TOKEN)

