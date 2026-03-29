import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

st.set_page_config(layout="wide")

# 🎯 TITLE
st.title("🎯 Valorant Analytics Dashboard")
st.caption("Interactive player & agent analytics")

# 🔗 DATA
@st.cache_data
def load_data():
    if not os.path.exists("game_data.db"):
        df = pd.read_csv("game_data.csv")
        conn = sqlite3.connect("game_data.db")
        df.to_sql("game_sessions", conn, if_exists="replace", index=False)
        conn.close()

    conn = sqlite3.connect("game_data.db")
    df = pd.read_sql("SELECT * FROM game_sessions", conn)
    conn.close()
    return df

df = load_data()

# 🎮 SIDEBAR
with st.sidebar:
    st.title("🎮 Filters")

    selected_agent = st.multiselect(
        "Agent",
        df["agent"].unique(),
        default=df["agent"].unique()
    )

    level_range = st.slider(
        "Level",
        int(df["level"].min()),
        int(df["level"].max()),
        (1, 50)
    )

# 🎯 FILTER
filtered_df = df[
    (df["agent"].isin(selected_agent)) &
    (df["level"].between(level_range[0], level_range[1]))
].copy()

if filtered_df.empty:
    st.warning("No data")
    st.stop()

# 🔥 FEATURES
filtered_df["kda"] = filtered_df["kills"] / (filtered_df["deaths"] + 1)

agent_roles = {
    "Jett": "Duelist",
    "Reyna": "Duelist",
    "Phoenix": "Duelist",
    "Sova": "Initiator",
    "Sage": "Sentinel"
}

agent_colors = {
    "Jett": "#00FFFF",
    "Reyna": "#8000FF",
    "Phoenix": "#FF5733",
    "Sova": "#00FF99",
    "Sage": "#A8E6CF"
}

filtered_df["role"] = filtered_df["agent"].map(agent_roles)

# 📊 OVERVIEW
st.markdown("## 📊 Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Players", filtered_df["user_id"].nunique())
c2.metric("Avg Kills", int(filtered_df["kills"].mean()))
c3.metric("Avg KDA", round(filtered_df["kda"].mean(), 2))

st.markdown("---")

# 🎯 AGENT PERFORMANCE + ROLE
col1, col2 = st.columns(2)

# Agent Performance
agent_perf = filtered_df.groupby("agent")["kills"].mean().reset_index()

fig1 = px.bar(
    agent_perf,
    x="agent",
    y="kills",
    color="agent",
    color_discrete_map=agent_colors,
    title="Kills per Agent"
)

fig1.update_layout(height=350)
fig1.update_traces(hovertemplate="Agent: %{x}<br>Kills: %{y}")

col1.plotly_chart(fig1, use_container_width=True)

# Role Distribution
role_counts = filtered_df["role"].value_counts().reset_index()
role_counts.columns = ["role", "count"]

fig2 = px.pie(
    role_counts,
    names="role",
    values="count",
    title="Role Distribution"
)

fig2.update_layout(height=350)

col2.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# 🏆 RANK
filtered_df["rank"] = pd.cut(
    filtered_df["kda"],
    bins=[0,1,1.5,2,10],
    labels=["Gold","Diamond","Immortal","Radiant"]
)

rank_counts = filtered_df["rank"].value_counts().reset_index()
rank_counts.columns = ["rank","count"]

fig3 = px.bar(rank_counts, x="rank", y="count", color="rank", title="Rank")

fig3.update_layout(height=350)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# 🆚 PLAYER COMPARISON
st.markdown("## 🆚 Player Comparison")

players = filtered_df["user_id"].unique()

p1, p2 = st.columns(2)

player1 = p1.selectbox("Player 1", players)
player2 = p2.selectbox("Player 2", players)

d1 = filtered_df[filtered_df["user_id"] == player1]
d2 = filtered_df[filtered_df["user_id"] == player2]

c1, c2 = st.columns(2)
c1.metric("Player 1 Kills", int(d1["kills"].mean()))
c2.metric("Player 2 Kills", int(d2["kills"].mean()))