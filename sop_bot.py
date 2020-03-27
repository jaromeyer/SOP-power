# sop_bot.py
import os, time, re, hashlib

import discord
from dotenv import load_dotenv
from PIL import Image

active = False
myTurn = True
players = 0
votes = {}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


def adb_execute(command):
    os.system('/Users/jaro/Library/Android/sdk/platform-tools/adb ' + command)


async def send_profile(message):
    global active, votes
    time.sleep(0.5)
    while True:
        response = "Loading image..."
        await message.channel.send(response)
        adb_execute('shell screencap -p /sdcard/DCIM/screenshot.png')
        adb_execute('pull /sdcard/DCIM/screenshot.png screenshot.png')
        adb_execute('shell input tap 880 1000')
        im = Image.open('screenshot.png')
        pix = im.load()
        im = im.crop((35, 193, 1050, 1687))
        im.save('cropped.png')
        await message.channel.send(file=discord.File('cropped.png'))
        if pix[1020, 202] == (255, 255, 255, 255) or pix[65, 202] != (255, 255, 255, 255):
            active = True
            votes = {}
            return


@client.event
async def on_message(message):
    global active, players, votes, myTurn
    print("Message: ", message.content, "- Author: ", message.author)
    if(message.attachments != []):
        img_hash = int(hashlib.sha256(
            bytes(message.attachments[0].id % 10)).hexdigest(), 16)
        myTurn = img_hash % 2 == 0
        print(message.attachments[0].id, img_hash)
    if message.content == 'Neue Runde...' and myTurn:
        await send_profile(message)

    if message.author == client.user:
        return

    if re.match(r'sop \d+', message.content) and not active:
        players = int(re.findall(r'\d+', message.content)[0])
        await message.channel.send("SOP started")
        await send_profile(message)
    elif message.content == 'stop' and active:
        active = False
        await message.channel.send("SOP stopped")
    elif active:
        if message.content == 'smash':
            votes[message.author.id] = True
        elif message.content == 'pass':
            votes[message.author.id] = False
        if len(votes) == players:
            active = False
            smash_count = 0
            for vote in votes.values():
                if vote:
                    smash_count += 1
            if smash_count == players/2:
                if votes[357527871482232833]:
                    response = "Die Uneinigkeit ist gross. Der fette hat sein Veto ausgesprochen: SMASH"
                    adb_execute('shell input tap 690 1820')
                else:
                    response = "Die Uneinigkeit ist gross. Der fette hat sein Veto ausgesprochen: PASS"
                    adb_execute('shell input tap 390 1820')
            elif smash_count > players/2:
                if smash_count == players:
                    response = "Der Grosse Rat hat sich entschieden: OBERMEGA-SMASH"
                else:
                    response = "Der Grosse Rat hat sich entschieden: SMASH"
                adb_execute('shell input tap 690 1820')
            else:
                if smash_count == 0:
                    response = "Der Grosse Rat hat sich entschieden: OBERMEGA-PASS:face_vomiting::face_vomiting::face_vomiting:"
                else:
                    response = "Der Grosse Rat hat sich entschieden: PASS"
                adb_execute('shell input tap 390 1820')
            await message.channel.send(response)
            await message.channel.send("Neue Runde...")

client.run(TOKEN)
