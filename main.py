import os
import pickle
from urllib import response
from wsgiref import headers
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_dl import YoutubeDL


os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=(r"C:\Users\jacob\OneDrive\Desktop\Programs\python_practice\youtubeToSpotify\youtubetospotify-342118-185125a4832a.json")
credentials = None


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
            'client_secret.json',
            scopes=[
                'https://www.googleapis.com/auth/youtube.readonly'
            ]
        )

        flow.run_local_server(port=8080, prompt='consent',
                            authorization_prompt_message='')
        credentials = flow.credentials

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials')
            pickle.dump(credentials, f)

            

def request_response():
            
    youtube = build('youtube', 'v3', credentials=credentials)

    request = youtube.playlistItems().list(
        part='status, contentDetails',
        playlistId= 'PLaJd4NqiJg0gmkgnS7KJA8VV24UGg8hIs',
        maxResults = 50                         
    )
    response = request.execute()
    yt_song_info(response)
    # request = youtube.playlistItems().list(
    #     part='snippet',
    #     playlistId= 'RDLUP0NjzDLPY',
    #     maxResults = 50                         
    # )
    
    #print(response)



def yt_song_info(response):
  
    song_info= []
    for item in response["items"]:
        video_id = item["contentDetails"]["videoId"]
        youtube_link = f"https://youtu.be/{video_id}"
        print(youtube_link)
        
        song_and_artist = YoutubeDL({}).extract_info(youtube_link, download=False)
        track, artist = song_and_artist['track'], song_and_artist['artist']
        song_info.append((track,artist))
        print(song_info)
        
    return song_info
    

def create_spotify_playlist():
    request_body = json.dumps({
  "name": "New Playlist",
  "description": "New playlist description",
  "public": False             })
    spotify_request = query = "https://api.spotify.com/v1/users/{}/playlists".format(
        #####spotify user)
    spotify_response = request.post(
        spotify_request,
        data = request_body,
        headers = {"Content-Type": "application/json",
            "Authorization": "Bearer {}".format("spotify_token")}
    )
    return spotify_response["id"]
    
    







#request_response()

