from codecs import ignore_errors
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_dl import YoutubeDL
import requests
import json
import spotipy.util as util
import details
from details import *


credentials = None
scopes=['https://www.googleapis.com/auth/youtube.readonly']

client_id= details.client_id
client_secret= details.client_secret
account = details.account_name




def spotify_auth():
    
    scope = "playlist-modify-private"
    token = util.prompt_for_user_token( scope = scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return token
        
        
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
        part='id, contentDetails',
        playlistId= 'PL7v1FHGMOadBTndBvtY4h213M10Pl9Y1c',   #change this youtube playlistID
        maxResults = 50,                       
        ).execute()
    
    nextPageToken = request.get('nextPageToken')
    while ('nextPageToken' in request):
        nextPage = youtube.playlistItems().list(
        part="snippet",
        playlistId='PL7v1FHGMOadBTndBvtY4h213M10Pl9Y1c',
        maxResults="50",
        pageToken=nextPageToken
        ).execute()
        request['items'] = request['items'] + nextPage['items']

        if 'nextPageToken' not in nextPage:
            request.pop('nextPageToken', None)
        else:
            nextPageToken = nextPage['nextPageToken']
    #print(request)
        
    return request


def yt_song_info(list):
    """Obtains the song details from youtube api and generates a link"""
    
    song_info= []
    for item in list["items"]:
        
        video_id = item["contentDetails"]["videoId"]
        youtube_link = f"https://youtu.be/{video_id}"
        #print(youtube_link)
        
        try:
            song_and_artist = YoutubeDL({'ignoreerrors': True}).extract_info(youtube_link, download=False)
            track, artist = song_and_artist['track'], song_and_artist['artist']
            if not song_and_artist:
                return []
            else:
                song_info.append((track, artist))
                print(song_info)    
            
        
        except KeyError:
            print('Song skipped')
            track = "Broken Strings"
            artist = 'James Morrison'
            song_info.append((track,artist))
            # return song_info
        
        
                
    

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
            "Authorization": f"Bearer {spotify_auth()}"}
    )
    
    spotify_response = spotify_response.json()
    #print(spotify_response)
    return spotify_response["id"]

def spotify_urls(track,artist):
    """Finds the songs on spotify using the youtube details"""
    
    url_query = f"https://api.spotify.com/v1/search?q={track}%2C{artist}&type=track,artist"
    response = requests.get(url_query,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {spotify_auth()}"
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
            "Authorization": f"Bearer {spotify_auth()}"
        }
    )
  
    print("Successfully made playlist!")


def run():
    spotify_auth()
    response = youtube_auth(credentials)
    playlist = create_spotify_playlist()
    song_details = yt_song_info(response)

    song_urls = []
    for i in range(len(response['items'])):
        song_urls.append(spotify_urls(song_details[i][0], song_details[i][1]))
        
    add_song_to_spotify_playlist(playlist, song_urls)
    
    
run()