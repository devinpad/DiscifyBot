import os
import discord
from discord_slash import SlashCommand
from discord.ext import commands
import time

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = "/", intents = intents)
slash = SlashCommand(client, override_type=True)

def connect(token):		
    print("Starting processes!")
    #Thread(target = lavarun).start()
    time.sleep(20) # yep i intentionally used a blocking module
    # lavalink takes a while to boot up
    # so this is to make sure its ready when bot gets ready
    print("-------------------------------\nRunning Bot!")
    client.run(token)

client.load_extension("bot")

my_secret = os.environ.get('TOKEN')

connect(my_secret)
