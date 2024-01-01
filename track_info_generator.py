# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# import configparser
from pprint import pprint


def structure_song(track_details, audio_details):
    song_data = {
        'id': track_details['id'],
        'name': track_details['name'],
        'artists': [artist['name'] for artist in track_details['artists']],
        'id_artists': [artist['id'] for artist in track_details['artists']],
        'explicit': track_details['explicit'],
        'popularity': track_details['popularity'],
        'release_date': track_details['album']['release_date'],
    }

    for feature, value in audio_details.items():
        if feature in ['popularity', 'explicit', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']:
            song_data[feature] = value

    return song_data


# config = configparser.ConfigParser()
# config.read('./configs/config.cfg')

# SPOTIPY_CLIENT_ID = config.get('SPOTIFY', 'SPOTIPY_CLIENT_ID')
# SPOTIPY_CLIENT_SECRET = config.get('SPOTIFY', 'SPOTIPY_CLIENT_SECRET')
# SPOTIPY_REDIRECT_URI = config.get('SPOTIFY', 'SPOTIPY_REDIRECT_URI')

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope='user-library-read'))


def fetch_track_info(sp, id):
    track_uri = 'spotify:track:'+id
    track_details = sp.track(track_uri)
    audio_details = sp.audio_features(track_uri)[0]
    song = structure_song(track_details, audio_details)
    return song


def apply_cover_images(sp, df):
    for index, row in df.iterrows():
        track_details = sp.track(row['id'])
        cover_image_url = track_details['album']['images'][0]['url']
        df.at[index, 'album_cover'] = cover_image_url
    return df


def apply_preview_url(sp, df):
    for index, row in df.iterrows():
        track_details = sp.track(row['id'])
        preview_url = track_details['preview_url']
        df.at[index, 'preview_url'] = preview_url
    return df


def convert_msTo_min(milliseconds):
    total_seconds = milliseconds / 1000

    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)

    return f"{minutes}:{seconds}"
