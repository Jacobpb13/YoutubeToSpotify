import os
import pickle
from urllib import response
from wsgiref import headers
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_dl import YoutubeDL
import requests
import json
import spotipy
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials

credentials = None
scopes=['https://www.googleapis.com/auth/youtube.readonly']

client_id='4f1eb090c2ba4ef9b1aaed2f98e748ce'
client_secret='dc2ba2db68224eab98ab51aedc89f454'

#sscope = "user-library-read"

#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=sscope))





def get_spotify_token():
    """ Generate the token. Please respect these credentials :) """
    spotify_credentials = oauth2.SpotifyClientCredentials(
        client_id='4f1eb090c2ba4ef9b1aaed2f98e748ce',
        client_secret='dc2ba2db68224eab98ab51aedc89f454')
    spot_token = spotify_credentials.get_access_token()
    return spot_token

def youtube_auth(credentials):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=(r"C:\Users\jacob\OneDrive\Desktop\Programs\python_practice\youtubeToSpotify\youtubetospotify-342118-185125a4832a.json")
   


    if os.path.exists("token.pickle"):
        print("Loading credentials")
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
           # request_response()
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', scopes
                
            )

            flow.run_local_server(port=8080, prompt='consent',
                                authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials')
                pickle.dump(credentials, f)
               # request_response()
    
    youtube = build('youtube', 'v3', credentials=credentials)

    request = youtube.playlistItems().list(
        part='status, contentDetails',
        playlistId= 'PLaJd4NqiJg0gmkgnS7KJA8VV24UGg8hIs',
        maxResults = 50                         
    )
    response = request.execute()
    return response

            

# def request_response():
            
#     youtube = build('youtube', 'v3', credentials=credentials)

#     request = youtube.playlistItems().list(
#         part='status, contentDetails',
#         playlistId= 'PLaJd4NqiJg0gmkgnS7KJA8VV24UGg8hIs',
#         maxResults = 50                         
#     )
#     response = request.execute()
#     return response
    # request = youtube.playlistItems().list(
    #     part='snippet',
    #     playlistId= 'RDLUP0NjzDLPY',
    #     maxResults = 50                         
    # )
    
    #print(response)



def yt_song_info(list):
  
    song_info= []
    for item in list["items"]:
        
        video_id = item["contentDetails"]["videoId"]
        youtube_link = f"https://youtu.be/{video_id}"
        print(youtube_link)
        
        song_and_artist = YoutubeDL({}).extract_info(youtube_link, download=False)
        track, artist = song_and_artist['track'], song_and_artist['artist']
        
        song_info.append((track,artist))
        print(song_info)
        
    return song_info
    

def create_spotify_playlist():
    request_body = json.dumps(
        {
            "name": "YouTube Playlist",
            "description": "Converted Youtube Playlist",
            "public": False             
        }
    )
    spotify_request  = "https://api.spotify.com/v1/users/{}/playlists".format(
        client_id)
    spotify_response = requests.post(
        spotify_request,
        data = request_body,
        headers = {"Content-Type": "application/json",
            "Authorization": "Bearer BQB9wDfMnKuYV3gjL2I9LdKf86yHlBy4DTItXk3V4d9jU9r44nIptHLd4X_yWSvz_XZ0bo2wZ1bQV9GUMt4iu8hzt0-iS7C0cU61UvHCwQp443AJ836-_B0JmdSEfR-6fzFmPn232twFx-iEwg0NoKTJv2NBEgT9cuOaZG7zw65Ft4nekPXuKLoztQ3540BNi2B86a-z2CiZind-KqZbtAjgUrPzoFpn-Ub_c-xginZ9bnydQA"}
    )
    #print(spotify_response)
    return spotify_response

def spotify_urls(track,artist):
    url_query = "https://api.spotify.com/v1/search?q={}%2C{}&type=track,artist".format(track,artist)
    response = requests.get(url_query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer BQB9wDfMnKuYV3gjL2I9LdKf86yHlBy4DTItXk3V4d9jU9r44nIptHLd4X_yWSvz_XZ0bo2wZ1bQV9GUMt4iu8hzt0-iS7C0cU61UvHCwQp443AJ836-_B0JmdSEfR-6fzFmPn232twFx-iEwg0NoKTJv2NBEgT9cuOaZG7zw65Ft4nekPXuKLoztQ3540BNi2B86a-z2CiZind-KqZbtAjgUrPzoFpn-Ub_c-xginZ9bnydQA"
        }
    )
    response_json = response.json()
    #print(response_json)
    songs = response_json["tracks"]["items"]
    
    url = songs[0]["uri"]
    
    return url

def add_song_to_spotify_playlist(playlist_id,urls):
    request_data = json.dumps(urls)
  
    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        playlist_id)
  
    response = requests.post(
        query,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer BQB9wDfMnKuYV3gjL2I9LdKf86yHlBy4DTItXk3V4d9jU9r44nIptHLd4X_yWSvz_XZ0bo2wZ1bQV9GUMt4iu8hzt0-iS7C0cU61UvHCwQp443AJ836-_B0JmdSEfR-6fzFmPn232twFx-iEwg0NoKTJv2NBEgT9cuOaZG7zw65Ft4nekPXuKLoztQ3540BNi2B86a-z2CiZind-KqZbtAjgUrPzoFpn-Ub_c-xginZ9bnydQA"
        }
    )
  
    return "Song added"


stoken = get_spotify_token()
response = youtube_auth(credentials)
playlist = create_spotify_playlist()
song_details = yt_song_info(response)

song_urls = []
for i in range(len(response['items'])):
    song_urls.append(spotify_urls(song_details[i][0], song_details[i][1]))
    
add_song_to_spotify_playlist(playlist, song_urls)