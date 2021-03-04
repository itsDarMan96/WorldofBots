import discord
from youtube_dl import YoutubeDL
import youtube_dl
import os
import urllib
import re
from functools import partial
from async_timeout import timeout
import asyncio

from discord.ext import commands

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


client = commands.Bot(command_prefix="!") #we can give whatever but i choose to keep the usual

#client = discord.Client()

async def connect_(ctx, *, channel: discord.VoiceChannel = None):
    """
    Connect to voice.

    Parameters
    ------------
    channel: discord.VoiceChannel [Optional]
        The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
        will be made.

    This command also handles moving the bot to different channels.

    """
    if not channel:
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send(":notes: Please join voice channel or specify one with command!")

    vc = ctx.voice_client

    if vc:
        if vc.channel.id == channel.id:
            return
        try:
            await vc.move_to(channel)
        except asyncio.TimeoutError:
            raise VoiceConnectionError(
                f'Moving to channel: <{channel}> timed out.')
    else:
        try:
            await channel.connect()
        except asyncio.TimeoutError:
            raise VoiceConnectionError(
                f'Connecting to channel: <{channel}> timed out.')

    await ctx.send(f":notes: Connected to channel: **{channel}**", delete_after=20)

@client.command()
async def play(ctx, *, search):
    await ctx.trigger_typing()
    """
    vc = ctx.voice_client

    if not vc:
        await connect_(ctx)

    elif ctx.author not in ctx.guild.voice_client.channel.members:
        return await ctx.send(":notes: Please join Genaral voice channel to execute this command.", delete_after=20)

    """
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    query_string= urllib.parse.urlencode({
        'search_query': search
    })
    print(query_string)
    html_content = urllib.request.urlopen(
        'http://www.youtube.com/results?' + query_string
    )
    print(html_content)
    search_results = re.findall(r"watch\?v=(\S{11})",html_content.read().decode())
    print(search_results)
    #await ctx.send('http://www.youtube.com/watch?v='+search_results[0])
    yt_url = "https://www.youtube.com/watch?v="+ search_results[0]
    print(yt_url)

    '''
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return
    '''

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    ytdl = YoutubeDL(ydl_opts)
    '''
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    '''
    ffmpegopts = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }
    loop = asyncio.get_event_loop()
    to_run = partial(ytdl.extract_info, url=yt_url, download=False)
    data = await loop.run_in_executor(None, to_run)
    
    voice.play(discord.FFmpegPCMAudio(data['url']), data=data, requester=ctx.author)



@client.command(name='leave')
async def _leave(ctx):
    voice=discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


@client.command()
async def hello(ctx, *args):
    await ctx.send("Hello, "+ctx.author+ " I am your very own Music bot.")



    print(ctx.author)
    print(ctx.message)
    print(ctx.guild)

#@client.event
"""
async def on_message(message):
    message.content = message.content.lower()
    if message.author==client.user:
        return
    if message.content.startswith("hello"):
        await message.channel.send("Hello, I am a Music Bot.")
"""

client.run('')
