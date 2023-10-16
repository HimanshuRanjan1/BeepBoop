#Important imports

import os
import dotenv
import discord
from PIL import Image, ImageDraw
import random
import yt_dlp as youtube_dl
import asyncio
import numpy


#Photo Edit

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

#youtube-dl initializing
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # binding to ipv4 since ipv6 addresses cause issues sometimes
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

ffmpeg_options = {
    'options': '-vn'
}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

#Search Song by name

def search(title):
    global ytdl,r
    #if get_url(title) is not None:
     #   return title
    r = ytdl.extract_info(title,download=False)

    if r == None:
        return None
    
    videocode = r['entries'][0]['id']

    return "https://www.youtube.com/watch?v={}".format(videocode)

#env file loader

dotenv.load_dotenv()

token = os.getenv("DISCORD_TOKEN")
guilds = {}

#Bot initiator

intent = discord.Intents.all()
bot = discord.Client(intents=intent)
cmd = discord.app_commands.CommandTree(bot)

#knock knock jokes
chatWith = ""
knMsg = 0


#Bot Events

def register(guild):
    file = open("guilds.txt",'a')
    file.write(guild.name+',')
    file.close()


@bot.event
async def on_ready():
    global guilds

    file = open("guilds.txt",'r')
    file_txt = []
    for i in file:
        for j in i.split(','):
            file_txt.append(j)
            
    file.close()
    for guild in bot.guilds:
        guilds[guild.name] = 0
        if guild.name not in file_txt:
            register(guild)
        await cmd.sync(guild = discord.Object(id = guild.id))
        
    print("Boop is READY!")
    

@bot.event
async def on_member_join(member):
    try:
        for ch in member.guild.channels:
            if ch.name.lower() == 'welcome':
                channel = bot.get_channel(ch.id)
    except:
        channel = bot.get_channel((member.guild.channels)[0].id)
    welcome = {"wild":f"Huh!! A wild {member.mention} appeared","pizza":f"Welcome, {member.mention}. We hope you brought pizza.","weapon":f"Welcome, {member.mention}. Leave your weapons by the door.","banana":f"{member.mention} just joined. HIDE YOUR BANANAS!","spawn":f"{member.mention} has spawned in the guild","challenge":f"Challenger approaching - {member.mention} has appeared!","disappoint":f"It's a bird! It's a plane! Nevermind, it's just {member.mention}."}
    choice = random.choice(list(welcome.keys()))
    pics = {"pizza":"img\\pizza.png","weapon":"img\\weapons.png","banana":"img\\banana.png","spawn":"img\\spawn.gif","challenge":"img\\vs.png","disappoint":"img\\disappointed.png"}
    
    if choice == "wild":
        fname = "avatar.png"
        await member.display_avatar.save(fname)
        im = Image.open('avatar.png')
        im = add_corners(im, 220)
        im.save('avatar.png')
        with open('avatar.png','rb') as f:
            avatar = discord.File(f)
            await channel.send(welcome[choice])
            await channel.send(file = avatar)
    else:
        with open(pics[choice],'rb') as f:
            avatar = discord.File(f)
            await channel.send(welcome[choice])
            await channel.send(file = avatar)


@bot.event
async def on_message(message):
    global chatWith,knMsg
    channel = bot.get_channel(message.channel.id)
    greet = ["What's kicking, little chicken?","Howdy, partner!","Wassup, homey?","Tring tring…this chat may or may not be recorded for training purposes."]
    if message.author == bot.user:
        return

    if message.content.lower() == "hello boop":
        await channel.send(random.choice(greet))

    elif message.content.lower() == "knock knock":
        chatWith = message.author
        knMsg = knMsg + 1
        await channel.send("Who's There?")

    elif message.author == chatWith:
        if knMsg == 1:
            await channel.send(f"{message.content} who?")
            knMsg = knMsg + 1
        elif knMsg == 2:
            react = ["LMAO 😂","I am Speechless! You are so Hilarious! 😂"]
            await channel.send(random.choice(react))

#Bot Commands


@cmd.command(name = "say",description = "To Say something",guild = discord.Object(id = 1149408094711980172))
async def say(args,string: str):
    if string.lower() == "hello":
        await args.response.send_message(f"{string} {args.user.display_name}")
    else:
        await args.response.send_message(f"{string}")


@cmd.command(name = "join_voice",description = "Prompts Boop to join a voice channel",guild = discord.Object(id = 1149408094711980172))
async def join(args,string: str):
    global guilds
    vClient = guilds[args.guild.name]
    try:
        print('here')
        for vc in bot.get_guild(args.guild_id).voice_channels:
            if vc.name.lower() == string.lower():
                break
        print('here1')
        channel = bot.get_channel(vc.id)
        guilds[args.guild.name] = await channel.connect()
        await args.response.send_message(f"Boop Connected to Channel {vc.name}.")
        print('here2')
    except:
        await args.response.send_message(f"Boop is already in Channel {vClient.channel.name}.")
        await args.channel.send("Try using '/hop_to' command to change the Channel Boop is Connected to.")


@cmd.command(name = "leave_voice",description = "Prompts Boop to leave the Voice Channel",guild = discord.Object(id = 1149408094711980172))
async def leave(args):
    vClient = args.guild.voice_client
    try:
        await vClient.disconnect()
        await args.response.send_message(f"Boop Disconnected from Channel {vClient.channel.name}.")
    except:
        await args.response.send_message(f"Boop is not Connected to any Voice Channel.")


@cmd.command(name = "hop_to",description = "Prompts Boop to hop to another Voice Channel",guild = discord.Object(id = 1149408094711980172))
async def hop(args,string: str):
    global guilds
    vClient = args.guild.voice_client
    try:
        await vClient.disconnect()
        for vc in bot.get_guild(args.guild_id).voice_channels:
            if vc.name.lower() == string.lower():
                break
        channel = bot.get_channel(vc.id)
        guilds[args.guild.name] = await channel.connect()
        await args.response.send_message(f"Boop Hopped to Voice Channel {vc.name}.")
    except:
        await args.response.send_message(f"Boop is not Connected to any Channel.")
        await args.channel.send("Try using '/join_voice' command to prompt Boop to Connect to a Channel.")


@cmd.command(name = "play_song",description = 'Prompts Boop to play a song',guild = discord.Object(id = 1149408094711980172))
async def play(args,name: str):
    global guilds
    vClient = guilds[args.guild.name]
    try:
        vc = bot.get_guild(args.guild_id).voice_channels[0]
        channel = bot.get_channel(vc.id)
        guilds[args.guild.name] = await channel.connect()
        vClient = guilds[args.guild.name]
    except:
        pass

    await args.channel.typing()
    await args.response.send_message(f"**Boop is Now Playing {name} **")

    url = search(name)

    filename = await YTDLSource.from_url(url,loop = bot.loop)
    vClient.play(discord.FFmpegPCMAudio(executable = "D:\Discordbot\BeepBoop\\ffmpeg.exe",source = filename))


@cmd.command(name = "pause_song",description = "Prompts Boop to pause the song",guild = discord.Object(id = 1149408094711980172))
async def pause(args):
    global guilds
    vClient = guilds[args.guild.name]
    await args.channel.typing()
    try:
        vClient.pause()
        await args.response.send_message("**Boop paused the Song.**")
    except:
        await args.response.send_message("Boop is not playing any Song. Use '/play_song' command to play a song")


@cmd.command(name = "resume",description = "Prompts Boop to resume the song",guild = discord.Object(id = 1149408094711980172))
async def resume(args):
    global guilds
    vClient = guilds[args.guild.name]
    await args.channel.typing()
    try:
        if vClient.is_paused():
            vClient.resume()
            await args.response.send_message("**Boop has resumed the song.**")
    except:
        await args.response.send_message("Boop has not paused any song.")


@cmd.command(name = "stop",description = "Prompts Boop to stop the song",guild = discord.Object(id = 1149408094711980172))
async def stop(args):
    global guilds
    vClient = guilds[args.guild.name]   
    await args.channel.typing()
    try:
        vClient.stop()
        await args.response.send_message("**Boop has stopped playing the song.**")
    except:
        await args.response.send_message("Boop is not playing any song.")
            

#Bot Startup


bot.run(token)


#add queue

@commands.command()
async def join(self, ctx):

    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel!")
        return
    else:
        channel = ctx.message.author.voice.channel
        self.queue = {}
        await ctx.send(f'Connected to ``{channel}``')

    await channel.connect()

@commands.command()
async def play(self, ctx, *, url):

    try:

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

            if len(self.queue) == 0:

                self.start_playing(ctx.voice_client, player)
                await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n<:youtube:763374159567781890> **Now Playing:** ``{}'.format(player.title) + "``")

            else:
                
                self.queue[len(self.queue)] = player
                await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n<:youtube:763374159567781890> **Added to queue:** ``{}'.format(player.title) + "``")

    except:

        await ctx.send("Somenthing went wrong - please try again later!")

def start_playing(self, voice_client, player):

    self.queue[0] = player

    i = 0
    while i <  len(self.queue):
        try:
            voice_client.play(self.queue[i], after=lambda e: print('Player error: %s' % e) if e else None)

        except:
            pass
        i += 1