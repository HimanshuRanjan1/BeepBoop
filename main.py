import os
import dotenv
import discord

a = 2+2
dotenv.load_dotenv()

token = os.getenv("DISCORD_TOKEN")
guilds = os.getenv("DISCORD_GUILD")

intent = discord.Intents.all()
bot = discord.Client(intents=intent)


@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        if guild.name == guilds:
            print(f"- {guild.id} (name : {guild.name})\n")
            break

        guild_count += 1
        
    members = '\n - '.join([member.name for member in guild.members])
    print(f"Guild Members : \n - {members}")
    

'''@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1148679496350838856)'''


@bot.event
async def on_message(message):
    channel = bot.get_channel(1149283559736098826)
    if message.author == bot.user:
        return

    if message.content == "hello boop":
        await channel.send("Hey There!")

bot.run(token)
