import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("./data/tracks.csv")
df = df.sample(frac=1).reset_index(drop=True)

total_records = len(df)
subset_size = 10000
num_subsets = total_records // subset_size
subsets = [df.iloc[i * subset_size: (i + 1) * subset_size]
           for i in range(num_subsets)]


def call_data():
    global df
    global subsets
    df = pd.read_csv("./data/tracks.csv")
    df = df.sample(frac=1).reset_index(drop=True)

    total_records = len(df)
    subset_size = 10000
    num_subsets = total_records // subset_size
    subsets = [df.iloc[i * subset_size: (i + 1) * subset_size]
               for i in range(num_subsets)]
    return df, subsets


def get_recommendations_subset(song_index, cosine_sim_matrix, num_recommendations):
    sim_scores = list(enumerate(cosine_sim_matrix[song_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    song_indices = [i[0] for i in sim_scores[1:num_recommendations+1]]
    return song_indices


def generate_playlist(input_song, num_recommendations, explicit):
    global df
    global subsets
    df = df.sample(frac=1).reset_index(drop=True)

    if not explicit:
        df = df[df['explicit'] != 1]
    else:
        df, subsets = call_data()

    # print(df['explicit'].value_counts())

    features = df.drop(
        ['id', 'name', 'artists', 'id_artists', 'release_date', 'duration_ms', 'time_signature'], axis=1)
    features = features.sort_index(axis='columns')
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    user_input_df = pd.DataFrame(input_song)
    user_input_df = user_input_df.drop(
        ['id', 'name', 'artists', 'id_artists', 'release_date', 'duration_ms', 'time_signature'], axis=1)
    user_input_df = user_input_df.sort_index(axis='columns')
    user_scaled_features = scaler.transform(user_input_df)

    recommendations = []

    for i, subset in enumerate(subsets):
        scaler = StandardScaler()
        # print("Iteration : ", i)

        features = subset.drop(
            ['id', 'name', 'artists', 'id_artists', 'release_date', 'duration_ms', 'time_signature'], axis=1)
        features = features.sort_index(axis='columns')
        scaled_features = scaler.fit_transform(features)

        user_cosine_sim_subset = cosine_similarity(
            user_scaled_features, scaled_features)
        user_recommendations_subset = get_recommendations_subset(
            0, user_cosine_sim_subset, num_recommendations=5)
        # print(user_recommendations_subset)

        recommendations.append(subset.iloc[user_recommendations_subset])

    final_df = pd.concat(recommendations, ignore_index=True)
    final_features = final_df.drop(
        ['id', 'name', 'artists', 'id_artists', 'release_date', 'duration_ms', 'time_signature'], axis=1)
    final_features = final_features.sort_index(axis='columns')
    final_scaled_features = scaler.fit_transform(final_features)

    final_user_cosine_sim_subset = cosine_similarity(
        user_scaled_features, final_scaled_features)
    final_user_recommendations_subset = get_recommendations_subset(
        0, final_user_cosine_sim_subset, num_recommendations)

    output_playlist = final_df.iloc[final_user_recommendations_subset]

    return output_playlist


def generate_playlist_from_mood(input_mood, num_recommendations, explicit):
    global df
    global subsets
    if not explicit:
        df = df[df['explicit'] != 1]
    else:
        df, subsets = call_data()

    # print(df['explicit'].value_counts())

    mask = df['popularity'] >= 65
    df = df.drop(df[~mask].index)

    features = df.drop(
        ['id', 'name', 'popularity', 'duration_ms', 'explicit', 'artists', 'id_artists', 'release_date', 'key', 'mode', 'speechiness', 'instrumentalness', 'liveness', 'time_signature'], axis=1)
    features = features.sort_index(axis='columns')
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    user_input_df = pd.DataFrame(input_mood)
    user_input_df = user_input_df.sort_index(axis='columns')
    user_scaled_features = scaler.transform(user_input_df)

    recommendations = []

    for i, subset in enumerate(subsets):
        scaler = StandardScaler()
        # print("Iteration : ", i)

        mask = subset['popularity'] >= 65
        subset = subset.drop(subset[~mask].index)
        # print(subset.shape)
        # print(subset['popularity'].value_counts)

        features = subset.drop(
            ['id', 'name', 'popularity', 'duration_ms', 'explicit', 'artists', 'id_artists', 'release_date', 'key', 'mode', 'speechiness', 'instrumentalness', 'liveness', 'time_signature'], axis=1)
        features = features.sort_index(axis='columns')
        scaled_features = scaler.fit_transform(features)

        user_cosine_sim_subset = cosine_similarity(
            user_scaled_features, scaled_features)
        user_recommendations_subset = get_recommendations_subset(
            0, user_cosine_sim_subset, num_recommendations=5)
        # print(user_recommendations_subset)

        recommendations.append(subset.iloc[user_recommendations_subset])

    final_df = pd.concat(recommendations, ignore_index=True)
    print(final_df.shape)
    final_features = final_df.drop(
        ['id', 'name', 'popularity', 'duration_ms', 'explicit', 'artists', 'id_artists', 'release_date', 'key', 'mode', 'speechiness', 'instrumentalness', 'liveness', 'time_signature'], axis=1)
    final_features = final_features.sort_index(axis='columns')
    final_scaled_features = scaler.fit_transform(final_features)

    final_user_cosine_sim_subset = cosine_similarity(
        user_scaled_features, final_scaled_features)
    final_user_recommendations_subset = get_recommendations_subset(
        0, final_user_cosine_sim_subset, num_recommendations)

    output_playlist = final_df.iloc[final_user_recommendations_subset]

    return output_playlist
