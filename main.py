from config import *
import pylast
import discord
import os
from discord.ext import tasks
from classes import *
import requests
import base64
client = discord.Client()
network = pylast.LastFMNetwork(api_key=lastfm_config["api_key"], api_secret=lastfm_config["Shared_secret"],
                               username=lastfm_config["Owner"], password_hash=pylast.md5(lastfm_config["Password"]))
SESSION_KEY_FILE = os.path.join(os.path.expanduser("~"), ".session_key")
if not os.path.exists(SESSION_KEY_FILE):
    skg = pylast.SessionKeyGenerator(network)
    url = skg.get_web_auth_url()

    print(f"Please authorize this script to access your account: {url}\n")
    import time
    import webbrowser

    webbrowser.open(url)

    while True:
        try:
            session_key = skg.get_web_auth_session_key(url)
            with open(SESSION_KEY_FILE, "w") as f:
                f.write(session_key)
            break
        except pylast.WSError:
            time.sleep(1)
else:
    session_key = open(SESSION_KEY_FILE).read()
network.session_key = session_key
last_song = ""


@client.event
async def on_ready():
    print(f'logged in as {client.user}')
    set_presence.start()


@tasks.loop(seconds=3)
async def set_presence():
    global last_song
    song = network.get_user(lastfm_config["lastfm_username"]).get_now_playing()
    if song is not None:
        if song.title != last_song:
            last_song = song.title
            if song.get_album() is not None:
                if song.get_album().get_cover_image() is not None:
                    art = song.get_album().get_cover_image()
                    art.replace("300x300", "512x512")
                else:
                    art = "https://lastfm.freetls.fastly.net/i/u/512x512/2a96cbd8b46e442fc41c2b86b821562f.png"
                    print("No Art Found,using default image")
                album = song.get_album().get_title()
            else:
                album = "Unknown Album"
                art = "https://lastfm.freetls.fastly.net/i/u/512x512/2a96cbd8b46e442fc41c2b86b821562f.png"
                print("Unkown album using default image")
            print(song)
            print(album)
            print(art)
            await client.change_presence(
                activity=Custom_listening_activity(
                    name=song.title,
                    details=f"by {song.artist}",
                    assets={
                        # song.get_album().get_cover_image(pylast.SIZE_LARGE),
                        "large_text": album,
                        "small_text": album
                    },

                )
            )
    else:
        await client.change_presence(status=discord.Status.online, activity=None)
        print("No song playing")
client.run(TOKEN)
