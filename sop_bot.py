# sop_bot.py
import os
import time

import discord
from dotenv import load_dotenv
from PIL import Image 

active = False
veto = False
votes = {}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_message(message):
    global active
    global votes
    print("Message: ", message.content, "- Author: ", message.author)
    if message.author == client.user:
        return

    if message.content == 'start' and not active:
        active = True
        response = "Smash or Pass has started"
        await message.channel.send(response)
    elif message.content == 'stop' and active:
        active = False
        response = "Smash or Pass has stoped"
        await message.channel.send(response)
    elif active:
        if message.content == 'smash':
            votes[message.author.id] = True
            response = "gönn dir " + message.author.display_name
            await message.channel.send(response)
        elif message.content == 'pass':
            votes[message.author.id] = False
            response = "fettig " + message.author.display_name
            await message.channel.send(response)
        
        if len(votes) == 2:
            active = False
            smash_count = 0
            pass_count = 0
            for vote in votes.values():
                if vote:
                    smash_count += 1
                else:
                    pass_count += 1
            if smash_count == pass_count:
                if votes[357527871482232833]:
                    response = "Die Uneinigkeit ist gross. Der fette hat sein Veto ausgesprochen: smash"
                    os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb shell input tap 690 1820')
                else:
                    response = "Die Uneinigkeit ist gross. Der fette hat sein Veto ausgesprochen: pass"
                    os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb shell input tap 390 1820')
            elif smash_count > pass_count:
                response = "Der grosse Rat hat sich für smash entschieden"
                os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb shell input tap 690 1820')
            else:
                response = "Der grosse Rat hat sich für pass entschieden"
                os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb shell input tap 390 1820')
            await message.channel.send(response)

            while True:
                time.sleep(0.5)
                os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb shell screencap -p /sdcard/DCIM/screenshot.png')
                os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb pull /sdcard/DCIM/screenshot.png screenshot.png')
                os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb shell input tap 880 1000')
                im = Image.open('screenshot.png')
                pix = im.load()
                im = im.crop((35, 193, 1050, 1687))
                im.save('cropped.png')
                await message.channel.send(file=discord.File('cropped.png'))
                if pix[1020,202] == (255, 255, 255, 255) or pix[65,202] != (255, 255, 255, 255):
                    break
            votes = {}
            active = True

client.run(TOKEN)
