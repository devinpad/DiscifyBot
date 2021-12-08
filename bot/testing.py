from discord.ext.commands import bot
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# from bot.testing import CLIENT_ID, CLIENT_SECRET

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')


def getID(name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    res1 = sp.search(name, limit=1)
    res2 = res1['tracks']
    res3 = dict(res2['items'][0])
    res4 = res3['album']
    res5 = dict(res4['artists'][0])
    return res5['id']


def getName(name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    res1 = sp.search(name, limit=1)
    res2 = res1['tracks']
    res3 = dict(res2['items'][0])
    res4 = res3['album']
    res5 = dict(res4['artists'][0])
    return res5['name']


def getTop10Songs(name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    topSongs = []
    id = getID(name)
    res1 = sp.artist_top_tracks(id)['tracks']
    for i in res1:
        topSongs.append(i['name'])
    return topSongs


def getTopAlbums(name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    albums = []
    id = getID(name)
    res1 = sp.artist_albums(id)['items']
    for i in res1:
        if i['album_type'] == 'album':
            count = 0
            temp = {"name": "", "image": ""}
            temp['name'] = i['name']
            image = i['images']
            temp['image'] = image[0]['url']
            for j in albums:
                if (j["name"] == i['name']):
                    count += 1
            if count == 0:
                albums.append(temp)
    return albums


def getRelatedArtists(name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    related_artists = []
    id = getID(name)
    res1 = sp.artist_related_artists(id)['artists']
    for i in res1:
        related_artists.append(i['name'])
    return related_artists


def getArtistImage(name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    id = getID(name)
    res1 = sp.artist(id)['images']
    return res1[0]['url']


def getArtistGenre(name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    genres = []
    id = getID(name)
    res1 = sp.artist(id)['genres']
    for i in res1:
        genres.append(i)
    return genres


def getTrackID(name, artist):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    res1 = sp.search(name)
    res2 = res1['tracks']
    res3 = res2['items']
    str1 = "string"

    for i in res3:
        if artist in str(i):
            tempname = str(i['name'])
            if tempname.__contains__(" ("):
                if type(tempname) != type(str1):
                    return 0
                else:
                    tempname = tempname.split(" (")[0]
                tempname = tempname.strip()

            if len(tempname) == len(name):
                return i['id']


def getRelatedSongs(name, artist):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    arr = []
    id = getTrackID(name, artist)
    res1 = sp.recommendations([], [], [id])
    res2 = res1['tracks']
    for i in res2:
        temp = {"title": i['name'], "artist": ""}
        res3 = i['artists']
        res4 = res3[0]
        temp['artist'] = res4['name']
        arr.append(temp)
    return arr


def getAll(song_title, name):
    client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    info = {"genre": "", "top songs": "", "albums": "", "related artists": "", "related songs": "", "image": ""}
    info['genre'] = getArtistGenre(name)
    info['top songs'] = getTop10Songs(name)
    info["albums"] = getTopAlbums(name)
    info['related artists'] = getRelatedArtists(name)
    info['related songs'] = getRelatedSongs(song_title, name)
    info['image'] = getArtistImage(name)
    return info


def botDisplay(info):
    res = []

    # genre
    genre_from_dict = info['genre']
    str1 = ""
    for i in genre_from_dict:
        index = (genre_from_dict.index(i)) + 1
        if index == len(genre_from_dict):
            temp = str(i)
        else:
            temp = str(i) + ", "
        str1 += temp
    res.append(str1)

    # top songs
    top_songs_from_dict = info['top songs']
    str2 = ""
    for i in top_songs_from_dict:
        index = (top_songs_from_dict.index(i)) + 1
        if index == len(top_songs_from_dict):
            temp = str(i)
        else:
            temp = str(i) + ", "
        str2 += temp
    res.append(str2)

    # albums
    albums_from_dict = info['albums']
    str3 = ""
    for i in albums_from_dict:
        index = (albums_from_dict.index(i)) + 1
        if index == len(albums_from_dict):
            temp = str(i['name'])
        else:
            temp = str(i['name']) + ", "
        str3 += temp
    res.append(str3)

    # related artists
    related_artists_from_dict = info['related artists']
    str4 = ""
    for i in related_artists_from_dict:
        index = (related_artists_from_dict.index(i)) + 1
        if index == len(related_artists_from_dict):
            temp = str(i)
        else:
            temp = str(i) + ", "
        str4 += temp
    res.append(str4)

    # related songs
    related_songs_from_dict = info['related songs']
    str5 = ""
    for i in related_songs_from_dict:
        index = (related_songs_from_dict.index(i)) + 1
        if index == len(related_songs_from_dict):
            temp1 = str(i['title'])
            temp2 = " by " + str(i['artist'])
            temp3 = temp1 + temp2
            str5 += temp3

        else:
            temp1 = str(i['title'])
            temp2 = " by " + str(i['artist']) + ", "
            temp3 = temp1 + temp2
            str5 += temp3
    res.append(str5)

    # image
    res.append(info['image'])

    return res

def test():
    if getTrackID("SLOW DANCING IN THE DARK", "Joji") == None:
        print("None")
    else:
        print(getTrackID("Run", "Joji"))

test()
