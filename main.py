import os
import pickle
from tokenize import Token
from urllib import response
from wsgiref import headers
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_dl import YoutubeDL
import requests
import json
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import details
from details import *
import base64
import asyncio

credentials = None
scopes=['https://www.googleapis.com/auth/youtube.readonly']

client_id= details.client_id
client_secret= details.client_secret
account = details.account_name

def spotify_auth(client_id, client_secret):
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    authHeader = {}
    authData = {}
    #scopes = 'playlist-modify-private'
    message = f"{client_id}:{client_secret}"
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    authHeader['Authorization'] = "Basic " + base64_message
    authData['grant_type'] = "client_credentials"
    request = requests.post(AUTH_URL, headers=authHeader, data=authData)
    
    responseObj = request.json()
    print(json.dumps(responseObj, indent=2))
    access_token = responseObj['access_token']
    return access_token
    
    

def youtube_auth(credentials):
    """OAuth for youtube, requests a refresh token or creates a new one and saves"""
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=(r"C:\Users\jacob\OneDrive\Desktop\Programs\python_practice\youtubeToSpotify\youtubetospotify-342118-185125a4832a.json")
   


    if os.path.exists("token.pickle"):
        print("Loading credentials")
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
           
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

            # Save the credentials for reuse
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials')
                pickle.dump(credentials, f)
               
    
    youtube = build('youtube', 'v3', credentials=credentials)
    
    
    request = youtube.playlistItems().list(
        part='status, contentDetails',
        playlistId= 'PLaJd4NqiJg0gmkgnS7KJA8VV24UGg8hIs',   #change this youtube playlistID
        maxResults = 50                        
        )
    response = request.execute()
        
    return response


def yt_song_info(list):
    """Obtains the song details from youtube api and generates a link"""
    
    song_info= []
    for item in list["items"]:
        
        video_id = item["contentDetails"]["videoId"]
        youtube_link = f"https://youtu.be/{video_id}"
        #print(youtube_link)
        
        song_and_artist = YoutubeDL({}).extract_info(youtube_link, download=False)
        track, artist = song_and_artist['track'], song_and_artist['artist']
        
        song_info.append((track,artist))
        print(song_info)
        
    return song_info
    

def create_spotify_playlist():
    """Creates a spotify playlist using spotify api post"""
    
    print("Creating spotify playlist...")
    request_body = json.dumps(
        {
            "name": "YouTube Playlist",
            "description": "Converted Youtube Playlist",
            "public": False             
        }
    )
    spotify_url  = f"https://api.spotify.com/v1/users/{account_name}/playlists"
    
    spotify_response = requests.post(
        spotify_url,
        data = request_body,
        headers = {"Content-Type": "application/json",
            "Authorization": f"Bearer {spotify_auth(client_id,client_secret)}"}
    )
    
    spotify_response = spotify_response.json()
    print(spotify_response)
    return spotify_response["id"]

def spotify_urls(track,artist):
    """Finds the songs on spotify using the youtube details"""
    
    url_query = f"https://api.spotify.com/v1/search?q={track}%2C{artist}&type=track,artist"
    response = requests.get(url_query,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {spotify_auth(client_id,client_secret)}"
        }
    )
    response_json = response.json()
    
    songs = response_json["tracks"]["items"]
    
    url = songs[0]["uri"]
    
    return url

def add_song_to_spotify_playlist(playlist_id,urls):
    """Adds the songs found on spotify to the created playlist"""
    
    print("Adding songs to spotify playlist...")
    request_data = json.dumps(urls)
  
    query = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
  
    response = requests.post(
        query,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {spotify_auth(client_id,client_secret)}"
        }
    )
  
    print("Successfully made playlist!")


def run():
    access = spotify_auth(client_id,client_secret)
    print(access)
    response = youtube_auth(credentials)
    playlist = create_spotify_playlist()
    song_details = yt_song_info(response)

    song_urls = []
    for i in range(len(response['items'])):
        song_urls.append(spotify_urls(song_details[i][0], song_details[i][1]))
        
    add_song_to_spotify_playlist(playlist, song_urls)
    
    
run()