import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- PAGE SETUP ---
st.set_page_config(page_title="🎶 Rhythm of Emotions", layout="wide", page_icon="🎧")
st.markdown("""
    <style>
    body { background-color: #121212; color: #fff; }
    .main { background-color: #121212; color: white; }
    h1, h2, h3, h4 { color: #1DB954; }
    .stPlotlyChart { border-radius: 10px; box-shadow: 0 0 20px #1DB95433; }
    </style>
""", unsafe_allow_html=True)

# --- LOAD AND CLEAN DATA ---
st.title("🎶 Rhythm of Emotions – The Sound Palette of 2023")
st.caption("Dive into the emotional heartbeat of Spotify’s top songs from 2023.")

df = pd.read_csv("spotify_2023.csv", encoding="latin1")

for col in ["streams", "danceability_%", "energy_%", "valence_%", 
            "acousticness_%", "instrumentalness_%", "liveness_%", "speechiness_%"]:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace(",", "")
            .str.extract("(\d+\.?\d*)")[0]
            .astype(float)
        )

# --- GENRE + COUNTRY MAPS ---
genre_map = {
    "Jung Kook": "K-Pop", "Latto": "Hip-Hop", "Olivia Rodrigo": "Pop",
    "Taylor Swift": "Pop", "The Weeknd": "R&B", "Drake": "Hip-Hop",
    "Bad Bunny": "Reggaeton", "Myke Towers": "Latin", "SZA": "R&B",
    "Harry Styles": "Pop", "Miley Cyrus": "Pop", "Doja Cat": "Rap",
    "Travis Scott": "Hip-Hop", "Lana Del Rey": "Indie", "Billie Eilish": "Alternative",
    "Post Malone": "Pop-Rock", "Imagine Dragons": "Rock", "BLACKPINK": "K-Pop",
    "NewJeans": "K-Pop", "Peso Pluma": "Latin", "Karol G": "Reggaeton"
}

country_map = {
    "Jung Kook": "South Korea", "Latto": "USA", "Olivia Rodrigo": "USA",
    "Taylor Swift": "USA", "The Weeknd": "Canada", "Drake": "Canada",
    "Bad Bunny": "Puerto Rico", "Myke Towers": "Puerto Rico", "SZA": "USA",
    "Harry Styles": "United Kingdom", "Miley Cyrus": "USA", "Doja Cat": "USA",
    "Travis Scott": "USA", "Lana Del Rey": "USA", "Billie Eilish": "USA",
    "Post Malone": "USA", "Imagine Dragons": "USA", "BLACKPINK": "South Korea",
    "NewJeans": "South Korea", "Peso Pluma": "Mexico", "Karol G": "Colombia"
}

df["Genre"] = df["artist(s)_name"].map(lambda x: next((genre_map[a] for a in genre_map if a in x), "Pop"))
df["Country"] = df["artist(s)_name"].map(lambda x: next((country_map[a] for a in country_map if a in x), "USA"))

# --- MOOD CLASSIFICATION ---
def mood(val):
    if val >= 70: return "Happy"
    elif val >= 50: return "Chill"
    elif val >= 30: return "Sad"
    else: return "Melancholic"

df["Mood"] = df["valence_%"].apply(mood)

# --- SIDEBAR FILTER ---
st.sidebar.header("🎧 Filter the Dashboard")
selected_genre = st.sidebar.selectbox(
    "Select a Genre:",
    options=sorted(df["Genre"].unique().tolist()) + ["All"],
    index=len(df["Genre"].unique())
)

# Apply genre filter
if selected_genre != "All":
    filtered_df = df[df["Genre"] == selected_genre]
else:
    filtered_df = df

st.markdown(f"### 📀 Showing songs from genre: **{selected_genre}**")

# --- FUN FACTS ---
if not filtered_df.empty:
    happiest = filtered_df.loc[filtered_df["valence_%"].idxmax()]
    energetic = filtered_df.loc[filtered_df["energy_%"].idxmax()]
    chillest = filtered_df.loc[filtered_df["acousticness_%"].idxmax()]

    col1, col2, col3 = st.columns(3)
    col1.metric("🥳 Happiest Song", happiest["track_name"], f"{int(happiest['valence_%'])}% valence")
    col2.metric("⚡ Most Energetic", energetic["track_name"], f"{int(energetic['energy_%'])}% energy")
    col3.metric("🌙 Most Chill", chillest["track_name"], f"{int(chillest['acousticness_%'])}% acoustic")

st.markdown("---")

# --- SCATTER ---
st.subheader("🎨 Emotional Spectrum of 2023 Hits")
fig1 = px.scatter(
    filtered_df, x="valence_%", y="energy_%", size="streams", color="Mood",
    hover_data=["track_name", "artist(s)_name"],
    color_discrete_map={'Happy':'#00FF85','Chill':'#00C3FF','Sad':'#FF6F61','Melancholic':'#8B5CF6'},
)
fig1.update_layout(paper_bgcolor="#121212", plot_bgcolor="#121212", font_color="white")
st.plotly_chart(fig1, use_container_width=True)

# --- PIE + BAR ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("💚 Mood Distribution")
    mood_counts = filtered_df["Mood"].value_counts().reset_index()
    mood_counts.columns = ["Mood", "count"]
    fig2 = px.pie(mood_counts, values="count", names="Mood",
                  color="Mood",
                  color_discrete_map={'Happy':'#00FF85','Chill':'#00C3FF','Sad':'#FF6F61','Melancholic':'#8B5CF6'})
    fig2.update_layout(paper_bgcolor="#121212", font_color="white")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("🔥 Top 10 Streamed Songs")
    top10 = filtered_df.nlargest(10, "streams")
    fig3 = px.bar(top10, x="streams", y="track_name", orientation="h",
                  color="streams", color_continuous_scale="greens")
    fig3.update_layout(paper_bgcolor="#121212", plot_bgcolor="#121212", font_color="white")
    st.plotly_chart(fig3, use_container_width=True)

# --- MAP (NOW FILTERED BY GENRE) ---
st.subheader("🌍 Global Pulse – Top 10 Streamed Songs by Country")

top10 = filtered_df.nlargest(10, "streams").copy()

# Add extra mapping fallback
song_country_map = {
    "seven": "South Korea", "flowers": "United States", "kill bill": "United States",
    "vampire": "United States", "cruel summer": "United States", "calm down": "Nigeria",
    "sprinter": "United Kingdom", "idol": "Japan", "(it goes like) nanana": "Germany",
    "cupid": "South Korea", "blinding lights": "Canada"
}

top10["Country"] = top10.apply(
    lambda row: song_country_map.get(row["track_name"].strip().lower(),
                                     country_map.get(row["artist(s)_name"], "USA")), axis=1)

fig_map = px.scatter_geo(
    top10,
    locations="Country",
    locationmode="country names",
    color="track_name",
    hover_name="track_name",
    hover_data={"artist(s)_name": True, "streams": True, "Country": True},
    size="streams",
    projection="natural earth",
    title="Where the World Streamed 2023’s Biggest Hits 🌏"
)
fig_map.update_layout(
    geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="rgba(29,185,84,0.3)"),
    paper_bgcolor="#121212",
    font_color="white"
)
st.plotly_chart(fig_map, use_container_width=True)

# --- HEATMAP ---
st.subheader("💃 Energy vs Danceability")
fig5 = px.density_heatmap(
    filtered_df, x="energy_%", y="danceability_%",
    nbinsx=20, nbinsy=20, color_continuous_scale="Greens"
)
fig5.update_layout(paper_bgcolor="#121212", plot_bgcolor="#121212", font_color="white")
st.plotly_chart(fig5, use_container_width=True)

# --- EMOTION PALETTE ---
st.subheader("🌈 Emotion Palette of 2023")
sorted_df = filtered_df.sort_values("valence_%")
fig6 = px.imshow(
    [sorted_df["valence_%"]],
    color_continuous_scale=['#8B5CF6','#FF6F61','#00C3FF','#00FF85'],
    aspect="auto"
)
fig6.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.markdown("**Developed by Hrishita 💚 | Rhythm of Emotions | Spotify 2023**")
