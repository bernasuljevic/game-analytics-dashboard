import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import os

sns.set(style="whitegrid")

st.set_page_config(layout="wide")

# 🎯 TITLE
st.title("🎯 Valorant Player Analytics Dashboard")
st.info("Duelists = entry fraggers | Initiators = intel | Sentinels = defense | Controllers = map control")

# 🔗 DATA
@st.cache_data
def load_data():
    db_path = "game_data.db"

    if not os.path.exists(db_path):
        df = pd.read_csv("game_data.csv")
        conn = sqlite3.connect(db_path)
        df.to_sql("game_sessions", conn, if_exists="replace", index=False)
        conn.close()

    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM game_sessions", conn)
    conn.close()

    return df

df = load_data()

# 🎮 SIDEBAR
with st.sidebar:
    st.title("🎮 Controls")

    selected_agent = st.multiselect(
        "Agent",
        options=df["agent"].unique(),
        default=df["agent"].unique()
    )

    level_range = st.slider(
        "Level Range",
        int(df["level"].min()),
        int(df["level"].max()),
        (1, 50)
    )

# 🎯 FILTER
filtered_df = df[
    (df["agent"].isin(selected_agent)) &
    (df["level"].between(level_range[0], level_range[1]))
]

if filtered_df.empty:
    st.warning("No data available.")
    st.stop()

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

# 🔥 AGENT ROLES
agent_roles = {
    "Jett": "Duelist",
    "Reyna": "Duelist",
    "Phoenix": "Duelist",
    "Sova": "Initiator",
    "Sage": "Sentinel"
}

filtered_df["role"] = filtered_df["agent"].map(agent_roles)

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
# 🏆 RANK DISTRIBUTION
# ---------------------------
st.markdown("---")
st.header("🏆 Rank Distribution")

rank_counts = filtered_df["rank"].value_counts()

fig, ax = plt.subplots(figsize=(8,5))
sns.barplot(x=rank_counts.index, y=rank_counts.values, ax=ax)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# ---------------------------
# 🧩 ROLE DISTRIBUTION
# ---------------------------
st.markdown("---")
st.header("🧩 Role Distribution")

role_counts = filtered_df["role"].value_counts()

fig, ax = plt.subplots(figsize=(8,5))
sns.barplot(x=role_counts.values, y=role_counts.index, ax=ax)
plt.tight_layout()
st.pyplot(fig)

# ---------------------------
# 🎯 AGENT PERFORMANCE
# ---------------------------
st.markdown("---")
st.header("🎯 Agent Performance")

agent_perf = filtered_df.groupby("agent")[["kills","kda"]].mean().sort_values(by="kills", ascending=False)

fig, ax = plt.subplots(figsize=(10,6))
agent_perf["kills"].plot(kind="bar", ax=ax)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# ---------------------------
# 🎮 PLAYER PERFORMANCE
# ---------------------------
st.markdown("---")
st.header("🎮 Player Performance")

fig, ax = plt.subplots(figsize=(10,5))
sns.histplot(filtered_df["kills"], bins=20, ax=ax)
plt.tight_layout()
st.pyplot(fig)

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

col1, col2 = st.columns(2)

col1.metric("Player 1 Avg Kills", int(player1["kills"].mean()))
col2.metric("Player 2 Avg Kills", int(player2["kills"].mean()))

# ---------------------------
# 📈 ACTIVITY ANALYSIS
# ---------------------------
st.markdown("---")
st.header("📈 Activity Analysis")

filtered_df["date"] = pd.to_datetime(filtered_df["date"])
daily_users = filtered_df.groupby(filtered_df["date"].dt.date)["user_id"].nunique()

fig, ax = plt.subplots(figsize=(10,5))
sns.lineplot(x=daily_users.index, y=daily_users.values, ax=ax)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)