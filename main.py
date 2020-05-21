import spotipy
import time
import os
import re
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from twitter_scraper import get_tweets

load_dotenv()

username = os.environ.get('SPOTIFY_USERNAME')
redirect_uri = "http://localhost:8888/callback/"
scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"
device_id = os.environ.get('SPOTIFY_DEVICE_ID')

token = util.prompt_for_user_token(username, scope, client_id=os.environ.get('SPOTIPY_CLIENT_ID'), client_secret=os.environ.get('SPOTIPY_CLIENT_SECRET'), redirect_uri=redirect_uri)
sp = spotipy.Spotify(auth=token)

tweets_indexed = []
sp.start_playback(device_id=device_id)

def spotify_search_song(title):
    return sp.search(title, limit=1, type="track")

def spotify_add_to_queue(uri, device_id):
    print("Adding song to playlist")
    sp.add_to_queue(uri, device_id=device_id)
    pass

def spotify_ensure_media_playing():
    pass

current_artist = None
current_song = None

while True:
    now_playing = sp.current_playback()

    if (now_playing['item']['name'] != current_song) and (now_playing['item']['artists'][0]['name'] != current_artist):
        current_artist = now_playing['item']['artists'][0]['name']
        current_song = now_playing['item']['name']
        print("Currently playing {0} - {1}".format(current_song, current_artist))

    for tweet in get_tweets(os.environ.get('TWITTER_HASHTAG'), pages=1):
       if tweet['tweetId'] not in tweets_indexed: 
        result = spotify_search_song(re.sub(r".(#\w+)","",tweet['text']))
        #album_art = result['tracks']['items'][0]['album']['images'][0]['url']
        uri = result['tracks']['items'][0]['uri']
        spotify_add_to_queue(uri, device_id)
        tweets_indexed.append(tweet['tweetId'])
       
    time.sleep(30)