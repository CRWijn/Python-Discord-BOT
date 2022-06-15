import os
import hangman
import time
import asyncio
import epicstore_api

from dotenv import load_dotenv, find_dotenv
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW


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
    test_channel = bot.get_channel(TEST_CHANNEL_ID)
    while (True):
        print("Doing EPIC STORE Check")
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
                        await channel.send("<@&867045278694637578>" + " " + game['title'] + " is free to keep on the epic store!")
                        if "\home" in game['productSlug']:
                            slug = game['productSlug'].split("\home")[0]
                            await channel.send("https://store.epicgames.com/en-US/p/" + slug)
                        else:
                            await channel.send("https://store.epicgames.com/en-US/p/" + game['productSlug'])
            else:
                try:
                    found = False
                    with open('free_games.txt') as f:
                        fdata = f.read()
                        f.close()
                    with open('free_games.txt') as f:
                        for line in f:
                            if line == game['title'] + "\n":
                                found = True
                        f.close()
                    if found:
                        fdata = fdata.replace(game['title'] + "\n", "")
                        with open('free_games.txt', 'w') as f:
                            f.write(fdata)
                            f.close()
                except FileNotFoundError:
                    with open('free_games.txt', 'w') as f:
                        f.close()

        print("Beginning Steam Check")
        chromeOptions = Options()
        chromeOptions.headless = True
        chrome_service = ChromeService('chromedriver')
        chrome_service.creationflags = CREATE_NO_WINDOW

        browser = webdriver.Chrome(options = chromeOptions, service = chrome_service)
        browser.get('https://store.steampowered.com/search/?maxprice=free&specials=1')

        try:
            game_names_list = []
            main = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'search_resultsRows')))

            games = main.find_elements(by=By.TAG_NAME, value="a")
            for i, game in enumerate(games):
                print(i)
                link = game.get_attribute('href')
                new_tab = webdriver.Chrome(options = chromeOptions)
                new_tab.get(link)
                try:
                    year_entry = new_tab.find_element(by=By.ID, value='ageYear')
                    year_entry_select = Select(year_entry)
                    year_entry_select.select_by_value('2000')
                    new_tab.find_element(by=By.ID, value='view_product_page_btn').click()
                except NoSuchElementException:
                    pass
                game_purchase = WebDriverWait(new_tab, 10).until(EC.presence_of_element_located((By.ID, 'game_area_purchase')))
                try:
                    dlc_bub = game_purchase.find_element(by=By.CLASS_NAME, value='game_area_dlc_bubble ')
                except NoSuchElementException:
                    try:
                        disc_block = game_purchase.find_element(by=By.CLASS_NAME, value='game_purchase_discount')
                        discount_percent = disc_block.find_element(by=By.CLASS_NAME, value='discount_pct')
                        if discount_percent.text == "-100%":
                            game_names_list.append((link, new_tab.find_element(by=By.ID, value='appHubAppName').text))
                    except NoSuchElementException:
                        pass
                finally:
                    new_tab.quit()

            literal_names = []
            for game in game_names_list:
                game_name = game[1]
                literal_names.append(game_name + "\n")
                try:
                    found = False
                    with open('free_games_steam.txt') as f:
                        for line in f:
                            if line == game_name + "\n":
                                found = True
                        f.close()
                    if not found:
                        with open('free_games_steam.txt', 'a') as f:
                            f.write(game_name + "\n")
                            f.close()
                        #ANNOUNCEMENT
                        await channel.send("<@&867045278694637578>" + " " + game_name + " is free to keep on the steam store!")
                        await channel.send(game[0])
                except FileNotFoundError:
                    with open('free_games_steam.txt', 'w') as f:
                        f.write(game_name + "\n")
                        f.close()
                    await channel.send("<@&867045278694637578>" + " " + game_name + " is free to keep on the steam store!")
                    await channel.send(game[0])

            removal_list = []
            with open('free_games_steam.txt') as f:
                sdata = f.read()
                f.close()
            with open('free_games_steam.txt') as f:
                for line in f:
                    if line not in literal_names:
                        removal_list.append(line)
                f.close()
            for game_to_remove in removal_list:
                sdata = sdata.replace(game_to_remove, "")
                with open('free_games_steam.txt', 'w') as f:
                    f.write(sdata)
                    f.close()
            
        except Exception as e:
            print(e)
            browser.quit()
            try:
                new_tab.quit()
            except:
                pass
        finally:
            browser.quit()

        await asyncio.sleep(43200)

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

