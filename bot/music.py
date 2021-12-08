from discord.embeds import Embed
from discord.ext import commands
import re
from discord.ext.commands.core import command
import lavalink
import discord
from lavalink.events import Event, QueueEndEvent
from spotify import *
from ytapi import *

url_rx = re.compile(r'https?://(?:www\.)?.+')

class Music(commands.Cog):

############ DONT TOUCH. THIS IS NEEDED FOR THE BOT TO WORK ###############

    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node("lava.link", self.bot.lavalinkport, self.bot.lavalinkpass, 'na', 'default-node')
            bot.add_listener(bot.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def ensure_voice(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError('Join a voice channel first.')

        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected.')

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            player.store('channel', ctx.channel.id)
            await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

############ DONT TOUCH. THIS IS NEEDED FOR THE BOT TO WORK ###############

    #The play command. A lot of jargon is used here but uses lavalink to play music.
    #If the user does "/play" with no input, it will attempt to unpause the song.
    # async def testing(self, ctx, _callback):
    #     player = self.bot.lavalink.player_manager.get(ctx.guild.id)
    #     player.play()
    #     await _callback(ctx)

    # async def doit(self,ctx):
    #     await ctx.send("it did it")


    @commands.command(aliases=['p'])
    async def play(self, ctx, *querys: str):
        query = " ".join(querys)
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')
        print("'" + query + "'")
        if query == "" and player.is_playing and player.paused:
            await player.set_pause(False)
            return

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')

        embed = discord.Embed(color=discord.Color.blurple())

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        test = ""
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist Queued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            if player.queue == [] and not player.is_playing:
                embed.title = 'Playing Track!'
            else:
                embed.title = 'Track Queued!'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

                       

    #Disconnects the player from the voice channel and clears its queue.
    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        """ Disconnects the player from the voice channel and clears its queue. """
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voicechannel!')

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await ctx.send('*⃣ | Disconnected.')

    #Pauses the song. To unpause just do /play
    @commands.command()
    async def pause(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if player.is_playing:
            await player.set_pause(True)
      
    @commands.command()
    async def info(self, ctx, *querys:str):
        query = " ".join(querys)
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')
        no_data_msg  = discord.Embed(title = "No data to display", description = "", color = 0x1DB954)
        wrong_format = discord.Embed(
            title = "Please format command as /info <song title> by <artist>. Capitalization and spelling must be exact.", 
            description = "", 
            color = 0x1DB954
        )

        if query == "":
            #display current info
            info = player.current.title
        
            if info.__contains__('-') or info.__contains__('–'):
                if info.__contains__(" ft."):
                    info = info.split(" ft.")[0]

                if info.__contains__(" feat."):
                    info = info.split(" feat.")[0]

                if info.__contains__('-'):
                    split = info.split(" - ")
                    artist = split[0]
                    title = split[1]
                else:
                    split = info.split(" – ")
                    artist = split[0]
                    title = split[1]

                if title.__contains__(" ("):
                    title = title.split(" (")[0]
        
                if artist.__contains__(","):
                    artist = artist.split(",")[0]

                title = title.strip()
                artist = artist.strip()

                if getTrackID(title, artist) == None:
                    await ctx.send(embed = no_data_msg)
                else:
                    res = botDisplay(getAll(title, artist))
        
                    if len(res) == 0:
                        res = botDisplay(getAll(artist, title))

                    if len(res) != 0:
                        msg = discord.Embed(
                            title = player.current.title,
                            description = "",
                            color = 0x1DB954
                        )
                        msg.add_field(name="Genre:", value=res[0], inline=False)
                        msg.add_field(name="Top Songs:", value=res[1], inline=False)
                        msg.add_field(name="Albums:", value=res[2], inline=False)
                        msg.add_field(name="Similar Artists:", value=res[3], inline=False)
                        msg.add_field(name="Similar Songs:", value=res[4], inline=False)
                        msg.set_image(url=res[5])
                        await ctx.send(embed = msg)
                    else:
                        await ctx.send(embed = no_data_msg)  
        else:
            title = ""
            artist = ""
            if query.__contains__("by") or query.__contains__("By"):
                if query.__contains__("by"):
                    s = query.split("by")
                    title = s[0]
                    artist = s[1]
                else:
                    s = query.split("By")
                    title = s[0]
                    artist = s[1]

                title = title.strip()
                artist = artist.strip()
                if getTrackID(title, artist) == None:
                    await ctx.send(embed = no_data_msg)
                else:
                    res = botDisplay(getAll(title, artist))
        
                    if len(res) == 0:
                        res = botDisplay(getAll(artist, title))

                    if len(res) != 0:
                        msg = discord.Embed(
                            title = title,
                            description = "",
                            color = 0x1DB954
                        )
                        msg.add_field(name="Genre:", value=res[0], inline=False)
                        msg.add_field(name="Top Songs:", value=res[1], inline=False)
                        msg.add_field(name="Albums:", value=res[2], inline=False)
                        msg.add_field(name="Similar Artists:", value=res[3], inline=False)
                        msg.add_field(name="Similar Songs:", value=res[4], inline=False)
                        msg.set_image(url=res[5])

                        await ctx.send(embed = msg)
                    else:
                        await ctx.send(embed = no_data_msg)
            else:
                await ctx.send(embed = wrong_format)



    #Clears the queue and stops the song
    @commands.command()
    async def clear(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        player.queue.clear()
        await player.stop()
        await ctx.send("Queue Cleared")

    #Skips the current song, if possible.
    @commands.command()
    async def skip(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await player.skip()

    @commands.command()
    async def queue(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        embed = discord.Embed(color=discord.Color.blurple())
        embed.title = "Queue:"
        desc = ""
        if player.queue == []:
            desc = "Queue is currently empty! Do '/play [SONG NAME]' to queue your next song."
            embed.description = desc
            await ctx.send(embed=embed)
        else:
            count = 1
            for i in player.queue:
                desc = desc + str(count) + ":  " + i.title + "\n\n"
                count += 1
            embed.description = desc
            await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, rem: int):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if rem >= 1:
            rem -= 1
        else:
            await ctx.send("Nothing to remove.")
            return
        if player.queue == []:
            await ctx.send("No queue found.")
        else:
            try:
                player.queue.pop(rem)
                await ctx.invoke(self.bot.get_command('queue'))
                await ctx.send("Song removed.")
            except IndexError:
                await ctx.send("Nothing to remove.")