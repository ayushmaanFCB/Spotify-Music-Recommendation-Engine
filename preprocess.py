import warnings
warnings.filterwarnings("ignore")

import pandas
import numpy

def get_decade(year):
    period_start = int(year/10) * 10
    decade = '{}s'.format(period_start)
    return decade

def preprocess_dataset(df):
    df['name'].fillna("not available", inplace=True)
    df['decade'] = df['year'].apply(get_decade)
    df = df[df['decade'] != "1900s"]

    unique_artists = df['id_artists'].unique()
    artist_to_index = {artist: idx for idx, artist in enumerate(unique_artists)}
    df['artist_index'] = df['id_artists'].map(artist_to_index)