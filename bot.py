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
import stockquotes
from decimal import *
import pickle

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

class NotEnoughError(Exception):
    def __init__(self, needed, have):
       self.needed = needed
       self.have = have

class Person:
    def __init__(self, balance=Decimal(0)):
        self.balance = balance
        self.stocks = defaultdict(Decimal)

    def buy_stock(self, ticker, shares=1):
        ticker = ticker.upper()
        stock = stockquotes.Stock(ticker)
        if shares*Decimal(stock.current_price) > self.balance:
            raise NotEnoughError(shares*Decimal(stock.current_price), self.balance)
        elif stock.current_price <= 0:
            raise stockquotes.StockDoesNotExistError
        else:
            self.stocks[ticker] += shares
            self.balance -= shares*Decimal(stock.current_price)
        return shares*Decimal(stock.current_price)

    def sell_stock(self, ticker, shares=1):
        ticker = ticker.upper()
        stock = stockquotes.Stock(ticker)
        if shares > self.stocks[ticker]:
            raise NotEnoughError(shares, self.stocks[ticker])
        else:
            self.stocks[ticker] -= shares
            self.balance += shares*Decimal(stock.current_price)
            if self.stocks[ticker] == 0:
                del self.stocks[ticker]

        return shares*Decimal(stock.current_price)


"""
Economy Commands
"""

costs = {}

def load_people():
    try:
        with open("people.pickle", "rb") as infile:
            return pickle.load(infile)
    except FileNotFoundError:
        return {}

people = defaultdict(Person, load_people())

for person in people.values():
    for stock in list(person.stocks.keys()):
        if not stock.isupper():
            person.stocks[stock.upper()] += person.stocks[stock]
            del person.stocks[stock]
        elif person.stocks[stock] == 0:
            del person.stocks[stock]

def save_people():
    with open("people.pickle", "wb") as outfile:
        pickle.dump(people, outfile)


atexit.register(save_people)


def command_cost(p, name):
    costs[name] = p

    async def predicate(ctx):
        if (people[str(ctx.author.id)].balance < p):
            await ctx.send(
                "{}, this command has an invocation cost of {} KhalilCoin™ and your current balance is {:.2f} KhalilCoin™.".
                format(ctx.author.mention, p, people[str(ctx.author.id)].balance))
            return False
        else:
            people[str(ctx.author.id)].balance -= p
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
            people[str(ctx.author.id)].balance += value[0]
        else:
            await msg.edit(
                content="Sorry {}, you didn't click the right button!".format(
                    ctx.author.mention))

@bot.command()
async def balance(ctx):
    await ctx.send("{}, your current balance is {:.2f} KhalilCoin™".format(
        ctx.author.mention, people[str(ctx.author.id)].balance))


@bot.command()
async def buy(ctx, shares: Decimal, ticker: str):
    ticker = ticker.upper()
    if (shares <= 0):
        return
    try:
        await ctx.send("{}, you purchased {} shares of {} for {:.2f} KhalilCoin™".format(
            ctx.author.mention, shares, ticker, people[str(ctx.author.id)].buy_stock(ticker, shares)))
    except NotEnoughError as e:
        await ctx.send("{}, you need {:.2f} KhalilCoin™ to buy {} shares of {}, but your balance is only {:.2f} KhalilCoin™".format(ctx.author.mention, e.needed, shares, ticker, e.have))
    except stockquotes.StockDoesNotExistError as e:
        await ctx.send("{}, that is not a valid ticker symbol".format(ctx.author.mention))

@bot.command()
async def sell(ctx, shares: Decimal, ticker: str):
    ticker = ticker.upper()
    if (shares <= 0):
        return
    try:
        await ctx.send("{}, you sold {} shares of {} for {:.2f} KhalilCoin™".format(
            ctx.author.mention, shares, ticker, people[str(ctx.author.id)].sell_stock(ticker, shares)))
    except NotEnoughError as e:
        await ctx.send("{}, you are trying to sell {} shares of {}, but you only have {} shares".format(ctx.author.mention, e.needed, ticker, e.have))
    except stockquotes.StockDoesNotExistError as e:
        await ctx.send("{}, that is not a valid ticker symbol".format(ctx.author.mention))

@bot.command()
async def portfolio(ctx):
    await ctx.send("{}, your current portfolio is:\n{}".format(ctx.author.mention, '\n'.join(["{} {}".format(shares, ticker) for ticker, shares in people[str(ctx.author.id)].stocks.items()])))

@bot.command()
async def price(ctx, ticker: str):
    ticker = ticker.upper()
    stock = stockquotes.Stock(ticker)
    await ctx.send("{}, the price of {} is {} KhalilCoin™ per share".format(ctx.author.mention, ticker, stock.current_price))

@bot.command()
@commands.is_owner()
async def brrr(ctx, amount: int, recipient: discord.Member):
    await ctx.send("{}, your balance has been increased by {} KhalilCoin™!".
                   format(recipient.mention, amount))
    people[str(recipient.id)].balance += amount


"""
Stupid Commands
"""


@bot.command()
@command_cost(10, "boohoo")
async def boohoo(ctx):
    with open('images/boohoocracker.jpg', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command()
@command_cost(10, "walt")
async def walt(ctx, *, text: commands.clean_content=None):
    if text is None:
        with open('images/breakingbad.gif', 'br') as img:
            await ctx.send(file=discord.File(img))
    else:
        await ctx.send(file=discord.File(
            bb.add_text(text), filename="walt.gif"))

@bot.command()
@command_cost(10, "tlaw")
async def tlaw(ctx, *, text: commands.clean_content=None):
    if text is None:
        with open('images/breakingbad_reversed.gif', 'br') as img:
            await ctx.send(file=discord.File(img))
    else:
        await ctx.send(file=discord.File(
            bb.add_text(text, img_file='mages/breakingbad_reversed.gif'), filename="walt.gif"))


@bot.command()
@command_cost(10, "handshake")
async def handshake(ctx):
    with open('images/me_and_my_best_friend.mp4', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command()
@command_cost(10, "cracka")
async def cracka(ctx):
    with open('images/cracka.gif', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command(name='6914')
@commands.guild_only()
@command_cost(10, "6914")
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
