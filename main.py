import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from youtube_dl import YoutubeDL


credentials = None

def authentication():
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
                'client_secret.json.json',
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
        playlistId= 'RDLUP0NjzDLPY',
        maxResults = 50                         
    )

    # request = youtube.playlistItems().list(
    #     part='snippet',
    #     playlistId= 'RDLUP0NjzDLPY',
    #     maxResults = 50                         
    # )
    response = request.execute()
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
        
    #return song_info
    
yt_song_info()   

