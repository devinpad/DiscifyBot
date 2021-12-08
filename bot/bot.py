from discord.ext import commands
import os
import time
from music import Music
import discord
from ytapi import *
from artist_info import *

# Global list containing all availble bot commands
commandsList = ["ping: pOnG", 
                "helpme: I assume you've already figured this out",
				"play (Song Title): I can play a song for you as long as you are in a voice chat!", 
				"pause: Pauses the song. Do /play to unpause!",
				"clear: Clears the queue",
				"skip: Skips the song",
                "disconnect: Later!",
				"info (Song Name): I'll grab as much information as possible about the currently playing song, or any other!",
                "topsongs (Artist Name): I'll show you the top ten songs of whatever artist you choose",
                "url (Song Title): I can grab a youtube url of whatever song you like!",
                "topalbums (Artist Name): I can list an artist's top albums.",
                "relatedartists (Artist Name): I can show you a bunch of artists similar to the one you requested!",
                "genre (Artist Name): I can display some information about what genres this artists fits into!",
                "pic (Artist Name): I can show you a picture of the artist you request."]


# Helper function to create embedded message
def created_embedded_msg(title, description, color, name, value, inline):
	# Create embedded message
	embedded_msg = discord.Embed(
				title = title,
				description = description,
				color = color
			)
	embedded_msg.add_field(name=name, value=value, inline=inline)

	# Return embedded message
	return embedded_msg


#This class is used to get the body started along with lavalink, the music playing application we use.
class Bot:
	def __init__(self, **kwargs):
		self.intents = discord.Intents.default()
		self.intents.members = True
		if "prefix" not in kwargs:
			raise "You must provide a prefix"
		else:
			self.bot = commands.Bot(command_prefix = kwargs["prefix"], intents = self.intents)
			self.bot.lavalinkpass = kwargs["lavalinkpass"]
			self.bot.lavalinkport = kwargs["lavalinkport"]

	def connect(self, token):		
		print("Starting processes!")
		time.sleep(5)
		print("Running Lavalink.")
		#Thread(target = lavarun).start()
		time.sleep(30) # yep i intentionally used a blocking module
		# lavalink takes a while to boot up
		# so this is to make sure its ready when bot gets ready
		self.bot.add_cog(init(self.bot))
		print("-------------------------------\nRunning Bot!")
		self.bot.run(token)

#This is the main body of the bot itself. The music player functionality is within a different file.
class init(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print("The bot is ready!")
		self.bot.add_cog(Music(self.bot))

	# Bot Command: /helpme
	# Purpose: Displays a message containing all available bot commands a discord server member may utilize.
	@commands.command(pass_context=True)
	async def helpme(self, ctx):
		# Initialize variables
		title = "Help Me"
		description = "Hi I'm Discify, your all-purpose Discord Music Bot!\nHere's what I can do if you type /(command):\n"
		color = 0x1DB954
		name = "Commands List:"
		commands = ""

		# Format commandsList into string
		for command in commandsList:
			commands += "• " + command + "\n"

		# Create embedded message
		spoken_str = created_embedded_msg(title, description, color, name, commands, True)
		
		# Send embedded message
		await ctx.send(embed = spoken_str)


	# Bot Command: /topsongs
	# Purpose: Displays a message containing a user entered artist's top 10 songs.
	@commands.command(pass_context=True)
	async def topsongs(self, ctx, *querylist):
		# Initialize variables
		artist = " ".join(querylist)
		title = "Top Songs"
		description = "Here are your artist's top 10 songs.\n"
		color = 0x1DB954
		name = artist + "'s Top 10:"
		songs = ""

		# Get artist's top 10 songs from Spotify API
		top10_list = getTop10Songs(artist)
		
		# Format top10_list into string
		for song in top10_list:
			songs += "• " + song + "\n"

		# Create embedded message
		spoken_str = created_embedded_msg(title, description, color, name, songs, True)

		# Send embedded message
		await ctx.send(embed = spoken_str)


	# Bot Command: /url
	# Purpose: Returns the song title, channel name, and YouTube url from a user entered song.
	@commands.command(pass_context=True)
	async def url(self, ctx, *querylist):
		# Initialize variables
		query = " ".join(querylist)
		title = "Song URL"
		description = "Here is the title, artist, and YouTube url for your song.\n"
		color = 0x1DB954
		video_title = "Title:"
		video_channel = "Artist:"
		video_url = "YouTube URL:"

		# Get song data from YouTube API
		data = get_youtube_data(query)

		# Access variables from YouTube data dictionary
		song_title = data['title']
		song_channel = data['artist']
		song_url = data['video_url']
		
		# Create embedded message
		spoken_str = created_embedded_msg(title, description, color, video_title, song_title, False)
		spoken_str.add_field(name=video_channel, value=song_channel, inline=False)
		spoken_str.add_field(name=video_url, value=song_url, inline=False)

		# Send embedded message
		await ctx.send(embed = spoken_str)


	# Bot Command: /topalbums
	# Purpose: Returns top albums from a user entered artist.
	@commands.command(pass_context=True)
	async def topalbums(self, ctx, *querylist):
		# Initialize variables
		artist = " ".join(querylist)
		title = "Top Albums"
		description = "Here are your artist's top albums.\n"
		color = 0x1DB954
		name = artist + "'s Top Albums:"
		albums = ""

		# Get artist's top albums from Spotify API
		topalbums = getTopAlbums(artist)

		# Format topalbums list into string
		for album in topalbums:
			albums += '• ' + album['name'] + '\n'

		# Create embedded message
		spoken_str = created_embedded_msg(title, description, color, name, albums, True)

		# Send embedded message
		await ctx.send(embed = spoken_str)


	# Bot Command: /relatedartists
	# Purpose: Returns related artists to a user entered artist.
	@commands.command(pass_context=True)
	async def relatedartists(self, ctx, *querylist):
		# Get user query
		query = " ".join(querylist)
		title = "Related Artists"
		description = "Related Artists to " + query + ":\n"
		color = 0x1DB954
		name = "You Might Like These:"
		artists = ""

		# Get artist's related artists from Spotify API
		data = getRelatedArtists(query)

		# Create string the bot will print
		for i in data:
			artists += '• ' + i + '\n'

		# Create embedded message
		spoken_str = created_embedded_msg(title, description, color, name, artists, True)

		# Bot prints the string
		await ctx.send(embed=spoken_str)


	# Bot Command: /artistPic
	# Purpose: Returns artist pic of a user entered artist.
	@commands.command(pass_context=True)
	async def pic(self, ctx, *querylist):
		query = " ".join(querylist)
		msg = discord.Embed(
			title="Artist Pic",
			description='This is ' + query + ':\n',
			color=0x1DB954
		)
		data = getArtistImage(query)
		msg.set_image(url=data)
		await ctx.send(embed = msg)


	# Bot Command: /getGenre
	# Purpose: Returns genre of a user entered artist.
	@commands.command(pass_context=True)
	async def genre(self, ctx, *querylist):
		query = " ".join(querylist)
		title = "Get Genre"
		description = 'Here is the genre information I could find from Spotify on ' + query + '! \n ' \
																						'If you want to dive into ' \
																						'genres, checkout this cool ' \
																						'site https://everynoise.com/ \n'
		color = 0x1DB954
		name = "Genres: "
		genres = ""
		data = getArtistGenre(query)

		for v in data:
			genres += '•' + v + '\n'

		spoken_str = created_embedded_msg(title, description, color, name, genres, True)
		await ctx.send(embed=spoken_str)

	@commands.command(pass_context=True)
	async def ping(self, ctx):
		await ctx.send("Pong!")
