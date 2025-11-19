import pandas as pd

df = pd.read_csv("spotify_top_songs_2023.csv", encoding="latin1", on_bad_lines="skip")

print("Before cleaning:\n", df.columns)

# Clean numeric columns safely
for col in ['streams', 'in_spotify_playlists', 'in_spotify_charts',
            'in_apple_playlists', 'in_apple_charts',
            'in_deezer_playlists', 'in_deezer_charts',
            'in_shazam_charts', 'bpm']:
    if col in df.columns:
        df[col] = (df[col].astype(str)
                              .str.replace(',', '', regex=False)
                              .str.extract('(\d+)', expand=False)
                              .astype(float))

# Drop rows with missing key metrics
df.dropna(subset=['streams', 'bpm'], inplace=True)

# Save cleaned file
df.to_csv("spotify_2023_cleaned.csv", index=False)
print("✅ Cleaned data saved as spotify_2023_cleaned.csv")
