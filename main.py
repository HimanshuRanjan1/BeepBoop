import os
import dotenv
import discord
from PIL import Image, ImageDraw
import random

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

dotenv.load_dotenv()

token = os.getenv("DISCORD_TOKEN")
guilds = os.getenv("DISCORD_GUILD")

intent = discord.Intents.all()
bot = discord.Client(intents=intent)
cmd = discord.app_commands.CommandTree(bot)

#knock knock jokes
chatWith = ""
knMsg = 0

#VoiceClient
vClient = None


@bot.event
async def on_ready():
    guild_count = 0
    await cmd.sync(guild = discord.Object(id = 1149408094711980172))

    for guild in bot.guilds:
        if guild.name == guilds:
            print(f"- {guild.id} (name : {guild.name})\n")
            break

        guild_count += 1
        
    members = '\n - '.join([member.name for member in guild.members])
    print(f"Guild Members : \n - {members}")
    

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1149408095672483945)
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
    channel = bot.get_channel(1149408183786418317)
    greet = ["What's kicking, little chicken?","Howdy, partner!","Wassup, homey?","Tring tring…this chat may or may not be recorded for training purposes."]
    if message.author == bot.user:
        return

    if message.channel.name == "general":
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


@cmd.command(name = "say",description = "To Say something",guild = discord.Object(id = 1149408094711980172))
async def say(args,string: str):
    channel = bot.get_channel(args.channel_id)
    if string.lower() == "hello":
        await channel.send(f"{string} {args.user.display_name}")
    else:
        await channel.send(f"{string}")


@cmd.command(name = "join_voice",description = "Prompts Boop to join a voice channel",guild = discord.Object(id = 1149408094711980172))
async def join(args,string: str):
    for vc in bot.get_guild(args.guild_id).voice_channels:
        if vc.name == str:
            break
    channel = bot.get_channel(vc.id)
    global vClient
    vClient = await channel.connect()
    await args.channel.send(f"Boop Connected to Channel {vc.name}")

@cmd.command(name = "leave_voice",description = "Prompts Boop to leave the Voice Channel",guild = discord.Object(id = 1149408094711980172))
async def leave(args):
    global vClient
    await vClient.disconnect()
    await args.channel.send(f"Boop Disconnected from Channel {vClient.channel.name}")
            


bot.run(token)
