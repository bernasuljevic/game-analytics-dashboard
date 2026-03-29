import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import os

sns.set(style="whitegrid")

st.set_page_config(layout="wide")
st.title("🎯 Valorant Player Analytics Dashboard")

# 🔗 
@st.cache_data
def load_data():
    db_path = "game_data.db"

    # DB yoksa CSV'den oluştur
    if not os.path.exists(db_path):
        df = pd.read_csv("game_data.csv")

        conn = sqlite3.connect(db_path)
        df.to_sql("game_sessions", conn, if_exists="replace", index=False)
        conn.close()

    # DB'den oku
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM game_sessions", conn)
    conn.close()

    return df


df = load_data()

# 🎯 FILTERS
st.sidebar.header("Filters")

selected_agent = st.sidebar.multiselect(
    "Select Agent",
    options=df["agent"].unique(),
    default=df["agent"].unique()
)

level_range = st.sidebar.slider(
    "Level Range",
    int(df["level"].min()),
    int(df["level"].max()),
    (1, 50)
)

filtered_df = df[
    (df["agent"].isin(selected_agent)) &
    (df["level"].between(level_range[0], level_range[1]))
]

if filtered_df.empty:
    st.warning("No data available.")
    st.stop()

# ⚠️ COPY (SettingWithCopy fix)
filtered_df = filtered_df.copy()

# 🔥 KDA
filtered_df["kda"] = filtered_df["kills"] / (filtered_df["deaths"] + 1)

# 🔥 RANK
def get_rank(kda):
    if kda > 2:
        return "Radiant"
    elif kda > 1.5:
        return "Immortal"
    elif kda > 1:
        return "Diamond"
    else:
        return "Gold"

filtered_df["rank"] = filtered_df["kda"].apply(get_rank)

# ---------------------------
# 🏆 RANK DISTRIBUTION
# ---------------------------
st.header("🏆 Rank Distribution")

rank_counts = filtered_df["rank"].value_counts()

fig, ax = plt.subplots()
sns.barplot(x=rank_counts.index, y=rank_counts.values, ax=ax)
st.pyplot(fig)

# ---------------------------
# 📊 OVERVIEW
# ---------------------------
st.markdown("---")
st.header("📊 Overview")

total_players = filtered_df["user_id"].nunique()
avg_kills = int(filtered_df["kills"].mean())
avg_kda = round(filtered_df["kda"].mean(), 2)

col1, col2, col3 = st.columns(3)

col1.metric("👥 Players", total_players)
col2.metric("🔫 Avg Kills", avg_kills)
col3.metric("⚔️ Avg KDA", avg_kda)

# ---------------------------
# 🎮 PLAYER PERFORMANCE
# ---------------------------
st.markdown("---")
st.header("🎮 Player Performance")

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.histplot(filtered_df["kills"], bins=20, ax=ax1)
st.pyplot(fig1)

# ---------------------------
# 🆚 PLAYER COMPARISON
# ---------------------------
st.markdown("---")
st.header("🆚 Player Comparison")

players = filtered_df["user_id"].unique()

p1 = st.selectbox("Player 1", players)
p2 = st.selectbox("Player 2", players, index=1)

player1 = filtered_df[filtered_df["user_id"] == p1]
player2 = filtered_df[filtered_df["user_id"] == p2]

st.write("Player 1 Avg Kills:", int(player1["kills"].mean()))
st.write("Player 2 Avg Kills:", int(player2["kills"].mean()))

# ---------------------------
# 🧠 AGENT ANALYSIS
# ---------------------------
st.markdown("---")
st.header("🧠 Agent Analysis")

top_agents = filtered_df["agent"].value_counts()

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(x=top_agents.values, y=top_agents.index, ax=ax2)
st.pyplot(fig2)

# ---------------------------
# 📈 ACTIVITY ANALYSIS
# ---------------------------
st.markdown("---")
st.header("📈 Activity Analysis")

filtered_df["date"] = pd.to_datetime(filtered_df["date"])
daily_users = filtered_df.groupby(filtered_df["date"].dt.date)["user_id"].nunique()

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.lineplot(x=daily_users.index, y=daily_users.values, ax=ax3)
st.pyplot(fig3)