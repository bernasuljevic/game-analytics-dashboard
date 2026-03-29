import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

st.set_page_config(page_title="Game Analytics", page_icon="🎮", layout="wide")

# 🎨 BACKGROUND STYLE
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# 🎯 TITLE (GRADIENT)
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(to right, #ff416c, #ff4b2b);
-webkit-background-clip: text;
color: transparent;'>
🎮 Valorant Analytics Dashboard
</h1>
""", unsafe_allow_html=True)

st.markdown(
"<p style='text-align:center; color:gray;'>Interactive player & agent insights</p>",
unsafe_allow_html=True
)

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
    st.markdown("<h2 style='text-align:center;'>🎮 Control Panel</h2>", unsafe_allow_html=True)

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

def card(title, value, icon):
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.05);
    padding:20px;border-radius:15px;text-align:center;
    backdrop-filter: blur(10px);'>
    <h4>{icon} {title}</h4>
    <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    card("Players", filtered_df["user_id"].nunique(), "👥")

with c2:
    card("Avg Kills", int(filtered_df["kills"].mean()), "🔫")

with c3:
    card("Avg KDA", round(filtered_df["kda"].mean(), 2), "⚔️")

st.divider()

# 🎯 AGENT PERFORMANCE + ROLE
col1, col2 = st.columns(2)

agent_perf = filtered_df.groupby("agent")["kills"].mean().reset_index()

fig1 = px.bar(
    agent_perf,
    x="agent",
    y="kills",
    color="agent",
    color_discrete_map=agent_colors,
    title="Kills per Agent"
)

fig1.update_layout(template="plotly_dark", height=350, title_x=0.5)
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

fig2.update_traces(textinfo='percent+label')
fig2.update_layout(template="plotly_dark", height=350)

col2.plotly_chart(fig2, use_container_width=True)

st.divider()

# 🏆 RANK
filtered_df["rank"] = pd.cut(
    filtered_df["kda"],
    bins=[0,1,1.5,2,10],
    labels=["Gold","Diamond","Immortal","Radiant"]
)

rank_counts = filtered_df["rank"].value_counts().reset_index()
rank_counts.columns = ["rank","count"]

fig3 = px.bar(rank_counts, x="rank", y="count", color="rank", title="Rank")

fig3.update_layout(template="plotly_dark", height=350, title_x=0.5)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

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

c3, c4 = st.columns(2)
c3.metric("Player 1 KDA", round(d1["kda"].mean(),2))
c4.metric("Player 2 KDA", round(d2["kda"].mean(),2))