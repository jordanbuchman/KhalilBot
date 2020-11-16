import discord
from discord.ext import commands
from time import sleep
import random
import bb
import os
from collections import defaultdict
import asyncio
from random_emoji import random_emoji
import atexit
import json


class KBHelpCommand(commands.MinimalHelpCommand):

    def __init__(self):
        super(KBHelpCommand, self).__init__()
        self.verify_checks = False

    def get_command_signature(self, command):
        if command.name in costs:
            return '`{0.clean_prefix}{1.qualified_name} {1.signature}`\nCosts {2} KhalilCoin™'.format(
                self, command, costs[command.name])
        else:
            return '`{0.clean_prefix}{1.qualified_name} {1.signature}`'.format(
                self, command)


bot = commands.Bot(command_prefix='$', help_command=KBHelpCommand())


@bot.command(name='quit')
@commands.is_owner()
async def quit(ctx):
    exit(0)


"""
Economy Commands
"""

costs = {}


def load_balances():
    try:
        with open("balances.json", "r") as infile:
            return json.load(infile)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_balances():
    with open("balances.json", "w") as outfile:
        json.dump(balances, outfile)


atexit.register(save_balances)

balances = defaultdict(lambda: 0, load_balances())


def command_cost(p, name):
    costs[name] = p

    async def predicate(ctx):
        if (balances[str(ctx.author.id)] < p):
            await ctx.send(
                "{}, this command has an invocation cost of {} KhalilCoin™ and your current balance is {} KhalilCoin™.".
                format(ctx.author.mention, p, balances[str(ctx.author.id)]))
            return False
        else:
            balances[str(ctx.author.id)] -= p
            return True

    return commands.check(predicate)


@bot.command()
async def mine(ctx):
    # buttons = [(6, "6️⃣"), (9, "9️⃣"), (1, "1️⃣"), (4, "4️⃣")]
    # buttons = [(i, random_emoji()[0]) for i in [6,9,1,4]]
    buttons = list(zip([6, 9, 1, 4], random.sample(bot.emojis, 4)))
    value = random.choice(buttons)

    msg = await ctx.send('KhalilCoin™ Miner (v6.914) initializing...')

    await asyncio.gather(* [msg.add_reaction(b[1]) for b in buttons])

    sleep(0.5)

    await msg.edit(
        content='{}, press the {} button to mine KhalilCoin™!'.format(
            ctx.author.mention, value[1]))

    def check(reaction, user):
        return reaction.message == msg and user == ctx.author

    try:
        reaction, _ = await bot.wait_for(
            'reaction_add', timeout=2.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(content="Sorry {}, too slow!".format(ctx.author.mention))
    else:
        if reaction.emoji == value[1]:
            await msg.edit(
                content="Congrats {}, you successfully mined {} KhalilCoin™!".
                format(ctx.author.mention, value[0]))
            balances[str(ctx.author.id)] += value[0]
        else:
            await msg.edit(
                content="Sorry {}, you didn't click the right button!".format(
                    ctx.author.mention))


@bot.command()
async def balance(ctx):
    await ctx.send("{}, your current balance is {} KhalilCoin™".format(
        ctx.author.mention, balances[str(ctx.author.id)]))


@bot.command()
@commands.is_owner()
async def brrr(ctx, amount: int, recipient: discord.Member):
    await ctx.send("{}, your balance has been increased by {} KhalilCoin™!".
                   format(recipient.mention, amount))
    balances[str(recipient.id)] += amount


"""
Stupid Commands
"""


@bot.command()
@command_cost(10, "boohoo")
async def boohoo(ctx):
    with open('images/boohoocracker.jpg', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command()
@command_cost(15, "walt")
async def walt(ctx, *, text: commands.clean_content=None):
    if text is None:
        with open('images/breakingbad.gif', 'br') as img:
            await ctx.send(file=discord.File(img))
    else:
        await ctx.send(file=discord.File(
            bb.add_text(text), filename="walt.gif"))


@bot.command()
@command_cost(20, "handshake")
async def handshake(ctx):
    with open('images/me_and_my_best_friend.mp4', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command()
@command_cost(15, "cracka")
async def cracka(ctx):
    with open('images/cracka.gif', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command(name='6914')
@commands.guild_only()
@command_cost(40, "6914")
async def snof(ctx, text=None):
    channel = max(ctx.guild.voice_channels,
                  key=lambda c: len(c.voice_states.keys()))
    if len(channel.voice_states.keys()) == 0:
        channel = discord.utils.get(ctx.guild.voice_channels, name="6914")

    print(channel)

    vc = await channel.connect()

    if text is None:
        audio = discord.FFmpegPCMAudio('sounds/6914.mp3')
        vc.play(audio, after=lambda e: print('done', e))
        while vc.is_playing():
            sleep(0.05)
    else:
        text = [c for c in text if c in '6914']
        for c in text[:10]:
            vc.play(discord.FFmpegPCMAudio('sounds/{}.mp3'.format(c)))
            while vc.is_playing():
                sleep(0.05)

    await vc.disconnect()


bot.run(os.getenv('DISCORD_KEY'))
