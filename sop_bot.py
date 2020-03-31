# sop_bot.py
import os
import time
import re
import hashlib

import requests
import discord
from dotenv import load_dotenv
from PIL import Image, ImageFilter
import pytesseract

multiplayer = True
myTurn = True

active = False
players = 0
votes = {}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


def adb_execute(command):
    os.system(r'/Users/jaro/Library/Android/sdk/platform-tools/adb ' + command)


async def send_profile(message):
    global active, votes
    time.sleep(0.5)
    im_count = 1
    if not os.path.exists(r'img/temp'):
        os.makedirs(r'img/temp')
    else:
        for f in os.listdir(r'img/temp'):
            os.remove(r'img/temp/%s' % f)
    while True:
        adb_execute('shell screencap -p /sdcard/DCIM/screenshot.png')
        adb_execute('pull /sdcard/DCIM/screenshot.png img/screenshot.png')
        adb_execute('shell input tap 880 1000')
        im = Image.open(r'img/screenshot.png')
        pix = im.load()
        im = im.crop((35, 193, 1050, 1687))
        im.save(r'img/temp/cropped%d.png' % im_count)
        if im_count == 1:
            temp = im.convert('L')
            temp = temp.point(lambda i: i < 250 and 255)
            temp = temp.filter(ImageFilter.GaussianBlur(0.5))
            im_name = temp.crop((130, 30, 500, 76))
            im_name.save(r'img/temp/name.png')
            name = pytesseract.image_to_string((im_name)).replace('\n', '')
            im_age = temp.crop((340, 75, 420, 115))
            age = pytesseract.image_to_string((im_age), config='digits')
            im_desc = temp.crop((27, 1300, 1000, 1465))
            im_desc.save(r'img/temp/desc.png')
            desc = pytesseract.image_to_string((im_desc)).replace('\n', '')
            response = "**%s**" % name
            if age != "":
                response += " (%s)" % age
                if int(age) < 16:
                    response += "\n:warning:**ACHTUNG YÄNNE: Dieses Fräulein ist ein bisschen zu jung!**:warning: "
            if desc != "":
                response += "\n%s" % desc
            await message.channel.send(response)
            insta_match = re.search(
                "((Instagram|instagram|Insta|insta|IG|1G|ig|@):\s?|@)(\S+)", desc)
            if insta_match != None:
                insta_url = "https://www.instagram.com/%s" % insta_match.group(
                    3)
                try:
                    r = requests.get(insta_url).text
                except:
                    print("Instagram error")
                else:
                    followers = int(re.search(
                        '"edge_followed_by":{"count":([0-9]+)}', r).group(1))
                    insta_response = "%s (%i Followers)" % (
                        insta_url, followers)
                    if followers < 150:
                        insta_response += "\n**Nicht für den Gebrauch im Garten geeignet!**"
                    elif followers > 500:
                        insta_response += "\n:warning:**Vorsicht: Gartengerät höchster Qualität!**:warning:"
                    else:
                        insta_response += "\n**Auf dieses Gerät ist verlass**"
                    await message.channel.send(insta_response)
        await message.channel.send(file=discord.File(r'img/temp/cropped%d.png' % im_count))
        im_count += 1
        if pix[1020, 202] == (255, 255, 255, 255) or pix[65, 202] != (255, 255, 255, 255):
            active = True
            votes = {}
            return


@client.event
async def on_message(message):
    global active, players, votes, myTurn
    print("Message: ", message.content, "- Author: ",
          message.author, message.author.id)
    if(message.attachments != []):
        img_hash = int(hashlib.sha256(
            bytes(message.attachments[0].id % 10)).hexdigest(), 16)
        myTurn = img_hash % 2 == 0
        print(message.attachments[0].id, img_hash)
    if (re.match(r'(Der fette.*|Der Grosse Rat.*)', message.content) and myTurn and multiplayer):
        await send_profile(message)

    if message.author == client.user:
        return

    if re.match(r'sop \d+', message.content) and not active:
        players = int(re.findall(r'\d+', message.content)[0])
        myTurn = True
        if not os.path.exists(r'img'):
            os.makedirs(r'img')
        if not os.path.exists(r'img/oms'):
            os.makedirs(r'img/oms')
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
                if votes[290120734997479425]:
                    response = "Der fette hat sein Veto ausgesprochen: **SMASH**:peach:"
                    adb_execute('shell input tap 690 1820')
                else:
                    response = "Der fette hat sein Veto ausgesprochen: **PASS**:nauseated_face:"
                    adb_execute('shell input tap 390 1820')
            elif smash_count > players/2:
                if smash_count == players:
                    folder_index = max(
                        [int(f) for f in next(os.walk(r'img/oms'))[1]]) + 1
                    os.rename(r'img/temp', r'img/oms/%i' % folder_index)
                    response = "Der Grosse Rat hat entschieden: **OBERMEGA-SMASH**:peach::eggplant::sweat_drops:"
                else:
                    response = "Der Grosse Rat hat entschieden: **SMASH**:peach:"
                adb_execute('shell input tap 690 1820')
            else:
                if smash_count == 0:
                    response = "Der Grosse Rat hat entschieden: **OBERMEGA-PASS**:face_vomiting:"
                else:
                    response = "Der Grosse Rat hat entschieden: **PASS**:nauseated_face:"
                adb_execute('shell input tap 390 1820')
            await message.channel.send(response)
            if not multiplayer:
                await send_profile(message)

client.run(TOKEN)
