import discord
from discord.ext import commands
from time import sleep
import random
import bb
import os

bot = commands.Bot(command_prefix='$')


@bot.command(name='quit')
@commands.is_owner()
async def quit(ctx):
    exit(0)


def kick_chance(p):
    async def predicate(ctx):
        num = random.random()
        print(num)
        if (num <= p):
            await ctx.author.kick()
            return False
        else:
            return True

    return commands.check(predicate)


@bot.command()
@kick_chance(0.001)
async def boohoo(ctx):
    with open('images/boohoocracker.jpg', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command()
@kick_chance(0.001)
async def walt(ctx, *, text: commands.clean_content=None):
    if text is None:
        with open('images/breakingbad.gif', 'br') as img:
            await ctx.send(file=discord.File(img))
    else:
        await ctx.send(file=discord.File(
            bb.add_text(text), filename="walt.gif"))


@bot.command()
@kick_chance(0.001)
async def handshake(ctx):
    with open('images/me_and_my_best_friend.mp4', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command()
@kick_chance(0.001)
async def cracka(ctx):
    with open('images/cracka.gif', 'br') as img:
        await ctx.send(file=discord.File(img))


@bot.command(name='6914')
@commands.guild_only()
@kick_chance(0.001)
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
